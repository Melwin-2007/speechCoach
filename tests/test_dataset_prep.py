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
    """Assert texts exist in dataset/transcripts/ and contain valid text."""
    texts_dir = REPO_ROOT / "dataset" / "transcripts"
    assert texts_dir.is_dir()

    txt_files = sorted(list(texts_dir.glob("T*.txt")))
    assert len(txt_files) >= 4, f"Expected at least 4 text files, found {len(txt_files)}"

    for text_file in txt_files:
        assert text_file.is_file(), f"Missing transcript {text_file.name}"
        content = text_file.read_text(encoding="utf-8").strip()
        assert len(content) > 50, f"Transcript {text_file.name} is too short"
        assert len(content.split()) >= 15, f"Transcript {text_file.name} has fewer than 15 words"


def test_metadata_csv_structure():
    """Assert recordings.csv and speakers.csv conform to dataset specifications."""
    recordings_path = REPO_ROOT / "dataset" / "metadata" / "recordings.csv"
    assert recordings_path.is_file(), "Missing recordings.csv"
    lines = [line.strip() for line in recordings_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) >= 5, "recordings.csv must have header and rows"
    header = lines[0]
    expected_header = "file_id,text_id,speaker_id,quality,duration_s,license,redistributable"
    assert header == expected_header

    speakers_path = REPO_ROOT / "dataset" / "metadata" / "speakers.csv"
    assert speakers_path.is_file(), "Missing speakers.csv"
    spk_lines = [line.strip() for line in speakers_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(spk_lines) >= 4, "speakers.csv must have header and rows"
    assert spk_lines[0] == "speaker_id,source,speaker_split"


def test_good_audio_conformance():
    """Assert audio files in dataset/raw/good/ are strictly 16 kHz mono."""
    good_dir = REPO_ROOT / "dataset" / "raw" / "good"
    if not good_dir.is_dir():
        pytest.skip("dataset/raw/good directory not present")

    wav_files = sorted(list(good_dir.glob("*/*.wav")))
    if not wav_files:
        pytest.skip("No audio files in dataset/raw/good/")

    for wav_path in wav_files[:5]:
        with wave.open(str(wav_path), "rb") as wf:
            assert wf.getframerate() == 16000, f"{wav_path.name} SR is {wf.getframerate()}, expected 16000"
            assert wf.getnchannels() == 1, f"{wav_path.name} channels is {wf.getnchannels()}, expected 1 (mono)"
            assert wf.getsampwidth() == 2, f"{wav_path.name} sampwidth is {wf.getsampwidth()}, expected 2 (16-bit)"

