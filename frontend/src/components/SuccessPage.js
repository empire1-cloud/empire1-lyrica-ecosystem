import { Link, useSearchParams } from "react-router-dom";

const email = "manda@empire1.cloud";

export default function SuccessPage() {
  const [params] = useSearchParams();
  const sessionId = params.get("session_id");

  return (
    <main>
      <nav>
        <Link className="brand" to="/">
          OMNI<span>AGENT</span>
        </Link>
      </nav>
      <section className="hero" id="top">
        <p className="eyebrow">YOU'RE IN</p>
        <h1>
          Payment received.
          <br />
          <em>Let's get you running.</em>
        </h1>
        <p className="lead">
          Thanks — your subscription is active. We'll email install
          instructions and your workspace config within one business day.
          {sessionId ? (
            <>
              {" "}
              Reference: <code>{sessionId}</code>
            </>
          ) : null}
        </p>
        <div className="actions">
          <a
            className="primary"
            href={`mailto:${email}?subject=${encodeURIComponent(
              `Omni-Agent onboarding${sessionId ? ` (${sessionId})` : ""}`
            )}`}
          >
            Email us your repo path
          </a>
          <Link className="secondary" to="/">
            Back to home
          </Link>
        </div>
      </section>
    </main>
  );
}
