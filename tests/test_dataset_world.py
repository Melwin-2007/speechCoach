"""tests/test_dataset_world.py - Unit tests for WORLD vocoder engine and label validation."""

import json
import math
from pathlib import Path

import numpy as np
import pytest

from scripts.validate_labels import validate_label_file
from speechcoach.dataset.world_engine import (
    analyze_world,
    map_word_times,
    render_time_program,
    stable_hash,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_stable_hash_reproducibility():
    """Assert stable_hash produces deterministic results across invocations."""
    h1 = stable_hash("test_id__PACE_FAST_L3")
    h2 = stable_hash("test_id__PACE_FAST_L3")
    assert h1 == h2
    assert isinstance(h1, int)
    assert h1 != stable_hash("test_id__PACE_FAST_L4")


def test_analyze_world_synthetic_tone():
    """Assert analyze_world extracts expected F0 on a known 200 Hz harmonic signal."""
    sr = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    # 200 Hz harmonic complex tone (speech-like)
    y = sum((1.0 / k) * np.sin(2 * np.pi * (200 * k) * t) for k in range(1, 5))
    y = (0.5 * y / np.max(np.abs(y))).astype(np.float32)

    f0, sp, ap = analyze_world(y, fs=sr, f0_floor=60.0, f0_ceil=600.0, frame_period=5.0)

    assert len(f0) > 0
    assert sp.shape[0] == len(f0)
    assert ap.shape[0] == len(f0)

    # Voiced frames should have F0 close to 200 Hz (+/- 2 Hz)
    voiced_f0 = f0[f0 > 0]
    assert len(voiced_f0) > 0.8 * len(f0)
    assert abs(np.median(voiced_f0) - 200.0) < 2.0


def test_render_time_program_synthetic():
    """Assert render_time_program compresses region duration by the speed factor."""
    sr = 16000
    duration = 2.0
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    y = 0.5 * np.sin(2 * np.pi * 220 * t).astype(np.float32)

    f0, sp, ap = analyze_world(y, fs=sr, f0_floor=60.0, f0_ceil=600.0, frame_period=5.0)

    # Accelerate 0.5s to 1.5s by 1.5x
    start_s, end_s, speed = 0.5, 1.5, 1.5
    y_synth, new_start, new_end = render_time_program(
        f0, sp, ap, sr, start_s, end_s, speed, frame_period=5.0
    )

    expected_orig_dur = 1.0
    expected_new_dur = expected_orig_dur / speed
    expected_total_dur = duration - (expected_orig_dur - expected_new_dur)

    actual_synth_dur = len(y_synth) / sr
    assert abs(actual_synth_dur - expected_total_dur) < 0.05
    assert new_start == start_s
    assert abs((new_end - new_start) - expected_new_dur) < 0.01


def test_map_word_times_monotonicity():
    """Assert mapped word boundaries remain strictly ordered and within duration."""
    words = [
        {"i": 0, "raw": "One", "norm": "one", "punct": "", "start": 0.2, "end": 0.6, "conf": 0.9},
        {"i": 1, "raw": "two,", "norm": "two", "punct": ",", "start": 0.8, "end": 1.2, "conf": 0.95},
        {"i": 2, "raw": "three", "norm": "three", "punct": "", "start": 1.4, "end": 1.8, "conf": 0.92},
        {"i": 3, "raw": "four.", "norm": "four", "punct": ".", "start": 2.0, "end": 2.5, "conf": 0.98},
    ]

    mapped = map_word_times(words, start_s=0.7, end_s=1.9, speed=1.5)

    assert len(mapped) == 4
    prev_end = 0.0
    for w in mapped:
        assert w["start"] <= w["end"]
        assert w["start"] >= prev_end - 0.001
        prev_end = w["end"]

    # Word 1 and 2 inside region should have shorter duration
    orig_dur_w1 = words[1]["end"] - words[1]["start"]
    mapped_dur_w1 = mapped[1]["end"] - mapped[1]["start"]
    assert mapped_dur_w1 < orig_dur_w1


def test_validate_labels_on_generated():
    """Assert all generated labels in dataset/labels pass validate_labels."""
    label_dir = REPO_ROOT / "dataset" / "labels"
    labels = list(label_dir.glob("*.json"))
    assert len(labels) >= 6, f"Expected at least 6 labels, found {len(labels)}"

    for lbl in labels:
        errs = validate_label_file(lbl)
        assert errs == [], f"Validation errors in {lbl.name}: {errs}"
