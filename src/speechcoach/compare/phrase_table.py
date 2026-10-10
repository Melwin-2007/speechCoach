import numpy as np

PHRASE_KEYS = ["sps", "sps_rel", "st_std", "st_range", "db_rel", "db_mad"]

def phrase_table(grid):
    """One row per phrase (first frame of each phrase_id)."""
    pid = grid["phrase_id"]
    ids = np.unique(pid[pid >= 0])
    first = np.array([np.argmax(pid == i) for i in ids])
    tab = {k: np.asarray(grid[k])[first] for k in PHRASE_KEYS}
    tab["id"] = ids
    tab["reliable"] = np.array([grid["reliable"][pid == i].all() for i in ids])
    return tab

def pause_events(grid):
    """One (type, seconds) per pause window, not per frame."""
    typ, ps = grid["pause_type"], grid["pause_s"]
    on = typ != "none"
    prev_on = np.r_[False, on[:-1]]
    changed = np.r_[True, (typ[1:] != typ[:-1]) | (ps[1:] != ps[:-1])]
    idx = np.where(on & (~prev_on | changed))[0]
    return [(str(typ[i]), float(ps[i])) for i in idx]
