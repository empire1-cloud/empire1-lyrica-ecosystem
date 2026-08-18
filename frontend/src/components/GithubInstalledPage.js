import { Link } from "react-router-dom";

const email = "manda@empire1.cloud";

// Target of the GitHub App manifest's `setup_url` — where GitHub sends
// the browser right after someone installs the App.
export default function GithubInstalledPage() {
  return (
    <main>
      <nav>
        <Link className="brand" to="/">
          OMNI<span>AGENT</span>
        </Link>
      </nav>
      <section className="hero" id="top">
        <p className="eyebrow">APP INSTALLED</p>
        <h1>
          You're connected.
          <br />
          <em>Here's what happens next.</em>
        </h1>
        <p className="lead">
          Omni-Agent's GitHub App now knows about your account. The task
          engine itself still runs from your machine against your repo —
          install the CLI and point it at the same repo to start closing
          your backlog.
        </p>
        <div className="actions">
          <a
            className="primary"
            href={`mailto:${email}?subject=${encodeURIComponent(
              "Omni-Agent — just installed the GitHub App"
            )}`}
          >
            Email us to finish setup
          </a>
          <Link className="secondary" to="/#pricing">
            See pricing
          </Link>
        </div>
      </section>
    </main>
  );
}
