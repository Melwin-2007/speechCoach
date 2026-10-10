# CONTRACTS.md: Frozen interfaces between Member A, B, C and D

**These definitions are the glue of the project. Nobody (human or AI) changes them alone.**
Change protocol is in section 9.

> **v1.1 (2026-10-06, PENDING APPROVAL).** Items tagged `[v1.1]` come from aligning the repo with the Track C build plan. They are all ADDITIVE (new optional fields, new enum values, new files); existing code that ignores them keeps working. They become frozen only after the approvals listed in `docs/HANDOFF.md` section 3 (A, B, C, D). Until then treat them as proposals; do not build on them in a way that breaks if they are rejected.

## 0. Conventions
- Time: seconds (float). Analysis grid hop: 0.01 s. Word index `i` is 0-based over the parsed transcript.
- Pitch: semitones relative to the speaker's median F0. Loudness: dB relative to the speaker's 95th-percentile level (values <= 0).
- `z`: signed deviation in units of calibrated sigma. Sign meaning is fixed in `docs/ARCHITECTURE.md` section 4/5.
- Seeds: `seed` in `configs/thresholds.yaml`.
- Sample rate: 16000 Hz mono everywhere in the dataset.

### 0.1 IDs and names
- `text_id`: `T01` ... `T08` [v1.1: was T01..T06]. T01-T04 = prepared public speeches; T05-T08 = original team-written texts (100-130 words). Text split: **dev** T01, T02, T04, T05; **test** T03, T06; **stress** T07, T08 [v1.1] (unseen-text set: kept OUT of the baseline library so the analyzer must use Mode B; also used for no-reference tests).
- `speaker_split` [v1.1]: by speaker, never by clip. `train` = S01-S05 and every `orig-*`; `val` = S06; `test` = S07, S08. A `synth-<base>` speaker inherits the base speaker's split. Speakers not yet recruited simply stay unused; the rule is fixed now so nobody tunes on a test voice later.
- Evaluation sets [v1.1]: DEV = text split dev AND speaker_split in (train, val); TEST-TEXT = text split test; TEST-SPEAKER = speaker_split test on dev texts; STRESS = text split stress plus composites/noise/loudness variants. Tuning only on DEV; thresholds picked on `val` speakers; TEST sets run once.
- Speaker ids: `S01` ... `S08` (teammates first, then volunteers), `orig-<name>` (historical original, e.g. `orig-jfk`), `synth-<base_speaker>` (synthetic derived from that base).
- `file_id = {speaker}_{text_id}_{quality}`. Quality:
  - `GOOD`: ideal recordings
  - `FLAWED`: synthetic or human flawed takes
- Examples: `S01_T04_GOOD`, `S02_T01_FLAWED`.

### 0.2 Enums
- **Flaw types:** `PACE_FAST, PACE_SLOW, PAUSE_MISSING, PAUSE_EXCESS, PAUSE_MISPLACED, MONOTONE, PITCH_ERRATIC, VOLUME_DROP, FLAT_ENERGY, CLARITY, FILLERS, STRESS_MISSING, STRESS_EXAGGERATED` [v1.1: added STRESS_EXAGGERATED]. The canonical name is `FILLERS` (an old HANDOFF entry says `FILLER_WORD`; that was a typo, do not use it).
- **Flaw families** [v1.1]: `pacing` (PACE_FAST, PACE_SLOW), `pausing` (PAUSE_MISSING, PAUSE_EXCESS, PAUSE_MISPLACED, FILLERS), `pitch` (MONOTONE, PITCH_ERRATIC), `volume` (VOLUME_DROP, FLAT_ENERGY), `clarity` (CLARITY), `emphasis` (STRESS_MISSING, STRESS_EXAGGERATED). FILLERS is a pausing-family flaw for labeling but is scored in the `fluency` dimension.
- **Report severity** [v1.1] (for tables/figures only; files keep L1-L5): L1-L2 = 1 subtle, L3 = 2 noticeable, L4 = 3 strong, L5 = 4 extreme, L0 = 0 good.
- **Dimensions:** `pacing, pausing, pitch, energy, emphasis, clarity, fluency`
- **Severity bands:** `minor, moderate, major`
- **Modes:** `reference, prior`

## 1. Word object
```json
{"i": 0, "raw": "Ask", "norm": "ask", "punct": "", "start": 1.20, "end": 1.52, "conf": 0.93}
```
`punct` is one of `""`, `,`, `.`, `;`, `:`, `?`, `!` (punctuation attached AFTER the word).

## 2. Alignment files: `dataset/alignments/good/<file_id>.json` and `dataset/alignments/flawed/<file_id>.json`
```json
{"file_id": "S01_T04_GOOD", "text_id": "T04", "sr": 16000, "duration_s": 41.2,
 "method": "torchaudio-MMS_FA", "words": [ <Word>, ... ]}
```

## 3. Metadata & Labels (`dataset/metadata/`)
Flaws and file metadata are tracked across `speakers.csv`, `recordings.csv`, and `flaws.csv`.

`recordings.csv` columns:
`file_id,text_id,speaker_id,quality,duration_s,license,redistributable`

`flaws.csv` columns:
`file_id,flaw_type,flaw_family,severity_level,start_s,end_s,first_word,last_word`

`speakers.csv` columns:
`speaker_id,source,speaker_split`

## 4. Splits (`dataset/splits/`)
Splits are defined in `train.csv`, `validation.csv`, and `test.csv`.

## 5. Python interfaces (signatures are frozen)
```python
# speechcoach/audio/io.py            (B)
def load_audio(path: str | Path, sr: int = 16000, target_lufs: float = -23.0) -> np.ndarray  # float32 mono

# speechcoach/align/transcript.py    (B)
def parse_transcript(text: str) -> list[dict]          # Word dicts without start/end/conf

# speechcoach/align/aligner.py       (B)
def align_words(y: np.ndarray, words: list[dict]) -> list[dict]   # adds start, end, conf

# speechcoach/features/frame.py      (B)
def frame_features(y: np.ndarray) -> dict   # keys: t, f0, st, db, db_rel, flux, mfcc, hnr (all on the 10 ms grid)
                                            # [v1.1] optional extra keys: cent (spectral centroid, Hz), band_ratio (energy 2-4 kHz / 0-1 kHz), dmfcc (MFCC delta)

# speechcoach/features/words.py      (B)
def word_table(words: list[dict], g: dict) -> list[dict]
def window_stats(g: dict, words: list[dict], W: int = 6) -> dict[str, np.ndarray]

# speechcoach/compare/baseline.py    (B)
def build_baseline(ideals: list[dict]) -> dict
def signals(P: dict, B: dict) -> dict[str, np.ndarray]
def calibrate(loo_signals: dict[str, np.ndarray], floors: dict[str, float]) -> dict[str, float]

# speechcoach/compare/regions.py     (B)
def find_regions(z: np.ndarray, words: list[dict], sign: int, cfg: dict, event_mode: bool = False) -> list[dict]

# speechcoach/explain/templates.py   (B)
def explain(region: dict, evidence: dict) -> dict      # keys: observed, deviation, where, why, fix

# speechcoach/scoring/rubric.py      (B)
def score(z_by_signal: dict, words: list[dict], cfg: dict) -> dict   # {"overall": float, "dimensions": {...}}

# speechcoach/analyze.py             (B)  <-- THE function the API calls
def analyze(audio_path: str | Path, transcript: str,
            baseline_id: str | None = None, mode: str = "auto") -> dict   # returns AnalysisResult (section 6)

# speechcoach/dataset/world_engine.py (A)
def analyze_world(y: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]   # f0, sp, ap
def inject(base_file_id: str, flaw: str, level: int, seed: int) -> tuple[np.ndarray, dict]  # audio, label dict
```

## 6. AnalysisResult JSON (what `analyze()` and `/analyze` return)
```json
{
  "meta": {"mode": "reference", "baseline_id": "T01", "duration_s": 58.4, "version": "1.0",
           "warnings": [], "mode_label": "Reference mode"},
  "words": [{"i": 0, "w": "ask", "start": 1.2, "end": 1.52, "punct": "", "conf": 0.93,
             "z": {"pace": 0.3, "pause": 0.1, "pitch": -0.2, "energy": 0.1, "clarity": 0.0}}],
  "series": {
    "t": [0.0, 0.05],
    "participant": {"pitch_st": [0.1, 0.2], "energy_db": [-12.0, -11.5], "rate_sps": [4.1, 4.2]},
    "baseline":    {"pitch_st": [0.0, 0.1], "pitch_lo": [-1.0, -0.9], "pitch_hi": [1.0, 1.1],
                    "energy_db": [-12.0, -12.0], "rate_sps": [4.0, 4.0]}
  },
  "flaws": [{
    "id": 1, "type": "PACE_FAST", "start": 42.1, "end": 51.3,
    "first_word": 57, "last_word": 71, "severity": 0.72, "band": "major",
    "family": "pacing", "confidence": 0.88,
    "evidence": {"participant": 5.9, "baseline": 4.1, "z": -4.5, "unit": "syl/s", "deviation_pct": 43.9},
    "explanation": {"observed": "...", "deviation": "...", "where": "...", "why": "...", "fix": "..."}
  }],
  "scores": {"overall": 71.3,
             "dimensions": {"pacing": 58, "pausing": 74, "pitch": 80, "energy": 85,
                            "emphasis": 70, "clarity": 88, "fluency": 90}}
}
```
Rules: `family`, `confidence`, `evidence.deviation_pct` and `meta.mode_label` are [v1.1] and OPTIONAL: `confidence` is `null` when the learned scorer is not used; `deviation_pct = 100*(participant-baseline)/baseline`; `mode_label` is "Reference mode" or "No-reference mode" (the UI shows it and, for Mode B, says the baseline is pooled). `scores.dimensions.emphasis` may be `null` until the emphasis signal exists. `series.t` is downsampled to 20 points/second; all series arrays have the same length as `t`; unvoiced pitch is `null`. Baseline series are warped onto the participant's word timeline (see `docs/ARCHITECTURE.md` plus the guide). `flaws` are sorted by `start`. Scores are 0-100. The JSON must be byte-identical across repeated runs on the same input (sorted keys, rounded floats to 4 decimals).

## 7. HTTP API (Member C owns, B's `analyze()` powers it)
| Method | Path | Body / params | Returns |
|---|---|---|---|
| GET | `/health` | none | `{"status":"ok"}` |
| GET | `/baselines` | none | `[{"id":"T01","title":"...","n_ideals":3}]` |
| POST | `/analyze` | multipart: `audio` (file), `transcript` (text), `baseline_id` (optional), `mode` (`auto|reference|prior`) | AnalysisResult |
| GET | `/demo/{name}` | `name` in `ideal`, `almost`, `botched`, `unseen` [v1.1: `unseen` = no-reference example] | AnalysisResult (precomputed) |

Errors: HTTP 400 with `{"error": "<message>"}` for bad audio/transcript; HTTP 422 for validation; never return a stack trace.

## 8. Mock data
`app/public/mock_result.json` is a hand-made valid AnalysisResult (Member C creates it on Day 1 from section 6, with 3 flaws; v1.1: add `family`, `confidence`, `deviation_pct`, `mode_label` and an `unseen` preset in prior mode). Frontend development uses it until the real pipeline is connected.

## 9. Change protocol
1. The person who needs a change writes the exact proposed diff in `docs/HANDOFF.md` under "Contract change requests".
2. The other affected member(s) approve in the group chat (all four members for v1.1).
3. ONE human edits this file, commits `contracts: <what> (approved by A,B,C,D)`, and tells everyone to pull.
4. Each member updates their own code the same day.
AI assistants never edit this file without that sequence.
