# Omni-Agent — 14-Day Pilot Program

_The fastest path from "interested founder" to "paying team" without procurement friction._

---

## SCOPE

- **One repo.** Customer picks.
- **One workspace.** Single `memory/tasks/**/*.md` inbox.
- **Up to 25 tasks** attempted over 14 days.
- **Hybrid persona mode** enabled from day 1 (uses customer's Emergent Universal Key or Anthropic key).
- Full access to: Client Report Generator, ROI Tracker, PR Autopilot preview.
- All three reports delivered weekly (at day 7 and day 14).

## OUT OF SCOPE

- Custom integrations (Linear, Jira, Slack) — available at Team tier after conversion.
- Self-hosted LLM deployment — Enterprise tier.
- White-label branding of reports — Team+ add-on.

---

## SUCCESS CRITERIA

A pilot converts when **four of the five** metrics below are hit at day 14:

| # | Metric | Target |
|---|---|---|
| 1 | Tasks closed with cohesion ≥ 85 | **≥ 10** |
| 2 | Average cohesion across runs | **≥ 85** |
| 3 | Hours saved (by ROI Tracker) | **≥ 8 hrs** |
| 4 | Blocked rate | **≤ 20 %** |
| 5 | Forbidden-path write attempts | **0** |

All five come from the ROI Tracker + state DB. No custom instrumentation. No interpretation.

If fewer than four metrics are hit, the customer walks. We send them the generated reports + audit DB + a "here's what we'd change" writeup. No invoice.

---

## ONBOARDING CHECKLIST (Day 0 — 30 min kickoff call)

- [ ] Customer shares the target repo (read-only GitHub access or local path confirmed).
- [ ] Install CLI (`pip install omni-agent-cli`) — `< 2 min`.
- [ ] Drop `config.yaml` into the repo. Confirm:
  - [ ] `persona_mode: hybrid`
  - [ ] `workspace.name` set to customer's org slug
  - [ ] `roi.minutes_per_task_manual` and `roi.dev_hourly_rate` match their internal numbers
  - [ ] `guardrails.forbidden_paths` includes **every** path the customer names as sensitive (secrets, migrations, infra, specific service dirs, etc.)
- [ ] Seed `memory/tasks/inbox.md` with 10–25 backlog items from the customer's real Linear/Jira/TODO list.
- [ ] Set Emergent Universal Key (or BYO Anthropic key) in `backend/.env`.
- [ ] Run `python scripts/omni_agent.py scan` together. Confirm every seeded task is picked up.
- [ ] Run `python scripts/omni_agent.py run-next --dry-run` together. Walk through Analyst output. Confirm guardrails are satisfactory.
- [ ] Schedule the two weekly sync calls (day 7, day 14).

---

## WEEKLY CADENCE

### Week 1 (Days 1–7)
- **Day 1–2**: First real `run-next`. First client report delivered via email (markdown + JSON).
- **Day 3–4**: Customer runs solo. We watch the SQLite audit trail.
- **Day 5**: Mid-week async check-in (Slack/email): any blocked tasks? Any guardrail false-positives to tune?
- **Day 7**: **Week 1 sync call (30 min)**. Review the weekly ROI number. Adjust `minutes_per_task_manual` if their real data shows something different. Tune guardrails if needed.

### Week 2 (Days 8–14)
- **Day 8–9**: Introduce PR Autopilot. Paste 2–3 previews into real GitHub PRs.
- **Day 10**: Customer runs a full day solo with PR previews.
- **Day 12**: Async check-in. Review blocked-task backlog. Decide which blocked tasks to unblock by adding context.
- **Day 14**: **Closing sync (45 min)**.
  - Review the 5 success metrics.
  - Walk through the cumulative Client Report (day 14 edition).
  - Show total hours/cost saved.
  - Present pricing. Discuss seat count + workspace needs.

---

## CONVERSION TO PAID PLAN

If the pilot hits success criteria, we offer — on the day-14 call — the following conversion path:

| Path | Offer | Commit |
|---|---|---|
| **Pro → self-serve** | First 30 days free. $49/seat/month starting day 45. Cancel anytime. | Stripe subscription |
| **Team** | First month **50 % off** ($149). 10 seats included. Slack/Linear/GitHub webhooks enabled. | Stripe subscription, monthly or annual |
| **Enterprise** | 90-day paid pilot at $1,500 flat. Self-host eval, SSO, custom policies. Converts to annual contract at day 90. | Invoice, net-30 |

If the pilot **does not** hit success criteria:
1. We hand over the full audit DB + all client reports + a written post-mortem (what we'd change to make it work).
2. We offer one free extension of 14 more days (optional) with the fixes applied.
3. No invoice. No retention pressure. They keep the data.

---

## INTERNAL CHECKLIST (founder-side)

- [ ] Pre-call: read the customer's repo tree. Pre-populate a candidate `forbidden_paths` list based on their directory structure.
- [ ] Pre-call: draft 3 candidate pilot tasks from their public GitHub issues (or infer from their TODO commits).
- [ ] Kickoff call: do not exceed 30 minutes. If config tuning takes longer, schedule a followup.
- [ ] Day 1: check the first `run-next` output within 2 hours of the customer running it. Send a one-line follow-up.
- [ ] Day 7 + Day 14: always send the sync-call report within 24 hours of the call, even if the meeting ran long.
- [ ] Never oversell during the pilot. If a metric is lagging, say so on day 5, not day 14.

---

## WHAT WE WON'T DO DURING A PILOT

- Write case studies, testimonials, or pull quotes from a customer mid-pilot.
- Use the pilot customer's name in marketing before day 14 + explicit written permission.
- Push for a contract commitment before the success metrics are visible.
- Recommend disabling guardrails to hit the cohesion threshold faster.

These aren't just ethics — they protect the product. Every honest pilot is the next customer's reference.
