# AGENTS.md: Rules for every AI assistant working in this repositry

You are an AI coding assistant helping a 3-person student team build **SpeechCoach** for the Multimodal AI Hackathon 2026, Track C. We have 10 days. Follow these rules exactly. If a rule conflicts with what the user asks, say so and ask before proceeding.

## 1. What we are building (30 seconds)
A speech-evaluation system. Input: a speech recording and its transcript. The system:
1. aligns the text to the audio (word start/end times),
2. extracts acoustic features (pitch, loudness, pace, pauses, clarity),
3. compares them to "ideal" recordings of the SAME text,
4. finds time regions where delivery deviates (flaws),
5. explains each flaw with numbers, and scores the delivery,
6. shows everything in a web dashboard.

We also build a public dataset: ideal vs deliberately flawed recordings of the same texts, with exact flaw timestamps.
Details: `docs/PROJECT_BRIEF.md`, `docs/ARCHITECTURE.md`.

## 2. Read before you act (every session, in this order)
1. `docs/CONTRACTS.md` (interfaces, DO NOT break)
2. Your role file: `docs/roles/MEMBER_<X>.md`
3. The task the user names in `docs/TASKS.md` (check the TASKS status board)
4. The latest entries of `docs/HANDOFF.md`
5. Read `docs/STRESS_TESTS.md` and `docs/RECORDING_PROTOCOL.md` where relevant.
6. If you are Member C: also read `docs/design/DESIGN_SYSTEM.md`, `docs/design/MOTION.md`, `docs/design/COMPONENTS.md`, and the matching prompt in `docs/DASHBOARD_PROMPTS.md`

If any of these is missing or contradicts the user's message, stop and ask.

## 3. Fixed tech stack (do not swap or add without asking)
- Python 3.11.9: numpy, scipy, pandas, librosa, soundfile, pyloudnorm
- praat-parselmouth (F0, HNR), pyworld (flaw injection)
- torch + torchaudio 2.5.1+cu124 GPU/CUDA (MMS_FA forced alignment)
- scikit-learn, ruptures (optional)
- FastAPI + uvicorn; React (Vite, JavaScript) + CSS Modules + d3-scale/d3-shape/d3-array + wavesurfer.js v7 (audio and waveform only) + lucide-react; design rules in docs/design/. No Plotly, no Tailwind, no UI kit.
- pytest, Docker
- NVIDIA GPU with CUDA 12.4 (minimum GTX 1050 / compute capability 6.1). No paid APIs. **No LLM calls inside the product**: explanations are template-based and deterministic.

## 4. Commands
```
make setup    # install dependencies
make test     # pytest
make check    # tests + smoke test + lint:design (MUST pass before any commit)
make smoke    # end-to-end run on dataset/sample/
make dataset  # build synthetic dataset (Member A)
make eval     # evaluation on dev/test splits (Member B)
make app      # run API + dashboard (dev)
make app-prod # build + serve on port 7860 (production)
```

## 5. Ownership: only edit your own area
| Area | Owner | Paths |
|---|---|---|
| Data | Member A | `src/speechcoach/dataset/`, `dataset/`, `data/`, `configs/flaws.yaml`, `scripts/prepare_audio.py`, `scripts/validate_labels.py`, `scripts/audacity_to_labels.py`, `scripts/upload_dataset.sh`, `scripts/download_dataset.sh`, `tests/test_dataset*.py`, `dataset/QC_LOG.md`, `dataset/texts/T5-T8.txt`, `docs/{dataset,methodology,scoring,demo}.md`, `docs/technical_document/`, `docs/RECORDING_PROTOCOL.md`, `scripts/make_stress_variants.py`, `dataset/metadata.csv` |
| Pipeline | Member B | `src/speechcoach/{audio,align,features,compare,explain,scoring}/`, `src/speechcoach/models/`, `src/speechcoach/analyze.py`, `configs/thresholds.yaml`, `configs/rubric.yaml`, `configs/sigma.json`, `scripts/{calibrate,run_eval,make_plots,plot_features}.py`, `scripts/stress_test.py`, `scripts/train_window_model.py`, `results/`, `notebooks/`, tests for these modules |
| App/Platform | Member C | `src/speechcoach/api/`, `app/`, `docs/design/`, `docs/DASHBOARD_PROMPTS.md`, `scripts/make_mock_result.py`, `Dockerfile`, `Makefile`, `requirements*.txt`, `.gitignore`, `.github/`, `README.md`, `scripts/smoke.sh`, `tests/test_api*.py` |
| Shared (ask first) | everyone | `AGENTS.md`, `docs/CONTRACTS.md`, `docs/ARCHITECTURE.md`, `docs/FLAW_SPEC.md` |
| Append-only | everyone | `docs/HANDOFF.md`; in `docs/TASKS.md` only tick your own task |

If you need a change in someone else's area: do NOT edit it. Write a request in `docs/HANDOFF.md` under "Requests".

## 6. Golden rules
1. **Smallest change that solves the task.** No drive-by refactors, renames, reformatting, or "improvements" in files you were not asked to touch.
2. **Never change** a function signature, JSON field, file name, enum value or unit defined in `docs/CONTRACTS.md`. If you think it must change: STOP, explain why, propose the exact diff to CONTRACTS.md, and wait for approval.
3. **Numbers live in `configs/*.yaml`** (thresholds, weights, flaw parameters). No magic numbers in code. Never change config values unless the task says so.
4. **Never fabricate.** No invented metrics, results, file paths, dataset facts, library functions or citations. If you did not run it, say "not run".
5. **Never make a test pass** by hard-coding the expected output, loosening the assertion, or deleting the test. Fix the code or explain why the test is wrong.
6. **Check library APIs against the INSTALLED version** (`python -c "import x; help(x.f)"`) before using them. Do not guess signatures.
7. **No new dependency** without asking. The human adds it to `requirements.txt`.
8. **Deterministic:** seeds come from `configs/thresholds.yaml` (`seed`). No time-dependent or order-dependent behaviour. Cache by content hash.
9. **Never commit** audio, model weights, `.env` or secrets. Never read or write outside the repo folder.
10. **Never run destructive commands:** `rm -rf` on `data/` or `dataset/`, `git reset --hard`, `git push --force`, `git clean -fd`, `git checkout .`. Ask first.
11. **Task too big?** If it touches more than ~3 files or needs more than ~1.5 hours, split it and do only the first part.
12. **Stuck after 2 failed attempts? Stop.** Report: what you tried, the exact error, and your top 3 hypotheses. Do not thrash or rewrite everything.
13. **Splits are by speaker and text**: no clip of one speaker in two speaker splits.
14. **Canonical enum FILLERS**: use `FILLERS` for filler word flaws.

## 7. Work loop (every task)
1. **PLAN:** restate the task in your own words; list files to create/edit; list tests; list risks. Then WAIT for the human to say "go".
2. **IMPLEMENT:** only what the plan says.
3. **RUN:** execute the code on a real sample and show the real output.
4. **TEST:** add or extend pytest tests (prefer synthetic signals with known answers, e.g. a 150 Hz sine must give F0 ~150 Hz). Run `make check`.
5. **REPORT:** files changed, how to run it, what was verified (with actual output), what is NOT done.
6. **COMMIT:** only when the human says so. Message format: `<area>: <what> (task <ID>)`.

## 8. Code conventions
- Python: type hints, docstrings that state units, `pathlib` not string paths, `logging` not `print` (except CLIs), functions under ~50 lines, no global mutable state.
- Units: seconds; pitch in semitones relative to the speaker's median; loudness in dB relative to the speaker's 95th percentile; z-scores signed (see CONTRACTS).
- Every module that does real work has a small CLI (`python -m speechcoach.<module> ...`) so a human can test it by hand.
- Errors: raise clear exceptions with context. No bare `except`. No silent fallbacks that change results.
- Frontend: all data comes from the API contract. **No analysis logic in the frontend.** JavaScript with JSDoc types. CSS Modules + design tokens (`docs/design/DESIGN_SYSTEM.md` section 4.4). Small components (under ~150 lines, split if larger). No Plotly, no Tailwind, no UI kit. Icons: lucide-react only. Animations: only those listed in `docs/design/MOTION.md` catalogue. No blue/purple (hue 190-320°), no gradients, no square corners (min radius 8 px).
- Tests: `tests/test_<module>.py`, tiny synthetic fixtures, no network access.

## 9. Handoff (end of EVERY session)
Append an entry to `docs/HANDOFF.md`: date, member, task ID, files changed, status, how to verify, open problems, requests for other members. Then tick your task in `docs/TASKS.md`.

## 10. When unsure
Ask ONE clear question instead of guessing.
