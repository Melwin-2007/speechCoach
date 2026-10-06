# FLAW_SPEC.md: Flaw taxonomy, severity levels and injection parameters

Owner of content: Member A. Member B reads it. Member A checks it by listening (QC). Changes need team agreement (shared file).

**Updated 2026-10-06 for the Track C build plan:** flaws are grouped into six **families** (pacing, pausing, pitch/monotony, volume dynamics, articulation/clarity, emphasis); the emphasis family is now core (it was a bonus); FLAT_ENERGY gets its own gradient; STRESS_EXAGGERATED is added. Values marked `(proposed)` are starting points that Member A tunes until the gradient plot rises monotonically.
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

**Mapping to the plan's 0-4 scale (for tables and the technical document only; files keep L1-L5):** L0 -> 0 good; L1, L2 -> 1 subtle; L3 -> 2 noticeable; L4 -> 3 strong; L5 -> 4 extreme. We keep five levels because the repo, labels and 30 existing files already use them and a finer gradient is a plus for the "egregious to almost perfect" requirement.

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
| FLAT_ENERGY | No dynamics | compress loudness variation toward region mean (`ratio` = share of variation kept) | loudness std drops |
| STRESS_MISSING (core) | Key words not emphasized | on the `n_words` key words: shrink pitch excursion (`alpha`) and lower loudness (`gain_db`) | emphasis signal negative on key words |
| STRESS_EXAGGERATED | Over-stressing ordinary words | on `n_words` NON-key words: raise loudness (`gain_db`) and add a pitch excursion (`boost_st`) | emphasis signal positive on non-key words |

**Key words** are chosen deterministically from the ideal recording itself: the top 15% of words by `stress_i` (ARCHITECTURE 4.2), at most `n_words` of them inside the flaw region, longest content words first. No hand-picking, so labels are reproducible.

## 3. Parameter table (`configs/flaws.yaml`)
```yaml
extent_fraction: [0.10, 0.15, 0.25, 0.40, 0.70]
region_start: phrase_boundary
levels: [1, 2, 3, 4, 5]
full_gradient: [PACE_FAST, PACE_SLOW, MONOTONE, VOLUME_DROP, PAUSE_MISSING, PAUSE_EXCESS, STRESS_MISSING]   # STRESS_MISSING added
reduced_gradient: {levels: [1, 3, 5], flaws: [PAUSE_MISPLACED, PITCH_ERRATIC, CLARITY, FILLERS, FLAT_ENERGY, STRESS_EXAGGERATED]}   # last two added
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
  FLAT_ENERGY:     {ratio: [0.85, 0.70, 0.50, 0.30, 0.10]}                    # (proposed)
  STRESS_MISSING:  {alpha: [0.8, 0.6, 0.4, 0.2, 0.0], gain_db: [-1, -2, -3, -4.5, -6], n_words: [1, 2, 3, 4, 6]}   # (proposed)
  STRESS_EXAGGERATED: {gain_db: [2, 4, 6, 8, 10], boost_st: [1.5, 3, 4, 5, 6], n_words: [1, 2, 3, 4, 5]}          # (proposed; used at levels 1,3,5)
composites:    # 5 per text, levels 2-4
  - [PACE_FAST, MONOTONE]
  - [VOLUME_DROP, CLARITY]
  - [PAUSE_MISPLACED, FILLERS]
  - [PACE_SLOW, FLAT_ENERGY]
  - [PACE_FAST, PAUSE_MISSING, MONOTONE]
```
Files per text: 1 control + 7x5 (full gradient) + 6x3 (reduced) + 5 composites = 59. Eight texts = about 470 synthetic files, inside the plan's 400-600 target for flawed recordings (plus the human takes below). T1 already has the original 30-file pacing/monotone/volume/pause set; A3 adds the rest.

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
| H | Stress the wrong words (loud, pitchy on small words) | STRESS_EXAGGERATED |
| I | Read every word with equal weight, no emphasis anywhere | STRESS_MISSING |
| J | Speak softly and flat, but at normal speed | VOLUME_DROP + FLAT_ENERGY (composite check) |

Each human take: the speaker records the SAME text as their ideal take, in the same room and phone position (see `docs/RECORDING_PROTOCOL.md`), and flaws only the region named on the card (read the card aloud to the speaker with the start and end words). Member A logs the intended region on the recording sheet before the take, so a rough label exists even before Audacity annotation.
Human flaw times are annotated by listening in Audacity (labels exported as txt, converted by `scripts/audacity_to_labels.py`).

## 5. Quality rules
- Listen to at least 3 files per flaw type; it must sound like a human flaw, not a glitch. Member A keeps the listening notes in `dataset/QC_LOG.md` (file_id, flaw, level, audible Y/N, level feels right Y/N, notes).
- No UNINTENDED major flaw: a PACE_FAST file must not also be monotone or clipped. A computed side-check (the other families' z stay below the minor band outside the labeled region) is reported per flaw type; files that fail are regenerated or flagged.
- The transcript is never changed in a mirrored file; word sequence in `words` equals the ideal's (resynth or human take of the same text).
- Level 1 must be measurably smaller than level 4 on the target feature, even if a casual listener barely notices it (plan: subtle but detectable).
- Crossfade 5-10 ms at every splice.
- Measured deviation must grow monotonically from L1 to L5 per flaw (plot in `results/gradient_check.png`).
- Regenerating with the same config and seed must give identical files.
- Re-run forced alignment on a sample of flawed files and compare with ground-truth word times (report median error).
