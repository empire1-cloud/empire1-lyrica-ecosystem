"""GitHub App authentication: App-level JWTs and installation access tokens.

Not wired into any product feature yet in v1 (see app/core/github_app.py
"Scope note") — this exists so the moment Omni-Agent needs to call the
GitHub API as an installation (Phase 2: opening PRs, posting checks), the
auth primitive is already here, tested, and doesn't block on a rewrite.
"""
from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional

import httpx
import jwt as pyjwt

GITHUB_API_BASE = "https://api.github.com"


class GitHubAppNotConfigured(RuntimeError):
    """Raised when GITHUB_APP_ID / GITHUB_APP_PRIVATE_KEY aren't set."""


class GitHubAPIError(RuntimeError):
    """Raised when the GitHub API rejects a request."""


def build_app_jwt(*, now: Optional[int] = None) -> str:
    """Build the short-lived (10 min) JWT a GitHub App uses to authenticate
    as itself (as opposed to as an installation). Signed RS256 with the
    App's private key.
    """
    app_id = os.environ.get("GITHUB_APP_ID")
    private_key = os.environ.get("GITHUB_APP_PRIVATE_KEY")
    if not app_id or not private_key:
        raise GitHubAppNotConfigured(
            "GITHUB_APP_ID and GITHUB_APP_PRIVATE_KEY must both be set. "
            "Run the manifest flow at GET /api/github/app/new to create "
            "the App and get these values."
        )
    ts = now if now is not None else int(time.time())
    payload = {
        "iat": ts - 60,  # allow for clock drift
        "exp": ts + (9 * 60),  # GitHub caps this at 10 minutes
        "iss": app_id,
    }
    # PEM may arrive from an env var with literal "\n" sequences instead of
    # real newlines (common when pasting a multi-line secret into a
    # single-line env var UI) — normalize before handing to the signer.
    key = private_key.replace("\\n", "\n")
    return pyjwt.encode(payload, key, algorithm="RS256")


async def get_installation_token(installation_id: int) -> Dict[str, Any]:
    """Exchange the App JWT for a short-lived (1hr) installation access
    token, scoped to whatever repos that installation has granted.
    """
    app_jwt = build_app_jwt()
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{GITHUB_API_BASE}/app/installations/{installation_id}/access_tokens",
            headers={
                "Authorization": f"Bearer {app_jwt}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
    if resp.status_code >= 400:
        raise GitHubAPIError(
            f"GitHub rejected installation token request "
            f"({resp.status_code}): {resp.text}"
        )
    return resp.json()
