# Omni-Agent — Last Mile to First Dollar

Everything below the line was code-ready as of the three stacked PRs
(`feat/backend-billing-and-health` → `feat/frontend-stripe-checkout` →
`feat/deploy-config`). Nothing was merged, deployed, or wired to real money
by that work — those are the taps below, in order.

## 1. Merge the stack

Merge in order (each is based on the previous one):
1. Backend billing + health routes
2. Frontend checkout buttons
3. This deploy config

## 2. Stripe — test mode first

1. Create (or use) a Stripe account.
2. Products → add **Pro** ($49/mo recurring) and **Team** ($299/mo
   recurring). Copy each Price ID (`price_...`).
3. Developers → API keys → copy the **test** secret key (`sk_test_...`).
4. Developers → Webhooks → add endpoint
   `https://<your-api-domain>/api/billing/webhook`, subscribe to
   `checkout.session.completed`, copy the signing secret (`whsec_...`).

## 3. Deploy (Render, via the included blueprint)

1. Render dashboard → New → Blueprint → point at this repo → it reads
   `render.yaml` and proposes two services: `omni-agent-api` (Python web
   service) and `omni-agent-web` (static site).
2. Before clicking **Apply** (this is the actual go-live step — do it when
   ready, not before), it'll prompt for the `sync: false` env vars:
   - `omni-agent-api`: `STRIPE_SECRET_KEY` (test key first),
     `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_PRO`, `STRIPE_PRICE_TEAM`,
     `APP_BASE_URL` (fill in after first deploy, then redeploy — it's the
     API's own URL), `CORS_ORIGINS` (the web service's URL),
     `MONGO_URL` (optional — leave blank to launch without Mongo; the
     billing/health/marketing surface doesn't need it).
   - `omni-agent-web`: `REACT_APP_BACKEND_URL` (the API service's URL).
3. Apply. Both services build from the same repo; `buildFilter` means a
   change to only `frontend/**` won't rebuild the API and vice versa.

Not on Render? `backend/Dockerfile` builds the API as a portable
container for Fly/Railway/App Runner/etc. The frontend is a static
`npm run build` output — any static host works.

## 4. Verify it's actually loading

```bash
curl https://<api-domain>/api/health
# {"status":"healthy","module":"health_service","mongo_configured":..,"stripe_configured":true}
```
Open the web URL, confirm the pricing page loads, click "Start Pro" —
should redirect to a real Stripe Checkout page once Stripe is configured
(a clean "checkout isn't turned on yet" message otherwise, never a crash).

## 5. Go live with Stripe

Once a **test-mode** checkout completes successfully end-to-end
(use Stripe's `4242 4242 4242 4242` test card), swap in live keys:
`STRIPE_SECRET_KEY` (`sk_live_...`), recreate the webhook endpoint in live
mode for the new `whsec_...`, and use the live Price IDs.

## 6. DNS (optional, your call)

Point a real domain at the Render static site (and optionally the API) via
Render's custom domain settings. Not required to take a first payment —
the `*.onrender.com` URLs work for that.

## 7. First customer

The GTM assets already exist and don't need engineering work:
- `omni_agent/sales/outreach_kit.md` — outreach copy
- `omni_agent/sales/demo_script.md` — demo script
- `omni_agent/sales/pilot_program.md` — 14-day pilot structure + close
- `omni_agent/sales/offer_sheet.md` — one-pager

Send the first outreach once steps 1–4 are done and you can point a real
prospect at a real URL with a real "Start Pro" button.
