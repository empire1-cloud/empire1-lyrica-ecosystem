"""Stripe integration for Omni-Agent's self-serve plans (Pro, Team).

Intentionally reads all secrets from the environment — nothing here ever
hardcodes a key. In a fresh environment with no Stripe env vars set, every
function raises `StripeNotConfigured` instead of crashing the app, so the
service (and the rest of the API) still boots and serves everything else.

Env vars (set these in the deploy target, never committed):
    STRIPE_SECRET_KEY       sk_test_... / sk_live_...
    STRIPE_WEBHOOK_SECRET   whsec_... (from the Stripe CLI or Dashboard)
    STRIPE_PRICE_PRO        price_... for the Pro plan
    STRIPE_PRICE_TEAM       price_... for the Team plan
    APP_BASE_URL            e.g. https://omni-agent.example.com (for redirect URLs)
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

import stripe

from app.core.plans import get_plan


class StripeNotConfigured(RuntimeError):
    """Raised when a Stripe operation is attempted without the required env vars."""


class StripeSessionError(RuntimeError):
    """Raised when Stripe itself rejects the request (bad price id, etc.)."""


def _require_api_key() -> str:
    api_key = os.environ.get("STRIPE_SECRET_KEY")
    if not api_key:
        raise StripeNotConfigured(
            "STRIPE_SECRET_KEY is not set. Add it in the deploy environment "
            "(Stripe Dashboard -> Developers -> API keys) before checkout can run."
        )
    return api_key


def create_checkout_session(
    *,
    plan_key: str,
    customer_email: Optional[str] = None,
    success_url: Optional[str] = None,
    cancel_url: Optional[str] = None,
) -> "stripe.checkout.Session":
    """Create a Stripe Checkout Session for a self-serve plan (pro/team).

    Raises StripeNotConfigured if Stripe or the plan's price id isn't
    configured yet, and StripeSessionError if Stripe rejects the request.
    """
    plan = get_plan(plan_key)
    if plan is None:
        raise ValueError(f"Unknown or non-self-serve plan: {plan_key!r}")

    stripe.api_key = _require_api_key()

    price_id = plan.stripe_price_id
    if not price_id:
        raise StripeNotConfigured(
            f"{plan.stripe_price_env} is not set. Create a Price for the "
            f"{plan.name} plan in Stripe and set {plan.stripe_price_env}."
        )

    base_url = os.environ.get("APP_BASE_URL", "").rstrip("/")
    success_url = success_url or f"{base_url}/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = cancel_url or f"{base_url}/cancel"

    try:
        session = stripe.checkout.Session.create(
            mode=plan.mode,
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=customer_email or None,
            allow_promotion_codes=True,
            metadata={"plan": plan.key},
            subscription_data={"metadata": {"plan": plan.key}},
        )
    except stripe.error.StripeError as exc:  # type: ignore[attr-defined]
        raise StripeSessionError(str(exc)) from exc

    return session


def construct_event(payload: bytes, sig_header: Optional[str]) -> Dict[str, Any]:
    """Verify and parse an incoming Stripe webhook payload."""
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        raise StripeNotConfigured(
            "STRIPE_WEBHOOK_SECRET is not set. Configure the webhook endpoint "
            "in the Stripe Dashboard and set STRIPE_WEBHOOK_SECRET."
        )
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", stripe.api_key)
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as exc:  # type: ignore[attr-defined]
        raise StripeSessionError(f"Invalid webhook payload/signature: {exc}") from exc
    return event
