import { BrandLogo } from "./brand-logo";

type HeaderLink = {
  label: string;
  href: string;
};

type SiteHeaderProps = {
  siteLabel?: string;
  sectionLabel?: string;
  sectionKey?: string;
  links: HeaderLink[];
  logoHref?: string;
};

export function SiteHeader({
  siteLabel,
  sectionLabel,
  sectionKey,
  links,
  logoHref
}: SiteHeaderProps) {
  const activeKey = sectionKey ?? sectionLabel?.toLowerCase();
  const showMeta = Boolean(siteLabel && activeKey);

  return (
    <header className="site-header">
      <div className="site-header__inner">
        <div className="site-header__brand">
          <BrandLogo href={logoHref} />
          {showMeta ? (
            <div className="site-header__meta">
              <span className="site-header__eyebrow">{siteLabel}</span>
              <span className="site-header__title" aria-label={`latesight > ${activeKey}`}>
                <span className="site-header__title-root">latesight</span>
                <span className="site-header__title-separator">&gt;</span>
                <span className="site-header__title-current">{activeKey}</span>
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
