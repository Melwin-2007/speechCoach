import os
import sys
import json
import argparse
import csv
import numpy as np
from pathlib import Path
from collections import defaultdict

# Add src to pythonpath for IDE linters
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from speechcoach.analyze import analyze
from speechcoach.evaluate import match

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", type=str, default="dev", help="Data split to evaluate on")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of files for quick testing")
    args = parser.parse_args()
    
    meta_path = Path("dataset/metadata.csv")
    if not meta_path.exists():
        print("No metadata found.")
        return
        
    reader_rows = []
    ideals_by_text = defaultdict(list)
    with open(meta_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            reader_rows.append(row)
            if row.get('severity_level', '0') == 'null':
                ideals_by_text[row["text_id"]].append(row)
                
    print("Texts with fewer than 2 other ideals (for LOO):")
    for text_id, ideals in ideals_by_text.items():
        speakers = set(row["speaker"] for row in ideals)
        for spk in speakers:
            other_ideals = [row for row in ideals if row["speaker"] != spk]
            if len(other_ideals) < 2:
                print(f"  {text_id} when excluding {spk}: has {len(other_ideals)} other ideals.")
    
    labels_dir = Path("dataset/labels")
    if not labels_dir.exists():
        print(f"No labels found in {labels_dir}")
        return
        
    eval_files = []
    for p in sorted(labels_dir.glob("*.json")):
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("split") == args.split:
            eval_files.append((p, data))
            
    print(f"\nFound {len(eval_files)} files in split {args.split}")
    
    if args.limit:
        eval_files = eval_files[:args.limit]
        print(f"Limiting evaluation to {args.limit} files for quick testing.")
    
    if not eval_files:
        return

    # Metrics
    total_tp = 0
    total_fp = 0
    total_fn = 0
    start_errors = []
    end_errors = []
    
    tp_type = defaultdict(int)
    fp_type = defaultdict(int)
    fn_type = defaultdict(int)
    
    false_regions_per_min = {}
    word_durs = []
    
    for label_path, label_data in eval_files:
        file_id = label_data["file_id"]
        text_id = label_data["text_id"]
        
        row = next((r for r in reader_rows if r["file_id"] == file_id), None)
        if not row:
            continue
            
        audio_path = row["audio_path"]
        variant = row["variant"]
        speaker = row["speaker"]
        source = row["source"]
        
        if not os.path.exists(audio_path):
            print(f"Audio not found for {file_id}, skipping")
            continue
            
        transcript_path = Path(f"dataset/texts/{text_id}.txt")
        if not transcript_path.exists():
            continue
            
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript = f.read()
            
        try:
            res = analyze(audio_path, transcript, baseline_id=text_id, mode="reference", exclude_speaker=speaker)
        except Exception as e:
            print(f"Error analyzing {file_id}: {e}")
            continue
            
        pred_flaws = res.get("flaws", [])
        true_flaws = label_data.get("flaws", [])
        
        duration_s = res["meta"]["duration_s"]
        
        for w in res.get("words", []):
            dur = w["end"] - w["start"]
            if dur > 0:
                word_durs.append(dur)
                
        if variant == "ideal" or variant == "resynth_control":
            frpm = (len(pred_flaws) / duration_s) * 60
            false_regions_per_min[file_id] = frpm
            
        if source == "synthetic" and variant != "resynth_control":
            tp, fp, fn, matches, matched_preds = match(true_flaws, pred_flaws)
            total_tp += tp
            total_fp += fp
            total_fn += fn
            
            for p_idx, p in enumerate(pred_flaws):
                if p_idx in matched_preds:
                    tp_type[p["type"]] += 1
                else:
                    fp_type[p["type"]] += 1
                    
            for t_idx, t in enumerate(true_flaws):
                is_matched = any(mt == t_idx for mt, mp in matches)
                if not is_matched:
                    fn_type[t["type"]] += 1
                    
            for t_idx, p_idx in matches:
                t = true_flaws[t_idx]
                p = pred_flaws[p_idx]
                t_start, t_end = t.get("start_s", t.get("start", 0)), t.get("end_s", t.get("end", 0))
                start_errors.append(abs(t_start - p["start"]))
                end_errors.append(abs(t_end - p["end"]))
                
            for t in true_flaws:
                t_start, t_end = t.get("start_s", t.get("start", 0)), t.get("end_s", t.get("end", 0))
                overlaps = 0
                union_intervals = []
                for p in pred_flaws:
                    if p["type"] == t["type"]:
                        inter_s = max(t_start, p["start"])
                        inter_e = min(t_end, p["end"])
                        if inter_e > inter_s:
                            overlaps += 1
                            union_intervals.append([inter_s, inter_e])
                
                union_intervals.sort()
                merged = []
                for interval in union_intervals:
                    if not merged or merged[-1][1] < interval[0]:
                        merged.append(interval)
                    else:
                        merged[-1][1] = max(merged[-1][1], interval[1])
                        
                covered_time = sum(e - s for s, e in merged)
                t_dur = t_end - t_start
                frac = covered_time / t_dur if t_dur > 0 else 0.0
                print(f"[{file_id}] True {t['type']} ({t_start:.1f}-{t_end:.1f}): overlaps={overlaps}, covered={frac:.2f}")

    print("\n--- Eval v1 Results ---")
    print(f"TP: {total_tp}, FP: {total_fp}, FN: {total_fn}")
    precision = total_tp / (total_tp + total_fp) if total_tp + total_fp > 0 else 0.0
    recall = total_tp / (total_tp + total_fn) if total_tp + total_fn > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0.0
    print(f"Precision: {precision:.3f}")
    print(f"Recall: {recall:.3f}")
    print(f"F1 (IoU 0.5): {f1:.3f}")
    
    mean_start_err = sum(start_errors) / len(start_errors) if start_errors else 0.0
    mean_end_err = sum(end_errors) / len(end_errors) if end_errors else 0.0
    print(f"Mean Start Error (matched): {mean_start_err:.3f} s")
    print(f"Mean End Error (matched): {mean_end_err:.3f} s")
    
    print("\nPrecision and Recall per flaw type:")
    all_types = set(list(tp_type.keys()) + list(fp_type.keys()) + list(fn_type.keys()))
    for t in sorted(list(all_types)):
        tp, fp, fn = tp_type[t], fp_type[t], fn_type[t]
        pr = tp / (tp + fp) if tp + fp > 0 else 0
        re = tp / (tp + fn) if tp + fn > 0 else 0
        print(f"  {t}: P={pr:.2f}, R={re:.2f} (TP={tp}, FP={fp}, FN={fn})")
        
    print("\nFalse regions per minute on ideal and resynth_control:")
    for fid, frpm in false_regions_per_min.items():
        print(f"  {fid}: {frpm:.2f} / min")
        
    if word_durs:
        perc = np.percentile(word_durs, [0, 5, 50])
        print(f"\nWord-duration percentiles (min, 5th, 50th): {perc}")

if __name__ == "__main__":
    main()
