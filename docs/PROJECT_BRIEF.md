# PROJECT_BRIEF.md: What the hackathon asks and what we build

## 1. The challenge (Track C: Contrastive Speech Analytics & Temporal Flaw Grounding)
Build a speech evaluation system that:
1. uses a **custom contrastive dataset** of "ideal" vs "flawed" recordings of the **same text**, covering a gradient from egregiously bad to near-perfect,
2. produces **reproducible, rubric-based scores** and **actionable delivery feedback**,
3. shows them in an **interactive dashboard**.

Why: human judges of Interpretive Reading, Declamation, Extemporaneous and Persuasive Oratory score inconsistently and give vague feedback. No public dataset maps good delivery against many bad deliveries of the same text.

## 2. Requirements (from the problem statement)
1. **Dataset and stress testing:** "good" baseline recordings with transcripts; a "bad" spectrum (synthesized, self-recorded or modified) of the exact same transcripts; accurate, temporally bounded labels.
2. **Feature extraction and forced alignment:** map transcript to audio timestamps; extract FFT, MFCC, pitch/F0 contours, speech rate, pause intervals, vocal clarity.
3. **Temporal grounding and causal flaw extraction:** isolate start/end timestamps of flaw regions; translate raw mathematical deltas into a structured, human-readable causal explanation per flaw.
4. **Visualization:** a frontend that accepts audio and transcript uploads and renders a time-series overlay of baseline vs participant features, highlighting flaw regions with their explanations.

## 3. Technical considerations (from the statement)
- Quality over quantity: a clean aligned contrastive spectrum beats a big noisy corpus.
- **Speaker-agnostic:** normalize pitch and energy so different voices are comparable.
- Flaw regions need enough temporal precision to support causal explanation.
- **Reproducible** across repeated runs and deployment environments.

## 4. Evaluation weights (what judges score)
| Criterion | Weight | What matters |
|---|---|---|
| Data Engineering and Stress Testing | 30% | Baseline sourcing, clean temporal labels, robust bad-mirror gradient |
| Causal Explainability and Temporal Grounding | 25% | Timestamp accuracy; clear mathematical rationale |
| Feature Extraction | 20% | Rigor of acoustic processing; stress-point and energy-contour accuracy |
| Visualization and Dashboard | 15% | Frontend execution, usability, clarity of time-series and explanations |
| Reproducibility and Code Quality | 10% | Clean execution, deployment instructions, architecture |

## 5. Deliverables
GitHub repo (code + docs) · the dataset (audio, transcripts, alignment labels; in GitHub or a public Drive link in README) · working dashboard · technical document (max 6 pages) · 3-10 minute YouTube video.

## 6. Our approach in one paragraph
We use **8 texts**: T01-T04 are the four public speeches already prepared (ideal audio done) and T05-T08 are **original, team-written 100-130 word texts** (no licensing problems). For each text we collect several **ideal** deliveries (the original speaker where legal, plus teammates and volunteers). We generate a **synthetic flaw spectrum** programmatically with the WORLD vocoder (6 flaw **families**, 14 flaw types, 5 severity levels L1-L5, plus composites). Because we edit through a known time map, we get **exact ground-truth flaw timestamps for free**. We also record **real human flawed takes** to prove generalization. The analyzer aligns words (MMS_FA), extracts speaker-normalized features, builds a baseline from ideal recordings, calibrates "natural spread" by leave-one-out between ideal speakers, converts deviations to z-scores, groups flagged words into flaw regions (optionally confirmed by a small learned window scorer), and writes deterministic template explanations containing the measured numbers. A FastAPI + React dashboard renders it all. The hybrid idea (baseline deviation supplies the *reason*, an optional learned score supports the *decision*) follows the Track C A-to-Z build plan.

## 7. Team and time
**3 members**: A Data, B Pipeline, C App/Platform. 10 days, Day 1 = 2026-10-03 (assumed; put the real deadline in `HANDOFF.md` section 1). Feature freeze at the end of Day 6. Last day is buffer.

## 8. Non-goals (do NOT build these)
Real-time/streaming analysis, user accounts, databases, LLM-generated explanations, speaker identification, languages other than English (unless everything else is done), mobile apps, large-scale training, Mode C (coach uploads their own reference recording; optional extension only, never before freeze).

## 9. Source boundary (what the challenge requires vs what we chose)
The challenge text requires: a custom good/bad contrastive dataset, temporal labels, forced alignment, acoustic features, temporal flaw grounding, causal explanations, an uploadable dashboard, documentation, a GitHub dataset/codebase, a 3-10 minute video. It does **not** prescribe speaker count, text count, flaw types, severity scale, model family, scoring formula or recording format. Everything we list for those is an engineering choice, and the technical document must say so.

## 10. Acceptance checklist (from the Track C build plan; status as of 2026-10-06)
Do not call the project finished until every line is demonstrably working. `[x]` done, `[~]` partly, `[ ]` not started. Update this table at the evening sync.
| # | Criterion | Status |
|---|---|---|
| 1 | Clean GOOD recordings completed and backed up (T01-T04 originals + teammates; T05-T08 x up to 12 speakers; see TASKS D2-D4) | [~] 4 originals done, rest not started |
| 2 | Each GOOD file maps to exactly one speaker and one text (`file_id`, `metadata.csv`) | [~] |
| 3 | Flawed files use the exact same transcript as their GOOD reference | [~] true by construction for synthetic; human takes not yet checked |
| 4 | All six flaw families have multiple severity levels | [~] pacing (and some others) on T01; emphasis family not built |
| 5 | Every intentional flaw has temporal start/end labels | [~] synthetic yes; human takes pending |
| 6 | Speaker-independent splits fixed BEFORE final evaluation (speaker split + text split) | [ ] written in CONTRACTS 0.1, not yet in `metadata.csv` |
| 7 | Forced alignment available and manually sanity-checked (every speaker, every flaw family) | [~] alignment works; no manual sanity log yet |
| 8 | Features cover the challenge categories: FFT/spectral, MFCC, F0, speech rate, pauses, clarity | [~] spectral centroid, MFCC delta, F0 slope, pause position still to add (B5c) |
| 9 | Pitch and energy are speaker-normalized | [x] with test |
| 10 | Window-level evidence and temporal smoothing give readable start/end regions | [~] works; F1 still low (see HANDOFF) |
| 11 | Each region has a mathematical deviation and a causal explanation | [x] templates exist |
| 12 | Dashboard accepts audio + transcript; shows reference vs no-reference mode | [~] upload on mock data done; real integration to verify (C4) |
| 13 | Unseen-speaker and unseen-text tests included (`docs/STRESS_TESTS.md`) | [ ] |
| 14 | Repeated runs reproducible (byte-identical JSON) | [ ] test not written |
| 15 | GitHub has code + docs (`docs/dataset.md`, `methodology.md`, `scoring.md`, `demo.md`, LICENSE) | [ ] |
| 16 | Dataset documentation: transcripts, alignments, metadata, licenses | [~] SOURCES.md exists |
| 17 | Technical document <= 6 pages | [ ] |
| 18 | Demo video 3-10 minutes | [ ] |
