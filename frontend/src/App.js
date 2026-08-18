import { useState } from "react";
import { Route, Routes } from "react-router-dom";
import "./App.css";
import { startCheckout } from "@/lib/billing";
import { getMarketplaceUrl, getPrimaryInstallUrl, isMarketplaceLive } from "@/lib/github";
import SuccessPage from "@/components/SuccessPage";
import CancelPage from "@/components/CancelPage";
import GithubInstalledPage from "@/components/GithubInstalledPage";

const plans = [
  { name: "Free", price: "$0", note: "25 tasks each month", features: ["Rule-mode agent loop", "One workspace", "30-day history"], cta: "Start free" },
  { name: "Pro", price: "$49", suffix: "/seat/month", note: "For founders and technical leads", features: ["500 tasks each month", "AI + rule fallback", "Reports, ROI and PR previews"], cta: "Start Pro", featured: true, planKey: "pro" },
  { name: "Team", price: "$299", suffix: "/workspace/month", note: "10 seats included", features: ["5,000 tasks each month", "GitHub, Slack and Linear hooks", "Audit export and priority support"], cta: "Get Team", planKey: "team" },
  { name: "Enterprise", price: "From $2,000", suffix: "/month", note: "For controlled or private environments", features: ["Self-hosted deployment", "SSO and company rules", "Dedicated onboarding"], cta: "Talk to Manda" },
];

const email = "manda@empire1.cloud";

// Plan selection + billing for Free/Pro/Team happens on GitHub's own
// Marketplace listing page once it's live (GitHub hosts that UI, not us —
// see omni_agent/sales/pricing.md and DEPLOY.md for why). Until then, the
// Stripe checkout built earlier stays as a direct-sale fallback: Marketplace
// requires 100 installs before a paid plan can even go live, so early
// customers need a way to pay before that threshold is hit. Enterprise
// stays sales-assisted (mailto) either way — that's not a Marketplace deal.
function PlanCard({ plan }) {
  const [status, setStatus] = useState("idle"); // idle | loading | error
  const [error, setError] = useState(null);
  const marketplaceUrl = getMarketplaceUrl();

  if (!plan.planKey) {
    return (
      <article className={plan.featured ? "featured" : ""}>
        {plan.featured && <small>BEST START</small>}
        <h3>{plan.name}</h3>
        <div className="price">{plan.price}<span>{plan.suffix}</span></div>
        <p>{plan.note}</p>
        <ul>{plan.features.map((f) => <li key={f}>{f}</li>)}</ul>
        <a href={`mailto:${email}?subject=${encodeURIComponent(`Omni-Agent ${plan.name}`)}`}>{plan.cta}</a>
      </article>
    );
  }

  const handleBuy = async () => {
    setStatus("loading");
    setError(null);
    try {
      const { checkoutUrl } = await startCheckout(plan.planKey);
      window.location.href = checkoutUrl;
    } catch (err) {
      setStatus("error");
      setError(err.message);
    }
  };

  return (
    <article className={plan.featured ? "featured" : ""}>
      {plan.featured && <small>BEST START</small>}
      <h3>{plan.name}</h3>
      <div className="price">{plan.price}<span>{plan.suffix}</span></div>
      <p>{plan.note}</p>
      <ul>{plan.features.map((f) => <li key={f}>{f}</li>)}</ul>
      {marketplaceUrl ? (
        <a href={marketplaceUrl} target="_blank" rel="noreferrer">
          View on GitHub Marketplace
        </a>
      ) : (
        <button type="button" onClick={handleBuy} disabled={status === "loading"}>
          {status === "loading" ? "Redirecting…" : plan.cta}
        </button>
      )}
      {status === "error" && <p className="checkoutError">{error}</p>}
      {!marketplaceUrl && (
        <p className="planNote">Also coming to GitHub Marketplace.</p>
      )}
    </article>
  );
}

function Home() {
  const primaryInstallUrl = getPrimaryInstallUrl();
  const marketplaceLive = isMarketplaceLive();

  return (
    <main>
      <nav><a className="brand" href="#top">OMNI<span>AGENT</span></a><div><a href="#product">Product</a><a href="#pricing">Pricing</a><a className="navCta" href={`mailto:${email}?subject=Omni-Agent demo`}>Book demo</a></div></nav>
      <section className="hero" id="top">
        <p className="eyebrow">
          {marketplaceLive ? "ON GITHUB MARKETPLACE" : "AI EXECUTION FOR REAL REPOSITORIES"}
        </p>
        <h1>Close your <code>TODO.md</code>.<br/><em>With receipts.</em></h1>
        <p className="lead">Omni-Agent turns unfinished repository tasks into reviewed work, then shows what changed, what passed, what was blocked and what the work saved.</p>
        <div className="actions">
          {primaryInstallUrl ? (
            <a className="primary" href={primaryInstallUrl} target="_blank" rel="noreferrer">
              {marketplaceLive ? "Install via GitHub Marketplace" : "Install the GitHub App"}
            </a>
          ) : (
            <a className="primary" href={`mailto:${email}?subject=Start Omni-Agent free`}>Start free</a>
          )}
          <a className="secondary" href={`mailto:${email}?subject=Omni-Agent 20-minute demo`}>Book a 20-minute demo</a>
        </div>
        <p className="trust">Runs on your machine · Protects forbidden paths · Nothing passes without evaluation</p>
      </section>

      <section className="product" id="product">
        <p className="eyebrow">ONE LOOP. THREE PAID OUTCOMES.</p>
        <div className="cards">
          <article><b>01</b><h2>Work reports</h2><p>Every run produces a plain report showing completed tasks, evidence, blockers, risks and next steps.</p></article>
          <article><b>02</b><h2>Time and money proof</h2><p>Track tasks finished, tests passed, hours saved and cost saved from the local history.</p></article>
          <article><b>03</b><h2>Pull-request previews</h2><p>Generate a ready-to-review change summary only after the task passes the required score.</p></article>
        </div>
      </section>

      <section className="pricing" id="pricing">
        <p className="eyebrow">PRICING</p><h2>Start small. Pay when it saves work.</h2>
        <div className="plans">{plans.map((plan) => <PlanCard plan={plan} key={plan.name} />)}</div>
        <p className="fine">Annual plans include two months free. Team white-label reports are available for $149/month. Monthly plans can be canceled at the end of the current billing period.</p>
      </section>

      <section className="pilot"><div><p className="eyebrow">14-DAY PILOT</p><h2>Give it one stale backlog.</h2><p>If Omni-Agent cannot close real tasks and produce measurable proof on your repository, you pay nothing and keep the reports.</p></div><a className="primary" href={`mailto:${email}?subject=Omni-Agent 14-day pilot`}>Start the pilot</a></section>
      <footer><div className="brand">OMNI<span>AGENT</span></div><p>Built by Empire-1 · Evidence before claims.</p><a href={`mailto:${email}`}>{email}</a></footer>
    </main>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/success" element={<SuccessPage />} />
      <Route path="/cancel" element={<CancelPage />} />
      <Route path="/github/installed" element={<GithubInstalledPage />} />
    </Routes>
  );
}

export default App;
