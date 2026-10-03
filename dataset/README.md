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

## 2. Audio Access & Setup

The canonical WAV audio files are committed directly to branch `a/A1-texts-sources` in `dataset/audio/ideal/`.

### Cloning or Pulling the Audio
```bash
# Fetch and checkout the Member A data branch
git fetch origin
git checkout a/A1-texts-sources
git pull origin a/A1-texts-sources
```

All 4 WAV files will be downloaded to `dataset/audio/ideal/` (~23.3 MB total).

---

## 3. How to Load and Inspect Audio in Python

All files are standardized to **16 kHz, mono, 16-bit PCM WAV**:

```python
import soundfile as sf

# Load audio samples
data, sr = sf.read("dataset/audio/ideal/T1__orig-indianpep__ideal.wav")
print(f"Sample rate: {sr} Hz, Duration: {len(data) / sr:.2f} seconds")

# Load matching transcript
with open("dataset/texts/T1.txt", "r", encoding="utf-8") as f:
    text = f.read()
print(f"Transcript character length: {len(text)}")
```

For complete instructions and torchaudio / alignment code snippets, see [`dataset/audio/ideal/README.md`](audio/ideal/README.md).
