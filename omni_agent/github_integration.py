"""GitHub integration layer for V2 autonomous features.

Provides synchronous and asynchronous HTTP clients for calling the
Omni-Agent backend's GitHub API endpoints during task completion.

The orchestrator is synchronous, so it uses create_pr_from_task_sync().
Async callers can use create_pr_from_task(). Both paths are non-fatal:
GitHub failures are logged and returned as None without changing a task's
successful evaluation result.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger("omni_agent.github_integration")


def _coerce_installation_id(value: Any) -> Optional[int]:
    """Return a positive installation ID or None for incomplete config."""
    if value in (None, ""):
        return None
    try:
        installation_id = int(value)
    except (TypeError, ValueError):
        return None
    return installation_id if installation_id > 0 else None


class GitHubIntegrationConfig:
    """Parsed GitHub integration config from omni_agent/config.yaml."""

    def __init__(self, config: Dict[str, Any]):
        gh_cfg = config.get("github", {}) or {}

        enabled = gh_cfg.get("auto_post_pr")
        if enabled is None:
            enabled = gh_cfg.get("auto_create_pr", False)
        self.enabled = bool(enabled)

        self.owner = gh_cfg.get("owner") or os.environ.get("OMNI_AGENT_GITHUB_OWNER")
        self.repo = gh_cfg.get("repo") or os.environ.get("OMNI_AGENT_GITHUB_REPO")
        self.installation_id = _coerce_installation_id(
            gh_cfg.get("installation_id")
            or os.environ.get("OMNI_AGENT_GITHUB_INSTALLATION_ID")
        )
        self.base_branch = gh_cfg.get("base_branch") or "main"
        self.branch_prefix = (gh_cfg.get("branch_prefix") or "omni-agent").strip("/")
        self.head_branch = (
            gh_cfg.get("head_branch")
            or os.environ.get("OMNI_AGENT_HEAD_BRANCH")
        )
        self.api_base_url = (
            gh_cfg.get("api_base_url")
            or os.environ.get("OMNI_AGENT_API_URL")
            or "http://localhost:8000"
        ).rstrip("/")
        self.api_token_env = (
            gh_cfg.get("api_token_env")
            or "OMNI_AGENT_INTERNAL_TOKEN"
        )
        self.api_token = os.environ.get(self.api_token_env)

        post_check_runs = gh_cfg.get("post_check_runs")
        if post_check_runs is None:
            post_check_runs = gh_cfg.get("include_check_runs", True)
        self.post_check_runs = bool(post_check_runs)
        # Backward-compatible attribute for callers created before auto_post_pr.
        self.include_check_runs = self.post_check_runs
        self.draft_initial = bool(gh_cfg.get("draft_initial", False))

    def is_ready(self) -> bool:
        """True when auto-posting is enabled and all required fields exist."""
        return bool(
            self.enabled
            and self.owner
            and self.repo
            and self.installation_id
            and self.api_token
        )

    def get_task_branch_name(self, task_id: str) -> str:
        """Resolve the already-pushed head branch for a task."""
        if self.head_branch:
            return self.head_branch.replace("{task_id}", task_id)
        return f"{self.branch_prefix}/{task_id}"


def _build_payload(
    *,
    task_id: str,
    config: GitHubIntegrationConfig,
    cohesion_score: Optional[float],
    title: Optional[str],
    body: Optional[str],
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "task_id": task_id,
        "owner": config.owner,
        "repo": config.repo,
        "head": config.get_task_branch_name(task_id),
        "base": config.base_branch,
        "installation_id": config.installation_id,
        "draft": config.draft_initial,
        "include_check_run": config.post_check_runs,
    }
    if cohesion_score is not None:
        payload["cohesion_score"] = cohesion_score
    if title:
        payload["title"] = title
    if body:
        payload["body"] = body
    return payload


def _parse_response(
    response: httpx.Response,
    *,
    task_id: str,
    config: GitHubIntegrationConfig,
) -> Optional[Dict[str, Any]]:
    if response.status_code >= 400:
        logger.warning(
            "PR creation failed (%s): %s -> %s/%s",
            response.status_code,
            task_id,
            config.owner,
            config.repo,
        )
        return None

    try:
        result = response.json()
    except ValueError:
        logger.warning("PR creation returned invalid JSON for %s", task_id)
        return None

    if result.get("success") and result.get("pr_url"):
        logger.info(
            "PR created for %s: %s/%s#%s (%s)",
            task_id,
            config.owner,
            config.repo,
            result.get("pr_number"),
            result.get("pr_url"),
        )
        return result

    logger.warning(
        "PR creation rejected for %s: code=%s",
        task_id,
        result.get("error_code"),
    )
    return None


def create_pr_from_task_sync(
    *,
    task_id: str,
    config: GitHubIntegrationConfig,
    cohesion_score: Optional[float] = None,
    title: Optional[str] = None,
    body: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Create a pull request from the synchronous orchestrator."""
    if not config.is_ready():
        logger.debug("PR creation disabled or GitHub config incomplete")
        return None

    payload = _build_payload(
        task_id=task_id,
        config=config,
        cohesion_score=cohesion_score,
        title=title,
        body=body,
    )
    api_url = f"{config.api_base_url}/api/github/create-pr"

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.post(
                api_url,
                json=payload,
                headers={"Authorization": f"Bearer {config.api_token}"},
            )
        return _parse_response(response, task_id=task_id, config=config)
    except httpx.TimeoutException:
        logger.warning("PR creation timeout for %s", task_id)
    except httpx.RequestError as exc:
        logger.warning("PR creation network error for %s: %s", task_id, exc)
    except Exception as exc:  # pragma: no cover - final non-fatal boundary
        logger.exception("Unexpected PR creation error for %s: %s", task_id, exc)
    return None


async def create_pr_from_task(
    *,
    task_id: str,
    config: GitHubIntegrationConfig,
    cohesion_score: Optional[float] = None,
    title: Optional[str] = None,
    body: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Create a pull request from an asynchronous caller."""
    if not config.is_ready():
        logger.debug("PR creation disabled or GitHub config incomplete")
        return None

    payload = _build_payload(
        task_id=task_id,
        config=config,
        cohesion_score=cohesion_score,
        title=title,
        body=body,
    )
    api_url = f"{config.api_base_url}/api/github/create-pr"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                api_url,
                json=payload,
                headers={"Authorization": f"Bearer {config.api_token}"},
            )
        return _parse_response(response, task_id=task_id, config=config)
    except httpx.TimeoutException:
        logger.warning("PR creation timeout for %s", task_id)
    except httpx.RequestError as exc:
        logger.warning("PR creation network error for %s: %s", task_id, exc)
    except Exception as exc:  # pragma: no cover - final non-fatal boundary
        logger.exception("Unexpected PR creation error for %s: %s", task_id, exc)
    return None
