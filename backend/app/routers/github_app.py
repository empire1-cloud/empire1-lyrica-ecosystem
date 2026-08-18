"""GitHub App routes: manifest-driven registration, the App+Marketplace
webhook receiver, and the post-install OAuth callback.

Nothing in this file creates the GitHub App or publishes anything on
GitHub by itself — GET /api/github/app/new only *serves a form* that a
human submits on github.com, in their own browser, against their own
account. That's the actual creation step, and it's deliberately left for
Manda to do.
"""
from __future__ import annotations

import html
import json
import logging
import os
from typing import Any, Dict, Optional

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from app.core.github_app import (
    build_manifest,
    frontend_base_url,
    is_configured,
    manifest_registration_url,
    webhook_configured,
)
from app.services import github_events_store as store
from app.services.github_manifest_service import (
    ManifestExchangeError,
    consume_state,
    exchange_manifest_code,
    issue_state,
)
from app.services.github_webhook_service import verify_signature

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/github", tags=["github-app"])


@router.get("/status")
async def status():
    return {
        "app_configured": is_configured(),
        "webhook_configured": webhook_configured(),
        "manifest_registration_url": manifest_registration_url(),
    }


@router.get("/app/new", response_class=HTMLResponse)
async def new_app_form():
    """Serves an auto-submitting form that POSTs our App Manifest to
    GitHub. Visiting this URL and clicking through is how the GitHub App
    actually gets created — a one-time, human-driven action.
    """
    manifest = build_manifest()
    state = issue_state()
    manifest_json = html.escape(json.dumps(manifest), quote=True)
    target_url = manifest_registration_url()
    body = f"""
    <!doctype html>
    <html><head><title>Create the Omni Agent GitHub App</title></head>
    <body style="font-family: sans-serif; max-width: 640px; margin: 60px auto;">
      <h1>Create the Omni Agent GitHub App</h1>
      <p>This submits Omni-Agent's App Manifest to GitHub. Review it on the
      next screen before confirming — nothing is created until you approve
      it there.</p>
      <pre style="background:#f4f4f4; padding:16px; overflow:auto; font-size:12px;">{manifest_json}</pre>
      <form action="{html.escape(target_url, quote=True)}" method="post">
        <input type="hidden" name="manifest" value='{manifest_json}'>
        <input type="hidden" name="state" value="{html.escape(state, quote=True)}">
        <button type="submit" style="padding:12px 20px; font-size:16px;">
          Continue to GitHub &rarr;
        </button>
      </form>
    </body></html>
    """
    return HTMLResponse(content=body)


@router.get("/manifest-callback", response_class=HTMLResponse)
async def manifest_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if not consume_state(state):
        return HTMLResponse(
            content="<p>Invalid or expired request. Start again at "
            "<a href='/api/github/app/new'>/api/github/app/new</a>.</p>",
            status_code=400,
        )
    if not code:
        return HTMLResponse(content="<p>Missing code from GitHub.</p>", status_code=400)

    try:
        credentials = await exchange_manifest_code(code)
    except ManifestExchangeError as exc:
        logger.error("Manifest exchange failed: %s", exc)
        return HTMLResponse(content=f"<p>GitHub rejected the exchange: {html.escape(str(exc))}</p>", status_code=502)

    # Shown ONCE. Nothing here logs or persists these values — copy them
    # into your deploy environment now (GITHUB_APP_ID, GITHUB_APP_PRIVATE_KEY,
    # GITHUB_WEBHOOK_SECRET, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET) and this
    # page becomes useless the moment you navigate away.
    rows = "".join(
        f"<tr><td><code>{html.escape(str(k))}</code></td>"
        f"<td><pre style='white-space:pre-wrap;word-break:break-all;'>{html.escape(str(v))}</pre></td></tr>"
        for k, v in credentials.items()
        if k in {"id", "slug", "pem", "webhook_secret", "client_id", "client_secret"}
    )
    body = f"""
    <!doctype html>
    <html><head><title>App created — copy these now</title></head>
    <body style="font-family: sans-serif; max-width: 800px; margin: 60px auto;">
      <h1>Your GitHub App is created</h1>
      <p><strong>Copy these into your deploy environment now.</strong> This
      page will not show them again.</p>
      <table border="1" cellpadding="8" style="border-collapse:collapse;">{rows}</table>
      <p>Map to env vars: <code>id</code> &rarr; <code>GITHUB_APP_ID</code>,
      <code>pem</code> &rarr; <code>GITHUB_APP_PRIVATE_KEY</code>,
      <code>webhook_secret</code> &rarr; <code>GITHUB_WEBHOOK_SECRET</code>,
      <code>client_id</code> &rarr; <code>GITHUB_CLIENT_ID</code>,
      <code>client_secret</code> &rarr; <code>GITHUB_CLIENT_SECRET</code>.</p>
      <p>Next: <a href="https://github.com/settings/apps">list it for GitHub
      Marketplace</a> once you're ready.</p>
    </body></html>
    """
    return HTMLResponse(content=body)


@router.get("/oauth-callback")
async def oauth_callback(request: Request):
    """Post-install OAuth exchange (request_oauth_on_install in the
    manifest). Identifies which GitHub user completed the install —
    useful for onboarding/CS — nothing else. Redirects to the frontend
    either way so the user always lands somewhere real.
    """
    code = request.query_params.get("code")
    frontend = frontend_base_url()
    fallback = f"{frontend}/github/installed" if frontend else "/"

    client_id = os.environ.get("GITHUB_CLIENT_ID")
    client_secret = os.environ.get("GITHUB_CLIENT_SECRET")
    if not code or not client_id or not client_secret:
        return RedirectResponse(url=fallback)

    async with httpx.AsyncClient(timeout=10.0) as client:
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={"client_id": client_id, "client_secret": client_secret, "code": code},
        )
    if token_resp.status_code >= 400:
        logger.warning("GitHub OAuth token exchange failed: %s", token_resp.text)
        return RedirectResponse(url=fallback)

    access_token = token_resp.json().get("access_token")
    if not access_token:
        return RedirectResponse(url=fallback)

    async with httpx.AsyncClient(timeout=10.0) as client:
        user_resp = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}", "Accept": "application/vnd.github+json"},
        )
    if user_resp.status_code < 400:
        login = user_resp.json().get("login")
        logger.info("GitHub App install OAuth completed for @%s", login)

    return RedirectResponse(url=fallback)


def _payload_str(d: Optional[Dict[str, Any]], *keys: str) -> Optional[Any]:
    cur: Any = d
    for k in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur


async def _handle_installation(payload: Dict[str, Any], db) -> None:
    installation = payload.get("installation") or {}
    account = installation.get("account") or {}
    await store.record_installation_event(
        action=payload.get("action", "unknown"),
        installation_id=installation.get("id"),
        account_login=account.get("login"),
        account_type=account.get("type"),
        repository_selection=installation.get("repository_selection"),
        db=db,
    )


async def _handle_marketplace_purchase(payload: Dict[str, Any], db) -> None:
    mp = payload.get("marketplace_purchase") or {}
    account = mp.get("account") or {}
    plan = mp.get("plan") or {}
    await store.record_marketplace_event(
        action=payload.get("action", "unknown"),
        account_id=account.get("id"),
        account_login=account.get("login"),
        account_type=account.get("type"),
        plan_name=plan.get("name"),
        plan_id=plan.get("id"),
        unit_count=mp.get("unit_count"),
        billing_cycle=mp.get("billing_cycle"),
        on_free_trial=bool(mp.get("on_free_trial")),
        effective_date=payload.get("effective_date"),
        db=db,
    )


@router.post("/webhook")
async def github_webhook(request: Request):
    secret = os.environ.get("GITHUB_WEBHOOK_SECRET")
    if not secret:
        logger.warning("GitHub webhook received but GITHUB_WEBHOOK_SECRET not set")
        return JSONResponse(
            status_code=503,
            content={"error": "github_app_not_configured", "message": "GITHUB_WEBHOOK_SECRET is not set."},
        )

    body = await request.body()
    signature = request.headers.get("x-hub-signature-256")
    if not verify_signature(body, signature, secret):
        logger.warning("GitHub webhook signature verification failed")
        return JSONResponse(status_code=400, content={"error": "invalid_signature"})

    event = request.headers.get("x-github-event", "")
    delivery_id = request.headers.get("x-github-delivery")
    try:
        payload = json.loads(body or b"{}")
    except json.JSONDecodeError:
        return JSONResponse(status_code=400, content={"error": "invalid_json"})

    db = getattr(request.app.state, "db", None)

    if event == "installation":
        await _handle_installation(payload, db)
    elif event == "marketplace_purchase":
        await _handle_marketplace_purchase(payload, db)
    elif event == "installation_repositories":
        installation = payload.get("installation") or {}
        account = installation.get("account") or {}
        await store.record_installation_event(
            action=f"repositories_{payload.get('action', 'unknown')}",
            installation_id=installation.get("id"),
            account_login=account.get("login"),
            account_type=account.get("type"),
            repository_selection=installation.get("repository_selection"),
            db=db,
        )
    else:
        # We only subscribe to the three events above (see
        # app/core/github_app.py DEFAULT_EVENTS), but GitHub can deliver
        # pings and other housekeeping events too — acknowledge, don't error.
        logger.info("Unhandled GitHub event type=%s delivery=%s", event, delivery_id)

    return {"received": True, "event": event, "delivery_id": delivery_id}
