import os
import sys
import json
import argparse
import csv
from pathlib import Path
from collections import defaultdict

# Add src to pythonpath for IDE linters
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from speechcoach.analyze import analyze

def compute_iou(start1, end1, start2, end2):
    intersection = max(0, min(end1, end2) - max(start1, start2))
    union = max(end1, end2) - min(start1, start2)
    return intersection / union if union > 0 else 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", type=str, default="dev", help="Data split to evaluate on")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of files for quick testing")
    args = parser.parse_args()
    
    labels_dir = Path("dataset/labels")
    if not labels_dir.exists():
        print(f"No labels found in {labels_dir}")
        return
        
    eval_files = []
    for p in sorted(labels_dir.glob("*.json")):
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("split") == args.split and data.get("source") == "synthetic":
            eval_files.append((p, data))
            
    print(f"Found {len(eval_files)} synthetic files in split {args.split}")
    
    if args.limit:
        eval_files = eval_files[:args.limit]
        print(f"Limiting evaluation to {args.limit} files for quick testing.")
    
    if not eval_files:
        return

    # Metrics
    tp = 0
    fp = 0
    fn = 0
    boundary_errors = []
    recall_by_level = defaultdict(lambda: {"tp": 0, "fn": 0})
    
    failures = []
    os.makedirs("results", exist_ok=True)
    
    for label_path, label_data in eval_files:
        file_id = label_data["file_id"]
        text_id = label_data["text_id"]
        
        audio_path = None
        with open("dataset/metadata.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["file_id"] == file_id:
                    audio_path = row["audio_path"]
                    break
                    
        if not audio_path or not os.path.exists(audio_path):
            print(f"Audio not found for {file_id}, skipping")
            continue
            
        transcript_path = Path(f"dataset/texts/{text_id}.txt")
        if not transcript_path.exists():
            print(f"Transcript not found for {text_id}, skipping")
            continue
            
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript = f.read()
            
        print(f"Running analyze on {file_id}...")
        try:
            res = analyze(audio_path, transcript, baseline_id=text_id, mode="reference")
        except Exception as e:
            print(f"Error analyzing {file_id}: {e}")
            continue
            
        pred_flaws = res.get("flaws", [])
        true_flaws = label_data.get("flaws", [])
        level = label_data.get("severity_level", 0)
        
        matched_preds = set()
        for t in true_flaws:
            t_start, t_end, t_type = t["start_s"], t["end_s"], t["type"]
            best_iou = 0
            best_pred_idx = -1
            best_pred = None
            
            for i, p in enumerate(pred_flaws):
                if i in matched_preds:
                    continue
                if p["type"] != t_type:
                    continue
                    
                iou = compute_iou(t_start, t_end, p["start"], p["end"])
                if iou > best_iou:
                    best_iou = iou
                    best_pred_idx = i
                    best_pred = p
                    
            if best_iou >= 0.5:
                tp += 1
                matched_preds.add(best_pred_idx)
                recall_by_level[level]["tp"] += 1
                boundary_errors.append(abs(t_start - best_pred["start"]) + abs(t_end - best_pred["end"]))
            else:
                fn += 1
                recall_by_level[level]["fn"] += 1
                failures.append(f"{file_id}: missed {t_type} at {t_start:.1f}s")
                
        fp += len(pred_flaws) - len(matched_preds)
        
    precision = tp / (tp + fp) if tp + fp > 0 else 0.0
    recall = tp / (tp + fn) if tp + fn > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0.0
    mean_boundary_err = sum(boundary_errors) / len(boundary_errors) if boundary_errors else 0.0
    
    print("\n--- Eval v1 Results ---")
    print(f"Precision: {precision:.3f}")
    print(f"Recall: {recall:.3f}")
    print(f"F1 (IoU 0.5): {f1:.3f}")
    print(f"Mean Boundary Error: {mean_boundary_err:.3f} s")
    
    print("\nRecall by Level:")
    for lvl in sorted(recall_by_level.keys()):
        stats = recall_by_level[lvl]
        lvl_rec = stats["tp"] / (stats["tp"] + stats["fn"]) if (stats["tp"] + stats["fn"]) > 0 else 0.0
        print(f"  Level {lvl}: {lvl_rec:.2f}")
        
    if failures:
        print(f"\nSome failure examples (first 5 of {len(failures)}):")
        for f in failures[:5]:
            print("  - " + f)
            
    csv_path = f"results/metrics_{args.split}.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["split", "precision", "recall", "f1", "mean_boundary_error_s"])
        writer.writerow([args.split, f"{precision:.4f}", f"{recall:.4f}", f"{f1:.4f}", f"{mean_boundary_err:.4f}"])
        
    print(f"\nSaved metrics to {csv_path}")

if __name__ == "__main__":
    main()
