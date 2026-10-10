import sys, csv, itertools
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from speechcoach.compare.deviation import load_bounds, CHANNELS, PARAMS, channel_signal
from speechcoach.compare.regions import detect_regions
from speechcoach.audio.io import load_audio
from speechcoach.align.transcript import parse_transcript
from speechcoach.align.aligner import align_words
from speechcoach.features.frame import frame_features
from speechcoach.features.words import word_table
from speechcoach.features.phrases import group_phrases, speaker_normalization, phrase_features, interpolate_to_grid

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
    return grid

def get_files():
    recordings_csv = Path("e:/SpeechCoach/dataset/metadata/recordings.csv")
    flaws_csv = Path("e:/SpeechCoach/dataset/metadata/flaws.csv")
    
    good_files = []
    with open(recordings_csv, 'r') as f:
        for row in csv.DictReader(f):
            if row.get('quality') == 'GOOD':
                good_files.append({
                    "id": row["file_id"],
                    "audio": f"e:/SpeechCoach/dataset/raw/good/{row['speaker_id']}/{row['file_id']}.wav",
                    "transcript": open(f"e:/SpeechCoach/dataset/transcripts/{row['text_id']}.txt").read(),
                    "speaker": row["speaker_id"],
                    "dur": float(row["duration_s"])
                })
                
    injected_files = []
    if flaws_csv.exists():
        with open(flaws_csv, 'r') as f:
            for row in csv.DictReader(f):
                injected_files.append({
                    "id": row["file_id"],
                    "audio": f"e:/SpeechCoach/dataset/raw/flawed/{row['speaker_id']}/{row['file_id']}.wav",
                    "transcript": open(f"e:/SpeechCoach/dataset/transcripts/{row['text_id']}.txt").read(),
                    "speaker": row["speaker_id"],
                    "flaw_type": row["flaw_type"],
                    "start": float(row["start_time"]),
                    "end": float(row["end_time"]),
                    "severity": int(row["severity"])
                })
    return good_files, injected_files

def iou(s1, e1, s2, e2):
    intersection = max(0, min(e1, e2) - max(s1, s2))
    union = max(e1, e2) - min(s1, s2)
    return intersection / union if union > 0 else 0

def main():
    B = load_bounds("configs/population_bounds.json")
    good_files, injected_files = get_files()
    
    # 1. Cache signals
    print("Caching signals for GOOD files...")
    good_cache = {}
    total_good_mins = sum(f["dur"] for f in good_files) / 60.0
    for f in good_files:
        if not Path(f["audio"]).exists(): continue
        g = grid_for(f["audio"], f["transcript"])
        good_cache[f["id"]] = {"t": g["t"], "sigs": {ch: channel_signal(ch, g, B)[0] for ch in CHANNELS}, "grid": g}
        
    print("Caching signals for INJECTED files...")
    inj_cache = {}
    for f in injected_files:
        if not Path(f["audio"]).exists(): continue
        g = grid_for(f["audio"], f["transcript"])
        inj_cache[f["id"]] = {"t": g["t"], "sigs": {ch: channel_signal(ch, g, B)[0] for ch in CHANNELS}, "grid": g}

    # 2. Sweep
    grid_enter = [2.0, 2.5, 3.0, 3.5]
    grid_min_dur = [1.0, 1.5, 2.0]
    
    print("\n" + "="*80)
    print("SWEEP TABLE (FP/min vs Recall@IoU>=0.5 by Severity)")
    print("="*80)
    
    for channel in CHANNELS:
        print(f"\n--- Channel: {channel} ---")
        best = []
        
        # Diagnostic list for Pace Fast
        pace_diags = []
        
        for enter, md in itertools.product(grid_enter, grid_min_dur):
            p = PARAMS.get(channel, PARAMS["default"]).copy()
            if channel in ["PAUSE_LONG", "PAUSE_MISSING"]:
                p.update(dict(enter=enter, exit=enter/2)) # retain min_dur=0.2, smooth=1
            else:
                p.update(dict(enter=enter, exit=enter/2, min_dur=md))
            
            # Count FPs
            fps = 0
            for f in good_files:
                if f["id"] not in good_cache: continue
                t = good_cache[f["id"]]["t"]
                sig = good_cache[f["id"]]["sigs"][channel]
                spans = detect_regions(sig, t, **p)
                fps += len(spans)
            fp_per_min = fps / total_good_mins
            
            # Count Recall
            mapping = {
                "PACE_FAST": ["PACE_FAST"],
                "PACE_SLOW": ["PACE_SLOW"],
                "PITCH_ERRATIC": ["PITCH_ERRATIC"],
                "PITCH_FLAT": ["PITCH_FLAT", "MONOTONE"],
                "ENERGY_LOW": ["VOLUME_DROP"],
                "ENERGY_FLAT": ["VOLUME_DROP"],
                "PAUSE_LONG": ["PAUSE_EXCESS"],
                "PAUSE_MISSING": ["PAUSE_MISSING"]
            }
            valid_flaws = mapping.get(channel, [])
            relevant_inj = [f for f in injected_files if f["flaw_type"] in valid_flaws]
            
            if not relevant_inj:
                best.append((enter, md, fp_per_min, "N/A"))
                continue
                
            recalls = {2: [0,0], 3: [0,0], 4: [0,0]} # [found, total]
            for f in relevant_inj:
                if f["id"] not in inj_cache: continue
                t = inj_cache[f["id"]]["t"]
                sig = inj_cache[f["id"]]["sigs"][channel]
                spans = detect_regions(sig, t, **p)
                
                # Did any span overlap the injected flaw > 0.5?
                hit = False
                best_iou = 0
                for s_idx, e_idx in spans:
                    ov = iou(t[s_idx], t[e_idx], f["start"], f["end"])
                    if ov > best_iou: best_iou = ov
                    if ov >= 0.5:
                        hit = True
                        break
                        
                # Diagnostics for PACE_FAST L3/L4
                if channel == "PACE_FAST" and enter == 2.5 and md == 1.5 and f["severity"] >= 3:
                    win = (t >= f["start"]) & (t <= f["end"])
                    peak = sig[win].max() if win.any() else 0.0
                    measured = np.mean(inj_cache[f["id"]]["grid"]["sps"][win]) if win.any() else 0.0
                    pace_diags.append(f"{f['id']} (L{f['severity']}): peak_sig_in_gt={peak:.2f}, best_iou={best_iou:.2f}, measured_sps={measured:.2f}")
                
                recalls[f["severity"]][1] += 1
                if hit: recalls[f["severity"]][0] += 1
                
            recall_str = " | ".join(f"L{sev}:{r[0]}/{r[1]}" for sev, r in recalls.items() if r[1] > 0)
            best.append((enter, md, fp_per_min, recall_str))
            
        # Print
        print(f"{'enter':<6} | {'min_dur':<7} | {'FP/min':<6} | Recall (L2 | L3 | L4)")
        print("-" * 60)
        for enter, md, fp_rate, rec in best:
            print(f"{enter:<6} | {md:<7.1f} | {fp_rate:<6.2f} | {rec}")
            
        if pace_diags:
            print("\nPACE_FAST Diagnostics (enter=2.5, min_dur=1.5):")
            for d in pace_diags: print("  " + d)

if __name__ == "__main__":
    main()
