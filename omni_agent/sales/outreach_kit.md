# Omni-Agent — Outreach Kit

_Founder-led outbound. Evidence > flattery. No fake social proof._

---

## Cold DMs (3 variants — 300 char max, Twitter/X / LinkedIn)

### Variant 1 — for **founders** (SaaS, seed/Series-A)
> Saw you're hiring your first eng hire. Before you do: I built a CLI that closes the stale `TODO.md` in your repo, produces an audit-grade report per run, and tells you hours-saved at the end of the week. 14-day pilot, no card, real numbers. Want to try it on one repo?

### Variant 2 — for **agency owners**
> If your devs spend half their week triaging client backlogs: I have a thing. One command closes stale tasks inside strict black-box rules (no `.env`, no `secrets/`), and every run prints a client-ready markdown report with cohesion score + time saved. DM if you want to pilot it on one client repo this month.

### Variant 3 — for **CTOs**
> Question: can you prove what your AI coding tools shipped last week? We built an execution loop (Analyst → Developer → Evaluator) that writes an audit-grade SQLite trail per run + a PR-ready preview. Runs on your machine. 14-day pilot if you have a messy backlog.

---

## Cold emails (3 variants — ≤ 120 words)

### Email 1 — _Problem-first, for CTOs_

> **Subject:** Your AI codes. Can you prove what it shipped?
>
> Hi {first_name},
>
> We built a CLI for the painful middle of AI-assisted engineering: after the LLM generates code, *who* verifies the change meets acceptance criteria, respects your allowed paths, and is worth shipping?
>
> Omni-Agent runs Analyst → Developer → Evaluator inside strict black-box guardrails and, per run, produces a markdown client report, a live ROI tracker, and a PR-ready preview. SQLite audit trail. Self-host available.
>
> If {company} has a stale `TODO.md` in a real repo, I'd love to run a 14-day pilot — you keep the data either way.
>
> 20-minute demo this week?
>
> — {sender}

---

### Email 2 — _ROI-first, for founders_

> **Subject:** The ROI number from last week's backlog runs
>
> {first_name},
>
> I'm building Omni-Agent. It closes unfinished tasks in markdown notes (`TODO:`, `- [ ]`) using a persona-based loop that writes only inside allowed paths and refuses to mark anything done below an 85/100 cohesion score.
>
> Every run emits a client report with evidence, blockers, risks, and a cost-saved number computed from the local audit DB. Before sending this email, paste your own numbers here from `status --json | jq .roi_weekly` — whatever they are, they're real, and that's the point.
>
> If that's the kind of number your team wants to see, I can set it up on one of your repos in 15 minutes. Free tier is real.
>
> — {sender}

---

### Email 3 — _Agencies, client-billing angle_

> **Subject:** A per-sprint report your clients will actually read
>
> Hey {first_name},
>
> Most client status docs are written by humans after the fact. Omni-Agent produces them per run, straight out of the execution loop — exec summary, tasks completed with cohesion scores, test evidence, blockers, risks, and next 7-day plan.
>
> White-label add-on available on Team tier. If {agency} is shipping a lot of backlog work for clients, I'd like to offer you a 14-day pilot on one client repo at no cost.
>
> Worth a 20-minute call?
>
> — {sender}

---

## Follow-up sequence (3 touches after initial cold email)

### Touch 2 — Day +3 (short nudge)
> **Subject:** re: your AI codes
>
> Bumping this in case it slipped. Happy to send the 2-minute demo video or just drop the README link — whichever fits.
>
> If Omni-Agent isn't the right shape for {company}, a quick "not now" is genuinely helpful. No hard feelings.

### Touch 3 — Day +7 (evidence drop)
> **Subject:** Here's the report output (no pitch)
>
> Attaching a real markdown report from a backlog run I did this morning. Sections: exec summary, tasks completed with cohesion, evidence, blockers, risks, next 7-day plan, time saved.
>
> This is the artifact your team would get per run. If it looks useful, happy to set up a pilot. If not, you've got a template you can steal.

### Touch 4 — Day +14 (break-up)
> **Subject:** Closing the loop
>
> I'll stop reaching out after this. If the stale-backlog problem comes back on your radar, the 14-day pilot stands — no procurement, no card.
>
> Wishing {company} a quiet `TODO.md`.

---

## Discovery call script (20 min)

### Minutes 0:00–2:00 — Frame
> "Thanks for the time. I'll keep this to 20 minutes. Plan: 3 minutes you talk, 7 minutes I show, 10 minutes we decide if a pilot makes sense. Sound good?"

### 2:00–5:00 — Qualify (ask, don't pitch)
1. "Walk me through how unfinished backlog tasks die at {company} today. Where do `TODO:` lines end up?"
2. "Who signs off on AI-generated code today? What do they need to see to sign off?"
3. "If you had to pick one repo where 10 closed tasks this month would actually matter — which one?"
4. _(If founder)_ "What's the cost to {company} of a stale backlog? How do you think about it?"
5. _(If CTO)_ "Any paths in that repo you'd never let an AI touch? I want to make sure our guardrails cover them before I show anything."

### 5:00–12:00 — Live demo
Run the **Demo Script** (see `demo_script.md`). Don't deviate. 5 minutes.

### 12:00–17:00 — Tailor the offer
- Name the repo and 3 tasks you'd target in the pilot (picked from their answer to Q3).
- Confirm their forbidden paths will be in `guardrails.forbidden_paths`.
- State the 14-day pilot: success metrics, no card, walk-away guarantee.

### 17:00–19:00 — Handle objections
Use objection sheet. Short answers. Don't over-sell.

### 19:00–20:00 — Close with next step
> "Two options: 1) We start the pilot this week — I'll send the config template and book a 30-minute kickoff. 2) You want to think — totally fine, pick a day next week and I'll resend the doc. Which works?"

---

## Objection handling sheet (top 10)

| # | Objection | Response |
|---|---|---|
| 1 | "We already use Cursor / Copilot / Claude Code." | "Those write code. We close *tasks* — with acceptance criteria, cohesion score, and a report. They're complementary. Several teams run both." |
| 2 | "Our backlog is in Linear / Jira, not markdown." | "Start by exporting the top 10 stuck items to one markdown file. Takes 5 minutes. We'll add a Linear/Jira connector in Team tier — on the roadmap this quarter." |
| 3 | "Sounds risky letting an AI write to our repo." | "That's why the guardrails exist. You list forbidden paths in config; every write is pre-checked. `.env`, `secrets/`, and `keys/` are hard-blocked by default. Dry-run mode lets you preview every patch before any file is touched." |
| 4 | "We don't trust LLM output quality." | "Neither do we. The Evaluator runs tests and checks acceptance criteria. Anything below 85/100 cohesion is marked `evaluating_failed`, not `done`. The PR preview refuses to generate for non-done tasks." |
| 5 | "Pricing is too high / too low." | _(High)_: "Run the free tier. The Pro number is less than 45 minutes of one dev's time. If 500 tasks/month don't save you more than that, cancel." _(Low)_: "Happy to hear that. What's the Enterprise configuration you'd want to see?" |
| 6 | "We can't send code to a third party." | "You don't. Runs are local. State is local SQLite. Enterprise tier adds self-hosted LLM (Ollama, vLLM, bedrock) — no outbound traffic required." |
| 7 | "No capacity to try something new right now." | "Understood. The 14-day pilot is designed for exactly this: no procurement, no card, no config review from your team. 30-minute kickoff total." |
| 8 | "We already built something internal." | "Show me the audit trail. If you already have run-level evidence + ROI + PR preview, you're ahead of us. If two of those three are missing, we're probably worth 20 minutes." |
| 9 | "What happens if the LLM goes down or rate-limits?" | "Hybrid mode auto-falls back to deterministic rule-based personas. Every run logs which mode was used. You keep shipping." |
| 10 | "How do I know the ROI numbers are real?" | "They're computed from the SQLite audit table on your machine. The only soft input is `minutes_per_task_manual` — which you set. No telemetry, no estimated numbers from us." |
