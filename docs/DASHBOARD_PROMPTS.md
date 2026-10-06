# DASHBOARD_PROMPTS.md: Prompts for building the dashboard (Member C)

> **Updated 2026-10-06.** Progress: D0a, D0, D1, D6, D8, D9a, D9b, D5, D7, D4 (loading/error parts) were delivered in tasks C1-C3 on mock data; D11 (task C4) must be verified with a real upload. Plan-driven additions (apply only after CONTRACTS v1.1 is approved): mode label chip ("Reference mode" / "No-reference mode"), confidence and deviation % on flaw cards, an `unseen` demo, honest processing stages. See section 6 at the end of this file.

This is the prompt library for the **front end** of SpeechCoach. It works with three design files in `docs/design/`: `DESIGN_SYSTEM.md` (look), `MOTION.md` (animation), `COMPONENTS.md` (layouts and specs). The prompts here are short on purpose; the detail lives in those files, so the AI must read them.

Backend prompts (repo scaffold, API, Docker) are in `docs/PROMPTS.md`; this file covers `app/` and the parts of `src/speechcoach/api/` that serve it.

---

## 0. Setup

### 0.1 Install the kit
```bash
# from the repo root, after unzipping ui_kit
cp -r ui_kit/docs/design docs/design
cp ui_kit/docs/DASHBOARD_PROMPTS.md docs/
git add docs && git commit -m "docs: design system, motion, components, dashboard prompts (task C1)"
```
The folder `docs/design/reference/` holds the two reference screenshots (Maestra and Clideo). AI tools cannot see them unless you attach them (see 0.2).

### 0.2 What to attach in every UI chat
| Always | `AGENTS.md`, `docs/CONTRACTS.md`, `docs/roles/MEMBER_C_APP.md`, `docs/design/DESIGN_SYSTEM.md`, `docs/design/MOTION.md`, `docs/design/COMPONENTS.md` |
|---|---|
| Visual prompts D2, D3, Q1 | also the two PNGs from `docs/design/reference/` |
| Review prompts (Q1) | screenshots of your own UI at 1440, 768 and 390 px |

If your AI tool cannot read files from disk, paste the contents instead.

### 0.3 Changes to existing project files (agree as a team first; AGENTS.md is a shared file)
The original plan names Plotly and the wavesurfer Regions plugin. For a polished, non-generic look (rounded shapes, custom animation, no default blue, smaller bundle) we use **custom SVG charts and our own region overlay**. Make these edits once, then log the decision in `docs/HANDOFF.md` under Decisions:

1. `AGENTS.md` section 3, replace the front-end line with:
   `FastAPI + uvicorn; React (Vite, JavaScript) + CSS Modules + d3-scale/d3-shape/d3-array + wavesurfer.js v7 (audio and waveform only) + lucide-react; design rules in docs/design/. No Plotly, no Tailwind, no UI kit.`
2. `docs/roles/MEMBER_C_APP.md` guardrail 5: replace "Regions plugin" with "our own region overlay layer" and "three stacked Plotly charts" with "three stacked custom SVG charts (d3-scale, d3-shape)".
3. `AGENTS.md` section 5, Member C paths: add `scripts/make_mock_result.py` and `docs/design/`.
4. `docs/TASKS.md` C2/C3 wording: "Plotly" becomes "SVG charts". Acceptance criteria stay the same.

### 0.4 Ports and API
- Dev: Vite on `5173`, FastAPI on `8000`. Vite proxies `/health`, `/baselines`, `/analyze`, `/demo` to `http://localhost:8000` so the app always calls relative URLs.
- Production (Docker / Hugging Face Space): everything on port `7860`, same origin.
- Demo audio convention (frontend only, not a contract change): JSON from `GET /demo/{name}`, audio from `GET /demo-audio/{name}.wav`.

### 0.5 Which prompt on which day
| Day | Plan task | Prompts | What you show at the evening sync |
|---|---|---|---|
| 1 | C1 scaffold | backend prompt C1 from `docs/PROMPTS.md`, then **D0a**, **D0** | `/#/styleguide` page, mock JSON valid, `make check` green |
| 2 | C2 dashboard v0 | **D1**, **D6**, **D8**, **D9a** | Waveform with regions, 3 charts, flaw list, all from mock data |
| 3 | C3 UI complete | **D9b**, **D5**, **D7** (+ pydantic models and Docker skeleton from `docs/PROMPTS.md`) | Explanation card with math, score ring, radar, word ribbon |
| 4 | C4 real integration (M1) | **D11**, **D4** | Real upload shows real flaws; friendly errors |
| 5 | C5 explanation and demo (M2) | **D2**, **D3**, **D10**, **Q4** | Landing page, demo buttons, stranger test |
| 6 | C6 polish and **freeze** | **D12**, **D13**, **D14** | Phone layout, motion pass, accessibility pass; tag `v0.9-freeze` |
| 7 | C7 package and deploy | **D16**, **D17**, **Q1** | Live Space, screenshots, design audit table |
| 8 | C8 bug fixes, doc | **R-prompts** as needed, **Q2**, **Q3** | Fixes from audits; doc page 1 |
| 9 | C9 video | **V1** | Demo recording and edit |

Re-baseline (2026-10-06, Day 4): rows 1-3 are done on mock data. Today: verify C4/D11 with a real upload and log it. Then D2, D3, D10, Q4 (C5), then D18-D20 once v1.1 is approved. Freeze is Day 6 (2026-10-08): if time is short, drop the bonus prompts and D21 first.

### 0.6 The UI loop (every task)
```
U0 opener ──► AI replies with plan + a paragraph describing how it will LOOK and MOVE
  └ you check the description against the design files
U1 "go" ──► AI builds ──► runs `npm run dev`, `npm run build`, `npm run lint:design`
  └ you open the browser, look at 1440 px and 390 px, click everything
R1 visual self-check (paste screenshots) ──► AI lists deviations from the design files and fixes ONLY those
  └ P7 contract check, P8 other-AI review (docs/PROMPTS.md), P10 session closer
```
Never accept a UI task from a text report alone. Look at the screen.

---

## 1. Opener and go (use for EVERY UI task)

### U0: UI session opener
Fill `<TASK>` with one of the task prompts D0a-D17 (copy the text in the box).
```
You are building the front end of SpeechCoach as Member C. Work only inside app/ (plus src/speechcoach/api/ or scripts/ only if the task says so).

Read first, in this order:
1. AGENTS.md
2. docs/CONTRACTS.md (sections 6 and 7)
3. docs/roles/MEMBER_C_APP.md
4. docs/design/DESIGN_SYSTEM.md
5. docs/design/MOTION.md
6. docs/design/COMPONENTS.md (the sections named in the task)
7. Any screenshots I attached: study them closely.

UI RULES (non-negotiable, they apply to everything you write):
1. Colour: no hue between 190 and 320 degrees anywhere (no blue, indigo, violet, purple). Use only tokens from tokens.css. No hex codes in components.
2. No gradients of any kind (backgrounds, buttons, text, chart fills, skeletons).
3. No hard squares: no border-radius under 8px (except 1px dividers); inputs, menus, tooltips, chips, bars, regions, focus rings, scrollbars are all rounded.
4. No glass/blur, no glow, no heavy shadows. Use the shadow tokens.
5. Fonts: Bricolage Grotesque (display), DM Sans (body), IBM Plex Mono (numbers), self-hosted via npm. Icons: lucide-react only. No emoji as icons.
6. Motion: only animations listed in MOTION.md, using the tokens and classes there; respect prefers-reduced-motion; animate only transform/opacity/stroke-dashoffset.
7. The frontend renders data from the contract. It never computes pitch, pace, z-scores, severity or scores. Display-only formatting is fine.
8. No new dependencies beyond the list in COMPONENTS.md section 0. If you think one is needed, ask.
9. CSS Modules plus tokens. Components under ~150 lines; split if larger.
10. Every component handles its states: loading, empty, error, and (where relevant) no-flaws.
11. Build against mock data first (app/public/mock_result.json); no hard-coded hosts; no contract changes (use the change protocol).
12. Accessibility: visible focus, keyboard operable, aria-labels, 44px touch targets, contrast per the design system.
13. Copy: plain, warm, specific; follow the voice rules in DESIGN_SYSTEM.md section 11; no invented stats, logos or claims.
14. Check library APIs against the INSTALLED version before using them (pip/npm docs, node_modules types, help text). Do not guess.

TASK:
<TASK>

Do NOT write code yet. Reply with:
(a) the task in your own words;
(b) the six UI rules that matter most for this task;
(c) the exact files you will create or edit;
(d) one paragraph describing how it will look and move (colours, radii, motion by catalogue number) so I can catch design problems before any code exists;
(e) how I will verify it (commands and what I should see on screen);
(f) risks and up to 3 questions.
Then wait for me to say "go".
```

### U1: go (UI version)
```
Go. Implement exactly the approved plan, nothing more.
When done:
1. Run `npm run build` and `npm run lint:design` (once they exist) and show the results.
2. Start `npm run dev` and tell me exactly what I should see and click to verify each acceptance point.
3. Report: files changed; commands; what I should see at 1440px and at 390px; any deviation from the design files (be honest); what is NOT done.
Do not commit. Do not touch files outside the plan.
```

---

## 2. Core task prompts (paste into U0 where it says `<TASK>`)

### D0a: Mock data generator (Day 1)
```
Task D0a: Mock data generator.
Create scripts/make_mock_result.py (Python, standard library plus numpy only) that writes contract-valid AnalysisResult JSON (docs/CONTRACTS.md section 6) so the UI can be built and judged before the real pipeline exists.

CLI: python scripts/make_mock_result.py --preset botched|almost|ideal --out <json path> [--audio <wav path>] [--seed 1234]

Presets:
- botched: 58.4 s, 5 flaws: PACE_FAST (major), MONOTONE (major, overlapping the first flaw in time by about 3 s so overlapping regions get tested), VOLUME_DROP (moderate), PAUSE_MISSING (moderate), FILLERS (minor). Overall score about 42. meta.warnings contains one warning string (to test the banner).
- almost: 58.4 s, one PACE_FAST flaw (minor). Overall about 88.
- ideal: 58.4 s, flaws = [] and overall about 94.

Consistency rules (a reviewer will check these):
- words: about 120 words from a built-in public-domain sample text (Tagore's "Where the mind is without fear" extended is fine), start/end from a simple speaking model (about 4.3 syllables/s, 0.3 to 0.6 s pauses after punctuation), conf between 0.8 and 0.99.
- series at exactly 20 points per second: participant pitch_st (smooth contour, about 20% null for unvoiced), energy_db (all <= 0), rate_sps; baseline pitch_st, pitch_lo, pitch_hi, energy_db, rate_sps. Inside each flaw region the participant series must visibly show the flaw (rate up for PACE_FAST, flat pitch for MONOTONE, energy dip for VOLUME_DROP).
- words[].z: small (|z| < 1.5) outside flaws, large inside, matching flaw severity.
- each flaw: evidence {participant, baseline, z, unit} consistent with the series and the word z-scores; explanation has five fields (observed, deviation, where, why, fix) written from those numbers in plain English; band from |z| (minor >= 2, moderate >= 3, major >= 4.5); severity = clip((|z| - 1.5) / 4.5, 0, 1).
- scores.dimensions plausible; overall = weighted sum with weights pacing .20, pausing .15, pitch .20, energy .15, emphasis .10, clarity .10, fluency .10.
- meta: mode "reference", baseline_id "T4".
- Deterministic (seeded), floats rounded to 4 decimals, keys sorted, flaws sorted by start.

--audio writes a 16 kHz mono 16-bit WAV (stdlib wave plus numpy): harmonic tone bursts at the word times (pitch following pitch_st, amplitude following energy_db) and silence in pauses. It does not need to sound like speech.

Include a validator in the script (types, len(series arrays) == len(t), start < end <= duration, first_word <= last_word < len(words)) and run it before writing files.

Generate: app/public/mock_result.json (botched preset), app/public/demo/{ideal,almost,botched}.json, app/public/demo-audio/{ideal,almost,botched}.wav.

Acceptance: running it twice gives byte-identical files; the validator passes; each wav is at most 2.5 MB; the three JSON files differ as described.
Verify: run it and print, for each preset: number of words, flaws (types), overall score, series length.
```

### D0: Design foundation (Day 1)
```
Task D0: Design foundation, tooling and style guide page. Sections: DESIGN_SYSTEM.md (all), MOTION.md sections 2-4, COMPONENTS.md sections 0 and 22.

Do:
1. Vite + React (JavaScript) in app/ (if it already exists from C1, keep it). Install only the allowed packages (COMPONENTS.md section 0). Verify exact npm package names with `npm view` before installing the font packages and tell me if any fails.
2. Create app/src/styles/tokens.css EXACTLY as in DESIGN_SYSTEM.md section 4.4 (do not change any value), base.css (reset, body background var(--paper), fonts, type styles from section 5, focus ring, selection colour, thin rounded scrollbars, `font-variant-numeric: tabular-nums` helper class), motion.css EXACTLY as in MOTION.md section 3, and import the fonts in main.jsx.
3. app/src/lib/colors.js (exact copy of COMPONENTS.md section 0.2), lib/format.js (fmtTime, fmtNum with true minus sign, scoreLabel, wordBand; display-only, commented as such), lib/motion.js (exact copy of MOTION.md section 4).
4. vite.config.js: proxy /health, /baselines, /analyze, /demo to http://localhost:8000.
5. A design linter: app/scripts/check-design.mjs run by `npm run lint:design`. It scans app/src/**/*.{css,jsx,js} and exits non-zero (printing file:line) on: `gradient(`, `backdrop-filter`, `transition: all`, any border-radius under 8px (allow 50%, 999px, 100px+, var(--r-*)), hex colours outside tokens.css, emoji characters in JSX, and any hex in tokens.css whose HSL hue is between 190 and 320 with saturation above 10%. Add it to the `check` target in the Makefile (Member C owns it).
6. Components/Styleguide + hash route `#/styleguide` rendering: palette swatches, flaw colours with their icons, type scale, buttons (primary/secondary/ghost/icon/play; all states), chips and severity pills, text input, textarea, radius samples, shadow samples, a bars loader, and tiny motion demos (reveal stagger, count-up, line draw-in with pathLength).

Acceptance: `npm run build` and `npm run lint:design` pass; the style guide page looks calm, warm and rounded, with no blue/purple, no gradients, no square corners; fonts load from node_modules (no CDN, check the Network tab).
Verify: open http://localhost:5173/#/styleguide at 1440px and 390px; deliberately add `background: linear-gradient(red, blue)` to a CSS file and confirm lint:design fails, then remove it.
```

### D1: App shell, state machine, API client (Day 2)
```
Task D1: App shell, state machine, API client. Sections: COMPONENTS.md sections 0, 0.1, 2, 3; DESIGN_SYSTEM.md sections 6.1, 6.2.

Build:
1. Nav (COMPONENTS section 3) with the logo mark (three rounded bars, DESIGN_SYSTEM section 8) and wordmark, links from src/links.js (placeholders), pill "Try a sample"; scroll hairline (M2).
2. api/client.js: getBaselines(), analyze({file, transcript, baselineId, mode, signal}), getDemo(name). `VITE_USE_MOCK` (default on until task D11): in mock mode analyze waits 1.2 s then returns /mock_result.json and the audio URL is the uploaded file (object URL) or /demo-audio/botched.wav when no file. Normalise failures to { kind: "audio" | "transcript" | "too_large" | "validation" | "network" | "timeout" | "server" | "invalid_response", message, status }. Add validateResult(result) checking required top-level keys, series arrays equal in length to series.t, and flaws sorted; failures become kind "invalid_response". Client timeout 120 s with AbortController.
3. state/useAnalysis.js (reducer: idle, loading, success, error; elapsed seconds counter; abort), state/SelectionContext.jsx, state/playStore.js (tiny external store: subscribe, getTime, setTime).
4. App.jsx: states idle -> loading -> success | error with a View Transition between idle and results (lib/motion.js). Hash routes: #/ and #/styleguide.
5. Temporary landing: a plainly styled but token-correct form (file input, transcript textarea, Select placeholder, Analyze button). Temporary results: a placeholder card showing meta, score and the flaw count. Both are replaced in later tasks (D2, D5).
6. types.js with JSDoc typedefs for AnalysisResult, Flaw, Word.

Acceptance: in mock mode I can pick any audio file, type any transcript, click Analyze, see a 1.2 s loading state, and then the placeholder results with real mock numbers; cancel works; forcing an error (a dev-only query param ?fail=network) shows the normalised message; `npm run build` and `lint:design` pass.
```

### D2: Landing hero and input card (Day 5; attach both reference PNGs)
```
Task D2: Landing hero and input card. Sections: COMPONENTS.md sections 1.1, 4, 5, 19, 20; DESIGN_SYSTEM.md sections 1, 3, 6; MOTION.md M1, M6-M11.
Study the attached reference screenshots (Maestra and Clideo). Recreate their layout logic (huge centred headline, one very round dominant card with segmented tabs, dashed tinted drop zone with an icon in a white circle, a pill button, a small underlined link, a row of ticks beneath) using OUR palette and rules. No blue, no gradients, nothing square.

Build: Hero, InputCard (segmented tabs with a sliding indicator, Dropzone with idle/hover/drag-over/accepted/invalid states, file chip, custom accessible Select fed by GET /baselines with options Auto-detect / each baseline / Other speech (general norms), auto-growing transcript textarea with word count, Analyze button with a disabled state and a message saying what is missing), reassurance ticks, and the Toast component.
Client-side validation: extensions .wav .mp3 .m4a .flac .ogg .webm, size <= 25 MB, transcript >= 5 words; plain-language messages from COMPONENTS.md.
Map the Select to the API: Auto-detect -> mode "auto"; a baseline -> mode "reference" + baseline_id; Other -> mode "prior".
The second tab ("Try a sample") may be an empty placeholder until task D3.
Use the suggested copy in COMPONENTS.md section 4 for the headline and sentence.

Acceptance: at 1440px the page reads as the same visual family as the references (airy, round, flat, confident type); drag-and-drop, click-to-choose and keyboard (Tab, Enter, Space, Esc in the Select) all work; oversize or wrong-type files show the nudge animation and a clear message; Analyze enables only when valid; layout works at 390px with no horizontal scroll; lint:design passes.
Verify: describe how you tested each state, and give me the list of files I should try (wrong type, 30 MB, valid wav).
```

### D3: Hero banner, sample cards, how it works, footer (Day 5)
```
Task D3: Hero banner, sample cards, how-it-works and footer. Sections: COMPONENTS.md sections 6, 7, 21 (the "How it works" spec is written out in item 3 of this prompt); DESIGN_SYSTEM.md sections 1.1, 8; MOTION.md M3-M5, M34. Attach the reference PNGs again and study Clideo's mint banner.

Build:
1. HeroBanner per section 6 (mint panel, ~48 rounded bars animated with M3, caption revealed word by word with the "without fear" underline drawn in (M5), 2-3 floating chips overlapping the panel edge (M4), small "Example of what we flag" caption, aria-hidden).
2. SampleCards per section 7 (three cards of different widths: Ideal/mint, Almost perfect/butter, Botched/blush, each with a static mini waveform thumbnail, duration and an "Open" pill; the "Try a sample" tab inside the InputCard reuses the same component). Clicking calls the demo loader (hook it to the existing analyze flow with getDemo; full demo mode comes in D10, so for now load /demo/{name}.json from public).
3. "How it works": three steps in ONE row but not identical boxes: large numerals, short plain text, different vertical offsets, a thin dashed flat connector (SVG). Steps: 1 Upload a recording and its text. 2 We compare it with a strong reference reading. 3 You see exactly where to improve and how. No icons-in-squares.
4. Footer per section 21.

Acceptance: the banner feels alive but calm (one idle loop only); nothing resembles a generic AI landing page; no identical-card row; chips overlap the banner edge without clipping; works at 390px; with reduced motion the banner is static; lint:design passes.
```

### D4: Loading, error and warnings (Day 4)
```
Task D4: Loading card, error banner and warnings. Sections: COMPONENTS.md section 8; MOTION.md M12, M30, M33.
Build LoadingCard (7 rounded animated bars, elapsed counter in mono, honest copy, Cancel button) over skeleton panels shaped like the results layout (no shimmer gradient), ErrorBanner with the mapping table (all causes), the warnings banner for meta.warnings (expandable list), and an "unexpected data" fallback that never crashes the page (wrap results in an error boundary with a friendly message).
Wire them to useAnalysis states. Do not invent progress steps or percentages.
Acceptance: each error kind from api/client.js shows its message with working actions ("Try again", "Choose another file"); cancelling returns to the input with the form intact; an exception inside a results component shows the fallback instead of a blank page; no layout shift when results arrive; reduced motion shows a static loader.
Verify: use the dev-only ?fail=<kind> switch to display every error; upload a .txt and a 30 MB file after D11 to see the real ones.
```

### D5: Results shell, score card and radar (Day 3)
```
Task D5: Results layout, header, score card and radar. Sections: COMPONENTS.md sections 1.2, 9, 10, 11; DESIGN_SYSTEM.md sections 4.2, 6, 9; MOTION.md M13-M16.
Build ResultsHeader, the results grid (score + radar row, then a left 8-column area and a sticky right 4-column area with placeholder cards for the parts coming in later tasks), ScoreCard (SVG ring with round caps, count-up number, label from lib/format scoreLabel, seven dimension chips with icons, tint circles and rounded mini bars, hover highlights are optional), and RadarCard (SVG, seven fixed axes, rings, polygon draw-in, vertex dots, axis labels with icons and numbers, accessible tooltip, list-of-bars fallback below 420px).
Handle: flaws.length === 0 (mint note in ScoreCard), missing dimension values (show an em dash and exclude from the polygon).
Acceptance: with mock data the summary row looks clean and balanced; ring and number animate together once; radar polygon grows from the centre; numbers use the mono font; no blue; works at 390px; reduced motion shows final values immediately.
```

### D6: Waveform panel with region overlay (Day 2)
```
Task D6: Waveform panel, region overlay, controls. Sections: COMPONENTS.md section 12 and the alignment rule in 1.2; DESIGN_SYSTEM.md sections 4.2, 6, 12; MOTION.md M17, M18, M24, M28.
First check the INSTALLED wavesurfer.js v7 API (node_modules typings or docs) for: WaveSurfer.create options (barWidth, barGap, barRadius, height, normalize, cursorColor, cursorWidth), load(url), playPause(), play(start, end), setTime(), getCurrentTime(), and events (ready, timeupdate, audioprocess, interaction, finish). Show me what you found and use only what exists.

Build:
1. WaveformPanel: wavesurfer for audio and waveform only (NOT the Regions plugin). Canvas colours must be resolved hex strings read from the CSS variables (getComputedStyle), unplayed bars --mint-2, played bars --ink. Load from the object URL or the demo URL.
2. Region overlay: an absolutely positioned layer with one <button> per flaw (left and width in percent of duration, radius 14, 22% dimension colour, 2px solid top edge, chip with icon and short label if the region is at least 90px wide, aria-label like "Rushing, 0:42 to 0:51, major"). Overlapping flaws must not hide each other: implement lib/lanes.js (greedy lane assignment) and reserve vertical room.
3. Controls: 56px play/pause circle, time "0:12.4 / 0:58.4" in mono, previous/next flaw buttons, keyboard (Space, left/right 2 s, [ and ]).
4. Sync: write current time to playStore from wavesurfer events; clicking a region selects the flaw (SelectionContext) and plays from its start. Do NOT put playback time in React state.
5. Entrance: M17 (bars reveal), then M18 (regions grow, staggered).
6. States: decoding failure (error variant), loading skeleton, audio over 5 minutes shows a note.

Acceptance: with mock_result.json and demo audio the waveform renders with rounded bars; five regions show in lanes without overlap problems; clicking a region plays from its start and selects it; Space/arrow keys work; playhead is smooth; no hex or blue anywhere; `npm run build` and lint pass.
Verify: tell me how to test overlapping regions (the botched mock has two overlapping flaws).
```

### D7: Word ribbon and transcript (Day 3)
```
Task D7: Word ribbon and transcript panel. Sections: COMPONENTS.md sections 13, 14; DESIGN_SYSTEM.md section 4.3; MOTION.md M19, M29.
Build WordRibbon (14px row under the waveform sharing the waveform's inner width, one rounded block per word positioned by time, colours from the severity ramp via lib/format wordBand(max |z|), tooltip with word, time and the largest deviation and its dimension, outline for words in the selected flaw, tiny legend with four swatches) and TranscriptPanel (words as inline rounded spans tinted by band, current word underlined during playback via playStore + rAF, click to seek, selected-flaw words outlined, scrolls inside the card, thin rounded scrollbar).
Acceptance: blocks line up exactly with the waveform (a word at 12.0 s sits at the same x in both); hovering shows the tooltip; clicking a transcript word seeks; the current word follows playback without re-rendering the whole panel; works with 400 words without lag.
```

### D8: Chart stack (Day 2)
```
Task D8: ChartStack and TimeChart (custom SVG). Sections: COMPONENTS.md section 15; DESIGN_SYSTEM.md section 9; MOTION.md M20, M21, M27, M28.
Use only d3-scale, d3-shape and d3-array (no Plotly, no chart library).
Build one white card (radius 28) with three stacked TimeChart instances: Pitch (series.participant.pitch_st with a baseline band pitch_lo..pitch_hi and dashed baseline line), Loudness (energy_db), Speaking rate (rate_sps). One shared x scale (0..meta.duration_s) and the same inner width and 24px side padding as the waveform so seconds line up.
Details: line with defined() so null (unvoiced) values break the line; participant 2.5px --ink; baseline dashed --ok; rounded flaw rectangles (rx 10, inset 4px) coloured by dimension (stronger fill in the matching chart); inset mono y labels; dashed horizontal grid only; x labels (m:ss) only under the last chart; ResizeObserver; memoised paths; synced crosshair and one tooltip (time, you, reference, difference) across all three charts; click seeks; crosshair also follows the playhead through playStore + rAF (do not re-render charts on playback); role="img" with a summary aria-label; "Not enough data" panel when fewer than 2 points.
Animation: lines draw in with pathLength="1" and .draw (M20), then regions grow (M21).
Acceptance: three clean charts, no default colours, no square shapes; gaps in pitch are visible; hover is smooth; the crosshair is synced; playback moves the crosshair smoothly; Performance panel shows no long tasks while hovering.
```

### D9a: Flaw list and selection (Day 2)
```
Task D9a: FlawList and selection behaviour. Sections: COMPONENTS.md sections 2, 16; MOTION.md M22-M24.
Build FlawList (heading with the real count, cards sorted by start time with tint icon circle, human label from lib/colors FLAW_TYPES, time range in mono, severity pill, rounded severity bar, selected state with 2px ink ring, hover lift, keyboard arrows + Enter, phone scroll-snap row, empty state card) and SelectionContext (selectedFlawId; default to the most severe flaw when results load).
Selection effects: the matching waveform region pulses once in its colour (M24), the waveform plays from the flaw's start when the user clicks a card or a region (not on default selection), words of the flaw are outlined in the ribbon and transcript (once those exist), and the ExplanationCard placeholder shows the selected flaw's raw explanation text.
Handle unknown flaw types gracefully (fallback label = the type string).
Acceptance: clicking a card or a region keeps both in sync; keyboard works; empty state appears for the "ideal" preset.
```

### D9b: Explanation card and "Show the math" (Day 3)
```
Task D9b: ExplanationCard and MathDisclosure. Sections: COMPONENTS.md sections 17; DESIGN_SYSTEM.md sections 6, 11; MOTION.md M25, M26.
Build the ExplanationCard (header with icon, label, severity pill and time range; five blocks in this order: What we measured, How far off, Where (with a "Play this part" pill), Why it matters, How to fix it (inside a --butter panel); text comes straight from the data, never rewritten) and MathDisclosure ("Show the math": rounded --paper-2 panel with a three-column You / Reference / Difference table using evidence.participant, evidence.baseline, evidence.z, evidence.unit, one plain sentence about what z means, and the formula in mono; expands with grid-template-rows 0fr to 1fr, chevron rotates).
Content swaps with a cross-fade and slight rise when the selection changes; interruptible.
Acceptance: all five fields visible for each mock flaw; math panel opens and closes smoothly and is keyboard operable (button with aria-expanded); long text wraps without overflow; card is sticky below the list on desktop and flows normally on phone.
```

### D10: Demo mode (Day 5)
```
Task D10: Demo mode end to end. Sections: COMPONENTS.md section 7 and 0.1; MOTION.md M13, M34.
Make the three sample cards (and the nav "Try a sample" button, which opens the Botched demo) load a full result with NO upload: GET /demo/{name} for the AnalysisResult and /demo-audio/{name}.wav for the audio. In dev these come from app/public (and the proxy); in production the API serves them (coordinate: if src/speechcoach/api does not yet serve /demo-audio, add the static route there, nothing else in the API).
Add the deep link #/results?sample=botched (and ideal, almost) that loads the demo directly (useful for the video and for judges).
Show "You're viewing a sample" as a small mint pill in ResultsHeader with a "Analyze your own" action.
Acceptance: clicking each card shows results within a second, audio plays, regions line up with the audio; the deep link works after a hard refresh; offline (no network to the API) the app still loads demos from public files in dev.
Milestone check (task Q4): a stranger must understand the botched demo within one minute.
```

### D11: Real API integration (Day 4)
```
Task D11: Connect the real API (milestone M1). Sections: COMPONENTS.md sections 0.1, 5, 8; CONTRACTS.md sections 6, 7.
1. Turn off mock mode by default (VITE_USE_MOCK defaults to off; keep it as a dev switch).
2. analyze() sends multipart/form-data with fields audio, transcript, baseline_id (only when mode is reference), mode, using relative URLs and the AbortController; keep the 120 s timeout.
3. Map real responses: 400 {error} to kind audio or transcript by message content (fall back to a generic bad-request message), 413 to too_large, 422 to validation, network to network, anything else to server; run validateResult on success and show the invalid_response error if it fails. Never show raw server text beyond the contract's error message.
4. Show warnings from meta.warnings in the warnings banner.
5. If the live response does not match the contract, do NOT change the frontend to work around it: write the exact mismatch in docs/HANDOFF.md under Requests for Member B.
Acceptance: uploading dataset/sample/<flawed>.wav with its transcript and baseline T4 shows REAL regions and charts; uploading the same file twice returns noticeably faster (server cache); a .txt file and a 30 MB file show friendly errors; the page never shows a stack trace.
Verify: give me the exact steps and the files to use; show the network request and response shape from the browser's Network tab.
```

### D12: Responsive and phone layout, mini player (Day 6)
```
Task D12: Responsive pass and mini player. Sections: COMPONENTS.md sections 1, 18; DESIGN_SYSTEM.md sections 6, 12.
Make every screen work at 1440, 1024, 768 and 390px with no horizontal scroll: landing (card and banner stack), results (single column in the order given in COMPONENTS 1.2), flaw cards as a horizontal scroll-snap row, radar replaced by bars below 420px, charts at 120px height. Touch targets at least 44px. Add MiniPlayer (M32) that slides up when the waveform leaves the viewport.
Test the iOS Safari quirks: 100vh issues (use dvh), audio play requires a user gesture, no hover-only interactions (tooltips also open on tap).
Acceptance: screenshots at the four widths look intentional (not just squeezed); tapping a region on a phone selects and plays; the mini player controls work; lint:design passes.
```

### D13: Motion polish pass (Day 6)
```
Task D13: Motion polish and audit. Sections: MOTION.md (all).
Audit the whole app against the catalogue in MOTION.md section 5. Produce a table: catalogue number, implemented yes/no, file, notes. Implement the missing ones that matter (M1, M6, M13, M14, M16, M20, M21, M24, M25, M26 first). Remove any animation that is not in the catalogue. Check: only transform/opacity/stroke-dashoffset/grid-rows/clip-path are animated; durations and easings use the tokens; stagger caps are respected; no layout shift; prefers-reduced-motion removes loops and draw/count-up; hidden tabs pause idle loops.
Measure with the Chrome Performance panel on the results reveal and report the longest task.
Acceptance: the app feels calm and polished; nothing bounces or flashes; reduced-motion mode is fully usable.
```

### D14: Accessibility pass (Day 6)
```
Task D14: Accessibility pass. Sections: DESIGN_SYSTEM.md section 12.
Check and fix: keyboard-only use end to end (upload, analyze, select flaws, play, open the math panel, use the Select); visible focus on every interactive element; logical tab order; skip link; aria-labels for regions, play controls, chips and charts; aria-live regions for loading and error messages; colour is never the only signal (icon + label present); contrast 4.5:1 for text and 3:1 for UI shapes (list any pair that fails and fix with tokens only); touch targets; reduced motion; zoom to 200% without breaking layout.
Run Lighthouse (Accessibility) in Chrome on the landing and results pages and paste the scores and every failed audit; fix them.
Acceptance: Lighthouse accessibility 95 or higher on both pages; a keyboard-only run-through succeeds; lint:design passes.
Then tag the repo: v0.9-freeze (after the whole team agrees). No new features after the freeze.
```

### D16: Production build and serving (Day 7)
```
Task D16: Production build, serving and Docker front-end stage. Files: app/ (build), src/speechcoach/api/ (static mount only), Dockerfile (frontend stage only).
1. `npm run build` outputs app/dist with hashed assets. FastAPI serves it from the same origin (StaticFiles) and keeps /health, /baselines, /analyze, /demo/{name}, /demo-audio/{name}.wav working; hashed assets get long cache headers, index.html no-cache.
2. Fonts are bundled (no CDN). Open the Network tab on the live build and confirm there are zero requests to other hosts.
3. Dockerfile frontend stage: node:20, `npm ci`, `npm run build`; the Python stage copies app/dist; port 7860. Do not touch the Python dependency layers.
4. Add `make app-prod` (build and serve on 7860) and keep `make app` (dev).
5. Hugging Face Space: list every manual step I must do on huggingface.co (SDK Docker, port, secrets none).
Acceptance: `docker build` and `docker run -p 7860:7860` show the full app at http://localhost:7860 including demo mode; refresh on #/results?sample=botched works; no third-party requests.
Note for the team: the Space runs on CPU. Member B must confirm analyze() works without a GPU.
```

### D17: Favicon, metadata, deep links and README visuals (Day 7)
```
Task D17: Finishing touches. Sections: DESIGN_SYSTEM.md section 8.
Create favicon.svg (the three-bar logo mark, rounded, palette colours, flat), page title and meta description (plain, no buzzwords), theme-color meta set to the paper colour, an Open Graph image description (static image generated from the banner design, flat), a 404/unknown route fallback that returns to the landing, and a "?demo" helper to open sample results.
Create docs/design/screenshots/ with a script (app/scripts/screenshots.mjs, using Playwright if allowed, otherwise instructions for manual capture) that saves: landing, input card with a file chosen, loading, results top, flaw selected with math open, and a phone view, each at 1440 and 390px.
Update README.md (Member C owns it) with the two best screenshots and the live link placeholder.
Acceptance: browser tab shows the favicon and a sensible title; screenshots exist and look consistent with the design files.
```

---

## 3. Bonus prompts (only before the Day 6 freeze, only if the core is finished)

### B1: Severity filter
```
Task B1: Severity filter (display only). Add a segmented control above the flaw list: All / Moderate and up / Major only. It filters which flaws are shown in the list, regions, ribbon outlines and chart regions; it does not change any analysis. Persist the choice in the URL hash params. Counts in the heading reflect the filter ("2 of 5 shown").
Acceptance: switching filters updates every panel consistently with a calm transition (M22).
```

### B2: Download JSON and print view
```
Task B2: "Download JSON" (a secondary pill in ResultsHeader that saves the exact result received) and a print stylesheet that lays out the results on A4: score, radar, flaw list with explanations, no waveform interactions, no animations, readable at black and white. 
Acceptance: Print preview looks like a tidy one- or two-page report.
```

### B3: Record in the browser (needs backend agreement)
```
Task B3: Record tab. Before writing code, ask Member B whether load_audio can decode webm/opus (needs ffmpeg in Docker); if not, stop. Add a third tab "Record" in InputCard using MediaRecorder: permission prompt with a friendly explanation, a round record button with an elapsed timer and a level meter of rounded bars, stop, replay, discard, use recording. Treat the result like an uploaded file (same validation).
Acceptance: record, review and analyze a 15-second clip on desktop Chrome and on a phone. Handle denied permission gracefully.
```
(A/B playback of baseline and participant needs baseline audio from the API, which is a contract change; skip unless all four members agree.)

---

## 4. Repair prompts (when the AI gets it wrong)

### R1: Visual self-check (use after any visual task; attach screenshots at 1440 and 390 px)
```
Here are screenshots of what you built (1440px and 390px). Compare them against docs/design/DESIGN_SYSTEM.md and COMPONENTS.md for this component.
Produce a table: issue, which rule or section it breaks, severity, exact fix. Check especially: any blue/purple, any gradient, any corner under 8px, font fallbacks, spacing rhythm, alignment of time-based panels, copy tone, missing states.
Then fix ONLY the issues in the table. Do not change anything else. Show the screenshots again after the fix if you can run the app.
```

### R2: "It looks AI-generated"
```
This looks like a generic AI-generated template. Compare it with the attached reference screenshots and the anti-AI checklist in DESIGN_SYSTEM.md section 13. List which checklist lines fail and why it feels generic (for example identical cards, centred everything, heavy borders, default shadows, generic copy). Propose specific changes using only our tokens and components (asymmetry, tinted panels instead of borders, bigger type contrast, specific copy, rounder shapes). Wait for my approval before changing code.
```

### R3: Chart problems
```
The chart is wrong: <describe: misaligned with waveform / line crosses gaps / tooltip misplaced / resize breaks / crosshair out of sync>. Do not rewrite the component. First print the scale domains and ranges, the container width and the first five points the chart receives. Explain the cause in plain words, then make the smallest fix. Remember: all time-based panels share the same inner width and padding, y labels are inset, null values must break lines.
```

### R4: Waveform or audio problems
```
The waveform or audio misbehaves: <describe: no sound / waveform empty / regions in the wrong place / playhead jumps / works on Chrome not Safari>. Check in this order and report what you find for each: (1) does the audio URL load (Network tab status and content type), (2) does decodeAudioData succeed (console), (3) is the waveform container width zero at creation, (4) are region percentages computed from meta.duration_s versus the real audio duration (show both numbers), (5) are canvas colours resolved hex strings and not var(...). Then fix the smallest thing.
```

### R5: Janky animation
```
The animation <name/where> is janky. Record a Chrome Performance profile of it and tell me: which property is animating, whether layout or paint is triggered, and the longest task. Fix it using only transform/opacity/stroke-dashoffset, move per-frame updates out of React state into refs and rAF, and respect the MOTION.md durations. Do not add libraries.
```

### R6: Layout overflow or shift
```
There is a layout problem at <width>: <horizontal scroll / overlapping / cumulative layout shift>. Find the element that overflows (print the offending element's scrollWidth versus clientWidth or use the DevTools layout shift regions), explain why, and fix with the smallest CSS change (min-width: 0 on grid children, overflow handling, reserved heights). Do not add fixed widths to hide it.
```

### R7: State sync bugs (selection, playhead, hover)
```
Selection/playhead/hover are out of sync: <describe>. Map the data flow: who writes selectedFlawId, who writes playStore time, who reads them. Find the component that breaks the single source of truth (local state duplicates, effects that fight each other). Fix by removing the duplicate, not by adding another sync effect. Keep playback time out of React state.
```

### R8: Works on mock, fails on real data
```
It works with mock_result.json but fails with real API data: <describe>. List every assumption the UI makes about the data (non-null pitch, at least one flaw, series length, flaws sorted, words count, long durations, extra or missing fields, unknown flaw types, NaN as null). Test each with a crafted JSON in the console or a unit test and show which assumption broke. Fix the UI to handle it gracefully. If the data violates the contract, do not work around it: write the mismatch in docs/HANDOFF.md under Requests for Member B.
```

### R9: Bundle size and speed
```
Run `npm run build` and report the size of each chunk. Find the biggest contributors (use a bundle visualiser only temporarily). Propose lazy-loading for the results view (wavesurfer and chart code) and for the styleguide route, remove unused dependencies, and confirm fonts are subset to the weights we use. Keep the first load of the landing page small. Do not change behaviour.
```

---

## 5. Quality prompts

### Q1: Design audit (Day 7; attach screenshots at 1440, 768, 390 px for landing and results, plus the two reference PNGs)
Use a different AI model from the one that built the UI.
```
You are a strict design reviewer. Read docs/design/DESIGN_SYSTEM.md (especially section 3 hard rules and section 13 checklist). Compare my screenshots with the two reference screenshots.
Output:
1. A table of checklist lines 1-24 with PASS or FAIL and one-sentence evidence from the screenshots.
2. The ten most valuable fixes, ranked, each with the exact token, radius, spacing or copy change.
3. A verdict on whether the pages belong to the same visual family as the references (airy, round, flat, confident type) and what is missing if not.
4. Any place that still looks like a generic AI template.
Do not praise. Be specific.
```

### Q2: Accessibility audit
```
I ran Lighthouse and axe on the landing and results pages. Results: <PASTE>. Map every failure to a component and give the minimal fix using our tokens. Also review these manually and report: keyboard path through the whole product, focus visibility, screen-reader names for regions and charts, colour contrast pairs from tokens.css (compute the ratios), and reduced-motion behaviour.
```

### Q3: Performance audit
```
I ran Lighthouse (Performance) and a Chrome Performance profile of the results reveal. Results: <PASTE>. Identify the top three causes of slowness or jank, with evidence from the profile, and propose minimal fixes (lazy loading, memoisation, moving updates to refs and rAF, fewer SVG nodes). Do not change visuals.
```

### Q4: Stranger test (human, milestone M2, Day 5)
Do this yourself, no AI needed.
1. Find someone who has never seen the project. Open the app, click **Botched**. Say nothing.
2. Give them 60 seconds. Then ask four questions and write down their words:
   - What went wrong with this speech?
   - Where (at what time) did it go wrong?
   - What would you change?
   - How bad was it overall?
3. Pass = they answer all four correctly without help. Anything they could not answer is a design bug: write it in `docs/HANDOFF.md` and fix with R1/R2.
4. Repeat with the **Almost perfect** demo: can they find the single slip?

### V1: Demo recording script (Day 9)
```
Write a 4-minute screen-recording script for the dashboard demo (Member C records the dashboard segment and narrations). Use only the real UI states: landing page, uploading a botched recording with its transcript, the loading card, results summary (score ring, radar), clicking a flaw (waveform region, explanation card, "Show the math"), the charts with the crosshair, the word ribbon and transcript, then the almost-perfect sample (what is and isn't caught), then a real human recording. For each step give: what to click, what to say (plain spoken English, no buzzwords, 20-35 words), and how long it takes. Use only facts visible on screen or in docs/design and results/*; mark anything unverified as [TODO]. End with a 20-second closing line pointing to the repo and the dataset.
```

---
## 6. Plan-driven additions (2026-10-06; need CONTRACTS v1.1 approved first)

### D18: Mode label and no-reference explanation (task C5)
```
Task D18: Show which mode ran. Sections: COMPONENTS.md sections 4, 9 (results header); CONTRACTS.md section 6 (`meta.mode`, `meta.mode_label`).
In the InputCard Select, keep Auto-detect / each baseline / Other speech. In ResultsHeader show a small pill with `meta.mode_label`. When `meta.mode === "prior"` also show one plain sentence under the score: "No-reference mode: we compared your delivery with typical good speakers, not with a reading of this exact text, so we only report objective problems." Use the design tokens, no new colours, no icons-in-squares.
If `mode_label` is missing (old API), derive the label from `meta.mode` in lib/format.js. No analysis math in JS.
Acceptance: botched/almost/ideal show "Reference mode"; the `unseen` demo shows "No-reference mode" plus the sentence; works at 390px; lint:design passes.
```

### D19: Confidence and deviation on flaw cards (task C5)
```
Task D19: Extend FlawList, ExplanationCard and MathDisclosure with the plan's fields. Each flaw shows type, time range, severity pill, and, when present, confidence (as "Confidence 88%", rounded) and deviation (`evidence.deviation_pct`, e.g. "+43.9% vs reference"). In "Show the math" add rows for observed, baseline, deviation %, z and (if present) confidence. If `confidence` is null or absent, show nothing (no placeholder). Clicking a flaw still jumps the audio to its start (already built in D9a).
Acceptance: mock flaws with and without confidence both render cleanly; no layout shift; keyboard and screen reader labels include the confidence.
```

### D20: `unseen` demo preset (tasks C5, D10)
```
Task D20: Add an `unseen` preset to scripts/make_mock_result.py (mode "prior", mode_label "No-reference mode", 2 flaws such as PACE_FAST and PAUSE_EXCESS, one warning that the baseline is pooled, emphasis score null). Generate app/public/demo/unseen.json and demo-audio/unseen.wav. Add a fourth sample card ("A new text") only if it fits the design (SampleCards currently has three). Update deep links to accept sample=unseen.
Acceptance: deterministic output (two runs identical); validator passes; the UI shows the null emphasis dimension as an em dash (already specified in D5).
```

### D21: Processing stages (task C4/D4, only if the API reports them)
```
Task D21: If the API can stream or poll real stages, show them in LoadingCard in order: checking transcript, aligning words, measuring voice, comparing with the baseline, writing explanations. If the API cannot report stages, keep the current honest generic copy. Never show fake percentages. Coordinate with Member B before assuming any endpoint.
```
