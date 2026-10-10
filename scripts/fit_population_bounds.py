import json, hashlib, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from speechcoach.audio.io import load_audio
from speechcoach.align.transcript import parse_transcript
from speechcoach.align.aligner import align_words
from speechcoach.features.frame import frame_features
from speechcoach.features.words import word_table
from speechcoach.features.phrases import group_phrases, speaker_normalization, phrase_features, interpolate_to_grid
from speechcoach.compare.phrase_table import phrase_table, pause_events

MIN_N = 12   # below this, a bound is unreliable, so warn

def grid_for(audio_path, transcript):
    y = load_audio(Path(audio_path), sr=16000, target_lufs=-23.0)
    duration_s = float(len(y) / 16000.0)
    raw_words = parse_transcript(transcript)
    words = align_words(y, raw_words)
    g = frame_features(y)
    w_table = word_table(words, g)
    phrases = group_phrases(w_table)
    norms = speaker_normalization(g, phrases)
    p_feats = phrase_features(phrases, g, norms)
    grid = interpolate_to_grid(p_feats, duration_s)
    
    assert (grid["sps"][grid["phrase_id"] < 0] == 0).all(), "sps leak into gaps"
    assert (grid["reliable"][grid["phrase_id"] < 0] == False).all(), "reliable leak into gaps"
    
    return grid

def stat(x):
    x = np.asarray(x, float)
    if len(x) == 0:
        return {"median": 0.0, "mad": 0.0, "n": 0}
    med = float(np.median(x))
    return {"median": round(med, 4),
            "mad": round(float(np.median(np.abs(x - med))), 4),
            "n": int(len(x))}

def main(out="configs/population_bounds.json", exclude_spk=None):
    import csv
    recordings_csv = Path("e:/SpeechCoach/dataset/metadata/recordings.csv")
    items = []
    if recordings_csv.exists():
        with open(recordings_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('quality') == 'GOOD':
                    if exclude_spk and row["speaker_id"] == exclude_spk:
                        continue
                    items.append({
                        "audio": f"e:/SpeechCoach/dataset/raw/good/{row['speaker_id']}/{row['file_id']}.wav",
                        "transcript": open(f"e:/SpeechCoach/dataset/transcripts/{row['text_id']}.txt").read(),
                        "label": "good",
                        "speaker": row["speaker_id"]
                    })
                    
    items.sort(key=lambda m: m["audio"])
    
    # Store per-speaker values to compute within_spk_mad
    speaker_feats = {k: {} for k in ["sps", "sps_rel", "st_std", "st_range", "db_mad", "db_rel"]}
    
    pooled = {k: [] for k in ["sps", "st_std", "st_range", "db_mad"]}
    pauses = {"terminal": [], "comma": [], "mid": []}
    
    print(f"Fitting bounds on {len(items)} files...")
    for m in items:
        if not Path(m["audio"]).exists(): continue
        g = grid_for(m["audio"], m["transcript"])
        tab = phrase_table(g)
        ok = tab["reliable"]
        spk = m["speaker"]
        
        for k in pooled:
            pooled[k].extend(tab[k][ok])
            
        for k in speaker_feats:
            if spk not in speaker_feats[k]:
                speaker_feats[k][spk] = []
            speaker_feats[k][spk].extend(tab[k][ok])
            
        for typ, s in pause_events(g):
            if typ != "none" and typ in pauses:
                pauses[typ].append(s)
                
    B = {k: stat(v) for k, v in pooled.items()}
    B["pause_s"] = {t: stat(v) for t, v in pauses.items() if len(v)}
    
    # Compute within_spk_mad
    within_spk_mad = {}
    for k in speaker_feats:
        mads = []
        for spk, vals in speaker_feats[k].items():
            if len(vals) >= 3:
                mads.append(stat(vals)["mad"])
        if mads:
            within_spk_mad[k] = round(float(np.median(mads)), 4)
        else:
            within_spk_mad[k] = 0.0
    
    B["within_spk_mad"] = within_spk_mad
    
    # sigma floors: the guard against S04-style false positives
    B["floor_sigma"] = {"sps": 0.9, "st_std": 0.6, "st_range": 2.0, "db_mad": 1.0,
                        "pause_terminal": 0.15, "pause_comma": 0.10, "pause_mid": 0.10,
                        "local_pace_rel": 0.15, "local_st_std": 0.6, "local_db": 2.0}
    B["n_speakers"] = len({m.get("speaker", m["audio"]) for m in items})
    
    for k, v in {**pooled, **{f"pause_{t}": p for t, p in pauses.items()}}.items():
        if len(v) < MIN_N:
            print(f"WARNING: only {len(v)} samples for {k}", file=sys.stderr)
            
    body = json.dumps(B, sort_keys=True, indent=2)
    Path(out).write_text(body)
    print("sha256:", hashlib.sha256(body.encode()).hexdigest()[:12])

if __name__ == "__main__":
    main()
