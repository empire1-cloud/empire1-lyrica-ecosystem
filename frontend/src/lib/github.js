// GitHub App / Marketplace link helpers. Both are env-driven so this
// works correctly at every stage of the rollout without a code change:
//
//   1. Before the App exists              -> both empty, CTA falls back to mailto
//   2. App created, not Marketplace-listed -> only INSTALL_URL set
//      (https://github.com/apps/<slug> works the moment the App is public —
//      this is how you build toward the 100-install Marketplace threshold)
//   3. Marketplace listing live            -> MARKETPLACE_URL set too,
//      becomes the primary CTA (GitHub's own page handles plan selection)
const INSTALL_URL = process.env.REACT_APP_GITHUB_APP_INSTALL_URL || "";
const MARKETPLACE_URL = process.env.REACT_APP_GITHUB_MARKETPLACE_URL || "";

export function getPrimaryInstallUrl() {
  return MARKETPLACE_URL || INSTALL_URL || null;
}

export function getInstallUrl() {
  return INSTALL_URL || null;
}

export function getMarketplaceUrl() {
  return MARKETPLACE_URL || null;
}

export function isMarketplaceLive() {
  return Boolean(MARKETPLACE_URL);
}
