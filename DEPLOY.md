# Omni-Agent — Last Mile to First Dollar

Everything below the line was code-ready as of six stacked PRs
(`feat/backend-billing-and-health` → `feat/frontend-stripe-checkout` →
`feat/deploy-config` → `feat/github-app-core` →
`feat/frontend-marketplace-cta` → `feat/marketplace-deploy-config`).
Nothing was merged, deployed, or wired to real money/GitHub by that work —
those are the taps below, in order.

**Primary target: a paid GitHub App listed on the GitHub Marketplace**
(product direction). Marketplace requires ~100 installs and a verified
publisher before a paid plan can go live — see `MARKETPLACE.md` for that
full sequence. The Stripe checkout built first stays as the **direct-sale
bridge**: the fastest way to take a real first payment while the app
builds toward Marketplace eligibility. Both paths are live in the code at
once; the landing page shows whichever is configured (see
`frontend/src/lib/github.js`).

## 1. Merge the stack

In order (each is based on the previous one):
1. Backend billing + health routes
2. Frontend checkout buttons
3. Deploy config (Render blueprint, Dockerfile)
4. GitHub App core (manifest flow, Marketplace webhook)
5. Frontend Marketplace CTA
6. This: updated deploy config + `MARKETPLACE.md`

## 2. Deploy (Render, via the included blueprint)

1. Render dashboard → New → Blueprint → point at this repo → reads
   `render.yaml` → two services: `omni-agent-api`, `omni-agent-web`.
2. Fill in the `sync: false` env vars it prompts for (nothing here is a
   live credential yet — they're all blank until you do this):
   - `omni-agent-api`: `CORS_ORIGINS`, `APP_BASE_URL`, `FRONTEND_BASE_URL`
     (fill both in after the first deploy, once you know the URLs, then
     redeploy), `MONGO_URL` (optional), plus the Stripe and GitHub App
     vars below once you have them.
   - `omni-agent-web`: `REACT_APP_BACKEND_URL`.
3. **Apply** — this is the actual go-live deploy tap.
4. `curl https://<api-domain>/api/health` → confirm `200`, everything
   reports `false`/unconfigured except what you've actually set.

## 3. Get a first dollar via Stripe (the bridge, works today)

1. Stripe → create Pro ($49/mo) and Team ($299/mo) products, test mode
   first. Copy Price IDs, secret key, webhook signing secret.
2. Set `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_PRO`,
   `STRIPE_PRICE_TEAM` on `omni-agent-api`, redeploy.
3. Click "Start Pro" on the live site, complete a **test-mode** checkout
   with Stripe's `4242 4242 4242 4242` card, confirm the webhook records
   it (`backend/data/customers.jsonl` or `db.billing_events`).
4. Swap to live keys when ready for a real charge.

## 4. Stand up the GitHub App

1. Visit `https://<api-domain>/api/github/app/new`, review the manifest,
   confirm on GitHub — this creates the real App.
2. Copy the one-time-shown credentials into `GITHUB_APP_ID`,
   `GITHUB_APP_PRIVATE_KEY`, `GITHUB_WEBHOOK_SECRET`, `GITHUB_CLIENT_ID`,
   `GITHUB_CLIENT_SECRET`, redeploy.
3. Set `REACT_APP_GITHUB_APP_INSTALL_URL` on `omni-agent-web` to
   `https://github.com/apps/<slug>` — works immediately, before any
   Marketplace listing exists.
4. Install it on a test repo yourself, confirm
   `backend/data/github_installations.jsonl` records it.

## 5. List on GitHub Marketplace

Full sequenced checklist — publisher verification, 100-install
threshold, listing content, pricing plans, GitHub's review — in
**`MARKETPLACE.md`**. Once the listing is live, set
`REACT_APP_GITHUB_MARKETPLACE_URL` and the site's CTAs switch to it
automatically.

## 6. DNS (optional, your call)

Point a real domain at the Render services via Render's custom domain
settings. Not required to take a first payment — the `*.onrender.com`
URLs work for both Stripe checkout and the GitHub App's URLs.

## 7. First customer

The GTM assets already exist and don't need engineering work:
- `omni_agent/sales/outreach_kit.md` — outreach copy
- `omni_agent/sales/demo_script.md` — demo script
- `omni_agent/sales/pilot_program.md` — 14-day pilot structure + close
- `omni_agent/sales/offer_sheet.md` — one-pager

Send the first outreach once steps 1–3 are done — Stripe direct-sale
doesn't wait on the Marketplace listing.
