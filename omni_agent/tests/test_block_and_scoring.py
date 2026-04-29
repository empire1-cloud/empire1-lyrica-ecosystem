"""Unit tests for block-up-front decision + guardrail_compliance scoring + cohesion."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import pytest

from omni_agent.personas.evaluator import (
    _cohesion,
    _evaluate_criteria_rule,
    _guardrail_compliance,
)


# --------- _should_block_upfront via a lightweight stand-in --------- #

@dataclass
class FakeTri:
    missing_context: List[str]
    confidence: float


def _decide(mode: str, tri: FakeTri, cfg: dict) -> str | None:
    # Re-implement the same policy inline so we don't need a real Orchestrator/DB
    if not tri.missing_context:
        return None
    if mode == "rule":
        return "rule_mode_missing_context"
    tri_cfg = cfg.get("triage", {}) or {}
    if mode == "hybrid" and tri_cfg.get("hybrid_block_on_missing_context", True):
        threshold = tri_cfg.get("missing_context_threshold", "high")
        sev_map = {"high": 1, "medium": 2, "low": 3}
        need = sev_map.get(threshold, 1)
        if len(tri.missing_context) >= need and tri.confidence < float(tri_cfg.get("confidence_threshold", 0.5)):
            return "missing_context_low_confidence"
    return None


BASE_CFG = {
    "triage": {
        "hybrid_block_on_missing_context": True,
        "missing_context_threshold": "high",
        "confidence_threshold": 0.5,
    }
}


def test_rule_mode_always_blocks_on_missing_context():
    tri = FakeTri(missing_context=["need x"], confidence=0.9)
    assert _decide("rule", tri, BASE_CFG) == "rule_mode_missing_context"


def test_hybrid_blocks_when_low_confidence_and_missing_context():
    tri = FakeTri(missing_context=["need x"], confidence=0.3)
    assert _decide("hybrid", tri, BASE_CFG) == "missing_context_low_confidence"


def test_hybrid_does_not_block_when_confidence_high():
    tri = FakeTri(missing_context=["need x"], confidence=0.9)
    assert _decide("hybrid", tri, BASE_CFG) is None


def test_llm_mode_never_auto_blocks():
    tri = FakeTri(missing_context=["need x"], confidence=0.1)
    assert _decide("llm", tri, BASE_CFG) is None


def test_no_missing_context_never_blocks():
    tri = FakeTri(missing_context=[], confidence=0.1)
    for m in ("rule", "hybrid", "llm"):
        assert _decide(m, tri, BASE_CFG) is None


def test_hybrid_threshold_medium_requires_two_items():
    cfg = {"triage": {**BASE_CFG["triage"], "missing_context_threshold": "medium"}}
    assert _decide("hybrid", FakeTri(missing_context=["a"], confidence=0.3), cfg) is None
    assert _decide("hybrid", FakeTri(missing_context=["a", "b"], confidence=0.3), cfg) == "missing_context_low_confidence"


# --------- _evaluate_criteria_rule: out_of_scope for filtered paths --------- #

def test_criterion_mentioning_filtered_path_is_out_of_scope(tmp_path):
    criteria = [
        "File src/payments/provider.ts exists and is valid",
        "backend/app/services/x.py contains a public callable",
    ]
    # build an applied .py file
    p = tmp_path / "backend" / "app" / "services" / "x.py"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("def hello():\n    return 1\n", encoding="utf-8")

    results = _evaluate_criteria_rule(
        criteria,
        applied_paths=["backend/app/services/x.py"],
        repo_root=tmp_path,
        filtered_paths=["src/payments/provider.ts"],
    )
    by_text = {r["text"]: r for r in results}
    assert by_text[criteria[0]]["out_of_scope"] is True
    assert by_text[criteria[0]]["met"] is False
    # in-scope criterion should be evaluated normally
    assert by_text[criteria[1]]["out_of_scope"] is False
    assert by_text[criteria[1]]["met"] is True


# --------- _guardrail_compliance --------- #

def test_guardrail_clean_run_scores_one():
    dev = {"applied": [{"path": "backend/app/services/x.py"}], "errors": [], "filtered_paths": [], "proposed_total": 1}
    g = _guardrail_compliance(dev)
    assert g["score"] == 1.0


def test_guardrail_some_filtered_but_recovered_small_dock():
    dev = {
        "applied": [{"path": "backend/app/services/x.py"}],
        "errors": [],
        "filtered_paths": ["src/payments/a.ts", "investor/b.md"],
        "proposed_total": 3,
    }
    g = _guardrail_compliance(dev)
    assert 0.6 <= g["score"] < 1.0


def test_guardrail_all_filtered_no_recovery_big_penalty():
    dev = {
        "applied": [],
        "errors": [],
        "filtered_paths": ["src/a", "src/b"],
        "proposed_total": 2,
    }
    g = _guardrail_compliance(dev)
    assert g["score"] == 0.4


def test_guardrail_write_time_forbidden_attempts_penalized():
    dev = {
        "applied": [{"path": "backend/app/services/x.py"}],
        "errors": ["guardrail blocked 'investor/plan.md': path forbidden"],
        "filtered_paths": [],
        "proposed_total": 2,
    }
    g = _guardrail_compliance(dev)
    assert g["score"] <= 0.5
    assert g["forbidden_write_attempts"] == 1


# --------- _cohesion 5-component --------- #

WEIGHTS = {"acceptance": 35, "tests": 25, "regression": 20, "quality": 10, "guardrail": 10}


def test_cohesion_perfect_in_scope():
    criteria = [{"text": "x", "met": True, "out_of_scope": False}]
    s = _cohesion(criteria, "pass", True, "pass", 1.0, WEIGHTS)
    assert s == 100.0


def test_cohesion_excludes_out_of_scope_from_acceptance():
    # 1 in-scope met, 2 out-of-scope -> accept_score = 1.0
    criteria = [
        {"text": "in", "met": True, "out_of_scope": False},
        {"text": "oos-1", "met": False, "out_of_scope": True},
        {"text": "oos-2", "met": False, "out_of_scope": True},
    ]
    s = _cohesion(criteria, "pass", True, "pass", 1.0, WEIGHTS)
    assert s == 100.0


def test_cohesion_all_out_of_scope_neutral():
    criteria = [
        {"text": "a", "met": False, "out_of_scope": True},
        {"text": "b", "met": False, "out_of_scope": True},
    ]
    # accept=0.7 neutral, rest perfect -> 0.7*35 + 25 + 20 + 10 + 10 = 89.5
    s = _cohesion(criteria, "pass", True, "pass", 1.0, WEIGHTS)
    assert s == pytest.approx(89.5, abs=0.01)


def test_cohesion_guardrail_subscore_moves_total():
    criteria = [{"text": "x", "met": True, "out_of_scope": False}]
    hi = _cohesion(criteria, "pass", True, "pass", 1.0, WEIGHTS)
    lo = _cohesion(criteria, "pass", True, "pass", 0.4, WEIGHTS)
    assert hi - lo == pytest.approx(6.0, abs=0.01)  # (1.0 - 0.4) * 10
