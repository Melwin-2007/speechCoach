# MEMBER_A_DATA.md: Role file for Member A (Data Engineer)

## Mission
Own the **dataset** (30% of the score): texts, ideal recordings, the synthetic flaw spectrum with exact labels, real human flawed recordings, quality control, publishing. Everything the analyzer is tested on comes from here. You coordinate the human recording sessions and listening QC; you build the files, labels and metadata.

**Status (2026-10-06, Day 4):** A1 done (T01-T04 ideal audio, transcripts, SOURCES.md). A2 done (WORLD engine, PACE_FAST). A3 in progress (30 synthetic files exist; remaining flaw types, FLAT_ENERGY, STRESS_* and composites to build). T05-T08 texts are written by D (task D1); you ingest them.

## You own (edit freely)
`src/speechcoach/dataset/`, `dataset/`, `data/`, `configs/flaws.yaml`, `scripts/prepare_audio.py`, `scripts/validate_labels.py`, `scripts/audacity_to_labels.py`, `scripts/upload_dataset.sh`, `scripts/download_dataset.sh`, `scripts/make_stress_variants.py` (loudness and noise variants), `tests/test_dataset*.py`, `dataset/README.md` (dataset card), `dataset/SOURCES.md`, `dataset/metadata/recordings.csv`. You edit `dataset/QC_LOG.md`, `dataset/texts/T05-T08.txt` and the recording sheet.

## You must NOT edit
`src/speechcoach/{audio,align,features,compare,explain,scoring}/`, `configs/thresholds.yaml`, `configs/rubric.yaml`, `src/speechcoach/api/`, `app/`, `Dockerfile`, `Makefile`, `docs/CONTRACTS.md` (without the change protocol).
You may IMPORT `speechcoach.audio.load_audio` and `speechcoach.align.*`, but not change them. Need a change? Write a request in `docs/HANDOFF.md`.

## What you hand to others
- To B: `dataset/` with audio, `labels/*.json`, `alignments/*.json`, `metadata.csv` exactly as in CONTRACTS sections 2-4. Also `dataset/sample/` (1 ideal + 1 flawed + label + text) by end of Day 2 so everyone can run smoke tests.
- To C: `dataset/sample/` and 3 short demo clips (ideal, almost-perfect, botched) for demo mode by Day 5, plus one clip of an unseen text (T07 or T08) for the no-reference demo.
- To B: the stress variants (loudness-changed, noisy) and the full-gradient set for T01 and T04 first, then all texts (see TASKS A3, A4). Alignment ground truth: label word times from the time map.
- To D: file lists per text/flaw/level for QC listening, and anything the recording sheet needs.
- To everyone: `dataset/SOURCES.md` with license and URL of every source recording.

## Technical guardrails
1. Data quality beats quantity. A clean 48-file spectrum per text beats hundreds of messy files.
2. **Ground truth comes from the time map**, not from re-running the aligner. Keep `(source_time, new_time)` anchors while building the time program, and write label word times from them.
3. **Every** synthetic file, including `resynth_control`, goes through the same WORLD analysis-synthesis. Never mix raw ideal audio and WORLD output as "good vs bad".
4. WORLD settings: 16 kHz, frame period 5 ms, `harvest` (f0 floor 60, ceil 600), `cheaptrick`, `d4c`. Cache analysis as `data/interim/<file_id>.npz`.
5. Flaw parameters come ONLY from `configs/flaws.yaml` (see `docs/FLAW_SPEC.md`). Never invent values.
6. Seed per file: `seed + stable_hash(file_id)` (use `hashlib`, NOT Python's `hash()`, which changes between runs).
7. Regions start/end on word boundaries, preferably at punctuation. Crossfade 5-10 ms at splices.
8. Do not loudness-normalize after injecting VOLUME_DROP.
9. Batch builds must skip files that already exist (power cuts happen) and be parallelizable (`multiprocessing`, process count from CLI arg).
10. `scripts/validate_labels.py` must check: JSON matches CONTRACTS section 3, `0 <= start_s < end_s <= duration_s`, word times monotonic, file exists, `file_id` matches filename. Run it in `make check`.
11. Licenses: only publish audio you may redistribute (own recordings with the speaker's OK, public-domain archives). For TED/TEDx and other restricted sources: no modified copies in the public dataset; publish only a download script + transcripts + labels.
12. Never delete raw recordings. Never overwrite a file in `dataset/raw/good/`.
13. **Splits are fixed by speaker AND text** (CONTRACTS 0.1): text split dev/test/stress, speaker_split train/val/test. Write both into every label and into `metadata.csv`. T07 and T08 (stress split) never enter the baseline library. Never place clips of one speaker in two speaker splits.
14. **Families and emphasis:** every flaw label carries `family`. Build STRESS_MISSING (full gradient) and STRESS_EXAGGERATED, FLAT_ENERGY (reduced) per `FLAW_SPEC.md`; key words come from the ideal's own stress score, never hand-picked.
15. **Licence audit before anything is public:** check `dataset/SOURCES.md` for T01-T04. Some public speeches (for example MLK's 1963 speech, held by the King estate) are probably NOT freely redistributable even though they are famous. For any source without a clear licence set `redistributable = no` in `metadata.csv`, keep the audio out of the public dataset and the public repo, and publish only a download script, transcripts and labels. The audio of T01-T04 is currently committed on branch `a/A1-texts-sources`: decide before the repo goes public whether it must be removed from git history. The original T05-T08 texts and our own teammate recordings are the clean public core.
16. **No unintended flaws:** after each build run the side-check in `FLAW_SPEC.md` section 5 (other families' z stay low outside the labeled region) and fix or regenerate offenders.
17. Human recordings come with a recording sheet (intended flaw region, card letter). Convert Audacity labels with `scripts/audacity_to_labels.py` and check them against the sheet.

## Typical commands
```
python scripts/prepare_audio.py in.m4a --out data/interim/T4__h1__ideal.wav
python -m speechcoach.dataset.build_dataset --config configs/flaws.yaml --texts T04 --workers 2
python scripts/validate_labels.py dataset/metadata/flaws.csv
```

## Definition of done for any A task
Files exist, `validate_labels.py` passes, you listened to samples, and HANDOFF.md is updated with counts (files generated, per text, per flaw).
