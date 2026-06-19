import type { Metadata } from "next";
import "@latesight/ui/brand-system.css";
import { sharedSiteIcons } from "@latesight/ui/site-metadata";
import { SiteFooter } from "@latesight/ui/site-footer";
import { SiteHeader } from "@latesight/ui/site-header";
import "./globals.css";

export const metadata: Metadata = {
  title: "LateSight",
  description: "A personal hub for focused web tools.",
  icons: sharedSiteIcons
};

const headerLinks = [
  { label: "Dictionary", href: "https://dict.latesight.com" }
];

const footerLinks = [
  { label: "Dictionary", href: "https://dict.latesight.com" }
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
            slogan="毅一世 舞一时"
            links={headerLinks}
            logoHref="/"
          />
          {children}
          <SiteFooter
            legal="Copyright © 2026 LateSight. All rights reserved."
            links={footerLinks}
          />
        </div>
      </body>
    </html>
  );
}
