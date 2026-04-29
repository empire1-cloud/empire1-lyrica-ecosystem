# Omni-Agent — Sales Packaging Kit

Launch-ready assets for founder-led selling. All content in this directory is tied to measurable outputs of the Omni-Agent tool (cohesion score, tasks completed, ROI Tracker numbers). No fake testimonials, no fabricated logos, no invented case studies.

## Contents

| File | Purpose | Length |
|---|---|---|
| [`pricing.md`](./pricing.md) | 4-tier pricing table with feature gates, usage limits, ICP, and upgrade triggers. | 92 lines |
| [`landing_page.md`](./landing_page.md) | Long-form landing page copy — hero, problem, solution, how-it-works, ROI proof, plan comparison, FAQ, CTA. | 153 lines |
| [`offer_sheet.md`](./offer_sheet.md) | One-page PDF-ready offer sheet — who/what/timeline/pricing/metrics/guarantee. | 81 lines |
| [`outreach_kit.md`](./outreach_kit.md) | 3 cold DMs, 3 cold emails, 3-touch follow-up, 20-min discovery script, 10 objections. | 138 lines |
| [`demo_script.md`](./demo_script.md) | 5-minute timed demo walkthrough. | 106 lines |
| [`pilot_program.md`](./pilot_program.md) | 14-day pilot: scope, success metrics, onboarding, cadence, conversion. | 114 lines |

---

## Ship the kit in 48 hours — checklist

### Hour 0–4 · Read + adapt (solo, 4 hours)

- [ ] Read `pricing.md` end-to-end. Adjust tier prices to match your market.
- [ ] Read `landing_page.md`. Replace the one ROI example table with **your own** numbers from a real `status --json | jq .roi` run on your repo.
- [ ] Read `offer_sheet.md`. Swap the contact email to yours.
- [ ] Read `outreach_kit.md`. Write 10 target accounts into a sheet; tag each one `{founder | agency | cto}`.
- [ ] Read `demo_script.md`. Run the 5-minute demo on yourself, timed. Fix any step that breaks on your machine.
- [ ] Read `pilot_program.md`. Confirm you can personally handle the day-1 kickoff + day-7 and day-14 syncs in the coming 14 days.

### Hour 4–8 · Set up the landing page + offer (4 hours)

- [ ] Paste `landing_page.md` into your marketing CMS (Framer / Webflow / plain HTML). Headline only, no custom design needed for v1.
- [ ] Add two CTAs: `Start free — one command` → anchor to an install snippet; `Book a 20-min demo` → Calendly or equivalent.
- [ ] Export `offer_sheet.md` to PDF (pandoc or `md-to-pdf`). Upload as `/offer-sheet.pdf` on your site.
- [ ] Create a 20-minute Calendly/Cal.com slot. Limit to 3 per day to protect focus.
- [ ] Connect Stripe Payment Links for the Pro ($49) and Team ($299) plans. Even a v1 checkout link will do.

### Hour 8–16 · First 10 conversations (rest of day 1 + morning day 2)

- [ ] Pick 10 accounts from your sheet. For each, fill the `{first_name}`, `{company}`, and `{sender}` placeholders in one of the three cold-email templates.
- [ ] Send 10 cold emails. Tag each as **sent** with date in your sheet.
- [ ] Pick 5 of those accounts where the person is also active on Twitter/X or LinkedIn. Send the matching DM variant. (Don't double-send on the same day to the same inbox.)
- [ ] Open Calendly availability for the next 5 business days.

### Hour 16–24 · Record the asynchronous demo (day 2 morning, 4 hours)

- [ ] Seed a **fresh** demo repo with 3 tasks in `memory/tasks/inbox.md`.
- [ ] Record a 4–5 minute screencap running the `demo_script.md` verbatim (Loom, OBS, QuickTime).
- [ ] Show, in order: `scan` → `run-next` → open the generated client report → `status` with ROI → `pr-preview TASK-001`.
- [ ] Upload to Loom or a public bucket. Drop the link into the follow-up template (Touch 3) so you have "evidence drop" ready.
- [ ] Save a transcript next to the video for accessibility + future content repurposing.

### Hour 24–40 · Prospect on LinkedIn + engage replies (rest of day 2)

- [ ] Connect to 25 new prospects on LinkedIn with the short DM-1 / DM-2 / DM-3 variants as appropriate.
- [ ] Reply to every inbound within 2 hours during working hours. Use the discovery call script as your frame.
- [ ] For every "not now": log the date, tag the reason, and schedule Touch 4 (break-up email) for day +14.

### Hour 40–48 · Close the first pilot (last 8 hours)

- [ ] For any prospect who booked a call: send the `offer_sheet.md` PDF 24h before the call. Do not send after — makes the call ceremonial.
- [ ] Run the 20-min discovery call per `outreach_kit.md` script. Stay under 20 minutes even if they want more.
- [ ] If qualified: pitch the `pilot_program.md` 14-day plan. No card. No procurement. Commit only to a 30-minute kickoff call next week.
- [ ] Send the kickoff calendar invite **before ending the call**. Include the onboarding checklist from `pilot_program.md`.

### Guardrails on what NOT to do in these 48 hours

- Do not write case studies or social proof. You have none yet.
- Do not paste AI-generated "customer quotes" anywhere on the site.
- Do not overpromise integrations that aren't shipping (Slack / Linear / Jira are Team+ roadmap items — don't imply they exist today).
- Do not discount below list price to close the first pilot. The pilot already has a $0 entry point — that's the offer.
- Do not skip the demo recording. Nothing moves faster than "here's a 4-minute video of the thing running on my repo right now."

---

## Maintenance

- Refresh the ROI example in `landing_page.md` every 30 days from your own `status --json`.
- Re-read `outreach_kit.md` objection sheet monthly — add any new objection you hit more than twice.
- Keep the `pricing.md` page in sync with `landing_page.md`. They must match exactly.

---

## Guardrails on sales claims

Every number in these assets is either:
- A product fact (e.g., "cohesion threshold 85", "Analyst → Developer → Evaluator"), or
- A configurable assumption the customer sets themselves (e.g., `minutes_per_task_manual`, `dev_hourly_rate`), or
- An output the customer will see on their own machine after running the tool.

If a prospect asks "where did that number come from?" the answer is always: _"From your own SQLite audit DB after your own run. We compute nothing on our servers."_
