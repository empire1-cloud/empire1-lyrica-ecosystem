# Lyrica Adapter Contracts

## Prime Directive
WE EVOLVE. NEVER DELETE.

Canon:

- Every repo matters.
- Every repo contains truth.
- We classify, connect, and evolve.
- We do not flatten, replace, or delete.

This document defines adapter contracts between Lyrica and connected systems without moving code, deleting code, or declaring that one repo replaces another.

## Source of Truth Lanes

| Lane | Source Of Truth | Adapter Purpose |
|---|---|---|
| Lyrica app implementation | `Lyrica3-pro` | Expose working product surfaces, routes, APIs, and integration evidence |
| Lyrica ecosystem architecture/orchestration | `empire1-lyrica-ecosystem` | Map subsystem boundaries, orchestration intent, memory, reports, and cross-repo coordination |
| Parent runtime and governance | `SLA113 / Empire-1` | Provide parent control plane, orchestration rules, registry, and governance contracts |
| Payment / DNA / royalties / ledger | `Archisynapse` | Provide trust, provenance, fraud, payment, and royalty services |
| Cultural intelligence / authenticity | `Cultura` | Provide cultural authenticity, dialect, heritage, and community-signal guardrails |
| Creative AI brain | `Soulfire Engine` | Provide generation, transformation, and creative reasoning services |
| Audio execution | `Native Audio Runtime` | Provide stems, DSP, Demucs, MMA, PFA, and render-time processing |
| Planning / safety / manifests | `Empire Auto Cofounder` | Provide planning discipline, approvals, preflight, manifests, and safe execution coordination |
| Adjacent entertainment surfaces | `Southern` | Provide separate entertainment and white-label experience lanes |

## Lyrica App ↔ Lyrica Ecosystem Orchestrator

Purpose:
Connect the working Lyrica app implementation to the ecosystem architecture/orchestration repo without conflating implementation and coordination.

Contract:
- The app repo provides product evidence: routes, pages, APIs, generation endpoints, and working flows.
- The ecosystem repo provides architecture mapping, orchestration docs, memory, reports, and subsystem classification.
- Cross-repo references should point to named surfaces and named contracts, not to assumptions about ownership.

Minimum adapter shape:
- Shared subsystem vocabulary
- Shared route/feature inventory
- Shared architecture references
- Shared protected-area list

What this adapter must not do:
- Rebuild the app inside the ecosystem repo
- Reclassify the app repo as the whole ecosystem
- Replace architecture mapping with only code discovery

## Lyrica ↔ SLA113 / Empire-1

Purpose:
Keep Lyrica connected to a parent runtime and governance layer without silently re-owning it inside Lyrica repos.

Contract:
- `SLA113 / Empire-1` defines control plane, universe registry, orchestration policy, and governance.
- Lyrica registers surfaces, engines, and capabilities into that parent layer through explicit interfaces.
- Lyrica consumes runtime rules and governance signals instead of duplicating them ad hoc.

Minimum adapter shape:
- Capability registration contract
- Runtime status contract
- Governance / policy contract
- Identity of owning universe and subsystem

Protected boundary:
- Lyrica should not implement a shadow control plane just because it contains local orchestration code.

## Lyrica ↔ Archisynapse

Purpose:
Connect Lyrica product flows to DNA, VICS, royalties, fraud, payments, and ledger systems while preserving Archisynapse as its own truth lane.

Contract:
- Lyrica emits track, remix, payout, and rights events.
- Archisynapse evaluates, records, resolves, and returns authoritative trust/payment state.
- Lyrica displays status and enforces product behavior based on Archisynapse responses.

Minimum adapter shape:
- DNA / provenance event contract
- Royalty event contract
- Payout / payment status contract
- Fraud / trust decision contract
- Ledger lookup contract

Protected boundary:
- Dashboard components or integration files in Lyrica are evidence of connection, not ownership transfer.

## Lyrica ↔ Cultura

Purpose:
Keep cultural intelligence and authenticity separate from generic feature logic while making it consumable by Lyrica surfaces and workflows.

Contract:
- Lyrica sends context for genre, lineage, dialect, persona, and audience/community sensitivity.
- Cultura returns authenticity constraints, warnings, scoring, or required policy outcomes.
- Lyrica applies those outcomes in creation, remix, and publishing flows.

Minimum adapter shape:
- Persona / archetype contract
- Dialect / linguistic guidance contract
- Heritage / authenticity guardrail contract
- Publishability / warning contract

Protected boundary:
- Cultura must not be reduced to a UI-only toggle or marketing label.

## Lyrica ↔ Soulfire Engine

Purpose:
Separate app surfaces from the creative AI brain while allowing generation and transformation workflows to function.

Contract:
- Lyrica app surfaces collect user intent, creator settings, and workflow context.
- Soulfire interprets that intent and returns generation plans, outputs, and creative state.
- Lyrica handles presentation, session flow, export flow, and product gating.

Minimum adapter shape:
- Generation request contract
- Generation result contract
- Session / iteration contract
- Creative metadata / provenance contract

Protected boundary:
- UI pages and route handlers must not become the sole definition of the Soulfire subsystem.

## Soulfire Engine ↔ Native Audio Runtime

Purpose:
Keep high-level creative reasoning separate from low-level render and audio-processing execution.

Contract:
- Soulfire produces render intent, structure, conditioning, and output directives.
- Native Audio Runtime performs synthesis, stems, DSP, MMA, PFA, Demucs, and processing tasks.
- Runtime returns artifacts, timing, failures, and render metadata back to Soulfire/Lyrica.

Minimum adapter shape:
- Render blueprint contract
- Stem I/O contract
- DSP / transform job contract
- Artifact / output metadata contract
- Failure / retry contract

Protected boundary:
- Runtime workers and audio engines inside app code are implementation evidence, not proof that runtime ownership must stay there forever.

## Sonance Pro ↔ SL Universal

Purpose:
Keep creator-studio and public listening/remix surfaces distinct while enabling creator-to-audience flows.

Contract:
- Sonance Pro produces tracks, metadata, proof, exports, and creator controls.
- SL Universal consumes publishable assets, public metadata, remix permissions, and audience interaction state.
- Shared proof, rights, and cultural constraints must survive the handoff.

Minimum adapter shape:
- Publish/export contract
- Track proof / provenance contract
- Remix permission contract
- Audience interaction / feedback contract

Protected boundary:
- Do not flatten studio and listening surfaces into one generic frontend model.

## Lyrica ↔ Empire Auto Cofounder

Purpose:
Connect Lyrica planning and execution discipline to a separate planning/safety/manifests lane.

Contract:
- Lyrica repos expose architecture state, task context, and protected boundaries.
- Empire Auto Cofounder produces planning structure, preflight discipline, approval checkpoints, manifests, and safe next actions.
- Execution discipline stays separate from product runtime logic.

Minimum adapter shape:
- Repo/state intake contract
- Approval / preflight contract
- Manifest / handoff contract
- Safe execution recommendation contract

Protected boundary:
- Empire Auto Cofounder should not become hidden runtime behavior inside product repos.

## Lyrica ↔ Southern

Purpose:
Allow Lyrica to connect to adjacent entertainment and white-label surfaces without collapsing universes together.

Contract:
- Lyrica may export or expose approved assets, experiences, or APIs for Southern-facing use cases.
- Southern keeps its own surface logic, audience logic, and business logic.
- Crossovers remain adapter-based and explicit.

Minimum adapter shape:
- Experience export contract
- White-label asset contract
- Rights / usage constraint contract

Protected boundary:
- Southern should remain its own universe lane, not a renamed Lyrica feature bucket.

## Anti-Flattening Rules

1. Do not treat `Lyrica3-pro` as the whole ecosystem.
2. Do not treat `empire1-lyrica-ecosystem` as the full app implementation.
3. Do not treat adapter files as proof of subsystem ownership transfer.
4. Do not merge `Soulfire Engine` into UI just because generation endpoints live in app code.
5. Do not merge `Native Audio Runtime` into app ownership just because workers currently live near backend code.
6. Do not merge `Archisynapse` into Lyrica just because royalty or DNA integration code exists.
7. Do not merge `Cultura` into product features as if authenticity were optional decoration.
8. Do not merge `SLA113 / Empire-1` into local orchestration scripts as if parent governance were app-local.
9. Do not flatten `Sonance Pro` and `SL Universal` into one generic frontend surface.
10. Preserve working code, then classify and connect it through contracts.

## Adapter Priority

| Priority | Adapter | Why First |
|---|---|---|
| P0 | Lyrica App ↔ Lyrica Ecosystem Orchestrator | Needed to keep architecture docs and app evidence synchronized without ownership confusion |
| P0 | Lyrica ↔ Soulfire Engine | Central to generation flows and product boundary clarity |
| P0 | Soulfire Engine ↔ Native Audio Runtime | Central to render execution and audio artifact flow |
| P0 | Lyrica ↔ Archisynapse | Central to DNA, royalties, payments, and trust-critical flows |
| P1 | Lyrica ↔ SLA113 / Empire-1 | Needed to prevent control-plane duplication and governance drift |
| P1 | Lyrica ↔ Cultura | Needed to preserve authenticity and community-signal enforcement |
| P1 | Sonance Pro ↔ SL Universal | Needed to preserve creator-to-audience boundary and publishing logic |
| P2 | Lyrica ↔ Empire Auto Cofounder | Needed for planning/preflight discipline across future work |
| P2 | Lyrica ↔ Southern | Needed when cross-universe entertainment experiences become active |

## Recommended Next Actions

1. Convert the `P0` adapters into explicit contract tables with request, response, owner, and protected fields.
2. Cross-reference each adapter against concrete evidence paths in `Lyrica3-pro` and `empire1-lyrica-ecosystem` without changing code.
3. Add a protected-fields appendix for DNA, royalties, authenticity signals, and runtime metadata.
4. Identify where current local files are only integration evidence versus true ownership boundaries.
5. Use this contract doc as the prerequisite before any refactor that touches Lyrica, Soulfire, Native Audio Runtime, Archisynapse, Cultura, or SLA113-adjacent code.
