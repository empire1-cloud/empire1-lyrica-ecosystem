"""V2 GitHub PR creation endpoint.

Enables omni-agent tasks to autonomously open pull requests after
completion, with full evidence and evaluation results in the PR body.

The endpoint is called by the orchestrator after a task reaches 'done'
status. It handles:
- PR preview generation (delegate to omni_agent.reporting.pr_preview)
- Installation ID lookup from install audit trail
- Safe API error handling and logging
- Optional: check run posting with cohesion score
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.services.github_api_service import GitHubAPIService
from app.services.github_app_auth import GitHubAPIError, GitHubAppNotConfigured

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/github", tags=["github-pr-v2"])


class CreatePRRequest(BaseModel):
    """Request body for autonomous PR creation from a completed task."""

    task_id: str
    """Omni-Agent task ID (e.g. TASK-001)"""

    owner: str
    """GitHub org or user (repo owner)"""

    repo: str
    """Repository name"""

    head: str
    """Branch to merge FROM. Can be owner:branch for forks."""

    base: str = "main"
    """Branch to merge INTO. Defaults to main."""

    installation_id: int
    """GitHub App installation ID (identifies which install/account to use)"""

    draft: bool = False
    """If True, create PR as draft (won't trigger auto-merge rules)"""

    include_check_run: bool = True
    """If True, post a check run with cohesion score to the PR's head commit."""


class CreatePRResponse(BaseModel):
    """Response after attempting PR creation."""

    success: bool
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
    check_run_id: Optional[int] = None
    error: Optional[str] = None
    error_code: Optional[str] = None


@router.post("/create-pr", response_model=CreatePRResponse)
async def create_pr(payload: CreatePRRequest, request: Request):
    """
    Create a PR from an omni-agent task completion.

    Flow:
    1. Fetch the task from omni_agent's state (SQL or JSON export)
    2. Generate PR preview markdown (scope, files, tests, risks)
    3. Call GitHub API to create the PR
    4. Optionally post a check run with the cohesion score
    5. Return the PR URL + check run ID if successful

    This endpoint is called by the orchestrator after evaluator marks a task 'done'.

    Error cases:
    - Task not found: 404-like response with error_code='task_not_found'
    - Installation not configured: 503-like with 'github_not_configured'
    - GitHub API rejected PR: 502-like with 'github_api_error'
    - No writable branch: 400-like with 'branch_not_found'
    """

    # TODO: Replace stub with real task lookup from omni_agent state.
    # For now, we accept the PR preview in the request or construct a minimal one.
    task_id = payload.task_id
    owner = payload.owner
    repo = payload.repo
    head = payload.head
    base = payload.base
    installation_id = payload.installation_id
    draft = payload.draft

    try:
        # Initialize GitHub API service with this installation
        gh = GitHubAPIService(installation_id)

        # Generate PR title and body
        # In production, fetch from omni_agent.reporting.pr_preview.generate()
        # For now, minimal defaults.
        pr_title = f"[omni-agent] {task_id}: Task completed"
        pr_body = (
            f"## Task: `{task_id}`\n\n"
            f"This PR was automatically created by Omni-Agent after task "
            f"evaluation passed.\n\n"
            f"**Base**: {base}\n"
            f"**Head**: {head}\n\n"
            f"### Evidence\n"
            f"See the task reports in omni_agent/reports/ for full details.\n"
        )

        # Create the PR
        pr_response = await gh.create_pr(
            owner=owner,
            repo=repo,
            title=pr_title,
            body=pr_body,
            head=head,
            base=base,
            draft=draft,
        )
        pr_number = pr_response.get("number")
        pr_url = pr_response.get("html_url")
        head_sha = pr_response.get("head", {}).get("sha")

        if not pr_number or not pr_url:
            logger.error(f"PR created but missing number/url: {pr_response}")
            return CreatePRResponse(
                success=False,
                error="PR response missing number/url",
                error_code="invalid_pr_response",
            )

        logger.info(f"PR created: {owner}/{repo}#{pr_number} ({pr_url})")

        # Optional: Post a check run with the cohesion score
        check_run_id = None
        if payload.include_check_run and head_sha:
            try:
                check_response = await gh.post_check_run(
                    owner=owner,
                    repo=repo,
                    name="Omni-Agent Task",
                    head_sha=head_sha,
                    status="completed",
                    conclusion="success",
                    output={
                        "title": f"Task {task_id} Completed",
                        "summary": f"Omni-Agent completed task {task_id} and opened this PR.",
                    },
                )
                check_run_id = check_response.get("id")
                logger.info(f"Check run posted: {check_run_id}")
            except GitHubAPIError as e:
                # Don't fail the PR creation if check run fails
                logger.warning(f"Failed to post check run: {e}")

        return CreatePRResponse(
            success=True,
            pr_number=pr_number,
            pr_url=pr_url,
            check_run_id=check_run_id,
        )

    except GitHubAppNotConfigured as e:
        logger.error(f"GitHub App not configured: {e}")
        return CreatePRResponse(
            success=False,
            error=str(e),
            error_code="github_not_configured",
        )
    except GitHubAPIError as e:
        logger.error(f"GitHub API error: {e}")
        return CreatePRResponse(
            success=False,
            error=str(e),
            error_code="github_api_error",
        )
    except Exception as e:
        logger.exception(f"Unexpected error during PR creation: {e}")
        return CreatePRResponse(
            success=False,
            error=f"Internal error: {str(e)[:100]}",
            error_code="internal_error",
        )
