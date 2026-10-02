# MEMBER_A_DATA.md: Role file for Member A (Data Engineer)

## Mission
Own the **dataset** (30% of the score): texts, ideal recordings, the synthetic flaw spectrum with exact labels, real human flawed recordings, quality control, publishing. Everything the analyzer is tested on comes from here.

## You own (edit freely)
`src/speechcoach/dataset/`, `dataset/`, `data/`, `configs/flaws.yaml`, `scripts/prepare_audio.py`, `scripts/validate_labels.py`, `scripts/audacity_to_labels.py`, `scripts/upload_dataset.sh`, `scripts/download_dataset.sh`, `tests/test_dataset*.py`, `dataset/README.md` (dataset card), `dataset/SOURCES.md`.

## You must NOT edit
`src/speechcoach/{audio,align,features,compare,explain,scoring}/`, `configs/thresholds.yaml`, `configs/rubric.yaml`, `src/speechcoach/api/`, `app/`, `Dockerfile`, `Makefile`, `docs/CONTRACTS.md` (without the change protocol).
You may IMPORT `speechcoach.audio.load_audio` and `speechcoach.align.*`, but not change them. Need a change? Write a request in `docs/HANDOFF.md`.

## What you hand to others
- To B: `dataset/` with audio, `labels/*.json`, `alignments/*.json`, `metadata.csv` exactly as in CONTRACTS sections 2-4. Also `dataset/sample/` (1 ideal + 1 flawed + label + text) by end of Day 2 so everyone can run smoke tests.
- To C: `dataset/sample/` and 3 short demo clips (ideal, almost-perfect, botched) for demo mode by Day 5.
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
12. Never delete raw recordings. Never overwrite a file in `dataset/audio/ideal/`.

## Typical commands
```
python scripts/prepare_audio.py in.m4a --out data/interim/T4__h1__ideal.wav
python -m speechcoach.dataset.build_dataset --config configs/flaws.yaml --texts T4 --workers 2
python scripts/validate_labels.py dataset/labels
```

## Definition of done for any A task
Files exist, `validate_labels.py` passes, you listened to samples, and HANDOFF.md is updated with counts (files generated, per text, per flaw).
