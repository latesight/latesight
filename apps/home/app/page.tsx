import { PageShell } from "@latesight/ui/page-shell";

export default function HomePage() {
  return (
    <PageShell>
      <section className="page-section" id="sites">
        <div className="hero-panel">
          <a className="home-site-link" href="https://dict.latesight.com">
            <h2 className="home-site-title">
              <span className="home-site-title__dot" aria-hidden="true" />
              <span>Word Lens</span>
            </h2>
            <span className="home-site-domain">dict.latesight.com</span>
          </a>
        </div>
      </section>
    </PageShell>
  );
}
