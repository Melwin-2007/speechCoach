import os
import sys
import json
import csv
import yaml
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict
import torch

sys.path.insert(0, str(Path("src").resolve()))
from speechcoach.audio.io import load_audio
from speechcoach.align.transcript import parse_transcript
from speechcoach.align.aligner import align_words
from speechcoach.features.frame import frame_features
from speechcoach.features.words import word_table, window_stats
from speechcoach.compare.baseline import signals
from speechcoach.compare.regions import find_regions
from speechcoach.analyze import load_baseline
from speechcoach.scoring.rubric import score

def compute_iou(start1, end1, start2, end2):
    intersection = max(0, min(end1, end2) - max(start1, start2))
    union = max(end1, end2) - min(start1, start2)
    return intersection / union if union > 0 else 0

def main():
    print("Loading config...")
    with open("configs/thresholds.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
        
    sigma_path = Path("configs/sigma.json")
    if sigma_path.exists():
        with open(sigma_path, "r", encoding="utf-8") as f:
            sigmas = json.load(f)
    else:
        sigmas = {k: 1.0 for k in ["pace", "pause", "pitch", "energy", "dynamics", "clarity"]}
        
    labels_dir = Path("dataset/labels")
    eval_files = []
    for p in sorted(labels_dir.glob("*.json")):
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("split") == "dev" and data.get("source") == "synthetic":
            eval_files.append(data)
            
    print(f"Found {len(eval_files)} dev files. Extracting features (this happens once)...")
    
    file_features = {}
    
    for label_data in eval_files:
        file_id = label_data["file_id"]
        text_id = label_data["text_id"]
        
        audio_path = None
        with open("dataset/metadata.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["file_id"] == file_id:
                    audio_path = row["audio_path"]
                    break
                    
        if not audio_path: continue
        
        transcript_path = f"dataset/texts/{text_id}.txt"
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript = f.read()
            
        print(f"  Extracting {file_id}...")
        try:
            y = load_audio(audio_path, sr=cfg.get("sr", 16000), target_lufs=cfg.get("target_lufs", -23.0))
            raw_words = parse_transcript(transcript)
            words = align_words(y, raw_words)
            g = frame_features(y)
            w_table = word_table(words, g)
            w_stats = window_stats(g, words)
            
            P = {k: v for k, v in w_stats.items()}
            P['pause_before'] = np.array([w['pause_before'] for w in w_table])
            
            B = load_baseline(text_id)
            if not B: B = {k: np.zeros_like(v) for k, v in P.items()}
            
            raw_signals = signals(P, B)
            z_scores = {k: raw_signals[k] / sigmas.get(k, 1.0) for k in raw_signals}
            
            file_features[file_id] = {
                "z_scores": z_scores,
                "words": words,
                "true_flaws": label_data.get("flaws", []),
                "level": label_data.get("severity_level", 0)
            }
        except Exception as e:
            print(f"Error on {file_id}: {e}")

    print("\n--- Tuning loop ---")
    best_f1 = -1
    best_params = (2.0, 1.5)
    
    # Tuning grid
    tau_flags = [1.5, 2.0, 2.5]
    tau_trims = [1.0, 1.5, 2.0]
    
    for tf in tau_flags:
        for tt in tau_trims:
            if tt >= tf: continue
            
            test_cfg = cfg.copy()
            test_cfg["tau_flag"] = tf
            test_cfg["tau_trim"] = tt
            
            tp = fp = fn = 0
            
            for file_id, data in file_features.items():
                z_scores = data["z_scores"]
                words = data["words"]
                true_flaws = data["true_flaws"]
                
                pred_flaws = []
                def test_add_regions(signal_name, sign, f_type):
                    if signal_name not in z_scores: return
                    z_arr = z_scores[signal_name]
                    event_mode = (signal_name == "pause")
                    regions = find_regions(z_arr, words, sign, test_cfg, event_mode=event_mode)
                    for r in regions:
                        pred_flaws.append({"type": f_type, "start": r["start"], "end": r["end"]})
                
                test_add_regions("pace", -1, "PACE_FAST")
                test_add_regions("pace", 1, "PACE_SLOW")
                test_add_regions("pause", -1, "PAUSE_MISSING")
                test_add_regions("pause", 1, "PAUSE_EXCESS")
                test_add_regions("pitch", -1, "MONOTONE")
                test_add_regions("pitch", 1, "PITCH_ERRATIC")
                test_add_regions("energy", -1, "VOLUME_DROP")
                test_add_regions("dynamics", -1, "FLAT_ENERGY")
                test_add_regions("clarity", -1, "CLARITY")
                
                matched_preds = set()
                for t in true_flaws:
                    t_start, t_end, t_type = t["start_s"], t["end_s"], t["type"]
                    best_iou, best_pred_idx = 0, -1
                    for i, p in enumerate(pred_flaws):
                        if i in matched_preds or p["type"] != t_type: continue
                        iou = compute_iou(t_start, t_end, p["start"], p["end"])
                        if iou > best_iou:
                            best_iou = iou
                            best_pred_idx = i
                    if best_iou >= 0.5:
                        tp += 1
                        matched_preds.add(best_pred_idx)
                    else:
                        fn += 1
                fp += len(pred_flaws) - len(matched_preds)
                
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            print(f"tau_flag={tf}, tau_trim={tt} => P: {precision:.3f}, R: {recall:.3f}, F1: {f1:.3f}")
            if f1 > best_f1:
                best_f1 = f1
                best_params = (tf, tt)
                
    print(f"\nBest Config: tau_flag={best_params[0]}, tau_trim={best_params[1]} with F1={best_f1:.3f}")
    
    # Save best
    cfg["tau_flag"] = best_params[0]
    cfg["tau_trim"] = best_params[1]
    with open("configs/thresholds.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)
        
    print("\nGenerating Score-vs-Level data with best config...")
    scores_by_level = defaultdict(list)
    
    for file_id, data in file_features.items():
        z_scores = data["z_scores"]
        words = data["words"]
        level = data["level"]
        
        res_scores = score(z_scores, words, cfg)
        scores_by_level[level].append(res_scores["overall"])
        
    # Plotting
    levels = sorted(scores_by_level.keys())
    mean_scores = [np.mean(scores_by_level[lvl]) for lvl in levels]
    
    plt.figure(figsize=(8, 5))
    plt.plot(levels, mean_scores, marker='o', linewidth=2)
    plt.title("Overall Score vs Flaw Severity Level (Dev Split)")
    plt.xlabel("Severity Level (0 = Ideal)")
    plt.ylabel("Overall Score (0-100)")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(levels)
    plt.ylim(0, 100)
    
    os.makedirs("results", exist_ok=True)
    plt.savefig("results/score_vs_level.png")
    print("Saved plot to results/score_vs_level.png")
    
if __name__ == "__main__":
    main()
