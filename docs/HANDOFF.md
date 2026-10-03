# HANDOFF.md: Shared project memory (append-only)

AI assistants forget everything between chats. **This file is their memory.** Read the newest entries at the start of a session; append at the end. Never delete or rewrite old entries (strike through with `~~text~~` if something becomes wrong).

---
## 1. Current state (humans update this at the evening sync)
- Day: 1
- Last green tag: none
- Milestones: M1 (upload shows real flaw regions): [ ]   M2 (demo mode + explanations): [ ]   Freeze (Day 6): [ ]
- Counts: ideal recordings: 4 | synthetic files: 0 | human flawed: 0
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

