import json, hashlib
import numpy as np
from speechcoach.compare.phrase_table import phrase_table

def load_bounds(path):
    text = open(path).read()
    B = json.loads(text)
    B["hash"] = hashlib.sha256(text.encode()).hexdigest()[:12]
    return B

def rdev(x, med, mad, floor_sigma):
    sigma = max(1.4826 * mad, floor_sigma)
    return rdev_sigma(x, med, sigma)

def rdev_sigma(x, med, sigma):
    if sigma == 0:
        return np.zeros_like(x)
    return (np.asarray(x, float) - med) / sigma

def gated_local(loc, glo, raw_delta, min_abs, glob_min=1.0, override=4.0):
    ok_abs = np.abs(raw_delta) >= min_abs
    agree  = (np.sign(glo) == np.sign(loc)) & (np.abs(glo) >= glob_min)
    ok = ok_abs & (agree | (np.abs(loc) >= override))
    return np.where(ok, loc, 0.0)

def _own_spread(v, ok):
    v = v[ok]
    return float(np.median(np.abs(v - np.median(v)))) if len(v) >= 3 else 0.0

# ---------- local layer: vs this speaker's own phrases ----------
def local_dev(grid, feat, B):
    tab, F = phrase_table(grid), B["floor_sigma"]
    ok = tab["reliable"]
    W = B.get("within_spk_mad", {})
    
    if feat == "pace":
        own_mad = _own_spread(tab["sps_rel"], ok)
        sigma = max(1.4826 * own_mad, 1.4826 * W.get("sps_rel", 0.0), F["local_pace_rel"])
        return rdev_sigma(grid["sps_rel"], 1.0, sigma), grid["sps_rel"] - 1.0
    if feat == "pitch":
        med = float(np.median(tab["st_std"][ok])) if np.sum(ok) > 0 else 1.0
        own_mad = _own_spread(tab["st_std"], ok)
        sigma = max(1.4826 * own_mad, 1.4826 * W.get("st_std", 0.0), F["local_st_std"])
        return rdev_sigma(grid["st_std"], med, sigma), grid["st_std"] - med
    if feat == "energy":
        own_mad = _own_spread(tab["db_rel"], ok)
        sigma = max(1.4826 * own_mad, 1.4826 * W.get("db_rel", 0.0), F["local_db"])
        
        # Energy local reference: rolling median over previous ~5 phrases
        n = len(grid["t"])
        rolling_med = np.zeros(n)
        for i in range(len(tab["id"])):
            if i == 0:
                med = tab["db_rel"][i]
            else:
                prev = tab["db_rel"][max(0, i-5):i]
                med = float(np.median(prev))
            mask = grid["phrase_id"] == tab["id"][i]
            rolling_med[mask] = med
            
        return rdev_sigma(grid["db_rel"], rolling_med, sigma), grid["db_rel"] - rolling_med
    raise KeyError(feat)

# ---------- global layer: vs the good-corpus distribution ----------
def global_dev(grid, feat, B):
    F = B["floor_sigma"]
    if feat == "pace":
        s = B["sps"]
        return rdev(grid["sps"], s["median"], s["mad"], F["sps"])
    if feat == "pitch":                       # larger magnitude of std and range
        a = rdev(grid["st_std"], B["st_std"]["median"], B["st_std"]["mad"], F["st_std"])
        b = rdev(grid["st_range"], B["st_range"]["median"], B["st_range"]["mad"], F["st_range"])
        return np.where(np.abs(a) >= np.abs(b), a, b)
    if feat == "energy_dyn":                  # - = flat dynamics
        s = B["db_mad"]
        return rdev(grid["db_mad"], s["median"], s["mad"], F["db_mad"])
    raise KeyError(feat)

def pause_dev(grid, B):
    """Global only. Long pauses are flagged for any type. Short ones only at terminals."""
    dev = np.zeros(len(grid["t"]))
    for typ in ("terminal", "comma", "mid"):
        if typ not in B["pause_s"]:
            continue
        m = grid["pause_type"] == typ
        s = B["pause_s"][typ]
        d = rdev(grid["pause_s"][m], s["median"], s["mad"], B["floor_sigma"][f"pause_{typ}"])
        if typ != "terminal":
            d = np.clip(d, 0, None)           # a short comma or mid pause is not a flaw
        dev[m] = d
    return dev

def combine(local, glob):
    pick_local = np.abs(local) >= np.abs(glob)
    return np.where(pick_local, local, glob), np.where(pick_local, "local", "global")

# ---------- channels ----------
CHANNELS = {
 #  name            feat          sign  layers
 "PACE_FAST":     ("pace",        +1, ("local", "global")),
 "PACE_SLOW":     ("pace",        -1, ("local", "global")),
 "PITCH_ERRATIC": ("pitch",       +1, ("local", "global")),
 "PITCH_FLAT":    ("pitch",       -1, ("local", "global")),
 "ENERGY_LOW":    ("energy",      -1, ("local",)),
 "ENERGY_FLAT":   ("energy_dyn",  -1, ("global",)),
 "PAUSE_LONG":    ("pause",       +1, ("global",)),
 "PAUSE_MISSING": ("pause",       -1, ("global",)),
}

PARAMS = {  # detect_regions kwargs per channel
 "default": dict(enter=2.0, exit=1.0, min_dur=1.0, merge_gap=0.5, smooth=7),
 "PAUSE_LONG":    dict(enter=2.0, exit=1.0, min_dur=0.2, merge_gap=0.0, smooth=1),
 "PAUSE_MISSING": dict(enter=2.0, exit=1.0, min_dur=0.2, merge_gap=0.0, smooth=1),
}

def hold_through_gaps(dev, in_speech):
    if not in_speech.any():
        return np.zeros_like(dev)
    idx = np.where(in_speech, np.arange(len(dev)), -1)
    prev = np.maximum.accumulate(idx)
    nxt_idx = np.where(in_speech, np.arange(len(dev)), len(dev))
    nxt = np.minimum.accumulate(nxt_idx[::-1])[::-1]
    prev_c = np.where(prev >= 0, prev, nxt.clip(max=len(dev) - 1))
    nxt_c = np.where(nxt < len(dev), nxt, prev_c)
    pick_prev = (np.arange(len(dev)) - prev_c) <= (nxt_c - np.arange(len(dev)))
    return dev[np.where(pick_prev, prev_c, nxt_c)]

def channel_signal(name, grid, B):
    feat, sign, layers = CHANNELS[name]
    n = len(grid["t"])
    in_speech = (grid["phrase_id"] >= 0)
    if feat in ("pitch", "energy", "energy_dyn"):
        in_speech = in_speech & grid["reliable"]
    
    if feat == "pause":
        dev, src = pause_dev(grid, B), np.full(n, "global")
        valid = grid["pause_type"] != "none"
        valid &= grid["pause_ok"]
        dev = np.where(valid, dev, 0.0)
    else:
        glo = global_dev(grid, feat, B) if "global" in layers else np.zeros(n)
        if "local" in layers:
            loc, raw_delta = local_dev(grid, feat, B)
            min_abs = {"pace": 0.25, "pitch": 1.0, "energy": 5.0}.get(feat, 0.0)
            if name == "PITCH_FLAT":
                min_abs = 0.7
            loc = gated_local(loc, glo, raw_delta, min_abs=min_abs)
        else:
            loc = np.zeros(n)
            
        dev, src = combine(loc, glo)
        if layers == ("local",):  src = np.full(n, "local")
        if layers == ("global",): src = np.full(n, "global")
        dev = hold_through_gaps(dev, in_speech)
        
    return np.clip(sign * dev, 0, None), dev, src
