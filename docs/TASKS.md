# TASKS.md: Task board (IDs, acceptance criteria)

Rules: tick `[x]` only your own task, only after its acceptance criteria are verified by RUNNING things. One task = one branch = one pull request. Task IDs are used in prompts and commit messages.
Branch names: `a/<task-id>-short-name`, `b/...`, `c/...`, `d/...`. Commit format: `<area>: <what> (task A2)`.

Legend: **[A]** Data, **[B]** Pipeline, **[C]** App/Platform. "Needs" lists what must exist first.
Checkboxes: `[x]` done and verified by running, `[~]` partly done or claimed without a HANDOFF entry (verify before relying on it), `[ ]` open. Priority tags: **(M)** must-have, **(S)** should-have, **(X)** stretch; if time runs out, drop X first, then S.

Updated 2026-10-06 (Day 4) to match the Track C build plan: three members, 8 texts, six flaw families, speaker + text splits, stress-test matrix, learned layer (optional), QC and docs tasks. Dates assume Day 1 = 2026-10-03; set the real deadline in `HANDOFF.md` section 1 and move the freeze if it is later.

---
## Status board (2026-10-06, Day 4)
- Done: A1, A2 (no session log, counts show 30 synthetic files), B1, B2, B3, B4, B4b, B5, C1, C2, C3.
- Partly / unverified: **A3** (30 synthetic files exist; remaining types, FLAT_ENERGY, STRESS_*, composites, gradient plot not confirmed), **C4** (ticked earlier, but no HANDOFF entry and M1 not ticked: reproduce a real upload and log it).
- Not started: all D-series tasks (now owned by A), A4-A9, B5b/B5c/B6-B9, C5-C9, all recordings except the 4 originals.
- Biggest risks: (1) detection quality (dev F1 0.065); (2) human recordings not started and they are the long pole (plan used 3 days for 96 takes); (3) Day 6 freeze is two days away; (4) licence of T1-T4 audio. See `HANDOFF.md` section 5.
- Work in parallel TODAY: B on B5b, A on A3, D1 and D2, C on C4 verification then C5.

## Added tasks from the Track C build plan (2026-10-06)
These tasks are new. Day numbers are targets; tasks marked M are on the critical path.

### Detection quality and features (Member B)
- [ ] **B5b [B] (M) Detection quality recovery.** Day 4-5. Needs: B5, some synthetic files.
  Do: (1) run dev eval twice, once with ORACLE word times from the label files and once with the real aligner, and put both F1 values in HANDOFF (separates alignment jitter from detector faults); (2) try wider window `W` (10+) and per-family `tau_flag`, tuned on DEV only; (3) check how many false positives remain on ideal files (FPR per minute) after each change; (4) refine region start/end with word boundaries (plan: boundaries snap to aligned words so the dashboard can name the exact phrase); (5) list the remaining failure examples by family.
  Accept: numbers table (oracle vs real, by level and family) in HANDOFF; F1@IoU0.5 on DEV for L4-L5 at least 0.5 and FPR on ideal <= 1 region/min (targets, adjust honestly if unreachable and write why); settings frozen in config with a note.
- [ ] **B5c [B] (S) Feature completeness for the challenge list.** Day 4-5. Needs: B2.
  Do: add spectral centroid, band-energy ratio, MFCC delta (frame level, additive keys per CONTRACTS v1.1), F0 slope and pause position relative to punctuation (word level); syllable rate and words/s both reported; docs table "feature -> challenge category -> formula" in `docs/methodology.md`; tests with synthetic signals (known tone gives known centroid).
  Accept: `make test` passes; table exists; a plot shows each new feature on one real file.
- [ ] **B6e [B] (S) Emphasis signal (STRESS_MISSING / STRESS_EXAGGERATED).** Day 5-6. Needs: B5b, A3 STRESS files.
  Do: ARCHITECTURE section 4.2; add to regions, explanations (5 fields) and the `emphasis` dimension; until done the emphasis score is `null` with a warning.
  Accept: recall on STRESS_MISSING L3-L5 reported on DEV; explanations real numbers.
- [ ] **B6f [B] (X) Learned window scorer (hybrid).** Day 5-6, only if B5b is done. Needs: B5b, A4.
  Do: ARCHITECTURE section 11, `scripts/train_window_model.py`, speaker-grouped validation, rules-only vs hybrid table, confidence in the result.
  Accept: model file + deterministic output; hybrid kept only if it beats rules-only on validation speakers.

### Data and recording (Member A)
- [ ] **D1 [A] (M) Original texts and roster.** Day 4. Needs: nothing.
  Do: write T5 "Technology and Human Connection", T6 "The Future of Education", T7 "Innovation and Failure", T8 "Building a Better Future" (original, 100-130 words each, plain spoken English, punctuation where a speaker would pause; 45-75 s when read); speaker roster h1-h12 with the split rule from CONTRACTS 0.1; recording sheet (Drive); consent message template; `dataset/SOURCES.md` consent column. A ingests the texts into `dataset/texts/`.
  Accept: 4 text files, each 100-130 words; roster and sheet exist; A has the texts.
- [ ] **D2 [A] (M) Recording pilot.** Day 4-5. Needs: D1.
  Do: one teammate records T5-T8 and one flawed card following `docs/RECORDING_PROTOCOL.md`; check placement, noise, clipping, durations, file handling; B aligns the pilot files.
  Accept: pilot files pass the QC checklist; alignment spot-check done; protocol corrected if anything failed. Do not record the rest before this passes.
- [ ] **D3 [A] (M) Recording sessions: GOOD takes.** Day 5-7 (overlaps the freeze: audio data may keep arriving, code must not wait for it).
  Do: teammate ideals for T1-T4 (at least 2 teammates per text); T5-T8 from all available speakers (target up to 12; core target 6+ including 2 val and 2 test speakers if possible); back up after every session.
  Accept: sheet and `metadata` rows complete; count and speaker split in HANDOFF; raw originals backed up.
- [ ] **D4 [A] (M) QC and listening.** Day 5-7. Needs: D3, A3/A4 outputs.
  Do: QC checklist for every recording; listening check of at least 3 files per flaw type; alignment spot-check (1 per speaker, 3 word boundaries); human flawed takes cards A-J (at least 8) with intended regions; log in `dataset/QC_LOG.md`.
  Accept: QC log complete; fix/regenerate list handed to A.
- [ ] **D5 [A] (S) Listener test.** Day 6-8. Needs: A5 material.
  Do: Google Form with 5 versions of 3 clips; collect at least 10 responses; A's script gives rank correlation between listener ratings and our severity levels.
  Accept: correlation number in HANDOFF for the document.
- [ ] **D6 [A] (M) Docs skeleton in the repo.** Day 6-7 (with a member's laptop). 
  Do: `docs/dataset.md`, `docs/methodology.md`, `docs/scoring.md`, `docs/demo.md`, LICENSE (agree on the licence first; code vs dataset licence), using prompt P14 and real numbers only.
  Accept: files exist, link from README, no invented numbers (`[TODO: number]` allowed until Day 8).
- [ ] **D7 [A] (S) Stress-test documentation.** Day 7-8. Needs: B6/B7 results.
  Do: turn `results/stress_*.csv` into the table and the limitations list for the document (`docs/STRESS_TESTS.md` section 2).
  Accept: every matrix row S1-S13 has a result or an honest "not run, because...".
- [ ] **D8 [A] (M) Technical document <= 6 pages.** Day 8-9. Needs: A8, B8, C8 inputs.
  Do: assemble pages 1-6, say which choices are ours (PROJECT_BRIEF section 9), include the plan's key plots, export PDF, count pages.
  Accept: PDF with at most 6 pages, every number traceable.
- [ ] **D9 [A] (M) Video script and narration.** Day 8-9.
  Do: script following the demo outline (problem 0:40, dataset 0:50, features 1:00, upload+timeline 1:30, click a flaw 1:00, second speaker and unseen text 1:00, stress results 1:00, repo and reproducibility 0:40); coordinate with C9 recording; check the final length is 3-10 minutes.
  Accept: script reviewed by all; video length verified.

---
## Day 1: Foundations
- [x] **C1 [C] Repo scaffold, design foundation and mock data.** Needs: nothing. Prompts: C1 from `docs/PROMPTS.md`, then D0a and D0 from `docs/DASHBOARD_PROMPTS.md`.
  Do: folder structure, `.gitignore`, `requirements.txt` (pinned), `Makefile` (setup/test/check/smoke/app/lint:design), FastAPI app with `/health`, Vite+React (JavaScript) skeleton with CSS Modules, `scripts/make_mock_result.py` generating contract-valid mock JSON for 3 presets (botched/almost/ideal) plus demo WAVs, `app/src/styles/tokens.css` + `base.css` + `motion.css` (exact copies from design system), `app/src/lib/colors.js` + `format.js` + `motion.js`, design linter (`app/scripts/check-design.mjs` via `npm run lint:design`), `/#/styleguide` page showing palette/type/buttons/chips/radii/shadows/motion demos, `tests/test_health.py`.
  Accept: fresh clone then `make setup && make check` passes; `make app` shows a page that loads mock JSON; `npm run lint:design` passes; `/#/styleguide` renders correctly; mock data is deterministic (two runs give identical files).
- [x] **A1 [A] Texts and sources.** Needs: nothing.
  Do: finalize T1-T4 text files in `dataset/texts/` (T5-T8 are written later, task D1) (exact spoken wording, punctuation kept), `dataset/SOURCES.md` (URL, license, notes per text), download source audio for historical texts, `scripts/prepare_audio.py` (ffmpeg convert to 16 kHz mono WAV, trim to <=1 s edge silence, print duration and peak level).
  Accept: >= 3 prepared source WAVs in `data/interim/`; every text has a transcript and a SOURCES entry.
- [x] **B1 [B] Transcript parsing and forced alignment.** Needs: a sample wav + text (use any 10 s recording).
  Do: `audio/io.py`, `align/transcript.py`, `align/aligner.py`, CLI `python -m speechcoach.align.run`, caching by content hash, tests for `parse_transcript`.
  Accept: CLI prints and saves a valid Alignment JSON (CONTRACTS section 2); word starts are non-decreasing; test passes.
- [ ] **ALL: record teammate ideals of T4 (Lincoln)**, at least 2 teammates, protocol in `docs/RECORDING_PROTOCOL.md`. (Old wording said T4 = Gitanjali 35; T4 is now Lincoln, per the HANDOFF decision of 2026-10-03.) Needs: D2 pilot passed.

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
- [ ] **ALL: record ideal T5 and T6** (original texts written in D1), teammates first. Now handled by D3.

## Day 3: Engine complete, baseline and calibration
- [~] **A3 [A] (M) Full flaw engine and batch build.** Needs: A2. Status: 30 synthetic files exist; rest unverified.
  Do: all flaw types and levels per FLAW_SPEC (now 14 types in 6 families, incl. FLAT_ENERGY, STRESS_MISSING, STRESS_EXAGGERATED; ~59 files per text), composites, `build_dataset.py` (skip-existing, `--workers`), `results/gradient_check.png` (measured deviation per level per flaw), run for T4 and T1 first.
  Accept: ~59 files per text generated for T4 and T1; gradient plot rises monotonically per flaw; side-check for unintended flaws reported; validation passes; HANDOFF entry with counts.
- [x] **B3 [B] Window stats, baseline, signals, calibration.** Needs: B2 and >= 2 ideal recordings of T4 aligned.
  Do: `window_stats`, `build_baseline`, `signals`, `calibrate` + `scripts/calibrate.py` writing `configs/sigma.json`; tests for `signals` (sped-up clip gives negative pace signal with correct magnitude).
  Accept: sigma values printed per signal and look sane (no zeros, no NaN); tests pass.
- [x] **C3 [C] UI completion with mock data.** (done 2026-10-04, see HANDOFF) Needs: C2. Prompts: D9b, D5, D7 from `docs/DASHBOARD_PROMPTS.md`.
  Do: ExplanationCard with "Show the math" (MathDisclosure, grid-rows accordion), ScoreCard (SVG ring with count-up, 7 dimension chips), RadarCard (SVG radar with polygon draw-in, list fallback below 420 px), WordRibbon (severity ramp colours, aligned with waveform), TranscriptPanel (click to seek, playback highlight via rAF), ResultsHeader, loading and error states (LoadingCard with honest bars, ErrorBanner with mapping table), pydantic response models, `/baselines` stub, Docker skeleton that builds.
  Accept: all UI parts render from mock JSON; `docker build` succeeds; `npm run lint:design` passes.
- [ ] **ALL: record teammate ideals of T1 and T3**; A and one teammate start human flawed takes (cards A-J) for T4 (Member A keeps the sheet). Now handled by D3/D4.

## Day 4: Detection v1 and first integration
- [ ] **A4 [A] (M) Full synthetic build, metadata, splits, human labels.** Needs: A3.
  Do: build all 8 texts (T7, T8 only after their ideals exist); `metadata.csv` with `split`, `speaker_split`, `flaw_families`, `redistributable` (CONTRACTS v1.1); stress variants via `scripts/make_stress_variants.py` (gain -12/-6/+6 dB; noise at 30/20/15 dB SNR); `scripts/audacity_to_labels.py` (Audacity label txt to label JSON); QC log (listening notes).
  Accept: `validate_labels.py` passes on everything; counts per text/flaw/level/family in HANDOFF; no clip of one speaker in two speaker splits.
- [x] **B4 [B] Region detection, typing, `analyze()`, eval v1.** Needs: B3.
  Do: `compare/regions.py`, flaw typing per ARCHITECTURE section 5, `analyze.py` returning a contract-valid dict (explanations may be placeholders), `scripts/run_eval.py --split dev` writing `results/metrics_dev.csv` (precision/recall/F1 at IoU 0.5, boundary error, recall by level).
  Accept: eval runs on dev; first numbers recorded in HANDOFF (even if poor); failure examples listed.
- [~] **C4 [C] (M) Real integration.** Ticked earlier but NO HANDOFF session entry and M1 is not ticked: re-run the acceptance below with a real upload, then log it and tick M1. Needs: B4 (or B's draft of `analyze()`). Prompts: D11, D4 from `docs/DASHBOARD_PROMPTS.md`.
  Do: `/analyze` calls real `analyze()`, result caching by hash, upload end-to-end, LoadingCard and ErrorBanner with all error mappings, warnings banner for `meta.warnings`.
  Accept: upload a flawed T4 file in the browser and see real flagged regions; friendly errors for bad inputs; `npm run lint:design` passes. **Milestone M1.**

## Day 5: Explanations, scoring, tuning
- [ ] **A5 [A] (M) QC fixes, human set, listener-test material.** Needs: A4, D4.
  Do: fix issues from `dataset/QC_LOG.md`; convert and validate human labels (at least 8 labeled human recordings across cards A-J, incl. 2 "almost perfect", at least 1 from a test speaker); material for the listener test (5 severity versions of 3 clips) and the script computing rank correlation from responses (D runs the form); dataset card draft.
  Accept: human labels validated against the recording sheet; listener material handed to D.
- [x] **B5 [B] Tuning, explanations, scoring.** Needs: B4.
  Do: tune `tau_flag`, `tau_trim`, window size on DEV only; explanation templates for every flaw type (5 fields, real numbers); `scoring/rubric.py` per ARCHITECTURE section 7; score-vs-level plot.
  Accept: every detected flaw has all 5 explanation fields; score correlation with severity reported (dev); settings frozen in config with a note in HANDOFF.
- [ ] **C5 [C] Landing page and demo mode.** Needs: C4. Prompts: D2, D3, D10, Q4 from `docs/DASHBOARD_PROMPTS.md`.
  Do: Landing hero and InputCard (segmented tabs, drop zone, custom Select, validation), HeroBanner (animated waveform bars, floating chips, caption), SampleCards (3 demo entry points), "How it works" section, Footer, demo mode end-to-end (`/demo/{name}` + `/demo-audio/{name}.wav`), deep links (`#/results?sample=botched`).
  Accept: demo buttons work without any upload; stranger test (Q4) passes; landing page matches the Maestra/Clideo reference family. **Milestone M2.**

## Day 6: Hard cases and FEATURE FREEZE
- [ ] **A6 [A] (S) Extra humans, final labels, alignment sanity, draft upload.** Needs: A5.
  Do: more human takes incl. held-out test speakers (h11, h12); licence audit of T1-T4 (`redistributable` flags, decision on removing audio from the public repo, see MEMBER_A guardrail 15); final labels and splits; script comparing re-aligned word times vs ground truth on flawed files (median error); draft upload to Hugging Face.
  Accept: numbers in HANDOFF; dataset visible on HF (private is fine for now).
- [ ] **B6 [B] (M) Fillers, Mode B, CPU Fallback, test runs.** Needs: B5b.
  Do: CPU Fallback in `aligner.py` for OOM errors (also needed because the Hugging Face Space runs on CPU); filled-pause detector (canonical enum `FILLERS`, not `FILLER_WORD`); Mode B (pooled prior baseline from statistical word/punctuation rules, removing artistic flaws like `PAUSE_MISPLACED`); single run on every TEST set (TEST-TEXT T3, T6; TEST-SPEAKER h11, h12; STRESS T7, T8) after freezing thresholds (no tuning after) and the stress matrix in `docs/STRESS_TESTS.md`.
  Accept: `results/metrics_test.csv`, `results/stress_*.csv`, figures saved, honest numbers in HANDOFF; T7/T8 report `mode: prior` and "No-reference mode".
- [ ] **C6 [C] Responsive, motion and accessibility polish.** Needs: C5. Prompts: D12, D13, D14 from `docs/DASHBOARD_PROMPTS.md`.
  Do: responsive pass at 1440/1024/768/390 px (MiniPlayer on phone, scroll-snap flaw cards, radar→bars below 420 px), motion audit against MOTION.md catalogue (all 34 motions), accessibility pass (Lighthouse ≥95, keyboard-only flow, visible focus, aria-labels, contrast, reduced motion), large-file handling.
  Accept: bad inputs give friendly errors; UI usable on a phone; Lighthouse accessibility ≥95; no animation outside the catalogue; `npm run lint:design` passes. **FEATURE FREEZE tonight.** Tag `v0.9-freeze`.

## Day 7: Package and publish
- [ ] **A7 [A] Final dataset publish.** Do: upload to Hugging Face dataset + public Drive mirror; final dataset card; `download_dataset.sh` tested on a clean machine. Accept: links in README work from a logged-out browser.
- [ ] **B7 [B] (M) Final results and reproducibility.** Do: final tables/figures in `results/` (all plots listed in `docs/STRESS_TESTS.md` section 2); two-run hash-equality test (`tests/test_reproducible.py`, stress item S10); extra unit tests for critical functions. Accept: `make eval` regenerates the tables; hashes equal.
- [ ] **C7 [C] Docker, deploy, README v1.** Prompts: D16, D17, Q1 from `docs/DASHBOARD_PROMPTS.md`.
  Do: production build (`npm run build` with hashed assets), FastAPI serves `app/dist`, Dockerfile frontend stage, `make app-prod`, favicon.svg (three-bar logo), meta tags, design audit (Q1 with screenshots at 3 widths vs references), deploy to Hugging Face Spaces.
  Accept: public URL works on phone and another laptop; `make check` passes inside Docker; no external network requests at runtime; design audit table is all-pass.

## Day 8: Polish and documentation
- [ ] **A8 [A]** Figures and numbers for technical-doc page 2 (dataset construction, gradient, QC); data-collection footage. A writes the text (D8).
- [ ] **B8 [B]** Figures, tables and formulas for technical-doc pages 3-6 (features, method, scoring, results, limitations). A assembles (D8).
- [ ] **C8 [C]** Dashboard polish (bugs only, no new features, use R-prompts from `docs/DASHBOARD_PROMPTS.md` as needed); screenshots for the document; video dashboard-segment script (V1 prompt). A owns document assembly (D8).

## Day 9: Document and video
- [ ] **A9 [A]** Review README and dataset links as a stranger; narrate the data part of the video.
- [ ] **B9 [B]** Fresh-clone test on a DIFFERENT laptop from scratch; narrate the pipeline part.
- [ ] **C9 [C]** Record dashboard demo (V1 prompt from `docs/DASHBOARD_PROMPTS.md`); edit the video (3-10 min); export final PDF doc.

## Day 10: Buffer and submit
- [ ] **ALL:** upload video early, final link check (GitHub, dataset, Space awake, video), submit hours before the deadline. Bug fixes only.
