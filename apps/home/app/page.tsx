import { PageShell } from "@latesight/ui/page-shell";

export default function HomePage() {
  return (
    <PageShell>
      <section className="page-section" id="sites">
        <div className="hero-panel">
          <h2 className="home-site-title">
            <span className="home-site-title__dot" aria-hidden="true" />
            <span>Word Lens</span>
          </h2>
          <a className="text-link" href="https://dict.latesight.com">
            dict.latesight.com
          </a>
        </div>
      </section>
    </PageShell>
  );
}
