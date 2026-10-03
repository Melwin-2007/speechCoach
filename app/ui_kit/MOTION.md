# MOTION.md: Animation rules and catalogue

Motion in SpeechCoach explains what changed ("this appeared", "this was selected", "this line is your pitch over time"). It is calm and quick. If an animation does not explain something, delete it.

## 1. Principles
1. **Only these animatable properties:** `transform`, `opacity`, SVG `stroke-dashoffset`, `grid-template-rows` (for accordions) and `clip-path` (charts). Never animate `width`, `height`, `top`, `left`, `margin` or `box-shadow` blur on large areas.
2. **Durations:** hover/press 140 ms, state changes 240 ms, entrances 420 ms, chart draw and count-up 900 ms. Nothing else is longer than 600 ms.
3. **Easing:** entrances and moves use `--ease-out`; symmetric moves use `--ease-in-out`; `--ease-soft` (tiny overshoot) only for the hero chips and the file chip appearing. No elastic or big bounces.
4. **Stagger:** at most 60 ms between items and at most 8 items staggered; for long lists stagger the first 8 and show the rest at once.
5. **Interruptible:** animations never block clicks. A new selection cancels the previous animation.
6. **One idle loop per screen** at most (hero waveform). Idle loops pause when the tab is hidden and are removed for reduced motion.
7. **No parallax, no scroll-jacking, no auto-playing carousels, no confetti, no pulsing glow.**
8. **No layout shift:** reserve space before content arrives (min-heights, skeleton panels).
9. **60 fps:** playhead and crosshair move through refs and `requestAnimationFrame`, not React state, so the tree is not re-rendered 60 times a second.

## 2. Tokens (already in `tokens.css`)
```css
--d-fast: 140ms; --d-base: 240ms; --d-slow: 420ms; --d-draw: 900ms;
--ease-out: cubic-bezier(.22, 1, .36, 1);
--ease-in-out: cubic-bezier(.65, 0, .35, 1);
--ease-soft: cubic-bezier(.34, 1.25, .64, 1);
```

## 3. `motion.css` (copy into `app/src/styles/motion.css`)
```css
@keyframes rise   { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
@keyframes fade   { from { opacity: 0; } to { opacity: 1; } }
@keyframes pop    { from { opacity: 0; transform: scale(.96); } to { opacity: 1; transform: none; } }
@keyframes draw   { to { stroke-dashoffset: 0; } }
@keyframes grow-y { from { opacity: 0; transform: scaleY(.2); } to { opacity: 1; transform: none; } }
@keyframes bars   { 0%, 100% { transform: scaleY(.3); } 50% { transform: scaleY(1); } }
@keyframes drift  { from { transform: translateY(-5px); } to { transform: translateY(5px); } }
@keyframes breathe{ 0%, 100% { opacity: .55; } 50% { opacity: 1; } }
@keyframes nudge  { 0%, 100% { transform: none; } 25% { transform: translateX(-3px); } 75% { transform: translateX(3px); } }
@keyframes ring   { 0% { box-shadow: 0 0 0 0 color-mix(in srgb, var(--ring, var(--ink)) 35%, transparent); }
                    100% { box-shadow: 0 0 0 14px transparent; } }

.reveal   { opacity: 0; animation: rise var(--d-slow) var(--ease-out) forwards; animation-delay: calc(var(--i, 0) * 60ms); }
.fade-in  { opacity: 0; animation: fade var(--d-base) var(--ease-out) forwards; animation-delay: calc(var(--i, 0) * 40ms); }
.pop-in   { opacity: 0; animation: pop var(--d-base) var(--ease-soft) forwards; }
.draw     { stroke-dasharray: 1; stroke-dashoffset: 1; animation: draw var(--d-draw) var(--ease-out) forwards; } /* needs pathLength="1" on the element */
.grow-y   { transform-origin: bottom; animation: grow-y var(--d-slow) var(--ease-out) both; animation-delay: calc(var(--i, 0) * 60ms); }
.pulse-once { animation: ring 700ms var(--ease-out) 1; }
.skeleton { background: var(--paper-2); border-radius: var(--r-md); animation: breathe 1.4s var(--ease-in-out) infinite; } /* no shimmer gradient */

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
    animation-delay: 0ms !important;
    transition-duration: .01ms !important;
    scroll-behavior: auto !important;
  }
  .reveal, .fade-in, .pop-in { opacity: 1; }
  .draw { stroke-dashoffset: 0; }
}
```

## 4. Hooks (put in `app/src/lib/motion.js`)
```js
import { useEffect, useRef, useState } from "react";

export const prefersReducedMotion = () =>
  typeof matchMedia !== "undefined" && matchMedia("(prefers-reduced-motion: reduce)").matches;

/** Counts from 0 to target. Returns the current number. Instant when reduced motion is on. */
export function useCountUp(target, { duration = 900, enabled = true } = {}) {
  const [v, setV] = useState(prefersReducedMotion() ? target : 0);
  useEffect(() => {
    if (!enabled) return;
    if (prefersReducedMotion()) { setV(target); return; }
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
    const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setSeen(true); io.disconnect(); } }, options);
    io.observe(el);
    return () => io.disconnect();
  }, [seen]);
  return [ref, seen];
}

/** Runs a view-transition when supported, otherwise just runs the update. */
export function withViewTransition(update) {
  if (!prefersReducedMotion() && document.startViewTransition) document.startViewTransition(update);
  else update();
}
```

## 5. Catalogue (every animation allowed in the product)
| # | Where | Trigger | What moves | Spec |
|---|---|---|---|---|
| M1 | Page sections | First render | Fade-up | `.reveal`, `--i` stagger 0..7, 420 ms |
| M2 | Nav | Scroll > 8 px | Hairline + soft shadow fade in | `transition: box-shadow, background 240ms` |
| M3 | Hero banner waveform | Idle (loops) | Bars scaleY breathing, each bar delayed by its index × 70 ms, 1.6 s | `bars` keyframe; paused when tab hidden |
| M4 | Hero flaw chips | Idle (loops) | Gentle float ±5 px, 5-7 s each, offset starts | `drift` alternate infinite ease-in-out |
| M5 | Hero caption | Mount | Words appear one by one (30 ms apart), the flawed words then get their coloured underline drawn left to right (400 ms) | transform/opacity + `scaleX` underline |
| M6 | Segmented tabs | Tab change | The white pill indicator slides to the new tab | `transform: translateX`, 240 ms ease-out; content cross-fades 140 ms |
| M7 | Drop zone | Hover | Background mint → mint-2, icon circle lifts 2 px | 240 ms |
| M8 | Drop zone | Drag over | Scale 1.01, dashed border turns solid ink | 240 ms ease-out |
| M9 | Drop zone | Invalid file | Nudge once | `nudge` 280 ms + error text fades in |
| M10 | File chip | File accepted | Chip pops in, drop-zone content cross-fades to the chip | `.pop-in` |
| M11 | Buttons | Hover / press | Lift -1 px and trailing arrow +3 px / scale .98 | 140 ms |
| M12 | Loading card | While analysing | 7 rounded bars scaleY loop (staggered), elapsed-seconds counter | `bars`; **no fake step names** |
| M13 | Landing → results | Result arrives | Cross-fade + 16 px slide (View Transitions API, fallback instant) | `withViewTransition` |
| M14 | Score ring | Results mount | Ring stroke draws 0 → score and the number counts up together | 900 ms ease-out, `useCountUp` |
| M15 | Dimension chips | After ring | Stagger fade-up | `.reveal`, 60 ms |
| M16 | Radar | In view | Polygon scales from centre 0 → 1 (700 ms), vertex dots fade 200 ms after | `transform-box: fill-box; transform-origin: center` |
| M17 | Waveform bars | Audio ready | Bars grow from the baseline left to right (clip-path reveal) | `clip-path: inset(0 100% 0 0)` → `inset(0)` 700 ms |
| M18 | Flaw regions on waveform | After waveform | Each region grows up (`grow-y`), stagger 60 ms | `.grow-y` |
| M19 | Word ribbon | After waveform | Blocks fade in, 8 ms per word, total capped at 600 ms | `.fade-in` with capped delay |
| M20 | Chart lines | In view | Line draws left to right, band fades in 300 ms | `.draw` (needs `pathLength="1"`) |
| M21 | Chart regions | After lines | `grow-y`, stagger 60 ms | |
| M22 | Flaw list | Results mount | Cards stagger fade-up | `.reveal` |
| M23 | Flaw card hover | Hover | Lift -2 px, shadow-1 → shadow-2 | 200 ms |
| M24 | Flaw selected | Click | Card gets an ink 2 px ring (transition), the matching region gets `.pulse-once` in its colour, the waveform scrolls it into view if needed | 240 ms + 700 ms ring |
| M25 | Explanation card | Selection changes | Old content fades out 140 ms, new content rises 8 px and fades in 240 ms | cross-fade, interruptible |
| M26 | "Show the math" | Toggle | Panel expands via `grid-template-rows: 0fr → 1fr`, chevron rotates 180° | 260 ms ease-out |
| M27 | Tooltip | Hover chart/word | Pops in (scale .96 → 1, 120 ms) | `.pop-in` shortened |
| M28 | Playhead and crosshair | Playback / pointer | Follows time exactly, no easing | ref + rAF + `transform: translateX` |
| M29 | Current word | Playback | Word highlight moves word to word (background tint, 140 ms) | |
| M30 | Error banner | Appears | Slides down 12 px + fades, single `nudge` | 240 ms |
| M31 | Toast | Appears / leaves | Slides up 12 px + fade, auto-dismiss 4 s | 240 ms |
| M32 | Mobile mini-player | Scroll past waveform | Slides up from the bottom | `transform` 240 ms |
| M33 | Skeleton panels | Loading | Opacity breathing (no gradient sweep) | `.skeleton` |
| M34 | Demo sample cards | Hover | Card lifts 3 px, thumbnail bars rise 8% | 200 ms |

## 6. Reduced motion
When `prefers-reduced-motion: reduce`: no loops (M3, M4, M12 becomes a static icon with the elapsed counter), no draw or count-up (values show immediately), no slides; opacity changes of 100 ms are acceptable. The product must stay fully usable.

## 7. Performance checklist
- Chrome Performance panel: no long tasks > 50 ms during the results reveal on a mid-range laptop.
- Chart SVG: at most about 1,200 points per series; memoise paths; do not re-render charts on playhead movement.
- Use `will-change: transform` only on elements that are animating right now.
- Remove animation classes after they finish when they would block later hover transforms (or keep `animation-fill-mode: both` only on non-interactive wrappers).
