"""GitHub App identity + manifest configuration.

Omni-Agent's primary distribution/billing surface is the GitHub
Marketplace (a paid GitHub App listing), per product direction — not a
standalone Stripe checkout. The Stripe billing added in an earlier branch
(app/services/stripe_service.py) stays as a direct-sale bridge: GitHub
Marketplace requires **100 installations before a paid plan can go live**
(see requirements-for-listing-an-app in GitHub's docs), so early paying
customers realistically come through Stripe/direct sale first, Marketplace
distribution second. Both paths are additive, not exclusive.

V2 UPDATE (Phase 1-3):
- Expanded DEFAULT_PERMISSIONS to support PR creation, check runs, and commit statuses.
- App now requests: metadata:read, contents:read, pull_requests:write, checks:write
- GitHub App can now autonomously open PRs and post check runs on behalf of tasks.
- Local execution model unchanged — the App's new permissions only activate when
  an installation has explicitly granted them during the install flow.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional


def _base_url(env_var: str, default: str = "") -> str:
    return os.environ.get(env_var, default).rstrip("/")


def api_base_url() -> str:
    """Public URL of this backend (webhook + manifest-callback target)."""
    return _base_url("APP_BASE_URL")


def frontend_base_url() -> str:
    """Public URL of the marketing/pricing site (post-install redirect target)."""
    return _base_url("FRONTEND_BASE_URL") or api_base_url()


def app_owner_org() -> Optional[str]:
    """Org to register the App under, if any (None = personal account)."""
    return os.environ.get("GITHUB_APP_OWNER_ORG") or None


def manifest_registration_url() -> str:
    """Where the manifest-flow form gets POSTed to create the App."""
    org = app_owner_org()
    if org:
        return f"https://github.com/organizations/{org}/settings/apps/new"
    return "https://github.com/settings/apps/new"


def build_manifest() -> Dict[str, Any]:
    """The GitHub App Manifest — see
    https://docs.github.com/en/apps/sharing-github-apps/registering-a-github-app-from-a-manifest

    Posting this (via the HTML form served at GET /api/github/app/new) is
    how the actual GitHub App gets created. Nothing in this repo creates
    it automatically — a human (Manda) drives that flow once, in her own
    browser, against her own GitHub account/org.
    """
    api_base = api_base_url()
    site_base = frontend_base_url()
    name = os.environ.get("GITHUB_APP_NAME", "Omni Agent")

    manifest: Dict[str, Any] = {
        "name": name,
        "url": site_base or "https://example.com",
        "hook_attributes": {"url": f"{api_base}/api/github/webhook"},
        "redirect_url": f"{api_base}/api/github/manifest-callback",
        "setup_url": f"{site_base}/github/installed" if site_base else None,
        "callback_urls": [f"{api_base}/api/github/oauth-callback"],
        "description": (
            "Close your TODO.md, with receipts. Omni-Agent scans your repo's "
            "markdown backlog and turns unfinished tasks into evaluated, "
            "audit-grade work — with autonomous PR creation and evidence."
        ),
        "public": True,
        "default_events": DEFAULT_EVENTS,
        "default_permissions": DEFAULT_PERMISSIONS,
        "request_oauth_on_install": True,
    }
    # Drop keys GitHub doesn't want to see as null/empty during local dev
    # (e.g. before APP_BASE_URL/FRONTEND_BASE_URL are set).
    return {k: v for k, v in manifest.items() if v not in (None, "")}


# V2 EXPANDED PERMISSIONS: enables autonomous PR + check-run posting.
# Users must grant these permissions during install; they're not retroactively
# applied to v1-only installs.
DEFAULT_PERMISSIONS: Dict[str, str] = {
    "metadata": "read",           # original v1
    "contents": "read",            # V2: read repo to validate file paths
    "pull_requests": "write",       # V2: create PRs from task completions
    "checks": "write",              # V2: post check runs with cohesion scores
    "statuses": "write",            # V2 fallback: legacy commit status API
}

# installation(_repositories): know who has the app installed, on what repos.
# marketplace_purchase: the actual billing event (purchased/changed/cancelled/
# pending_change/pending_change_cancelled) — mandatory for a paid listing.
DEFAULT_EVENTS: List[str] = [
    "installation",
    "installation_repositories",
    "marketplace_purchase",
]


def is_configured() -> bool:
    """True once the App has actually been created and its credentials
    are set in the environment (as opposed to just this manifest existing
    in code)."""
    return bool(
        os.environ.get("GITHUB_APP_ID") and os.environ.get("GITHUB_APP_PRIVATE_KEY")
    )


def webhook_configured() -> bool:
    return bool(os.environ.get("GITHUB_WEBHOOK_SECRET"))
