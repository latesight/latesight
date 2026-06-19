import { PageShell } from "@latesight/ui/page-shell";

export default function HomePage() {
  return (
    <PageShell>
      <section className="page-section hero-grid hero-grid--single" id="index">
        <div className="hero-copy">
          <h1>Latesight</h1>
          <p>一个保持极简的工具入口页。当前只提供词典站。</p>
        </div>
      </section>

      <section className="page-section" id="sites">
        <div className="hero-panel">
          <p className="section-eyebrow">Site</p>
          <h2>Word Lens</h2>
          <p className="panel-copy">英语单词查询、释义、发音和例句。</p>
          <a className="text-link" href="https://dict.latesight.com">
            dict.latesight.com
          </a>
        </div>
      </section>
    </PageShell>
  );
}
