# ARCHITECTURE.md: System design, algorithms and formulas

This is the reference for HOW the system works. Do not invent different algorithms. If you think one is wrong, raise it with the human first.

## 1. Data flow
```
Audio + transcript
   │
   ├─ audio.load_audio ............ 16 kHz mono, loudness -23 LUFS
   ├─ align.parse_transcript ...... words with raw / norm / punct
   ├─ align.align_words ........... start, end, conf per word (torchaudio MMS_FA)
   │
   ├─ features.frame_features ..... 10 ms grid: f0, st, db, db_rel, flux, mfcc, hnr
   ├─ features.word_table ......... per-word stats + pause_before
   ├─ features.window_stats ....... sliding 6-word window stats
   │
   ├─ compare.build_baseline ...... from ideal recordings of the same text
   ├─ compare.signals ............. deviation signals (natural units)
   ├─ z = signal / sigma .......... sigma from leave-one-out calibration
   ├─ compare.find_regions ........ flaw regions (word-level, trimmed)
   │
   ├─ explain.explain ............. 5-part deterministic explanation
   ├─ scoring.score ............... 7 dimension scores + overall
   └─ analyze() ................... returns AnalysisResult JSON (see CONTRACTS)
                                         │
                      api (FastAPI) ─────┘───► dashboard (React)
```

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
- **Mode B (prior):** no matching text; baseline from pooled ideal statistics (global pace band, pause length per punctuation type, pitch-std band, loudness dynamics band); fewer flaw types.
The result JSON always states which mode ran.

## 9. Flaw engine principles (Member A)
1. Analyze each ideal once with WORLD (`harvest`, `cheaptrick`, `d4c`, 16 kHz, 5 ms), cache as `.npz`.
2. All time edits are a "time program": a list of source-frame index arrays (pieces at a speed, inserted silence frames, repeated words) concatenated; keep `(source_time, new_time)` anchors so original word times map exactly to the new file.
3. Pitch/spectral edits apply only to frames of the flawed region.
4. EVERY synthetic file, including the unmodified `resynth_control`, passes through the same WORLD analysis-synthesis (prevents "vocoder sound" shortcut).
5. Regions start/end on word boundaries; prefer phrase (punctuation) boundaries.
6. Seed per file = `seed + stable_hash(file_id)`. Never normalize loudness after injecting VOLUME_DROP.

## 10. Quality gates (what "working" means)
- Region detection on synthetic dev set: F1 at IoU>=0.5 high for L3-L5, honestly lower for L1-L2.
- Score decreases monotonically with severity level (Spearman correlation reported).
- Running the pipeline twice gives byte-identical JSON.
- Alignment on flawed files matches the ground-truth time map within tens of milliseconds (median).
