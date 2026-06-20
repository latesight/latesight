"use client";

import { SiteLaunchOverlay } from "@latesight/ui/site-launch-overlay";
import { useEffect, useRef, useState, type MouseEvent } from "react";

type SiteLaunchLinkProps = {
  href: string;
  productName: string;
  domain: string;
};

export function SiteLaunchLink({ href, productName, domain }: SiteLaunchLinkProps) {
  const [overlayProductName, setOverlayProductName] = useState(productName);
  const [loading, setLoading] = useState(false);
  const navigationTimerRef = useRef<number | null>(null);
  const resetTimerRef = useRef<number | null>(null);

  useEffect(() => {
    function clearTimers() {
      if (navigationTimerRef.current !== null) {
        window.clearTimeout(navigationTimerRef.current);
        navigationTimerRef.current = null;
      }

      if (resetTimerRef.current !== null) {
        window.clearTimeout(resetTimerRef.current);
        resetTimerRef.current = null;
      }
    }

    function handlePageShow(event: PageTransitionEvent) {
      const navigationEntry = performance.getEntriesByType("navigation")[0] as PerformanceNavigationTiming | undefined;
      const isBackForward = event.persisted || navigationEntry?.type === "back_forward";

      if (!isBackForward) {
        return;
      }

      clearTimers();
      setOverlayProductName("LateSight");
      setLoading(true);
      resetTimerRef.current = window.setTimeout(() => {
        setLoading(false);
      }, 900);
    }

    function handlePageHide() {
      clearTimers();
    }

    window.addEventListener("pageshow", handlePageShow);
    window.addEventListener("pagehide", handlePageHide);

    return () => {
      window.removeEventListener("pageshow", handlePageShow);
      window.removeEventListener("pagehide", handlePageHide);
      clearTimers();
    };
  }, []);

  function handleClick(event: MouseEvent<HTMLAnchorElement>) {
    if (
      loading ||
      event.defaultPrevented ||
      event.button !== 0 ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey
    ) {
      return;
    }

    event.preventDefault();
    if (resetTimerRef.current !== null) {
      window.clearTimeout(resetTimerRef.current);
      resetTimerRef.current = null;
    }

    setOverlayProductName(productName);
    setLoading(true);

    navigationTimerRef.current = window.setTimeout(() => {
      window.location.href = href;
    }, 180);
  }

  return (
    <>
      <a className="home-site-link" href={href} onClick={handleClick}>
        <h2 className="home-site-title">
          <span className="home-site-title__dot" aria-hidden="true" />
          <span>{productName}</span>
          <span className="home-site-domain">{domain}</span>
        </h2>
      </a>
      <SiteLaunchOverlay productName={overlayProductName} active={loading} />
    </>
  );
}
