# Canonical Ideal Audio Dataset

This directory contains the 4 canonical "ideal" baseline speech recordings for the SpeechCoach evaluation dataset ($T_1$ through $T_4$), representing a balanced mix of Indian and American English oratory styles.

---

## 1. Quick File Reference

| File Name | Text ID | Speaker / Title | Accent | Duration | Matching Transcript |
|:---|:---:|:---|:---|:---:|:---|
| `T1__orig-indianpep__ideal.wav` | **T1** | Indian Motivational Orator (*Missed Opportunities*) | Indian English | 186.5s | [`dataset/texts/T1.txt`](../../texts/T1.txt) |
| `T2__orig-mlk__ideal.wav` | **T2** | Martin Luther King Jr. (*I Have a Dream*) | American English | 234.1s | [`dataset/texts/T2.txt`](../../texts/T2.txt) |
| `T3__orig-kalam__ideal.wav` | **T3** | Dr. A.P.J. Abdul Kalam (*Culture of Excellence*) | Indian English | 198.9s | [`dataset/texts/T3.txt`](../../texts/T3.txt) |
| `T4__orig-lincoln__ideal.wav` | **T4** | Abraham Lincoln (*Gettysburg Address*) | American English | 145.2s | [`dataset/texts/T4.txt`](../../texts/T4.txt) |

---

## 2. Technical Specifications (Per CONTRACTS §0)

All audio files in this folder strictly conform to the repository contracts:
- **Format:** Uncompressed 16-bit PCM WAV
- **Sampling Rate:** 16,000 Hz (`16 kHz`)
- **Channels:** 1 channel (Mono)
- **Edge Padding:** Sliced to spoken speech with $\le 0.5\text{ s}$ clean edge silence (no intro titles, no outro music).

---

## 3. How to Access the Audio in Git

If you are a team member pulling this repo for the first time or syncing updates, run:

```bash
# 1. Fetch latest branches from remote
git fetch origin

# 2. Switch to the Member A data branch
git checkout a/A1-texts-sources

# 3. Pull the latest commits (which include these 4 WAV files)
git pull origin a/A1-texts-sources
```

All 4 WAV files will automatically be available in `dataset/audio/ideal/`.

---

## 4. How to Load and Use in Python

### Using `soundfile` (Recommended)
```python
import soundfile as sf
from pathlib import Path

audio_path = Path("dataset/audio/ideal/T1__orig-indianpep__ideal.wav")
samples, sr = sf.read(str(audio_path))

print(f"Sample Rate: {sr} Hz")           # 16000
print(f"Total Samples: {len(samples)}")
print(f"Duration: {len(samples)/sr:.2f}s")
```

### Using `torchaudio` (for Forced Alignment / Member B)
```python
import torchaudio

wav_path = "dataset/audio/ideal/T1__orig-indianpep__ideal.wav"
waveform, sample_rate = torchaudio.load(wav_path)

print(f"Waveform shape: {waveform.shape}")  # [1, N]
print(f"Sample rate: {sample_rate}")        # 16000
```

### Using Standard Library `wave` (No external dependencies)
```python
import wave

with wave.open("dataset/audio/ideal/T1__orig-indianpep__ideal.wav", "rb") as wf:
    print("Channels:", wf.getnchannels())       # 1
    print("Sample Width:", wf.getsampwidth())   # 2 (16-bit)
    print("Frame Rate:", wf.getframerate())     # 16000
    print("Frames:", wf.getnframes())
```

---

## 5. Team Responsibilities

- **Member A (Data):** Uses these ideal files to generate flaw injections (PACE_FAST, PAUSE_LONG, VOLUME_DROP, PITCH_MONOTONE, MUMBLE) via WORLD vocoder.
- **Member B (Pipeline):** Uses these files + matching `.txt` transcripts for forced alignment (`align/aligner.py`) and feature extraction (`features/frame.py`).
- **Member C (Dashboard):** Uses these files for frontend waveform visualization in wavesurfer.js.
