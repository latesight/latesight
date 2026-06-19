import { PageShell } from "@latesight/ui/page-shell";
import { DictionarySearch } from "./dictionary-search";

export default function DictHomePage() {
  return (
    <PageShell>
      <section className="page-section hero-grid hero-grid--single" id="lookup">
        <DictionarySearch />
      </section>
    </PageShell>
  );
}
