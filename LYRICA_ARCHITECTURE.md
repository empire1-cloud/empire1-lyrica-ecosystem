# Lyrica Architecture Map

## Prime Directive
WE EVOLVE. NEVER DELETE.

This document maps the current `empire1-lyrica-ecosystem` repository into durable Lyrica subsystems without flattening the ecosystem into a generic AI music app. When a boundary is unclear, the area stays visible and is marked for review instead of being removed or renamed.

## Source Repo
`empire1-cloud/empire1-lyrica-ecosystem`

## App Repo Cross-Reference
`empire1-cloud/Lyrica3-pro`

## Product Hierarchy
- `Lyrica` is the parent music platform and ecosystem umbrella.
- `Sonance Pro` is the creator studio surface for artists, producers, operators, and internal tooling.
- `SL Universal` is the public listening, discovery, and remix distribution surface.
- `Soulfire Engine` is the AI creative brain that would drive composition, generation, transformation, and workflow intelligence.
- `Soulfire Training Pipeline` is the training, data, persona, provenance, and culture corpus pipeline that feeds Soulfire safely.
- `Native Audio Runtime` is the low-level audio execution layer for MMA, PFA, Demucs, stems, DSP, and render-time processing.
- `Archisynapse` is the trust and transaction layer for DNA, VICS, royalties, fraud, payments, and ledger logic.
- `Cultura` is the cultural intelligence and authenticity layer that protects genre, lineage, persona, and community fit.
- `SLA113` is the parent runtime and orchestration layer that coordinates the platform and its agents.

## Current Repo Position
Based on `README.md`, `memory/PRD.md`, `omni_agent/reports/latest.md`, and the folder tree, this repository is currently an `Omni-Agent` centered execution slice. It appears to be closest to an early `SLA113` orchestration layer with partial `Sonance Pro` support surfaces and limited backend/frontend scaffolding.

The code and docs present here do not yet show full implementations of `SL Universal`, `Soulfire Engine`, `Soulfire Training Pipeline`, `Native Audio Runtime`, `Archisynapse`, or `Cultura`. Those must remain first-class architecture targets, but in this repo they are mostly represented as future subsystem boundaries rather than active modules.

## Subsystem Definitions

### Lyrica Platform
The parent platform that unifies creator tooling, public listening/remix experiences, AI generation, audio execution, rights infrastructure, and culture-aware intelligence. In this repo, the platform is represented more by intent and repo naming than by a complete integrated runtime.

### Sonance Pro
The creator studio surface. In this repo, the strongest candidates are the `frontend/` and `backend/` scaffolds plus any operator-facing workflows that would later become the studio control plane. Current evidence suggests a general app shell rather than a finished creator studio.

### SL Universal
The public listening and remix platform. No direct public-consumer delivery flow is clearly implemented in this repo yet. Treat as a protected target boundary that should later be compared against `Lyrica3-pro` before making assumptions.

### Soulfire Engine
The AI creative brain for music ideation, transformation, and assisted creation. In this repo, the closest conceptual precursor is the persona-based `omni_agent/` orchestration system, but that system is currently a task-completion engine, not a music-generation engine. The relationship is architectural, not literal.

### Soulfire Training Pipeline
The data, training, persona, and provenance pipeline behind Soulfire. No explicit training corpus, dataset management, or model pipeline is visible in this repo. Mark as absent-in-code but required in platform architecture.

### Native Audio Runtime
The execution layer for stems, DSP, separation, transformation, and low-level audio processing. No dedicated audio runtime, render queue, or DSP module is clearly present in the inspected tree. This boundary must remain protected for future implementation.

### Archisynapse
The rights, payments, fraud, and ledger substrate. The current repo contains a placeholder payment-oriented service name under `backend/app/services/`, but no mature royalties, ledger, or anti-fraud subsystem is visible. This is a future architecture zone with an early placeholder signal.

### Cultura
The cultural intelligence and authenticity layer. No explicit module is present, but this subsystem remains necessary to prevent generic and culturally flattened AI music behavior across the broader Lyrica ecosystem.

### SLA113
The parent runtime and orchestration layer. The clearest active fit in this repo is `omni_agent/`, which already includes scanner, triage, guardrails, orchestration, state machine, reporting, and persona flow. That makes `omni_agent/` the strongest currently implemented candidate for a proto-`SLA113` layer.

### Legacy / Needs Review
Anything that is scaffold-only, placeholder-named, generic framework output, or conceptually misaligned with the long-term subsystem map belongs here until cross-checked. This includes template frontend assets, ambiguous backend placeholders, sales collateral that is product-adjacent but not runtime architecture, and any module whose future subsystem ownership is unclear.

## Folder / File Map

| Path | Subsystem | Purpose | Status | Notes |
|---|---|---|---|---|
| `/README.md` | Lyrica Platform | Minimal top-level repo entrypoint. | Docs Only | Does not yet define the larger Lyrica platform architecture. |
| `/.emergent/` | SLA113 | Environment/bootstrap metadata for the local stack. | Protected | Infra-adjacent metadata; do not casually alter without environment context. |
| `/.emergent/emergent.yml` | SLA113 | Environment configuration anchor. | Protected | Likely affects runtime assumptions outside feature code. |
| `/backend/` | Sonance Pro | Backend application scaffold for operator or creator-facing flows. | Needs Review | Looks generic and early-stage rather than domain-complete. |
| `/backend/server.py` | Sonance Pro | FastAPI entrypoint with status endpoints and Mongo wiring. | Active | Useful app shell, but not yet clearly mapped to a music-specific service boundary. |
| `/backend/requirements.txt` | Sonance Pro | Python backend dependency list. | Active | Dependency manifest for the backend slice. |
| `/backend/app/core/` | Sonance Pro | Shared backend helpers/core utilities. | Needs Review | Small footprint; subsystem boundaries are not yet explicit. |
| `/backend/app/core/email_validator_helper.py` | Sonance Pro | Email validation helper. | Active | General app support, not music-domain specific. |
| `/backend/app/services/` | Archisynapse | Service-layer placeholder area. | Adapter Needed | Some services may later split between studio logic and trust/commerce logic. |
| `/backend/app/services/health_service.py` | SLA113 | Runtime/service health support. | Active | Better aligned with orchestration/runtime observability than content logic. |
| `/backend/app/services/integrate_with_payment_provider_tbd_for__service.py` | Archisynapse | Placeholder for payment integration. | Needs Review | Strong hint toward Archisynapse, but naming and maturity are incomplete. |
| `/frontend/` | Sonance Pro | Web application shell and component surface. | Needs Review | Appears scaffolded; likely a future studio/admin surface. |
| `/frontend/README.md` | Sonance Pro | CRA template documentation. | Legacy | Generic template doc, not ecosystem-specific architecture. |
| `/frontend/package.json` | Sonance Pro | Frontend dependency and script manifest. | Active | Standard app shell metadata. |
| `/frontend/public/` | Sonance Pro | Static web assets. | Active | Generic app asset area. |
| `/frontend/public/index.html` | Sonance Pro | Frontend HTML entrypoint. | Active | Standard shell entrypoint. |
| `/frontend/src/` | Sonance Pro | Main React source tree. | Active | Current likely studio/control UI surface. |
| `/frontend/src/App.js` | Sonance Pro | Root React app component. | Active | Root entrypoint for the current web shell. |
| `/frontend/src/App.css` | Sonance Pro | Root app styling. | Active | Presentation layer only. |
| `/frontend/src/index.js` | Sonance Pro | React bootstrap entrypoint. | Active | Standard root loader. |
| `/frontend/src/index.css` | Sonance Pro | Global frontend styling. | Active | Generic styling layer. |
| `/frontend/src/components/ui/` | Sonance Pro | Shared UI component library. | Needs Review | Large generic UI kit; not yet evidence of subsystem-specific workflows. |
| `/frontend/src/hooks/use-toast.js` | Sonance Pro | Shared frontend interaction helper. | Active | UI support utility. |
| `/frontend/src/lib/utils.js` | Sonance Pro | Frontend utility helpers. | Active | Generic app utility layer. |
| `/frontend/plugins/` | SLA113 | Frontend plugin integration area. | Adapter Needed | Plugin wiring may later bridge runtime health and studio surfaces. |
| `/frontend/plugins/health-check/` | SLA113 | Frontend-side health tooling plugin area. | Active | Supports system observability more than product-domain features. |
| `/frontend/plugins/health-check/health-endpoints.js` | SLA113 | Health endpoint definitions or checks. | Active | Runtime observability bridge. |
| `/frontend/plugins/health-check/webpack-health-plugin.js` | SLA113 | Build/runtime health plugin. | Active | Tooling/runtime support. |
| `/memory/` | SLA113 | Persistent human-authored task and planning memory. | Protected | Central operating memory for the current repo workflow. |
| `/memory/PRD.md` | SLA113 | Product requirements source for Omni-Agent behavior. | Protected | Primary architecture evidence for the current active system. |
| `/memory/tasks/` | SLA113 | Task intake area scanned by Omni-Agent. | Protected | Current operational inbox; tied to automated write-back. |
| `/memory/tasks/inbox.md` | SLA113 | Markdown task queue and blocker annotations. | Protected | Directly used by the orchestrator. |
| `/omni_agent/` | SLA113 | Persona-based orchestration runtime. | Active | Strongest implemented subsystem in the repo. |
| `/omni_agent/README.md` | SLA113 | Module architecture and contract documentation. | Protected | Core reference for current runtime behavior. |
| `/omni_agent/scanner.py` | SLA113 | Markdown task discovery and parsing. | Active | Ingestion edge of the runtime. |
| `/omni_agent/triage.py` | SLA113 | Task classification and missing-context analysis. | Active | Analyst-phase decision support. |
| `/omni_agent/guardrails.py` | SLA113 | Path safety and access constraints. | Protected | Safety-critical enforcement layer. |
| `/omni_agent/llm_client.py` | Soulfire Engine | Hybrid LLM client wrapper and fallback signaling. | Adapter Needed | AI orchestration exists, but it is not yet music-creation specific. |
| `/omni_agent/state_machine.py` | SLA113 | Persistence and lifecycle transitions. | Active | Canonical task-state logic. |
| `/omni_agent/orchestrator.py` | SLA113 | End-to-end task execution pipeline. | Active | Closest current implementation to parent orchestration. |
| `/omni_agent/personas/` | Soulfire Engine | Persona layer for analyst/developer/evaluator roles. | Adapter Needed | Strong precursor pattern for Soulfire-style intelligence, but domain mismatch remains. |
| `/omni_agent/personas/analyst.py` | Soulfire Engine | Analysis persona implementation. | Active | Intelligence layer, but currently software-task focused. |
| `/omni_agent/personas/developer.py` | Soulfire Engine | Execution persona implementation. | Active | Action persona within the orchestration runtime. |
| `/omni_agent/personas/evaluator.py` | Soulfire Engine | Validation persona implementation. | Active | Review and scoring layer. |
| `/omni_agent/reporting/` | SLA113 | Structured output generation and reporting. | Active | Runtime reporting and externalization layer. |
| `/omni_agent/reporting/client_report.py` | SLA113 | Client-facing report generation. | Active | Output layer for operator review. |
| `/omni_agent/reporting/pr_preview.py` | SLA113 | PR preview/report support. | Active | Change review adapter. |
| `/omni_agent/reporting/roi.py` | SLA113 | ROI reporting calculations. | Active | Business-facing instrumentation. |
| `/omni_agent/reports/` | SLA113 | Persisted execution reports and snapshots. | Protected | Runtime evidence store; important for audit. |
| `/omni_agent/reports/latest.md` | SLA113 | Latest execution report. | Protected | One of the required source docs for this map. |
| `/omni_agent/reports/pr/` | SLA113 | PR-specific report output area. | Active | Review artifact storage. |
| `/omni_agent/reports/state_snapshot.json` | SLA113 | Machine-readable runtime state snapshot. | Protected | Audit and external integration candidate. |
| `/omni_agent/state/` | SLA113 | Runtime database and exported state. | Protected | Canonical local operational state. |
| `/omni_agent/state/omni.db` | SLA113 | SQLite canonical store. | Protected | High-risk stateful asset; do not casually modify. |
| `/omni_agent/state/tasks.json` | SLA113 | JSON state export. | Protected | Human-readable state mirror. |
| `/omni_agent/tests/` | SLA113 | Unit tests for the runtime module. | Active | Protects runtime behavior. |
| `/omni_agent/config.yaml` | SLA113 | Runtime configuration. | Protected | Configuration boundary for orchestration behavior. |
| `/omni_agent/sales/` | Lyrica Platform | Founder-led packaging, positioning, and sales collateral. | Docs Only | Commercial enablement, not runtime architecture. |
| `/omni_agent/sales/README.md` | Lyrica Platform | Sales kit overview and guardrails. | Docs Only | Useful for go-to-market, not subsystem code. |
| `/omni_agent/sales/pricing.md` | Lyrica Platform | Pricing collateral. | Docs Only | Commercial artifact. |
| `/omni_agent/sales/landing_page.md` | Lyrica Platform | Marketing site copy. | Docs Only | Messaging asset, not runtime logic. |
| `/omni_agent/sales/offer_sheet.md` | Lyrica Platform | Offer sheet content. | Docs Only | Sales artifact. |
| `/omni_agent/sales/outreach_kit.md` | Lyrica Platform | Outreach templates and call structure. | Docs Only | Commercial ops asset. |
| `/omni_agent/sales/demo_script.md` | Lyrica Platform | Demo walk-through content. | Docs Only | Product demo aid. |
| `/omni_agent/sales/pilot_program.md` | Lyrica Platform | Pilot plan documentation. | Docs Only | Commercial delivery guide. |
| `/omni_agent/sales/investor_contact_tracker.md` | Lyrica Platform | Investor/outreach tracking doc. | Docs Only | Business artifact outside core runtime. |
| `/omni_agent/sales/investor_dm_batch1.md` | Lyrica Platform | Investor DM content. | Docs Only | Business collateral. |
| `/omni_agent/sales/investor_dm_followups.md` | Lyrica Platform | Investor follow-up content. | Docs Only | Business collateral. |
| `/omni_agent/sales/investor_handoff_email_template.md` | Lyrica Platform | Investor handoff template. | Docs Only | Business collateral. |
| `/scripts/` | SLA113 | CLI entrypoint area. | Active | Operational interface to the runtime. |
| `/scripts/omni_agent.py` | SLA113 | CLI command entrypoint. | Active | Main operator command surface. |
| `/tests/` | Legacy / Needs Review | Sparse top-level test area. | Needs Review | Ownership is unclear relative to `omni_agent/tests/`. |
| `/test_reports/` | SLA113 | Test output artifact area. | Protected | Generated evidence storage. |
| `/test_reports/pytest/` | SLA113 | Pytest report output path. | Protected | Artifact destination. |
| `/test_result.md` | SLA113 | Test run summary artifact. | Docs Only | Evidence file, not a source module. |
| `/.gitignore` | Legacy / Needs Review | Repo ignore rules. | Protected | Standard repo hygiene; not subsystem logic. |
| `/.gitconfig` | Legacy / Needs Review | Local repo git configuration. | Protected | Repo-local config; leave unchanged unless intentional. |

## Protected Areas
- `memory/` because the current runtime depends on markdown task memory and write-back semantics.
- `omni_agent/guardrails.py`, `omni_agent/config.yaml`, and `omni_agent/state_machine.py` because they define safety, lifecycle, and orchestration behavior.
- `omni_agent/state/` and `omni_agent/reports/` because they are evidence and state stores.
- `.emergent/` because it appears to encode environment/bootstrap assumptions.
- Any placeholder commerce or payment path under `backend/app/services/` because that likely evolves into `Archisynapse` and should not be casually improvised.

## Legacy / Needs Review
- `frontend/README.md` is generic CRA documentation and does not describe the Lyrica architecture.
- `frontend/src/components/ui/` is a broad generic UI component inventory; ownership by `Sonance Pro` is provisional until real workflows are mapped.
- `tests/` at the repo root is sparse and its relationship to `omni_agent/tests/` is unclear.
- `backend/` is likely a useful shell, but current endpoints are generic status plumbing rather than a named Lyrica subsystem contract.
- `omni_agent/sales/` is valid business collateral but should not be mistaken for core product architecture.
- `omni_agent/llm_client.py` and persona modules are important, but their current semantics are software-task oriented rather than music-creation oriented.

## Adapter Needs
- `Lyrica <-> Sonance Pro`
  A stable contract is needed between platform identity/capabilities and the creator-studio UI/backend shell so studio workflows do not become the de facto definition of the whole platform.
- `Lyrica <-> SL Universal`
  A public-consumption and remix contract is needed so audience-facing features remain distinct from creator tooling and internal automation.
- `Lyrica <-> Soulfire`
  A capability boundary is needed between the platform shell and the AI creative brain: prompts, generations, revisions, provenance, and review loops should be explicit.
- `Soulfire <-> Native Audio Runtime`
  An execution adapter is needed between model intent and audio rendering/transformation primitives such as stems, DSP, MMA, PFA, and Demucs.
- `Lyrica <-> Archisynapse`
  Rights, fraud, royalty, payment, and ledger events need platform-level contracts instead of isolated service placeholders.
- `Lyrica <-> Cultura`
  Cultural policy, lineage checks, authenticity scoring, and persona constraints need explicit interfaces so the platform does not drift into generic outputs.
- `Lyrica <-> SLA113`
  The parent platform needs a clear orchestration boundary describing what the runtime controls, what it observes, and how subsystems register with it.

## App Repo Cross-Check Needed
Later compare this repo against `~/projects/Lyrica3-pro` for:
- The real public product boundaries for `Sonance Pro` versus `SL Universal`.
- Whether `Lyrica3-pro` already contains UI or route naming that should become the canonical platform vocabulary.
- Whether audio-generation or remix flows exist there that should be mapped to `Soulfire Engine` or `Native Audio Runtime`.
- Whether rights, royalties, subscriptions, or payment flows exist there that should define `Archisynapse` more concretely.
- Whether culture, persona, moderation, or authenticity logic exists there that should anchor `Cultura`.
- Whether orchestration/runtime responsibilities are duplicated between repos and need one shared `SLA113` boundary.

Do not treat this repo as the whole product until that cross-check is completed.

## Recommended Next Actions
1. Cross-check `~/projects/Lyrica3-pro` routes, feature names, and flows against this map without changing code, then tighten subsystem ownership.
2. Create a follow-up contract document for adapter boundaries between `SLA113`, `Sonance Pro`, `Soulfire`, and `Archisynapse`.
3. Audit `backend/` and `frontend/` to separate scaffold/template assets from true product surfaces.
4. Identify where music-domain capabilities will live versus where the current Omni-Agent orchestration should remain runtime infrastructure only.
5. Preserve all unclear folders as visible architecture inventory and mark ownership explicitly before any refactor, rename, or consolidation work.

## Mapping Summary
- Mapped the current repo as an active `Omni-Agent` and orchestration-heavy slice, best aligned today with an early `SLA113` runtime.
- Mapped `frontend/` and `backend/` provisionally to `Sonance Pro`, with warnings that they are still generic shells.
- Preserved absent or partial major platform layers such as `SL Universal`, `Soulfire Training Pipeline`, `Native Audio Runtime`, `Archisynapse`, and `Cultura` as architecture boundaries rather than deleting them conceptually.
- Marked template, placeholder, or ambiguous areas as `Legacy`, `Needs Review`, or `Adapter Needed` instead of flattening them into a false single-product story.
