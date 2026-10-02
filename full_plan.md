# SpeechCoach — Full Plan (Plain Language)

> This is the one document every team member reads. It tells you exactly what to do each day, how to test it, and when you're done. No jargon — just steps.

---

## How to Read This Plan

- Each day has 3 sections: **Member A**, **Member B**, **Member C**.
- Each section has:
  - **What to do** — step by step
  - **How to test it works** — exact commands and what you should see
  - **You're done when** — the checklist that must be 100% true
- Tasks marked with 🔧 are coding tasks. Tasks marked with 🎤 are recording tasks. Tasks marked with 📝 are documentation tasks.
- If you finish early, help review a teammate's pull request — don't start tomorrow's work.

---

## Before Day 1: Setup (Everyone, 30 minutes)

### What to do
1. Clone the repo: `git clone <repo-url>`
2. Follow [setup.md](../setup.md) — create venv, install dependencies
3. Verify GPU works:
   ```
   python -c "import torch; print(torch.cuda.is_available())"
   ```
   Should print `True`.
4. Read [SIMPLE_EXPLANATIONS.md](../SpeechCoach%20Guide/SIMPLE_EXPLANATIONS.md) end to end — this explains every concept you'll encounter.
5. Everyone says "OK" to the contracts in the group chat. After this, nobody changes JSON formats or function names alone.

### You're done when
- [ ] `pip install -r requirements.txt` completes without errors
- [ ] `python -c "import torch; print(torch.cuda.is_available())"` prints `True`
- [ ] You've read SIMPLE_EXPLANATIONS.md
- [ ] You said "OK" to contracts in the group chat

---

# 📅 DAY 1: Foundations

---

## Member A — Day 1: Texts and Audio Sources

**Task ID:** A1 · **Branch:** `a/A1-texts-sources`

### What to do

1. 🔧 **Write `scripts/prepare_audio.py`** — a script that converts any audio file to our standard format:
   - Input: any audio file (mp3, m4a, wav, etc.)
   - What it does: uses `ffmpeg` to convert to 16 kHz, mono, 16-bit WAV
   - Also trims silence at the start/end to at most 1 second
   - Prints: duration, peak level, noise floor estimate
   - Example usage: `python scripts/prepare_audio.py input.m4a --out data/interim/T4__h1__ideal.wav`

2. 📝 **Create `dataset/SOURCES.md`** — a table listing where each text comes from:
   ```
   | Text ID | Title | Genre | Source URL | License | Notes |
   |---------|-------|-------|------------|---------|-------|
   | T1 | ... | ... | ... | ... | ... |
   ```

3. 📝 **Write the 6 transcript files** in `dataset/texts/`:
   - `T1.txt`, `T2.txt`, `T3.txt`, `T4.txt`, `T5.txt`, `T6.txt`
   - These are the EXACT words spoken, with punctuation
   - Listen to each source recording carefully — write what you HEAR, not what a website says

4. 🔧 **Download source audio** for historical speeches and convert them:
   ```
   python scripts/prepare_audio.py raw_jfk.mp3 --out data/interim/T1__orig-jfk__ideal.wav
   ```

### How to test it works

```bash
# Test prepare_audio.py with any audio file you have
python scripts/prepare_audio.py some_audio.m4a --out data/interim/test.wav

# You should see output like:
# Duration: 42.3s
# Peak level: -1.2 dB
# Noise floor: -45.3 dB
# Saved: data/interim/test.wav

# Verify the output file is correct format:
python -c "import soundfile; info = soundfile.info('data/interim/test.wav'); print(f'SR={info.samplerate}, CH={info.channels}, DUR={info.duration:.1f}s')"
# Should show: SR=16000, CH=1, DUR=42.3s
```

### You're done when
- [ ] 6 transcript files exist in `dataset/texts/` (T1.txt through T6.txt)
- [ ] `dataset/SOURCES.md` has an entry for every text with URL and license
- [ ] At least 3 source WAVs are in `data/interim/`, all 16 kHz mono
- [ ] `prepare_audio.py` runs successfully on a test file
- [ ] You've committed and pushed your branch

---

## Member B — Day 1: Transcript Parsing and Forced Alignment

**Task ID:** B1 · **Branch:** `b/B1-alignment`

### What to do

1. 🔧 **Implement `src/speechcoach/audio/io.py`** — the `load_audio` function:
   - Takes a file path, loads it as a numpy array
   - Converts to 16 kHz mono
   - Normalizes loudness to -23 LUFS
   - Returns a float32 numpy array

2. 🔧 **Implement `src/speechcoach/align/transcript.py`** — the `parse_transcript` function:
   - Takes a string like `"Ask not what your country can do for you."`
   - Returns a list of word dictionaries:
     ```python
     [{"i": 0, "raw": "Ask", "norm": "ask", "punct": ""}, 
      {"i": 1, "raw": "not", "norm": "not", "punct": ""},
      ...
      {"i": 8, "raw": "you.", "norm": "you", "punct": "."}]
     ```
   - Handles: numbers → words ("42" → "forty two"), punctuation attached after words, apostrophes kept

3. 🔧 **Implement `src/speechcoach/align/aligner.py`** — the `align_words` function:
   - Uses the MMS_FA model from torchaudio to find when each word starts and ends
   - Takes the audio array and the word list from step 2
   - Adds `start`, `end`, `conf` (confidence) to each word dict
   - This runs on the GPU

4. 🔧 **Implement `src/speechcoach/align/run.py`** — a command-line tool:
   ```bash
   python -m speechcoach.align.run sample.wav transcript.txt --out alignment.json
   ```
   - Outputs a JSON file matching the format in CONTRACTS.md section 2

5. 🔧 **Write tests** in `tests/test_align.py`:
   - Test `parse_transcript` with numbers, punctuation, apostrophes
   - Test that word starts are non-decreasing (word 5 can't start before word 4)

### ⚠️ Important: Check the API first!
Before writing any code, run this to see the REAL torchaudio API:
```python
python -c "import torchaudio; help(torchaudio.pipelines.MMS_FA)"
```
The API might differ from what you expect. Use what the installed version actually provides.

### How to test it works

```bash
# Record a 10-second sample on your phone, convert it:
ffmpeg -i sample.m4a -ac 1 -ar 16000 sample.wav

# Write the transcript in a text file:
echo "This is a test of the speech alignment system." > sample.txt

# Run the alignment:
python -m speechcoach.align.run sample.wav sample.txt --out test_alignment.json

# Check the output — you should see word timings:
python -c "import json; data=json.load(open('test_alignment.json')); [print(f'{w[\"raw\"]:15s} {w[\"start\"]:.2f}s - {w[\"end\"]:.2f}s') for w in data['words'][:5]]"

# Run tests:
python -m pytest tests/test_align.py -v
```

**Spot-check:** Open the audio in Audacity. Look at word 3. Does it start roughly where the JSON says? Check 3 words.

### You're done when
- [ ] `parse_transcript` handles numbers, punctuation, and apostrophes correctly
- [ ] The CLI produces a valid alignment JSON (check against CONTRACTS section 2)
- [ ] Word `start` times are non-decreasing in the output
- [ ] All tests pass
- [ ] You can explain what forced alignment does if asked

---

## Member C — Day 1: Repo Scaffold and Kit

**Task ID:** C1 · **Branch:** `c/C1-scaffold`

### What to do

1. 🔧 **Create the `Makefile`** with these targets:
   ```makefile
   setup:     # pip install -r requirements.txt
   test:      # python -m pytest tests/
   check:     # make test && make smoke
   smoke:     # runs scripts/smoke.sh (for now, prints "no sample yet" and exits 0)
   app:       # starts the API server and frontend dev server
   dataset:   # python -m speechcoach.dataset.build_dataset (placeholder for now)
   eval:      # python scripts/run_eval.py (placeholder for now)
   ```

2. 🔧 **Create the FastAPI app** in `src/speechcoach/api/main.py`:
   - `GET /health` → returns `{"status": "ok"}`
   - `GET /baselines` → returns a hard-coded list (stub for now)
   - `POST /analyze` → returns mock data from `app/public/mock_result.json`
   - `GET /demo/{name}` → stub, returns mock data

3. 🔧 **Create `app/public/mock_result.json`** — a valid AnalysisResult:
   - Must match CONTRACTS.md section 6 EXACTLY
   - Include 3 flaws of different types (e.g., PACE_FAST, MONOTONE, VOLUME_DROP)
   - Include realistic-looking numbers (scores, word timings, z-scores)
   - This is what Member B and C will use until the real pipeline works

4. 🔧 **Set up the React app** in `app/`:
   - Use Vite: `npx -y create-vite@latest ./ -- --template react`
   - For now, just load and display the mock JSON to prove it works

5. 🔧 **Write `tests/test_health.py`**:
   ```python
   # Test that GET /health returns {"status": "ok"}
   ```

6. 🔧 **Write `scripts/smoke.sh`** — placeholder:
   ```bash
   #!/bin/bash
   if [ -d "dataset/sample" ] && [ "$(ls dataset/sample/*.wav 2>/dev/null)" ]; then
       echo "Running smoke test..."
       # Will be filled in later
   else
       echo "No sample yet — skipping smoke"
   fi
   ```

### How to test it works

```bash
# Run the full check
make setup
make check
# Should see: all tests pass, smoke prints "no sample yet"

# Start the app
make app
# Open http://localhost:8000/health in your browser — should see {"status":"ok"}
# Open http://localhost:8000/docs — should see the FastAPI docs page

# Verify mock JSON is valid
python -c "
import json
data = json.load(open('app/public/mock_result.json'))
assert 'meta' in data
assert 'words' in data
assert 'series' in data
assert 'flaws' in data and len(data['flaws']) == 3
assert 'scores' in data
print('Mock JSON is valid!')
print(f'Flaws: {[f[\"type\"] for f in data[\"flaws\"]]}')
print(f'Overall score: {data[\"scores\"][\"overall\"]}')
"
```

### You're done when
- [ ] A fresh clone → `make setup && make check` passes
- [ ] `make app` starts a server; `/health` returns `{"status": "ok"}`
- [ ] `mock_result.json` has 3 flaws and matches the contract format
- [ ] React app loads in the browser and shows something from the mock JSON
- [ ] `tests/test_health.py` passes

---

## Everyone — Day 1 Evening: 🎤 Record Ideal T4

**Text T4** is short (Gitanjali 35 by Tagore). Each person records 3 takes.

### Recording protocol
1. Find a quiet room — turn off fans and AC
2. Use your phone, hold it 15-20 cm from your mouth
3. Record in a lossless format (use a voice recorder app that saves WAV or M4A)
4. Start with 2 seconds of silence, then speak, then 2 seconds of silence
5. Record 3 takes — keep the best one

### After recording
```bash
# Convert your recording
ffmpeg -i my_recording.m4a -ac 1 -ar 16000 T4__h1__ideal.wav
# (Replace h1 with h2 or h3 depending on who you are)
```

Send the WAV to Member A via Google Drive. A stores them in `dataset/audio/ideal/`.

### Day 1 Finish Line (Evening Sync)
| Check | How to verify |
|---|---|
| Repo clones and builds | Fresh clone → `make setup && make check` ✅ |
| Alignment works | B demos the CLI on a real recording |
| At least 3 source WAVs exist | A shows them in `data/interim/` |
| Mock JSON is valid | C shows it loading in the browser |
| T4 ideal recordings collected | 3 WAV files on Drive |
| Tag the repo | `git tag day-1-green && git push --tags` |

---

# 📅 DAY 2: Features and First Flaw

---

## Member A — Day 2: WORLD Engine and First Flaw

**Task ID:** A2 · **Branch:** `a/A2-world-engine`

### What to do

1. 🔧 **Implement `src/speechcoach/dataset/world_engine.py`**:
   
   **`analyze_world(y)`** — takes audio, returns 3 arrays:
   - `f0` — pitch at each moment
   - `sp` — spectral envelope (the "shape" of the sound)
   - `ap` — aperiodicity (breathiness)
   - Cache the result to `data/interim/<file_id>.npz` so you don't recalculate
   
   **Time-program renderer** — the system that speeds up/slows down parts of audio:
   - Takes WORLD components + a "time program" (which frames to play at what speed)
   - Keeps track of anchors: `(original_time, new_time)` so word positions can be mapped
   - Resynthesizes audio from the modified components
   
   **`inject(base_file_id, flaw, level, seed)`** — creates a flawed version:
   - For now, only implement `PACE_FAST` (levels 1-5)
   - Reads parameters from `configs/flaws.yaml` (speed values: 1.10, 1.20, 1.35, 1.55, 1.80)
   - Picks a region (starting at a punctuation boundary) covering the right fraction of the text
   - Speeds up that region by the speed factor
   - Also creates a `resynth_control` — the ideal audio passed through WORLD with NO changes
   
2. 🔧 **Implement `scripts/validate_labels.py`** — checks that label files are correct:
   - JSON matches the format in CONTRACTS section 3
   - All times are valid: `0 <= start_s < end_s <= duration_s`
   - Word times are in order (non-decreasing)
   - The audio file referenced actually exists
   - The `file_id` in the JSON matches the filename

3. 🔧 **Build `dataset/sample/`** — one ideal + one flawed file:
   - This is what B and C use for testing until the full dataset exists
   - Include: WAV file, label JSON, alignment JSON, transcript

### How to test it works

```bash
# Generate PACE_FAST L1 through L5 for T4
python -m speechcoach.dataset.world_engine --text T4 --flaw PACE_FAST --levels 1,2,3,4,5

# Validate all labels
python scripts/validate_labels.py dataset/labels/

# LISTEN to the files (most important test!)
# L1 should sound almost normal
# L3 should be noticeably fast in the middle
# L5 should sound obviously rushed

# Check that the resynth_control sounds identical to the original
# (It won't be bit-identical, but should sound the same to your ears)
```

### You're done when
- [ ] 5 PACE_FAST files (L1-L5) + 1 resynth_control exist for T4
- [ ] `validate_labels.py` passes on all label files
- [ ] You LISTENED to L1, L3, and L5 — L1 is barely noticeable, L5 is clearly rushed
- [ ] `dataset/sample/` has 1 ideal + 1 flawed file with labels and transcript
- [ ] The sample is pushed so B and C can use it

---

## Member B — Day 2: Feature Extraction

**Task ID:** B2 · **Branch:** `b/B2-features`

### What to do

1. 🔧 **Implement `src/speechcoach/features/frame.py`** — `frame_features(y)`:
   
   This is the "ear" of the system. For every 10ms frame of audio, measure:
   
   | Output key | What it is | How to compute it |
   |---|---|---|
   | `t` | Time of each frame | `[0.00, 0.01, 0.02, ...]` |
   | `f0` | Raw pitch in Hz | Praat autocorrelation via `parselmouth` (two passes) |
   | `st` | Pitch in semitones relative to median | `12 * log2(f0 / median_f0)` — NaN where unvoiced |
   | `db` | Loudness in dB | `20 * log10(rms)` per frame |
   | `db_rel` | Loudness relative to speaker's P95 | `db - percentile(db, 95)` |
   | `flux` | Spectral flux | How much the spectrum changes frame-to-frame |
   | `mfcc` | MFCC coefficients | Via librosa, with CMVN (subtract mean, divide by std) |
   | `hnr` | Harmonic-to-noise ratio | Via parselmouth |

2. 🔧 **Implement `src/speechcoach/features/words.py`** — `word_table(words, g)`:
   - Takes the word list (with start/end times) and the frame features
   - For each word, computes: mean pitch, mean loudness, duration, pause before it
   - Returns enriched word dicts

3. 🔧 **Implement `src/speechcoach/features/syllables.py`**:
   - Count syllables in a word using CMU Pronouncing Dictionary
   - Fallback: count vowel groups in the spelling

4. 🔧 **Implement `scripts/plot_features.py`**:
   - Generates a figure showing pitch, energy, and pauses over time
   - Draw vertical lines at word boundaries
   - This is for visual verification — show it to your team

5. 🔧 **Write tests** in `tests/test_features.py`:

### How to test it works

```bash
# Test with a synthetic signal (known answer)
python -c "
import numpy as np
from speechcoach.features.frame import frame_features

# Create a pure 150 Hz tone (we KNOW the pitch should be ~150 Hz)
sr = 16000
t = np.linspace(0, 1, sr)
y = np.sin(2 * np.pi * 150 * t).astype(np.float32)
g = frame_features(y)
voiced_f0 = g['f0'][~np.isnan(g['f0'])]
median_f0 = np.median(voiced_f0)
print(f'Expected F0: 150 Hz')
print(f'Measured F0: {median_f0:.1f} Hz')
print(f'Error: {abs(median_f0 - 150):.1f} Hz')
assert abs(median_f0 - 150) < 2, 'F0 error too large!'
print('✅ F0 test passed!')
"

# Generate the feature plot for a real file
python scripts/plot_features.py dataset/sample/some_file.wav --out results/feature_plot.png
# Open the PNG — pitch line should go up and down naturally, energy should be high during speech

# Run all tests
python -m pytest tests/test_features.py -v
```

### You're done when
- [ ] A 150 Hz sine wave gives F0 within 2 Hz of 150
- [ ] A signal with a 0.5s silence gap reports `pause_before` of 0.5s ± 20ms
- [ ] Two synthetic voices with different base pitch give equal semitone curves after normalization
- [ ] Feature plot is generated for a real file and looks reasonable
- [ ] All tests pass

---

## Member C — Day 2: Dashboard v0

**Task ID:** C2 · **Branch:** `c/C2-dashboard`

### What to do

Build the dashboard one component at a time, using `mock_result.json` as data. **Wait for your own OK after each component before moving to the next.**

1. 🔧 **Waveform with flaw regions** (wavesurfer.js v7):
   - Show the audio waveform
   - Color-coded regions for each flaw (e.g., red for PACE_FAST, blue for MONOTONE)
   - Clicking a region plays that segment and selects the flaw

2. 🔧 **Three stacked charts** (Plotly.js):
   - Chart 1: Pitch (semitones) over time
   - Chart 2: Energy (dB) over time
   - Chart 3: Speech rate over time
   - All share the same x-axis (time)
   - Baseline drawn as a shaded band, participant as a line
   - Flaw regions shown as colored rectangles

3. 🔧 **Flaw list and explanation card**:
   - List of all detected flaws (type, time range, severity)
   - Clicking one shows the explanation: observed, deviation, where, why, fix

4. 🔧 **Upload form**:
   - Audio file picker
   - Transcript text box
   - Baseline dropdown (list of available texts)
   - "Analyze" button
   - For now, posting to `/analyze` returns the mock data

### How to test it works

```bash
# Start the dev server
make app

# Open http://localhost:5173 (or whatever port Vite uses)
# You should see:
# ✅ A waveform
# ✅ Three charts with data from mock_result.json
# ✅ Colored flaw regions on the waveform
# ✅ A list of 3 flaws
# ✅ Clicking a flaw shows its explanation
# ✅ An upload form (the button should work but just returns mock data)
```

Take a screenshot for HANDOFF.md.

### You're done when
- [ ] Waveform renders with clickable flaw regions
- [ ] 3 charts show pitch, energy, and rate from mock data
- [ ] Flaw list shows all 3 mock flaws
- [ ] Clicking a flaw shows the 5-field explanation
- [ ] Upload form exists and posts to the API
- [ ] Screenshot saved in HANDOFF.md

---

## Everyone — Day 2 Evening: 🎤 Record Ideal T5 and T6

Same protocol as Day 1. 3 takes each of T5 and T6.

### Day 2 Finish Line
| Check | How to verify |
|---|---|
| Sample pack exists | `dataset/sample/` has files B and C can use |
| Features work on synthetic signals | B runs the 150 Hz test |
| Dashboard shows mock data | C shows it in the browser |
| T5 and T6 recordings collected | WAV files on Drive |

---

# 📅 DAY 3: Full Flaw Engine + Baseline

---

## Member A — Day 3: All Flaw Types

**Task ID:** A3 · **Branch:** `a/A3-full-engine`

### What to do

Extend the flaw engine to all 12 flaw types. Implement them in this order and **stop for a listen-check after each**:

1. **Pause flaws** (PAUSE_MISSING, PAUSE_EXCESS, PAUSE_MISPLACED)
   - MISSING: shorten pauses after punctuation
   - EXCESS: add silence at punctuation pauses
   - MISPLACED: insert silence at random non-punctuation positions

2. **Pitch flaws** (MONOTONE, PITCH_ERRATIC)
   - MONOTONE: flatten pitch toward the median
   - ERRATIC: add random pitch noise

3. **Volume flaws** (VOLUME_DROP, FLAT_ENERGY)
   - DROP: reduce gain in a region
   - FLAT: compress loudness variation toward the mean

4. **CLARITY** — smooth the spectral envelope over time (simulates mumbling)

5. **FILLERS** — insert "uh" sounds (held vowels with falling pitch)

6. **Composites** — combine 2-3 flaws in one file (5 combos per text)

7. **Batch builder** — `scripts/build_dataset.py` that generates all files:
   - Skips files that already exist (resume-safe)
   - Supports `--workers N` for parallel processing
   - Run for T4 and T1 first

8. 📊 **Gradient check plot** — `results/gradient_check.png`:
   - X axis: severity level (L1 to L5)
   - Y axis: measured deviation (speed ratio, pitch std, etc.)
   - One line per flaw type — all should go UP from L1 to L5

### How to test it works

```bash
# Build flaws for T4
python -m speechcoach.dataset.build_dataset --config configs/flaws.yaml --texts T4 --workers 2

# Validate everything
python scripts/validate_labels.py dataset/labels/

# Count files
ls dataset/audio/synthetic/T4__* | wc -l
# Should be ~48 (1 control + 30 full-gradient + 12 reduced + 5 composites)

# LISTEN to 3 files per flaw type — does it sound like a human flaw, not a glitch?
# Check: does L1 sound almost normal? Does L5 sound clearly bad?
```

### You're done when
- [ ] ~48 files per text for T4 and T1
- [ ] `validate_labels.py` passes on everything
- [ ] Gradient plot shows monotonically increasing deviation per flaw
- [ ] You listened to at least 3 files per flaw type
- [ ] Results pushed; counts posted in HANDOFF.md

---

## Member B — Day 3: Baseline and Calibration

**Task ID:** B3 · **Branch:** `b/B3-baseline`

### What to do

1. 🔧 **Add `window_stats` to `src/speechcoach/features/words.py`**:
   - For each word, look at the 6-word window around it
   - Compute: total window duration, pitch std, mean loudness, loudness std, mean spectral flux

2. 🔧 **Implement `src/speechcoach/compare/baseline.py`** — three functions:

   **`build_baseline(ideals)`** — takes window stats from multiple ideal recordings, averages them:
   - Geometric mean for durations, stds, flux (ratio-type quantities)
   - Arithmetic mean for dB and pause values
   
   **`signals(P, B)`** — computes deviation of participant P from baseline B:
   - `pace = log(P.win_dur / B.win_dur)` — negative = faster
   - `pause = P.pause_before - B.pause_before` — positive = longer pause
   - `pitch = log(P.f0_std / B.f0_std)` — negative = more monotone
   - `energy = P.db_mean - B.db_mean` — negative = quieter
   - `dynamics = log(P.db_std / B.db_std)` — negative = flatter dynamics
   - `clarity = log(P.flux / B.flux)` — negative = less articulation
   
   **`calibrate(loo_signals, floors)`** — measures natural spread between good speakers:
   - For each ideal, compute its signals vs the baseline built from the OTHER ideals
   - Pool all values per signal
   - `sigma = max(1.4826 * MAD(values), floor)`
   - Save to `configs/sigma.json`

3. 🔧 **Implement `scripts/calibrate.py`** — CLI that runs leave-one-out calibration

### How to test it works

```bash
# Run calibration (needs at least 2 ideal recordings of the same text aligned)
python scripts/calibrate.py

# Check sigma values
python -c "import json; s=json.load(open('configs/sigma.json')); [print(f'{k}: {v:.4f}') for k,v in s.items()]"
# Should see 6 numbers, none zero, none NaN, all positive

# Test with a known-answer signal: speed up a clip by 1.5x
# The pace signal in the sped-up region should be approximately -log(1.5) = -0.405
python -c "
from speechcoach.compare.baseline import signals
# ... (test with synthetic data)
print(f'Expected pace: {-0.405:.3f}')
print(f'Measured pace: {measured:.3f}')
"

# Run tests
python -m pytest tests/test_compare.py -v
```

### You're done when
- [ ] `configs/sigma.json` exists with sane numbers (no zeros, no NaN)
- [ ] A sped-up clip gives the correct pace signal (≈ -log(speed_factor))
- [ ] Identical inputs give all-zero signals
- [ ] All tests pass
- [ ] Sigma values posted in HANDOFF.md

---

## Member C — Day 3: Complete UI + Docker

**Task ID:** C3 · **Branch:** `c/C3-ui-complete`

### What to do

1. 🔧 **Per-word deviation strip** — a colored bar under the waveform:
   - Each word gets a colored block
   - Color intensity = how far from baseline (|z-score|)
   - Green = fine, yellow = slight issue, red = major flaw

2. 🔧 **Score radar chart** — 7 dimensions on a radar/spider chart:
   - Pacing, Pausing, Pitch, Energy, Emphasis, Clarity, Fluency
   - Scores from 0-100, from the mock data

3. 🔧 **Overall score display** — big number with a label

4. 🔧 **Loading and error states**:
   - Spinner while analysis is running
   - Error message if something goes wrong
   - Friendly message if audio format is wrong

5. 🔧 **Pydantic response models** in `src/speechcoach/api/main.py`:
   - Define Python classes that match the AnalysisResult JSON format
   - Validate every API response against them
   - If the response doesn't match, return a clear error

6. 🔧 **Dockerfile skeleton**:
   ```dockerfile
   # Stage 1: Build the frontend
   FROM node:20 AS frontend
   WORKDIR /app
   COPY app/ .
   RUN npm install && npm run build

   # Stage 2: Python runtime
   FROM python:3.11-slim
   # ... install deps, copy code, copy built frontend
   EXPOSE 7860
   CMD ["uvicorn", "speechcoach.api.main:app", "--host", "0.0.0.0", "--port", "7860"]
   ```

### How to test it works

```bash
# Check all UI elements render
make app
# Open in browser — you should see ALL of:
# ✅ Waveform with flaw regions
# ✅ Three charts
# ✅ Per-word colored strip
# ✅ Radar chart with 7 dimensions
# ✅ Overall score number
# ✅ Flaw list + explanations
# ✅ Upload form with loading state

# Test Docker builds
docker build -t speechcoach .
# Should complete without errors (the app may not fully work inside Docker yet)

# Test invalid JSON response
python -c "
from speechcoach.api.main import AnalysisResultModel
import json
data = json.load(open('app/public/mock_result.json'))
model = AnalysisResultModel(**data)
print('✅ Mock JSON passes validation')
"
```

### You're done when
- [ ] All UI components render from mock JSON
- [ ] Radar chart shows 7 dimensions
- [ ] Invalid JSON shows a friendly error (not a stack trace)
- [ ] `docker build` completes successfully
- [ ] Screenshot in HANDOFF.md

---

## Everyone — Day 3 Evening: 🎤 Record Ideal T1, T3 + Human Flaws

- Record ideal takes of T1 and T3 (3 takes each)
- A and one teammate start recording **human flawed takes** of T4:
  - Use the flaw cards from FLAW_SPEC section 4 (Rush, Monotone, Fillers, etc.)
  - Record 2-3 takes per card

### Day 3 Finish Line
| Check | How to verify |
|---|---|
| Full flaw engine works | A shows gradient plot — lines go up |
| Calibration done | B shows sigma.json with reasonable numbers |
| Complete UI on mock data | C shows all components in the browser |
| Docker builds | `docker build -t speechcoach .` succeeds |

---

# 📅 DAY 4: Detection and First Real Integration ⭐

---

## Member A — Day 4: Full Dataset Build

**Task ID:** A4 · **Branch:** `a/A4-full-dataset`

### What to do

1. 🔧 Run `build_dataset.py` for ALL 6 texts
2. 🔧 Generate `dataset/metadata.csv` with columns from CONTRACTS section 4
3. 🔧 Add `split` field: dev for T1, T2, T4, T5; test for T3, T6
4. 🔧 Implement `scripts/audacity_to_labels.py`:
   - Reads Audacity label export (tab-separated: start, end, label)
   - Converts to our label JSON format
   - Maps label text to flaw type enums
5. 📝 Write QC log: listen to at least 10 files, note any problems

### How to test it works

```bash
# Build everything
python -m speechcoach.dataset.build_dataset --config configs/flaws.yaml --texts T1,T2,T3,T4,T5,T6 --workers 4

# Validate
python scripts/validate_labels.py dataset/labels/

# Check metadata
python -c "
import pandas as pd
df = pd.read_csv('dataset/metadata.csv')
print(df.groupby(['text_id', 'source']).size())
print(f'Total files: {len(df)}')
print(f'Dev: {len(df[df.split==\"dev\"])}, Test: {len(df[df.split==\"test\"])}')
"
```

### You're done when
- [ ] All 6 texts have synthetic files generated
- [ ] `validate_labels.py` passes on everything
- [ ] `metadata.csv` has correct counts and split assignments
- [ ] QC log with notes on at least 10 files posted in HANDOFF.md

---

## Member B — Day 4: Region Detection + analyze()

**Task ID:** B4 · **Branch:** `b/B4-regions-analyze`

### What to do

1. 🔧 **Implement `src/speechcoach/compare/regions.py`** — `find_regions`:
   - Scan z-scores per signal
   - Flag words where `|z| > threshold`
   - Bridge small gaps between flagged words
   - Trim edges back to meaningful values
   - Assign flaw type based on signal + sign (e.g., negative pace = PACE_FAST)

2. 🔧 **Implement `src/speechcoach/analyze.py`** — `analyze()`:
   - This is THE main function. It chains everything together:
     ```
     load_audio → parse_transcript → align_words → frame_features → 
     word_table → window_stats → build_baseline → signals → z-scores → 
     find_regions → explain → score → return AnalysisResult
     ```
   - Explanations can be placeholder strings for now
   - Must return JSON matching CONTRACTS section 6 EXACTLY

3. 🔧 **Implement `scripts/run_eval.py --split dev`**:
   - Compare detected flaws vs ground-truth labels
   - For each detected flaw, check if it overlaps a real flaw by ≥50% (IoU ≥ 0.5)
   - Report: precision, recall, F1, boundary error, recall by severity level
   - Write `results/metrics_dev.csv`

### How to test it works

```bash
# Run analyze on a flawed file
python -m speechcoach.analyze dataset/sample/T4__synth-orig__PACE_FAST_L3.wav dataset/texts/T4.txt --baseline T4

# Check it detects the PACE_FAST region
# The output should show a flaw near the same time range as the ground truth

# Run evaluation
python scripts/run_eval.py --split dev
cat results/metrics_dev.csv
# Numbers may be poor at first — that's fine! Record them honestly.
```

### You're done when
- [ ] `analyze()` returns a valid AnalysisResult JSON
- [ ] Running it on a PACE_FAST_L3 file detects something near the right region
- [ ] `metrics_dev.csv` exists with first numbers (even if poor)
- [ ] 3 failure examples listed in HANDOFF.md
- [ ] Notify Member C that `analyze()` is ready!

---

## Member C — Day 4: Real Integration ⭐ MILESTONE M1

**Task ID:** C4 · **Branch:** `c/C4-integration`

### What to do

1. 🔧 Make `POST /analyze` call the REAL `analyze()` function instead of returning mock data
2. 🔧 Load the ML model once at server startup (not on every request)
3. 🔧 Cache results by hash of (audio + transcript + baseline_id + mode) so the same upload doesn't recompute
4. 🔧 Add a 25 MB upload limit, reject non-audio files
5. 🔧 Update `scripts/smoke.sh` to run `analyze()` on `dataset/sample/` and validate the output

### How to test it works

```bash
# Start the app
make app

# Upload a flawed file in the browser
# Select audio: dataset/sample/T4__synth-orig__PACE_FAST_L3.wav
# Paste transcript from dataset/texts/T4.txt
# Select baseline: T4
# Click Analyze

# You should see:
# ✅ Real flaw regions on the waveform (not mock data!)
# ✅ Real charts with actual feature data
# ✅ Real flaw detections

# Run smoke test
make smoke
```

### You're done when
- [ ] Upload a flawed file → see REAL detected flaws (not mock data)
- [ ] Results are cached (uploading the same file twice is instant)
- [ ] Uploading a >25MB file or a .txt file shows a friendly error
- [ ] `make smoke` passes
- [ ] **🎉 MILESTONE M1: Upload shows real flaw regions!**

### Day 4 Finish Line
| Check | How to verify |
|---|---|
| Full dataset built | A shows file counts |
| analyze() returns valid JSON | B runs it on a flawed file |
| **Real results in the browser** | C uploads a file and shows real flaws |
| Smoke test passes | `make smoke` ✅ |

---

# 📅 DAY 5: Explanations, Scoring, Demo ⭐

---

## Member A — Day 5: QC + Human Recordings + Listener Test

**Task ID:** A5 · **Branch:** `a/A5-qc-humans`

### What to do

1. 🔧 Fix issues from QC log
2. 🎤 Ensure at least 8 labeled human recordings exist (mix of flaw cards)
3. 🎤 Record 2 "almost perfect" takes
4. 🔧 Create listener test material: for 3 clips, select 5 severity versions each
5. 🔧 Write a script to compute rank correlation from listener responses
6. 📝 Draft `dataset/README.md` (the dataset card)

### You're done when
- [ ] Human labels validated with `validate_labels.py`
- [ ] Listener test Google Form sent to ≥10 people
- [ ] Dataset card draft in the repo

---

## Member B — Day 5: Tuning + Explanations + Scoring

**Task ID:** B5 · **Branch:** `b/B5-tuning-scoring`

### What to do (in 5 small steps — stop after each for review)

1. **Tune thresholds** on dev split ONLY:
   - Try different values for `tau_flag` and `tau_trim`
   - Show a small grid of F1 scores
   - Pick the best values, save to `configs/thresholds.yaml`
   - **Never look at the test split while tuning!**

2. **Explanation templates** (`src/speechcoach/explain/templates.py`):
   - For each flaw type, fill in the 5 fields with real measured numbers:
     ```
     observed: "You spoke at 5.9 syllables/second in this section"
     deviation: "Baseline speakers average 4.1 syl/s here (z = -4.5)"
     where: "Words 57-71 (0:42.1 - 0:51.3)"
     why: "Rushing reduces listener comprehension time"
     fix: "Practice this section at 80% of your current speed"
     ```

3. **Scoring** (`src/speechcoach/scoring/rubric.py`):
   - For each word: penalty = how far the z-score is from the "free zone"
   - Dimension score = 100 × (1 - weighted average of penalties)
   - Overall score = weighted average of 7 dimension scores
   - Weights from `configs/rubric.yaml`

4. **Wire into analyze()** — real explanations and scores in the output

5. **Score-vs-level plot** — prove that scores decrease as severity increases

### How to test it works

```bash
# Run on a flawed file — check explanations have real numbers
python -m speechcoach.analyze dataset/sample/T4__synth-orig__PACE_FAST_L3.wav dataset/texts/T4.txt --baseline T4 | python -m json.tool

# Check the "explanation" field of each flaw — all 5 subfields should have text
# Check the "scores" field — all 7 dimensions should have numbers

# Run eval with scores
python scripts/run_eval.py --split dev
# Check: Spearman correlation between score and severity level
```

### You're done when
- [ ] Every detected flaw has all 5 explanation fields with REAL numbers
- [ ] Scores exist for all 7 dimensions
- [ ] Score-vs-severity correlation reported on dev
- [ ] Thresholds frozen with a note in HANDOFF.md

---

## Member C — Day 5: Explanation Card + Demo Mode ⭐ MILESTONE M2

**Task ID:** C5 · **Branch:** `c/C5-demo`

### What to do

1. 🔧 **Explanation card** — show all 5 fields + a "show the math" tooltip:
   - Tooltip shows: participant value, baseline value, z-score, formula
   
2. 🔧 **Radar chart** — use REAL scores from `analyze()`, not mock data

3. 🔧 **Demo mode** — 3 buttons that work without any upload:
   - "Ideal" — loads a precomputed result for a perfect recording
   - "Almost Perfect" — one small flaw
   - "Botched" — multiple severe flaws
   - These use `GET /demo/{name}` which returns precomputed JSON + audio

### How to test it works

```bash
make app

# Click "Botched" demo button
# A stranger should understand within 1 minute:
# - What went wrong (the flaw list with explanations)
# - Where it went wrong (highlighted regions on the waveform)
# - How to fix it (the fix field in explanations)
# - How bad it was (the score and radar chart)
```

### You're done when
- [ ] Demo buttons work without any upload
- [ ] Explanation card shows all 5 fields with a "show the math" option
- [ ] Radar chart uses real scores
- [ ] **🎉 MILESTONE M2: A stranger understands the botched demo in 1 minute!**

### Day 5 Finish Line
| Check | How to verify |
|---|---|
| Explanations have real numbers | B shows analyze() output with all 5 fields |
| Scores decrease with severity | B shows the correlation plot |
| Demo mode works | C clicks "Botched" — it works with no upload |
| Human labels exist | A shows 8+ labeled human recordings |

---

# 📅 DAY 6: Hard Cases + 🔒 FEATURE FREEZE

---

## Member A — Day 6: Final Labels + Upload

**Task ID:** A6

- More human takes including a **held-out speaker** (someone NOT on the team)
- Finalize all labels and splits
- Run forced alignment on 30 synthetic files and compare vs ground truth (report error)
- Upload dataset to Hugging Face (private for now)

### You're done when: Numbers in HANDOFF, dataset on Hugging Face

---

## Member B — Day 6: Fillers + Mode B + Test Run

**Task ID:** B6

- Implement filled-pause detector (detect "um" and "uh")
- Implement Mode B (no matching ideal recordings — use general statistics)
- Run evaluation on TEST split **ONCE** — record numbers honestly
- **Do NOT change any thresholds after seeing test results**

### You're done when: `results/metrics_test.csv` exists with honest numbers

---

## Member C — Day 6: Polish + FREEZE

**Task ID:** C6

- Handle edge cases: large files, wrong formats, empty transcript, mismatched audio
- Phone layout
- Bug fixes only, no new features

### You're done when
- Bad inputs give friendly errors
- UI works on phone
- **🔒 Tag `v0.9-freeze` — NO MORE FEATURES after tonight**

---

# 📅 DAY 7: Package and Publish

| Member | Task | Done when |
|---|---|---|
| **A** | Publish dataset (Hugging Face public + Drive mirror), test download script on another device | Links work in incognito browser |
| **B** | Final results tables, reproducibility test (2 runs = identical JSON), extra unit tests | `make eval` regenerates tables; hash-equality test passes |
| **C** | Finish Dockerfile, deploy to Hugging Face Spaces, write README.md | Public URL works on phone AND another laptop; `make check` passes in Docker |

---

# 📅 DAY 8: Polish and Documentation

| Member | Task | Done when |
|---|---|---|
| **A** | Technical doc page 2 (dataset construction, gradient analysis, QC, listener test) + record footage | Section text + 2 figures |
| **B** | Technical doc pages 3-6 (features, method, scoring, results, limitations) with figures | Four sections, every number traceable to `results/` |
| **C** | Bug fixes ONLY, doc page 1 (problem + system overview), assemble full doc ≤6 pages, video script | Document v1 ≤ 6 pages |

---

# 📅 DAY 9: Fresh-Clone Test + Video

| Member | Task | Done when |
|---|---|---|
| **A** | Review README as a stranger, fix broken links, narrate data section (~2 min) | Links verified |
| **B** | Fresh clone on a DIFFERENT laptop — follow README exactly; narrate pipeline section (~2 min) | It works from scratch |
| **C** | Record dashboard demo, edit video (3-10 min), export final PDF | Video draft + final PDF |

---

# 📅 DAY 10: Buffer and Submit

**Everyone together:**
1. Upload video first (processing takes time)
2. Final link check: GitHub ✅ | Dataset (HF + Drive) ✅ | Live Space ✅ | YouTube ✅ | PDF ✅
3. Bug fixes only
4. **Submit several hours before the deadline**

---

# Quick Reference: Daily Verification Commands

```bash
# Run this EVERY DAY before pushing:
make check                     # All tests + smoke must pass
git status                     # Nothing unexpected
git diff --stat main           # Only YOUR files changed

# Verify GPU is working:
python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0)}')"

# Verify the full pipeline (after Day 4):
python -m speechcoach.analyze dataset/sample/*.wav dataset/texts/T4.txt --baseline T4

# Verify Docker (after Day 3):
docker build -t speechcoach .
docker run -p 7860:7860 speechcoach
# Open http://localhost:7860/health
```
