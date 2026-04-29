"""Client-facing report generator. Emits both Markdown and JSON per run."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from omni_agent.reporting import roi as roi_mod
from omni_agent.state_machine import StateMachine


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "-", s).strip("-").lower() or "default"


def _fmt_list(items: List[str], bullet: str = "-") -> str:
    return "\n".join(f"{bullet} {x}" for x in items) if items else "_None_"


def _evidence_for_run(state: StateMachine, run_id: str, task_id: str) -> Dict[str, Any]:
    with state.conn() as c:
        personas = [dict(r) for r in c.execute(
            "SELECT persona, mode_used, output_json, ts FROM persona_outputs "
            "WHERE run_id=? ORDER BY id ASC", (run_id,)
        ).fetchall()]
        arts = [dict(r) for r in c.execute(
            "SELECT kind, path, metadata_json, ts FROM artifacts WHERE run_id=? ORDER BY id ASC",
            (run_id,),
        ).fetchall()]
        tests = [dict(r) for r in c.execute(
            "SELECT command, exit_code, status, output_excerpt, ts FROM test_executions "
            "WHERE run_id=? ORDER BY id ASC", (run_id,)
        ).fetchall()]
    for p in personas:
        try:
            p["output"] = json.loads(p["output_json"])
        except Exception:
            p["output"] = p.get("output_json")
        p.pop("output_json", None)
    for a in arts:
        try:
            a["metadata"] = json.loads(a["metadata_json"]) if a.get("metadata_json") else {}
        except Exception:
            a["metadata"] = {}
        a.pop("metadata_json", None)
    return {"personas": personas, "artifacts": arts, "tests": tests}


def _next_7_day_plan(state: StateMachine, limit: int = 10) -> List[Dict[str, Any]]:
    open_tasks = state.list_tasks(status=None)
    plan = []
    for t in open_tasks:
        if t["status"] in ("done",):
            continue
        plan.append({
            "task_id": t["id"],
            "status": t["status"],
            "task_type": t["task_type"],
            "priority": t["priority"],
            "source": f"{t['source_file']}:{t['source_line']}",
            "text": t["normalized_text"][:160],
        })
        if len(plan) >= limit:
            break
    return plan


def _risks(run_output: Dict[str, Any], evidence: Dict[str, Any]) -> List[str]:
    risks: List[str] = []
    gc = (run_output.get("evidence") or {}).get("guardrail_compliance") or {}
    if gc.get("forbidden_write_attempts"):
        risks.append(f"Developer attempted {gc['forbidden_write_attempts']} writes to forbidden paths (auto-blocked).")
    if gc.get("filtered_paths"):
        risks.append(f"{len(gc['filtered_paths'])} LLM-proposed paths filtered by guardrails.")
    if run_output.get("final_status") == "evaluating_failed":
        risks.append("Task below cohesion threshold — review acceptance criteria.")
    for t in evidence.get("tests", []):
        if t.get("status") == "fail":
            risks.append(f"Test suite failed: {t.get('command')}")
    return risks


def generate(
    *,
    run_output: Dict[str, Any],
    state: StateMachine,
    config: Dict[str, Any],
    workspace: Optional[str] = None,
    out_dir: Optional[Path] = None,
) -> Dict[str, Path]:
    """Generate MD + JSON client report. Returns dict with 'markdown' and 'json' paths."""
    workspace = workspace or ((config.get("workspace") or {}).get("name") or "default")
    out_dir = out_dir or Path(config["repo_root"]) / "omni_agent" / "reports" / "client"
    out_dir.mkdir(parents=True, exist_ok=True)

    date = _today()
    ws = _slug(workspace)
    tid = run_output.get("task_id", "NA")
    base = out_dir / f"{date}_{ws}_{tid}"

    task = state.get_task(tid) if tid != "NA" else None
    latest_run = state.latest_run_for_task(tid) if tid != "NA" else None
    run_id = run_output.get("run_id") or (latest_run or {}).get("run_id")
    evidence = _evidence_for_run(state, run_id, tid) if run_id else {"personas": [], "artifacts": [], "tests": []}

    weekly_roi = roi_mod.weekly(state, config)

    files_changed = run_output.get("files_changed", []) or []
    final_status = run_output.get("final_status")
    cohesion = run_output.get("cohesion_score")
    spec = run_output.get("mini_spec") or {}
    blockers = run_output.get("risks_blockers", []) or []
    filtered = run_output.get("filtered_by_guardrails", []) or []

    # minutes saved for *this* run
    mpt = weekly_roi["assumptions"]["minutes_per_task_manual"]
    rate = weekly_roi["assumptions"]["dev_hourly_rate"]
    this_hours = round((mpt / 60.0), 2) if final_status == "done" else 0.0
    this_cost = round(this_hours * rate, 2)

    exec_summary_bits = [
        f"- **Task**: `{tid}` — {((task or {}).get('normalized_text') or '')[:180]}",
        f"- **Final status**: `{final_status}`",
        f"- **Cohesion score**: {cohesion if cohesion is not None else '—'}",
        f"- **Files changed**: {len(files_changed)}",
        f"- **Workspace**: `{workspace}`",
        f"- **Run ID**: `{run_id}`",
    ]
    if run_output.get("blocked_stage"):
        exec_summary_bits.append(
            f"- **Blocked stage / reason**: `{run_output['blocked_stage']}` / `{run_output['blocked_reason']}`"
        )

    md_lines: List[str] = [
        f"# Omni-Agent Client Report — {date}",
        f"_Workspace: **{workspace}** · Task: `{tid}` · Run: `{run_id}`_",
        "",
        "## Executive Summary",
        *exec_summary_bits,
        "",
        "## Tasks Completed (this run)",
    ]
    if final_status == "done":
        md_lines.append(
            f"- `{tid}` — {((task or {}).get('normalized_text') or '')} "
            f"(cohesion **{cohesion}**)"
        )
    else:
        md_lines.append(f"_No tasks completed in this run. Final status: `{final_status}`._")

    md_lines += [
        "",
        "## Evidence",
        "### Files changed",
        _fmt_list([f"`{p}`" for p in files_changed]) if files_changed else "_None_",
        "",
        "### Acceptance criteria",
    ]
    criteria = (run_output.get("evidence") or {}).get("criteria_results") or []
    if criteria:
        for c in criteria:
            mark = "✓" if c.get("met") else ("~" if c.get("out_of_scope") else "✗")
            note = " _(out-of-scope)_" if c.get("out_of_scope") else ""
            md_lines.append(f"- [{mark}] {c.get('text')}{note} — {c.get('evidence','')}")
    else:
        md_lines.append("_None recorded._")

    md_lines += ["", "### Tests & lint"]
    if evidence["tests"]:
        for t in evidence["tests"]:
            md_lines.append(f"- `{t['command']}` → **{t['status']}** (exit={t['exit_code']})")
    else:
        md_lines.append("_No test executions recorded for this run._")
    if (run_output.get("lint") or {}).get("status"):
        md_lines.append(f"- lint: **{run_output['lint']['status']}**")

    md_lines += ["", "### Artifacts"]
    if evidence["artifacts"]:
        for a in evidence["artifacts"]:
            md_lines.append(f"- {a['kind']}: `{a.get('path') or '—'}`")
    else:
        md_lines.append("_None._")

    md_lines += ["", "## Blockers"]
    md_lines.append(_fmt_list(blockers))
    if filtered:
        md_lines += ["", "### Paths filtered by guardrails", _fmt_list([f"`{p}`" for p in filtered])]

    md_lines += ["", "## Risks"]
    risks = _risks(run_output, evidence)
    md_lines.append(_fmt_list(risks))

    md_lines += ["", "## Next 7-day plan"]
    plan = _next_7_day_plan(state)
    if plan:
        for p in plan:
            md_lines.append(
                f"- `{p['task_id']}` [{p['status']}] ({p['task_type']} · p{p['priority']}) "
                f"— {p['text']} _({p['source']})_"
            )
    else:
        md_lines.append("_No open tasks._")

    md_lines += [
        "",
        "## Time saved estimate (this run)",
        f"- Hours saved: **{this_hours}**",
        f"- Cost saved: **{weekly_roi['currency']} {this_cost}**",
        f"- Assumptions: {mpt:.0f} min/task @ {weekly_roi['currency']} {rate}/hr",
        "",
        "## Weekly ROI",
        f"- Tasks completed (7d): **{weekly_roi['tasks_completed']}**",
        f"- Average cohesion: **{weekly_roi['avg_cohesion_score']}**",
        f"- Blocked rate: **{int(weekly_roi['blocked_rate']*100)}%**",
        f"- Test pass rate: **{weekly_roi['test_pass_rate']}**",
        f"- Hours saved (7d): **{weekly_roi['estimated_hours_saved']}**",
        f"- Cost saved (7d): **{weekly_roi['currency']} {weekly_roi['estimated_cost_saved']}**",
        "",
    ]

    md_path = base.with_suffix(".md")
    json_path = base.with_suffix(".json")
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    pdf_ready = {
        "version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": workspace,
        "task_id": tid,
        "run_id": run_id,
        "sections": {
            "executive_summary": {
                "task_id": tid,
                "task_text": (task or {}).get("normalized_text"),
                "final_status": final_status,
                "cohesion_score": cohesion,
                "files_changed_count": len(files_changed),
                "blocked_stage": run_output.get("blocked_stage"),
                "blocked_reason": run_output.get("blocked_reason"),
            },
            "tasks_completed": (
                [{"task_id": tid, "cohesion": cohesion}] if final_status == "done" else []
            ),
            "evidence": {
                "files_changed": files_changed,
                "criteria": criteria,
                "tests": evidence["tests"],
                "artifacts": evidence["artifacts"],
                "lint": run_output.get("lint"),
                "personas": evidence["personas"],
            },
            "blockers": blockers,
            "filtered_by_guardrails": filtered,
            "risks": risks,
            "next_7_day_plan": plan,
            "time_saved_estimate": {
                "this_run_hours": this_hours,
                "this_run_cost": this_cost,
                "currency": weekly_roi["currency"],
                "assumptions": weekly_roi["assumptions"],
            },
            "weekly_roi": weekly_roi,
        },
        "mini_spec": spec,
    }
    json_path.write_text(json.dumps(pdf_ready, indent=2, default=str), encoding="utf-8")

    return {"markdown": md_path, "json": json_path}
