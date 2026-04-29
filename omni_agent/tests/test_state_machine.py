"""Unit tests for omni_agent.state_machine."""
from __future__ import annotations

import pytest

from omni_agent.state_machine import StateError, StateMachine


def _new(tmp_path):
    sm = StateMachine(tmp_path / "s.db")
    sm.upsert_task(
        id="TASK-1", source_file="memory/tasks/inbox.md", source_line=1,
        raw_text="- [ ] do thing", normalized_text="do thing",
        task_type="backend", priority=2,
    )
    return sm


def test_initial_status(tmp_path):
    sm = _new(tmp_path)
    t = sm.get_task("TASK-1")
    assert t["status"] == "not_started"


def test_legal_transition(tmp_path):
    sm = _new(tmp_path)
    sm.transition("TASK-1", "analyzing", actor="orchestrator")
    sm.transition("TASK-1", "building", actor="orchestrator")
    sm.transition("TASK-1", "evaluating", actor="orchestrator")
    sm.transition("TASK-1", "done", actor="evaluator", reason="ok")
    t = sm.get_task("TASK-1")
    assert t["status"] == "done"
    assert t["closed_at"]


def test_illegal_transition_raises(tmp_path):
    sm = _new(tmp_path)
    with pytest.raises(StateError):
        sm.transition("TASK-1", "done", actor="x")


def test_blocked_then_resume(tmp_path):
    sm = _new(tmp_path)
    sm.transition("TASK-1", "blocked_context", actor="triage", reason="missing X")
    t = sm.get_task("TASK-1")
    assert t["status"] == "blocked_context"
    assert "missing X" in (t["blocked_reason"] or "")
    sm.transition("TASK-1", "analyzing", actor="orchestrator")
    assert sm.get_task("TASK-1")["status"] == "analyzing"


def test_run_lifecycle(tmp_path):
    sm = _new(tmp_path)
    rid = sm.start_run("TASK-1", mode="hybrid", config_snapshot={"persona_mode": "hybrid"})
    sm.add_persona_output(rid, "TASK-1", "analyst", "rule", {"scope": "x"})
    sm.add_artifact(rid, "TASK-1", "file_change", "backend/app/services/x.py", {"action": "create"})
    sm.add_test_execution(rid, "TASK-1", command="pytest", exit_code=0, status="pass", output_excerpt="ok")
    sm.end_run(rid, final_status="done", cohesion_score=92.5, summary="ok")
    last = sm.latest_run_for_task("TASK-1")
    assert last["final_status"] == "done"
    assert last["cohesion_score"] == 92.5


def test_next_runnable_priority_order(tmp_path):
    sm = _new(tmp_path)
    sm.upsert_task(
        id="TASK-2", source_file="memory/tasks/inbox.md", source_line=2,
        raw_text="- [ ] high prio", normalized_text="high",
        task_type="backend", priority=1,
    )
    nxt = sm.next_runnable()
    assert nxt["id"] == "TASK-2"


def test_export_json(tmp_path):
    sm = _new(tmp_path)
    out = sm.export_json(tmp_path / "out.json")
    assert out.exists()
    assert "TASK-1" in out.read_text()
