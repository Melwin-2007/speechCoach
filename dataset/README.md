# SpeechCoach Dataset Card

Welcome to the **SpeechCoach Evaluation Corpus** repository ($T_1$ through $T_4$).

This directory hosts the speech audio, canonical transcripts, alignments, and flaw annotations for testing speech delivery across pitch, rate, pauses, and loudness.

---

## 1. Corpus Summary

The corpus provides a 2–2 balance of Indian and American English speeches across motivational, inspirational, and historical oratory genres:

| Text ID | Title | Speaker | Accent | Spoken Duration | Word Count | Audio File | Transcript |
|:---:|:---|:---|:---|:---:|:---:|:---|:---|
| **T1** | Missed Opportunities & The Second Life | Indian Orator (Preppy Mic / Pep Talk) | Indian English | 186.5s | 302 | [`dataset/audio/ideal/T1__orig-indianpep__ideal.wav`](audio/ideal/T1__orig-indianpep__ideal.wav) | [`dataset/texts/T1.txt`](texts/T1.txt) |
| **T2** | I Have a Dream | Martin Luther King Jr. | American English | 234.1s | 388 | [`dataset/audio/ideal/T2__orig-mlk__ideal.wav`](audio/ideal/T2__orig-mlk__ideal.wav) | [`dataset/texts/T2.txt`](texts/T2.txt) |
| **T3** | Culture of Excellence & Being Unique | Dr. A.P.J. Abdul Kalam | Indian English | 198.9s | 391 | [`dataset/audio/ideal/T3__orig-kalam__ideal.wav`](audio/ideal/T3__orig-kalam__ideal.wav) | [`dataset/texts/T3.txt`](texts/T3.txt) |
| **T4** | The Gettysburg Address | Abraham Lincoln | American English | 145.2s | 270 | [`dataset/audio/ideal/T4__orig-lincoln__ideal.wav`](audio/ideal/T4__orig-lincoln__ideal.wav) | [`dataset/texts/T4.txt`](texts/T4.txt) |

Full source provenance and licensing are documented in [`dataset/SOURCES.md`](SOURCES.md).

---

## 2. Audio Access & Dataset Layout

All audio files in the SpeechCoach dataset are standardized to **16 kHz, mono, 16-bit PCM WAV**:

### Directory Structure
```
dataset/
├── audio/
│   ├── ideal/         # Canonical reference audio (T1-T4, ~23.3 MB)
│   ├── human/         # Teammate speech recordings (Adi, Krutika, Sagar)
│   └── synthetic/     # Controlled WORLD flaw audio (PACE_FAST, PACE_SLOW, MONOTONE, VOLUME_DROP)
├── alignments/        # Forced alignment JSONs (torchaudio MMS_FA word timestamps)
├── labels/            # Ground-truth flaw annotations and word maps (CONTRACTS §3)
├── sample/            # Smoke test package (ideal.wav, flawed.wav, label, alignment, transcript)
├── texts/
│   ├── T1.txt..T4.txt # Canonical texts
│   └── takes/         # Spoken transcripts for teammate recordings
└── metadata.csv       # Master file manifest (CONTRACTS §4)
```

---

## 3. Human Teammate Recordings ($T_1$)
Spoken takes by the team members for multi-speaker evaluation:
- [`dataset/audio/human/T1__h-adi__ideal.wav`](audio/human/T1__h-adi__ideal.wav) (77.3s, Adi)
- [`dataset/audio/human/T1__h-krutika__ideal.wav`](audio/human/T1__h-krutika__ideal.wav) (75.9s, Krutika)
- [`dataset/audio/human/T1__h-sagar__take1.wav`](audio/human/T1__h-sagar__take1.wav) (68.5s, Sagar Take 1)
- [`dataset/audio/human/T1__h-sagar__take2.wav`](audio/human/T1__h-sagar__take2.wav) (60.3s, Sagar Take 2)

---

## 4. Synthetic Benchmark Spectrum ($T_1$ & $T_4$)
30 calibrated synthetic flaw audio files generated via WORLD vocoder (`pyworld.harvest` + `cheaptrick` + `d4c`) in `dataset/audio/synthetic/`:
- **Resynth Controls:** `T1__synth-orig-indianpep__resynth_control.wav`, `T4__synth-orig-lincoln__resynth_control.wav`
- **Pace Variations:** `PACE_FAST` (L1–L5), `PACE_SLOW` (L1, L3, L5)
- **Pitch Variations:** `MONOTONE` (L1, L3, L5)
- **Energy Variations:** `VOLUME_DROP` (L1, L3, L5)

---

## 5. How to Load and Inspect Audio in Python

```python
import soundfile as sf
import json

# 1. Load audio samples
data, sr = sf.read("dataset/audio/ideal/T1__orig-indianpep__ideal.wav")
print(f"Sample rate: {sr} Hz, Duration: {len(data) / sr:.2f} seconds")

# 2. Load ground-truth label
with open("dataset/labels/T1__synth-orig-indianpep__PACE_FAST_L3.json", "r", encoding="utf-8") as f:
    label = json.load(f)
print(f"Flaws: {label['flaws']}")
```

