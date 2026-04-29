# Omni-Agent — One-Page Offer Sheet

_Print / PDF-ready. One page at 11pt._

---

## Omni-Agent
**Turn unfinished tasks in your repo into finished tasks — with a full audit trail.**

An internal, persona-based execution loop for engineering backlogs. Scans your markdown notes for `- [ ]`, `TODO:`, `FIXME:`; runs Analyst → Developer → Evaluator; writes the change inside your allowed paths; produces a cohesion-scored client report, ROI metrics, and a PR preview. Ships nothing unless it passes evaluation.

---

## WHO IT'S FOR

- Founders and CTOs of 3–30-person engineering teams with a persistent backlog.
- Agencies shipping client work who need audit-grade evidence per delivery.
- Compliance-sensitive orgs (fintech, health, defense) that need strict black-box guardrails before letting AI near the repo.

---

## WHAT YOU GET

1. **Client Report Generator** — markdown + JSON per run; executive summary, tasks completed, evidence, blockers, risks, next 7-day plan, time-saved estimate.
2. **ROI Tracker** — live metrics from a local SQLite audit trail: tasks completed, avg cohesion score, blocked rate, test pass rate, hours & cost saved. Weekly / monthly windows.
3. **PR Autopilot (preview)** — one command converts a done task into a ready-to-paste PR body: summary, files changed, test evidence, risk notes, rollback instructions.
4. **Hybrid persona engine** — LLM (Claude Sonnet 4.5) with rule-based fallback when LLM is rate-limited or unavailable. You choose the mode per workspace.
5. **Strict black-box guardrails** — configurable allowed / forbidden paths. Hard-block of `.env`, `secrets/**`, `keys/**`. Every write pre-checked.
6. **Audit-grade state** — SQLite store with 7 tables, including per-run `state_transitions` and full persona output history. Exportable as JSON.

---

## IMPLEMENTATION TIMELINE

| Day | Milestone |
|---|---|
| Day 0 | Install CLI (pip + config.yaml). First `scan`. |
| Day 1 | First `run-next --dry-run` on your real backlog. Guardrails tuned to your repo. |
| Day 2 | First real task closed end-to-end. First client report generated. |
| Day 3–5 | Five more tasks completed. ROI baseline established. |
| Day 7 | Weekly ROI review. Threshold + guardrail policy finalized. |
| Day 14 | Pilot conversion: you have measurable savings or you walk with the data. |

---

## PRICING

- **Free** — rule mode, 1 workspace, 25 tasks/mo. Try the loop.
- **Pro — $49 / seat / month** — hybrid LLM, 500 tasks/mo, all three monetized modules, email support.
- **Team — $299 / month** — 10 seats, 5,000 tasks/mo, Slack/Linear/GitHub webhooks, priority support.
- **Enterprise — from $2,000 / month** — self-host, SSO, policies-as-code, audit export, 4h SLA.

Annual = 2 months free. Seat add-ons available at any tier.

---

## SUCCESS METRICS (what we measure at day 14)

- Tasks closed with cohesion ≥ 85: **target ≥ 10**
- Average cohesion score across runs: **target ≥ 85**
- Hours saved per week: **target ≥ 8**
- Blocked rate (blocked ÷ total): **target ≤ 20%**
- Forbidden-path write attempts: **target = 0** (guardrails never breached)

All five come straight from the ROI Tracker. No custom instrumentation.

---

## GUARANTEE / RISK REVERSAL

**14-day pilot guarantee.** If at the end of the pilot Omni-Agent has not produced the five success metrics above on your real backlog, you pay nothing and keep the generated reports + audit DB. No clawback. No lock-in.

**Data guarantee.** Runs execute on your machine. State stays in your repo. We never see your code, your tasks, or your reports.

**Cancellation.** Monthly plans: cancel any time, prorated to the period end. Annual: 14-day refund window.

---

## NEXT STEP

Email **founder@omni-agent.dev** with the repo path you'd point it at, and we'll schedule a 20-minute demo this week.
