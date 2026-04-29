# Omni-Agent — 5-Minute Demo Script

> Memorize timing. Run on a **pre-seeded repo** with 3 tasks in `memory/tasks/inbox.md`, one of which is intentionally under-specified (to showcase `blocked_context`).
>
> Goal: show all three monetized features + the guardrail story. Close with the 14-day pilot offer.

---

## 0:00–0:30 — Setup & frame (30s)

> "I'm going to show Omni-Agent end-to-end in five minutes. You'll see three things: how it closes a task, what the client report looks like, and how it hands you a PR. Nothing I run touches anything outside allowed paths. Watch the left pane."

_(Screen: terminal at repo root, `inbox.md` visible in a split.)_

---

## 0:30–2:00 — Scan + run a real task (90s)

```bash
$ python scripts/omni_agent.py scan
Scanned tasks. parsed=3 new=3 existing=0
```

> "It just parsed three tasks from `memory/tasks/inbox.md` — an unchecked box, a `TODO:`, and a `FIXME:`. Now I'll run the first one."

```bash
$ python scripts/omni_agent.py run-next
```

_(Show the terminal output live. Highlight these lines on screen.)_

> Read out loud:
> - "Analyst wrote a mini-spec — scope, assumptions, acceptance criteria, impacted files."
> - "Developer applied a minimal patch to `backend/app/services/health_service.py`. Only allowed paths."
> - "Evaluator ran tests, checked every criterion, computed a cohesion score of **91 out of 100**. Threshold is 85, so it's marked done."
> - _(Open inbox.md)_ "And the checkbox flipped — `- [x]`, with the timestamp and task ID. That's the markdown write-back."

---

## 2:00–3:00 — Client report (60s)

```bash
$ cat omni_agent/reports/client/2026-04-29_default_TASK-001.md | head -60
```

> "This is generated automatically after every run. Executive summary, tasks completed with cohesion scores, evidence — files changed, criteria results, tests, artifacts — then blockers, risks, a 7-day plan, and a time-saved estimate."
>
> "The same report also ships as JSON for PDF generation or piping into your own reporting stack."

_(Scroll once. Don't read the whole thing.)_

---

## 3:00–3:45 — ROI summary (45s)

```bash
$ python scripts/omni_agent.py status --json | jq .roi
```

> "Here's the live ROI. Tasks completed, average cohesion, blocked rate, hours saved, cost saved. Configurable assumptions — I've got 60 minutes per manual task at $100/hour. Those are editable in `config.yaml`. Every number reads directly from the SQLite audit table on this machine. Nothing leaves the laptop."

_(Point at the `estimated_cost_saved` line.)_

---

## 3:45–4:45 — PR preview (60s)

```bash
$ python scripts/omni_agent.py pr-preview TASK-001
Wrote: omni_agent/reports/pr/TASK-001.md
```

```bash
$ cat omni_agent/reports/pr/TASK-001.md
```

> "That's the PR body. Title, summary, files changed, test evidence, acceptance criteria with checkmarks, risk notes, and rollback instructions. Paste into GitHub. Done."
>
> "And — critical — watch this:"

```bash
$ python scripts/omni_agent.py pr-preview TASK-594f6b3c
Error: task TASK-594f6b3c status is 'blocked_context'; PR preview refused.
```

> "PR preview refuses to generate for a task that didn't pass evaluation. You can't ship evidence that doesn't exist."

---

## 4:45–5:00 — Close with offer (15s)

> "That's the loop. Three products, one CLI, local state, strict guardrails.
>
> Next step: 14-day pilot on one of your repos. No card, no procurement, no obligation. If at day 14 the ROI report doesn't show real savings, you keep the data and we part ways.
>
> I'll send the kickoff doc tonight. What's the best repo to point it at?"

---

## Demo failure recovery (if anything breaks)

| Failure | Action |
|---|---|
| LLM rate-limits mid-demo | Say: "This is why hybrid mode exists." Re-run — the rule-based fallback kicks in. Point out the `mode_used: rule` line in the output. |
| Test step fails unexpectedly | Don't panic. Say: "This is the Evaluator working — it's about to drop the cohesion score below 85." Show the `evaluating_failed` status. It's still a feature demo. |
| Terminal resets / tmux issue | Switch to the pre-recorded 2-minute clip (kept in `sales/demo_video.mp4`). |
