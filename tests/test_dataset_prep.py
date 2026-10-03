"""tests/test_dataset_prep.py - Unit tests for audio preparation and dataset texts integrity."""

import math
import wave
from pathlib import Path

import pytest

from scripts.prepare_audio import (
    compute_audio_stats,
    read_wav_samples,
    trim_silence,
    write_wav_samples,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_trim_silence_synthetic():
    """Assert trim_silence removes leading and trailing silence to <= specified pad."""
    sr = 16000
    # 2 seconds silence + 1 second 440 Hz tone + 2 seconds silence
    leading_silence = [0.0] * (2 * sr)
    tone = [0.5 * math.sin(2 * math.pi * 440 * i / sr) for i in range(sr)]
    trailing_silence = [0.0] * (2 * sr)
    signal = leading_silence + tone + trailing_silence

    # Total duration = 5.0 seconds
    assert len(signal) == 5 * sr

    trimmed = trim_silence(signal, sr=sr, threshold_db=-40.0, keep_silence_s=0.5)
    # Expected duration: 1.0s tone + 0.5s leading + 0.5s trailing = ~2.0s (+/- 0.05s)
    expected_samples = 2.0 * sr
    assert abs(len(trimmed) - expected_samples) <= (0.05 * sr)


def test_compute_audio_stats():
    """Assert audio stats correctly report duration, peak dB, and noise floor."""
    sr = 16000
    # 1 second of amplitude 0.5 tone -> peak dB should be 20*log10(0.5) ~= -6.02 dB
    tone = [0.5 * math.sin(2 * math.pi * 440 * i / sr) for i in range(sr)]
    stats = compute_audio_stats(tone, sr=sr)

    assert stats["duration_s"] == 1.0
    assert abs(stats["peak_db"] - (-6.02)) < 0.1
    assert stats["noise_floor_db"] <= 0.0


def test_write_and_read_wav(tmp_path):
    """Assert writing and reading a 16-bit mono WAV preserves samples."""
    sr = 16000
    samples = [0.25 * math.sin(2 * math.pi * 200 * i / sr) for i in range(sr // 2)]
    test_wav = tmp_path / "test_io.wav"

    write_wav_samples(test_wav, samples, framerate=sr)
    assert test_wav.exists()

    loaded_samples, loaded_sr = read_wav_samples(test_wav)
    assert loaded_sr == 16000
    assert len(loaded_samples) == len(samples)
    for orig, loaded in zip(samples[:50], loaded_samples[:50]):
        assert abs(orig - loaded) < 1e-3


def test_all_transcripts_exist_and_non_empty():
    """Assert exactly 4 texts T1..T4 exist in dataset/texts/ and contain valid text."""
    texts_dir = REPO_ROOT / "dataset" / "texts"
    assert texts_dir.is_dir()

    txt_files = sorted(list(texts_dir.glob("*.txt")))
    assert len(txt_files) == 4, f"Expected exactly 4 text files, found {len(txt_files)}"

    for i in range(1, 5):
        text_file = texts_dir / f"T{i}.txt"
        assert text_file.is_file(), f"Missing transcript {text_file.name}"
        content = text_file.read_text(encoding="utf-8").strip()
        assert len(content) > 100, f"Transcript {text_file.name} is too short"
        assert len(content.split()) >= 50, f"Transcript {text_file.name} has fewer than 50 words"


def test_sources_table_integrity():
    """Assert dataset/SOURCES.md exists and covers all 4 texts."""
    sources_file = REPO_ROOT / "dataset" / "SOURCES.md"
    assert sources_file.is_file()
    content = sources_file.read_text(encoding="utf-8")

    for i in range(1, 5):
        assert f"T{i}" in content, f"Text T{i} not documented in SOURCES.md"


def test_interim_wavs_conformance():
    """Assert all 4 prepared WAV files in data/interim/ and dataset/audio/ideal/ are strictly 16 kHz mono 16-bit PCM."""
    interim_dir = REPO_ROOT / "data" / "interim"
    wav_files = sorted(list(interim_dir.glob("T*__*__ideal.wav")))
    assert len(wav_files) == 4, f"Expected 4 interim WAVs, found {len(wav_files)}"

    for wav_path in wav_files:
        with wave.open(str(wav_path), "rb") as wf:
            assert wf.getframerate() == 16000, f"{wav_path.name} SR is {wf.getframerate()}, expected 16000"
            assert wf.getnchannels() == 1, f"{wav_path.name} channels is {wf.getnchannels()}, expected 1 (mono)"
            assert wf.getsampwidth() == 2, f"{wav_path.name} sampwidth is {wf.getsampwidth()}, expected 2 (16-bit)"
            duration = wf.getnframes() / float(wf.getframerate())
            assert duration >= 30.0, f"{wav_path.name} duration {duration}s is too short"


def test_human_audio_conformance():
    """Assert all 4 teammate recordings in dataset/audio/human/ are strictly 16 kHz mono 16-bit PCM."""
    human_dir = REPO_ROOT / "dataset" / "audio" / "human"
    assert human_dir.is_dir(), "Missing dataset/audio/human/ directory"

    wav_files = sorted(list(human_dir.glob("*.wav")))
    assert len(wav_files) == 4, f"Expected 4 human recordings, found {len(wav_files)}"

    expected_files = {
        "T1__h-adi__ideal.wav",
        "T1__h-krutika__ideal.wav",
        "T1__h-sagar__take1.wav",
        "T1__h-sagar__take2.wav",
    }
    found_names = {f.name for f in wav_files}
    assert found_names == expected_files

    for wav_path in wav_files:
        with wave.open(str(wav_path), "rb") as wf:
            assert wf.getframerate() == 16000, f"{wav_path.name} SR is {wf.getframerate()}, expected 16000"
            assert wf.getnchannels() == 1, f"{wav_path.name} channels is {wf.getnchannels()}, expected 1 (mono)"
            assert wf.getsampwidth() == 2, f"{wav_path.name} sampwidth is {wf.getsampwidth()}, expected 2 (16-bit)"
            duration = wf.getnframes() / float(wf.getframerate())
            assert 50.0 <= duration <= 100.0, f"{wav_path.name} unexpected duration {duration}s"


def test_human_transcripts_integrity():
    """Assert transcript text files exist for all human recordings and have sufficient words."""
    takes_dir = REPO_ROOT / "dataset" / "texts" / "takes"
    assert takes_dir.is_dir(), "Missing dataset/texts/takes/ directory"

    expected_transcripts = [
        "T1__h-adi__ideal.txt",
        "T1__h-krutika__ideal.txt",
        "T1__h-sagar__take1.txt",
        "T1__h-sagar__take2.txt",
    ]

    for name in expected_transcripts:
        txt_path = takes_dir / name
        assert txt_path.is_file(), f"Missing transcript {name}"
        words = txt_path.read_text(encoding="utf-8").strip().split()
        assert len(words) >= 100, f"Transcript {name} has fewer than 100 words ({len(words)})"


def test_metadata_csv_structure():
    """Assert metadata.csv conforms to CONTRACTS.md section 4."""
    meta_path = REPO_ROOT / "dataset" / "metadata.csv"
    assert meta_path.is_file()

    lines = [line.strip() for line in meta_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) >= 9  # Header + 4 canonical + 4 human
    header = lines[0]
    expected_header = "file_id,text_id,source,speaker,variant,severity_level,flaw_types,split,duration_s,license,audio_path,label_path"
    assert header == expected_header

