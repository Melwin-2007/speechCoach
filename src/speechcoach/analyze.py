import os
import json
import csv
import yaml
import numpy as np
from functools import lru_cache
from pathlib import Path

from speechcoach.audio.io import load_audio
from speechcoach.align.transcript import parse_transcript
from speechcoach.align.aligner import align_words
from speechcoach.features.frame import frame_features
from speechcoach.features.words import word_table, window_stats
from speechcoach.compare.baseline import build_baseline, signals
from speechcoach.compare.regions import find_regions
from speechcoach.explain.templates import explain
from speechcoach.scoring.rubric import score

@lru_cache(maxsize=16)
def load_baseline(baseline_id: str, exclude_speaker: str | None = None) -> dict:
    """Loads and computes the baseline statistics for a given text ID."""
    ideals = []
    meta_path = Path("dataset/metadata/recordings.csv")
    if not meta_path.exists():
        return {}
        
    with open(meta_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['text_id'] == baseline_id and row.get('quality', 'GOOD') == 'GOOD':
                if exclude_speaker and row['speaker_id'] == exclude_speaker:
                    continue
                audio_path = f"dataset/raw/good/{row['speaker_id']}/{row['file_id']}.wav"
                align_path = f"dataset/alignments/good/{row['file_id']}.json"
                
                if not os.path.exists(audio_path) or not os.path.exists(align_path):
                    continue
                    
                y = load_audio(audio_path)
                g = frame_features(y)
                with open(align_path, 'r', encoding='utf-8') as af:
                    align_data = json.load(af)
                    
                words = align_data['words']
                w_table = word_table(words, g)
                w_stats = window_stats(g, words)
                
                merged = {k: v for k, v in w_stats.items()}
                merged['pause_before'] = np.array([w['pause_before'] for w in w_table])
                ideals.append(merged)
                
    if not ideals:
        return {}
        
    return build_baseline(ideals)

def analyze(audio_path: str | Path, transcript: str, baseline_id: str | None = None, mode: str = "auto", exclude_speaker: str | None = None) -> dict:
    """
    Main analysis pipeline.
    """
    audio_path = Path(audio_path)
    
    # 1. Load config and sigmas
    with open("configs/thresholds.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    
    sigma_path = Path("configs/sigma.json")
    if sigma_path.exists():
        with open(sigma_path, "r", encoding="utf-8") as f:
            sigmas = json.load(f)
    else:
        sigmas = {k: 1.0 for k in ["pace", "pause", "pitch", "energy", "dynamics", "clarity"]}
        
    # 2. Extract features
    y = load_audio(audio_path, sr=cfg.get("sr", 16000), target_lufs=cfg.get("target_lufs", -23.0))
    duration_s = float(len(y) / cfg.get("sr", 16000))
    
    raw_words = parse_transcript(transcript)
    words = align_words(y, raw_words)
    
    g = frame_features(y)
    w_table = word_table(words, g)
    w_stats = window_stats(g, words)
    
    P = {k: v for k, v in w_stats.items()}
    P['pause_before'] = np.array([w['pause_before'] for w in w_table])
    
    # 3. Get Baseline and Signals
    warnings_list = []
    
    # Default to reference mode if baseline is found
    actual_mode = "reference" if baseline_id else "prior"
    if mode != "auto":
        actual_mode = mode
        
    if actual_mode == "reference" and baseline_id:
        B = load_baseline(baseline_id, exclude_speaker=exclude_speaker)
        if not B:
            warnings_list.append(f"No ideals found for baseline {baseline_id}, falling back to empty baseline.")
            B = {k: np.zeros_like(v) for k, v in P.items()}
            actual_mode = "prior"
    else:
        # Mode B placeholder
        B = {k: np.zeros_like(v) for k, v in P.items()}
        
    raw_signals = signals(P, B)
    z_scores = {k: raw_signals[k] / sigmas.get(k, 1.0) for k in raw_signals}
    
    if "pause" in z_scores:
        mask = np.abs(raw_signals["pause"]) < cfg.get("min_pause_diff_s", 0.15)
        z_scores["pause"][mask] = 0.0
        
    # Fill word-level z-scores
    for i, w in enumerate(words):
        w["z"] = {
            "pace": float(z_scores.get("pace", np.zeros_like(P['win_dur']))[i]) if i < len(z_scores.get("pace", [])) else 0.0,
            "pause": float(z_scores.get("pause", np.zeros_like(P['win_dur']))[i]) if i < len(z_scores.get("pause", [])) else 0.0,
            "pitch": float(z_scores.get("pitch", np.zeros_like(P['win_dur']))[i]) if i < len(z_scores.get("pitch", [])) else 0.0,
            "energy": float(z_scores.get("energy", np.zeros_like(P['win_dur']))[i]) if i < len(z_scores.get("energy", [])) else 0.0,
            "clarity": float(z_scores.get("clarity", np.zeros_like(P['win_dur']))[i]) if i < len(z_scores.get("clarity", [])) else 0.0
        }
        
    # 4. Find Flaw Regions
    flaws = []
    flaw_id = 1
    
    try:
        with open("configs/tau.json", "r") as f:
            taus = json.load(f)
    except Exception:
        taus = {}
        
    def add_regions(signal_name: str, sign: int, flaw_type_punct: str, flaw_type_nopunct: str | None = None):
        nonlocal flaw_id
        if signal_name not in z_scores:
            return
        z_arr = z_scores[signal_name]
        event_mode = (signal_name == "pause")
        
        cfg_sig = cfg.copy()
        if signal_name in taus:
            cfg_sig["tau_flag"] = taus[signal_name]
            cfg_sig["tau_trim"] = max(1.0, taus[signal_name] * 0.75)
            
        # Wire NaN z-scores to extreme values so they fire
        if signal_name == "energy" and sign == -1:
            z_arr = np.nan_to_num(z_arr, nan=-10.0)
        elif signal_name == "dynamics" and sign == -1:
            z_arr = np.nan_to_num(z_arr, nan=-10.0)
        elif signal_name == "clarity" and sign == -1:
            z_arr = np.nan_to_num(z_arr, nan=-10.0)
        elif signal_name == "pitch" and sign == 1:
            z_arr = np.nan_to_num(z_arr, nan=10.0)
            
        regions = find_regions(z_arr, words, sign, cfg_sig, event_mode=event_mode)
        
        for r in regions:
            word_idx = r["first_word"]
            has_punct = bool(words[word_idx].get("punct", ""))
            
            f_type = flaw_type_punct
            if flaw_type_nopunct and not has_punct:
                f_type = flaw_type_nopunct
                
            # Calculate evidence
            start_idx = r["first_word"]
            end_idx = r["last_word"]
            p_map = {
                "pace": "win_dur",
                "pause": "pause_before",
                "pitch": "f0_std",
                "energy": "db_mean",
                "dynamics": "db_std",
                "clarity": "flux"
            }
            p_key = p_map.get(signal_name, signal_name)
            obs_val = float(np.mean(P[p_key][start_idx:end_idx+1]))
            base_val = float(np.mean(B[p_key][start_idx:end_idx+1]))
            
            unit_map = {
                "pace": " log-ratio",
                "pause": " s",
                "pitch": " log-ratio",
                "energy": " dB",
                "dynamics": " log-ratio",
                "clarity": " log-ratio"
            }
            unit_str = unit_map.get(signal_name, "")
            
            evidence = {
                "participant": obs_val,
                "baseline": base_val,
                "z": float(r["z_mean"]),
                "unit": unit_str
            }
            
            flaw_dict = {
                "id": flaw_id,
                "type": f_type,
                "start": float(r["start"]),
                "end": float(r["end"]),
                "first_word": r["first_word"],
                "last_word": r["last_word"],
                "severity": r["severity"],
                "band": r["band"],
                "evidence": evidence
            }
            
            flaw_dict["explanation"] = explain(flaw_dict, evidence)
            flaws.append(flaw_dict)
            flaw_id += 1

    add_regions("pace", -1, "PACE_FAST")
    add_regions("pace", 1, "PACE_SLOW")
    add_regions("pause", -1, "PAUSE_MISSING")
    add_regions("pause", 1, "PAUSE_EXCESS", "PAUSE_MISPLACED")
    add_regions("pitch", -1, "MONOTONE")
    add_regions("pitch", 1, "PITCH_ERRATIC")
    add_regions("energy", -1, "VOLUME_DROP")
    add_regions("dynamics", -1, "FLAT_ENERGY")
    add_regions("clarity", -1, "CLARITY")
    
    # Sort flaws by start time
    flaws.sort(key=lambda x: x["start"])
    
    # 5. Build series (placeholder downsampling to 20Hz for dashboard)
    t_grid = np.arange(0, duration_s, 0.05)
    
    series = {
        "t": [round(float(x), 3) for x in t_grid],
        "participant": {
            "pitch_st": [0.0] * len(t_grid),
            "energy_db": [0.0] * len(t_grid),
            "rate_sps": [0.0] * len(t_grid)
        },
        "baseline": {
            "pitch_st": [0.0] * len(t_grid),
            "pitch_lo": [0.0] * len(t_grid),
            "pitch_hi": [0.0] * len(t_grid),
            "energy_db": [0.0] * len(t_grid),
            "rate_sps": [0.0] * len(t_grid)
        }
    }

    # 6. Build response
    result = {
        "meta": {
            "mode": actual_mode,
            "baseline_id": baseline_id,
            "duration_s": round(duration_s, 4),
            "version": "1.0",
            "warnings": warnings_list
        },
        "words": words,
        "series": series,
        "flaws": flaws,
        "scores": score(z_scores, words, cfg)
    }
    
    return result
