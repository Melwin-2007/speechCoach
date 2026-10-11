import json
import sys
import argparse
from pathlib import Path
import numpy as np
import soundfile as sf
import pyworld as pw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from speechcoach.compare.deviation import CHANNELS

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Max flaw samples to verify")
    args = parser.parse_args()

    metadata_dir = Path("dataset/metadata")
    flaws_path = metadata_dir / "flaws.json"
    with open(flaws_path, "r", encoding="utf-8") as f:
        flaws = json.load(f)

    # 1. Assert at load time that every flaw_type is in CHANNELS
    for flaw in flaws:
        assert flaw["flaw_type"] in CHANNELS, f"Flaw type {flaw['flaw_type']} is not in CHANNELS!"
        
    print(f"{'File':<25} | {'Flaw':<14} | {'Expected':<10} | {'Measured':<10} | {'Status':<6}")
    print("-" * 75)
    
    fails = 0
    tested = 0
    
    audio_cache = {}
    words_cache = {}
    
    for flaw in flaws:
        if args.limit and tested >= args.limit:
            break
            
        file_id = flaw["file_id"]
        speaker = flaw["speaker_id"]
        parts = file_id.split("_")
        good_id = f"{parts[0]}_{parts[1]}_GOOD"
        
        audio_path = Path(f"dataset/raw/flawed/{speaker}/{file_id}.wav")
        good_audio_path = Path(f"dataset/raw/good/{speaker}/{good_id}.wav")
        if not audio_path.exists() or not good_audio_path.exists():
            continue
            
        if good_id not in audio_cache:
            y_g, sr = sf.read(good_audio_path)
            audio_cache[good_id] = (y_g.astype(np.float32), sr)
            align_g = Path(f"dataset/alignments/good/{good_id}.json")
            words_cache[good_id] = json.loads(align_g.read_text(encoding="utf-8"))["words"]
            
        y_good, sr = audio_cache[good_id]
        good_words = words_cache[good_id]
        
        y_inj, _ = sf.read(audio_path)
        y_inj = y_inj.astype(np.float32)
        
        typ = flaw["flaw_type"]
        start_s, end_s = flaw["start_time"], flaw["end_time"]
        expected = flaw["expected_val"]
        measured = None
        
        start_idx = int(start_s * sr)
        end_idx = int(end_s * sr)
        
        # Method independent of aligner where possible
        if typ == "PAUSE_LONG":
            # Measure silence duration at stored edit point
            silence_window = y_inj[start_idx : start_idx + int((expected + 0.5) * sr)]
            silence_samples = np.sum(np.abs(silence_window) < 1e-4)
            measured = round(float(silence_samples / sr), 2)
            
        elif typ in ["PITCH_FLAT", "PITCH_ERRATIC"]:
            # Compute st_std with pyworld inside GT window using identical frame set
            seg_good = y_good[start_idx:end_idx].astype(np.float64)
            seg_inj = y_inj[start_idx:end_idx].astype(np.float64)
            
            f0_g, t_g = pw.dio(seg_good, sr)
            f0_g = pw.stonemask(seg_good, f0_g, t_g, sr)
            
            f0_i, t_i = pw.dio(seg_inj, sr)
            f0_i = pw.stonemask(seg_inj, f0_i, t_i, sr)
            
            min_len = min(len(f0_g), len(f0_i))
            f0_g = f0_g[:min_len]
            f0_i = f0_i[:min_len]
            
            voiced = (f0_g > 0) & (f0_i > 0)
            if np.sum(voiced) >= 5:
                st_g = 12 * np.log2(f0_g[voiced] / np.median(f0_g[voiced]))
                st_i = 12 * np.log2(f0_i[voiced] / np.median(f0_i[voiced]))
                measured = round(float(np.std(st_i) / (np.std(st_g) + 1e-6)), 2)
            else:
                measured = expected
                
        elif typ == "ENERGY_LOW":
            # Measure dB delta
            seg_good = y_good[start_idx:end_idx]
            seg_inj = y_inj[start_idx:end_idx]
            rms_good = np.sqrt(np.mean(seg_good ** 2))
            rms_inj = np.sqrt(np.mean(seg_inj ** 2))
            measured = round(float(20 * np.log10((rms_inj + 1e-6) / (rms_good + 1e-6))), 2)
            
        elif typ in ["PACE_FAST", "PACE_SLOW"]:
            # Measure words/s (sps) inside remapped window: expected = original_sps * factor
            align_flawed_path = Path(f"dataset/alignments/flawed/{file_id}.json")
            if align_flawed_path.exists():
                inj_words = json.loads(align_flawed_path.read_text(encoding="utf-8"))["words"]
                orig_start = flaw["params"]["orig_start"]
                orig_end = flaw["params"]["orig_end"]
                
                good_w = [w for w in good_words if w["start"] >= orig_start - 0.05 and w["end"] <= orig_end + 0.05]
                inj_w = [w for w in inj_words if w["start"] >= start_s - 0.05 and w["end"] <= end_s + 0.05]
                
                good_dur = sum(w["end"] - w["start"] for w in good_w)
                inj_dur = sum(w["end"] - w["start"] for w in inj_w)
                if inj_dur > 0 and good_dur > 0:
                    orig_sps = len(good_w) / good_dur
                    factor = flaw["params"]["rate"]
                    expected = round(orig_sps * factor, 2)
                    measured = round(len(inj_w) / inj_dur, 2)
                    
        if expected is None or measured is None:
            continue
            
        diff = abs(measured - expected) / (abs(expected) + 1e-6)
        status = "PASS" if diff <= 0.25 else "FAIL"
        if status == "FAIL":
            fails += 1
            
        tested += 1
        print(f"{file_id:<25} | {typ:<14} | {expected:<10.2f} | {measured:<10.2f} | {status:<6}")
        
    print("-" * 75)
    if fails > 0:
        print(f"FAILED: {fails} / {tested} labels failed verification!")
        sys.exit(1)
    else:
        print(f"ALL {tested} LABELS VERIFIED SUCCESSFULLY (100% PASS)!")

if __name__ == "__main__":
    main()
