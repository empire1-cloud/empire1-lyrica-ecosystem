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

import hmac
import logging
import os
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

    title: Optional[str] = None
    """Evidence-generated PR title from the orchestrator."""

    body: Optional[str] = None
    """Evidence-generated PR body from the orchestrator."""

    cohesion_score: Optional[float] = None
    """Final task cohesion score for the check run and fallback body."""

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
    1. Authenticate the orchestrator's internal bearer token
    2. Receive the completed task's evidence-generated PR preview
    3. Call GitHub API with the requested App installation
    4. Optionally post a check run with the cohesion score
    5. Return the PR URL + check run ID if successful

    This endpoint is called by the orchestrator after evaluator marks a task 'done'.

    Error cases:
    - Caller token missing on server: 503 with 'internal_auth_not_configured'
    - Caller token rejected: 401 with 'unauthorized'
    - Installation not configured: response with 'github_not_configured'
    - GitHub API rejected PR: response with 'github_api_error'
    """

    expected_token = os.environ.get("OMNI_AGENT_INTERNAL_TOKEN")
    if not expected_token:
        logger.error("OMNI_AGENT_INTERNAL_TOKEN is not configured")
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "error": "Internal caller authentication is not configured",
                "error_code": "internal_auth_not_configured",
            },
        )

    authorization = request.headers.get("authorization", "")
    scheme, _, supplied_token = authorization.partition(" ")
    authenticated = (
        scheme.lower() == "bearer"
        and bool(supplied_token)
        and hmac.compare_digest(supplied_token, expected_token)
    )
    if not authenticated:
        logger.warning("Rejected unauthorized autonomous PR request")
        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "error": "Unauthorized",
                "error_code": "unauthorized",
            },
        )

    # The orchestrator generates the authoritative preview from its local
    # evidence store and sends it here, keeping this API stateless.
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

        # Prefer the evidence-rich preview produced by the orchestrator.
        # Fallback content keeps direct API callers backward compatible.
        pr_title = (payload.title or f"[omni-agent] {task_id}: Task completed")[:256]
        score_line = (
            f"**Cohesion score**: {payload.cohesion_score}\n"
            if payload.cohesion_score is not None
            else ""
        )
        pr_body = payload.body or (
            f"## Task: `{task_id}`\n\n"
            f"This PR was automatically created by Omni-Agent after task "
            f"evaluation passed.\n\n"
            f"**Base**: {base}\n"
            f"**Head**: {head}\n"
            f"{score_line}\n"
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
                        "summary": (
                            f"Omni-Agent completed task {task_id} and opened this PR."
                            + (
                                f" Cohesion score: {payload.cohesion_score}."
                                if payload.cohesion_score is not None
                                else ""
                            )
                        ),
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
