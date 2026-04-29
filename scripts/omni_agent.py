#!/usr/bin/env python3
"""Omni-Agent CLI entrypoint."""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Make /app importable regardless of cwd
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from omni_agent.orchestrator import Orchestrator, load_config  # noqa: E402


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _print_json(payload) -> None:
    print(json.dumps(payload, indent=2, default=str))


def _build_orchestrator(args) -> Orchestrator:
    repo_root = Path(args.repo_root).resolve()
    config = load_config(repo_root, Path(args.config) if args.config else None)
    return Orchestrator(repo_root, config)


def cmd_scan(args) -> int:
    orc = _build_orchestrator(args)
    summary = orc.scan()
    print(f"Scanned tasks. parsed={summary['parsed']} new={summary['new']} existing={summary['existing']}")
    if args.json:
        _print_json(summary)
    return 0


def cmd_run_next(args) -> int:
    orc = _build_orchestrator(args)
    out = orc.run_next(dry_run=args.dry_run)
    if not out:
        print("No runnable tasks.")
        return 0
    _print_human_output(out)
    if args.json:
        _print_json(out)
    return 0 if out.get("final_status") in ("done", "dry_run") else 2


def cmd_run_task(args) -> int:
    orc = _build_orchestrator(args)
    out = orc.run_task(args.task_id, dry_run=args.dry_run)
    _print_human_output(out)
    if args.json:
        _print_json(out)
    return 0 if out.get("final_status") in ("done", "dry_run") else 2


def cmd_status(args) -> int:
    orc = _build_orchestrator(args)
    st = orc.status()
    print(f"Total tasks: {st['total']}")
    for s, n in sorted(st["by_status"].items()):
        print(f"  {s}: {n}")
    if args.verbose or args.json:
        for t in st["tasks"]:
            print(f"  - {t['id']} [{t['status']}] {t['task_type']} p{t['priority']} :: {t['normalized_text']}")
    if args.json:
        _print_json(st)
    return 0


def cmd_report(args) -> int:
    orc = _build_orchestrator(args)
    path = orc.report()
    print(f"Report written: {path}")
    return 0


def _print_human_output(out: dict) -> None:
    print("=" * 72)
    print(f"Task ID:               {out.get('task_id')}")
    print(f"Run ID:                {out.get('run_id')}")
    print(f"Final status:          {out.get('final_status')}")
    print(f"Dry run:               {out.get('dry_run')}")
    if out.get("blocked_stage"):
        print(f"Blocked stage:         {out.get('blocked_stage')}")
        print(f"Blocked reason:        {out.get('blocked_reason')}")
    print(f"Cohesion score:        {out.get('cohesion_score')}")
    print(f"Files changed:         {out.get('files_changed')}")
    if out.get("filtered_by_guardrails"):
        print(f"Filtered by guardrails: {out.get('filtered_by_guardrails')}")
    print(f"Risks/blockers:        {out.get('risks_blockers')}")
    print(f"Next task recommended: {out.get('next_task_recommendation')}")
    spec = out.get("mini_spec") or {}
    if spec:
        print("Mini-spec:")
        print(f"  scope: {spec.get('scope')}")
        print(f"  acceptance_criteria: {spec.get('acceptance_criteria')}")
        print(f"  impacted_files: {spec.get('impacted_files')}")
    tests = out.get("tests") or {}
    if tests:
        print(f"Tests: status={tests.get('status')} ran={tests.get('ran')} cmd={tests.get('command')}")
    lint = out.get("lint") or {}
    if lint:
        print(f"Lint:  status={lint.get('status')}")
    gc = (out.get("evidence") or {}).get("guardrail_compliance") or {}
    if gc:
        print(f"Guardrail: score={gc.get('score')} proposed={gc.get('proposed_total')} "
              f"applied={gc.get('applied_total')} filtered={len(gc.get('filtered_paths') or [])}")
    print("=" * 72)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="omni_agent", description="Omni-Agent CLI")
    p.add_argument("--repo-root", default=str(ROOT))
    p.add_argument("--config", default=None)
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("--json", action="store_true", help="emit machine-readable JSON")

    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("scan", help="scan markdown for tasks")

    rn = sub.add_parser("run-next", help="run the next highest-priority task")
    rn.add_argument("--dry-run", action="store_true")

    rt = sub.add_parser("run-task", help="run a specific task by id")
    rt.add_argument("task_id")
    rt.add_argument("--dry-run", action="store_true")

    sub.add_parser("status", help="show task counts and list")
    sub.add_parser("report", help="write reports/latest.md")

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _setup_logging(args.verbose)
    handlers = {
        "scan": cmd_scan,
        "run-next": cmd_run_next,
        "run-task": cmd_run_task,
        "status": cmd_status,
        "report": cmd_report,
    }
    return handlers[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
