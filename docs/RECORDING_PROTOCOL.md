# RECORDING_PROTOCOL.md: How to record, name, check and back up speech takes

Owner: Member A (coordination, QC, consumes the files). Source: Track C build plan, adapted to our file naming (`CONTRACTS.md` 0.1).

## 1. What we record
| Set | Texts | Who | Takes |
|---|---|---|---|
| Public-speech ideals | T1-T4 | teammates only (long texts, 2-4 min), at least 2 teammates per text so leave-one-out calibration has more than the original speaker | 1 good take each |
| Original short texts | T5-T8 (100-130 words, 45-75 s, written by the team) | up to 12 speakers (h1-h12): teammates first, then volunteers | 1 good take each (keep best of 2-3) |
| Human flawed takes | cards A-J in `FLAW_SPEC.md` 4 | at least 3 different speakers, at least 1 from the test speakers (h11, h12) | 1 take per card |

Plan target for GOOD takes was 12 speakers x 8 texts = 96. Our realistic core is T5-T8 x 12 speakers = 48, plus T1-T4 x (originals + 2-4 teammates). Stretch: more speakers on T1-T4 excerpts. Quality and coverage beat the count.

Texts T5-T8 must be original (written by us) so they can be published. Write them in plain spoken English with punctuation where a speaker would pause. Never use someone else's script without checking its licence (SOURCES.md).

## 2. Setup (same for every session)
- Quiet room, no fan, no music, no one talking; soft furnishings reduce echo.
- Phone on a stable surface or held the same way every take, 15-20 cm from the mouth, microphone not covered. Same position all session.
- Format: record the best original the phone app offers. Preferred: mono, 48 kHz, 16-bit WAV. If the app only makes M4A/MP3, that is fine: keep the ORIGINAL file, do not delay recording, and convert once later (`scripts/prepare_audio.py` does 16 kHz mono WAV). Converting lossy to WAV does not restore lost detail, so never convert twice.
- Phone on airplane mode, do-not-disturb on.

## 3. Take protocol
1. Press record. Stay silent for 5 seconds (room tone).
2. Read the whole text. Natural best presentation: do not slow down, speed up, exaggerate, or act robotic. Natural pauses, emphasis and volume.
3. Stay silent for 2 seconds. Stop.
4. If you make a clear mistake, stop and redo the take. Keep the best clean take. Do not edit breaths or pauses.
5. Order for T5-T8: T5-T6, short break, T7-T8. Do not record all texts when tired.

## 4. Naming and folders
- Raw originals (never edited, never overwritten): `data/raw/<speaker>/<file_id>.<ext>` e.g. `data/raw/h4/T5__h4__ideal.m4a`.
- `file_id = {text_id}__{speaker}__{variant}`: ideal `T5__h4__ideal`; human flawed `T5__h4__flaw03` (card letter goes in the label and the sheet, not the id).
- Plan names for reference: `S04_T05_GOOD.wav` = `T5__h4__ideal`. Do not use plan names in the repo.
- Prepared WAV (16 kHz mono) goes to `data/interim/`, then `dataset/audio/`. Member A runs the preparation.

## 5. Recording sheet (Member A keeps it; one row per take)
`date, session_id, speaker, text_id, variant, card (if flawed), intended_flaw_region (first and last words), device, room, phone_distance_cm, takes_made, kept_take, notes`
Speaker details: only `speaker, device, room/session`; age group only if volunteered. No names in the public repo, only `hN`. Every volunteer agrees in writing (a message is enough) that their voice may be published in the dataset; record that in `dataset/SOURCES.md` (consent column, yes/no). If someone says no or is unsure, their takes stay private (`redistributable = no`).

## 6. Pilot first
One teammate records all of T5-T8 (and one flawed card). Check: placement, noise, clipping, durations (45-75 s), file handling, transcript matches what was read. Run the pilot through `scripts/prepare_audio.py` and the aligner (Member B). Do not record the other speakers until the pilot passes.

## 7. QC checklist per file (Member A ticks; failures go in `dataset/QC_LOG.md`)
Every file: opens; transcript matches (no missing or repeated sentence); no music or other voices; no severe clipping (peak below -1 dBFS after preparation); correct speaker and text ID; metadata row complete; correct split.
GOOD takes: natural delivery, no intentional flaw, audible pitch and loudness variation, understandable articulation, reasonable pauses; speech rate roughly 2-4 words/s; duration in range.
Flawed takes: same transcript; intended flaw audible AND measurable; matches the card; start/end words recorded; no other major flaw dominating.
Alignment: after Member B aligns, spot-check at least 1 file per speaker and per flaw family by listening to 3 word boundaries (play from the aligned start of a word). Automated alignment is never trusted blindly.

## 8. Backups
After every session copy `data/raw/` to the team Drive folder and note the date in the recording sheet. Raw originals are never deleted.
