"use client";

import { useEffect, useRef, type CSSProperties } from "react";

const loaderDotColors = [
  "#ff2f92",
  "#ff9800",
  "#9bf000",
  "#00d9b8",
  "#248cff",
  "#7f39ff",
  "#ff2f4f"
] as const;

const LOADER_DURATION_MS = 2280;
const MOVE_STAGGER_RATIO = 0.075;
const MOVE_WINDOW_RATIO = 0.2;
const RETURN_START_RATIO = 0.5;

function clamp01(value: number) {
  return Math.max(0, Math.min(1, value));
}

function easeInOutCubic(value: number) {
  return value < 0.5 ? 4 * value * value * value : 1 - Math.pow(-2 * value + 2, 3) / 2;
}

function getDotOffset(progress: number, index: number, count: number) {
  const reverseIndex = count - 1 - index;
  const forwardStart = reverseIndex * MOVE_STAGGER_RATIO;
  const forwardEnd = forwardStart + MOVE_WINDOW_RATIO;
  const backwardStart = RETURN_START_RATIO + (index * MOVE_STAGGER_RATIO);
  const backwardEnd = backwardStart + MOVE_WINDOW_RATIO;

  if (progress < RETURN_START_RATIO) {
    if (progress <= forwardStart) {
      return 0;
    }

    if (progress >= forwardEnd) {
      return 1;
    }

    return easeInOutCubic(clamp01((progress - forwardStart) / MOVE_WINDOW_RATIO));
  }

  if (progress <= backwardStart) {
    return 1;
  }

  if (progress >= backwardEnd) {
    return 0;
  }

  return 1 - easeInOutCubic(clamp01((progress - backwardStart) / MOVE_WINDOW_RATIO));
}

export function SiteLoader() {
  const trackRef = useRef<HTMLDivElement | null>(null);
  const dotRefs = useRef<Array<HTMLSpanElement | null>>([]);

  useEffect(() => {
    const track = trackRef.current;

    if (!track) {
      return;
    }

    let animationFrame = 0;
    let trackTravel = 66;
    let packStep = 7;

    const readMetrics = () => {
      const styles = window.getComputedStyle(track);
      trackTravel = Number.parseFloat(styles.getPropertyValue("--loader-travel")) || 66;
      packStep = Number.parseFloat(styles.getPropertyValue("--loader-pack-step")) || 7;
    };

    const render = (timestamp: number) => {
      const progress = (timestamp % LOADER_DURATION_MS) / LOADER_DURATION_MS;

      dotRefs.current.forEach((dot, index) => {
        if (!dot) {
          return;
        }

        const offsetRatio = getDotOffset(progress, index, loaderDotColors.length);
        const offset = offsetRatio * trackTravel;
        const emphasis = 0.34 + (offsetRatio * 0.66);
        const scale = 0.82 + (offsetRatio * 0.12);

        dot.style.transform = `translate3d(${(index * packStep) + offset}px, 0, 0) scale(${scale})`;
        dot.style.opacity = `${emphasis}`;
      });

      animationFrame = window.requestAnimationFrame(render);
    };

    readMetrics();
    const resizeObserver = new ResizeObserver(readMetrics);
    resizeObserver.observe(track);
    animationFrame = window.requestAnimationFrame(render);

    return () => {
      resizeObserver.disconnect();
      window.cancelAnimationFrame(animationFrame);
    };
  }, []);

  return (
    <div className="site-loader" role="status" aria-live="polite" aria-label="Loading">
      <div
        className="site-loader__track"
        aria-hidden="true"
        ref={trackRef}
        style={
          {
            "--loader-dot-count": loaderDotColors.length
          } as CSSProperties
        }
      >
        {loaderDotColors.map((color, index) => (
          <span
            key={color}
            className="site-loader__dot"
            ref={(element) => {
              dotRefs.current[index] = element;
            }}
            style={
              {
                "--loader-dot-color": color,
                "--loader-dot-index": index
              } as CSSProperties
            }
          />
        ))}
      </div>
    </div>
  );
}
