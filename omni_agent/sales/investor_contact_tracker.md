# Investor Contact Tracker

Capture every DM, every reply, every next step. Update within 15 minutes of any action.

Owner column: who on the founding team is on the hook for the next action.

## Columns (CSV-ready)

`fund | partner_name | channel | profile_url | intro_status | reply_status | next_step | owner | notes`

- **channel** = `linkedin_dm` | `x_dm` | `warm_intro` | `email` (once captured)
- **intro_status** = `draft` | `sent_day0` | `sent_day1` | `bumped_day3` | `closed_day7` | `replied` | `meeting_booked` | `passed` | `dead`
- **reply_status** = `none` | `read_no_reply` | `holding_pattern` | `route_to_other_partner` | `send_deck` | `send_email` | `book_call` | `pass`
- **next_step** = one short sentence, verb-first. Example: `send 1-pager to partner@fund.com`
- **notes** = anything ops/legal relevant. Never put sensitive personal info here.

## Initial rows — one per target (fill as you send)

| fund | partner_name | channel | profile_url | intro_status | reply_status | next_step | owner | notes |
|---|---|---|---|---|---|---|---|---|
| Greylock | {partner_name} | linkedin_dm | {url} | draft | none | send day0 | Manda |  |
| Andreessen Horowitz | {partner_name} | linkedin_dm | {url} | draft | none | send day0 | Manda |  |
| Sequoia | {partner_name} | linkedin_dm | {url} | draft | none | send day0 | Manda |  |
| Lightspeed | {partner_name} | linkedin_dm | {url} | draft | none | send day0 | Manda |  |
| Redpoint | {partner_name} | linkedin_dm | {url} | draft | none | send day0 | Manda |  |
| Khosla | {partner_name} | linkedin_dm | {url} | draft | none | send day0 | Manda |  |
| Index | {partner_name} | linkedin_dm | {url} | draft | none | send day0 | Manda |  |
| First Round | {partner_name} | linkedin_dm | {url} | draft | none | send day0 | Manda |  |
| Bessemer | {partner_name} | linkedin_dm | {url} | draft | none | send day1 | Manda |  |
| Y Combinator | {partner_name} | linkedin_dm | {url} | draft | none | send day1 | Manda | parallel accelerator track |
| Insight Partners | {partner_name} | linkedin_dm | {url} | draft | none | send day1 | Manda |  |
| Founders Fund | {partner_name} | linkedin_dm | {url} | draft | none | send day1 | Manda |  |
| Lerer Hippeau | {partner_name} | linkedin_dm | {url} | draft | none | send day1 | Manda |  |
| Techstars Music | {partner_name} | linkedin_dm | {url} | draft | none | send day1 | Manda | accelerator, not direct check |
| TechCrunch Disrupt | {partner_name} | linkedin_dm | {url} | draft | none | submit app day1 | Manda | visibility, not investor |

## Daily update ritual (5 min)

1. For every row where `intro_status = sent_day0` and the clock is past 72h → change to `bumped_day3` and send the Day +3 template.
2. For every row where `intro_status = bumped_day3` and the clock is past 96h → change to `closed_day7` and send the Day +7 template.
3. For every `reply_status = send_deck` → advance `next_step` to `send 1-pager + 2-min walkthrough within 24h`.
4. For every `reply_status = send_email` → use `investor_handoff_email_template.md`, send within 2 hours of reply.
5. For every `reply_status = pass` → set `intro_status = passed`, move on; re-surface only on next funding round.

## Export

Keep this file as the canonical source. A CSV export is trivial: copy the table, paste into any spreadsheet; the column names are pre-set.
