# ARCHITECTURE.md: System design, algorithms and formulas

This is the reference for HOW the system works. Do not invent different algorithms. If you think one is wrong, raise it with the human first.

## 1. Data flow
```
Audio + transcript
   │
   ├─ audio.load_audio ............ 16 kHz mono, loudness -23 LUFS
   ├─ align.parse_transcript ...... words with raw / norm / punct
   ├─ align.align_words ........... start, end, conf per word (torchaudio MMS_FA)
   ├─ transcript validation ....... low-conf words / big gaps -> meta.warnings (no ASR dependency; see 1.1)
   │
   ├─ features.frame_features ..... 10 ms grid: f0, st, db, db_rel, flux, mfcc, hnr
   ├─ features.word_table ......... per-word stats + pause_before
   ├─ features.window_stats ....... sliding 6-word window stats
   │
   ├─ compare.build_baseline ...... from ideal recordings of the same text
   ├─ compare.signals ............. deviation signals (natural units)
   ├─ z = signal / sigma .......... sigma from leave-one-out calibration
   ├─ compare.find_regions ........ flaw regions (word-level, trimmed)
   ├─ [optional] learned window scorer ... per-family probability -> confidence (see 11)
   │
   ├─ explain.explain ............. 5-part deterministic explanation
   ├─ scoring.score ............... 7 dimension scores + overall
   └─ analyze() ................... returns AnalysisResult JSON (see CONTRACTS)
                                         │
                      api (FastAPI) ─────┘───► dashboard (React)
```

### 1.1 Mapping to the Track C plan's pipeline
| Plan step | Our implementation |
|---|---|
| ASR / transcript validation | Transcript is user-supplied. Validation = forced-alignment confidence: words with `conf` below `thresholds.yaml: min_conf`, or a mean confidence drop, produce `meta.warnings` ("transcript may not match audio"). A real ASR pass is NOT required (non-goal). |
| 2-3 s sliding windows with overlap | `window_stats` uses W=6 words, stride 1, centered (7 words, about 2-3 s of speech at 2.5-3 words/s), so neighbouring windows overlap by 6 of 7 words. Same config in calibration and inference. |
| Speaker normalization | Section 2 (semitones, dB re P95, CMVN). Plan formula `z=(x-mu_spk)/sigma_spk` is the alternative; ours is per-recording because a judge uploads one file. |
| Flaw-specific detectors | One signal per flaw family (section 4/5) plus the optional learned scorer (section 11). |
| Temporal smoothing and region merging | `max_gap_words` bridging + trimming (section 5). |
| Severity + confidence | Severity from mean |z| (section 5); confidence from section 11 (v1.1). |
| Causal explanation, dashboard overlay | Sections 6 and CONTRACTS 6. |

Dataset side (Member A) runs separately:
```
ideal wav ─► WORLD analysis (f0, sp, ap) cached ─► "time program" (pace/pause/repeat)
          ─► parameter edits in the flaw region (pitch / spectrum) ─► synthesize
          ─► gain edits (volume) ─► save wav + label JSON with exact flaw times
```

## 2. Normalization (speaker-agnostic)
| Quantity | Formula |
|---|---|
| Pitch | `st = 12 * log2(f0 / median(f0 of this recording))` (unvoiced = NaN) |
| Loudness | `db_rel = 20*log10(rms) - percentile(20*log10(rms), 95)` |
| Spectral | MFCC with per-recording mean/variance normalization (CMVN); spectral features on an 80-4000 Hz band-passed copy |
| Pace | no per-speaker normalization; natural tempo differences are absorbed by sigma (see 4) |

F0 extraction: Praat autocorrelation via parselmouth, two passes. Pass 1: floor 75, ceiling 600 Hz. Pass 2: `floor = max(60, 0.75*Q1)`, `ceiling = min(800, 1.5*Q3)` of pass-1 voiced F0, `very_accurate=True`. Hop 0.01 s.

## 3. Window statistics (W = 6 words, stride 1, centered on each word)
Per word `i`, half-width is W // 2 = 3. The window is words `i-3 .. i+3` (which is 7 words total, clipped at the ends). Computed: `win_dur` (sum of word durations, pauses excluded), `f0_std` (std of `st`, NaN-aware), `db_mean`, `db_std` (over frames inside words), `flux` (mean spectral flux inside words).

## 4. Baseline, signals, calibration
Baseline for a text B = per-word aggregate over its ideal recordings: geometric mean for `win_dur, f0_std, db_std, flux`; arithmetic mean for `db_mean, pause_before`.

Deviation signals of participant P vs baseline B (per word):
```
pace      = log(P.win_dur / B.win_dur)      # <0 faster, >0 slower
pause     = P.pause_before - B.pause_before # seconds
pitch     = log(P.f0_std / B.f0_std)        # <0 flatter (monotone), >0 more wobble
energy    = P.db_mean - B.db_mean           # dB, <0 quieter
dynamics  = log(P.db_std / B.db_std)        # <0 flatter loudness
clarity   = log(P.flux / B.flux)            # <0 less articulation movement
```
**Calibration (leave-one-out):** for each ideal recording, compute its signals against the baseline built from the OTHER ideals of the same text. Pool all values per signal across all texts. `sigma = max(1.4826 * MAD(values), sigma_floor[signal])`. Saved to `configs/sigma.json`. Then `z = signal / sigma`.
Meaning: z = 3 means "3x more different from baseline than two good speakers normally are from each other".

### 4.1 Flaw families (plan terms) and our signals
| Family (plan) | Flaw types | Signal | Dimension |
|---|---|---|---|
| Pacing | PACE_FAST, PACE_SLOW | pace | pacing |
| Pausing | PAUSE_MISSING, PAUSE_EXCESS, PAUSE_MISPLACED, (FILLERS counted in fluency) | pause, filled-pause detector | pausing, fluency |
| Monotony / pitch variation | MONOTONE, PITCH_ERRATIC | pitch | pitch |
| Volume dynamics | VOLUME_DROP, FLAT_ENERGY | energy, dynamics | energy |
| Articulation / clarity | CLARITY | clarity | clarity |
| Emphasis / stress | STRESS_MISSING, STRESS_EXAGGERATED | emphasis (4.2) | emphasis |

A large deviation is evidence ONLY for the family it is causally tied to (e.g. a pace deviation is never reported as MONOTONE). Composite files test that causes stay separated.

### 4.2 Emphasis signal [v1.1 PROPOSED, implement after B5b]
Per word: `stress_i = mean(zr(st_peak_i), zr(db_peak_i), zr(dur_i))`, where `zr` is the within-recording z-score of the word's pitch peak (semitones), loudness peak (dB re P95) and duration. Baseline stress per word = mean over ideals. Key words of a text = words whose baseline stress is in the top 15%. `emphasis = P.stress - B.stress`. Negative on key words = STRESS_MISSING; positive on non-key words = STRESS_EXAGGERATED. Thresholds in `thresholds.yaml`. Until implemented, the emphasis dimension score is reported as null with a warning, not as a fake number.

## 5. Flaw regions
Per signal and sign (+/-): flag word if `sign*z > tau_flag`; bridge gaps of `max_gap_words`; group consecutive flagged words; trim ends where `sign*z < tau_trim`; keep if `>= min_region_words` words AND `>= min_region_s` seconds (pause and filler events are exempt: single events allowed). All thresholds in `configs/thresholds.yaml`.
`severity = clip((mean|z| - 1.5) / 4.5, 0, 1)`. Bands: minor `|z|>=2`, moderate `>=3`, major `>=4.5`.

| Signal | Negative z | Positive z |
|---|---|---|
| pace | PACE_FAST | PACE_SLOW |
| pause | PAUSE_MISSING (only where transcript has punctuation) | PAUSE_EXCESS (at punctuation) / PAUSE_MISPLACED (no punctuation) |
| pitch | MONOTONE | PITCH_ERRATIC |
| energy | VOLUME_DROP | (ignored) |
| dynamics | FLAT_ENERGY | (ignored) |
| clarity | CLARITY | (ignored) |
| filled-pause detector | n/a | FILLERS |

Filled pause: a gap between words longer than `filled_pause_min_s` where more than 60% of frames are voiced and above the silence level.

## 6. Explanations (deterministic templates, NO LLM)
Each flaw gets 5 fields: `observed`, `deviation`, `where`, `why`, `fix`. All numbers come from measured data (raw value, baseline value, z-score, time range, word indices). `why` and `fix` come from a fixed dictionary keyed by flaw type.

## 7. Scoring
Per word per dimension: `p = clip((|z| - z_free) / (z_max - z_free), 0, 1)` (`z_free=1`, `z_max=4`). Dimension deviation `D = 0.6*mean(p) + 0.4*P90(p)`. Dimension score `= 100*(1 - D)`. Overall `= sum(weight_d * score_d)` with weights from `configs/rubric.yaml`. Dimension to signal map: pacing<-pace, pausing<-pause, pitch<-pitch, energy<-energy+dynamics (average), emphasis<-stress match, clarity<-clarity, fluency<-filled pauses/omissions per minute.

## 8. Modes
- **Mode A (reference):** transcript matches a library text; baseline from that text's ideals.
- **Mode B (prior):** no matching text; baseline dynamically synthesized from global statistics (e.g., character-length duration estimates, punctuation-based pause rules, global flat medians for pitch/energy). Uses wider `tau` thresholds. It evaluates objective mistakes (`PACE_FAST`, `PACE_SLOW`, `MONOTONE`, `PAUSE_EXCESS`, `CLARITY`, `FILLERS`) but ignores artistic flaws (`PAUSE_MISPLACED`, `VOLUME_DROP`) to prevent false positives.
The dashboard calls Mode B "No-reference mode" and states in plain words that the baseline is pooled, not text-specific. If alignment confidence is low in Mode B, report fewer flaw types and say so in `meta.warnings`. The result JSON always states which mode ran. If `aligner` causes CUDA OOM on long files in either mode, it automatically triggers a CPU Fallback to ensure completion.

## 9. Flaw engine principles (Member A)
1. Analyze each ideal once with WORLD (`harvest`, `cheaptrick`, `d4c`, 16 kHz, 5 ms), cache as `.npz`.
2. All time edits are a "time program": a list of source-frame index arrays (pieces at a speed, inserted silence frames, repeated words) concatenated; keep `(source_time, new_time)` anchors so original word times map exactly to the new file.
3. Pitch/spectral edits apply only to frames of the flawed region.
4. EVERY synthetic file, including the unmodified `resynth_control`, passes through the same WORLD analysis-synthesis (prevents "vocoder sound" shortcut).
5. Regions start/end on word boundaries; prefer phrase (punctuation) boundaries.
6. Seed per file = `seed + stable_hash(file_id)`. Never normalize loudness after injecting VOLUME_DROP.

## 10. Quality gates (what "working" means)
Evaluation sets (fixed in CONTRACTS 0.1): DEV = dev texts x train/val speakers (tuning allowed); TEST-TEXT = T3, T6; TEST-SPEAKER = speakers h11, h12 on dev texts; STRESS = T7, T8 (unseen text, forced Mode B), composites, noise, loudness changes. TEST sets are run ONCE after freeze of thresholds.
- Region detection on synthetic dev set: F1 at IoU>=0.5 high for L3-L5, honestly lower for L1-L2.
- Score decreases monotonically with severity level (Spearman correlation reported).
- Running the pipeline twice gives byte-identical JSON.
- False-positive rate on ideal (GOOD) files, including unseen speakers: reported as flagged regions per minute and share of ideal files with any region at all. Target (adjust with the team): <= 1 region/min.
- Detection with ORACLE word times (label times instead of the aligner) is reported next to detection with real alignment, so alignment error and detector error are separated.
- Severity vs measured deviation plot per flaw (`results/gradient_check.png`) and flaw-type confusion matrix; ROC/PR per family only if the learned scorer exists.
- Alignment on flawed files matches the ground-truth time map within tens of milliseconds (median).

## 11. Optional learned layer (hybrid, [v1.1 PROPOSED], task B6f)
Purpose: the z-score rules decide with fixed thresholds; a small model can learn which windows really are flawed and give a `confidence`. It never replaces the explanation: reasons and numbers always come from the measured signals (section 6).
- Input per word window: the z-signals (pace, pause, pitch, energy, dynamics, clarity, emphasis), their window means, neighbours at +-1 word, and mode flag. NO raw absolute pitch or loudness.
- Model: one light tree-based classifier per family (XGBoost or sklearn `GradientBoostingClassifier`; sklearn is acceptable if XGBoost is awkward on CPU), fixed `random_state`, labels from `labels/*.json` (word inside a flaw region of that family, severity as optional regression target).
- Training data: synthetic + human files of TRAIN speakers on DEV texts only. Splits grouped by speaker (never random clips). Validation speakers (h9, h10) choose thresholds. Test speakers/texts are touched once.
- Use: `confidence = p_family` for each merged region; a region is kept if rule evidence passes AND `p >= p_min` (from `thresholds.yaml`), or if rule evidence is very strong (|z| >= tau_override). Report the rules-only and hybrid F1 side by side; keep whichever is better on validation and say so honestly.
- Fallback: if the model file is missing, `analyze()` runs rules-only and sets `confidence = null`. Output stays deterministic (fixed seed, saved model).
