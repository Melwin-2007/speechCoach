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

### [2026-10-03 23:45] Member A, task A1 (Human Recordings Ingestion)
- Goal: Standardize 4 teammate recordings for Text T1 (Adi, Krutika, Sagar Take 1, Sagar Take 2) from diverse media formats into 16 kHz mono 16-bit PCM WAVs, produce matching word-for-word spoken transcripts, and register them in metadata.csv and SOURCES.md.
- Files changed:
  - Audio: `dataset/audio/human/T1__h-adi__ideal.wav`, `dataset/audio/human/T1__h-krutika__ideal.wav`, `dataset/audio/human/T1__h-sagar__take1.wav`, `dataset/audio/human/T1__h-sagar__take2.wav` (plus `data/interim/human/` copies)
  - Transcripts: `dataset/texts/takes/T1__h-adi__ideal.txt`, `dataset/texts/takes/T1__h-krutika__ideal.txt`, `dataset/texts/takes/T1__h-sagar__take1.txt`, `dataset/texts/takes/T1__h-sagar__take2.txt`
  - Metadata: `dataset/metadata.csv`, `dataset/SOURCES.md`
  - Tests: `tests/test_dataset_prep.py`
- What I ran and what it printed (real output, short):
  `$env:PYTHONPATH="src"; .\.venv\Scripts\pytest.exe -v tests/test_dataset_prep.py` -> 9 passed in 0.07s
- Status: done
- NOT done / open problems: None for data ingestion. Baseline builder can leverage these human takes for multi-reference comparisons.
- How a teammate can verify (exact command):
  `$env:PYTHONPATH="src"; .\.venv\Scripts\pytest.exe -v tests/test_dataset_prep.py`
- Requests for others: Member B can align these takes with MMS_FA once torch/torchaudio dependencies are loaded into the environment.

### [2026-10-04 00:15] Member A, task A2 (WORLD Vocoder Engine & First Flaw PACE_FAST)
- Goal: Implement WORLD vocoder analysis-synthesis engine (`world_engine.py`), anchors-based time map renderer, `inject()` for `resynth_control` and `PACE_FAST` L1-L5 on T4, label schema validator (`validate_labels.py`), and populate smoke sample package in `dataset/sample/`.
- Files changed:
  - Source: `src/speechcoach/dataset/world_engine.py`, `scripts/validate_labels.py`
  - Configs: `configs/flaws.yaml`, `configs/thresholds.yaml`
  - Alignments & Audio: `dataset/alignments/T4__orig-lincoln__ideal.json`, `dataset/audio/synthetic/T4__synth-orig-lincoln__*.wav` (6 files)
  - Labels: `dataset/labels/T4__synth-orig-lincoln__*.json` (6 files)
  - Sample package: `dataset/sample/` (ideal.wav, flawed.wav, label.json, alignment.json, transcript.txt)
  - Metadata: `dataset/metadata.csv`
  - Tests: `tests/test_dataset_world.py`, `docs/TASKS.md`
- What I ran and what it printed (real output, short):
  - `python -m speechcoach.dataset.world_engine --text T4 --flaw PACE_FAST --levels 1,2,3,4,5` -> generated control (145.24s) and PACE_FAST L1 (143.88s) through L5 (100.01s).
  - `python scripts/validate_labels.py dataset/labels` -> `6/6 passed, 0 failed.`
  - `pytest -v tests/test_dataset_prep.py tests/test_dataset_world.py` -> `14 passed in 1.83s`
- Status: done
- NOT done / open problems: Full batch build with other flaw types (Task A3).
- How a teammate can verify (exact command):
  `$env:PYTHONPATH="src"; .\.venv\Scripts\pytest.exe -v tests/test_dataset_world.py`
- Requests for others: Member B can use `dataset/sample/` or `T4__synth-orig-lincoln__PACE_FAST_L3.wav` to test feature shifts and detection.

### [2026-10-04 00:30] Member A, task A3 (Multi-Text & Multi-Flaw Expansion: T1 & T4)
- Goal: Expand flaw injection engine with `PACE_SLOW`, `MONOTONE`, and `VOLUME_DROP`. Generate synthetic spectrum for both T1 (Indian Pep Talk) and T4 (Lincoln), bringing total synthetic benchmark files to 21.
- Files changed:
  - Engine: `src/speechcoach/dataset/world_engine.py` (added PACE_SLOW, MONOTONE, VOLUME_DROP)
  - Alignments: `dataset/alignments/T1__orig-indianpep__ideal.json` (corrected word 244 numeric timestamp)
  - Audio & Labels (30 synthetic files):
    - T1 (15 takes): `PACE_FAST` L1-L5, `PACE_SLOW` L1, L3, L5; `MONOTONE` L1, L3, L5; `VOLUME_DROP` L1, L3, L5; `resynth_control` (WAVs + JSONs)
    - T4 (15 takes): `PACE_FAST` L1-L5, `PACE_SLOW` L1, L3, L5; `MONOTONE` L1, L3, L5; `VOLUME_DROP` L1, L3, L5; `resynth_control` (WAVs + JSONs)
  - Metadata: `dataset/metadata.csv` (now tracking 38 total recordings)
- What I ran and what it printed (real output, short):
  - `python scripts/validate_labels.py dataset/labels` -> `30/30 passed, 0 failed.`
  - `pytest -v tests/test_dataset_prep.py tests/test_dataset_world.py` -> `14 passed in 1.68s`
- Status: done
- NOT done / open problems: Flaws PAUSE_MISSING and PAUSE_EXCESS, plus T2/T3 generation.
- How a teammate can verify (exact command):
  `.\.venv\Scripts\python.exe scripts/validate_labels.py dataset/labels`
- Requests for others: Member B can now calibrate baselines (Task B3) on both American (T4) and Indian (T1) accents with identical flaw dimensions.




