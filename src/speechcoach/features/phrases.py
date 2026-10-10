import numpy as np
from speechcoach.features.syllables import count_syllables

def group_phrases(words: list[dict], pause_threshold: float = 0.25) -> list[list[dict]]:
    """Group aligned words into prosodic phrases using punctuation and pauses."""
    phrases = []
    current_phrase = []
    
    for i, w in enumerate(words):
        current_phrase.append(w)
        break_phrase = False
        
        # 1. Break on Punctuation
        punct = w.get("punct", "").strip()
        if punct in [".", ",", "!", "?", ";", ":"]:
            break_phrase = True
            
        # 2. Break on Pauses > 0.25s
        if i < len(words) - 1:
            next_w = words[i+1]
            pause_dur = next_w['start'] - w['end']
            if pause_dur >= pause_threshold:
                break_phrase = True
                
        if break_phrase and current_phrase:
            phrases.append(current_phrase)
            current_phrase = []
            
    if current_phrase:
        phrases.append(current_phrase)
        
    return phrases

def speaker_normalization(g: dict, phrases: list[list[dict]]) -> dict:
    """Calculate speaker-level medians (F0, Energy, Pace)."""
    # 1. Median F0 (voiced frames only)
    valid_f0 = g['f0'][g['f0'] > 0]
    median_f0 = float(np.median(valid_f0)) if len(valid_f0) > 0 else 100.0
    
    # 2. Median Energy (voiced frames only)
    voiced_mask = g['f0'] > 0
    valid_db = g['db_rel'][voiced_mask]
    median_db = float(np.median(valid_db)) if len(valid_db) > 0 else -20.0
    
    # 3. Median Pace (Syllables/sec per phrase)
    phrase_rates = []
    for p in phrases:
        if not p: continue
        dur = p[-1]['end'] - p[0]['start']
        if dur > 0:
            syllables = sum(count_syllables(w.get('norm', w.get('raw', ''))) for w in p)
            phrase_rates.append(syllables / dur)
            
    median_pace = float(np.median(phrase_rates)) if phrase_rates else 4.0
    
    return {
        "median_f0": median_f0,
        "median_db": median_db,
        "median_pace": median_pace
    }

def phrase_features(phrases: list[list[dict]], g: dict, norms: dict) -> list[dict]:
    """Compute features per phrase using speaker-normalized values."""
    res = []
    t = g['t']
    
    # Convert global F0 to relative semitones
    st_rel = np.full_like(g['f0'], np.nan)
    mask_f0 = g['f0'] > 0
    if norms['median_f0'] > 0:
        st_rel[mask_f0] = 12 * np.log2(g['f0'][mask_f0] / norms['median_f0'])
        
    # Relative Energy
    db_rel_spk = g['db_rel'] - norms['median_db']
    
    for i, p in enumerate(phrases):
        start = p[0]['start']
        end = p[-1]['end']
        
        # Calculate Pause Before
        pause_before = 0.0
        if i > 0:
            prev_end = phrases[i-1][-1]['end']
            pause_before = start - prev_end
            
        dur = end - start
        sps = 0.0
        if dur > 0:
            syllables = sum(count_syllables(w.get('norm', w.get('raw', ''))) for w in p)
            sps = syllables / dur
            
        # Acoustic features within the phrase
        mask = (t >= start) & (t <= end) & mask_f0
        
        st_std = float(np.std(st_rel[mask])) if np.sum(mask) >= 2 else 0.0
        st_range = float(np.max(st_rel[mask]) - np.min(st_rel[mask])) if np.sum(mask) >= 2 else 0.0
        
        # Determine Pause Type
        pause_type = "mid" # default
        if i > 0:
            prev_punct = phrases[i-1][-1].get("punct", "").strip()
            if prev_punct in [".", "!", "?"]:
                pause_type = "terminal"
            elif prev_punct in [",", ";", ":"]:
                pause_type = "comma"
                
        # Phrase relative energy
        mask_all = (t >= start) & (t <= end)
        db_rel_phrase = float(np.median(db_rel_spk[mask_all])) if np.sum(mask_all) > 0 else 0.0
        db_mad = float(np.median(np.abs(db_rel_spk[mask_all] - np.median(db_rel_spk[mask_all])))) if np.sum(mask_all) > 0 else 0.0
        
        # Minimum confidence and constraints
        confs = [w.get("score", 1.0) for w in p]
        min_conf = min(confs) if confs else 1.0
        
        # Voiced fraction and duration constraints
        voiced_frac = float(np.sum(mask_f0[mask])) / float(np.sum(mask)) if np.sum(mask) > 0 else 0.0
        is_reliable = min_conf > 0.6 and voiced_frac >= 0.4 and dur >= 0.8 and (sps * dur >= 3.0)
        
        res.append({
            "id": i,
            "start": float(start),
            "end": float(end),
            "words": p,
            "pause_before": float(pause_before),
            "pause_type": pause_type,
            "sps": float(sps),
            "sps_rel": float(sps / norms['median_pace']) if norms['median_pace'] > 0 else 1.0,
            "st_std": st_std,
            "st_range": st_range,
            "db_rel": db_rel_phrase,
            "db_mad": db_mad,
            "reliable": is_reliable
        })
        
    return res

def interpolate_to_grid(phrase_feats: list[dict], duration_s: float, hop_s: float = 0.1) -> dict:
    """Interpolate phrase-level features onto a 0.1s grid."""
    t_grid = np.arange(0, duration_s, hop_s)
    n = len(t_grid)
    
    grid = {
        "t": t_grid,
        "sps": np.zeros(n),
        "sps_rel": np.ones(n),
        "st_std": np.zeros(n),
        "st_range": np.zeros(n),
        "db_rel": np.zeros(n),
        "db_mad": np.zeros(n),
        "pause_s": np.zeros(n),
        "pause_type": np.full(n, "none", dtype="<U8"),
        "phrase_id": np.full(n, -1, dtype=int),
        "reliable": np.zeros(n, dtype=bool),
        "pause_ok": np.zeros(n, dtype=bool)
    }
    
    for i, p in enumerate(phrase_feats):
        mask = (t_grid >= p['start']) & (t_grid <= p['end'])
        grid["phrase_id"][mask] = p["id"]
        grid["sps"][mask] = p["sps"]
        grid["sps_rel"][mask] = p["sps_rel"]
        grid["st_std"][mask] = p["st_std"]
        grid["st_range"][mask] = p["st_range"]
        grid["db_rel"][mask] = p["db_rel"]
        grid["db_mad"][mask] = p["db_mad"]
        grid["reliable"][mask] = p["reliable"]
        
        # Attribute pause_before to the beginning of the phrase (e.g. 0.2s window)
        pause_mask = (t_grid >= p['start']) & (t_grid < p['start'] + 0.2)
        grid["pause_s"][pause_mask] = p["pause_before"]
        grid["pause_type"][pause_mask] = p["pause_type"]
        
        # Determine if pause is assessable (both neighboring phrases are reliable)
        if i > 0:
            prev_reliable = phrase_feats[i-1]["reliable"]
            grid["pause_ok"][pause_mask] = prev_reliable and p["reliable"]
        else:
            # First pause is just leading silence
            grid["pause_ok"][pause_mask] = False
            
    gap_frames = grid["phrase_id"] < 0
    assert np.all(grid["sps"][gap_frames] == 0.0), "sps must be 0 in gaps"
    assert np.all(grid["reliable"][gap_frames] == False), "reliable must be False in gaps"
        
    return grid
