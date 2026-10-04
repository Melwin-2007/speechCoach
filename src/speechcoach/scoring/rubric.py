import numpy as np

def score(z_by_signal: dict, words: list[dict], cfg: dict) -> dict:
    """
    Score per word per dimension: p = clip((|z| - z_free) / (z_max - z_free), 0, 1)
    Dimension deviation D = 0.6*mean(p) + 0.4*P90(p)
    Dimension score = 100*(1 - D)
    Overall = sum(weight_d * score_d)
    """
    z_free = 1.0
    z_max = 4.0
    
    # Map signals to dimensions
    dim_map = {
        "pacing": ["pace"],
        "pausing": ["pause"],
        "pitch": ["pitch"],
        "energy": ["energy", "dynamics"],
        "emphasis": [], # Not fully implemented yet
        "clarity": ["clarity"],
        "fluency": [] # Fillers not fully implemented yet
    }
    
    dim_scores = {}
    for dim, signals in dim_map.items():
        if not signals:
            dim_scores[dim] = 100.0
            continue
            
        p_list = []
        for sig in signals:
            if sig in z_by_signal:
                z_vals = z_by_signal[sig]
                z_abs = np.abs(z_vals[:len(words)])
                p = np.clip((z_abs - z_free) / (z_max - z_free), 0.0, 1.0)
                p_list.append(p)
                
        if p_list:
            p_mean_across_signals = np.nanmean(p_list, axis=0) 
            valid_p = p_mean_across_signals[~np.isnan(p_mean_across_signals)]
            mean_p = float(np.mean(valid_p)) if len(valid_p) > 0 else 0.0
            p90 = float(np.percentile(valid_p, 90)) if len(valid_p) > 0 else 0.0
            D = 0.6 * mean_p + 0.4 * p90
            dim_scores[dim] = 100.0 * (1.0 - D)
        else:
            dim_scores[dim] = 100.0
            
    # Default weights if not in cfg
    weights = cfg.get("rubric_weights", {
        "pacing": 0.20,
        "pausing": 0.20,
        "pitch": 0.15,
        "energy": 0.15,
        "emphasis": 0.10,
        "clarity": 0.10,
        "fluency": 0.10
    })
    
    overall = 0.0
    total_w = 0.0
    for dim, val in dim_scores.items():
        w = weights.get(dim, 0.0)
        overall += val * w
        total_w += w
        
    if total_w > 0:
        overall /= total_w
        
    rounded_dims = {k: int(round(v)) for k, v in dim_scores.items()}
    
    return {
        "overall": round(overall, 1),
        "dimensions": rounded_dims
    }
