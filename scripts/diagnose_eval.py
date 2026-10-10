import os
import sys
import json
import csv
import numpy as np
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from speechcoach.analyze import analyze

def main():
    floors = {
        'pace': 0.05,
        'pause': 0.05,
        'pitch': 0.05,
        'energy': 1.0,
        'dynamics': 0.05,
        'clarity': 0.05
    }
    
    with open("configs/sigma.json", "r") as f:
        sigmas = json.load(f)
        
    print("Sigma vs Floor:")
    for sig, sigma in sigmas.items():
        print(f"  {sig}: {sigma:.4f} (floor {floors.get(sig, 0):.4f})")
        
    meta_path = Path("dataset/metadata/recordings.csv")
    files = []
    with open(meta_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["split"] == "dev":
                files.append(row)
                
    labels_dir = Path("dataset/metadata/flaws.csv")
    for row in files:
        variant = row["variant"]
        file_id = row["file_id"]
        text_id = row["text_id"]
        audio_path = row["audio_path"]
        speaker = row["speaker"]
        level = row.get("severity_level", "0")
        
        if variant == "ideal":
            try:
                transcript_path = Path(f"dataset/texts/{text_id}.txt")
                with open(transcript_path, "r", encoding="utf-8") as f: transcript = f.read()
                res = analyze(audio_path, transcript, baseline_id=text_id, mode="reference", exclude_speaker=speaker)
            except Exception as e:
                continue
                
            words = res.get("words", [])
            print(f"\nShare of words with |z| > 2 for ideal {file_id}:")
            for sig in sigmas.keys():
                z_vals = [w["z"].get(sig, 0.0) for w in words]
                gt2 = sum(1 for z in z_vals if abs(z) > 2.0)
                tot = len(words)
                share = gt2 / tot if tot > 0 else 0
                print(f"  {sig}: {share:.2%} ({gt2}/{tot})")
                
        if (file_id == "T1__synth-orig-indianpep__VOLUME_DROP_L5" or file_id == "T1__synth-orig-indianpep__PACE_FAST_L5"):
            try:
                transcript_path = Path(f"dataset/texts/{text_id}.txt")
                with open(transcript_path, "r", encoding="utf-8") as f: transcript = f.read()
                res = analyze(audio_path, transcript, baseline_id=text_id, mode="reference", exclude_speaker=speaker)
            except Exception as e:
                continue
                
            label_path = labels_dir / f"{file_id}.json"
            if label_path.exists():
                with open(label_path, "r") as f:
                    label_data = json.load(f)
                true_flaw = label_data["flaws"][0] if label_data.get("flaws") else None
                if not true_flaw: continue
                
                t_start, t_end = true_flaw["start_s"], true_flaw["end_s"]
                words = res.get("words", [])
                
                z_in = defaultdict(list)
                z_out = defaultdict(list)
                
                for w in words:
                    w_s, w_e = w["start"], w["end"]
                    mid = (w_s + w_e) / 2
                    is_in = t_start <= mid <= t_end
                    for sig in sigmas.keys():
                        z_val = w["z"].get(sig, 0.0)
                        if is_in: z_in[sig].append(z_val)
                        else: z_out[sig].append(z_val)
                        
                print(f"\nZ percentiles for {file_id} (True: {t_start:.1f}-{t_end:.1f}):")
                for sig in sigmas.keys():
                    in_perc = np.percentile(z_in[sig], [0, 25, 50, 75, 100]) if z_in[sig] else []
                    out_perc = np.percentile(z_out[sig], [0, 25, 50, 75, 100]) if z_out[sig] else []
                    print(f"  {sig} IN : {in_perc}")
                    print(f"  {sig} OUT: {out_perc}")

if __name__ == "__main__":
    main()
