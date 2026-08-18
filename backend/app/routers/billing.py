"""Self-serve billing routes: create a Stripe Checkout session for the
Pro/Team plans, and receive the Stripe webhook that confirms payment.

Enterprise stays sales-assisted (mailto on the landing page) — never
routed through here.
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, field_validator

from app.core.plans import list_plans
from app.services import customer_store
from app.services.stripe_service import (
    StripeNotConfigured,
    StripeSessionError,
    construct_event,
    create_checkout_session,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/billing", tags=["billing"])


class CheckoutRequest(BaseModel):
    plan: str
    customer_email: Optional[EmailStr] = None

    @field_validator("plan")
    @classmethod
    def _normalize_plan(cls, v: str) -> str:
        return (v or "").strip().lower()


@router.get("/plans")
async def get_plans():
    """Self-serve plan catalog, including whether each is currently
    purchasable (i.e. Stripe is configured for it). Lets the frontend
    disable/hide a Buy button instead of sending users into a dead flow.
    """
    return {"plans": list_plans()}


@router.post("/checkout")
async def create_checkout(payload: CheckoutRequest, request: Request):
    if payload.plan not in {"pro", "team"}:
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_plan", "message": "plan must be 'pro' or 'team'"},
        )

    try:
        session = create_checkout_session(
            plan_key=payload.plan,
            customer_email=payload.customer_email,
        )
    except StripeNotConfigured as exc:
        # Not an error in the customer's flow — it's a deploy config gap.
        # Return 503 so the frontend can show "checkout coming soon" instead
        # of a raw crash.
        logger.warning("Checkout requested but Stripe not configured: %s", exc)
        return JSONResponse(
            status_code=503,
            content={"error": "billing_not_configured", "message": str(exc)},
        )
    except StripeSessionError as exc:
        logger.error("Stripe rejected checkout session: %s", exc)
        return JSONResponse(
            status_code=502,
            content={"error": "stripe_error", "message": str(exc)},
        )

    db = getattr(request.app.state, "db", None)
    await customer_store.record_checkout_started(
        plan=payload.plan,
        customer_email=payload.customer_email,
        session_id=session.id,
        db=db,
    )

    return {"checkout_url": session.url, "session_id": session.id}


@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = construct_event(payload, sig_header)
    except StripeNotConfigured as exc:
        logger.warning("Webhook received but Stripe not configured: %s", exc)
        return JSONResponse(
            status_code=503,
            content={"error": "billing_not_configured", "message": str(exc)},
        )
    except StripeSessionError as exc:
        logger.warning("Rejected webhook: %s", exc)
        return JSONResponse(status_code=400, content={"error": "invalid_signature"})

    event_type = event.get("type")
    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        db = getattr(request.app.state, "db", None)
        await customer_store.record_checkout_completed(
            plan=(session.get("metadata") or {}).get("plan", "unknown"),
            customer_email=session.get("customer_email") or session.get("customer_details", {}).get("email"),
            session_id=session.get("id"),
            subscription_id=session.get("subscription"),
            db=db,
        )

    return {"received": True, "type": event_type}
