"""Unit tests for omni_agent.triage."""
from __future__ import annotations

from omni_agent.scanner import ParsedTask
from omni_agent.triage import triage_task


CFG = {
    "triage": {
        "type_keywords": {
            "backend": ["api", "endpoint", "service"],
            "frontend": ["react", "component"],
            "docs": ["documentation", "readme"],
            "tests": ["pytest", "test"],
        },
        "priority_keywords": {
            1: ["urgent", "p0"],
            2: ["high", "p1"],
            3: ["medium"],
        },
    }
}


def _t(text: str) -> ParsedTask:
    return ParsedTask(
        id="TASK-1", source_file="x.md", line=1, text=text, raw_text=text,
        pattern="checkbox", tags=[], explicit_id=None,
    )


def test_classifies_backend():
    r = triage_task(_t("Create a new endpoint for users"), CFG)
    assert r.task_type == "backend"


def test_classifies_frontend():
    r = triage_task(_t("Build a react component for login"), CFG)
    assert r.task_type == "frontend"


def test_classifies_docs():
    r = triage_task(_t("Update the README documentation"), CFG)
    assert r.task_type == "docs"


def test_priority_urgent():
    r = triage_task(_t("urgent: fix the api"), CFG)
    assert r.priority == 1


def test_default_priority():
    r = triage_task(_t("just a thing"), CFG)
    assert r.priority == 3


def test_persona_order_default():
    r = triage_task(_t("anything"), CFG)
    assert r.persona_order == ["analyst", "developer", "evaluator"]


def test_path_hints_extracted():
    r = triage_task(_t("Create backend/app/services/health_service.py with status"), CFG)
    assert "backend/app/services/health_service.py" in r.path_hints


def test_missing_context_for_integration():
    r = triage_task(_t("Integrate with payment provider TBD"), CFG)
    assert r.missing_context  # non-empty
