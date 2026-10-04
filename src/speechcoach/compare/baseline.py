import warnings
import numpy as np

def build_baseline(ideals: list[dict]) -> dict:
    """
    Build baseline for a text from its ideal recordings.
    
    Args:
        ideals: list of dictionaries, each containing arrays for 
                'win_dur', 'f0_std', 'db_std', 'flux', 'db_mean', 'pause_before'.
        
    Returns:
        dict: aggregated baseline signals.
    """
    if not ideals:
        return {}
        
    keys_geo = ['win_dur', 'f0_std', 'db_std', 'flux']
    keys_arith = ['db_mean', 'pause_before']
    
    baseline = {}
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        for key in keys_geo:
            max_len = max(len(ideal[key]) for ideal in ideals)
            padded = []
            for ideal in ideals:
                arr = ideal[key]
                pad_width = max_len - len(arr)
                padded.append(np.pad(arr, (0, pad_width), constant_values=np.nan))
            stacked = np.stack(padded)
            # Geometric mean: exp(mean(log(x)))
            # Add small epsilon to avoid log(0) if any value is exactly 0
            log_stacked = np.log(np.where(stacked <= 0, np.nan, stacked))
            baseline[key] = np.exp(np.nanmean(log_stacked, axis=0))
            
        for key in keys_arith:
            max_len = max(len(ideal[key]) for ideal in ideals)
            padded = []
            for ideal in ideals:
                arr = ideal[key]
                pad_width = max_len - len(arr)
                padded.append(np.pad(arr, (0, pad_width), constant_values=np.nan))
            stacked = np.stack(padded)
            baseline[key] = np.nanmean(stacked, axis=0)
            
    return baseline

def signals(P: dict, B: dict) -> dict[str, np.ndarray]:
    """
    Calculate deviation signals of participant P vs baseline B.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        
        def align(p_arr, b_arr):
            n = min(len(p_arr), len(b_arr))
            return p_arr[:n], b_arr[:n]
            
        p_wd, b_wd = align(P["win_dur"], B["win_dur"])
        p_pb, b_pb = align(P["pause_before"], B["pause_before"])
        p_f0, b_f0 = align(P["f0_std"], B["f0_std"])
        p_dbm, b_dbm = align(P["db_mean"], B["db_mean"])
        p_dbs, b_dbs = align(P["db_std"], B["db_std"])
        p_flx, b_flx = align(P["flux"], B["flux"])
        
        res = {
            "pace": np.log(p_wd / b_wd),
            "pause": p_pb - b_pb,
            "pitch": np.log(p_f0 / b_f0),
            "energy": p_dbm - b_dbm,
            "dynamics": np.log(p_dbs / b_dbs),
            "clarity": np.log(p_flx / b_flx),
        }
    return res

def calibrate(loo_signals: dict[str, np.ndarray], floors: dict[str, float]) -> dict[str, float]:
    """
    Calibrate sigma using leave-one-out signals.
    """
    sigmas = {}
    for sig, values in loo_signals.items():
        v = values[np.isfinite(values)]
        if len(v) == 0:
            sigmas[sig] = float(floors.get(sig, 1e-6))
        else:
            med = np.median(v)
            mad = np.median(np.abs(v - med))
            sigma = max(1.4826 * mad, floors.get(sig, 1e-6))
            sigmas[sig] = float(sigma)
    return sigmas
