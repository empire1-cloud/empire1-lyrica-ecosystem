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

## What's been implemented
- 2026-04-29 MVP: full Omni-Agent package, SQLite persistence, hybrid LLM, 22 unit tests, first-run loop verified, 3/4 demo tasks done.
- 2026-04-29 P1.1 + P1.2:
  - Block-up-front policy locked: `rule` always blocks; `hybrid` hard-blocks pre-Analyst when missing_context + confidence<0.5; `llm` never auto-blocks.
  - New audit fields `blocked_stage` (`pre_analyst` | `analyst` | `developer`) and `blocked_reason` (code) on every blocked output.
  - Evaluator now computes a **guardrail_compliance** subscore; criteria referencing guardrail-filtered paths are marked `out_of_scope` and excluded from acceptance.
  - Cohesion weights rebalanced: 35 / 25 / 20 / 10 / **10** (guardrail).
  - +15 new unit tests (total 37 passing).
  - Verified live: TASK-594f6b3c now correctly lands at `blocked_context` with `blocked_stage=pre_analyst` / `blocked_reason=missing_context_low_confidence` instead of `evaluating_failed`.

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
