import os
import sys
import json
import csv
import pickle
import hashlib
import numpy as np
from pathlib import Path
from typing import Any
from sklearn.linear_model import RidgeCV
from sklearn.isotonic import IsotonicRegression
from sklearn.preprocessing import StandardScaler
from scipy.stats import spearmanr  # type: ignore
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
    seen_flaws = set()
    for f in all_flaws:
        fid = f["file_id"]
        # Max severity if multiple
        severity_map[fid] = max(severity_map.get(fid, 0), f["severity"])
        if fid not in seen_flaws:
            seen_flaws.add(fid)
            reader_rows.append({
                "file_id": fid,
                "speaker_id": f["speaker_id"],
                "text_id": f["text_id"],
                "quality": "FLAWED"
            })
        
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
    X: Any = np.array([f["features"] for f in features])
    y: Any = np.array([f["target"] for f in features])
    spks = np.array([f["speaker"] for f in features])
    alphas: Any = np.logspace(-3, 3, 10)
    
    for holdout in speakers:
        train_idx = spks != holdout
        test_idx = spks == holdout
        
        X_train, y_train = X[train_idx], y[train_idx]
        X_test, y_test = X[test_idx], y[test_idx]
        
        # Balanced class weights for holdout training
        n_good_tr = np.sum(y_train == 0)
        n_flawed_tr = np.sum(y_train > 0)
        w_tr: Any = np.where(y_train == 0, n_flawed_tr / max(n_good_tr, 1), 1.0)
        
        scaler = StandardScaler()
        X_train_s: Any = scaler.fit_transform(X_train)
        X_test_s: Any = scaler.transform(X_test)
        
        ridge = RidgeCV(alphas=alphas)
        ridge.fit(X_train_s, y_train, sample_weight=w_tr)
        
        raw_pred_train: Any = ridge.predict(X_train_s)
        raw_pred_test: Any = ridge.predict(X_test_s)
        
        score_target_train: Any = 100 - y_train * 25
        iso = IsotonicRegression(increasing=False, y_min=0, y_max=100, out_of_bounds='clip')
        iso.fit(raw_pred_train, score_target_train, sample_weight=w_tr)
        
        scores_test = iso.predict(raw_pred_test)
        
        # Spearman correlation between score and severity
        # Should be strongly negative, or we can just abs it
        res: Any = spearmanr(scores_test, y_test)
        corr = float(getattr(res, "statistic", res[0]))
        correlations[holdout] = abs(corr)
        print(f"Speaker {holdout} Spearman: {abs(corr):.3f}")
        
    # Finally, train on all data with balanced sample weights
    print("\nTraining final model on all data with class balancing...")
    n_good_all = np.sum(y == 0)
    n_flawed_all = np.sum(y > 0)
    w_all: Any = np.where(y == 0, n_flawed_all / max(n_good_all, 1), 1.0)
    
    scaler = StandardScaler()
    X_s: Any = scaler.fit_transform(X)
    
    ridge = RidgeCV(alphas=alphas)
    ridge.fit(X_s, y, sample_weight=w_all)
    
    raw_pred: Any = ridge.predict(X_s)
    score_target: Any = 100 - y * 25
    iso = IsotonicRegression(increasing=False, y_min=0, y_max=100, out_of_bounds='clip')
    iso.fit(raw_pred, score_target, sample_weight=w_all)
    
    feature_names = []
    for name in CHANNELS:
        feature_names.append(f"{name}_area")
        feature_names.append(f"{name}_p95")

    model_data: dict[str, Any] = {
        "feature_names": feature_names,
        "scaler": scaler,
        "ridge": ridge,
        "isotonic": iso,
    }
    hash_val = get_hash(model_data)
    model_data["hash"] = hash_val
    
    os.makedirs("src/speechcoach/models/weights", exist_ok=True)
    with open("src/speechcoach/models/weights/scoring_model.pkl", "wb") as f:
        pickle.dump(model_data, f)
        
    print(f"Saved model with hash {hash_val}")
    
if __name__ == "__main__":
    feats = extract_features()
    train_and_eval(feats)
