# CONTRACTS.md: Frozen interfaces between Member A, B and C

**These definitions are the glue of the project. Nobody (human or AI) changes them alone.**
Change protocol is in section 9.

## 0. Conventions
- Time: seconds (float). Analysis grid hop: 0.01 s. Word index `i` is 0-based over the parsed transcript.
- Pitch: semitones relative to the speaker's median F0. Loudness: dB relative to the speaker's 95th-percentile level (values <= 0).
- `z`: signed deviation in units of calibrated sigma. Sign meaning is fixed in `docs/ARCHITECTURE.md` section 4/5.
- Seeds: `seed` in `configs/thresholds.yaml`.
- Sample rate: 16000 Hz mono everywhere in the dataset.

### 0.1 IDs and names
- `text_id`: `T1` ... `T6`. Dev split: T1, T2, T4, T5. Test split: T3, T6.
- Speaker ids: `h1`, `h2`, `h3` (teammates), `orig-<name>` (historical original, e.g. `orig-jfk`), `synth-<base_speaker>` (synthetic derived from that base).
- `file_id = {text_id}__{speaker}__{variant}`. Variants:
  - ideal recordings: `ideal`, `ideal2` ...
  - resynth control: `resynth_control`
  - synthetic flaws: `{FLAW}_L{1-5}` or composites `COMP{n}_L{2-4}`
  - human flawed takes: `flaw01`, `flaw02` ... (+ `almost01` for "almost perfect")
- Examples: `T4__h1__ideal`, `T1__synth-orig-jfk__PACE_FAST_L3`, `T3__h2__flaw01`.

### 0.2 Enums
- **Flaw types:** `PACE_FAST, PACE_SLOW, PAUSE_MISSING, PAUSE_EXCESS, PAUSE_MISPLACED, MONOTONE, PITCH_ERRATIC, VOLUME_DROP, FLAT_ENERGY, CLARITY, FILLERS, STRESS_MISSING`
- **Dimensions:** `pacing, pausing, pitch, energy, emphasis, clarity, fluency`
- **Severity bands:** `minor, moderate, major`
- **Modes:** `reference, prior`

## 1. Word object
```json
{"i": 0, "raw": "Ask", "norm": "ask", "punct": "", "start": 1.20, "end": 1.52, "conf": 0.93}
```
`punct` is one of `""`, `,`, `.`, `;`, `:`, `?`, `!` (punctuation attached AFTER the word).

## 2. Alignment file: `dataset/alignments/<file_id>.json`
```json
{"file_id": "T4__h1__ideal", "text_id": "T4", "sr": 16000, "duration_s": 41.2,
 "method": "torchaudio-MMS_FA", "words": [ <Word>, ... ]}
```

## 3. Label file: `dataset/labels/<file_id>.json`
```json
{
  "file_id": "T1__synth-orig-jfk__PACE_FAST_L3",
  "text_id": "T1",
  "source": "synthetic",
  "base_file_id": "T1__orig-jfk__ideal",
  "reference_file_ids": ["T1__orig-jfk__ideal", "T1__h1__ideal"],
  "severity_level": 3,
  "split": "dev",
  "duration_s": 58.4,
  "flaws": [
    {"type": "PACE_FAST", "start_s": 12.40, "end_s": 19.85,
     "first_word": 24, "last_word": 41, "params": {"speed": 1.35}}
  ],
  "words": [ <Word>, ... ],
  "license": "public-domain; source: <url>"
}
```
Rules: `source` is `synthetic`, `human` or `original`. `severity_level` is 0-5 for synthetic (0 = ideal/control), `null` for human. For ideal recordings `flaws` is `[]`. `words` times are in the NEW file's time (mapped through the time program for synthetic files). Every `start_s < end_s <= duration_s`.

## 4. `dataset/metadata.csv` columns
`file_id,text_id,source,speaker,variant,severity_level,flaw_types,split,duration_s,license,audio_path,label_path`

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
  "meta": {"mode": "reference", "baseline_id": "T1", "duration_s": 58.4, "version": "1.0",
           "warnings": []},
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
    "evidence": {"participant": 5.9, "baseline": 4.1, "z": -4.5, "unit": "syl/s"},
    "explanation": {"observed": "...", "deviation": "...", "where": "...", "why": "...", "fix": "..."}
  }],
  "scores": {"overall": 71.3,
             "dimensions": {"pacing": 58, "pausing": 74, "pitch": 80, "energy": 85,
                            "emphasis": 70, "clarity": 88, "fluency": 90}}
}
```
Rules: `series.t` is downsampled to 20 points/second; all series arrays have the same length as `t`; unvoiced pitch is `null`. Baseline series are warped onto the participant's word timeline (see `docs/ARCHITECTURE.md` plus the guide). `flaws` are sorted by `start`. Scores are 0-100. The JSON must be byte-identical across repeated runs on the same input (sorted keys, rounded floats to 4 decimals).

## 7. HTTP API (Member C owns, B's `analyze()` powers it)
| Method | Path | Body / params | Returns |
|---|---|---|---|
| GET | `/health` | none | `{"status":"ok"}` |
| GET | `/baselines` | none | `[{"id":"T1","title":"...","n_ideals":3}]` |
| POST | `/analyze` | multipart: `audio` (file), `transcript` (text), `baseline_id` (optional), `mode` (`auto|reference|prior`) | AnalysisResult |
| GET | `/demo/{name}` | `name` in `ideal`, `almost`, `botched` | AnalysisResult (precomputed) |

Errors: HTTP 400 with `{"error": "<message>"}` for bad audio/transcript; HTTP 422 for validation; never return a stack trace.

## 8. Mock data
`app/public/mock_result.json` is a hand-made valid AnalysisResult (Member C creates it on Day 1 from section 6, with 3 flaws). Frontend development uses it until the real pipeline is connected.

## 9. Change protocol
1. The person who needs a change writes the exact proposed diff in `docs/HANDOFF.md` under "Contract change requests".
2. The other affected member(s) approve in the group chat.
3. ONE human edits this file, commits `contracts: <what> (approved by A,B,C)`, and tells everyone to pull.
4. Each member updates their own code the same day.
AI assistants never edit this file without that sequence.
