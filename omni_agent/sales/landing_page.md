# Omni-Agent — Landing Page Copy

> Tone: clear, confident, no hype. Evidence over promises. Audience: founders, CTOs, tech leads.

---

## HERO

### Close your `TODO.md`. With receipts.

**Omni-Agent turns unfinished tasks in your repo into finished tasks with a full audit trail — every run produces a cohesion-scored client report, tracked ROI, and a PR-ready preview.**

[ Start free — one command ]    [ Book a 20-min demo ]

_Runs on your machine. Reads only allowed paths. Ships only what passes evaluation._

---

## PROBLEM — _Why teams lose money without this_

Engineering backlogs don't die from lack of ideas. They die from **untracked, unfinished middle work** — the `TODO:` left in a PR, the `FIXME:` in the service file, the unchecked box in `inbox.md`.

- A typical backlog item costs **45–90 minutes of engineer time** to triage, scope, implement, and verify.
- Most of that time is spent on **scoping and evaluation**, not writing code.
- LLM tools can draft code, but they don't:
  - prove the change meets acceptance criteria,
  - respect your "do-not-touch" paths,
  - produce audit-grade evidence a reviewer can sign off on,
  - or tell you the ROI of what you shipped this week.

The result: your AI is fast but reviewers are the bottleneck, and nobody can answer "what did the bot actually save us?"

---

## SOLUTION — _Three products in one CLI_

### 1. Client Report Generator
Every run produces a markdown + JSON report with:
executive summary, tasks completed, evidence (criteria, tests, artifacts), blockers, risks, next 7-day plan, and time saved. Handed to your client, your CTO, or your board without editing.

### 2. ROI Tracker
Live metrics from the same state DB: tasks completed, average cohesion score, blocked rate, test pass rate, hours saved, cost saved. Configurable assumptions. Weekly + monthly windows. Queryable history.

### 3. PR Autopilot (preview)
One command turns a completed task into a ready-to-paste PR body — summary, files changed, test evidence, risk notes, rollback instructions. Refuses to generate if the task didn't pass evaluation.

All three ride on the same core: **Analyst → Developer → Evaluator** with strict black-box guardrails. Nothing ships without passing a cohesion score of 85/100 by default.

---

## HOW IT WORKS (3 steps)

### 1. Drop your tasks in a markdown file
`- [ ]`, `TODO:`, `FIXME:` — Omni-Agent scans `memory/tasks/**/*.md` and registers each one.

### 2. Run the loop
```
python scripts/omni_agent.py run-next
```
Analyst writes a mini-spec. Developer applies a minimal patch inside your allowed paths. Evaluator runs tests, checks acceptance criteria, and computes a cohesion score.

### 3. Ship with evidence
Done? The checkbox flips to `[x]` with a timestamp, a client report lands in `reports/client/`, and the ROI tracker updates. Ask for a PR preview and it writes the PR body for you.

Blocked? It says so explicitly — `blocked_stage: pre_analyst`, `blocked_reason: missing_context_low_confidence` — and annotates the task in your markdown so the next scan sees it.

---

## ROI PROOF — _How the math works_

Every run writes to a SQLite audit table. The ROI Tracker reads it directly. No telemetry, no servers, no black boxes.

**Default assumptions (editable in `config.yaml`):**
- `minutes_per_task_manual`: **60**
- `dev_hourly_rate`: **$100**

**`REPLACE-BEFORE-PUBLISH` — paste your own output from `python scripts/omni_agent.py status --json | jq .roi_weekly`.**

For reference, the current state DB in this repo produces:

| Metric | Value |
|---|---|
| Tasks completed | 3 of 4 |
| Avg. cohesion score | 80.25 |
| Blocked rate | 25% |
| Hours saved (7d) | 3.0 |
| Cost saved (7d) | **USD 300** |

These are the exact numbers emitted by the ROI Tracker on the repo where Omni-Agent itself was built. Swap in your own before publishing.

> Claim boundary: we report the numbers the state DB contains. We do not estimate future savings or inflate. The only soft assumption is minutes-per-task — you set it.

---

## PLAN COMPARISON

| | **Free** | **Pro** $49/seat/mo | **Team** $299/mo | **Enterprise** |
|---|:-:|:-:|:-:|:-:|
| Rule-mode personas | ✅ | ✅ | ✅ | ✅ |
| Hybrid / LLM mode | — | ✅ | ✅ | ✅ |
| Client Reports | — | ✅ | ✅ | ✅ |
| ROI Tracker | — | ✅ | ✅ | ✅ |
| PR Autopilot preview | — | ✅ | ✅ | ✅ |
| Slack / Linear / GitHub webhooks | — | — | ✅ | ✅ |
| SSO + Self-host | — | — | — | ✅ |
| Tasks / month | 25 | 500 | 5,000 | Unlimited |

[ See full pricing → ](/pricing)

---

## FAQ

**Q. Does it run in my repo or on your servers?**
On your machine. The CLI is Python. The state is a local SQLite file. We never see your code.

**Q. What LLM does it use?**
Anthropic Claude Sonnet 4.5 by default, via Emergent Universal Key or your own Anthropic key. Rule mode works with no LLM at all.

**Q. What if the LLM is rate-limited or down?**
Hybrid mode auto-falls back to deterministic rule-based personas and logs which mode was used per task. You're never stuck.

**Q. Can it touch my `.env` or secrets?**
No. The guardrails hard-block `**/.env*`, `**/secrets/**`, `**/keys/**`, and anything you add to `forbidden_paths` in config.

**Q. How do I stop it from modifying a specific folder?**
Add the glob to `guardrails.forbidden_paths` in `config.yaml`. Every write is pre-checked against that list.

**Q. Will it open a PR automatically?**
Not unless you turn it on (Team tier and above). By default it produces a PR **preview** — a markdown body you can paste into GitHub manually. The preview refuses to generate if the task hasn't passed evaluation.

**Q. What about sensitive code — finance, health, defense?**
Enterprise tier adds policies-as-code, SSO, audit-log export (JSONL/Parquet), and self-hosted deploy. Your compliance team reviews the guardrail spec before anything runs.

**Q. What makes a task "done"?**
A cohesion score ≥ 85/100. The score weighs acceptance criteria (35%), tests (25%), regression checks (20%), code quality/lint (10%), and guardrail compliance (10%). Threshold is configurable.

**Q. What's the setup cost?**
Free tier: one command. Pro/Team: paste in a key. Enterprise: 30-minute kickoff with a success engineer.

**Q. Can I cancel anytime?**
Yes. Monthly plans cancel at the end of the current period. Annual plans are refundable in the first 14 days.

---

## CTA

### Start for free. Ship with receipts.

The fastest way to find out if this works for your team is to run it on one stale `inbox.md` tonight.

[ **Start free — one command** ](/#install)
[ **Book a 20-min demo** ](/demo)

_No credit card for Free. No seat minimum for Pro. No procurement deck for Enterprise pilots._
