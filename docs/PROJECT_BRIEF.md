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
We create 6 texts. For each we collect/record several **ideal** deliveries (original public-domain speaker where legal + teammates). We generate a **synthetic flaw spectrum** programmatically with the WORLD vocoder (12 flaw types, 5 severity levels L1-L5, plus composites). Because we edit through a known time map, we get **exact ground-truth flaw timestamps for free**. We also record **real human flawed takes** to prove generalization. The analyzer aligns words (MMS_FA), extracts speaker-normalized features, builds a baseline from ideal recordings, calibrates "natural spread" by leave-one-out between ideal speakers, converts deviations to z-scores, groups flagged words into flaw regions, and writes deterministic template explanations containing the measured numbers. A FastAPI + React dashboard renders it all.

## 7. Team and time
3 members (A: Data, B: Pipeline, C: App/Platform). 10 days. Feature freeze at the end of Day 6. Last day is buffer.

## 8. Non-goals (do NOT build these)
Real-time/streaming analysis, user accounts, databases, LLM-generated explanations, speaker identification, languages other than English (unless everything else is done), mobile apps, large-scale training.
