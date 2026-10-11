# SpeechCoach

[![Python 3.11](https://img.shields.io/badge/python-3.11.9-blue.svg)](https://www.python.org/downloads/release/python-3119/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.5.1%2Bcu124-EE4C2C.svg)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **SpeechCoach** is an objective, multimodal speech evaluation and delivery coaching engine developed for the Multimodal AI Hackathon 2026 (Track C). It detects delivery flaws in spoken recordings by aligning transcripts, extracting acoustic features, and identifying statistical deviations against calibrated baseline distributions—producing deterministic, number-backed explanations without black-box LLM calls.

---

## Architecture Overview

```
                      ┌──────────────────────┐
                      │  Audio + Transcript  │
                      └──────────┬───────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       ┌───────────────────┐           ┌───────────────────┐
       │ Forced Alignment  │           │ Acoustic Feature  │
       │ (Torchaudio MMS)  │           │   Extraction      │
       └─────────┬─────────┘           └─────────┬─────────┘
                 │                               │
                 └───────────────┬───────────────┘
                                 ▼
                     ┌───────────────────────┐
                     │ Phrase Grouping &     │
                     │ Speaker Normalization │
                     └───────────┬───────────┘
                                 ▼
                     ┌───────────────────────┐
                     │ Dual-Layer Deviation  │
                     │  (Local vs Global)    │
                     └───────────┬───────────┘
                                 ▼
                     ┌───────────────────────┐
                     │ Region Detection with │
                     │   Hysteresis & Exit   │
                     └───────────┬───────────┘
                                 ▼
                     ┌───────────────────────┐
                     │ Deterministic Scoring │
                     │  & Math Explanations  │
                     └───────────┬───────────┘
                                 ▼
                     ┌───────────────────────┐
                     │ FastAPI REST Backend  │
                     │ + Interactive React UI│
                     └───────────────────────┘
```

1. **Forced Alignment**: Torchaudio MMS_FA extracts exact word start/end timestamps.
2. **Acoustic Profiling**:
   - **Pitch ($F_0$) & Voice Quality**: Parselmouth (Praat) autocorrelation and Harmonic-to-Noise Ratio (HNR).
   - **Loudness & Dynamics**: PyLoudnorm integrated LUFS and frame-level relative dB.
   - **Pacing & Pauses**: Syllable rate (syllables per second) and pause gap classification (comma, mid-phrase, terminal).
3. **Dual-Layer Deviation Tracking**:
   - **Local Layer**: Tracks within-speaker deviations relative to their own speaking baseline and neighboring phrases.
   - **Global Layer**: Compares performance against population bounds (median and median absolute deviation, MAD) computed across reference speakers.
4. **Hysteresis Region Detection**: Two-threshold hysteresis with unsmoothed edge expansion captures the complete temporal bounds of pacing, volume, and pitch flaws.
5. **Deterministic Explanations**: Every flaw cites exact measured figures, speaker baseline values, and effect sizes ($\Delta$, z-scores).

---

## Flaw Taxonomy

SpeechCoach analyzes 6 delivery channels across 3 severity levels ($L_2$ subtle, $L_3$ moderate, $L_4$ severe):

| Channel | Description | Primary Metric |
|---|---|---|
| `PACE_FAST` | Rushed delivery or accelerated phrasing | Syllables per second ($sps > \text{baseline}$) |
| `PACE_SLOW` | Dragged, hesitant speaking rate | Syllables per second ($sps < \text{baseline}$) |
| `PAUSE_LONG` | Unnatural silence or awkward hesitation | Gap duration snapped to word boundaries ($\Delta t$) |
| `PAUSE_MISSING`| Run-on sentences lacking punctuation pauses | Terminal sentence gap duration |
| `ENERGY_LOW` | Volume drop or fading voice projection | Relative loudness ($dB_{\text{rel}}$ vs whole-file median) |
| `ENERGY_FLAT` | Monotone dynamics lacking vocal variety | Within-phrase loudness variance |
| `PITCH_FLAT` | Monotone, robotic intonation | Semitone pitch standard deviation ($st_{\text{std}}$) |
| `PITCH_ERRATIC`| Erratic pitch breaks or unnatural squeaks | Pitch jumps and octave fluctuations |

---

## Directory Structure

```
SpeechCoach/
├── configs/               # Population bounds and calibration configurations
│   ├── population_bounds.json
│   ├── population_bounds_loo_*.json
│   └── thresholds.yaml
├── dataset/               # Speech recordings and annotations
│   ├── alignments/        # Word-level timestamp JSONs (good and flawed)
│   ├── metadata/          # recordings.csv, speakers.csv, flaws.json
│   ├── raw/               # 16 kHz mono audio (good/ and flawed/)
│   ├── splits/            # Train, dev, and test split definitions
│   └── transcripts/       # Canonical text transcripts (T01 - T08)
├── docs/                  # System architecture, contracts, and role definitions
│   ├── ARCHITECTURE.md
│   ├── CONTRACTS.md
│   ├── HANDOFF.md
│   └── TASKS.md
├── results/               # Frozen model hashes and evaluation reports
│   ├── eval_report.md
│   ├── eval_report_s04.md
│   └── frozen.json
├── scripts/               # Calibration, evaluation, and data preparation utilities
│   ├── fit_population_bounds.py
│   ├── freeze_parameters.py
│   ├── run_eval.py
│   └── verify_labels.py
├── src/speechcoach/       # Core Python library
│   ├── align/             # Forced alignment (Torchaudio MMS)
│   ├── audio/             # 16 kHz audio I/O and preprocessing
│   ├── features/          # Frame, word, and phrase acoustic feature extractors
│   ├── compare/           # Deviation metrics, bounds loading, and region hysteresis
│   ├── explain/           # Mathematical template-based explanations
│   ├── scoring/           # Dimension scores and overall delivery rating
│   ├── api/               # FastAPI application and schemas
│   └── analyze.py         # End-to-end analysis pipeline entrypoint
├── tests/                 # Colocated pytest unit tests
├── app/                   # React + Vite frontend dashboard
├── Dockerfile             # Production container definition
├── Makefile               # Standard project workflow targets
└── pyproject.toml         # Dependencies and build configuration
```

---

## Quickstart

### Prerequisites
- Python 3.11.9
- NVIDIA GPU with CUDA 12.4+ (recommended) or CPU fallback
- Node.js 18+ (for frontend dashboard)

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/Melwin-2007/speechCoach.git
cd speechCoach

# Create virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Tests
Execute the comprehensive test suite:
```bash
pytest tests
```

### 3. Run Pipeline Analysis
Analyze an individual recording from the command line:
```bash
python -m speechcoach.analyze \
  dataset/raw/good/S01/S01_T01_GOOD.wav \
  dataset/transcripts/T01.txt
```

### 4. Evaluate Held-Out Speakers
Run the evaluation harness:
```bash
# Evaluate on training/validation speakers S01-S03
python scripts/run_eval.py

# Evaluate on held-out speaker S04
python scripts/run_eval.py --s04_only
```

### 5. Launch API & Dashboard
```bash
# Start backend API (FastAPI on port 8000)
uvicorn speechcoach.api.main:app --host 0.0.0.0 --port 8000 --reload

# Start frontend dashboard (React Vite)
cd app
npm install
npm run dev
```

---

## Reproducibility & Frozen Hashes

Detector configurations, deviation channels, and parameter bounds are version-controlled and cryptographically locked. SHA-256 signatures are saved in `results/frozen.json`:
- **Clean False Positive Rate**: $\le 0.470$ FP/min on S01–S03 corpus.
- **Strict Monotonicity**: Recall increases monotonically with flaw severity ($L_2 \le L_3 \le L_4$).
- **Deterministic**: Fully deterministic across repeated runs with zero stochastic drift.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
