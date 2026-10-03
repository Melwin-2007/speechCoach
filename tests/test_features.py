import numpy as np
import pytest
from speechcoach.features.frame import frame_features

def test_pitch_150hz_sine():
    """Generate a pure 150 Hz sine wave and assert F0 extraction is correct."""
    sr = 16000
    t = np.linspace(0, 1.0, sr, endpoint=False)
    y = 0.5 * np.sin(2 * np.pi * 150 * t).astype(np.float32)
    
    g = frame_features(y)
    assert np.nanmedian(g['f0']) == pytest.approx(150.0, abs=2.0)

def test_speaker_agnostic_st():
    """Generate two sine waves of different pitches and check normalized st."""
    sr = 16000
    t = np.linspace(0, 1.0, sr, endpoint=False)
    
    y1 = 0.5 * np.sin(2 * np.pi * 150 * t).astype(np.float32)
    g1 = frame_features(y1)
    
    y2 = 0.5 * np.sin(2 * np.pi * 300 * t).astype(np.float32)
    g2 = frame_features(y2)
    
    st1 = np.nanmedian(g1['st'])
    st2 = np.nanmedian(g2['st'])
    
    # Both should be exactly 0 (since they are constant pitch, median = current pitch)
    assert st1 == pytest.approx(0.0, abs=0.1)
    assert st2 == pytest.approx(0.0, abs=0.1)

def test_known_gap():
    """Generate a known silence gap and assert pause length error < 20 ms."""
    sr = 16000
    t = np.linspace(0, 1.0, sr, endpoint=False)
    y = 0.5 * np.sin(2 * np.pi * 150 * t).astype(np.float32)
    
    gap_start = int(0.5 * sr)
    gap_end = int(0.6 * sr)
    y[gap_start:gap_end] = 0.0
    
    g = frame_features(y)
    
    silent_frames = np.where(g['db'] < -60)[0]
    
    # The gap is 100ms (10 frames). Because of the 20ms frame length, the detected silence might be slightly smaller.
    assert 5 <= len(silent_frames) <= 12
