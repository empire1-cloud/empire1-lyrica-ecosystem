# Omni-Agent

An internal, persona-based, black-box system that autonomously completes unfinished tasks discovered in markdown notes (`memory/tasks/**/*.md`).

> **Mode**: hybrid by default — LLM (Claude Sonnet 4.5 via Emergent Universal Key) with automatic fallback to deterministic rule-based personas when the LLM is unavailable, rate-limited, or times out.

---

## Architecture

```
omni_agent/
├── scanner.py          # markdown -> ParsedTask objects
├── triage.py           # classify type / priority / missing context
├── guardrails.py       # allowed/forbidden path enforcement
├── llm_client.py       # Emergent Universal Key wrapper + fallback signaling
├── state_machine.py    # SQLite persistence + transitions audit trail
├── orchestrator.py     # run_task / run_next pipeline (Analyst -> Developer -> Evaluator)
├── personas/
│   ├── analyst.py      # mini-spec
│   ├── developer.py    # minimal patch under allowed paths
│   └── evaluator.py    # acceptance + tests + lint + cohesion score
├── state/
│   ├── omni.db         # SQLite (canonical store)
│   └── tasks.json      # JSON export for human-readable consumption
├── reports/
│   ├── latest.md
│   └── state_snapshot.json
└── tests/              # unit tests for scanner, triage, state machine
```

CLI entry point: `scripts/omni_agent.py`.

---

## CLI

```bash
python scripts/omni_agent.py scan
python scripts/omni_agent.py run-next
python scripts/omni_agent.py run-next --dry-run
python scripts/omni_agent.py run-task TASK-001
python scripts/omni_agent.py status
python scripts/omni_agent.py report
```

Add `--json` to any command for machine-readable output.

---

## Task lifecycle (state machine)

```
not_started
   └─ analyzing ─ building ─ evaluating ─ done
                                  └─ evaluating_failed ─┐
                                                        └─> analyzing/building (next run)
   └─ blocked_context        (missing input — task text rewritten with BLOCKED_CONTEXT marker)
   └─ blocked_dependency     (waiting on upstream task / external)
```

Every transition is recorded in `state_transitions` with actor, reason, and timestamp.

## Cohesion score (0–100)

| Component | Weight |
|---|---|
| Acceptance criteria met | 40% |
| Tests pass | 30% |
| Regression checks (compile + path safety) | 20% |
| Code quality (lint) | 10% |

Default `done` threshold: **85**.

## Black-box guardrails (strict)

Allowed write roots (relative to repo root):
- `frontend/src/**`
- `backend/app/routers/**`, `backend/app/services/**`, `backend/app/core/**`, `backend/tests/**`
- `memory/tasks/**`
- `omni_agent/**`

Forbidden roots (never read or written):
- `foundry/empire1/laws/**`, `foundry/empire1/blueprints/**`, `foundry/empire1/documentation/**`
- `**/.env`, `**/.env.*`, `**/secrets/**`, `**/keys/**`
- `investor/**`, `strategy/**`

Any developer-emitted change targeting forbidden or out-of-allowlist paths is dropped before disk write.

## Notes write-back

- On `done`: rewrites the task line `- [ ]` → `- [x]` and appends `(done <ISO timestamp> <TASK-ID>)`.
- On `blocked_context`: appends `<!-- BLOCKED_CONTEXT: <reason> (task TASK-ID) -->` to the task line so the next scan sees it without losing the original.

## Output contract

Each `run-task` / `run-next` returns:

```json
{
  "task_id": "TASK-001",
  "run_id": "...",
  "final_status": "done | evaluating_failed | blocked_context | blocked_dependency | dry_run",
  "mini_spec": { "scope": "...", "acceptance_criteria": [...], "impacted_files": [...] },
  "files_changed": ["backend/app/services/..."],
  "tests": { "status": "pass|fail|skipped", "command": "..." },
  "evidence": { "criteria_results": [...], "regression_ok": true },
  "cohesion_score": 92.5,
  "risks_blockers": [],
  "next_task_recommendation": "TASK-002"
}
```


## Module Overview

### Purpose

The `omni_agent` module implements a sophisticated multi-persona AI system designed to handle complex tasks through collaborative intelligence. By leveraging specialized AI personas, each with distinct capabilities and perspectives, the module orchestrates comprehensive workflows that mirror human team collaboration patterns.

### Architecture

The omni-agent architecture is built on a persona-based collaboration model where different AI agents work together in a coordinated fashion:

```
┌─────────────────────────────────────────────────────────┐
│                    Omni-Agent System                     │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │ Analyst  │→│ Planner  │→│ Executor │→│ Reviewer ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
│       ↓             ↓             ↓             ↓        │
│  ┌────────────────────────────────────────────────────┐ │
│  │         Shared Context & Memory Layer              │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. **Analyst Persona**
- **Responsibility**: Triages incoming tasks, identifies requirements, and performs initial analysis
- **Capabilities**: 
  - Task classification and prioritization
  - Dependency detection
  - Context extraction and gap identification
  - Requirement clarification
- **Output**: Structured triage reports with task metadata and execution recommendations

#### 2. **Planner Persona**
- **Responsibility**: Transforms triage results into detailed, actionable specifications
- **Capabilities**:
  - Technical specification generation
  - Scope definition and boundary establishment
  - Acceptance criteria formulation
  - Risk and constraint identification
- **Output**: Comprehensive mini-specs that guide implementation

#### 3. **Executor Persona** (Developer)
- **Responsibility**: Implements changes based on specifications
- **Capabilities**:
  - Code generation and modification
  - File system operations (create, append, replace)
  - Multi-file coordination
  - Adherence to architectural patterns and constraints
- **Output**: JSON patch objects describing file changes with strict path validation

#### 4. **Reviewer Persona** (Evaluator)
- **Responsibility**: Validates implementation against specifications and quality standards
- **Capabilities**:
  - Acceptance criteria verification
  - Code quality assessment
  - Security and best practice validation
  - Integration and consistency checking
- **Output**: Structured evaluation reports with pass/fail determinations and improvement recommendations

### Persona Interaction Flow

1. **Task Intake**: A task is submitted to the system
2. **Analysis Phase**: Analyst persona examines the task, extracts context, and produces triage data
3. **Planning Phase**: Planner persona receives triage output and generates detailed specifications
4. **Execution Phase**: Executor persona implements changes according to the spec
5. **Review Phase**: Reviewer persona validates the implementation against acceptance criteria
6. **Iteration**: If review fails, the task may cycle back to planning or execution for refinement

### Design Principles

- **Separation of Concerns**: Each persona has a distinct, well-defined role
- **Context Preservation**: Shared memory and context ensure continuity across persona transitions
- **Path Safety**: Strict allowed/forbidden path enforcement prevents unauthorized modifications
- **Declarative Outputs**: Personas produce structured, machine-readable outputs for seamless handoffs
- **Quality Gates**: Multi-stage validation ensures high-quality deliverables
- **Transparency**: All persona decisions and rationales are documented for auditability

### Use Cases

- **Feature Development**: Complete feature implementation from requirements to tested code
- **Documentation**: Comprehensive documentation generation and maintenance
- **Refactoring**: Safe, systematic code improvements with validation
- **Bug Fixes**: Root cause analysis, targeted fixes, and verification
- **Testing**: Test generation, execution, and coverage analysis

### Integration Points

The omni_agent module integrates with:
- **Memory Layer**: Persistent task storage and retrieval (`memory/tasks/`)
- **Backend Services**: API endpoints for task submission and status tracking
- **Frontend**: User interfaces for task management and monitoring
- **Core Infrastructure**: Configuration, authentication, and orchestration services
