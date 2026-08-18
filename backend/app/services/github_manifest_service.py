"""GitHub App manifest-flow helpers: the one-time "create the App" dance.

Flow (https://docs.github.com/en/apps/sharing-github-apps/registering-a-github-app-from-a-manifest):
1. GET /api/github/app/new  -> serves an auto-submitting HTML form that
   POSTs our manifest (app/core/github_app.py) to github.com.
2. A human (Manda) reviews + confirms on GitHub's own UI.
3. GitHub redirects to our redirect_url with a one-time `code`.
4. GET /api/github/manifest-callback exchanges that code for the App's
   real credentials (id, pem, webhook_secret, client secret) via this
   module, and shows them ONCE so she can copy them into env vars. Nothing
   here persists those values to disk/db/logs.

CSRF protection: a random `state` is generated when serving the form and
must come back unchanged on the callback. Kept in an in-memory TTL store —
fine for a one-person, one-time bootstrap action; not meant to survive a
multi-instance deploy (documented limitation, not a product requirement).
"""
from __future__ import annotations

import secrets
import time
from typing import Any, Dict, Optional

import httpx

GITHUB_API_BASE = "https://api.github.com"
_STATE_TTL_SECONDS = 15 * 60
_pending_states: Dict[str, float] = {}


class ManifestExchangeError(RuntimeError):
    """Raised when GitHub rejects the manifest-code exchange."""


def issue_state() -> str:
    token = secrets.token_urlsafe(24)
    _pending_states[token] = time.time() + _STATE_TTL_SECONDS
    _prune_expired()
    return token


def consume_state(token: Optional[str]) -> bool:
    """Returns True and invalidates the token iff it was issued and not
    expired. Single-use — a replayed state fails."""
    _prune_expired()
    if not token or token not in _pending_states:
        return False
    del _pending_states[token]
    return True


def _prune_expired() -> None:
    now = time.time()
    expired = [t for t, exp in _pending_states.items() if exp < now]
    for t in expired:
        _pending_states.pop(t, None)


async def exchange_manifest_code(code: str) -> Dict[str, Any]:
    """POST /app-manifests/{code}/conversions — trades the one-time code
    from the manifest flow for the App's real id/pem/webhook_secret/client
    credentials. Must happen within an hour of the code being issued.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{GITHUB_API_BASE}/app-manifests/{code}/conversions",
            headers={"Accept": "application/vnd.github+json"},
        )
    if resp.status_code >= 400:
        raise ManifestExchangeError(
            f"GitHub rejected the manifest code exchange "
            f"({resp.status_code}): {resp.text}"
        )
    return resp.json()
