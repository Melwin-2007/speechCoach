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
            dev_sigma = float(np.mean(sig[s_idx:e_idx+1]))
            raw_dev = float(np.mean(dev[s_idx:e_idx+1]))
            
            evidence = {
                "flaw": name,
                "start": round(start_s, 2),
                "end": round(end_s, 2),
                "source": str(src_mode),
                "dev_sigma": round(dev_sigma, 2),
                "raw_dev": round(raw_dev, 2)
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
                
            flaw_dict = {
                "id": flaw_id,
                "type": name,
                "start": round(start_s, 2),
                "end": round(end_s, 2),
                "evidence": evidence
            }
            
            try:
                flaw_dict["explanation"] = explain(evidence)
            except Exception as e:
                flaw_dict["explanation"] = f"Detected {name}."
                
            regions.append(flaw_dict)
            flaw_id += 1
            
    regions.sort(key=lambda x: x["start"])
    
    # 5. Build response
    result = {
        "meta": {
            "mode": mode,
            "duration_s": round(duration_s, 4),
            "version": "2.0",
            "bounds_hash": B.get("hash", "unknown")
        },
        "words": words,
        "flaws": regions,
        "soft_features": soft_features,
        "scores": {} # Placeholder for Score model (Fix 6)
    }
    
    return result
