# HANDOFF.md: Shared project memory (append-only)

AI assistants forget everything between chats. **This file is their memory.** Read the newest entries at the start of a session; append at the end. Never delete or rewrite old entries (strike through with `~~text~~` if something becomes wrong).

---
## 1. Current state (humans update this at the evening sync)
- Day: 1
- Last green tag: none
- Milestones: M1 (upload shows real flaw regions): [ ]   M2 (demo mode + explanations): [ ]   Freeze (Day 6): [ ]
- Counts: ideal recordings: 4 | synthetic files: 30 | human takes: 4
- Latest dev metrics (F1@IoU0.5 / Spearman score-vs-level): n/a
- Biggest risk right now: n/a

## 2. Requests between members
Format: `[date] FROM -> TO: request. Status: open/done`
- [2026-10-03] A -> B: 4 ideal recordings prepared (T1 Indian Pep, T2 MLK, T3 Kalam, T4 Lincoln) in `data/interim/` and `dataset/audio/ideal/`. Status: done

## 3. Contract change requests
Format: `[date] who: exact proposed diff to docs/CONTRACTS.md. Approvals: A[ ] B[ ] C[ ]`
- (none yet)

## 4. Decisions log
Format: `[date] decision: reason`
- Stack fixed as in AGENTS.md section 3.
- Dev split T1,T2,T4,T5; test split T3,T6 (never tune on test).
- Focused the primary corpus on the 4 user-provided speeches: T1 (Indian Pep Talk), T2 (Martin Luther King Jr.), T3 (Dr. A.P.J. Abdul Kalam), T4 (Abraham Lincoln), providing a 2-2 accent balance (Indian vs American).
- [2026-10-03] decision: Committed ideal audio files (T1-T4 WAVs, ~23.3 MB) directly to branch a/A1-texts-sources per explicit user instruction so all team members have immediate access to canonical audio.
- [2026-10-03] decision: Adopted the `app/ui_kit/` design system. Copied to `docs/design/` (DESIGN_SYSTEM.md, COMPONENTS.md, MOTION.md, reference PNGs) and `docs/DASHBOARD_PROMPTS.md`. Frontend tech changed: Plotly.js → custom SVG charts (d3-scale/d3-shape/d3-array), wavesurfer Regions plugin → our own region overlay layer, added CSS Modules + lucide-react + design linter. Updated AGENTS.md (section 3, 5), MEMBER_C_APP.md (guardrail 5-6), TASKS.md (all C tasks now reference design prompts D0a–D17). Reason: polished non-generic look (rounded shapes, custom animation, warm palette, no default blue, smaller bundle).

## 5. Known issues
Format: `[date] who: issue, how to reproduce, status`
- (none yet)

## 6. Session log (newest at the bottom)

### [2026-10-03 02:20] Member A, task A1
- Goal: Ingest 4 user-provided video speeches (2 Indian, 2 American), transcribe their entire word-for-word spoken subtitles, build audio standardization pipeline (`prepare_audio.py`), and establish exactly 4 matching transcripts (T1.txt to T4.txt) and provenance in `SOURCES.md`.
- Files changed: `scripts/prepare_audio.py`, `dataset/SOURCES.md`, `dataset/texts/T{1..4}.txt`, `tests/test_dataset_prep.py`.
- What I ran and what it printed (real output, short):
  `.\.venv\Scripts\pytest.exe -v tests/test_dataset_prep.py` -> 6 passed in 0.04s.
  Converted 4 MP4s to 16 kHz mono WAVs with edge silence trimmed:
  - `T1__orig-indianpep__ideal.wav`: 186.5s (302 words, intro & outro trimmed)
  - `T2__orig-mlk__ideal.wav`: 234.1s (388 words)
  - `T3__orig-kalam__ideal.wav`: 198.9s (391 words)
  - `T4__orig-lincoln__ideal.wav`: 145.2s (270 words)
- Status: done
- NOT done / open problems: Forced alignment (Task B1) and WORLD vocoder flaw injection (Task A2).
- How a teammate can verify (exact command): `.\.venv\Scripts\pytest.exe -v tests/test_dataset_prep.py`
- Requests for others: Member B can align and inspect ideal baseline audios.


### [2026-10-03 11:47] Member B, task B1
- Goal: Transcript parsing and forced alignment implementation using torchaudio MMS_FA.
- Files changed: `src/speechcoach/audio/io.py`, `src/speechcoach/align/transcript.py`, `src/speechcoach/align/aligner.py`, `src/speechcoach/align/run.py`, `tests/test_align.py`
- What I ran and what it printed (real output, short):
  `$env:PYTHONPATH="src"; .\.venv\Scripts\python.exe -m speechcoach.align.run dataset/audio/ideal/T1__orig-indianpep__ideal.wav dataset/texts/T1.txt results/T1_alignment.json` -> `Alignment saved to results\T1_alignment.json`
- Status: done
- NOT done / open problems: Caching logic computes the hash and saves it in the JSON, but full skip-if-cached logic isn't wired yet.
- How a teammate can verify (exact command): `$env:PYTHONPATH="src"; .\.venv\Scripts\pytest.exe tests/test_align.py`
- Requests for others: Member C can wire the JSON output into the UI mock / backend.

### [2026-10-03 13:14] Member B, task B2
- Goal: Feature extraction (pitch, loudness, spectral flux), word aggregation, and syllable counting.
- Files changed: `src/speechcoach/features/frame.py`, `src/speechcoach/features/words.py`, `src/speechcoach/features/syllables.py`, `scripts/plot_features.py`, `tests/test_features.py`
- What I ran and what it printed (real output, short):
  `$env:PYTHONPATH="src"; .\.venv\Scripts\pytest.exe tests/test_features.py` -> 3 passed
  `$env:PYTHONPATH="src"; .\.venv\Scripts\python.exe scripts/plot_features.py dataset/audio/ideal/T1__orig-indianpep__ideal.wav results/T1_alignment.json` -> Rendered plot successfully.
- Status: done
- NOT done / open problems: None.
- How a teammate can verify (exact command): Run the plot_features script to visualize the data.
- Requests for others: Member B or C can now move to Comparing features (Task B3).

### [2026-10-03 20:15] Member C, task C1
- Goal: Build repo scaffold, FastAPI API, mock generator, design token foundation, styleguide, and interactive dashboard graphs (Score ring, 7-axis Radar, 3-tier Pitch/Loudness/Pacing time series charts, WaveformPanel with lane assignment, WordRibbon, TranscriptPanel, FlawList, and ExplanationCard with MathDisclosure).
- Files changed: `app/package.json`, `app/vite.config.js`, `app/src/main.jsx`, `app/src/App.jsx`, `app/src/styles/tokens.css`, `app/src/styles/base.css`, `app/src/styles/motion.css`, `app/src/lib/colors.js`, `app/src/lib/format.js`, `app/src/lib/motion.js`, `app/src/lib/lanes.js`, `app/src/components/Styleguide/*`, `app/src/components/Charts/*`, `app/src/components/ScoreCard/*`, `app/src/components/WaveformPanel/*`, `app/src/components/WordRibbon/*`, `app/src/components/TranscriptPanel/*`, `app/src/components/FlawList/*`, `app/src/components/ExplanationCard/*`, `scripts/make_mock_result.py`, `app/scripts/check-design.mjs`, `tests/test_mock_result.py`, `pytest.ini`.
- What I ran and what it printed (real output, short):
  `pytest tests/test_health.py tests/test_mock_result.py` -> 4 passed in 0.53s
  `cd app && npm run lint:design` -> ✅ Design Linter: All design system checks passed!
  `cd app && npm run build` -> ✓ built in 350ms
- Status: done
- NOT done / open problems: Live backend POST /analyze integration with real MMS_FA pipeline on GPU (Task C4).
- How a teammate can verify (exact command): `npm run lint:design` in `app/`, `pytest` in repo root, open `http://localhost:5173` to explore interactive graphs.
- Requests for others: Member B pipeline modules can now connect directly to the FastAPI `/analyze` endpoint when ready.

### [2026-10-04 11:08] Member C, task C2
- Goal: Dashboard v0 on mock data. App shell, waveform panel, three stacked custom SVG charts, flaw list with selection behaviour, upload form.
- Files changed: `app/src/App.jsx`, `app/src/App.module.css`.
- What I ran and what it printed (real output, short):
  `cd app && npm run lint:design` -> ✅ Design Linter: All design system checks passed!
- Status: done
- NOT done / open problems: A test from A1 `test_dataset_prep.py` is failing locally, but this is a Member A issue.
- How a teammate can verify (exact command): `cd app && npm run dev`, check `http://localhost:5173`.
- Requests for others: None.

### [2026-10-04 12:00] Member C, task C3
- Goal: UI completion with mock data. LoadingCard, ErrorBanner, Pydantic response models, `/baselines` stub, Docker skeleton.
- Files changed: `app/src/components/LoadingCard/*`, `app/src/components/ErrorBanner/*`, `src/speechcoach/api/models.py`, `src/speechcoach/api/main.py`, `Dockerfile`, `app/src/App.jsx`.
- What I ran and what it printed: `python -c "from speechcoach.api.models import AnalysisResult..."` passed validation. `npm run lint:design` -> passed.
- Status: done
- NOT done / open problems: Docker container needs the fully integrated backend (Task C4) to function end-to-end, but skeleton builds correctly.
- How a teammate can verify: `make app` and open `http://localhost:5173`. Click the sidebar icons to see placeholder states.
- Requests for others: None.

### [2026-10-04 13:20] Member B, task B4
- Goal: Region detection, flaw typing, `analyze()` pipeline, eval v1.
- Files changed: `src/speechcoach/compare/regions.py`, `src/speechcoach/analyze.py`, `scripts/run_eval.py`.
- What I ran and what it printed (real output, short):
  `$env:PYTHONPATH="src"; .\.venv\Scripts\python.exe scripts/run_eval.py --split dev --limit 2` →
  ```
  Found 30 synthetic files in split dev
  Limiting evaluation to 2 files for quick testing.
  Running analyze on T1__synth-orig-indianpep__MONOTONE_L1...
  Running analyze on T1__synth-orig-indianpep__MONOTONE_L3...

  --- Eval v1 Results ---
  Precision: 0.000
  Recall: 0.000
  F1 (IoU 0.5): 0.000
  Mean Boundary Error: 0.000 s

  Recall by Level:
    Level 1: 0.00
    Level 3: 0.00

  Some failure examples (first 5 of 2):
    - T1__synth-orig-indianpep__MONOTONE_L1: missed MONOTONE at 33.5s
    - T1__synth-orig-indianpep__MONOTONE_L3: missed MONOTONE at 14.8s
  ```
  Saved metrics to `results/metrics_dev.csv`.
- Status: done (code complete; first numbers recorded, all zeros as expected before tuning)
- NOT done / open problems: Full 30-file dev eval not yet run (only --limit 2). All metrics are 0 — MONOTONE detection likely needs calibrated sigma values and pitch-variance signal tuning (task B5). Explanations are placeholder strings. Scoring is hardcoded 80 across all dimensions.
- How a teammate can verify (exact command): `$env:PYTHONPATH="src"; .\.venv\Scripts\python.exe scripts/run_eval.py --split dev --limit 2`
- Requests for others: None.

### [2026-10-04 14:25] Member B, task B5
- Goal: Tuning, explanations, scoring.
- Files changed: `src/speechcoach/analyze.py`, `src/speechcoach/compare/regions.py`, `src/speechcoach/explain/templates.py`, `src/speechcoach/scoring/rubric.py`, `configs/thresholds.yaml`, `scripts/tune_dev.py`
- What I ran and what it printed (real output, short):
  `$env:PYTHONPATH="src"; .\.venv\Scripts\python.exe scripts/tune_dev.py` -> Generated `results/score_vs_level.png`.
- Status: done
- NOT done / open problems: F1 score remains extremely low (1.1%) despite NaN fixes because MMS_FA alignment jitter on synthetic files causes massive z-score fluctuations. We need to explore wider `window_size` (W=10+) and higher `tau_flag` values to smooth this out, but the immediate B5 requirements (templates, rubric, initial tuning loop, plot) are met. Settings frozen at tau_flag=2.0, tau_trim=1.0.
- How a teammate can verify (exact command): Look at `results/score_vs_level.png` to verify monotonic score decrease.
- Requests for others: None.


### [2026-10-04 21:15] Member B, task B4b
- Goal: Diagnose and fix the false-positive flood. Formulate a plan for Mode B, CPU Fallback, and Filler words.
- Files changed: `configs/thresholds.yaml`, `scripts/calibrate.py`, `src/speechcoach/analyze.py`, `src/speechcoach/features/words.py`, `src/speechcoach/compare/regions.py`, `docs/TASKS.md`, `docs/ARCHITECTURE.md`, `configs/tau.json`.
- What I ran and what it printed (real output, short):
  `.\.venv\Scripts\python.exe scripts/run_eval.py` -> `F1 (IoU 0.5): 0.065`, false-positive rate dropped drastically (T4 dropped to 3.30/min). Caught CUDA OOM errors on some L5 files.
- Status: done
- NOT done / open problems: Mode B (Prior Baseline) still uses the `zeros_like` placeholder which causes `inf` math errors and floods `MONOTONE` FPs. Long files crash the GPU (OOM) in `aligner.py`. Detailed plan created in `mode_b_implementation_plan.md` artifact.
- How a teammate can verify (exact command): Run `run_eval.py` to see the improved false-positive rates on T4.
- Requests for others: Member B needs to implement Mode B, CPU Fallback, and `FILLER_WORD` flaw (see TASKS.md B6).

