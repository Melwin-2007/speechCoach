"""Known-answer tests for window_stats. Each test targets one reported bug."""
import sys
from pathlib import Path

# Add src to pythonpath for IDE linters
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import numpy as np

from speechcoach.features.words import window_stats

HOP = 0.01
KEYS = ("win_dur", "f0_std", "db_mean", "db_std", "flux")


def make_words(durs, gap=0.05, extra_gap_after=None, extra_gap=0.0):
    """Words with given durations and gaps. Optionally one very long pause."""
    words, t = [], 0.5
    for i, d in enumerate(durs):
        words.append({"i": i, "start": round(t, 4), "end": round(t + d, 4)})
        t += d + gap
        if extra_gap_after == i:
            t += extra_gap
    return words


def make_g(words, st=0.0, db_in=-10.0, db_out=-60.0, flux_in=2.0, flux_out=100.0):
    """Frame features: constant inside words, very different values in pauses."""
    n = int((words[-1]["end"] + 0.5) / HOP)
    inw = np.zeros(n, bool)
    for w in words:
        inw[int(round(w["start"] / HOP)): int(round(w["end"] / HOP))] = True
    return {
        "t": np.arange(n) * HOP,
        "st": np.where(inw, st, np.nan),
        "f0": np.where(inw, 150.0, np.nan),
        "db": np.where(inw, db_in, db_out),
        "db_rel": np.where(inw, db_in, db_out),
        "flux": np.where(inw, flux_in, flux_out),
    }


# Bug 1: pacing must count speech time only
def test_win_dur_ignores_a_long_pause():
    durs = [0.3] * 12
    plain = make_words(durs)
    paused = make_words(durs, extra_gap_after=4, extra_gap=3.0)   # dramatic 3 s pause
    a = window_stats(make_g(plain), plain)["win_dur"]
    b = window_stats(make_g(paused), paused)["win_dur"]
    assert np.allclose(a, b), "a pause must not change speech time"
    # the buggy 'first start to last end' version would exceed 3 s for windows around the pause
    span_at_4 = paused[7]["end"] - paused[1]["start"]
    assert span_at_4 > 3.0 and b[4] < 3.0


# Bug 4: window must be centred on the word
def test_window_is_centred_and_clipped_at_the_edges():
    durs = [0.1 * (j + 1) for j in range(20)]          # word j lasts 0.1*(j+1) s
    words = make_words(durs)
    wd = window_stats(make_g(words), words)["win_dur"]
    assert np.isclose(wd[10], 0.1 * sum(range(8, 15)))  # words 7..13
    assert np.isclose(wd[0], 0.1 * sum(range(1, 5)))    # words 0..3 (clipped)
    assert np.isclose(wd[19], 0.1 * sum(range(17, 21)))  # words 16..19 (clipped)
    assert not np.isclose(wd[10], 0.1 * sum(range(11, 17)))  # NOT words 10..15 (forward-looking bug)


# Bug 2: pitch variation is measured on semitones, not Hz
def test_f0_std_uses_semitones_column():
    words = make_words([0.3] * 12)
    g = make_g(words)
    n = len(g["t"])
    alt = np.where(np.arange(n) % 2 == 0, 1.0, -1.0)     # +1 / -1 semitone
    g["st"] = np.where(np.isfinite(g["st"]), alt, np.nan)
    g["f0"] = np.where(np.isfinite(g["st"]), 150.0 * 2 ** (alt / 12), np.nan)   # same contour in Hz (std about 8.7 Hz)
    f0_std = window_stats(g, words)["f0_std"]
    assert np.allclose(f0_std[3:-3], 1.0, atol=0.05)     # semitones: std of +-1 st is 1 st, not ~8.7 (Hz)


def test_monotone_gives_zero_pitch_variation_and_unvoiced_gives_nan():
    words = make_words([0.3] * 12)
    g = make_g(words, st=0.0)                              # perfectly flat pitch
    assert np.allclose(window_stats(g, words)["f0_std"], 0.0)
    g["st"][:] = np.nan                                    # nothing voiced
    assert np.isnan(window_stats(g, words)["f0_std"]).all()   # no crash, no warning-driven garbage


# Bug 3: clarity (spectral flux) must exist and ignore pauses
def test_flux_present_and_computed_inside_words_only():
    words = make_words([0.3] * 12)
    out = window_stats(make_g(words), words)
    assert "flux" in out
    assert np.allclose(out["flux"], 2.0)                   # pauses (flux 100) are excluded


def test_loudness_stats_ignore_pauses():
    words = make_words([0.3] * 12)
    out = window_stats(make_g(words), words)
    assert np.allclose(out["db_mean"], -10.0)
    assert np.allclose(out["db_std"], 0.0)


# Contract shape
def test_returns_all_keys_with_one_value_per_word():
    words = make_words([0.3] * 8)
    out = window_stats(make_g(words), words)
    assert set(out) == set(KEYS)
    assert all(len(v) == len(words) for v in out.values())
    assert window_stats(make_g(words), [])["win_dur"].size == 0
