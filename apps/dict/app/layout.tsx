import type { Metadata } from "next";
import "@latesight/ui/brand-system.css";
import { sharedSiteIcons } from "@latesight/ui/site-metadata";
import { SiteFooter } from "@latesight/ui/site-footer";
import { SiteHeader } from "@latesight/ui/site-header";
import "./globals.css";

export const metadata: Metadata = {
  title: "latesight > dict",
  description: "A focused dictionary and word lookup site.",
  icons: sharedSiteIcons
};

const headerLinks = [
  { label: "Lookup", href: "#lookup" },
  { label: "Main Site", href: "https://latesight.com" }
];

const footerLinks = [
  { label: "Latesight", href: "https://latesight.com" },
  { label: "Dictionary", href: "/" },
  { label: "Lookup", href: "#lookup" }
];

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>
        <div className="site-shell">
          <SiteHeader
            links={headerLinks}
            logoHref="https://latesight.com"
          />
          {children}
          <SiteFooter
            summary="Word Lens is the first Latesight tool site, focused on direct and readable word lookup."
            legal="Copyright © 2026 Latesight. All rights reserved."
            links={footerLinks}
          />
        </div>
      </body>
    </html>
  );
}
