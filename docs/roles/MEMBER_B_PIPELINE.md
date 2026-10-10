# MEMBER_B_PIPELINE.md: Role file for Member B (Signal / Analysis Engineer)

## Mission
Own the **analyzer** (feature extraction 20% + temporal grounding and explainability 25% of the score): forced alignment, acoustic features, normalization, baseline, calibration, flaw regions, explanations, scoring, evaluation, stress tests.

**Status (2026-10-06, Day 4):** B1-B5 and B4b done. Pipeline runs end to end, but dev F1@IoU0.5 is only 0.065 (false positives tamed, recall still poor). Mode B is still a placeholder, long files can run out of GPU memory, FILLERS detector missing. Your next job is **detection quality** (B5b), because temporal precision is the biggest scoring lever after the dataset.

## You own (edit freely)
`src/speechcoach/{audio,align,features,compare,explain,scoring}/`, `src/speechcoach/analyze.py`, `configs/thresholds.yaml`, `configs/rubric.yaml`, `configs/sigma.json`, `src/speechcoach/models/` (optional learned layer), `scripts/calibrate.py`, `scripts/run_eval.py`, `scripts/stress_test.py`, `scripts/train_window_model.py`, `scripts/make_plots.py`, `scripts/plot_features.py`, `results/`, `notebooks/`, `tests/test_{audio,align,features,compare,explain,scoring,analyze}*.py`.

## You must NOT edit
`src/speechcoach/dataset/`, `dataset/`, `configs/flaws.yaml`, `src/speechcoach/api/`, `app/`, `Dockerfile`, `Makefile`, `docs/CONTRACTS.md` (without the change protocol).

## What you receive / hand over
- From A: `dataset/` (CONTRACTS sections 2-4). Until it exists, test on `dataset/sample/` and on synthetic signals.
- To C: `analyze(audio_path, transcript, baseline_id, mode) -> AnalysisResult` exactly as in CONTRACTS section 6. Until it is ready, C uses `app/public/mock_result.json`.
- To everyone: `results/metrics_dev.csv`, `results/metrics_test.csv`, plots, and numbers for the technical document.

## Technical guardrails
1. **Follow `docs/ARCHITECTURE.md` formulas exactly.** Do not substitute other statistics. If you believe something is wrong, say so with evidence first.
2. **Speaker-agnostic:** pitch in semitones relative to the file's own median, loudness in dB relative to the file's own 95th percentile, CMVN on MFCC. Prove it with a test on two synthetic "speakers" (same contour at different base pitch gives equal normalized output).
3. All thresholds, floors and weights come from `configs/*.yaml` / `sigma.json`. No magic numbers.
4. **Tune only on DEV** (dev texts T01, T02, T04, T05, speakers in `train`/`val`); pick thresholds on the `val` speakers. TEST-TEXT (T03, T06), TEST-SPEAKER (S11, S12) and the stress texts (T07, T08) are run ONCE after the Day 6 freeze and reported honestly. Never adjust thresholds after looking at test results. Never split clips of one speaker across train and test.
5. Alignment: torchaudio `MMS_FA`, cached per file by content hash. Words with low `conf` produce a warning in `meta.warnings` (possible omission/insertion); do not silently trust them.
6. Explanations are deterministic templates with measured numbers. No LLM, no randomness, no invented facts.
7. Determinism: `analyze()` twice on the same input gives byte-identical JSON (sorted keys, floats rounded to 4 decimals, fixed seeds).
8. Handle edge cases explicitly: all-NaN pitch windows, very short files, transcript mismatch, empty gaps. Return a warning, not a crash.
9. Unit tests use synthetic signals: sine of known F0, silence gaps of known length, a clip sped up by a known factor. Assert on real computed values.
10. Check installed library APIs before use (`parselmouth`, `torchaudio.pipelines.MMS_FA`, `librosa`).
11. Torchaudio is pinned to 2.5.1. If the alignment API fails, tell the human; the fallback is the `ctc-forced-aligner` package (needs approval to add).

12. **Separate alignment error from detector error.** Always report detection with ORACLE word times (label times) next to detection with the real aligner (STRESS_TESTS S13). The low F1 is probably alignment jitter on synthetic files plus window size; measure before changing thresholds again.
13. **Mode B must be real:** no `zeros_like` baselines, no inf/NaN; objective flaws only (see ARCHITECTURE section 8). Label it "No-reference mode" (`meta.mode_label`). Texts T07, T08 are always Mode B in tests.
14. **Features required by the challenge** are all present and documented: FFT-based spectral features (centroid, band energy, flux), MFCC (+delta, CMVN), F0 contour stats (+slope), speech rate (syllables/s, words/s), pause statistics incl. position relative to punctuation, loudness/dynamic range, clarity proxies (flux, HNR, alignment confidence). Add the missing ones in B5c without changing the frozen keys (new keys are additive, CONTRACTS v1.1).
15. **Learned layer is optional and subordinate** (ARCHITECTURE section 11): one small model per family, speaker-grouped validation, never replaces the measured-number explanations. If it does not beat rules-only on validation, ship rules-only and say so.
16. Use the canonical enum `FILLERS` (not `FILLER_WORD`).
17. Report FPR on GOOD speech (per minute and per file) and write `results/stress_*.csv` per `docs/STRESS_TESTS.md`.

## Evaluation you must be able to produce
Temporal grounding: precision/recall/F1 at IoU >= 0.5 (same flaw type), mean start/end error in seconds; recall by severity level L1-L5; flaw-type confusion matrix; Spearman correlation of overall score vs severity level; reproducibility (hash equality across two runs); alignment-vs-ground-truth median error and P90; false-positive rate on ideal files; oracle-vs-real-alignment F1; severity-vs-deviation gradient plot; per-family metrics.

## Typical commands
```
python -m speechcoach.align.run dataset/sample/x.wav dataset/texts/T04.txt --out /tmp/x.json
python -m speechcoach.analyze dataset/sample/x.wav dataset/texts/T04.txt --baseline T04
python scripts/calibrate.py
python scripts/run_eval.py --split dev
```

## Definition of done for any B task
Unit tests pass, a real run on a dataset file printed sensible numbers (shown in the report), no contract fields changed, HANDOFF.md updated with measured results.
