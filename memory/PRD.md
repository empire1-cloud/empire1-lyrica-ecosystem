# Omni-Agent — Internal Product Requirements

## Original problem statement
Build an internal Omni-Agent that autonomously completes unfinished tasks discovered in markdown notes via persona-based execution (Analyst → Developer → Evaluator), in strict black-box mode. CLI-only, hybrid LLM (Claude Sonnet 4.5 via Emergent Universal Key) with rule-based fallback, SQLite persistence, JSON export.

## User personas
- Repo maintainer who drops `- [ ]` / `TODO:` / `FIXME:` lines into `memory/tasks/**/*.md` and expects safe, auditable completion.
- Reviewer who reads `omni_agent/reports/latest.md` and `state_snapshot.json` to audit what changed.

## Core requirements (static)
- Scanner parses markdown for `- [ ]`, `TODO:`, `FIXME:` patterns.
- Triage classifies type/priority/missing context.
- Personas: Analyst → Developer → Evaluator with hybrid LLM/rule mode.
- State machine: not_started, analyzing, building, evaluating, done, blocked_context, blocked_dependency, evaluating_failed.
- Black-box guardrails enforce allowed/forbidden paths.
- Cohesion score (40/30/20/10) with done threshold = 85.
- Notes write-back (`[ ]` → `[x]` + timestamp; `BLOCKED_CONTEXT` markers).
- CLI: `scan | run-next | run-task | status | report` (+ `--dry-run`, `--json`).

## What's been implemented (2026-04-29)
- Full module tree: `omni_agent/` (scanner, triage, guardrails, llm_client, state_machine, orchestrator, personas/{analyst,developer,evaluator}, tests/) + `scripts/omni_agent.py` CLI.
- SQLite schema with 7 tables (tasks, task_runs, state_transitions, persona_outputs, artifacts, test_executions, run_config_snapshots).
- Hybrid LLM with Claude Sonnet 4.5 (Emergent Universal Key) and automatic fallback to rule-based personas.
- 22 unit tests for scanner / triage / state machine — all passing.
- First-run loop verified: scan → run-next --dry-run → real run-task → report. 3 of 4 demo tasks completed (`done` with score 88–91); 1 correctly landed at `evaluating_failed` because LLM proposed forbidden paths and acceptance criteria couldn't be met.

## Backlog
### P0
- None (system functional).

### P1
- Block-up-front mode: when triage detects missing_context, also block in hybrid mode (configurable).
- Better acceptance-criterion checking for criteria that mention non-applied paths (currently scores low if LLM creatively names files outside allowlist).

### P2
- Read-only minimal dashboard (status, queue, scores, blockers).
- Run-N concurrent tasks.
- Optional Git commit per run.
