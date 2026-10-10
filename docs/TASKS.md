# TASKS.md: Track C Detailed 3-Member Execution Plan

This is the shared task board tracking the 20-day execution plan. Each member owns their deliverables.
Legend: **[A]** Data, **[B]** Pipeline, **[C]** App/Platform.
Status: `[x]` done and verified, `[~]` partly done, `[ ]` open.

---
## Status board (2026-10-10)
- **Current Phase:** We have completed the structural rewrite and engine foundations. Audio collection (Member A) is the long pole.
- **Biggest risks:** (1) human recordings not started (64 takes needed); (2) pandas logic in pipeline needs update after structural rewrite; (3) detection quality.

---
## 20-day checklist

### Day 1
- [x] **A:** Finalize 8 texts, IDs, metadata schema and recording instructions. (Texts T01-T04 done; structure rewritten).
- [x] **B:** Choose feature list, model approach and pipeline design.
- [x] **C:** Choose frontend/backend stack; create wireframes and Git repo.

### Day 2
- [x] **A:** Record 1 speaker's 8 GOOD texts as a pilot.
- [x] **B:** Build audio loading and file-quality checks.
- [x] **C:** Create app skeleton and audio/transcript upload screen.

### Day 3
- [x] **A:** Review pilot quality; fix recording instructions.
- [x] **B:** Implement resampling, mono conversion and duration checks.
- [x] **C:** Build results-page layout using mock data.

### Day 4
- [x] **A:** Record GOOD samples for speakers S01–S04.
- [x] **B:** Prototype feature extraction on pilot recordings.
- [x] **C:** Create timeline and flaw-card components.

### Day 5
- [ ] **A:** Record GOOD samples for S05–S08.
- [x] **B:** Save window-level features to CSV/Parquet.
- [~] **C:** Build backend upload endpoint and processing status.

### Day 6
- [ ] **A:** Review recordings and prepare metadata.
- [x] **B:** Validate feature outputs on varied speakers.
- [~] **C:** Connect upload screen to backend.

### Day 7
- [ ] **A:** Audit all 64 GOOD files and complete recordings.csv.
- [x] **B:** Create baseline statistics and speaker-normalization functions.
- [x] **C:** Show mock baseline overlays and summary cards.

### Day 8
- [~] **A:** Plan flaw coverage across speakers/texts/severities. (Synthetic flaws generated; human flaws pending).
- [x] **B:** Integrate forced alignment and inspect word timestamps.
- [x] **C:** Add audio player and timeline interaction.

### Day 9
- [x] **A:** Create and label first pacing/pausing flawed samples.
- [x] **B:** Implement deviation metrics and first pacing/pausing detectors.
- [x] **C:** Define agreed JSON response schema with B.

### Day 10
- [ ] **A:** Create and label monotony/volume samples.
- [ ] **B:** Implement pitch and energy feature detectors.
- [ ] **C:** Connect results JSON to UI.

### Day 11
- [ ] **A:** Create and label clarity/emphasis samples.
- [ ] **B:** Implement remaining detector prototypes.
- [ ] **C:** Display flaw type, severity, timestamps and confidence.

### Day 12
- [ ] **A:** Audit flaw labels and severity balance.
- [ ] **B:** Train baseline models using training speakers only.
- [ ] **C:** Display observed values versus expected baseline.

### Day 13
- [ ] **A:** Create composite flaws and additional subtle cases.
- [ ] **B:** Implement window smoothing and merge neighboring regions.
- [ ] **C:** Clicking a flaw jumps playback to its timestamps.

### Day 14
- [ ] **A:** Review false positives on GOOD recordings.
- [ ] **B:** Add severity scoring and explanation metrics.
- [ ] **C:** Build reference/no-reference mode indicators.

### Day 15
- [ ] **A:** Finish dataset README and label documentation.
- [ ] **B:** Evaluate on validation speakers; tune thresholds.
- [ ] **C:** Integrate error handling and processing progress.

### Day 16
- [ ] **A:** Run final dataset integrity checks.
- [ ] **B:** Test unseen speakers and unseen texts; record metrics.
- [ ] **C:** Run end-to-end tests using actual audio.

### Day 17
- [ ] **A:** Review mislabeled or questionable regions with B.
- [ ] **B:** Fix detection errors and generate evaluation plots.
- [ ] **C:** Polish charts, layout, and audio playback.

### Day 18
- [ ] **A:** Freeze dataset splits and release candidate.
- [ ] **B:** Freeze model/configuration and test reproducibility.
- [ ] **C:** Write deployment instructions and connect clean startup.

### Day 19
- [ ] **A:** Provide dataset/method details for report.
- [ ] **B:** Write model, features, evaluation and scoring sections.
- [ ] **C:** Finish technical document and record demo draft.

### Day 20
- [ ] **A:** Verify dataset files and public-access plan.
- [ ] **B:** Run the final test suite and save results.
- [ ] **C:** Record 3–10 minute demo and verify the complete submission.
