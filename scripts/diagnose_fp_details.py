import sys
import csv
from pathlib import Path
from collections import defaultdict
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from speechcoach.audio.io import load_audio
from speechcoach.align.transcript import parse_transcript
from speechcoach.align.aligner import align_words
from speechcoach.features.frame import frame_features
from speechcoach.features.words import word_table
from speechcoach.features.phrases import group_phrases, speaker_normalization, phrase_features, interpolate_to_grid
from speechcoach.compare.deviation import load_bounds, CHANNELS, PARAMS, channel_signal
from speechcoach.compare.regions import detect_regions

def main():
    recordings_path = Path("dataset/metadata/recordings.csv")
    with open(recordings_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        
    good_files = [r for r in reader if r.get("quality") == "GOOD" and r["speaker_id"] in ["S01", "S02", "S03"]]
    
    samples_found = 0
    print(f"{'File':<14} | {'Channel':<12} | {'Time':<10} | {'Dur(s)':<6} | {'Syll':<4} | {'Voiced%':<7} | {'Reliable':<8} | {'Src':<6}")
    print("-" * 85)
    
    for r in good_files:
        fid = r["file_id"]
        spk = r["speaker_id"]
        text_id = r["text_id"]
        audio_path = f"dataset/raw/good/{spk}/{fid}.wav"
        transcript = open(f"dataset/transcripts/{text_id}.txt", encoding="utf-8").read()
        
        y = load_audio(audio_path, sr=16000, target_lufs=-23.0)
        dur_s = float(len(y) / 16000.0)
        cache_path = f"dataset/alignments/good/{fid}.json"
        import json
        words = json.loads(open(cache_path).read())["words"]
        
        g = frame_features(y)
        w_table = word_table(words, g)
        phrases = group_phrases(w_table)
        norms = speaker_normalization(g, phrases)
        p_feats = phrase_features(phrases, g, norms)
        grid = interpolate_to_grid(p_feats, dur_s)
        
        bounds_path = f"configs/population_bounds_loo_{spk}.json"
        B = load_bounds(bounds_path)
        
        for name in CHANNELS:
            sig, dev, src = channel_signal(name, grid, B)
            p = PARAMS.get(name, PARAMS["default"])
            spans = detect_regions(sig, grid["t"], **p)
            for s_idx, e_idx in spans:
                start_s = float(grid["t"][s_idx])
                end_s = float(grid["t"][e_idx])
                reg_dur = end_s - start_s
                
                # Find matching phrases
                p_ids = np.unique(grid["phrase_id"][s_idx:e_idx+1])
                p_ids = [pid for pid in p_ids if pid >= 0]
                
                if p_ids:
                    matching_p = [p_feats[pid] for pid in p_ids if pid < len(p_feats)]
                    p_dur = sum(p["end"] - p["start"] for p in matching_p)
                    p_syll = sum(p["sps"] * (p["end"] - p["start"]) for p in matching_p)
                    p_rel = all(p["reliable"] for p in matching_p)
                    # voiced fraction
                    mask_f0 = (g["t"] >= start_s) & (g["t"] <= end_s) & (g["f0"] > 0)
                    total_f = (g["t"] >= start_s) & (g["t"] <= end_s)
                    voiced_frac = np.sum(mask_f0) / max(np.sum(total_f), 1) * 100
                else:
                    p_dur = reg_dur
                    p_syll = 0
                    p_rel = False
                    voiced_frac = 0.0
                    
                src_mode = src[s_idx]
                print(f"{fid:<14} | {name:<12} | {start_s:.1f}-{end_s:.1f}s | {p_dur:<6.2f} | {int(round(p_syll)):<4} | {voiced_frac:<7.1f} | {str(p_rel):<8} | {src_mode:<6}")
                samples_found += 1
                if samples_found >= 10:
                    return

if __name__ == "__main__":
    main()
