"""ROI tracker: compute sellable metrics from state DB.

Metrics produced:
    tasks_completed, tasks_total, avg_cohesion_score, blocked_rate, test_pass_rate,
    estimated_hours_saved, estimated_cost_saved

Assumptions are configurable under config['roi']:
    minutes_per_task_manual  (default 60)
    dev_hourly_rate          (default 100)
    currency                 (default "USD")
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

from omni_agent.state_machine import StateMachine


def _cfg(config: Dict[str, Any]) -> Tuple[float, float, str]:
    roi = (config or {}).get("roi", {}) or {}
    return (
        float(roi.get("minutes_per_task_manual", 60)),
        float(roi.get("dev_hourly_rate", 100)),
        str(roi.get("currency", "USD")),
    )


def _window_clause(since: Optional[datetime]) -> Tuple[str, tuple]:
    if not since:
        return "", ()
    return " WHERE started_at >= ?", (since.isoformat(),)


def compute_roi(state: StateMachine, config: Dict[str, Any], *, since: Optional[datetime] = None) -> Dict[str, Any]:
    minutes_per_task, hourly_rate, currency = _cfg(config)

    with state.conn() as c:
        # All runs (optionally windowed)
        where_runs, args_runs = _window_clause(since)
        runs = [dict(r) for r in c.execute(
            f"SELECT * FROM task_runs{where_runs} ORDER BY started_at DESC", args_runs
        ).fetchall()]
        done_task_ids = {
            row["task_id"] for row in c.execute(
                "SELECT DISTINCT task_id FROM task_runs WHERE final_status='done'"
                + (" AND started_at >= ?" if since else ""),
                (since.isoformat(),) if since else (),
            ).fetchall()
        }
        # Tasks present
        tasks_total = c.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        # Blocked count (current status)
        blocked_count = c.execute(
            "SELECT COUNT(*) FROM tasks WHERE status IN ('blocked_context','blocked_dependency')"
        ).fetchone()[0]
        # Test pass rate: out of all test_executions (windowed)
        if since:
            tp = c.execute(
                "SELECT status, COUNT(*) as n FROM test_executions WHERE ts >= ? GROUP BY status",
                (since.isoformat(),),
            ).fetchall()
        else:
            tp = c.execute(
                "SELECT status, COUNT(*) as n FROM test_executions GROUP BY status"
            ).fetchall()
        test_counts = {row["status"]: row["n"] for row in tp}

    tasks_completed = len(done_task_ids)
    cohesion_scores = [r["cohesion_score"] for r in runs if r.get("cohesion_score") is not None]
    avg_cohesion = round(sum(cohesion_scores) / len(cohesion_scores), 2) if cohesion_scores else 0.0

    blocked_rate = round(blocked_count / tasks_total, 3) if tasks_total else 0.0

    passed = test_counts.get("pass", 0)
    failed = test_counts.get("fail", 0)
    test_pass_rate = round(passed / (passed + failed), 3) if (passed + failed) else None

    hours_saved = round(tasks_completed * (minutes_per_task / 60.0), 2)
    cost_saved = round(hours_saved * hourly_rate, 2)

    return {
        "tasks_completed": tasks_completed,
        "tasks_total": tasks_total,
        "avg_cohesion_score": avg_cohesion,
        "blocked_rate": blocked_rate,
        "blocked_count": blocked_count,
        "test_pass_rate": test_pass_rate,
        "test_executions": {"pass": passed, "fail": failed, "skipped": test_counts.get("skipped", 0)},
        "estimated_hours_saved": hours_saved,
        "estimated_cost_saved": cost_saved,
        "currency": currency,
        "assumptions": {
            "minutes_per_task_manual": minutes_per_task,
            "dev_hourly_rate": hourly_rate,
        },
        "window": {
            "since": since.isoformat() if since else None,
            "runs_in_window": len(runs),
        },
    }


def weekly(state: StateMachine, config: Dict[str, Any]) -> Dict[str, Any]:
    since = datetime.now(timezone.utc) - timedelta(days=7)
    return compute_roi(state, config, since=since)


def monthly(state: StateMachine, config: Dict[str, Any]) -> Dict[str, Any]:
    since = datetime.now(timezone.utc) - timedelta(days=30)
    return compute_roi(state, config, since=since)


def format_summary_line(roi: Dict[str, Any]) -> str:
    return (
        f"ROI — done:{roi['tasks_completed']}/{roi['tasks_total']} "
        f"avg_cohesion:{roi['avg_cohesion_score']} "
        f"blocked_rate:{int(roi['blocked_rate']*100)}% "
        f"hours_saved:{roi['estimated_hours_saved']} "
        f"cost_saved:{roi['currency']} {roi['estimated_cost_saved']}"
    )
