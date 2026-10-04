import numpy as np

def word_table(words: list[dict], g: dict) -> list[dict]:
    """
    Merge word dictionaries with frame-level acoustic features.
    
    Args:
        words: List of word dicts (must have 'start', 'end').
        g: The frame features dict from frame_features.
        
    Returns:
        list[dict]: Words appended with per-word stats and 'pause_before'.
    """
    res = []
    t = g['t']
    
    for i, w in enumerate(words):
        start = w['start']
        end = w['end']
        
        mask = (t >= start) & (t <= end)
        
        # Find the end time of the most recent valid word
        last_valid_end = 0.0
        for j in range(i - 1, -1, -1):
            if words[j]['end'] > 0.0:
                last_valid_end = words[j]['end']
                break
                
        pause_before = max(0.0, start - last_valid_end)
        
        w_out = w.copy()
        w_out['pause_before'] = pause_before
        
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            
            if not np.any(mask):
                w_out['f0_mean'] = np.nan
                w_out['st_mean'] = np.nan
                w_out['db_mean'] = np.nan
                w_out['db_max'] = np.nan
                w_out['db_rel_mean'] = np.nan
                w_out['flux_mean'] = np.nan
                w_out['hnr_mean'] = np.nan
                w_out['mfcc_mean'] = np.full(13, np.nan).tolist()
            else:
                w_out['f0_mean'] = float(np.nanmean(g['f0'][mask]))
                w_out['st_mean'] = float(np.nanmean(g['st'][mask]))
                w_out['db_mean'] = float(np.nanmean(g['db'][mask]))
                w_out['db_max'] = float(np.nanmax(g['db'][mask]))
                w_out['db_rel_mean'] = float(np.nanmean(g['db_rel'][mask]))
                w_out['flux_mean'] = float(np.nanmean(g['flux'][mask]))
                w_out['hnr_mean'] = float(np.nanmean(g['hnr'][mask]))
                w_out['mfcc_mean'] = np.nanmean(g['mfcc'][:, mask], axis=1).tolist()
            
        res.append(w_out)
        
    return res

def _finite_std(x: np.ndarray) -> float:
    """Std of the finite values; NaN when fewer than 2 are available."""
    x = x[np.isfinite(x)]
    return float(x.std()) if x.size >= 2 else float("nan")

def window_stats(g: dict, words: list[dict], W: int = 12) -> dict[str, np.ndarray]:
    """
    Compute sliding window statistics over W words.
    
    Args:
        g: The frame features dict.
        words: Word dictionaries containing start/end.
        W: Window size.
        
    Returns:
        dict[str, np.ndarray]: Dict of arrays for win_dur, f0_std, db_mean, db_std, flux.
    """
    HOP = 0.01
    KEYS = ("win_dur", "f0_std", "db_mean", "db_std", "flux")
    n = len(words)
    out = {k: np.full(n, np.nan) for k in KEYS}
    if n == 0:
        return out

    n_frames = len(g["t"])
    half = W // 2

    starts = np.array([w["start"] for w in words], dtype=float)
    ends = np.array([w["end"] for w in words], dtype=float)

    # Frame index range of every word, clipped to the grid.
    fs = np.clip(np.round(starts / HOP).astype(int), 0, n_frames)
    fe = np.maximum(np.clip(np.round(ends / HOP).astype(int), 0, n_frames), fs)

    # Frames that lie INSIDE some word (built once, not per window).
    inword = np.zeros(n_frames, dtype=bool)
    for a, b in zip(fs, fe):
        inword[a:b] = True

    # Prefix sums of word durations: speech time only, pauses never counted.
    cum = np.concatenate([[0.0], np.cumsum(ends - starts)])

    for i in range(n):
        lo, hi = max(0, i - half), min(n - 1, i + half)   # centred on word i
        out["win_dur"][i] = cum[hi + 1] - cum[lo]

        a, b = fs[lo], fe[hi]                              # frames spanned by the window
        out["f0_std"][i] = _finite_std(g["st"][a:b])       # semitones, NaN-aware

        m = inword[a:b]                                    # ignore pauses between words
        if m.any():
            db = g["db_rel"][a:b][m]
            out["db_mean"][i] = float(db.mean())
            out["db_std"][i] = float(db.std())
            out["flux"][i] = float(g["flux"][a:b][m].mean())
    return out
