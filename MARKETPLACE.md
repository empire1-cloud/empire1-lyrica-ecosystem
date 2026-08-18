# Omni-Agent — GitHub Marketplace Path

The real, sequenced path from "code is ready" to "listed, paid GitHub App
on the Marketplace" — with what's already built vs. what's a GitHub-side
process step only Manda can do. Sources: GitHub's own docs on
[requirements for listing an app](https://docs.github.com/en/apps/github-marketplace/creating-apps-for-github-marketplace/requirements-for-listing-an-app),
[publisher verification](https://docs.github.com/en/apps/github-marketplace/github-marketplace-overview/applying-for-publisher-verification-for-your-organization),
[Marketplace webhook events](https://docs.github.com/en/apps/github-marketplace/using-the-github-marketplace-api-in-your-app/webhook-events-for-the-github-marketplace-api),
and [pricing plans for Marketplace apps](https://docs.github.com/en/apps/github-marketplace/selling-your-app-on-github-marketplace/pricing-plans-for-github-marketplace-apps).

## The one fact that shapes the whole sequence

**GitHub requires ~100 installations before a paid plan can go live**, and
a paid listing requires the owning org to be a **verified publisher**
(2FA + verified domain + contact info). So "first dollar via Marketplace"
is not the fastest path from zero — it's the target end-state. The
sequencing below builds toward it while a direct-sale channel (the Stripe
work from the earlier branches) covers the gap.

## Step-by-step

### 1. Create the GitHub App — code ready, action is Manda's

- [x] App Manifest defined in code (`backend/app/core/github_app.py`) —
      minimal permissions (`metadata: read`), subscribed to
      `installation`, `installation_repositories`, `marketplace_purchase`.
- [x] `GET /api/github/app/new` serves the manifest form.
- [x] `GET /api/github/manifest-callback` exchanges GitHub's code for
      real credentials and shows them once.
- [ ] **Your tap**: deploy PR #5+ first, set `APP_BASE_URL` /
      `FRONTEND_BASE_URL`, visit `/api/github/app/new`, confirm on GitHub,
      copy the shown credentials into env vars.
- [ ] **Your tap**: set `REACT_APP_GITHUB_APP_INSTALL_URL` to
      `https://github.com/apps/<slug>` once created — this link works
      immediately (App is public), no Marketplace listing needed yet.

### 2. Handle Marketplace billing events — code ready

- [x] `POST /api/github/webhook` verifies signatures and handles every
      `marketplace_purchase` action: `purchased`, `changed`, `cancelled`,
      `pending_change`, `pending_change_cancelled`.
- [x] Each event is recorded to an audit trail with a derived
      active/cancelled status per account (`backend/app/services/github_events_store.py`).
- [x] Unknown/unsubscribed event types are acknowledged (200), never
      error — required so GitHub doesn't disable the webhook.
- [ ] **Your tap**: once the App is created, add its webhook URL
      (`{APP_BASE_URL}/api/github/webhook`) and secret in the App's
      Marketplace settings if GitHub doesn't already reuse the App's main
      webhook config for Marketplace events (confirm in the App's
      Marketplace tab when you get there — the docs describe both a
      per-App webhook and, for older listing types, a separate one).

### 3. Build toward 100 installs

- [ ] Share `https://github.com/apps/<slug>` — every real install counts,
      whether or not anyone's paying yet. The Stripe/direct-sale path from
      the earlier PRs is how those early users actually pay you before
      Marketplace's paid-plan gate opens.
- [ ] Track installs via the audit trail this branch writes
      (`backend/data/github_installations.jsonl`, or `db.github_installations`
      if Mongo is configured).

### 4. Publisher verification (required for a paid listing)

- [ ] **Your tap, GitHub-side, not code**: apply for publisher
      verification for the owning org — needs 2FA enabled on the org,
      a verified domain, and valid contact info. This has its own review
      timeline; start it in parallel with building installs, not after.

### 5. Submit the listing

- [ ] **Your tap, GitHub-side, not code**: from the App's settings →
      "List in Marketplace" → fill in: description, logo/feature
      card/screenshots, category, support URL/email, privacy policy URL,
      terms of service URL, and pricing plans (configured in GitHub's UI,
      not code — up to 10 plans, each needs both a monthly *and* annual
      price; per-unit or flat-rate).
- [ ] Suggested plan mapping from `omni_agent/sales/pricing.md`: **Free**
      (rule-mode, $0), **Pro** ($49/seat/mo, per-unit), **Team**
      ($299/mo flat + seats). Enterprise stays off-Marketplace (direct
      sales contract), matching how it's already handled on the site.
- [ ] Accept the GitHub Marketplace Developer Agreement.
- [ ] GitHub reviews the listing (content + a technical check that your
      webhook actually responds correctly to a test purchase) before it
      goes live. Budget real calendar time for this — it's a manual
      review, not instant.

### 6. Go live

- [ ] **Your tap**: set `REACT_APP_GITHUB_MARKETPLACE_URL` — the site's
      primary CTA and all self-serve plan cards switch to it automatically
      (see `frontend/src/lib/github.js`), no further code change needed.
- [ ] Test the full purchase flow yourself once live (GitHub doesn't have
      a Marketplace "test mode" the way Stripe does — the first real
      transaction is real, so do it on a throwaway/personal account
      first if possible).

## What's explicitly NOT in v1 (by design, not an oversight)

- The App only requests `metadata: read` — it does not open PRs, read
  repo contents, or post checks. The task-execution engine stays the
  local CLI, matching the existing "runs on your machine, we never see
  your code" pitch. Expanding permissions to let the App act on repos
  directly is a deliberate Phase 2, once there's a paying Marketplace
  customer asking for it.
- No dashboard reads `db.marketplace_accounts` back out yet to gate CLI
  features by plan — the audit trail exists and is queryable, but wiring
  "this account's plan = X, so unlock Y in the CLI" is Phase 2 as well.
