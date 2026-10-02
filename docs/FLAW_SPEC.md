# FLAW_SPEC.md: Flaw taxonomy, severity levels and injection parameters

Owner of content: Member A. Member B reads it. Changes need team agreement (shared file).
The same numbers live in `configs/flaws.yaml`; the YAML is the source the code reads, this file explains it.

## 1. Severity levels
| Level | Meaning |
|---|---|
| L0 | Ideal (or `resynth_control`: the ideal passed through the same WORLD pipeline with NO edit) |
| L1 | Almost perfect: a small flaw most listeners would not notice |
| L2 | Slight |
| L3 | Moderate: clearly noticeable |
| L4 | Severe |
| L5 | Botched: strong flaw over most of the clip |

Both strength and extent grow with level. Extent = share of the clip affected: `[0.10, 0.15, 0.25, 0.40, 0.70]` for L1..L5. The flaw region starts at a phrase (punctuation) boundary and begins/ends on word boundaries.

## 2. Flaw types and what they change
| Flaw | Plain meaning | How it is injected | Measured signature |
|---|---|---|---|
| PACE_FAST | Rushing | time program: region at speed > 1 | words shorter than baseline |
| PACE_SLOW | Dragging | time program: region at speed < 1 | words longer |
| PAUSE_MISSING | Runs through punctuation | shorten pauses after punctuation words to `keep` x original (min 30 ms) | pause_before much shorter at punctuation |
| PAUSE_EXCESS | Over-long pause at correct place | add `add_s` seconds of real room-tone silence at each punctuation pause | pause_before much longer |
| PAUSE_MISPLACED | Pause inside a phrase | insert `n` silences of `dur_s` after random NON-punctuation words | long gap where baseline has none |
| MONOTONE | Flat pitch | `f0' = exp(ref + alpha*(log f0 - ref))`, ref = log of file median F0 | pitch std drops |
| PITCH_ERRATIC | Unnatural pitch wobble | add smoothed random pitch noise (std in semitones) | pitch std rises |
| VOLUME_DROP | Trailing off | gain in dB with 200 ms fades | energy below baseline |
| FLAT_ENERGY | No dynamics | compress loudness variation toward region mean | loudness std drops |
| CLARITY | Mumbling | smooth log spectral envelope over time + high-frequency tilt | spectral flux and HNR drop |
| FILLERS | uh / repeated words | hold a stable vowel of the same speaker (e.g. from "a", "the") with slightly falling pitch; repeat short words twice | voiced gap inside pause; repetition |
| STRESS_MISSING (bonus) | Key word not emphasized | MONOTONE only on key words + lower their loudness 3-6 dB | stress score missing |

## 3. Parameter table (`configs/flaws.yaml`)
```yaml
extent_fraction: [0.10, 0.15, 0.25, 0.40, 0.70]
region_start: phrase_boundary
levels: [1, 2, 3, 4, 5]
full_gradient: [PACE_FAST, PACE_SLOW, MONOTONE, VOLUME_DROP, PAUSE_MISSING, PAUSE_EXCESS]
reduced_gradient: {levels: [1, 3, 5], flaws: [PAUSE_MISPLACED, PITCH_ERRATIC, CLARITY, FILLERS]}
params:
  PACE_FAST:       {speed:   [1.10, 1.20, 1.35, 1.55, 1.80]}
  PACE_SLOW:       {speed:   [0.92, 0.85, 0.72, 0.58, 0.45]}
  MONOTONE:        {alpha:   [0.85, 0.70, 0.50, 0.25, 0.00]}
  VOLUME_DROP:     {gain_db: [-2, -4, -7, -11, -16]}
  PAUSE_MISSING:   {keep:    [0.70, 0.50, 0.30, 0.10, 0.00]}
  PAUSE_EXCESS:    {add_s:   [0.25, 0.45, 0.70, 1.00, 1.40]}
  PAUSE_MISPLACED: {n: [1, 2, 3, 4, 5], dur_s: [0.35, 0.5, 0.7, 0.9, 1.2]}
  PITCH_ERRATIC:   {std_st:  [0.5, 1.0, 2.0, 3.0, 4.5]}
  CLARITY:         {smooth_frames: [3, 5, 9, 15, 25], tilt_db: [0, 1, 2, 4, 6]}   # frame = 5 ms
  FILLERS:         {n: [1, 2, 4, 6, 9], hold_s: [0.3, 0.35, 0.4, 0.45, 0.5]}
composites:    # 5 per text, levels 2-4
  - [PACE_FAST, MONOTONE]
  - [VOLUME_DROP, CLARITY]
  - [PAUSE_MISPLACED, FILLERS]
  - [PACE_SLOW, FLAT_ENERGY]
  - [PACE_FAST, PAUSE_MISSING, MONOTONE]
```
Files per text: 1 control + 6x5 + 4x3 + 5 composites = 48. Six texts = about 290 files.

## 4. Human flaw cards (real recordings)
| Card | Instruction | Maps to |
|---|---|---|
| A | Rush the second half | PACE_FAST |
| B | Read like a train timetable | MONOTONE, FLAT_ENERGY |
| C | Say "umm/uh" 6-8 times | FILLERS |
| D | Fade out in the last two lines | VOLUME_DROP |
| E | Pause awkwardly mid-sentence | PAUSE_MISPLACED |
| F | Mumble the middle section | CLARITY |
| G | Almost perfect: one slightly rushed sentence | PACE_FAST (L1-like) |
Human flaw times are annotated by listening in Audacity (labels exported as txt, converted by `scripts/audacity_to_labels.py`).

## 5. Quality rules
- Listen to at least 3 files per flaw type; it must sound like a human flaw, not a glitch.
- Crossfade 5-10 ms at every splice.
- Measured deviation must grow monotonically from L1 to L5 per flaw (plot in `results/gradient_check.png`).
- Regenerating with the same config and seed must give identical files.
- Re-run forced alignment on a sample of flawed files and compare with ground-truth word times (report median error).
