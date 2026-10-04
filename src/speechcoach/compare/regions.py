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
    min_region_words = cfg.get("min_region_words", 3)
    min_region_s = cfg.get("min_region_s", 1.0)
    
    # 1. Flag words where sign*z > tau_flag
    flagged = (sign * z) > tau_flag
    
    # 2. Bridge gaps of <= max_gap_words
    regions = []
    current_region = []
    
    for i, is_flagged in enumerate(flagged):
        if is_flagged:
            current_region.append(i)
        elif current_region:
            # Look ahead to see if there's a flagged word within max_gap_words
            lookahead_end = min(len(flagged), i + max_gap_words + 1)
            if np.any(flagged[i:lookahead_end]):
                current_region.append(i) # Bridge the gap
            else:
                regions.append(current_region)
                current_region = []
                
    if current_region:
        regions.append(current_region)
        
    final_regions = []
    for r in regions:
        # 3. Trim ends where sign*z < tau_trim
        start_idx = r[0]
        end_idx = r[-1]
        
        while start_idx <= end_idx and (sign * z[start_idx]) < tau_trim:
            start_idx += 1
            
        while end_idx >= start_idx and (sign * z[end_idx]) < tau_trim:
            end_idx -= 1
            
        if start_idx > end_idx:
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
