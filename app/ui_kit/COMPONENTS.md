# COMPONENTS.md: Layouts and component specs for the dashboard

Read with `DESIGN_SYSTEM.md` (look) and `MOTION.md` (movement). Data shapes come from `docs/CONTRACTS.md` section 6; **if this file and CONTRACTS.md disagree, CONTRACTS.md wins.**

The frontend renders data. It never computes pitch, pace, z-scores, severity or scores. Allowed in JS: scales, formatting, sorting for display, lane assignment for overlapping regions, simple display labels from a score.

---

## 0. Stack and folders (frontend)
Allowed packages (anything else needs team approval): `react`, `react-dom`, `d3-scale`, `d3-shape`, `d3-array`, `wavesurfer.js` (v7), `lucide-react`, `motion` (optional, only for presence animations), `@fontsource-variable/bricolage-grotesque`, `@fontsource-variable/dm-sans`, `@fontsource/ibm-plex-mono`. Styling: plain CSS with the tokens plus CSS Modules (no Tailwind, no UI kit, no Plotly). JavaScript with JSDoc types.

```
app/
  index.html  vite.config.js  package.json
  public/  mock_result.json  demo/ (ideal.json, almost.json, botched.json)  demo-audio/ (*.wav)  favicon.svg
  src/
    main.jsx  App.jsx  types.js
    styles/  tokens.css  base.css  motion.css
    api/     client.js
    state/   useAnalysis.js  SelectionContext.jsx  playStore.js
    lib/     colors.js  format.js  motion.js  lanes.js
    components/
      Nav/  Hero/  InputCard/  Select/  HeroBanner/  SampleCards/  LoadingCard/  ErrorBanner/
      Results/  ResultsHeader/  ScoreCard/  RadarCard/  WaveformPanel/  WordRibbon/  TranscriptPanel/
                ChartStack/  TimeChart/  FlawList/  ExplanationCard/  MathDisclosure/  MiniPlayer/
      Styleguide/
```

## 0.1 Data cheat-sheet (what the UI reads)
```
meta:   { mode: "reference"|"prior", baseline_id, duration_s, version, warnings: [string] }
words:  [{ i, w, start, end, punct, conf, z: { pace, pause, pitch, energy, clarity } }]
series: { t: [..20 Hz..],
          participant: { pitch_st: [number|null], energy_db: [], rate_sps: [] },
          baseline:    { pitch_st, pitch_lo, pitch_hi, energy_db, rate_sps } }
flaws:  [{ id, type, start, end, first_word, last_word, severity (0-1), band: "minor"|"moderate"|"major",
           evidence: { participant, baseline, z, unit },
           explanation: { observed, deviation, where, why, fix } }]
scores: { overall (0-100), dimensions: { pacing, pausing, pitch, energy, emphasis, clarity, fluency } }
```
API: `GET /health`, `GET /baselines`, `POST /analyze` (multipart `audio`, `transcript`, `baseline_id?`, `mode`), `GET /demo/{name}` (`ideal|almost|botched`), plus the frontend-only convention `GET /demo-audio/{name}.wav` for the demo audio.

## 0.2 Shared lookups (`lib/colors.js`, copy exactly)
```js
export const DIMENSIONS = {
  pacing:   { label: "Pacing",   color: "var(--c-pacing)",   tint: "var(--c-pacing-tint)",   icon: "Gauge" },
  pausing:  { label: "Pausing",  color: "var(--c-pausing)",  tint: "var(--c-pausing-tint)",  icon: "Pause" },
  pitch:    { label: "Pitch",    color: "var(--c-pitch)",    tint: "var(--c-pitch-tint)",    icon: "Activity" },
  energy:   { label: "Loudness", color: "var(--c-energy)",   tint: "var(--c-energy-tint)",   icon: "Volume2" },
  emphasis: { label: "Emphasis", color: "var(--c-emphasis)", tint: "var(--c-emphasis-tint)", icon: "Target" },
  clarity:  { label: "Clarity",  color: "var(--c-clarity)",  tint: "var(--c-clarity-tint)",  icon: "Ear" },
  fluency:  { label: "Fluency",  color: "var(--c-fluency)",  tint: "var(--c-fluency-tint)",  icon: "Mic" },
};
export const FLAW_TYPES = {
  PACE_FAST:       { dimension: "pacing",   label: "Rushing" },
  PACE_SLOW:       { dimension: "pacing",   label: "Dragging" },
  PAUSE_MISSING:   { dimension: "pausing",  label: "Missing pause" },
  PAUSE_EXCESS:    { dimension: "pausing",  label: "Overlong pause" },
  PAUSE_MISPLACED: { dimension: "pausing",  label: "Awkward pause" },
  MONOTONE:        { dimension: "pitch",    label: "Flat pitch" },
  PITCH_ERRATIC:   { dimension: "pitch",    label: "Wobbly pitch" },
  VOLUME_DROP:     { dimension: "energy",   label: "Volume drop" },
  FLAT_ENERGY:     { dimension: "energy",   label: "Flat loudness" },
  STRESS_MISSING:  { dimension: "emphasis", label: "Missing emphasis" },
  CLARITY:         { dimension: "clarity",  label: "Mumbling" },
  FILLERS:         { dimension: "fluency",  label: "Filler sounds" },
};
export const BANDS = { minor: "Minor", moderate: "Moderate", major: "Major" };
// Unknown types must still render: fall back to { dimension: "pacing", label: type }.
```
Display-only helpers in `lib/format.js`: `fmtTime(s)` → `m:ss.s`; `fmtNum(x, d=1)` with the proper minus sign; `scoreLabel(score)` → "Strong delivery" (≥ 85), "Good, with a few things to fix" (70-84), "Needs work" (50-69), "Major problems" (< 50) (display wording only, comment it as such); `wordBand(z)` → fine / minor / moderate / major by `max |z|` with cut-offs 2, 3, 4.5.

---

## 1. Page layouts

### 1.1 Landing (desktop ≥ 960 px)
```
┌──────────────────────────────────────────────────────────────────────────┐
│ [logo] SpeechCoach     How it works   Dataset   GitHub        ( Try a sample ) │  Nav (pill button)
│                                                                          │
│              See exactly where your speech goes wrong.                   │  H1 display-xl, centred
│     Upload a recording and its text. We compare your delivery with a     │  one grey sentence
│     strong reference and point to the exact seconds that need work.      │
│                                                                          │
│   ╭────────────────────────────────────────────────────────────────╮    │
│   │   ( Analyze a recording | Try a sample )      segmented tabs   │    │  InputCard (radius 40)
│   │  ╭┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈╮   │    │
│   │  ┆        (↑)  Drop your recording here                  ┆   │    │  dashed mint drop zone
│   │  ┆        WAV, MP3, M4A, FLAC or OGG · up to 25 MB       ┆   │    │
│   │  ┆             ( Choose a file )     or try a sample     ┆   │    │
│   │  ╰┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈╯   │    │
│   │  Which speech is this? [ Auto-detect ▾ ]                       │    │
│   │  Transcript  [ paste the exact words that were spoken…      ]  │    │
│   │                                            ( Analyze )         │    │
│   ╰────────────────────────────────────────────────────────────────╯    │
│       ✓ Pinpoints the exact seconds  ✓ Explains each flaw with numbers  ✓ Free to try │
│                                                                          │
│   ╭──────────────── mint HeroBanner ────────────────────────────────╮   │
│   │  ▂▃▅▇▅▃▂▃▆█▆▃▂▂▃▅▇▅▃▂▃▅  (animated bars)      ◖ Flat pitch 0:07 ◗ │   │  floating chips
│   │  Where the mind is without fear and the head is held high        │   │  caption, flawed words marked
│   ╰──────────────────────────────────────────────────────────────────╯   │
│   Try a sample:  [ Ideal ]  [ Almost perfect ]  [ Botched ]  (SampleCards)│
│   How it works (3 steps, one row, not identical boxes)                   │
│   footer                                                                 │
└──────────────────────────────────────────────────────────────────────────┘
```
Phone: single column; the banner sits under the card; sample cards stack; nav collapses to logo + pill button.

### 1.2 Results (desktop)
```
 [Nav]
 ResultsHeader:  ( ← Analyze another )   file name · duration · "Compared with: <title>"          ( Download JSON )
 ┌───────────────────── ScoreCard (wide) ─────────────────────┬──────── RadarCard ────────┐
 │  (ring 72)  Strong delivery / Needs work                    │        7-axis radar       │
 │  7 dimension chips with mini bars                           │                           │
 └─────────────────────────────────────────────────────────────┴───────────────────────────┘
 ┌──────────── left (8 cols) ───────────────────────────┬──── right (4 cols, sticky) ─────┐
 │ WaveformPanel  (play button, time, prev/next flaw)   │ FlawList  "3 things to work on" │
 │   flaw regions overlay (rounded, lanes)              │   card · card · card            │
 │ WordRibbon (colour by deviation)                     │ ExplanationCard                 │
 │ ChartStack: Pitch / Loudness / Speaking rate         │   what · how far · where · why  │
 │ TranscriptPanel (click a word to seek)               │   · fix · Show the math         │
 └──────────────────────────────────────────────────────┴─────────────────────────────────┘
```
Phone: header → ScoreCard → Radar → WaveformPanel + ribbon → FlawList (horizontal swipe cards) → ExplanationCard → Charts → Transcript. A sticky **MiniPlayer** bar at the bottom appears once the waveform scrolls out of view.

**Alignment rule:** WaveformPanel, WordRibbon and every TimeChart use the same inner width and the same left/right padding (24 px), so a given second sits at the same x in all of them.

---

## 2. Global state
- `useAnalysis` (reducer): `status: "idle" | "loading" | "success" | "error"`, `result`, `error {kind, message}`, `audioUrl`, `fileName`, `elapsed`, `abort()`.
- `SelectionContext`: `selectedFlawId`, `hoverTime` (low frequency; fine for React state).
- `playStore` (tiny external store with `subscribe/getTime/setTime`): current playback time, updated by wavesurfer; components read it via refs and rAF, **not** via React state.
- Flaw ↔ words: `first_word..last_word` highlights words in the ribbon and transcript.

---

## 3. Navigation: `Nav`
Logo mark (three rounded bars) + wordmark; links "How it works" (scroll), "Dataset" and "GitHub" (external placeholders from a `links.js`); right: primary pill "Try a sample" (scrolls to SampleCards or loads the botched demo). Height 72. On scroll > 8 px the bottom hairline and soft shadow fade in (M2). Phone: logo + pill only.

## 4. `Hero`
H1 (display-xl, centred, max width about 14 words) and one grey sentence (18 px `--muted`, max 60 ch). Suggested copy: **"See exactly where your speech goes wrong."** / "Upload a recording and its text. We compare your delivery with a strong reference and point to the exact seconds that need work." Entrance: M1.

## 5. `InputCard`
**Container:** white, radius 40, padding 28-32, `--shadow-2`, max width 880, centred.
**Segmented tabs:** "Analyze a recording" / "Try a sample". Pill container `--paper-2`; sliding white indicator (M6). Tab 2 shows the SampleCards content inside the card.
**Drop zone:** radius 28, `--mint`, 2 px dashed `--dash`, min-height 220. Content: 56 px white circle with `Upload` icon; title "Drop your recording here"; helper "WAV, MP3, M4A, FLAC or OGG · up to 25 MB"; primary pill "Choose a file"; ghost link "or try a sample" (switches tab). States: idle, hover (M7), drag-over (M8), accepted (file chip: music icon, name, size, duration once read, "Remove" icon button, M10), invalid (M9 + message).
**Which speech is this?** custom `Select` (`GET /baselines`): "Auto-detect" (mode `auto`), each baseline title (mode `reference`, `baseline_id`), "Other speech, no reference (general norms)" (mode `prior`). Helper text under it: "Pick the matching text for the most precise comparison."
**Transcript:** auto-growing textarea, radius 16, placeholder "Paste the exact words that were spoken, with punctuation…", live word count, ghost link "Use the sample transcript" when a baseline is chosen (only if the API/baselines list provides text; otherwise hide it).
**Analyze:** primary pill, disabled until a valid audio file and at least 5 words of transcript exist; helper under it explains what is missing ("Add a recording to continue").
**Validation (client side):** accepted extensions `.wav .mp3 .m4a .flac .ogg .webm`, size ≤ 25 MB, transcript ≥ 5 words. Messages in plain language.
**Reassurance ticks under the card** (3 small check icons): "Pinpoints the exact seconds", "Explains each flaw with numbers", "Free to try".
A11y: the drop zone is a `<label>` + hidden file input and is keyboard operable; the whole form is a real `<form>` with `aria-live` status text.

## 6. `HeroBanner` (inspired by the Clideo banner)
Mint panel, radius 40, height 220 (phone 180), overflow visible so chips can overlap the edge. Inside: a row of about 48 rounded bars (3 px wide, random-but-seeded heights, `--ink-2` for most, a few in tangerine under the flawed phrase) animated with M3. Beneath: the caption "Where the mind is without fear and the head is held high" revealed word by word (M5); the words "without fear" get a tangerine underline drawn in. Two or three floating chips overlapping the panel edges (M4): "Flat pitch · 0:07" (pitch tint), "Rushing +38%" (pacing tint), "Pause too short" (pausing tint). **Decorative: `aria-hidden="true"`.** The numbers on the chips are illustrative, so label the banner "Example" with a small caption ("Example of what we flag").

## 7. `SampleCards` (demo mode entry)
Three cards in a row (desktop) with different widths (for example 5/4/3 columns), radius 28:
- **Ideal** (mint): "A strong reading. See what good looks like."
- **Almost perfect** (butter): "One small slip. Can you spot it?"
- **Botched** (blush): "Rushed, flat and quiet. See how we explain it."
Each has a mini waveform thumbnail (static rounded bars), a duration, and a pill button "Open". Hover M34. Clicking loads `/demo/{name}` and `/demo-audio/{name}.wav` and goes straight to results. No upload is required.

## 8. `LoadingCard` and `ErrorBanner`
**LoadingCard:** centred white card (radius 32): 7 animated rounded bars (M12), title "Analyzing your speech…", an elapsed counter in mono ("12 s"), hint "Longer recordings take a little more time", ghost "Cancel" (AbortController). **No fake step names or fake percentages.** Skeleton panels of the results layout behind it (M33) prevent layout shift.
**ErrorBanner:** radius 20, `--blush`, `AlertCircle` icon, title, one plain sentence, actions ("Try again", "Choose another file"). Mapping:
| Cause | Message |
|---|---|
| HTTP 400 audio unreadable | "We couldn't read that audio file. Try WAV, MP3 or M4A under 25 MB." |
| HTTP 400 transcript | "The transcript looks empty or too short. Paste the words that were spoken." |
| HTTP 413 / over 25 MB | "That file is larger than 25 MB. Trim it or export a smaller version." |
| HTTP 422 | "Something in the form wasn't right. Check the file and transcript, then try again." |
| Network failure | "We can't reach the server. Check your connection and try again." |
| Client timeout (120 s) | "This is taking longer than expected. You can wait, or cancel and try a shorter clip." |
| Response invalid / unexpected | "The server sent something we couldn't read. Please try again, and tell the team if it keeps happening." |
**Warnings:** `meta.warnings` render as a butter banner above the results ("Some words may not match the audio, so timings near them can be less precise.") listing the warning strings in a small expandable list.

## 9. `ResultsHeader`
Ghost pill "← Analyze another", file name (truncate with ellipsis), duration, badge "Compared with: <baseline title>" (mode `reference`) or "Compared with general norms" (mode `prior`), secondary pill "Download JSON" (bonus), M1 entrance.

## 10. `ScoreCard`
White card, radius 28, padding 28. Left: SVG ring (r 54, stroke 12, round caps; track `--paper-2`, progress `--ink`), overall number in display font inside (M14 count-up), under it `scoreLabel` text. Right: seven dimension chips in a wrapping grid: icon in tint circle, name, number in mono, mini rounded bar (height 6) in the dimension colour on `--paper-2` track. Chips stagger (M15). Hovering a chip highlights that dimension's flaws in the list (display only).
If `flaws.length === 0`, the card shows a mint "No flaws crossed the detection threshold" note (honest wording).

## 11. `RadarCard`
White card, radius 28. SVG radar with the seven dimensions in a fixed order (pacing, pausing, pitch, energy, emphasis, clarity, fluency), rings at 25/50/75/100 in `--line`, polygon per the design system, vertex dots, axis labels with the dimension icon and the number. Hover/focus on an axis shows a rounded tooltip with the dimension name and score. Phone: below 420 px replace with a list of seven horizontal bars. M16.

## 12. `WaveformPanel`
White card, radius 28, padding 24.
- **Header row:** title "Your recording", on the right a ghost "Playback speed" pill is optional; skip if tight.
- **Waveform:** wavesurfer v7, height 120 (phone 96), `barWidth 3`, `barGap 3`, `barRadius 3`, unplayed bars `--mint-2`, played bars `--ink`, cursor 2 px `--ink`, `normalize: true`, no zoom, no scroll (the whole clip fits the width). Canvas colours must be **resolved hex strings** (read them from CSS variables with `getComputedStyle`), not `var(...)`. Load the recording from `URL.createObjectURL(file)` or the demo URL. **Do not use the Regions plugin.**
- **Region overlay (our own layer):** an absolutely positioned layer over the waveform. Each flaw is a `<button>` with `left = start/duration`, `width = (end−start)/duration` in percent, rounded (radius 14), fill = dimension colour at 22%, 2 px top edge in the solid colour, a small chip (icon + short label) at the top-left when the region is at least 90 px wide. Overlapping flaws go into lanes (`lib/lanes.js`, greedy assignment) so they never hide each other; each lane is 24-28 px high and the waveform leaves room above. Click or Enter selects the flaw and plays from its start (M24). Hover tooltip with the flaw name and time range. `aria-label` such as "Rushing, 0:42 to 0:51, major".
- **Controls row:** 56 px round play/pause (ink), time `0:12.4 / 0:58.4` (mono), icon buttons "previous flaw" and "next flaw", and a "Play this flaw" action appears in the ExplanationCard. Keyboard: Space, ← → (2 s), `[` `]`.
- **Playhead sync:** wavesurfer `timeupdate`/`audioprocess` writes to `playStore`; other panels read it through refs and rAF.
- **Entrance:** M17 then M18.
- Handles: audio fails to decode (show ErrorBanner variant), very long audio (≥ 5 min) shows a note.

## 13. `WordRibbon`
A 14 px high row directly under the waveform, same inner width. One rounded block (radius 6, 2 px gaps) per word, positioned by time (`left = start/duration`, `width = (end−start)/duration`, minimum 2 px). Colour from the severity ramp using `wordBand(max |z|)`. Hover shows a tooltip: word, time, the largest deviation and its dimension ("pace z = −4.5"). Words inside the selected flaw (`first_word..last_word`) get an ink 2 px outline. M19. Include a tiny legend (four swatches: Fine, Minor, Moderate, Major) and a note that colour shows how far a word is from the reference.

## 14. `TranscriptPanel`
White card, radius 28, "Transcript" title. Words flow as inline spans (radius 8, padding 2 6) tinted by `wordBand`; the word currently playing gets an ink underline; clicking a word seeks to its start; words of the selected flaw are outlined. Punctuation stays attached to words. Long transcripts scroll inside the card (max height 320, thin rounded scrollbar). Search/filter not needed.

## 15. `ChartStack` and `TimeChart`
One white card (radius 28) containing three stacked charts, gap 8, each 150 px high (phone 120), titles "Pitch", "Loudness", "Speaking rate" with a small unit label ("semitones from your usual pitch", "dB below your loudest", "syllables per second") and a one-line "what this shows" help popover.
Implementation: custom SVG with `d3-scale` and `d3-shape` only. One shared `xScale` (0 to `meta.duration_s`), one `yScale` per chart (domain from the data plus 10% padding).
- Participant: path with `line().defined(d => d != null).curve(curveMonotoneX)`; baseline: band via `area()` (pitch only: `pitch_lo` to `pitch_hi`) plus dashed baseline line.
- Flaw regions drawn as `<rect rx="10">` per the design system; the chart whose dimension matches (pitch chart for MONOTONE/PITCH_ERRATIC, loudness chart for VOLUME_DROP/FLAT_ENERGY, rate chart for PACE_*) gets the stronger fill and a chip. Other flaw types (pausing, clarity, fluency, emphasis) show the light fill in all three charts.
- Hover: overlay rect captures the pointer, bisects `series.t`, shows the synced crosshair in all three charts and one tooltip (time, you, reference, difference). Click seeks. The crosshair also follows the playhead (ref + rAF).
- X axis labels (`m:ss`) only under the last chart. Y labels inset over the plot. Horizontal dashed grid only.
- `ResizeObserver` for width; memoise paths; points are about 20 per second so 60 s is 1,200 points per series.
- Empty/short series (fewer than 2 points) show a plain "Not enough data to draw this" panel.
- `role="img"` with an `aria-label` such as "Pitch over time. One flaw region from 0:42 to 0:51."
- M20 (lines draw), M21 (regions grow).

## 16. `FlawList`
Heading "3 things to work on" (the count is the real number; singular/plural handled). Sorted by start time. Each `FlawCard` (radius 20, white, `--shadow-1`, padding 16): 40 px tint circle with the dimension icon, the human flaw label (h3-ish), time range in mono ("0:42.1 – 0:51.3"), a severity pill (Minor/Moderate/Major) and a rounded severity bar (width = `severity`, colour from the ramp). Selected: 2 px ink ring (transition) and `--paper` background; hover lifts (M23). Keyboard: arrow keys move between cards, Enter selects. Selecting also scrolls the matching waveform region into view and pulses it (M24).
Empty state (no flaws): a mint card, `CheckCircle` icon, "No flaws crossed the detection threshold." with a muted line "This doesn't mean the delivery is perfect. Check the scores and charts for smaller differences."
Phone: horizontal scroll-snap row of cards.

## 17. `ExplanationCard`
White card, radius 28, padding 24, sticky under the flaw list on desktop. Header: tint icon circle, flaw label, severity pill, time range. Five labelled blocks in this order, each with a short title and text from the data (never rewrite or invent numbers):
1. **What we measured**: `explanation.observed`
2. **How far off**: `explanation.deviation`
3. **Where**: `explanation.where` plus a secondary pill "Play this part" (plays start→end)
4. **Why it matters**: `explanation.why`
5. **How to fix it**: `explanation.fix`, inside a `--butter` panel (radius 20)
Then **`MathDisclosure`** ("Show the math", M26): a rounded `--paper-2` panel with a small three-column table: "You" / "Reference" / "Difference" using `evidence.participant`, `evidence.baseline`, `evidence.z` and `evidence.unit`; one line explaining: "z compares your difference with how much two strong speakers normally differ. Beyond about 2 it stands out." and the formula in mono: `z = (your value − reference value) ÷ normal spread`. Content swaps with M25. If nothing is selected, show the first (most severe) flaw by default.

## 18. `MiniPlayer` (phone)
Fixed bottom bar, radius 24 with 12 px margin, white, `--shadow-pop`: play/pause circle, time, previous/next flaw. Appears with M32 when the waveform is out of view (IntersectionObserver).

## 19. `Select` (custom dropdown)
Button trigger (radius 16) + listbox menu (radius 20, `--shadow-pop`, max height 280, scrolls). Keyboard: Up/Down, Enter, Esc, type-ahead; `role="combobox"`/`listbox`/`option`; focus returns to the trigger. Opens with `.pop-in`.

## 20. `Toast`
Bottom-centre pill (radius 999), ink background, white text, optional action; M31.

## 21. `Footer`
Small text and links (GitHub, dataset, video, technical document) from `links.js`, credits line "Built for the Multimodal AI Hackathon 2026, Track C". No fake legal text.

## 22. `Styleguide` (`/#/styleguide`)
Renders: palette swatches, flaw colours with icons, type scale, buttons (all states), chips and severity pills, inputs and the custom Select, radii samples, shadows, loader, and small motion demos (reveal, count-up, draw-in). It is the visual test page for the design rules.

## 23. Bonus components (only before the Day 6 freeze, only if everything above is done)
- **Severity filter:** segmented control "All / Moderate and up / Major only", a display filter on `flaws` (does not change analysis).
- **Record tab:** in the input card, a third tab "Record" using `MediaRecorder` (webm). Needs the backend to decode webm; confirm with Member C/B first.
- **Download JSON** and a **print stylesheet** for the results page.
- **A/B playback** of baseline vs participant needs baseline audio from the API, which is a contract change; skip unless the team agrees.
