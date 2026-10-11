import pytest
import numpy as np
from speechcoach.features.phrases import (
    group_phrases,
    phrase_features,
    interpolate_to_grid,
    speaker_normalization
)

def test_gap_splitting_creates_mid_phrase_boundary():
    """Verify that an inserted 2.5s silence gap creates a phrase boundary typed 'mid'."""
    # Words without punctuation: "hello world" ... 2.5s pause ... "how are you"
    words = [
        {"raw": "hello", "norm": "hello", "punct": "", "start": 0.0, "end": 0.5, "score": 0.95},
        {"raw": "world", "norm": "world", "punct": "", "start": 0.6, "end": 1.1, "score": 0.95},
        # 2.5s gap between 1.1 and 3.6
        {"raw": "how", "norm": "how", "punct": "", "start": 3.6, "end": 4.0, "score": 0.95},
        {"raw": "are", "norm": "are", "punct": "", "start": 4.1, "end": 4.4, "score": 0.95},
        {"raw": "you", "norm": "you", "punct": ".", "start": 4.5, "end": 4.9, "score": 0.95},
    ]
    
    phrases = group_phrases(words, pause_threshold=0.25)
    assert len(phrases) == 2, f"Expected 2 phrases split across 2.5s gap, got {len(phrases)}"
    assert [w["norm"] for w in phrases[0]] == ["hello", "world"]
    assert [w["norm"] for w in phrases[1]] == ["how", "are", "you"]
    
    # Mock frame features (10 ms grid over 5.0 seconds)
    sr = 16000
    dur_s = 5.0
    n_frames = int(dur_s / 0.01)
    t = np.arange(n_frames) * 0.01
    f0 = np.full(n_frames, 150.0)
    db_rel = np.full(n_frames, -10.0)
    g = {"t": t, "f0": f0, "db_rel": db_rel}
    
    norms = speaker_normalization(g, phrases)
    p_feats = phrase_features(phrases, g, norms)
    
    assert len(p_feats) == 2
    # Second phrase was preceded by an unpunctuated 2.5s gap, so pause_type must be "mid"
    assert p_feats[1]["pause_type"] == "mid"
    assert pytest.approx(p_feats[1]["pause_before"], abs=0.05) == 2.5

def test_grid_gap_invariants():
    """Verify that in gap frames, sps == 0.0 and reliable == False."""
    words = [
        {"raw": "one", "norm": "one", "punct": "", "start": 0.5, "end": 1.5, "score": 0.95},
        # 2.0s gap
        {"raw": "two", "norm": "two", "punct": "", "start": 3.5, "end": 4.5, "score": 0.95},
    ]
    phrases = group_phrases(words, pause_threshold=0.25)
    
    dur_s = 5.0
    n_frames = int(dur_s / 0.01)
    t = np.arange(n_frames) * 0.01
    g = {"t": t, "f0": np.full(n_frames, 150.0), "db_rel": np.full(n_frames, -10.0)}
    norms = speaker_normalization(g, phrases)
    p_feats = phrase_features(phrases, g, norms)
    
    grid = interpolate_to_grid(p_feats, duration_s=dur_s, hop_s=0.1)
    
    # Gaps are frames where phrase_id == -1 (e.g., [0.0, 0.5) and [1.6, 3.4])
    gap_mask = grid["phrase_id"] < 0
    assert np.any(gap_mask), "Should have gap frames"
    assert np.all(grid["sps"][gap_mask] == 0.0), "sps must be 0.0 in gap frames"
    assert np.all(grid["reliable"][gap_mask] == False), "reliable must be False in gap frames"
