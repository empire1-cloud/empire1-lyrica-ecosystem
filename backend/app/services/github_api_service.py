"""GitHub REST API wrapper for V2 autonomous features.

Provides safe, async-first wrappers for:
- Creating pull requests from task completions
- Posting check runs with cohesion scores + evidence
- Adding comments to PRs/issues
- Updating commit statuses (legacy fallback)

All methods use installation access tokens (not app JWT) so they operate
within the scope of granted permissions on a specific repository.

Error handling is defensive: network errors, rate limits, and permission
denials are surfaced explicitly to the caller so the task orchestrator can
log/report them without crashing.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx

from app.services.github_app_auth import (
    GitHubAPIError,
    GitHubAppNotConfigured,
    get_installation_token,
)

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"


class GitHubAPIService:
    """Async client for GitHub App → GitHub REST API calls.

    Designed to be instantiated once per request with the installation_id
    so tokens are fetched once and reused for multiple calls in the same
    request context.
    """

    def __init__(self, installation_id: int):
        self.installation_id = installation_id
        self._token: Optional[str] = None

    async def _get_token(self) -> str:
        """Lazy-load and cache the installation token for this request."""
        if self._token:
            return self._token
        token_resp = await get_installation_token(self.installation_id)
        self._token = token_resp.get("token")
        if not self._token:
            raise GitHubAPIError(
                f"Installation token response missing 'token' field: {token_resp}"
            )
        return self._token

    def _auth_headers(self, token: str) -> Dict[str, str]:
        """Standard headers for GitHub API calls."""
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def create_pr(
        self,
        owner: str,
        repo: str,
        *,
        title: str,
        body: str,
        head: str,
        base: str = "main",
        draft: bool = False,
    ) -> Dict[str, Any]:
        """Create a pull request.

        Args:
            owner: GitHub org/user login
            repo: Repository name
            title: PR title
            body: PR description (Markdown)
            head: Branch to merge FROM (can be owner:branch for forks)
            base: Branch to merge INTO (default: main)
            draft: If True, create as draft PR

        Returns:
            PR object from GitHub API response

        Raises:
            GitHubAppNotConfigured: App credentials missing
            GitHubAPIError: GitHub API rejection (4xx/5xx)
        """
        token = await self._get_token()
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls",
                headers=self._auth_headers(token),
                json={
                    "title": title,
                    "body": body,
                    "head": head,
                    "base": base,
                    "draft": draft,
                },
            )
        if resp.status_code >= 400:
            logger.error(
                f"Create PR failed ({resp.status_code}): {resp.text}"
            )
            raise GitHubAPIError(
                f"GitHub rejected create PR for {owner}/{repo}: "
                f"{resp.status_code} {resp.text[:200]}"
            )
        return resp.json()

    async def post_check_run(
        self,
        owner: str,
        repo: str,
        *,
        name: str,
        head_sha: str,
        status: str = "completed",  # queued | in_progress | completed
        conclusion: Optional[str] = None,  # success | failure | neutral | cancelled | skipped | timed_out
        output: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Post a check run against a commit.

        Args:
            owner: GitHub org/user login
            repo: Repository name
            name: Check run name (e.g. "Omni-Agent Task")
            head_sha: Commit SHA to attach the check to
            status: Check status (queued | in_progress | completed)
            conclusion: Final conclusion if status=completed
            output: dict with {title, summary, annotations, images, text}

        Returns:
            Check run object from GitHub API response

        Raises:
            GitHubAppNotConfigured: App credentials missing
            GitHubAPIError: GitHub API rejection (4xx/5xx)
        """
        token = await self._get_token()
        payload: Dict[str, Any] = {
            "name": name,
            "head_sha": head_sha,
            "status": status,
        }
        if conclusion:
            payload["conclusion"] = conclusion
        if output:
            payload["output"] = output

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{GITHUB_API_BASE}/repos/{owner}/{repo}/check-runs",
                headers=self._auth_headers(token),
                json=payload,
            )
        if resp.status_code >= 400:
            logger.error(
                f"Post check run failed ({resp.status_code}): {resp.text}"
            )
            raise GitHubAPIError(
                f"GitHub rejected check run for {owner}/{repo}: "
                f"{resp.status_code} {resp.text[:200]}"
            )
        return resp.json()

    async def add_pr_comment(
        self,
        owner: str,
        repo: str,
        *,
        issue_number: int,
        body: str,
    ) -> Dict[str, Any]:
        """Add a comment to a PR (uses issues API).

        Args:
            owner: GitHub org/user login
            repo: Repository name
            issue_number: PR number (issues API uses PR numbers)
            body: Comment text (Markdown)

        Returns:
            Comment object from GitHub API response

        Raises:
            GitHubAppNotConfigured: App credentials missing
            GitHubAPIError: GitHub API rejection (4xx/5xx)
        """
        token = await self._get_token()
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues/{issue_number}/comments",
                headers=self._auth_headers(token),
                json={"body": body},
            )
        if resp.status_code >= 400:
            logger.error(
                f"Add comment failed ({resp.status_code}): {resp.text}"
            )
            raise GitHubAPIError(
                f"GitHub rejected comment for {owner}/{repo}#{issue_number}: "
                f"{resp.status_code} {resp.text[:200]}"
            )
        return resp.json()

    async def create_commit_status(
        self,
        owner: str,
        repo: str,
        *,
        sha: str,
        state: str,  # pending | success | failure | error
        description: Optional[str] = None,
        context: str = "omni-agent/task",
        target_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a commit status (legacy; use check runs for new code).

        Args:
            owner: GitHub org/user login
            repo: Repository name
            sha: Commit SHA
            state: pending | success | failure | error
            description: Status description (max 140 chars)
            context: Status context (grouped by this in PR details)
            target_url: URL to link from the status

        Returns:
            Status object from GitHub API response

        Raises:
            GitHubAppNotConfigured: App credentials missing
            GitHubAPIError: GitHub API rejection (4xx/5xx)
        """
        token = await self._get_token()
        payload: Dict[str, Any] = {
            "state": state,
            "context": context,
        }
        if description:
            payload["description"] = description[:140]
        if target_url:
            payload["target_url"] = target_url

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{GITHUB_API_BASE}/repos/{owner}/{repo}/statuses/{sha}",
                headers=self._auth_headers(token),
                json=payload,
            )
        if resp.status_code >= 400:
            logger.error(
                f"Create status failed ({resp.status_code}): {resp.text}"
            )
            raise GitHubAPIError(
                f"GitHub rejected status for {owner}/{repo}@{sha}: "
                f"{resp.status_code} {resp.text[:200]}"
            )
        return resp.json()
