import os
import sys
from pathlib import Path

# Add src to pythonpath for IDE linters
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import json
import csv
import numpy as np
from collections import defaultdict
from speechcoach.audio.io import load_audio
from speechcoach.features.frame import frame_features
from speechcoach.features.words import word_table, window_stats
from speechcoach.compare.baseline import build_baseline, signals, calibrate

def main():
    print("Starting calibration...")
    # Read metadata.csv
    ideals = defaultdict(list)
    with open('dataset/metadata.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['severity_level'] == 'null':
                ideals[row['text_id']].append(row)

    ideal_stats = defaultdict(dict)
    
    for text_id, records in ideals.items():
        print(f"Processing {text_id}...")
        for row in records:
            file_id = row['file_id']
            audio_path = row['audio_path']
            align_path = f"dataset/alignments/{file_id}.json"
            
            if not os.path.exists(align_path):
                print(f"Skipping {file_id}: No alignment found.")
                continue
                
            print(f"  Extracting features for {file_id}...")
            y = load_audio(audio_path)
            g = frame_features(y)
            
            with open(align_path, 'r') as f:
                align_data = json.load(f)
            
            words = align_data['words']
            w_table = word_table(words, g)
            w_stats = window_stats(g, words)
            
            # Merge
            merged = {k: v for k, v in w_stats.items()}
            merged['pause_before'] = np.array([w['pause_before'] for w in w_table])
            
            ideal_stats[text_id][file_id] = merged

    # Leave-one-out
    loo_signals = defaultdict(list)
    for text_id, items in ideal_stats.items():
        if len(items) < 2:
            print(f"Skipping leave-one-out for {text_id}: only {len(items)} ideals.")
            continue
            
        print(f"Running leave-one-out for {text_id} with {len(items)} ideals...")
        for file_id, stats in items.items():
            other_stats = [v for k, v in items.items() if k != file_id]
            B = build_baseline(other_stats)
            sig = signals(stats, B)
            
            n = min(len(stats["pause_before"]), len(B["pause_before"]))
            p_pause = stats["pause_before"][:n]
            b_pause = B["pause_before"][:n]
            pause_mask = (p_pause > 0.05) | (b_pause > 0.05)

            for s_name, s_vals in sig.items():
                if s_name == "pause":
                    s_vals = s_vals[pause_mask]
                loo_signals[s_name].extend(s_vals.tolist())

    loo_arrays: dict[str, np.ndarray] = {
        s_name: np.array(vals) for s_name, vals in loo_signals.items()
    }

    floors = {
        'pace': 0.05,
        'pause': 0.05,
        'pitch': 0.05,
        'energy': 1.0,
        'dynamics': 0.05,
        'clarity': 0.05
    }

    sigmas = calibrate(loo_arrays, floors)

    print("\nCalibration complete. Sigmas:")
    for k, v in sigmas.items():
        print(f"  {k}: {v:.4f}")
        
    # Calculate tau per signal from the LOO false-positive budget (1%)
    budget = 0.01
    taus = {}
    for sig, values in loo_arrays.items():
        v = values[np.isfinite(values)]
        if len(v) == 0:
            taus[sig] = 2.0
        else:
            z_vals = np.abs(v / sigmas[sig])
            tau = np.percentile(z_vals, 100 * (1 - budget))
            taus[sig] = max(float(tau), 2.0)
            
    print("\nTaus (1% FP budget):")
    for k, v in taus.items():
        print(f"  {k}: {v:.4f}")
        
    os.makedirs('configs', exist_ok=True)
    with open('configs/sigma.json', 'w') as f:
        json.dump(sigmas, f, indent=2)
    with open('configs/tau.json', 'w') as f:
        json.dump(taus, f, indent=2)
    print("Saved to configs/sigma.json and configs/tau.json")

if __name__ == "__main__":
    main()
