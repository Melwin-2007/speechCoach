import { useEffect, useRef, useState } from "react";

export const prefersReducedMotion = () =>
  typeof matchMedia !== "undefined" && matchMedia("(prefers-reduced-motion: reduce)").matches;

/** Counts from 0 to target. Returns the current number. Instant when reduced motion is on. */
export function useCountUp(target, { duration = 900, enabled = true } = {}) {
  const [v, setV] = useState(prefersReducedMotion() ? target : 0);
  useEffect(() => {
    if (!enabled) return;
    if (prefersReducedMotion()) {
      setV(target);
      return;
    }
    let raf, t0;
    const ease = (t) => 1 - Math.pow(1 - t, 3);
    const tick = (t) => {
      t0 ??= t;
      const p = Math.min(1, (t - t0) / duration);
      setV(target * ease(p));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target, duration, enabled]);
  return v;
}

/** True once the element has entered the viewport (stays true). */
export function useInView(options = { threshold: 0.15 }) {
  const ref = useRef(null);
  const [seen, setSeen] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el || seen) return;
    const io = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) {
        setSeen(true);
        io.disconnect();
      }
    }, options);
    io.observe(el);
    return () => io.disconnect();
  }, [seen, options]);
  return [ref, seen];
}

/** Runs a view-transition when supported, otherwise just runs the update. */
export function withViewTransition(update) {
  if (!prefersReducedMotion() && typeof document !== "undefined" && document.startViewTransition) {
    document.startViewTransition(update);
  } else {
    update();
  }
}
