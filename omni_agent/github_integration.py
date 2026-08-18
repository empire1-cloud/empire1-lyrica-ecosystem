"""GitHub integration layer for V2 autonomous features.

Provides async HTTP client methods to call the omni-agent backend's GitHub
API endpoints (POST /api/github/create-pr, etc.) during task completion.

This acts as a bridge between the local omni_agent orchestrator and the
backend FastAPI service, allowing the local CLI to trigger GitHub actions
on behalf of the current installation.

Design notes:
- All methods are non-blocking; failures log warnings but don't crash the task.
- Respects config.github.auto_create_pr flag to allow opt-out.
- Handles missing credentials gracefully (silently skips PR posting).
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger("omni_agent.github_integration")


class GitHubIntegrationConfig:
    """Parsed GitHub integration config from omni_agent/config.yaml."""

    def __init__(self, config: Dict[str, Any]):
        gh_cfg = config.get("github", {})
        self.enabled = gh_cfg.get("auto_create_pr", False)
        self.owner = gh_cfg.get("owner")
        self.repo = gh_cfg.get("repo")
        self.installation_id = gh_cfg.get("installation_id")
        self.base_branch = gh_cfg.get("base_branch", "main")
        self.branch_prefix = gh_cfg.get("branch_prefix", "omni-agent")
        self.api_base_url = (
            gh_cfg.get("api_base_url")
            or os.environ.get("OMNI_AGENT_API_URL")
            or "http://localhost:8000"
        )
        self.include_check_runs = gh_cfg.get("include_check_runs", True)
        self.draft_initial = gh_cfg.get("draft_initial", False)

    def is_ready(self) -> bool:
        """True if all required fields are configured."""
        return bool(self.owner and self.repo and self.installation_id and self.enabled)

    def get_task_branch_name(self, task_id: str) -> str:
        """Generate a branch name for a task (e.g., 'omni-agent/TASK-001')."""
        return f"{self.branch_prefix}/{task_id}"


async def create_pr_from_task(
    *,
    task_id: str,
    config: GitHubIntegrationConfig,
    cohesion_score: Optional[float] = None,
) -> Optional[Dict[str, Any]]:
    """Autonomously create a PR from a completed task.

    Calls the backend's POST /api/github/create-pr endpoint to open a PR
    with the task's evidence and results.

    Args:
        task_id: Omni-Agent task ID (e.g., TASK-001)
        config: Parsed GitHub integration config
        cohesion_score: Task's final cohesion score (for logging)

    Returns:
        Response dict with keys: {success, pr_number, pr_url, check_run_id, error}
        or None if PR creation is disabled in config

    Note:
        - Failures are logged but do not raise exceptions
        - Missing config fields cause silent skip (non-fatal)
        - Network errors are caught and logged
    """

    if not config.is_ready():
        logger.debug(
            f"PR creation disabled or incomplete config: enabled={config.enabled}, "
            f"owner={config.owner}, repo={config.repo}, installation_id={config.installation_id}"
        )
        return None

    head_branch = config.get_task_branch_name(task_id)
    api_url = f"{config.api_base_url}/api/github/create-pr"

    payload = {
        "task_id": task_id,
        "owner": config.owner,
        "repo": config.repo,
        "head": head_branch,
        "base": config.base_branch,
        "installation_id": config.installation_id,
        "draft": config.draft_initial,
        "include_check_run": config.include_check_runs,
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(api_url, json=payload)
        if resp.status_code >= 400:
            logger.warning(
                f"PR creation failed ({resp.status_code}): {task_id} → {config.owner}/{config.repo}. "
                f"Response: {resp.text[:200]}"
            )
            return None

        result = resp.json()
        if result.get("success"):
            pr_url = result.get("pr_url")
            pr_number = result.get("pr_number")
            logger.info(f"PR created for {task_id}: {config.owner}/{config.repo}#{pr_number} ({pr_url})")
            return result
        else:
            logger.warning(
                f"PR creation rejected: {task_id}. Error: {result.get('error')}. "
                f"Code: {result.get('error_code')}"
            )
            return None

    except httpx.TimeoutException:
        logger.warning(f"PR creation timeout for {task_id}: API not responding within 15s")
        return None
    except httpx.NetworkError as e:
        logger.warning(f"PR creation network error for {task_id}: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error during PR creation for {task_id}: {e}")
        return None
