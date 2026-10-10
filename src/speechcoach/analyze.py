import os
import json
import yaml
import numpy as np
from pathlib import Path

from speechcoach.audio.io import load_audio
from speechcoach.align.transcript import parse_transcript
from speechcoach.align.aligner import align_words
from speechcoach.features.frame import frame_features
from speechcoach.features.words import word_table
from speechcoach.features.phrases import group_phrases, speaker_normalization, phrase_features, interpolate_to_grid
from speechcoach.compare.deviation import load_bounds, CHANNELS, PARAMS, channel_signal
from speechcoach.compare.regions import detect_regions
from speechcoach.explain.templates import explain

def analyze(audio_path: str | Path, transcript: str, baseline_id: str | None = None, mode: str = "auto", exclude_speaker: str | None = None) -> dict:
    audio_path = Path(audio_path)
    bounds_path = f"configs/population_bounds_loo_{exclude_speaker}.json" if exclude_speaker else "configs/population_bounds.json"
    B = load_bounds(bounds_path)
    
    # 1. Load Audio & Align
    y = load_audio(audio_path, sr=16000, target_lufs=-23.0)
    duration_s = float(len(y) / 16000.0)
    raw_words = parse_transcript(transcript)
    
    # Check cache for alignments
    import json
    audio_path_str = str(audio_path).replace("\\", "/")
    words = None
    if "dataset/raw" in audio_path_str:
        cache_path = audio_path_str.replace("dataset/raw", "dataset/alignments")
        # remove speaker dir
        parts = cache_path.split("/")
        # dataset/alignments/type/speaker/file.wav -> dataset/alignments/type/file.json
        if len(parts) >= 5:
            cache_path = "/".join(parts[:-2] + [parts[-1].replace(".wav", ".json")])
        if Path(cache_path).exists():
            words = json.loads(Path(cache_path).read_text())["words"]
            
    if words is None:
        words = align_words(y, raw_words)
    
    # 2. Extract Phrase Features
    g = frame_features(y)
    w_table = word_table(words, g)
    phrases = group_phrases(w_table)
    norms = speaker_normalization(g, phrases)
    p_feats = phrase_features(phrases, g, norms)
    grid = interpolate_to_grid(p_feats, duration_s)
    
    # 3. Detect Regions and Extract Soft Features
    regions = []
    flaw_id = 1
    soft_features = {}
    speech_frames = np.sum(grid["phrase_id"] >= 0)
    speech_seconds = max(speech_frames * 0.1, 0.1)
    
    for name in CHANNELS:
        sig, dev, src = channel_signal(name, grid, B)
        p = PARAMS.get(name, PARAMS["default"])
        
        # Soft features
        if "PAUSE" in name:
            valid_frames = (grid["pause_type"] != "none")
            valid_sig = sig[valid_frames]
            denom = max(np.sum(valid_frames) * 0.1, 0.1)
        else:
            valid_frames = (grid["phrase_id"] >= 0)
            valid_sig = sig[valid_frames]
            denom = speech_seconds
            
        if len(valid_sig) > 0:
            area = float(np.sum(np.clip(valid_sig - 1.0, 0, None)) * 0.1 / denom)
            p95 = float(np.percentile(valid_sig, 95))
        else:
            area, p95 = 0.0, 0.0
            
        soft_features[f"{name}_area"] = area
        soft_features[f"{name}_p95"] = p95
        
        spans = detect_regions(sig, grid["t"], **p)
        
        for s_idx, e_idx in spans:
            start_s = float(grid["t"][s_idx])
            end_s = float(grid["t"][e_idx])
            
            src_mode = src[s_idx]
            dev_peak = float(np.max(dev[s_idx:e_idx+1]))
            dev_mean = float(np.mean(dev[s_idx:e_idx+1]))
            
            evidence = {
                "flaw": name,
                "start": round(start_s, 2),
                "end": round(end_s, 2),
                "source": str(src_mode),
                "dev_peak": round(dev_peak, 2),
                "dev_mean": round(dev_mean, 2)
            }
            
            # Additional context for specific flaws
            if "PACE" in name:
                evidence["value"] = round(float(np.mean(grid["sps"][s_idx:e_idx+1])), 1)
                evidence["baseline"] = round(float(norms["median_pace"]), 1)
                evidence["unit"] = "syll/s"
                evidence["pause_mean"] = round(float(np.mean(grid["pause_s"][s_idx:e_idx+1])), 2)
                evidence["pause_baseline"] = round(float(B.get("pause_s", {}).get("mid", {}).get("median", 0.3)), 2)
                
            elif "PITCH" in name:
                evidence["value"] = round(float(np.mean(grid["st_std"][s_idx:e_idx+1])), 1)
                evidence["baseline"] = round(float(norms["median_f0"]), 1)
                evidence["unit"] = "semitones std"
                
            elif "ENERGY" in name:
                evidence["value"] = round(float(np.mean(grid["db_rel"][s_idx:e_idx+1])), 1)
                evidence["baseline"] = 0.0
                evidence["unit"] = "dB below median"
                
            elif "PAUSE" in name:
                evidence["value"] = round(float(np.mean(grid["pause_s"][s_idx:e_idx+1])), 2)
                evidence["baseline"] = round(float(B.get("pause_s", {}).get("comma", {}).get("median", 0.3)), 2)
                evidence["unit"] = "s"
                
            tier = "flagged" if dev_peak >= p.get("enter", 2.0) else "minor"
            
            flaw_dict = {
                "id": flaw_id,
                "type": name,
                "flaw": name,
                "tier": tier,
                "start": round(start_s, 2),
                "end": round(end_s, 2),
                "source": str(src_mode),
                "value": evidence.get("value", 0.0),
                "baseline": evidence.get("baseline", 0.0),
                "band": "unknown",
                "dev_peak": round(dev_peak, 2),
                "dev_mean": round(dev_mean, 2),
                "text_span": "TODO",
                "explanation": explain(evidence)
            }
            
            try:
                flaw_dict["explanation"] = explain(evidence)
            except Exception as e:
                flaw_dict["explanation"] = f"Detected {name}."
                
            regions.append(flaw_dict)
            flaw_id += 1
            
    regions.sort(key=lambda x: x["start"])
    
    # 5. Build response
    
    # Extract unassessed regions (gaps and unreliable areas)
    not_assessed = []
    unreliable = ~grid["reliable"]
    unreliable_spans = detect_regions(np.where(unreliable, 3.0, 0.0), grid["t"], enter=2.0, exit=1.0, min_dur=0.5, merge_gap=0.0, smooth=1)
    for s_idx, e_idx in unreliable_spans:
        not_assessed.append({"start": round(float(grid["t"][s_idx]), 2), "end": round(float(grid["t"][e_idx]), 2)})
        
    score = 0.0
    subscores = {}
    model_hash = "unknown"
    
    model_path = Path(__file__).resolve().parent / "models" / "weights" / "scoring_model.pkl"
    if model_path.exists():
        try:
            import pickle
            with open(model_path, "rb") as f:
                model_data = pickle.load(f)
            model_hash = model_data.get("hash", "unknown")
            X = np.array([[soft_features.get(f, 0.0) for f in model_data["feature_names"]]])
            X_scaled = model_data["scaler"].transform(X)
            raw_pred = model_data["ridge"].predict(X_scaled)
            score_pred = model_data["isotonic"].predict(raw_pred)[0]
            score = round(float(max(0.0, min(100.0, score_pred))), 1)
        except Exception as e:
            print(f"Failed to score: {e}")
        
    result = {
        "bounds_hash": B.get("hash", "unknown"),
        "model_hash": model_hash,
        "score": score,
        "subscores": subscores,
        "grid": {
            "t": grid["t"].tolist(),
            "sps": grid["sps"].tolist(),
            "st_std": grid["st_std"].tolist(),
            "db_rel": grid["db_rel"].tolist(),
            "pause_s": grid["pause_s"].tolist(),
            "f0_contour": g["f0"].tolist(),
            "energy_contour": g["db_rel"].tolist(),
            "baseline_pace": np.full_like(grid["t"], norms.get("median_pace", 0.0)).tolist(),
            "baseline_pitch": np.full_like(grid["t"], norms.get("median_f0", 0.0)).tolist()
        },
        "regions": regions,
        "not_assessed": not_assessed,
        "words": words, # Kept for UI convenience
        "soft_features": soft_features, # Kept for scoring model
        "meta": {
            "duration_s": round(duration_s, 4),
            "version": "2.0"
        }
    }
    
    return result
