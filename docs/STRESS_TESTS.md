# STRESS_TESTS.md: Stress-test matrix and required plots

Why: Data Engineering and Stress Testing is 30% of the score. This file says what we test, with what data, and what we report. Owner: Member B (runs), Member A (data, verifies and documents). Never tune on TEST sets; evaluation sets are defined in `CONTRACTS.md` 0.1.

## 1. Matrix
| # | Category | Data | Expectation | Output |
|---|---|---|---|---|
| S1 | GOOD speech from unseen speakers | ideal files of `speaker_split` test (h11, h12) and `val` | Few false alarms: <= 1 flagged region/min (target, adjust with team); report share of ideal files with any region | `results/stress_good_fpr.csv` |
| S2 | Subtle level-1 flaws | L1 files, all families | Lower severity and confidence than L4; honestly lower recall | recall by level table |
| S3 | Strong level-4/5 flaws | L4, L5 files | Clear regions, high severity, high confidence | F1@IoU0.5 by level |
| S4 | Unseen text | T7, T8 (stress split; NOT in baseline library) | Analyzer must switch to Mode B ("No-reference mode") and say so; fewer flaw types reported | mode flag check + F1 in prior mode |
| S5 | Unseen speaker | test speakers h11, h12 on dev texts | Normalization keeps speaker identity from driving results; compare score distributions of ideal files across speakers | per-speaker score boxplot |
| S6 | Two simultaneous flaws | composites (5 per text) | Both flaws found, or uncertainty reported; causes not merged into one | per-component recall, confusion matrix |
| S7 | Long pauses and sentence boundaries | PAUSE_EXCESS L4-L5, PAUSE_MISSING | Region boundaries not systematically shifted | mean signed start/end error |
| S8 | Different recording loudness | ideal and flawed files re-gained by -12, -6, +6 dB (create with a script, not new recordings) | Result unchanged except VOLUME_DROP logic stays stable (analysis uses loudness relative to the file's own P95) | max change in z and in score |
| S9 | Noisy but usable recording | ideal files with added room-like noise at 30, 20, 15 dB SNR (script) | Score degrades gracefully; clarity/pitch warnings may appear; no crash | score vs SNR plot |
| S10 | Repeated runs | any 5 files, 2 runs each | Byte-identical JSON | `tests/test_reproducible.py` + hash table |
| S11 | Bad inputs | empty transcript, 1-second audio, silence, wrong text, 30 MB file, .txt as audio | Friendly 400 error or warning, never a stack trace | API test list |
| S12 | Alignment robustness | flawed files: re-aligned word times vs ground-truth time map | Median error in tens of ms; report P90 too | `results/alignment_error.csv` |
| S13 | Oracle vs real alignment | DEV flawed files | Detector F1 with label word times next to F1 with the aligner (separates alignment error from detector error) | table in HANDOFF and tech doc |

## 2. Required plots and tables (for the technical document and video)
1. Severity level vs measured deviation, one panel per flaw (`results/gradient_check.png`; must rise monotonically).
2. Overall score vs severity level, with Spearman correlation (dev).
3. Precision/recall/F1 at IoU >= 0.5 per family and per level; mean start/end error in seconds.
4. Flaw-type confusion matrix (including composites).
5. False-positive rate on GOOD speech (S1) with and without unseen speakers.
6. ROC/PR per family IF the learned scorer (B6f) exists.
7. Score calibration: score vs report severity (0-4).
8. Timestamp overlap: IoU histogram.
Every number in the document comes from `results/*.csv`. If a test was not run, the document says so; no invented numbers.

## 3. Rules
- Settings are frozen before TEST runs; the test run happens once, after the Day 6 freeze; numbers are reported even if poor.
- Failures are kept in a short "limitations" list (what breaks, why), not hidden.
- Stress data built by script (S8, S9) uses a fixed seed and is listed in `dataset/README.md` as derived data.
