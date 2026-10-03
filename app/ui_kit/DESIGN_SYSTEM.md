# DESIGN_SYSTEM.md: Visual rules for the SpeechCoach dashboard

Every AI that touches `app/` must follow this file. If a request conflicts with it, say so and ask. Motion rules are in `MOTION.md`, component behaviour in `COMPONENTS.md`.

The three reference images live in `docs/design/reference/` (attach them whenever you do visual work):
- `ref-1-maestra-landing.png` (Maestra, audio to text)
- `ref-2-clideo-landing.png` (Clideo, audio to text)

---

## 1. What we take from the references (and what we change)

### 1.1 Borrow these ideas
| Idea seen in the references | How we use it |
|---|---|
| **One huge, confident headline** with a single quiet grey sentence under it (both pages) | Landing hero: bold display type, one plain sentence |
| **One dominant, very round container** holding the main action (Maestra's card, radius about 40 px) | The input card is the star of the landing page. Everything else is quieter |
| **Segmented pill tabs** inside the card (Maestra: File Upload / Paste Link / Record) | Input card tabs: "Analyze a recording" / "Try a sample" |
| **Dashed, softly tinted drop zone** with an icon in a white circle, a pill button and a small underlined link ("Try a sample file") | Our drop zone, same anatomy, our colours |
| **Row of tiny reassurance ticks** under the card | Three honest ticks under the input card |
| **Pill-shaped nav button**, airy nav, lots of space | Nav with a pill "Try a sample" button |
| **Pastel panel with live waveform bars and a typing caption** (Clideo's green banner) | Hero banner: mint panel, animated waveform, caption with the flawed words marked |
| **Floating, overlapping objects** (Clideo's SRT/TXT cards, round photo, flag badge) that add depth without gradients | Floating "flaw chips" overlapping the banner edges |
| Flat colour fills, soft rounded shapes, nothing glossy | Whole product |

### 1.2 Change these
- **No blue accents, no cool-tinted backgrounds.** Both references use blue; we use warm paper, mint, butter, coral and deep ink-green.
- **No stock photo or logo wall.** We have no customers to show. Use our own waveform and flaw chips.
- **After "Analyze" the page becomes a dashboard**, not a marketing page. The calm landing style carries over (same radii, colours, type), but the data areas are denser.

---

## 2. The feel in one paragraph
Calm, editorial and a little tactile, like a well-made notebook app rather than a SaaS template. Big friendly type, soft rounded shapes, flat colour (never gradients), colour used only to carry meaning, and motion that explains what changed. If a screen could be mistaken for a default AI-generated landing page (purple/blue gradient, glass cards, sparkles, three identical feature boxes), it is wrong.

---

## 3. Hard rules (checked in the QA audit)
1. **Colour:** no hue between 190° and 320° anywhere (no blue, indigo, violet, purple). This includes charts, focus rings, selection, scrollbars and default library colours.
2. **No gradients** of any kind: backgrounds, buttons, text, borders, chart fills, skeletons (no shimmer sweep). Flat fills and translucent flat fills only.
3. **No hard squares:** nothing has `border-radius: 0` and nothing smaller than 8 px, except 1 px dividers. This includes inputs, dropdown menus, tooltips, tags, waveform bars, chart region rectangles, word blocks, focus rings, scrollbars, images and buttons.
4. **No glassmorphism** (no `backdrop-filter` blur panels), no neon glow, no heavy black drop shadows.
5. **No emoji as icons.** Use `lucide-react` icons only.
6. **No fake content:** no lorem ipsum, no invented testimonials, user counts, company logos, accuracy numbers or "trusted by" strips.
7. **No "card in a card in a card"** with borders on each level. Use tinted panels (no border) inside white cards.
8. **No default fonts** as the visible look (not Inter, Roboto, Arial or the browser default). Use the fonts in section 5.
9. **Self-hosted everything:** fonts via npm packages, no CDN links, no external requests at runtime.
10. **Flat, warm, human copy** (section 11), no marketing buzzwords.

---

## 4. Colour

### 4.1 Palette
| Token | Hex | Used for |
|---|---|---|
| `--paper` | `#F5F3EE` | Page background (warm off-white) |
| `--paper-2` | `#ECE8DE` | Recessed areas, tracks, segmented-tab background |
| `--card` | `#FFFFFF` | Main cards |
| `--mint` | `#E4F1E7` | Hero banner, drop zone, positive panels |
| `--mint-2` | `#CBE3D2` | Baseline band in charts, hover on mint, unplayed waveform bars |
| `--butter` | `#FAEFC9` | "How to fix it" panel, warnings |
| `--blush` | `#FBE6E1` | "Botched" sample, soft error background |
| `--ink` | `#12302B` | Text, primary buttons, played waveform, participant line |
| `--ink-2` | `#2D4A44` | Secondary strong text |
| `--muted` | `#5B6B66` | Secondary text (contrast 4.5:1 or better on paper and white) |
| `--faint` | `#8F9A94` | Disabled text, tertiary labels (never for essential text) |
| `--line` | `#E3DFD4` | Hairlines and dividers |
| `--line-strong` | `#CFC9BA` | Input borders, secondary button borders |
| `--dash` | `#BFD3C6` | Dashed drop-zone border |
| `--ok` / `--warn` / `--bad` | `#2F8F63` / `#D9A21B` / `#C8412F` | Status icons and dots (not large fills) |

### 4.2 Flaw dimension colours (used in regions, chips, icons, list)
| Dimension | Token | Hex | Icon (lucide) |
|---|---|---|---|
| Pacing | `--c-pacing` | `#EE8434` (tangerine) | `Gauge` |
| Pausing | `--c-pausing` | `#E9C46A` (butter-gold) | `Pause` |
| Pitch | `--c-pitch` | `#2A9D8F` (teal-green) | `Activity` |
| Loudness (energy) | `--c-energy` | `#8AB33F` (olive-lime) | `Volume2` |
| Emphasis | `--c-emphasis` | `#D1495B` (raspberry) | `Target` |
| Clarity | `--c-clarity` | `#A9714B` (clay) | `Ear` |
| Fluency | `--c-fluency` | `#F2A7A0` (blush-pink) | `Mic` |

Rules: never put text directly on these colours; use the tint token (16% colour on white) as the background with `--ink` text and a solid colour dot or icon. Never rely on colour alone: every coloured thing also has an icon and a text label.

### 4.3 Severity ramp (word blocks and severity bars)
`--sev-0 #DDEBDF` (fine) → `--sev-1 #F3E4A6` (minor) → `--sev-2 #F2B66B` (moderate) → `--sev-3 #E0674A` → `--sev-4 #B8392B` (major).
Bands from the contract: minor `|z| ≥ 2`, moderate `≥ 3`, major `≥ 4.5`. Below 2 = fine.

### 4.4 `tokens.css` (copy exactly into `app/src/styles/tokens.css`)
```css
:root {
  /* Surfaces */
  --paper: #F5F3EE;
  --paper-2: #ECE8DE;
  --card: #FFFFFF;
  --mint: #E4F1E7;
  --mint-2: #CBE3D2;
  --butter: #FAEFC9;
  --blush: #FBE6E1;

  /* Ink */
  --ink: #12302B;
  --ink-2: #2D4A44;
  --muted: #5B6B66;
  --faint: #8F9A94;
  --on-ink: #FFFFFF;

  /* Lines */
  --line: #E3DFD4;
  --line-strong: #CFC9BA;
  --dash: #BFD3C6;

  /* Actions */
  --action: #12302B;
  --action-hover: #1D4740;
  --action-press: #0B201C;

  /* Status */
  --ok: #2F8F63;
  --warn: #D9A21B;
  --bad: #C8412F;

  /* Severity ramp */
  --sev-0: #DDEBDF;
  --sev-1: #F3E4A6;
  --sev-2: #F2B66B;
  --sev-3: #E0674A;
  --sev-4: #B8392B;

  /* Flaw dimensions */
  --c-pacing: #EE8434;
  --c-pausing: #E9C46A;
  --c-pitch: #2A9D8F;
  --c-energy: #8AB33F;
  --c-emphasis: #D1495B;
  --c-clarity: #A9714B;
  --c-fluency: #F2A7A0;
  --c-pacing-tint: color-mix(in srgb, var(--c-pacing) 16%, white);
  --c-pausing-tint: color-mix(in srgb, var(--c-pausing) 22%, white);
  --c-pitch-tint: color-mix(in srgb, var(--c-pitch) 16%, white);
  --c-energy-tint: color-mix(in srgb, var(--c-energy) 20%, white);
  --c-emphasis-tint: color-mix(in srgb, var(--c-emphasis) 14%, white);
  --c-clarity-tint: color-mix(in srgb, var(--c-clarity) 16%, white);
  --c-fluency-tint: color-mix(in srgb, var(--c-fluency) 28%, white);

  /* Radii: nothing below 8px */
  --r-xs: 8px;
  --r-sm: 12px;
  --r-md: 16px;
  --r-lg: 24px;
  --r-card: 28px;
  --r-xl: 32px;
  --r-2xl: 40px;
  --r-pill: 999px;

  /* Spacing (4px base) */
  --s-1: 4px;  --s-2: 8px;  --s-3: 12px; --s-4: 16px; --s-5: 24px;
  --s-6: 32px; --s-7: 48px; --s-8: 64px; --s-9: 96px;

  /* Shadows: soft and warm, never black */
  --shadow-1: 0 1px 2px rgba(18,48,43,.05), 0 4px 14px rgba(18,48,43,.05);
  --shadow-2: 0 2px 4px rgba(18,48,43,.05), 0 14px 40px rgba(18,48,43,.09);
  --shadow-pop: 0 8px 30px rgba(18,48,43,.18);

  /* Type */
  --font-display: "Bricolage Grotesque Variable", "Bricolage Grotesque", ui-sans-serif, system-ui, sans-serif;
  --font-body: "DM Sans Variable", "DM Sans", ui-sans-serif, system-ui, sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, monospace;

  /* Layout */
  --container: 1240px;
  --gutter: clamp(16px, 4vw, 40px);

  /* Motion (full set in MOTION.md) */
  --d-fast: 140ms;
  --d-base: 240ms;
  --d-slow: 420ms;
  --d-draw: 900ms;
  --ease-out: cubic-bezier(.22, 1, .36, 1);
  --ease-in-out: cubic-bezier(.65, 0, .35, 1);
  --ease-soft: cubic-bezier(.34, 1.25, .64, 1);
}
```

---

## 5. Typography
Install with npm (verify the exact package names first with `npm view <name>`): `@fontsource-variable/bricolage-grotesque`, `@fontsource-variable/dm-sans`, `@fontsource/ibm-plex-mono` (weights 400 and 500).

| Role | Family | Weight | Notes |
|---|---|---|---|
| Display / headings | Bricolage Grotesque | 600-700 | Tight tracking `-0.02em` on large sizes |
| Body / UI | DM Sans | 400-600 | |
| Numbers, times, z-scores | IBM Plex Mono | 400-500 | Also `font-variant-numeric: tabular-nums` on any changing number |

| Style | Size / line-height | Use |
|---|---|---|
| `display-xl` | `clamp(40px, 6.4vw, 72px)` / 1.02, weight 700, tracking -0.025em | Landing H1 |
| `h1` | 36 / 1.1 | Results title |
| `h2` | 28 / 1.15 | Panel titles |
| `h3` | 20 / 1.25, weight 600 | Card titles |
| `body` | 16 / 1.55 | Default |
| `small` | 14 / 1.5 | Secondary text |
| `micro` | 12 / 1.4 | Axis labels, captions |
| `mono-sm` | 13 / 1.4 | Times, numbers |

No all-caps labels with wide letter-spacing (an AI-template tell). Sentence case everywhere.

---

## 6. Shape, space and surfaces
- **Radii:** big containers 28-40 px (`--r-card`, `--r-2xl`), nested panels 20-24, inputs and menus 16, small chips and word blocks 8-12, buttons and chips fully round (`--r-pill`). Nested radii shrink inward (child radius = parent radius minus padding, roughly).
- **Cards:** white, `--shadow-1`, padding 24-32. Inside a card use tinted panels (`--mint`, `--butter`, `--paper-2`) with no border.
- **Borders:** prefer tint contrast over borders. When a border is needed use 1 px `--line` (cards on paper) or `--line-strong` (inputs).
- **Spacing:** generous. Between major sections 64-96 px; between cards 24; inside cards 24-32.
- **Layout:** max width `--container`, side padding `--gutter`. 12-column grid on desktop. Mix card sizes; avoid rows of identical boxes.
- **Breakpoints:** 640, 960, 1280. Phone (≤ 640) is a first-class layout.
- **Scrollbars:** thin, rounded thumb, `--line-strong`.
- **Selection colour:** `--butter` background with ink text.
- **Focus ring:** `outline: 2px solid var(--ink); outline-offset: 3px;` (it follows the element's radius).
- **No dark mode** (out of scope).

### 6.1 Buttons
| Type | Look | States |
|---|---|---|
| **Primary** | Pill, background `--action`, white text, display font 600, height 52 (hero) / 44 (default), padding 0 28 | hover: `--action-hover`, lift -1px, `--shadow-1`, trailing arrow moves 3px; active: scale .98 `--action-press`; disabled: `--paper-2` bg, `--faint` text |
| **Secondary** | Pill, white background, 1 px `--line-strong`, ink text | hover: `--paper` background |
| **Ghost** | No background, ink text, underline on hover (offset 4px) | |
| **Icon button** | 44 px circle, white or `--paper-2` | hover lift |
| **Play button** | 56 px circle, `--ink`, white icon | |

### 6.2 Inputs
Radius 16, white, 1 px `--line-strong`, padding 14/16. Focus: border `--ink` plus a 3 px `--mint-2` ring. Error: border `--bad`, message in `--bad` with an icon. Textareas auto-grow, `resize: none`. **Dropdowns are custom** (button + listbox, radius 20 menu, keyboard accessible), never the native square popup.

### 6.3 Chips and badges
Height 28-32, fully round. Flaw chip = tinted background + solid colour dot or icon + ink text. Severity pill: `Minor`, `Moderate`, `Major` using the ramp tints with ink text.

---

## 7. Iconography
`lucide-react`, stroke width 1.75, sizes 16 / 20 / 24, round caps and joins (the lucide default). Icon-in-circle pattern (like the upload icon in the reference): 56 px white circle, 24 px ink icon. No emoji, no sparkle icon, no robot icon.

## 8. Illustration style
Simple flat SVG made of rounded bars, blobs and chips; two or three colours per illustration from the palette; no gradients, no 3D, no outlines. The logo mark is three rounded vertical bars of different heights in mint-2, butter and coral (`#F26B4E`, used only in the logo and favicon), next to the wordmark "SpeechCoach" in the display font.

---

## 9. Data visualisation
- **Participant line:** `--ink`, 2.5 px, round joins. Gaps where pitch is unvoiced (`null`): break the line, never interpolate across.
- **Baseline:** a band in `--mint-2` (opacity .7) where the contract provides `pitch_lo`/`pitch_hi`; plus a dashed `--ok` line (1.5 px, dash 4 4) for the baseline value.
- **Flaw regions:** rounded rectangles (rx 10), 4 px inset top and bottom, filled with the dimension colour at 14% opacity; in the chart that matches the flaw's dimension use 30% and add a small chip at the top-left of the region.
- **Grid:** horizontal lines only, `--line`, dashed `1 4`. No chart border, no vertical grid.
- **Axis text:** 12 px mono, `--muted`; y-axis labels are inset over the plot (not in a left gutter) so all time panels share identical left/right edges and line up with the waveform.
- **Tooltip:** dark `--ink` rounded (radius 14) with white text, small arrow-free; shows time, your value, reference value, difference.
- **Crosshair:** 1 px `--ink` at 35% opacity plus dots on the lines.
- **Radar:** 7 axes, rings in `--line`, polygon fill `--mint-2` at 55% with a 2.5 px `--ink` stroke, round joins, dots at vertices.
- **Library colours:** if any library is used, override its default palette and fonts; the default blue must never appear.

## 10. Layout wireframes
See `COMPONENTS.md` section 1 (landing and results, desktop and phone).

---

## 11. Voice and microcopy
Plain, warm, specific. Say what the system measured, in numbers a judge can verify. Short sentences.

| Instead of | Write |
|---|---|
| "Unlock powerful insights with AI" | "See exactly where your speech goes wrong." |
| "Analysis complete!" | "Done. We found 3 things to work on." |
| "Oops! Something went wrong." | "We couldn't read that audio file. Try WAV, MP3 or M4A under 25 MB." |
| "Utilize the baseline" | "Compared with a strong reference reading" |
| "F0 std deviation" | "Pitch variation" |

Banned words and symbols: unlock, supercharge, leverage, seamless, elevate, revolutionize, AI-powered, magic, effortless, game-changer, "Welcome to", "Get started in seconds", sparkle emoji, exclamation marks in errors.
Numbers: one decimal; times as `m:ss.s` (for example `0:42.1`); a proper minus sign `−` (U+2212); z-scores as `z = −4.5`; units after a thin space.
Never claim things the product doesn't do (no "instantly", no accuracy percentages, no privacy promises we haven't verified).

---

## 12. Accessibility
- Text contrast 4.5:1 or better; large text and UI shapes 3:1.
- Never colour alone: icon + label + position/pattern too.
- Visible focus on everything interactive; logical tab order; skip link to main content.
- Waveform keyboard controls: Space play/pause, ← → seek 2 s, `[` and `]` previous/next flaw.
- Flaw regions are real buttons with `aria-label` ("Rushing, 0:42 to 0:51, major").
- Charts have `role="img"` and an `aria-label` summary; the flaw list is the text equivalent.
- Respect `prefers-reduced-motion` (see MOTION.md).
- Touch targets at least 44 × 44 px.

---

## 13. Anti-AI-look checklist (the QA audit scores each line pass/fail)
1. No hue 190-320° anywhere (blue, indigo, purple).
2. No gradients anywhere (backgrounds, buttons, text, charts, skeletons).
3. No element with a corner radius under 8 px (except 1 px dividers).
4. No glass/blur panels, no glow, no heavy shadows.
5. No emoji as icons; no sparkle icon.
6. Fonts are Bricolage Grotesque, DM Sans and IBM Plex Mono; nothing falls back to a default.
7. Hero is a single big headline and one sentence, not a slogan plus three badges.
8. The main action sits in one big rounded card.
9. No row of three identical feature cards with identical icons.
10. No bordered card inside a bordered card inside a bordered card.
11. Colour is used for meaning only (flaw dimension, severity, status); decoration uses paper, mint, butter, blush.
12. Copy is specific and human; no buzzwords; no fake stats or logos.
13. Mixed card sizes and asymmetric layout on the results page.
14. Numbers are in the mono font and aligned.
15. Chart palette overrides library defaults; regions are rounded.
16. Word blocks, waveform bars, tooltips, menus, inputs and focus rings are rounded.
17. Animations use only the catalogue in MOTION.md (no random bounces, no parallax, no auto-playing carousels).
18. Loading state is honest (no fake progress steps).
19. Every state exists: empty, loading, error, warning, no flaws found.
20. Looks right at 1440 px, 768 px and 390 px with no horizontal scroll.
21. No external network requests at runtime.
22. Keyboard-only use works end to end.
23. Reduced-motion users see no moving elements.
24. Screenshots next to the two references feel like the same family: airy, round, flat, confident type.

## 14. Definition of "design done"
`/#/styleguide` shows every token and component; the QA audit table is all pass; screenshots at three widths are saved in `docs/design/screenshots/` and linked from HANDOFF.md.
