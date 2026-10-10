import os
import sys
import json
import csv
import pickle
import hashlib
import numpy as np
from pathlib import Path
from sklearn.linear_model import RidgeCV
from sklearn.isotonic import IsotonicRegression
from sklearn.preprocessing import StandardScaler
from scipy.stats import spearmanr
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from speechcoach.analyze import analyze
from speechcoach.compare.deviation import CHANNELS

def get_hash(obj):
    s = pickle.dumps(obj)
    return hashlib.sha256(s).hexdigest()[:8]

def extract_features():
    cache_path = Path("dataset/metadata/features_cache.json")
    if cache_path.exists():
        with open(cache_path, "r") as f:
            return json.load(f)

    # Need to run analyze on all files
    recordings_path = Path("dataset/metadata/recordings.csv")
    reader_rows = []
    with open(recordings_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            reader_rows.append(row)
            
    # Flaw severities
    flaw_path = Path("dataset/metadata/flaws.json")
    with open(flaw_path, "r", encoding="utf-8") as f:
        all_flaws = json.load(f)
        
    severity_map = {}
    for f in all_flaws:
        fid = f["file_id"]
        # Max severity if multiple
        severity_map[fid] = max(severity_map.get(fid, 0), f["severity"])
        
    features = []
    
    for row in reader_rows:
        fid = row["file_id"]
        spk = row["speaker_id"]
        text_id = row["text_id"]
        
        target = 0
        if row.get("quality") != "GOOD":
            target = severity_map.get(fid, 0)
            
        audio_path = f"dataset/raw/{row.get('quality', 'GOOD').lower()}/{spk}/{fid}.wav"
        if not os.path.exists(audio_path): continue
        
        transcript = open(f"dataset/transcripts/{text_id}.txt", encoding="utf-8").read()
        res = analyze(audio_path, transcript, exclude_speaker=spk)
        
        feats = res["soft_features"]
        
        # Flatten feats
        f_vec = []
        for name in CHANNELS:
            f_vec.append(feats.get(f"{name}_area", 0.0))
            f_vec.append(feats.get(f"{name}_p95", 0.0))
            
        features.append({
            "file_id": fid,
            "speaker": spk,
            "target": target,
            "features": f_vec
        })
        print(f"Extracted features for {fid}")
        
    with open(cache_path, "w") as f:
        json.dump(features, f)
        
    return features

def train_and_eval(features):
    speakers = sorted(list(set(f["speaker"] for f in features)))
    
    # We will do leave-one-speaker-out
    correlations = {}
    
    # Feature matrix
    X = np.array([f["features"] for f in features])
    y = np.array([f["target"] for f in features])
    spks = np.array([f["speaker"] for f in features])
    
    for holdout in speakers:
        train_idx = spks != holdout
        test_idx = spks == holdout
        
        X_train, y_train = X[train_idx], y[train_idx]
        X_test, y_test = X[test_idx], y[test_idx]
        
        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)
        
        ridge = RidgeCV(alphas=np.logspace(-3, 3, 10))
        ridge.fit(X_train_s, y_train)
        
        raw_pred_train = ridge.predict(X_train_s)
        raw_pred_test = ridge.predict(X_test_s)
        
        iso = IsotonicRegression(y_min=0, y_max=100, out_of_bounds='clip')
        iso.fit(raw_pred_train, y_train * 25) # Map severity 0-4 to 0-100 score roughly
        
        # We actually want severity 0 -> 100, severity 4 -> 0?
        # The user says "output mapped to 0-100 with isotonic regression"
        # Usually severity 0 means perfect (score 100).
        # Let's map target to score: score = 100 - severity * 25
        score_target_train = 100 - y_train * 25
        iso.fit(raw_pred_train, score_target_train)
        
        scores_test = iso.predict(raw_pred_test)
        
        # Spearman correlation between score and severity
        # Should be strongly negative, or we can just abs it
        corr, _ = spearmanr(scores_test, y_test)
        correlations[holdout] = abs(corr)
        print(f"Speaker {holdout} Spearman: {abs(corr):.3f}")
        
    # Finally, train on all data (or S01-S03) to produce the final model
    print("\nTraining final model on all data...")
    scaler = StandardScaler()
    X_s = scaler.fit_transform(X)
    
    ridge = RidgeCV(alphas=np.logspace(-3, 3, 10))
    ridge.fit(X_s, y)
    
    raw_pred = ridge.predict(X_s)
    score_target = 100 - y * 25
    iso = IsotonicRegression(y_min=0, y_max=100, out_of_bounds='clip')
    iso.fit(raw_pred, score_target)
    
    model_data = {
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_scale": scaler.scale_.tolist(),
        "ridge_coef": ridge.coef_.tolist(),
        "ridge_intercept": float(ridge.intercept_),
        "iso_X": iso.X_min_,
        "iso_y": iso.y_min_,
        "iso_f": iso
    }
    
    os.makedirs("src/speechcoach/models/weights", exist_ok=True)
    with open("src/speechcoach/models/weights/scoring_model.pkl", "wb") as f:
        pickle.dump(model_data, f)
        
    hash_val = get_hash(model_data)
    print(f"Saved model with hash {hash_val}")
    
if __name__ == "__main__":
    feats = extract_features()
    train_and_eval(feats)
