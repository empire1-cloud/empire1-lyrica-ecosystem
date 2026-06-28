# Lyrica App Crosscheck

## Prime Directive
WE EVOLVE. NEVER DELETE.

## Repos Compared
- `empire1-lyrica-ecosystem` = Lyrica ecosystem architecture/orchestration repo
- `Lyrica3-pro` = Lyrica app/product implementation repo

## Critical Correction
Not every subsystem should physically live inside `Lyrica3-pro`.

`Lyrica3-pro` may contain UI surfaces, API routes, stubs, adapters, or proof-of-concept integrations for subsystems whose real ownership belongs elsewhere.

Do not mark `Archisynapse`, `Cultura`, `SLA113`, `Southern`, or `Empire Auto Cofounder` as missing just because they are not folders inside `Lyrica3-pro`.

## Source of Truth By Lane

| Repo / System | Source of Truth For | What It Proves | What It Must Not Become |
|---|---|---|---|
| `empire1-lyrica-ecosystem` | Lyrica ecosystem architecture, orchestration, agent memory, reports, cross-repo coordination | The ecosystem frame, orchestration intent, memory, runtime reporting, and architecture mapping | It must not become a false claim that it already contains the full product implementation |
| `Lyrica3-pro` | Current app implementation, product surfaces, routes, backend APIs, working product evidence | The current running app shape, concrete UI surfaces, concrete API routes, and integration evidence | It must not become a claim that it owns every adjacent subsystem |
| `Archisynapse` | DNA, VICS, royalties, fraud, payments, ledger | That trust, payout, and provenance logic belong in their own truth lane | It must not become embedded app glue with no boundary |
| `Cultura` | Cultural intelligence, authenticity, dialect, heritage, community signal | That cultural guardrails are their own layer, not cosmetic UI | It must not become flattened into a generic feature flag or app-only widget |
| `SLA113 / Empire-1` | Parent runtime, control plane, universe registry, orchestration, governance | That parent orchestration and federation rules exist above the app layer | It must not become duplicated ad hoc inside product repos |
| `Southern` | Entertainment, arcade, white-label experiences | That adjacent entertainment surfaces can exist as separate universe logic | It must not become absorbed into Lyrica naming just because the repos are related |
| `Empire Auto Cofounder` | Planning, safety gates, approvals, preflight, manifests, Hermes intake, execution discipline | That execution governance and planning discipline can remain separate from product runtime | It must not become hidden as undocumented app-side behavior |

## Ownership Model

| Subsystem | Correct Ownership Frame |
|---|---|
| Lyrica Platform | Music product universe / parent platform |
| Sonance Pro | Lyrica creator-studio surface |
| SL Universal | Lyrica listening/remix surface |
| Soulfire Engine | Creative AI brain; may be app-integrated but should stay separate from UI |
| Soulfire Training Pipeline | Training/data/culture/persona pipeline; may be external or future service |
| Native Audio Runtime | Audio processing runtime; may be separate local/service package |
| Archisynapse | External connected payment/DNA/royalty/ledger subsystem |
| Cultura | External/adjacent cultural authenticity subsystem |
| SLA113 | Parent orchestration/control plane, not owned by Lyrica app |
| Southern | Separate entertainment/arcade universe |
| Empire Auto Cofounder | Separate command brain / safety planner |

## Evidence Found In Lyrica3-pro

### Lyrica Platform
- Evidence path(s): [README.md](/home/shiestybizz113/projects/Lyrica3-pro/README.md), [frontend/src/routes.tsx](/home/shiestybizz113/projects/Lyrica3-pro/frontend/src/routes.tsx)
- What the evidence proves: `Lyrica3-pro` is source of truth for current app implementation, product surfaces, routes, backend APIs, and working product evidence.
- What it does NOT prove: it does not prove that all ecosystem ownership lives in the app repo.
- Classification: `Present in Lyrica3-pro`

### Sonance Pro
- Evidence path(s): [frontend/src/pages/Studio.tsx](/home/shiestybizz113/projects/Lyrica3-pro/frontend/src/pages/Studio.tsx), [frontend/src/pages/MakeMusic.tsx](/home/shiestybizz113/projects/Lyrica3-pro/frontend/src/pages/MakeMusic.tsx), [memory/PRD.md](/home/shiestybizz113/projects/Lyrica3-pro/memory/PRD.md)
- What the evidence proves: the app repo is source of truth for the current creator-studio implementation lane.
- What it does NOT prove: it does not prove Sonance Pro should be collapsed into a generic frontend shell.
- Classification: `Present in Lyrica3-pro`

### SL Universal
- Evidence path(s): [frontend/src/pages/Radio.tsx](/home/shiestybizz113/projects/Lyrica3-pro/frontend/src/pages/Radio.tsx), [frontend/src/features/radio/pages/RadioDirectoryPage.tsx](/home/shiestybizz113/projects/Lyrica3-pro/frontend/src/features/radio/pages/RadioDirectoryPage.tsx), [frontend/src/features/radio/components/SLMediaExportPanel.tsx](/home/shiestybizz113/projects/Lyrica3-pro/frontend/src/features/radio/components/SLMediaExportPanel.tsx)
- What the evidence proves: the app repo is source of truth for the current listening, radio, and remix-facing app surfaces.
- What it does NOT prove: it does not prove SL Universal is only a sub-panel of Sonance Pro.
- Classification: `Present in Lyrica3-pro`

### Soulfire Engine
- Evidence path(s): [api/main.py](/home/shiestybizz113/projects/Lyrica3-pro/api/main.py), [soulfire_kernel/kernel.py](/home/shiestybizz113/projects/Lyrica3-pro/soulfire_kernel/kernel.py), [backend/lyrica_agent/orchestrator.py](/home/shiestybizz113/projects/Lyrica3-pro/backend/lyrica_agent/orchestrator.py)
- What the evidence proves: the app repo contains direct Soulfire-facing integration and implementation evidence.
- What it does NOT prove: it does not prove Soulfire’s final ownership boundary should collapse into the app repo.
- Classification: `Present in Lyrica3-pro`, `Adapter Needed`

### Soulfire Training Pipeline
- Evidence path(s): [backend/prompts/](/home/shiestybizz113/projects/Lyrica3-pro/backend/prompts), [backend/agents/](/home/shiestybizz113/projects/Lyrica3-pro/backend/agents), [backend/lyrica_agent/slang_dictionary_v1.json](/home/shiestybizz113/projects/Lyrica3-pro/backend/lyrica_agent/slang_dictionary_v1.json), [backend/schemas/soulfire_payload.json](/home/shiestybizz113/projects/Lyrica3-pro/backend/schemas/soulfire_payload.json)
- What the evidence proves: training-adjacent assets and persona/culture inputs are present in the app implementation repo.
- What it does NOT prove: it does not prove the full training pipeline should live inside the app repo.
- Classification: `Needs Contract`, `Legacy / Needs Review`

### Native Audio Runtime
- Evidence path(s): [backend/audio_engine.py](/home/shiestybizz113/projects/Lyrica3-pro/backend/audio_engine.py), [backend/demucs_worker.py](/home/shiestybizz113/projects/Lyrica3-pro/backend/demucs_worker.py), [backend/mma_worker.py](/home/shiestybizz113/projects/Lyrica3-pro/backend/mma_worker.py), [backend/pfa_worker.py](/home/shiestybizz113/projects/Lyrica3-pro/backend/pfa_worker.py), [backend/music_engine/](/home/shiestybizz113/projects/Lyrica3-pro/backend/music_engine)
- What the evidence proves: the app repo contains working audio-processing paths and runtime evidence.
- What it does NOT prove: it does not prove the Native Audio Runtime should be permanently owned by the app repo instead of an adjacent runtime lane.
- Classification: `Present in Lyrica3-pro`, `External Connected Subsystem`, `Adapter Needed`

### Archisynapse
- Evidence path(s): [backend/archisynapse_integration.py](/home/shiestybizz113/projects/Lyrica3-pro/backend/archisynapse_integration.py), [frontend/src/features/radio/pages/ArchisynapseDashboard.tsx](/home/shiestybizz113/projects/Lyrica3-pro/frontend/src/features/radio/pages/ArchisynapseDashboard.tsx), [backend/micro_royalty_distributor.py](/home/shiestybizz113/projects/Lyrica3-pro/backend/micro_royalty_distributor.py)
- What the evidence proves: the app repo contains Archisynapse integration evidence.
- What it does NOT prove: it does not prove Archisynapse belongs physically inside `Lyrica3-pro`.
- Classification: `External Connected Subsystem`, `Adapter Needed`, `Needs Contract`

### Cultura
- Evidence path(s): [cultura/frontend/src/App.js](/home/shiestybizz113/projects/Lyrica3-pro/cultura/frontend/src/App.js), [README.md](/home/shiestybizz113/projects/Lyrica3-pro/README.md)
- What the evidence proves: the app-adjacent codebase contains Cultura evidence and references.
- What it does NOT prove: it does not prove Cultura is owned by the app repo rather than its own truth lane.
- Classification: `External Connected Subsystem`, `Needs Contract`, `Legacy / Needs Review`

### SLA113
- Evidence path(s): [sla113_governance/pipeline_compiler/compiler.py](/home/shiestybizz113/projects/Lyrica3-pro/sla113_governance/pipeline_compiler/compiler.py), [sla113_governance/engine_interfaces/engine_service.proto](/home/shiestybizz113/projects/Lyrica3-pro/sla113_governance/engine_interfaces/engine_service.proto), [sla113_governance/universe_manifests/universes.yaml](/home/shiestybizz113/projects/Lyrica3-pro/sla113_governance/universe_manifests/universes.yaml)
- What the evidence proves: the app repo contains SLA113-related governance and interface evidence.
- What it does NOT prove: it does not prove the app repo owns the parent control plane.
- Classification: `External Connected Subsystem`, `Adapter Needed`, `Needs Contract`

### Southern
- Evidence path(s): [README.md](/home/shiestybizz113/projects/Lyrica3-pro/README.md)
- What the evidence proves: Southern is referenced as a separate universe lane.
- What it does NOT prove: it does not prove Southern should be pulled into the app repo.
- Classification: `External Connected Subsystem`

### Empire Auto Cofounder
- Evidence path(s): no direct app-local implementation evidence found in the inspected `Lyrica3-pro` paths
- What the evidence proves: no direct lane ownership inside the app repo in this pass.
- What it does NOT prove: it does not prove the subsystem is absent from the ecosystem.
- Classification: `External Connected Subsystem`, `Needs Contract`

### Legacy / Needs Review
- Evidence path(s): [cultura/frontend/src/App.js](/home/shiestybizz113/projects/Lyrica3-pro/cultura/frontend/src/App.js), generated assets under `frontend/build/`, local infra under `.local/`, deployment metadata under `.vercel/`
- What the evidence proves: some named subsystem areas are thin, placeholder-like, generated, or environment-specific.
- What it does NOT prove: it does not prove those lanes should be deleted.
- Classification: `Legacy / Needs Review`

## Evidence Found In empire1-lyrica-ecosystem
- [LYRICA_ARCHITECTURE.md](/home/shiestybizz113/projects/empire1-lyrica-ecosystem/LYRICA_ARCHITECTURE.md)
  This repo is source of truth for the current Lyrica ecosystem architecture framing.
- [memory/PRD.md](/home/shiestybizz113/projects/empire1-lyrica-ecosystem/memory/PRD.md)
  This repo is source of truth for the current internal orchestration slice requirements.
- [omni_agent/](/home/shiestybizz113/projects/empire1-lyrica-ecosystem/omni_agent)
  This repo is source of truth for the current internal orchestration, guardrail, and reporting runtime in its lane.
- [omni_agent/reports/latest.md](/home/shiestybizz113/projects/empire1-lyrica-ecosystem/omni_agent/reports/latest.md)
  Reporting and execution evidence live here.
- [memory/tasks/](/home/shiestybizz113/projects/empire1-lyrica-ecosystem/memory/tasks)
  Operating memory and task intake live here.
- [backend/](/home/shiestybizz113/projects/empire1-lyrica-ecosystem/backend), [frontend/](/home/shiestybizz113/projects/empire1-lyrica-ecosystem/frontend)
  These are scaffolds and support surfaces in the architecture/orchestration repo, not proof of the full product implementation.

This repo is source of truth for Lyrica ecosystem architecture, orchestration, agent memory, reports, and cross-repo coordination.

## Cross-Repo Ownership Risks
- Mistaking adapter files for subsystem ownership.
- Treating the app repo as the whole ecosystem.
- Duplicating SLA113 governance between repos.
- Mixing Soulfire AI brain with UI components.
- Mixing Archisynapse payment/ledger logic directly into app code.
- Treating Cultura as a feature instead of a guardrail layer.
- Flattening Sonance Pro and SL Universal into one generic frontend.

## Adapter / Contract Needs

### Lyrica ↔ SLA113
Define how the app consumes parent orchestration, runtime control, and governance without re-owning them.

### Lyrica ↔ Archisynapse
Define contracts for DNA, VICS, royalties, fraud, payments, ledger events, and payout states.

### Lyrica ↔ Cultura
Define contracts for authenticity, dialect, heritage, persona, and community-signal guardrails.

### Lyrica ↔ Soulfire
Define the boundary between app surfaces and the creative AI brain.

### Soulfire ↔ Native Audio Runtime
Define the render/runtime handoff for stems, DSP, MMA, PFA, Demucs, and output lifecycle.

### Sonance Pro ↔ SL Universal
Define the boundary for export, remix provenance, listening surfaces, and creator-to-audience flow.

### Lyrica ↔ Empire Auto Cofounder
Define how planning, safety gates, approvals, manifests, and preflight discipline connect without being buried inside app logic.

## Protected Areas

### In empire1-lyrica-ecosystem
- [LYRICA_ARCHITECTURE.md](/home/shiestybizz113/projects/empire1-lyrica-ecosystem/LYRICA_ARCHITECTURE.md)
- [memory/](/home/shiestybizz113/projects/empire1-lyrica-ecosystem/memory)
- [omni_agent/guardrails.py](/home/shiestybizz113/projects/empire1-lyrica-ecosystem/omni_agent/guardrails.py)
- [omni_agent/state_machine.py](/home/shiestybizz113/projects/empire1-lyrica-ecosystem/omni_agent/state_machine.py)
- [omni_agent/config.yaml](/home/shiestybizz113/projects/empire1-lyrica-ecosystem/omni_agent/config.yaml)
- [omni_agent/state/](/home/shiestybizz113/projects/empire1-lyrica-ecosystem/omni_agent/state)
- [omni_agent/reports/](/home/shiestybizz113/projects/empire1-lyrica-ecosystem/omni_agent/reports)

### In Lyrica3-pro
- [frontend/src/routes.tsx](/home/shiestybizz113/projects/Lyrica3-pro/frontend/src/routes.tsx)
  Protected working route evidence.
- [frontend/src/pages/Studio.tsx](/home/shiestybizz113/projects/Lyrica3-pro/frontend/src/pages/Studio.tsx), [frontend/src/pages/Radio.tsx](/home/shiestybizz113/projects/Lyrica3-pro/frontend/src/pages/Radio.tsx), [frontend/src/pages/MakeMusic.tsx](/home/shiestybizz113/projects/Lyrica3-pro/frontend/src/pages/MakeMusic.tsx)
  Protected app-surface evidence.
- [backend/server.py](/home/shiestybizz113/projects/Lyrica3-pro/backend/server.py), [api/main.py](/home/shiestybizz113/projects/Lyrica3-pro/api/main.py)
  Protected working API evidence.
- [soulfire_kernel/](/home/shiestybizz113/projects/Lyrica3-pro/soulfire_kernel), [backend/music_engine/](/home/shiestybizz113/projects/Lyrica3-pro/backend/music_engine), [backend/demucs_worker.py](/home/shiestybizz113/projects/Lyrica3-pro/backend/demucs_worker.py), [backend/mma_worker.py](/home/shiestybizz113/projects/Lyrica3-pro/backend/mma_worker.py), [backend/pfa_worker.py](/home/shiestybizz113/projects/Lyrica3-pro/backend/pfa_worker.py)
  Protected audio generation and runtime evidence.
- [backend/archisynapse_integration.py](/home/shiestybizz113/projects/Lyrica3-pro/backend/archisynapse_integration.py), [frontend/src/features/radio/pages/ArchisynapseDashboard.tsx](/home/shiestybizz113/projects/Lyrica3-pro/frontend/src/features/radio/pages/ArchisynapseDashboard.tsx)
  Protected DNA/VICS/royalty/ledger integration evidence.
- [cultura/frontend/src/App.js](/home/shiestybizz113/projects/Lyrica3-pro/cultura/frontend/src/App.js)
  Protected Cultura evidence.
- Deployment configs such as [frontend/vercel.json](/home/shiestybizz113/projects/Lyrica3-pro/frontend/vercel.json), [render.yaml](/home/shiestybizz113/projects/Lyrica3-pro/render.yaml), [railway.toml](/home/shiestybizz113/projects/Lyrica3-pro/railway.toml)
  Protected deployment evidence.

## Corrected Bottom Line
Every repo matters.
Every repo contains truth.
The job is not to flatten them.
The job is to classify each repo’s truth, preserve working code, and connect the system through adapters.

`Lyrica3-pro` proves current app implementation.
`empire1-lyrica-ecosystem` proves ecosystem orchestration and architecture intent.
`Archisynapse`, `Cultura`, `SLA113 / Empire-1`, `Southern`, and `Empire Auto Cofounder` remain their own truth lanes.
The next step is to define adapter contracts, not delete or collapse repos.
