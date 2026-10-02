# MEMBER_B_PIPELINE.md: Role file for Member B (Signal / Analysis Engineer)

## Mission
Own the **analyzer** (feature extraction 20% + temporal grounding and explainability 25% of the score): forced alignment, acoustic features, normalization, baseline, calibration, flaw regions, explanations, scoring, evaluation.

## You own (edit freely)
`src/speechcoach/{audio,align,features,compare,explain,scoring}/`, `src/speechcoach/analyze.py`, `configs/thresholds.yaml`, `configs/rubric.yaml`, `configs/sigma.json`, `scripts/calibrate.py`, `scripts/run_eval.py`, `scripts/make_plots.py`, `scripts/plot_features.py`, `results/`, `notebooks/`, `tests/test_{audio,align,features,compare,explain,scoring,analyze}*.py`.

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
4. **Tune only on the dev split** (T1, T2, T4, T5). The test split (T3, T6 and held-out humans) is run ONCE at the end of Day 6/7 and reported honestly. Never adjust thresholds after looking at test results.
5. Alignment: torchaudio `MMS_FA`, cached per file by content hash. Words with low `conf` produce a warning in `meta.warnings` (possible omission/insertion); do not silently trust them.
6. Explanations are deterministic templates with measured numbers. No LLM, no randomness, no invented facts.
7. Determinism: `analyze()` twice on the same input gives byte-identical JSON (sorted keys, floats rounded to 4 decimals, fixed seeds).
8. Handle edge cases explicitly: all-NaN pitch windows, very short files, transcript mismatch, empty gaps. Return a warning, not a crash.
9. Unit tests use synthetic signals: sine of known F0, silence gaps of known length, a clip sped up by a known factor. Assert on real computed values.
10. Check installed library APIs before use (`parselmouth`, `torchaudio.pipelines.MMS_FA`, `librosa`).
11. Torchaudio is pinned to 2.5.1. If the alignment API fails, tell the human; the fallback is the `ctc-forced-aligner` package (needs approval to add).

## Evaluation you must be able to produce
Temporal grounding: precision/recall/F1 at IoU >= 0.5 (same flaw type), mean start/end error in seconds; recall by severity level L1-L5; flaw-type confusion matrix; Spearman correlation of overall score vs severity level; reproducibility (hash equality across two runs); alignment-vs-ground-truth median error.

## Typical commands
```
python -m speechcoach.align.run dataset/sample/x.wav dataset/texts/T4.txt --out /tmp/x.json
python -m speechcoach.analyze dataset/sample/x.wav dataset/texts/T4.txt --baseline T4
python scripts/calibrate.py
python scripts/run_eval.py --split dev
```

## Definition of done for any B task
Unit tests pass, a real run on a dataset file printed sensible numbers (shown in the report), no contract fields changed, HANDOFF.md updated with measured results.
