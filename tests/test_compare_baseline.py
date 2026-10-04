import sys
from pathlib import Path

# Add src to pythonpath for IDE linters
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import numpy as np
from speechcoach.compare.baseline import build_baseline, signals, calibrate

def test_build_baseline():
    ideal1 = {
        'win_dur': np.array([1.0, 2.0]),
        'f0_std': np.array([2.0, 4.0]),
        'db_std': np.array([1.0, 1.0]),
        'flux': np.array([1.0, 1.0]),
        'db_mean': np.array([-10.0, -12.0]),
        'pause_before': np.array([0.0, 0.5])
    }
    ideal2 = {
        'win_dur': np.array([4.0, 8.0]),
        'f0_std': np.array([8.0, 16.0]),
        'db_std': np.array([1.0, 1.0]),
        'flux': np.array([1.0, 1.0]),
        'db_mean': np.array([-20.0, -14.0]),
        'pause_before': np.array([0.0, 1.5])
    }
    B = build_baseline([ideal1, ideal2])
    # Geometric mean of win_dur: sqrt(1*4)=2, sqrt(2*8)=4
    assert np.allclose(B['win_dur'], [2.0, 4.0])
    # Arithmetic mean of db_mean: (-10 - 20)/2 = -15, (-12 - 14)/2 = -13
    assert np.allclose(B['db_mean'], [-15.0, -13.0])

def test_signals():
    P = {
        'win_dur': np.array([2.0]), # Sped-up clip (smaller duration) -> pacing should be < 0
        'f0_std': np.array([1.0]),
        'db_std': np.array([1.0]),
        'flux': np.array([1.0]),
        'db_mean': np.array([-10.0]),
        'pause_before': np.array([0.0])
    }
    B = {
        'win_dur': np.array([4.0]),
        'f0_std': np.array([1.0]),
        'db_std': np.array([1.0]),
        'flux': np.array([1.0]),
        'db_mean': np.array([-10.0]),
        'pause_before': np.array([0.0])
    }
    res = signals(P, B)
    assert np.allclose(res['pace'], np.log(2.0/4.0)) # < 0 faster
    assert res['pace'][0] < 0

def test_calibrate():
    loo_signals = {
        'pace': np.array([-1.0, -0.5, 0.0, 0.5, 1.0]),
        'pause': np.array([np.nan, 0.0])
    }
    floors = {'pace': 0.1, 'pause': 0.01}
    sigmas = calibrate(loo_signals, floors)
    # median = 0.0, mad = 0.5
    # sigma = 1.4826 * 0.5 = 0.7413
    assert np.isclose(sigmas['pace'], 0.7413)
    assert np.isclose(sigmas['pause'], 0.01) # fallback to floor since mad=0
