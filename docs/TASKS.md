# TASKS.md: Task board (IDs, acceptance criteria)

Rules: tick `[x]` only your own task, only after its acceptance criteria are verified by RUNNING things. One task = one branch = one pull request. Task IDs are used in prompts and commit messages.
Branch names: `a/<task-id>-short-name`, `b/...`, `c/...`. Commit format: `<area>: <what> (task A2)`.

Legend: **[A]** Data, **[B]** Pipeline, **[C]** App/Platform. "Needs" lists what must exist first.

---
## Day 1: Foundations
- [ ] **C1 [C] Repo scaffold and kit.** Needs: nothing.
  Do: folder structure, `.gitignore`, `requirements.txt` (pinned), `Makefile` (setup/test/check/smoke/app), commit the AI kit files, FastAPI app with `/health`, Vite+React skeleton, `app/public/mock_result.json` valid against CONTRACTS section 6 (3 flaws), `tests/test_health.py`.
  Accept: fresh clone then `make setup && make check` passes; `make app` shows a page that loads mock JSON.
- [x] **A1 [A] Texts and sources.** Needs: nothing.
  Do: finalize T1-T6 text files in `dataset/texts/` (exact spoken wording, punctuation kept), `dataset/SOURCES.md` (URL, license, notes per text), download source audio for historical texts, `scripts/prepare_audio.py` (ffmpeg convert to 16 kHz mono WAV, trim to <=1 s edge silence, print duration and peak level).
  Accept: >= 3 prepared source WAVs in `data/interim/`; every text has a transcript and a SOURCES entry.
- [x] **B1 [B] Transcript parsing and forced alignment.** Needs: a sample wav + text (use any 10 s recording).
  Do: `audio/io.py`, `align/transcript.py`, `align/aligner.py`, CLI `python -m speechcoach.align.run`, caching by content hash, tests for `parse_transcript`.
  Accept: CLI prints and saves a valid Alignment JSON (CONTRACTS section 2); word starts are non-decreasing; test passes.
- [ ] **ALL: record ideal T4 (Gitanjali 35)**, 3 takes each, Day 1 evening (see guide for recording protocol).

## Day 2: Features and first flaw
- [ ] **A2 [A] WORLD analysis, time-program renderer, first flaw.** Needs: A1.
  Do: `dataset/world_engine.py` with `analyze_world`, `render`, anchors-based time map, `inject` for PACE_FAST L1-L5 on T4 using `configs/flaws.yaml`; `resynth_control`; `scripts/validate_labels.py`; build `dataset/sample/` (1 ideal + 1 flawed + label + transcript).
  Accept: 5 PACE_FAST files + control for T4 with labels passing `validate_labels.py`; A listened to L1, L3, L5; word times in labels consistent with the time map.
- [x] **B2 [B] Frame features, word table, syllables.** Needs: B1.
  Do: `features/frame.py`, `features/words.py` (`word_table`), syllable counter (cmudict + fallback), `scripts/plot_features.py` (figure: pitch, energy, pauses over time), tests with a 150 Hz sine (F0 ~150 +/- 2 Hz), a known-gap signal (pause length error < 20 ms), two synthetic speakers with different base pitch giving equal normalized `st`.
  Accept: `make test` passes; figure produced for one real file and shown to the team.
- [ ] **C2 [C] Dashboard v0 on mock data.** Needs: C1.
  Do: waveform with flaw regions (wavesurfer.js Regions), stacked Plotly charts with shaded flaw regions, flaw list, explanation card, upload form posting to `/analyze` (stub returns mock).
  Accept: opening the page shows all of that from `mock_result.json`; clicking a region selects the flaw and plays the segment.
- [ ] **ALL: record ideal T5 and T6**, 3 takes each.

## Day 3: Engine complete, baseline and calibration
- [ ] **A3 [A] Full flaw engine and batch build.** Needs: A2.
  Do: all flaw types and levels per FLAW_SPEC, composites, `build_dataset.py` (skip-existing, `--workers`), `results/gradient_check.png` (measured deviation per level per flaw), run for T4 and T1 first.
  Accept: ~48 files per text generated for T4 and T1; gradient plot rises monotonically per flaw; validation passes.
- [ ] **B3 [B] Window stats, baseline, signals, calibration.** Needs: B2 and >= 2 ideal recordings of T4 aligned.
  Do: `window_stats`, `build_baseline`, `signals`, `calibrate` + `scripts/calibrate.py` writing `configs/sigma.json`; tests for `signals` (sped-up clip gives negative pace signal with correct magnitude).
  Accept: sigma values printed per signal and look sane (no zeros, no NaN); tests pass.
- [ ] **C3 [C] UI completion with mock data.** Needs: C2.
  Do: per-word deviation strip, radar chart, overall score, sensitivity control (UI only), loading and error states, pydantic response models, `/baselines` stub, Docker skeleton that builds.
  Accept: all UI parts render from mock JSON; `docker build` succeeds.
- [ ] **ALL: record ideal T1 and T3**; A and one teammate start human flawed takes (cards A-G) for T4.

## Day 4: Detection v1 and first integration
- [ ] **A4 [A] Full synthetic build, metadata, splits, human labels.** Needs: A3.
  Do: build all 6 texts; `metadata.csv`; dev/test split fields; `scripts/audacity_to_labels.py` (Audacity label txt to label JSON); QC log (listening notes).
  Accept: `validate_labels.py` passes on everything; counts per text/flaw/level in HANDOFF.
- [ ] **B4 [B] Region detection, typing, `analyze()`, eval v1.** Needs: B3.
  Do: `compare/regions.py`, flaw typing per ARCHITECTURE section 5, `analyze.py` returning a contract-valid dict (explanations may be placeholders), `scripts/run_eval.py --split dev` writing `results/metrics_dev.csv` (precision/recall/F1 at IoU 0.5, boundary error, recall by level).
  Accept: eval runs on dev; first numbers recorded in HANDOFF (even if poor); failure examples listed.
- [ ] **C4 [C] Real integration.** Needs: B4 (or B's draft of `analyze()`).
  Do: `/analyze` calls real `analyze()`, result caching by hash, upload end-to-end. Decision point: if the React UI is far behind, switch to Streamlit now.
  Accept: upload a flawed T4 file in the browser and see real flagged regions. **Milestone M1.**

## Day 5: Explanations, scoring, tuning
- [ ] **A5 [A] QC fixes, human set, listener test.** Needs: A4.
  Do: fix issues found in QC; at least 8 labeled human recordings (mix of flaw cards, incl. 2 "almost perfect"); Google Form listener-test material (5 versions of 3 clips); script to compute rank correlation from responses; dataset card draft.
  Accept: human labels validated; listener form sent.
- [ ] **B5 [B] Tuning, explanations, scoring.** Needs: B4.
  Do: tune `tau_flag`, `tau_trim`, window size on DEV only; explanation templates for every flaw type (5 fields, real numbers); `scoring/rubric.py` per ARCHITECTURE section 7; score-vs-level plot.
  Accept: every detected flaw has all 5 explanation fields; score correlation with severity reported (dev); settings frozen in config with a note in HANDOFF.
- [ ] **C5 [C] Explanation card, radar, demo mode.** Needs: C4.
  Do: explanation card with "show the math"; radar from real scores; `/demo/{name}` plus 3 demo clips (from A) with precomputed JSON.
  Accept: demo buttons work without any upload. **Milestone M2.**

## Day 6: Hard cases and FEATURE FREEZE
- [ ] **A6 [A] Extra humans, final labels, alignment sanity, draft upload.** Needs: A5.
  Do: more human takes incl. held-out speaker for test; final labels and splits; script comparing re-aligned word times vs ground truth on flawed files (median error); draft upload to Hugging Face.
  Accept: numbers in HANDOFF; dataset visible on HF (private is fine for now).
- [ ] **B6 [B] Fillers, Mode B, test run, speaker-agnostic experiment.** Needs: B5.
  Do: filled-pause detector; Mode B (pooled prior baseline); single TEST-split run (no tuning after); male-vs-female (or two-voice) comparison figure.
  Accept: `results/metrics_test.csv`, figures saved, honest numbers in HANDOFF.
- [ ] **C6 [C] Robustness and polish.** Needs: C5.
  Do: large-file handling, wrong-transcript warning from `meta.warnings`, progress states, phone layout; A/B playback only if everything else is done.
  Accept: bad inputs give friendly errors; UI usable on a phone. **FEATURE FREEZE tonight.** Tag `v0.9-freeze`.

## Day 7: Package and publish
- [ ] **A7 [A] Final dataset publish.** Do: upload to Hugging Face dataset + public Drive mirror; final dataset card; `download_dataset.sh` tested on a clean machine. Accept: links in README work from a logged-out browser.
- [ ] **B7 [B] Final results and reproducibility.** Do: final tables/figures in `results/`; two-run hash-equality test; extra unit tests for critical functions. Accept: `make eval` regenerates the tables; hashes equal.
- [ ] **C7 [C] Docker, deploy, README v1.** Do: finish Dockerfile, deploy to Hugging Face Spaces, README. Accept: public URL works on phone and another laptop; `make check` passes inside Docker.

## Day 8: Polish and documentation
- [ ] **A8 [A]** Technical-doc page 2 (dataset construction, gradient, QC, listener test) with figures; record data-collection footage.
- [ ] **B8 [B]** Technical-doc pages 3-6 content (features with formulas, method, scoring, results, limitations) with figures.
- [ ] **C8 [C]** Dashboard polish (bugs only, no new features); doc page 1 and assembly to <= 6 pages; video script.

## Day 9: Document and video
- [ ] **A9 [A]** Review README and dataset links as a stranger; narrate the data part of the video.
- [ ] **B9 [B]** Fresh-clone test on a DIFFERENT laptop from scratch; narrate the pipeline part.
- [ ] **C9 [C]** Record dashboard demo; edit the video (3-10 min); export final PDF doc.

## Day 10: Buffer and submit
- [ ] **ALL:** upload video early, final link check (GitHub, dataset, Space awake, video), submit hours before the deadline. Bug fixes only.
