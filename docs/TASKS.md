# TASKS.md: Task board (IDs, acceptance criteria)

Rules: tick `[x]` only your own task, only after its acceptance criteria are verified by RUNNING things. One task = one branch = one pull request. Task IDs are used in prompts and commit messages.
Branch names: `a/<task-id>-short-name`, `b/...`, `c/...`. Commit format: `<area>: <what> (task A2)`.

Legend: **[A]** Data, **[B]** Pipeline, **[C]** App/Platform. "Needs" lists what must exist first.

---
## Day 1: Foundations
- [x] **C1 [C] Repo scaffold, design foundation and mock data.** Needs: nothing. Prompts: C1 from `docs/PROMPTS.md`, then D0a and D0 from `docs/DASHBOARD_PROMPTS.md`.
  Do: folder structure, `.gitignore`, `requirements.txt` (pinned), `Makefile` (setup/test/check/smoke/app/lint:design), FastAPI app with `/health`, Vite+React (JavaScript) skeleton with CSS Modules, `scripts/make_mock_result.py` generating contract-valid mock JSON for 3 presets (botched/almost/ideal) plus demo WAVs, `app/src/styles/tokens.css` + `base.css` + `motion.css` (exact copies from design system), `app/src/lib/colors.js` + `format.js` + `motion.js`, design linter (`app/scripts/check-design.mjs` via `npm run lint:design`), `/#/styleguide` page showing palette/type/buttons/chips/radii/shadows/motion demos, `tests/test_health.py`.
  Accept: fresh clone then `make setup && make check` passes; `make app` shows a page that loads mock JSON; `npm run lint:design` passes; `/#/styleguide` renders correctly; mock data is deterministic (two runs give identical files).
- [x] **A1 [A] Texts and sources.** Needs: nothing.
  Do: finalize T1-T6 text files in `dataset/texts/` (exact spoken wording, punctuation kept), `dataset/SOURCES.md` (URL, license, notes per text), download source audio for historical texts, `scripts/prepare_audio.py` (ffmpeg convert to 16 kHz mono WAV, trim to <=1 s edge silence, print duration and peak level).
  Accept: >= 3 prepared source WAVs in `data/interim/`; every text has a transcript and a SOURCES entry.
- [x] **B1 [B] Transcript parsing and forced alignment.** Needs: a sample wav + text (use any 10 s recording).
  Do: `audio/io.py`, `align/transcript.py`, `align/aligner.py`, CLI `python -m speechcoach.align.run`, caching by content hash, tests for `parse_transcript`.
  Accept: CLI prints and saves a valid Alignment JSON (CONTRACTS section 2); word starts are non-decreasing; test passes.
- [ ] **ALL: record ideal T4 (Gitanjali 35)**, 3 takes each, Day 1 evening (see guide for recording protocol).

## Day 2: Features and first flaw
- [x] **A2 [A] WORLD analysis, time-program renderer, first flaw.** Needs: A1.
  Do: `dataset/world_engine.py` with `analyze_world`, `render`, anchors-based time map, `inject` for PACE_FAST L1-L5 on T4 using `configs/flaws.yaml`; `resynth_control`; `scripts/validate_labels.py`; build `dataset/sample/` (1 ideal + 1 flawed + label + transcript).
  Accept: 5 PACE_FAST files + control for T4 with labels passing `validate_labels.py`; A listened to L1, L3, L5; word times in labels consistent with the time map.

- [x] **B2 [B] Frame features, word table, syllables.** Needs: B1.
  Do: `features/frame.py`, `features/words.py` (`word_table`), syllable counter (cmudict + fallback), `scripts/plot_features.py` (figure: pitch, energy, pauses over time), tests with a 150 Hz sine (F0 ~150 +/- 2 Hz), a known-gap signal (pause length error < 20 ms), two synthetic speakers with different base pitch giving equal normalized `st`.
  Accept: `make test` passes; figure produced for one real file and shown to the team.
- [x] **C2 [C] Dashboard v0 on mock data.** Needs: C1. Prompts: D1, D6, D8, D9a from `docs/DASHBOARD_PROMPTS.md`.
  Do: App shell (Nav, state machine, API client with mock mode), waveform panel (wavesurfer.js v7, audio only) with our own region overlay layer (NOT the Regions plugin, lane assignment via `lib/lanes.js`), three stacked custom SVG charts (d3-scale, d3-shape; pitch/loudness/rate with baseline band and flaw regions as rounded rects), flaw list with selection behaviour, upload form posting to `/analyze` (stub returns mock).
  Accept: opening the page shows all of that from `mock_result.json`; clicking a region selects the flaw and plays the segment; overlapping flaws render in lanes; `npm run build` and `npm run lint:design` pass.
- [ ] **ALL: record ideal T5 and T6**, 3 takes each.

## Day 3: Engine complete, baseline and calibration
- [ ] **A3 [A] Full flaw engine and batch build.** Needs: A2.
  Do: all flaw types and levels per FLAW_SPEC, composites, `build_dataset.py` (skip-existing, `--workers`), `results/gradient_check.png` (measured deviation per level per flaw), run for T4 and T1 first.
  Accept: ~48 files per text generated for T4 and T1; gradient plot rises monotonically per flaw; validation passes.
- [x] **B3 [B] Window stats, baseline, signals, calibration.** Needs: B2 and >= 2 ideal recordings of T4 aligned.
  Do: `window_stats`, `build_baseline`, `signals`, `calibrate` + `scripts/calibrate.py` writing `configs/sigma.json`; tests for `signals` (sped-up clip gives negative pace signal with correct magnitude).
  Accept: sigma values printed per signal and look sane (no zeros, no NaN); tests pass.
- [ ] **C3 [C] UI completion with mock data.** Needs: C2. Prompts: D9b, D5, D7 from `docs/DASHBOARD_PROMPTS.md`.
  Do: ExplanationCard with "Show the math" (MathDisclosure, grid-rows accordion), ScoreCard (SVG ring with count-up, 7 dimension chips), RadarCard (SVG radar with polygon draw-in, list fallback below 420 px), WordRibbon (severity ramp colours, aligned with waveform), TranscriptPanel (click to seek, playback highlight via rAF), ResultsHeader, loading and error states (LoadingCard with honest bars, ErrorBanner with mapping table), pydantic response models, `/baselines` stub, Docker skeleton that builds.
  Accept: all UI parts render from mock JSON; `docker build` succeeds; `npm run lint:design` passes.
- [ ] **ALL: record ideal T1 and T3**; A and one teammate start human flawed takes (cards A-G) for T4.

## Day 4: Detection v1 and first integration
- [ ] **A4 [A] Full synthetic build, metadata, splits, human labels.** Needs: A3.
  Do: build all 6 texts; `metadata.csv`; dev/test split fields; `scripts/audacity_to_labels.py` (Audacity label txt to label JSON); QC log (listening notes).
  Accept: `validate_labels.py` passes on everything; counts per text/flaw/level in HANDOFF.
- [ ] **B4 [B] Region detection, typing, `analyze()`, eval v1.** Needs: B3.
  Do: `compare/regions.py`, flaw typing per ARCHITECTURE section 5, `analyze.py` returning a contract-valid dict (explanations may be placeholders), `scripts/run_eval.py --split dev` writing `results/metrics_dev.csv` (precision/recall/F1 at IoU 0.5, boundary error, recall by level).
  Accept: eval runs on dev; first numbers recorded in HANDOFF (even if poor); failure examples listed.
- [ ] **C4 [C] Real integration.** Needs: B4 (or B's draft of `analyze()`). Prompts: D11, D4 from `docs/DASHBOARD_PROMPTS.md`.
  Do: `/analyze` calls real `analyze()`, result caching by hash, upload end-to-end, LoadingCard and ErrorBanner with all error mappings, warnings banner for `meta.warnings`.
  Accept: upload a flawed T4 file in the browser and see real flagged regions; friendly errors for bad inputs; `npm run lint:design` passes. **Milestone M1.**

## Day 5: Explanations, scoring, tuning
- [ ] **A5 [A] QC fixes, human set, listener test.** Needs: A4.
  Do: fix issues found in QC; at least 8 labeled human recordings (mix of flaw cards, incl. 2 "almost perfect"); Google Form listener-test material (5 versions of 3 clips); script to compute rank correlation from responses; dataset card draft.
  Accept: human labels validated; listener form sent.
- [ ] **B5 [B] Tuning, explanations, scoring.** Needs: B4.
  Do: tune `tau_flag`, `tau_trim`, window size on DEV only; explanation templates for every flaw type (5 fields, real numbers); `scoring/rubric.py` per ARCHITECTURE section 7; score-vs-level plot.
  Accept: every detected flaw has all 5 explanation fields; score correlation with severity reported (dev); settings frozen in config with a note in HANDOFF.
- [ ] **C5 [C] Landing page and demo mode.** Needs: C4. Prompts: D2, D3, D10, Q4 from `docs/DASHBOARD_PROMPTS.md`.
  Do: Landing hero and InputCard (segmented tabs, drop zone, custom Select, validation), HeroBanner (animated waveform bars, floating chips, caption), SampleCards (3 demo entry points), "How it works" section, Footer, demo mode end-to-end (`/demo/{name}` + `/demo-audio/{name}.wav`), deep links (`#/results?sample=botched`).
  Accept: demo buttons work without any upload; stranger test (Q4) passes; landing page matches the Maestra/Clideo reference family. **Milestone M2.**

## Day 6: Hard cases and FEATURE FREEZE
- [ ] **A6 [A] Extra humans, final labels, alignment sanity, draft upload.** Needs: A5.
  Do: more human takes incl. held-out speaker for test; final labels and splits; script comparing re-aligned word times vs ground truth on flawed files (median error); draft upload to Hugging Face.
  Accept: numbers in HANDOFF; dataset visible on HF (private is fine for now).
- [ ] **B6 [B] Fillers, Mode B, test run, speaker-agnostic experiment.** Needs: B5.
  Do: filled-pause detector; Mode B (pooled prior baseline); single TEST-split run (no tuning after); male-vs-female (or two-voice) comparison figure.
  Accept: `results/metrics_test.csv`, figures saved, honest numbers in HANDOFF.
- [ ] **C6 [C] Responsive, motion and accessibility polish.** Needs: C5. Prompts: D12, D13, D14 from `docs/DASHBOARD_PROMPTS.md`.
  Do: responsive pass at 1440/1024/768/390 px (MiniPlayer on phone, scroll-snap flaw cards, radar→bars below 420 px), motion audit against MOTION.md catalogue (all 34 motions), accessibility pass (Lighthouse ≥95, keyboard-only flow, visible focus, aria-labels, contrast, reduced motion), large-file handling.
  Accept: bad inputs give friendly errors; UI usable on a phone; Lighthouse accessibility ≥95; no animation outside the catalogue; `npm run lint:design` passes. **FEATURE FREEZE tonight.** Tag `v0.9-freeze`.

## Day 7: Package and publish
- [ ] **A7 [A] Final dataset publish.** Do: upload to Hugging Face dataset + public Drive mirror; final dataset card; `download_dataset.sh` tested on a clean machine. Accept: links in README work from a logged-out browser.
- [ ] **B7 [B] Final results and reproducibility.** Do: final tables/figures in `results/`; two-run hash-equality test; extra unit tests for critical functions. Accept: `make eval` regenerates the tables; hashes equal.
- [ ] **C7 [C] Docker, deploy, README v1.** Prompts: D16, D17, Q1 from `docs/DASHBOARD_PROMPTS.md`.
  Do: production build (`npm run build` with hashed assets), FastAPI serves `app/dist`, Dockerfile frontend stage, `make app-prod`, favicon.svg (three-bar logo), meta tags, design audit (Q1 with screenshots at 3 widths vs references), deploy to Hugging Face Spaces.
  Accept: public URL works on phone and another laptop; `make check` passes inside Docker; no external network requests at runtime; design audit table is all-pass.

## Day 8: Polish and documentation
- [ ] **A8 [A]** Technical-doc page 2 (dataset construction, gradient, QC, listener test) with figures; record data-collection footage.
- [ ] **B8 [B]** Technical-doc pages 3-6 content (features with formulas, method, scoring, results, limitations) with figures.
- [ ] **C8 [C]** Dashboard polish (bugs only, no new features, use R-prompts from `docs/DASHBOARD_PROMPTS.md` as needed); doc page 1 and assembly to ≤ 6 pages; video script (V1 prompt).

## Day 9: Document and video
- [ ] **A9 [A]** Review README and dataset links as a stranger; narrate the data part of the video.
- [ ] **B9 [B]** Fresh-clone test on a DIFFERENT laptop from scratch; narrate the pipeline part.
- [ ] **C9 [C]** Record dashboard demo (V1 prompt from `docs/DASHBOARD_PROMPTS.md`); edit the video (3-10 min); export final PDF doc.

## Day 10: Buffer and submit
- [ ] **ALL:** upload video early, final link check (GitHub, dataset, Space awake, video), submit hours before the deadline. Bug fixes only.
