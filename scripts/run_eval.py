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
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from speechcoach.analyze import analyze

def match_flaw(true_flaw, pred_flaws):
    t_start = true_flaw["start"]
    t_end = true_flaw["end"]
    t_dur = max(t_end - t_start, 0.001)
    
    best_iou = 0.0
    best_iou_match = None
    
    best_time_match = None
    
    for p in pred_flaws:
        if p["type"] == true_flaw["type"]:
            # IoU
            inter_s = max(t_start, p["start"])
            inter_e = min(t_end, p["end"])
            inter = max(inter_e - inter_s, 0.0)
            union = max(p["end"], t_end) - min(p["start"], t_start)
            iou = inter / max(union, 0.001)
            
            if iou > best_iou:
                best_iou = iou
                best_iou_match = p
                
            # Time tolerance
            if abs(p["start"] - t_start) <= 1.0 and abs(p["end"] - t_end) <= 1.0:
                best_time_match = p
                
    return best_iou_match is not None and best_iou >= 0.5, best_time_match is not None, best_iou

def main():
    # Precompute LOO bounds
    print("Precomputing LOO bounds...", flush=True)
    from scripts.fit_population_bounds import main as fit_bounds
    for spk in ["S01", "S02", "S03", "S04"]:
        out_path = f"configs/population_bounds_loo_{spk}.json"
        if not os.path.exists(out_path):
            fit_bounds(out=out_path, exclude_spk=spk)
        
    labels_path = Path("dataset/metadata/flaws.json")
    if not labels_path.exists():
        print(f"No labels found in {labels_path}")
        return
        
    with open(labels_path, "r", encoding="utf-8") as f:
        all_flaws = json.load(f)
        
    flaw_map = defaultdict(list)
    for f in all_flaws:
        # only keep L2, L3, L4
        if f.get("severity", 0) >= 2:
            flaw_map[f["file_id"]].append({
                "type": f["flaw_type"],
                "start": f["start_time"],
                "end": f["end_time"],
                "severity": f["severity"]
            })
            
    reader_rows = []
    with open(Path("dataset/metadata/recordings.csv"), "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            reader_rows.append(row)
            
    eval_files = []
    good_files = []
    
    for row in reader_rows:
        fid = row["file_id"]
        spk = row["speaker_id"]
        # Skip S04 for tuning unless doing final test
        if spk == "S04":
            continue # For tuning phase
            
        if row.get('quality') == 'GOOD':
            good_files.append((fid, row["speaker_id"], row["text_id"]))
            
    for fid, flaws in flaw_map.items():
        spk = fid.split("_")[0]
        text_id = fid.split("_")[1]
        if spk == "S04": continue
        eval_files.append((fid, {
            "file_id": fid,
            "speaker": spk,
            "text_id": text_id,
            "flaws": flaws
        }))
            
    print(f"\nEvaluating {len(eval_files)} flawed files and {len(good_files)} good files (S01-S03)")
    
    # FP tracking
    fp_by_type = defaultdict(int)
    fp_by_speaker = defaultdict(int)
    good_duration_s = 0.0
    speaker_duration_s = defaultdict(float)
    
    # Recall tracking
    # (channel, severity) -> {"iou_pass": int, "time_pass": int, "total": int}
    recall_stats = defaultdict(lambda: {"iou": 0, "time": 0, "total": 0})
    
    # Determinism test on first file
    det_file = eval_files[0] if eval_files else None
    if det_file:
        audio_path = f"dataset/raw/flawed/{det_file[1]['speaker']}/{det_file[0]}.wav"
        transcript = open(f"dataset/transcripts/{det_file[1]['text_id']}.txt", encoding="utf-8").read()
        res1 = analyze(audio_path, transcript, exclude_speaker=det_file[1]['speaker'])
        res2 = analyze(audio_path, transcript, exclude_speaker=det_file[1]['speaker'])
        
        # Check determinism
        assert res1.get("bounds_hash") == res2.get("bounds_hash"), "Bounds hash determinism failed"
        assert len(res1.get("regions", [])) == len(res2.get("regions", [])), "Flaws length determinism failed"
        for f1, f2 in zip(res1.get("regions", []), res2.get("regions", [])):
            assert f1["start"] == f2["start"] and f1["end"] == f2["end"] and f1["type"] == f2["type"], "Flaw values determinism failed"
        print("Determinism test PASSED", flush=True)
    
    # Evaluate Good files for FP/min
    for i, (fid, spk, text_id) in enumerate(good_files):
        print(f"Good {i+1}/{len(good_files)}: {fid}", flush=True)
        try:
            audio_path = f"dataset/raw/good/{spk}/{fid}.wav"
            if not os.path.exists(audio_path): continue
            transcript = open(f"dataset/transcripts/{text_id}.txt", encoding="utf-8").read()
            res = analyze(audio_path, transcript, exclude_speaker=spk)
            dur = res["meta"]["duration_s"]
            good_duration_s += dur
            speaker_duration_s[spk] += dur
            
            for f in res.get("regions", []):
                fp_by_type[f["type"]] += 1
                fp_by_speaker[spk] += 1
        except Exception as e:
            import traceback
            print(f"Error on good file {fid}: {e}\n{traceback.format_exc()}", flush=True)

            
    # Evaluate Flawed files for Recall
    for i, (fid, label_data) in enumerate(eval_files):
        print(f"Flawed {i+1}/{len(eval_files)}: {fid}", flush=True)
        try:
            spk = label_data["speaker"]
            text_id = label_data["text_id"]
            row = None
            audio_path = f"dataset/raw/flawed/{spk}/{fid}.wav"
            if not os.path.exists(audio_path): continue
            
            transcript = open(f"dataset/transcripts/{text_id}.txt", encoding="utf-8").read()
            res = analyze(audio_path, transcript, exclude_speaker=spk)
            
            pred_flaws = res.get("regions", [])
            
            for t in label_data["flaws"]:
                typ = t["type"]
                sev = t["severity"]
                key = f"{typ}_L{sev}"
                
                iou_pass, time_pass, best_iou = match_flaw(t, pred_flaws)
                
                recall_stats[key]["total"] += 1
                if iou_pass: recall_stats[key]["iou"] += 1
                if time_pass: recall_stats[key]["time"] += 1
                
                if not iou_pass and typ == "PACE_FAST" and sev == 4:
                    # Diagnostic
                    print(f"[DIAGNOSTIC] Missed PACE_FAST L4 in {fid}. Best IoU: {best_iou:.2f}", flush=True)
        except Exception as e:
            import traceback
            print(f"Error on flawed file {fid}: {e}\n{traceback.format_exc()}", flush=True)

    # Generate Report
    report = []
    report.append("## Phase 5 Evaluation Report")
    report.append("")
    report.append("### False Positives (Good Files)")
    total_fp = sum(fp_by_type.values())
    total_fp_min = (total_fp / good_duration_s * 60) if good_duration_s > 0 else 0
    report.append(f"**Total FP/min**: {total_fp_min:.2f}")
    for spk, fp in fp_by_speaker.items():
        dur = speaker_duration_s[spk]
        fpm = (fp / dur * 60) if dur > 0 else 0
        report.append(f"- {spk}: {fpm:.2f} FP/min ({fp} FPs)")
    
    report.append("")
    report.append("### Recall by Flaw Type and Severity")
    report.append("| Flaw | Severity | Recall (IoU>=0.5) | Recall (Time +-1.0s) |")
    report.append("|---|---|---|---|")
    
    for key in sorted(recall_stats.keys()):
        stats = recall_stats[key]
        n = stats["total"]
        if n == 0: continue
        iou_r = stats["iou"] / n
        time_r = stats["time"] / n
        flaw, sev = key.split("_L")
        report.append(f"| {flaw} | L{sev} | {iou_r*100:.1f}% ({stats['iou']}/{n}) | {time_r*100:.1f}% ({stats['time']}/{n}) |")
        
    md_report = "\n".join(report)
    print(md_report)
    
    os.makedirs("results", exist_ok=True)
    with open("results/eval_report.md", "w") as f:
        f.write(md_report)
        
    with open("results/eval_report.json", "w") as f:
        json.dump({
            "fp_per_min": total_fp_min,
            "fp_by_type": fp_by_type,
            "recall": recall_stats
        }, f, indent=2)

if __name__ == "__main__":
    main()
