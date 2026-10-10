import numpy as np

def find_regions(z: np.ndarray, words: list[dict], sign: int, cfg: dict, event_mode: bool = False) -> list[dict]:
    """
    Find contiguous regions of deviation in the signal.
    
    Args:
        z: Array of z-scores, length should match len(words)
        words: List of word dictionaries
        sign: +1 to look for positive deviations, -1 for negative
        cfg: Configuration dictionary containing thresholds
        event_mode: If True, bypass minimum region length requirements (for pauses/fillers)
    
    Returns:
        List of dictionaries containing region bounds and severity.
    """
    if len(z) == 0 or len(words) == 0:
        return []
        
    tau_flag = cfg.get("tau_flag", 2.0)
    tau_trim = cfg.get("tau_trim", 1.5)
    max_gap_words = cfg.get("max_gap_words", 2)
    max_gap_s = cfg.get("max_gap_s", 0.5)
    min_region_words = cfg.get("min_region_words", 3)
    min_region_s = cfg.get("min_region_s", 1.0)
    
    # 1. Base threshold (hysteresis lower bound)
    with np.errstate(invalid='ignore'):
        above_trim = (sign * z) >= tau_trim
    
    # 2. Bridge gaps
    regions = []
    current_region = []
    
    for i, is_above in enumerate(above_trim):
        if is_above:
            current_region.append(i)
        elif current_region:
            # Check gap condition
            next_above = -1
            for j in range(i + 1, len(above_trim)):
                if above_trim[j]:
                    next_above = j
                    break
                    
            if next_above != -1:
                gap_words = next_above - i
                gap_s = words[next_above]["start"] - words[i - 1]["end"]
                if gap_words <= max_gap_words or gap_s <= max_gap_s:
                    current_region.append(i)
                    continue
                    
            regions.append(current_region)
            current_region = []
            
    if current_region:
        regions.append(current_region)
        
    final_regions = []
    for r in regions:
        start_idx = r[0]
        end_idx = r[-1]
        
        # Hysteresis requirement: region MUST peak above tau_flag
        with np.errstate(invalid='ignore'):
            if not np.any((sign * z[start_idx:end_idx + 1]) >= tau_flag):
                continue

            
        # Extract word objects
        region_words = words[start_idx:end_idx + 1]
        start_s = region_words[0]["start"]
        end_s = region_words[-1]["end"]
        
        # 4. Filter by length and duration
        word_count = end_idx - start_idx + 1
        duration = end_s - start_s
        
        if not event_mode:
            if word_count < min_region_words or duration < min_region_s:
                continue
                
        # Calculate severity and band
        # Severity = clip((mean(|z|) - 1.5) / 4.5, 0, 1)
        z_region = z[start_idx:end_idx + 1]
        valid_z = z_region[~np.isnan(z_region)]
        if len(valid_z) == 0:
            continue
        mean_abs_z = float(np.mean(np.abs(valid_z)))
        severity = float(np.clip((mean_abs_z - 1.5) / 4.5, 0.0, 1.0))
        
        # Bands: minor |z|>=2, moderate >=3, major >=4.5
        if mean_abs_z >= 4.5:
            band = "major"
        elif mean_abs_z >= 3.0:
            band = "moderate"
        else:
            band = "minor"
            
        final_regions.append({
            "first_word": int(start_idx),
            "last_word": int(end_idx),
            "start": float(start_s),
            "end": float(end_s),
            "severity": float(severity),
            "band": band,
            "z_mean": float(np.mean(valid_z))
        })
        
    return final_regions

def detect_regions(dev: np.ndarray, t: np.ndarray, enter: float = 2.0, exit: float = 1.0, min_dur: float = 1.0, merge_gap: float = 0.5, smooth: int = 7) -> list[tuple[int, int]]:
    """
    Find regions using hysteresis (enter/exit thresholds) and median filtering.
    As proposed in the mentor critique.
    
    Args:
        dev: signed deviation per 0.1s frame for one feature.
        t: array of time values (e.g. 0.1s grid).
    """
    from scipy.ndimage import median_filter
    # 1. Median filtering
    if smooth > 1:
        dev_smooth = median_filter(dev, size=smooth)
    else:
        dev_smooth = dev
        
    # 2. Hysteresis detection
    regions = []
    active = None
    for i, d in enumerate(np.abs(dev_smooth)):
        if active is None and d > enter:
            active = i
        elif active is not None and d < exit:
            regions.append((active, i))
            active = None
            
    if active is not None:
        regions.append((active, len(dev_smooth) - 1))
        
    # 3. Merge close regions
    merged = []
    for r in regions:
        if not merged:
            merged.append(list(r))
        else:
            prev_end_idx = merged[-1][1]
            curr_start_idx = r[0]
            if t[curr_start_idx] - t[prev_end_idx] <= merge_gap:
                merged[-1][1] = r[1]
            else:
                merged.append(list(r))
                
    # 4. Filter by minimum duration
    final_regions = []
    for r in merged:
        start_idx, end_idx = r
        if t[end_idx] - t[start_idx] >= min_dur:
            final_regions.append((start_idx, end_idx))
            
    return final_regions
