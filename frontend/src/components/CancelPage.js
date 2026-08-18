import { Link } from "react-router-dom";

const email = "manda@empire1.cloud";

export default function CancelPage() {
  return (
    <main>
      <nav>
        <Link className="brand" to="/">
          OMNI<span>AGENT</span>
        </Link>
      </nav>
      <section className="hero" id="top">
        <p className="eyebrow">CHECKOUT CANCELED</p>
        <h1>
          No charge made.
          <br />
          <em>Questions first?</em>
        </h1>
        <p className="lead">
          Your checkout was canceled and nothing was charged. If something
          didn't look right, or you'd rather talk it through first, we're
          one email away.
        </p>
        <div className="actions">
          <Link className="primary" to="/#pricing">
            Back to pricing
          </Link>
          <a
            className="secondary"
            href={`mailto:${email}?subject=Omni-Agent checkout question`}
          >
            Email us
          </a>
        </div>
      </section>
    </main>
  );
}
