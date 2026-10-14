import sys
import csv
import json
from pathlib import Path
from typing import Any
import numpy as np
import librosa
import soundfile as sf
import pyworld as _pw
pw: Any = _pw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from speechcoach.compare.deviation import CHANNELS

def apply_pace_fast(y, sr, words, start_w, end_w, severity):
    orig_start_s = float(words[start_w]["start"])
    orig_end_s = float(words[end_w]["end"])
    start_idx = int(orig_start_s * sr)
    end_idx = int(orig_end_s * sr)
    segment = y[start_idx:end_idx]
    
    rate = {2: 1.20, 3: 1.35, 4: 1.55}.get(severity, 1.35)
    stretched = librosa.effects.time_stretch(segment, rate=rate)
    y_new = np.concatenate([y[:start_idx], stretched, y[end_idx:]])
    new_end_s = orig_start_s + (len(stretched) / sr)
    
    # Remap words
    remapped_words = []
    shift = (new_end_s - orig_start_s) - (orig_end_s - orig_start_s)
    for idx, w in enumerate(words):
        w_copy = dict(w)
        if idx < start_w:
            pass
        elif idx <= end_w:
            w_copy["start"] = round(orig_start_s + (float(w["start"]) - orig_start_s) / rate, 3)
            w_copy["end"] = round(orig_start_s + (float(w["end"]) - orig_start_s) / rate, 3)
        else:
            w_copy["start"] = round(float(w["start"]) + shift, 3)
            w_copy["end"] = round(float(w["end"]) + shift, 3)
        remapped_words.append(w_copy)
        
    return y_new, orig_start_s, new_end_s, rate, {"rate": rate, "orig_start": orig_start_s, "orig_end": orig_end_s}, remapped_words

def apply_pace_slow(y, sr, words, start_w, end_w, severity):
    orig_start_s = float(words[start_w]["start"])
    orig_end_s = float(words[end_w]["end"])
    start_idx = int(orig_start_s * sr)
    end_idx = int(orig_end_s * sr)
    segment = y[start_idx:end_idx]
    
    rate = {2: 0.80, 3: 0.65, 4: 0.50}.get(severity, 0.65)
    stretched = librosa.effects.time_stretch(segment, rate=rate)
    y_new = np.concatenate([y[:start_idx], stretched, y[end_idx:]])
    new_end_s = orig_start_s + (len(stretched) / sr)
    
    # Remap words
    remapped_words = []
    shift = (new_end_s - orig_start_s) - (orig_end_s - orig_start_s)
    for idx, w in enumerate(words):
        w_copy = dict(w)
        if idx < start_w:
            pass
        elif idx <= end_w:
            w_copy["start"] = round(orig_start_s + (float(w["start"]) - orig_start_s) / rate, 3)
            w_copy["end"] = round(orig_start_s + (float(w["end"]) - orig_start_s) / rate, 3)
        else:
            w_copy["start"] = round(float(w["start"]) + shift, 3)
            w_copy["end"] = round(float(w["end"]) + shift, 3)
        remapped_words.append(w_copy)
        
    return y_new, orig_start_s, new_end_s, rate, {"rate": rate, "orig_start": orig_start_s, "orig_end": orig_end_s}, remapped_words

def apply_pause_long(y, sr, words, start_w, end_w, severity):
    insert_s = float(words[start_w]["end"])
    dur = {2: 1.2, 3: 1.8, 4: 2.5}.get(severity, 1.8)
    insert_idx = int(insert_s * sr)
    silence = np.zeros(int(dur * sr), dtype=y.dtype)
    y_new = np.concatenate([y[:insert_idx], silence, y[insert_idx:]])
    
    # Remap words
    remapped_words = []
    for idx, w in enumerate(words):
        w_copy = dict(w)
        if idx <= start_w:
            pass
        else:
            w_copy["start"] = round(float(w["start"]) + dur, 3)
            w_copy["end"] = round(float(w["end"]) + dur, 3)
        remapped_words.append(w_copy)
        
    return y_new, insert_s, insert_s + dur, dur, {"dur_added": dur}, remapped_words

def apply_energy_low(y, sr, words, start_w, end_w, severity):
    start_s = float(words[start_w]["start"])
    end_s = float(words[end_w]["end"])
    start_idx = int(start_s * sr)
    end_idx = int(end_s * sr)
    gain = {2: 0.50, 3: 0.30, 4: 0.15}.get(severity, 0.30)
    y_new = y.copy()
    y_new[start_idx:end_idx] = y_new[start_idx:end_idx] * gain
    expected_db = round(float(20 * np.log10(gain)), 2)
    return y_new, start_s, end_s, expected_db, {"gain": gain}, [dict(w) for w in words]

def apply_pitch_flat(y, sr, words, start_w, end_w, severity):
    start_s = float(words[start_w]["start"])
    end_s = float(words[end_w]["end"])
    start_idx = int(start_s * sr)
    end_idx = int(end_s * sr)
    segment = y[start_idx:end_idx].astype(np.float64)
    
    target = {2: 0.80, 3: 0.50, 4: 0.30}.get(severity, 0.50)
    f0, t = pw.dio(segment, sr)
    f0 = pw.stonemask(segment, f0, t, sr)
    sp = pw.cheaptrick(segment, f0, t, sr)
    ap = pw.d4c(segment, f0, t, sr)
    
    voiced = f0 > 0
    if np.any(voiced):
        f0_med = float(np.median(f0[voiced]))
        st = 12 * np.log2(f0[voiced] / f0_med)
        
        curr_f = target
        best_syn = None
        best_meas = target
        best_diff = 999.0
        
        for it in range(3):
            f0_mod = f0.copy()
            f0_mod[voiced] = f0_med * (2 ** (st * curr_f / 12.0))
            syn = pw.synthesize(f0_mod, sp, ap, sr).astype(np.float64)
            
            f0_s, t_s = pw.dio(syn, sr)
            f0_s = pw.stonemask(syn, f0_s, t_s, sr)
            min_l = min(len(f0), len(f0_s))
            common = (f0[:min_l] > 0) & (f0_s[:min_l] > 0)
            
            st_g = 12 * np.log2(f0[:min_l][common] / np.median(f0[:min_l][common]))
            st_s = 12 * np.log2(f0_s[:min_l][common] / np.median(f0_s[:min_l][common]))
            meas = np.std(st_s) / (np.std(st_g) + 1e-6)
            diff = abs(meas - target) / target
            if diff < best_diff:
                best_diff = diff
                best_syn = syn
                best_meas = meas
            if diff <= 0.10:
                break
            curr_f = curr_f * (target / (meas + 1e-6))
            
        if best_syn is not None:
            synthesized = best_syn.astype(np.float32)
        else:
            synthesized = segment.astype(np.float32)
        if len(synthesized) > len(segment):
            synthesized = synthesized[:len(segment)]
        elif len(synthesized) < len(segment):
            synthesized = np.pad(synthesized, (0, len(segment) - len(synthesized)))
        y_new = y.copy()
        y_new[start_idx:end_idx] = synthesized
        actual_ratio = round(float(best_meas), 2)
    else:
        y_new = y.copy()
        actual_ratio = target
        
    return y_new, start_s, end_s, actual_ratio, {"compression": actual_ratio}, [dict(w) for w in words]

def apply_pitch_erratic(y, sr, words, start_w, end_w, severity):
    start_s = float(words[start_w]["start"])
    end_s = float(words[end_w]["end"])
    start_idx = int(start_s * sr)
    end_idx = int(end_s * sr)
    segment = y[start_idx:end_idx].astype(np.float64)
    
    target = {2: 1.50, 3: 2.00, 4: 2.50}.get(severity, 2.00)
    f0, t = pw.dio(segment, sr)
    f0 = pw.stonemask(segment, f0, t, sr)
    sp = pw.cheaptrick(segment, f0, t, sr)
    ap = pw.d4c(segment, f0, t, sr)
    
    voiced = f0 > 0
    if np.any(voiced):
        f0_med = float(np.median(f0[voiced]))
        st = 12 * np.log2(f0[voiced] / f0_med)
        
        curr_f = target
        best_syn = None
        best_meas = target
        best_diff = 999.0
        
        for it in range(3):
            f0_mod = f0.copy()
            f0_mod[voiced] = f0_med * (2 ** (st * curr_f / 12.0))
            syn = pw.synthesize(f0_mod, sp, ap, sr).astype(np.float64)
            
            f0_s, t_s = pw.dio(syn, sr)
            f0_s = pw.stonemask(syn, f0_s, t_s, sr)
            min_l = min(len(f0), len(f0_s))
            common = (f0[:min_l] > 0) & (f0_s[:min_l] > 0)
            
            st_g = 12 * np.log2(f0[:min_l][common] / np.median(f0[:min_l][common]))
            st_s = 12 * np.log2(f0_s[:min_l][common] / np.median(f0_s[:min_l][common]))
            meas = np.std(st_s) / (np.std(st_g) + 1e-6)
            diff = abs(meas - target) / target
            if diff < best_diff:
                best_diff = diff
                best_syn = syn
                best_meas = meas
            if diff <= 0.10:
                break
            curr_f = curr_f * (target / (meas + 1e-6))
            
        if best_syn is not None:
            synthesized = best_syn.astype(np.float32)
        else:
            synthesized = segment.astype(np.float32)
        if len(synthesized) > len(segment):
            synthesized = synthesized[:len(segment)]
        elif len(synthesized) < len(segment):
            synthesized = np.pad(synthesized, (0, len(segment) - len(synthesized)))
        y_new = y.copy()
        y_new[start_idx:end_idx] = synthesized
        actual_ratio = round(float(best_meas), 2)
    else:
        y_new = y.copy()
        actual_ratio = target
        
    return y_new, start_s, end_s, actual_ratio, {"exaggeration": actual_ratio}, [dict(w) for w in words]

def main():
    print("Generating Synthetic Flawed Dataset matching CHANNELS...")
    raw_good_dir = Path("dataset/raw/good")
    raw_flawed_dir = Path("dataset/raw/flawed")
    align_good_dir = Path("dataset/alignments/good")
    align_flawed_dir = Path("dataset/alignments/flawed")
    metadata_dir = Path("dataset/metadata")
    
    flaws_json_path = metadata_dir / "flaws.json"
    recordings_csv_path = metadata_dir / "recordings.csv"
    
    align_flawed_dir.mkdir(parents=True, exist_ok=True)
    raw_flawed_dir.mkdir(parents=True, exist_ok=True)
    
    # Injected flaws matching CHANNELS exactly
    all_flaws = [
        ("PACE_FAST", apply_pace_fast),
        ("PACE_SLOW", apply_pace_slow),
        ("PAUSE_LONG", apply_pause_long),
        ("PITCH_FLAT", apply_pitch_flat),
        ("PITCH_ERRATIC", apply_pitch_erratic),
        ("ENERGY_LOW", apply_energy_low),
    ]
    
    # Assert load-time that every flaw_type is in CHANNELS
    for flaw_type, _ in all_flaws:
        assert flaw_type in CHANNELS, f"Flaw type {flaw_type} is not a valid CHANNELS key!"
        
    flaws_data = []
    
    with open(recordings_csv_path, "r", encoding="utf-8") as f:
        recordings = list(csv.DictReader(f))
        
    for row in recordings:
        if row.get("quality") != "GOOD":
            continue
        speaker_id = row["speaker_id"]
        # Train and tune on S01-S03 (include S04 as holdout set)
        file_id = row["file_id"]
        text_id = row["text_id"]
        
        audio_path = raw_good_dir / speaker_id / f"{file_id}.wav"
        align_path = align_good_dir / f"{file_id}.json"
        if not audio_path.exists() or not align_path.exists():
            continue
            
        y, sr = sf.read(audio_path)
        y = y.astype(np.float32)
        words = json.loads(align_path.read_text(encoding="utf-8"))["words"]
        n_words = len(words)
        if n_words < 12:
            continue
            
        print(f"Generating flaws for {file_id}...")
        out_speaker_dir = raw_flawed_dir / speaker_id
        out_speaker_dir.mkdir(exist_ok=True)
        
        # Precompute valid contiguous delivery phrase spans
        from speechcoach.features.phrases import group_phrases
        phrases = group_phrases(words)
        word_idx = {w["start"]: idx for idx, w in enumerate(words)}
        
        valid_spans = []
        for p in phrases[1:-1]:
            dur = p[-1]["end"] - p[0]["start"]
            if 1.0 <= dur <= 4.0 and len(p) >= 4:
                s_idx = word_idx[p[0]["start"]]
                e_idx = word_idx[p[-1]["start"]]
                valid_spans.append((s_idx, e_idx))
                
        for i in range(1, len(phrases) - 2):
            p1, p2 = phrases[i], phrases[i+1]
            gap = p2[0]["start"] - p1[-1]["end"]
            total_dur = p2[-1]["end"] - p1[0]["start"]
            if gap <= 0.35 and 1.5 <= total_dur <= 4.0:
                s_idx = word_idx[p1[0]["start"]]
                e_idx = word_idx[p2[-1]["start"]]
                valid_spans.append((s_idx, e_idx))
                
        pause_points = [word_idx[phrases[i][-1]["start"]] for i in range(1, len(phrases) - 1)]
                    
        for flaw_type, flaw_func in all_flaws:
            for severity in [2, 3, 4]:
                seed = abs(hash(f"{file_id}_{flaw_type}_{severity}")) % 100000
                rng = np.random.default_rng(seed)
                
                if flaw_type == "PAUSE_LONG":
                    if pause_points:
                        pt_idx = rng.integers(0, len(pause_points))
                        start_w = pause_points[pt_idx]
                    else:
                        min_w = 4
                        max_w = max(min_w + 1, n_words - 8)
                        start_w = rng.integers(min_w, max_w)
                    end_w = start_w
                else:
                    if valid_spans:
                        span_idx = rng.integers(0, len(valid_spans))
                        start_w, end_w = valid_spans[span_idx]
                    else:
                        min_w = 4
                        max_w = max(min_w + 1, n_words - 8)
                        start_w = rng.integers(min_w, max_w)
                        end_w = min(start_w + 6, n_words - 4)
                
                y_new, flaw_start, flaw_end, expected_val, params, remapped_words = flaw_func(
                    y, sr, words, start_w, end_w, severity
                )
                
                new_file_id = file_id.replace("_GOOD", f"_{flaw_type}_L{severity}")
                out_audio_path = out_speaker_dir / f"{new_file_id}.wav"
                sf.write(out_audio_path, y_new, sr)
                
                out_align_path = align_flawed_dir / f"{new_file_id}.json"
                out_align_path.write_text(json.dumps({
                    "file_id": new_file_id,
                    "text_id": text_id,
                    "sr": sr,
                    "duration_s": round(len(y_new) / float(sr), 3),
                    "words": remapped_words
                }, indent=2), encoding="utf-8")
                
                flaws_data.append({
                    "file_id": new_file_id,
                    "speaker_id": speaker_id,
                    "text_id": text_id,
                    "flaw_type": flaw_type,
                    "start_time": round(flaw_start, 3),
                    "end_time": round(flaw_end, 3),
                    "severity": severity,
                    "expected_val": expected_val,
                    "params": params
                })
                
    flaws_json_path.write_text(json.dumps(flaws_data, indent=2), encoding="utf-8")
    print(f"\nSuccessfully generated {len(flaws_data)} synthetic flawed audio recordings and alignments.")
    print(f"Flaws metadata saved to {flaws_json_path}")

if __name__ == "__main__":
    main()
