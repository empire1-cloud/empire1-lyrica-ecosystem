"""Plan / pricing definitions for Omni-Agent.

Single source of truth for the paid tiers referenced by the billing router
and (optionally) the frontend pricing page. Mirrors
`omni_agent/sales/pricing.md` — keep the two in sync when pricing changes.

Only "Pro" and "Team" are self-serve (Stripe Checkout). "Free" needs no
checkout. "Enterprise" is sales-assisted (mailto), never self-serve.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class Plan:
    key: str
    name: str
    monthly_usd: int
    unit_label: str  # e.g. "seat" or "workspace"
    stripe_price_env: str  # name of the env var holding the live/test Stripe Price ID
    mode: str = "subscription"

    @property
    def stripe_price_id(self) -> Optional[str]:
        return os.environ.get(self.stripe_price_env) or None


# Self-serve plans only. Free needs no checkout; Enterprise is sales-assisted.
PLANS: Dict[str, Plan] = {
    "pro": Plan(
        key="pro",
        name="Pro",
        monthly_usd=49,
        unit_label="seat",
        stripe_price_env="STRIPE_PRICE_PRO",
    ),
    "team": Plan(
        key="team",
        name="Team",
        monthly_usd=299,
        unit_label="workspace",
        stripe_price_env="STRIPE_PRICE_TEAM",
    ),
}


def get_plan(plan_key: str) -> Optional[Plan]:
    return PLANS.get((plan_key or "").strip().lower())


def list_plans() -> Dict[str, dict]:
    """JSON-serializable view of the self-serve plans, including whether
    each one is currently purchasable (i.e. its Stripe Price ID is configured).
    """
    return {
        key: {
            "name": plan.name,
            "monthly_usd": plan.monthly_usd,
            "unit_label": plan.unit_label,
            "purchasable": plan.stripe_price_id is not None,
        }
        for key, plan in PLANS.items()
    }
