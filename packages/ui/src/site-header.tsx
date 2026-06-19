import { BrandLogo } from "./brand-logo";

type HeaderLink = {
  label: string;
  href: string;
};

type SiteHeaderProps = {
  siteLabel?: string;
  sectionLabel?: string;
  sectionKey?: string;
  titleRoot?: string;
  titleCurrent?: string;
  slogan?: string;
  links: HeaderLink[];
  logoHref?: string;
};

export function SiteHeader({
  siteLabel,
  sectionLabel,
  sectionKey,
  titleRoot,
  titleCurrent,
  slogan,
  links,
  logoHref
}: SiteHeaderProps) {
  const activeKey = sectionKey ?? sectionLabel?.toLowerCase();
  const visibleTitleRoot = titleRoot ?? "latesight";
  const visibleTitleCurrent = titleCurrent ?? sectionLabel ?? activeKey;
  const showMeta = Boolean(visibleTitleCurrent);

  return (
    <header className="site-header">
      <div className="site-header__inner">
        <div className="site-header__brand">
          <BrandLogo href={logoHref} />
          {slogan ? <span className="site-header__slogan">{slogan}</span> : null}
          {showMeta ? (
            <div className="site-header__meta">
              {siteLabel ? <span className="site-header__eyebrow">{siteLabel}</span> : null}
              <span className="site-header__title" aria-label={`${visibleTitleRoot} > ${visibleTitleCurrent}`}>
                <span className="site-header__title-root">{visibleTitleRoot}</span>
                <span className="site-header__title-separator">&gt;</span>
                <span className="site-header__title-current">{visibleTitleCurrent}</span>
              </span>
            </div>
          ) : null}
        </div>

        <nav className="site-nav" aria-label="Primary">
          {links.map((link) => (
            <a key={link.href} className="site-nav__link" href={link.href}>
              {link.label}
            </a>
          ))}
        </nav>
      </div>
    </header>
  );
}
