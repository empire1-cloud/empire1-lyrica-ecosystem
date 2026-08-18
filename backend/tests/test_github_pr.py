"""Tests for the autonomous GitHub PR endpoint."""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.pop("MONGO_URL", None)
os.environ.pop("STRIPE_SECRET_KEY", None)

from fastapi.testclient import TestClient  # noqa: E402

from app.routers import github_pr  # noqa: E402
from server import app  # noqa: E402


client = TestClient(app)


def test_create_pr_uses_orchestrator_evidence(monkeypatch):
    monkeypatch.setenv("OMNI_AGENT_INTERNAL_TOKEN", "test-token")
    calls = {}

    class FakeGitHubAPIService:
        def __init__(self, installation_id):
            calls["installation_id"] = installation_id

        async def create_pr(self, **kwargs):
            calls["create_pr"] = kwargs
            return {
                "number": 17,
                "html_url": "https://github.com/empire1-cloud/example/pull/17",
                "head": {"sha": "abc123"},
            }

        async def post_check_run(self, **kwargs):
            calls["check_run"] = kwargs
            return {"id": 88}

    monkeypatch.setattr(github_pr, "GitHubAPIService", FakeGitHubAPIService)

    response = client.post(
        "/api/github/create-pr",
        json={
            "task_id": "TASK-001",
            "owner": "empire1-cloud",
            "repo": "example",
            "head": "omni-agent/TASK-001",
            "base": "main",
            "installation_id": 42,
            "title": "Evidence title",
            "body": "Evidence body",
            "cohesion_score": 97.5,
            "include_check_run": True,
        },
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "pr_number": 17,
        "pr_url": "https://github.com/empire1-cloud/example/pull/17",
        "check_run_id": 88,
        "error": None,
        "error_code": None,
    }
    assert calls["installation_id"] == 42
    assert calls["create_pr"]["title"] == "Evidence title"
    assert calls["create_pr"]["body"] == "Evidence body"
    assert "97.5" in calls["check_run"]["output"]["summary"]


def test_create_pr_fallback_body_is_backward_compatible(monkeypatch):
    monkeypatch.setenv("OMNI_AGENT_INTERNAL_TOKEN", "test-token")
    calls = {}

    class FakeGitHubAPIService:
        def __init__(self, installation_id):
            pass

        async def create_pr(self, **kwargs):
            calls.update(kwargs)
            return {
                "number": 18,
                "html_url": "https://github.com/empire1-cloud/example/pull/18",
                "head": {"sha": None},
            }

    monkeypatch.setattr(github_pr, "GitHubAPIService", FakeGitHubAPIService)

    response = client.post(
        "/api/github/create-pr",
        json={
            "task_id": "TASK-002",
            "owner": "empire1-cloud",
            "repo": "example",
            "head": "omni-agent/TASK-002",
            "installation_id": 42,
            "include_check_run": False,
        },
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert calls["title"].startswith("[omni-agent] TASK-002")
    assert "TASK-002" in calls["body"]


def test_create_pr_rejects_unauthorized_call(monkeypatch):
    monkeypatch.setenv("OMNI_AGENT_INTERNAL_TOKEN", "test-token")

    response = client.post(
        "/api/github/create-pr",
        json={
            "task_id": "TASK-003",
            "owner": "empire1-cloud",
            "repo": "example",
            "head": "omni-agent/TASK-003",
            "installation_id": 42,
        },
    )

    assert response.status_code == 401
    assert response.json()["error_code"] == "unauthorized"


def test_create_pr_fails_closed_without_server_token(monkeypatch):
    monkeypatch.delenv("OMNI_AGENT_INTERNAL_TOKEN", raising=False)

    response = client.post(
        "/api/github/create-pr",
        json={
            "task_id": "TASK-004",
            "owner": "empire1-cloud",
            "repo": "example",
            "head": "omni-agent/TASK-004",
            "installation_id": 42,
        },
    )

    assert response.status_code == 503
    assert response.json()["error_code"] == "internal_auth_not_configured"
