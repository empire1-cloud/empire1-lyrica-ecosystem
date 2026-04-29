"""PR preview generator — produces a markdown PR body for a completed task.

No git or network calls. This is preview-only.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from omni_agent.state_machine import StateMachine


class PRPreviewError(Exception):
    pass


def _evidence(state: StateMachine, run_id: str) -> Dict[str, Any]:
    with state.conn() as c:
        personas = [dict(r) for r in c.execute(
            "SELECT persona, mode_used, output_json FROM persona_outputs WHERE run_id=? ORDER BY id ASC",
            (run_id,),
        ).fetchall()]
        arts = [dict(r) for r in c.execute(
            "SELECT kind, path, metadata_json FROM artifacts WHERE run_id=? ORDER BY id ASC",
            (run_id,),
        ).fetchall()]
        tests = [dict(r) for r in c.execute(
            "SELECT command, exit_code, status, output_excerpt FROM test_executions WHERE run_id=? ORDER BY id ASC",
            (run_id,),
        ).fetchall()]
    for p in personas:
        try:
            p["output"] = json.loads(p["output_json"])
        except Exception:
            p["output"] = None
        p.pop("output_json", None)
    return {"personas": personas, "artifacts": arts, "tests": tests}


def _spec_from(personas: List[Dict[str, Any]]) -> Dict[str, Any]:
    for p in personas:
        if p["persona"] == "analyst" and isinstance(p.get("output"), dict):
            return p["output"]
    return {}


def _dev_summary(personas: List[Dict[str, Any]]) -> Dict[str, Any]:
    for p in personas:
        if p["persona"] == "developer" and isinstance(p.get("output"), dict):
            return p["output"]
    return {}


def _eval_summary(personas: List[Dict[str, Any]]) -> Dict[str, Any]:
    for p in personas:
        if p["persona"] == "evaluator" and isinstance(p.get("output"), dict):
            return p["output"]
    return {}


def generate(
    *,
    task_id: str,
    state: StateMachine,
    config: Dict[str, Any],
    out_dir: Optional[Path] = None,
    require_done: bool = True,
) -> Dict[str, Any]:
    """Return dict with keys: markdown (str), path (Path), meta (dict).

    Raises PRPreviewError if the task is not eligible (not found / not done).
    """
    task = state.get_task(task_id)
    if not task:
        raise PRPreviewError(f"task {task_id} not found")
    if require_done and task["status"] != "done":
        raise PRPreviewError(
            f"task {task_id} status is '{task['status']}' (not 'done'); PR preview refused."
        )

    run = state.latest_run_for_task(task_id)
    if not run:
        raise PRPreviewError(f"no runs recorded for task {task_id}")

    ev = _evidence(state, run["run_id"])
    spec = _spec_from(ev["personas"])
    dev = _dev_summary(ev["personas"])
    ev_eval = _eval_summary(ev["personas"])

    files_changed = sorted({a["path"] for a in ev["artifacts"] if a.get("path")})
    criteria = ev_eval.get("criteria_results") or []
    tests = ev["tests"]
    gc = ev_eval.get("guardrail_compliance") or {}
    filtered = gc.get("filtered_paths") or []
    cohesion = run.get("cohesion_score")
    mode = run.get("mode") or config.get("persona_mode", "hybrid")

    title = f"[omni-agent] {task['id']}: {task['normalized_text'][:80]}"

    lines: List[str] = [
        f"# {title}",
        "",
        "## Summary",
        f"- **Task**: `{task['id']}` — {task['normalized_text']}",
        f"- **Source**: `{task['source_file']}:{task['source_line']}`",
        f"- **Type / Priority**: `{task['task_type']}` / p{task['priority']}",
        f"- **Cohesion score**: **{cohesion}** (threshold 85)",
        f"- **Persona mode**: `{mode}`",
        f"- **Scope**: {spec.get('scope', '_(not recorded)_')}",
        "",
        "## Files changed",
    ]
    if files_changed:
        lines += [f"- `{p}`" for p in files_changed]
    else:
        lines.append("_None_")

    lines += ["", "## Test evidence"]
    if tests:
        for t in tests:
            lines.append(f"- `{t['command']}` → **{t['status']}** (exit={t['exit_code']})")
            if t.get("output_excerpt"):
                lines.append("  <details><summary>output</summary>\n\n  ```\n"
                             + str(t["output_excerpt"]).strip()[:1500]
                             + "\n  ```\n  </details>")
    else:
        lines.append("_No pytest executions recorded. Evaluator relied on static checks + lint._")

    lines += ["", "### Acceptance criteria"]
    if criteria:
        for c in criteria:
            mark = "✅" if c.get("met") else ("➖" if c.get("out_of_scope") else "❌")
            note = " _(out-of-scope by guardrails)_" if c.get("out_of_scope") else ""
            lines.append(f"- {mark} {c.get('text')}{note}")
    else:
        lines.append("_None recorded._")

    lines += ["", "## Risk notes"]
    risk_items: List[str] = []
    if gc.get("forbidden_write_attempts"):
        risk_items.append(f"{gc['forbidden_write_attempts']} forbidden-path write attempts auto-blocked by guardrails.")
    if filtered:
        risk_items.append(f"{len(filtered)} LLM-proposed path(s) filtered by guardrails: "
                          + ", ".join(f"`{p}`" for p in filtered))
    if (ev_eval.get("lint") or {}).get("status") == "fail":
        risk_items.append("Lint did not pass on applied files.")
    if not risk_items:
        risk_items.append("No risks detected during this run.")
    for r in risk_items:
        lines.append(f"- {r}")

    lines += ["", "## Rollback notes",
              "Revert this PR by deleting the following files (all created by omni-agent within allowed paths):"]
    if files_changed:
        lines += [f"- `{p}`" for p in files_changed]
    else:
        lines.append("_No files to revert (no changes applied)._")
    lines += ["",
              "If this task was applied via `append` action (docs), revert the specific block added by omni-agent.",
              "",
              "---",
              f"_Generated by omni-agent pr-preview at {datetime.now(timezone.utc).isoformat()}_"]

    markdown = "\n".join(lines) + "\n"

    out_dir = out_dir or Path(config["repo_root"]) / "omni_agent" / "reports" / "pr"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{task['id']}.md"
    path.write_text(markdown, encoding="utf-8")

    return {
        "markdown": markdown,
        "path": path,
        "meta": {
            "task_id": task["id"],
            "run_id": run["run_id"],
            "cohesion_score": cohesion,
            "files_changed": files_changed,
            "filtered_by_guardrails": filtered,
            "mode": mode,
            "title": title,
        },
    }
