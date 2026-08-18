"""Health/readiness routes.

Wires the previously-unused `health_service` module into the actual API so
deploy targets (Render, Fly, etc.) have something to point a health check
probe at, and so "is it actually loading" can be verified with one curl.
"""
from __future__ import annotations

import os

from fastapi import APIRouter

from app.services.health_service import get_health

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
async def health():
    payload = dict(get_health())
    payload["mongo_configured"] = bool(os.environ.get("MONGO_URL"))
    payload["stripe_configured"] = bool(os.environ.get("STRIPE_SECRET_KEY"))
    return payload
