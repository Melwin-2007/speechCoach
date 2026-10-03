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

def window_stats(g: dict, words: list[dict], W: int = 6) -> dict[str, np.ndarray]:
    """
    Compute sliding window statistics over W words.
    
    Args:
        g: The frame features dict.
        words: Word dictionaries containing start/end.
        W: Window size.
        
    Returns:
        dict[str, np.ndarray]: Dict of arrays for win_dur, f0_std, db_mean, db_std.
    """
    N = len(words)
    if N < W:
        return {}
        
    win_dur = np.zeros(N - W + 1)
    f0_std = np.zeros(N - W + 1)
    db_mean = np.zeros(N - W + 1)
    db_std = np.zeros(N - W + 1)
    
    t = g['t']
    
    for i in range(N - W + 1):
        start = words[i]['start']
        end = words[i + W - 1]['end']
        win_dur[i] = end - start
        
        mask = (t >= start) & (t <= end)
        if np.any(mask):
            f0_std[i] = np.nanstd(g['f0'][mask])
            db_mean[i] = np.nanmean(g['db'][mask])
            db_std[i] = np.nanstd(g['db'][mask])
        else:
            f0_std[i] = np.nan
            db_mean[i] = np.nan
            db_std[i] = np.nan
            
    return {
        'win_dur': win_dur,
        'f0_std': f0_std,
        'db_mean': db_mean,
        'db_std': db_std
    }
