"""Tests for V2 GitHub task-completion integration."""
from __future__ import annotations

from types import SimpleNamespace

from omni_agent.github_integration import (
    GitHubIntegrationConfig,
    create_pr_from_task_sync,
)
from omni_agent.orchestrator import Orchestrator


def _config(**github):
    return GitHubIntegrationConfig({"github": github})


def test_canonical_config_and_task_branch(monkeypatch):
    monkeypatch.delenv("OMNI_AGENT_HEAD_BRANCH", raising=False)
    monkeypatch.setenv("OMNI_AGENT_INTERNAL_TOKEN", "test-token")
    config = _config(
        auto_post_pr=True,
        owner="empire1-cloud",
        repo="example",
        installation_id="42",
        branch_prefix="omni-agent",
        post_check_runs=False,
    )
    assert config.is_ready() is True
    assert config.installation_id == 42
    assert config.post_check_runs is False
    assert config.get_task_branch_name("TASK-001") == "omni-agent/TASK-001"


def test_legacy_config_keys_remain_supported(monkeypatch):
    monkeypatch.setenv("OMNI_AGENT_INTERNAL_TOKEN", "test-token")
    config = _config(
        auto_create_pr=True,
        owner="empire1-cloud",
        repo="example",
        installation_id=42,
        include_check_runs=True,
    )
    assert config.is_ready() is True
    assert config.post_check_runs is True


def test_explicit_head_branch_supports_task_placeholder(monkeypatch):
    monkeypatch.setenv("OMNI_AGENT_INTERNAL_TOKEN", "test-token")
    config = _config(
        auto_post_pr=True,
        owner="empire1-cloud",
        repo="example",
        installation_id=42,
        head_branch="work/{task_id}",
    )
    assert config.get_task_branch_name("TASK-002") == "work/TASK-002"


def test_incomplete_config_skips_without_network(monkeypatch):
    def fail_client(*args, **kwargs):
        raise AssertionError("network client should not be constructed")

    monkeypatch.setattr("omni_agent.github_integration.httpx.Client", fail_client)
    result = create_pr_from_task_sync(
        task_id="TASK-003",
        config=_config(auto_post_pr=True),
    )
    assert result is None


def test_sync_client_posts_evidence_payload(monkeypatch):
    monkeypatch.setenv("OMNI_AGENT_INTERNAL_TOKEN", "test-token")
    captured = {}

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return {
                "success": True,
                "pr_number": 17,
                "pr_url": "https://github.com/empire1-cloud/example/pull/17",
                "check_run_id": 88,
            }

    class Client:
        def __init__(self, **kwargs):
            captured["client_kwargs"] = kwargs

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def post(self, url, json, headers):
            captured["url"] = url
            captured["payload"] = json
            captured["headers"] = headers
            return Response()

    monkeypatch.setattr("omni_agent.github_integration.httpx.Client", Client)
    config = _config(
        auto_post_pr=True,
        owner="empire1-cloud",
        repo="example",
        installation_id=42,
        api_base_url="https://api.example.test/",
        post_check_runs=True,
    )
    result = create_pr_from_task_sync(
        task_id="TASK-004",
        config=config,
        cohesion_score=96.5,
        title="Evidence title",
        body="Evidence body",
    )

    assert result["pr_number"] == 17
    assert captured["url"] == "https://api.example.test/api/github/create-pr"
    assert captured["payload"]["head"] == "omni-agent/TASK-004"
    assert captured["payload"]["cohesion_score"] == 96.5
    assert captured["payload"]["title"] == "Evidence title"
    assert captured["payload"]["body"] == "Evidence body"
    assert captured["payload"]["include_check_run"] is True
    assert captured["headers"] == {"Authorization": "Bearer test-token"}


def test_orchestrator_attaches_and_persists_pr(monkeypatch):
    monkeypatch.setenv("OMNI_AGENT_INTERNAL_TOKEN", "test-token")
    artifacts = []

    orchestrator = object.__new__(Orchestrator)
    orchestrator.config = {
        "github": {
            "auto_post_pr": True,
            "owner": "empire1-cloud",
            "repo": "example",
            "installation_id": 42,
        }
    }
    orchestrator.state = SimpleNamespace(
        add_artifact=lambda *args: artifacts.append(args)
    )
    orchestrator.generate_pr_preview = lambda task_id: {
        "markdown": "Evidence body",
        "meta": {"title": "Evidence title"},
    }

    def fake_create(**kwargs):
        assert kwargs["cohesion_score"] == 99
        assert kwargs["title"] == "Evidence title"
        assert kwargs["body"] == "Evidence body"
        return {
            "success": True,
            "pr_number": 21,
            "pr_url": "https://github.com/empire1-cloud/example/pull/21",
            "check_run_id": 90,
        }

    monkeypatch.setattr(
        "omni_agent.orchestrator.create_pr_from_task_sync",
        fake_create,
    )

    out = {}
    orchestrator._attach_github_pr(
        task_id="TASK-005",
        run_id="run-5",
        cohesion_score=99,
        out=out,
    )

    assert out["github_pr"]["status"] == "created"
    assert out["github_pr"]["pr_number"] == 21
    assert artifacts[0][2] == "github_pull_request"
    assert artifacts[0][3].endswith("/pull/21")
