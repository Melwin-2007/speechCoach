import os
import csv
import json
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
try:
    import pyworld as pw
except ImportError:
    pw = None

np.random.seed(42)

def apply_pace_fast(y, sr, start_s, end_s):
    start_idx = int(start_s * sr)
    end_idx = int(end_s * sr)
    segment = y[start_idx:end_idx]
    # Speed up by 1.5x
    stretched = librosa.effects.time_stretch(segment, rate=1.5)
    y_new = np.concatenate([y[:start_idx], stretched, y[end_idx:]])
    # The end_s in the new file will be earlier because it shrank
    new_end_s = start_s + (len(stretched) / sr)
    return y_new, start_s, new_end_s

def apply_pace_slow(y, sr, start_s, end_s):
    start_idx = int(start_s * sr)
    end_idx = int(end_s * sr)
    segment = y[start_idx:end_idx]
    # Slow down by 0.7x
    stretched = librosa.effects.time_stretch(segment, rate=0.7)
    y_new = np.concatenate([y[:start_idx], stretched, y[end_idx:]])
    new_end_s = start_s + (len(stretched) / sr)
    return y_new, start_s, new_end_s

def apply_pause_excess(y, sr, insert_s):
    # Insert 2.5 seconds of silence
    insert_idx = int(insert_s * sr)
    silence = np.zeros(int(2.5 * sr), dtype=y.dtype)
    y_new = np.concatenate([y[:insert_idx], silence, y[insert_idx:]])
    return y_new, insert_s, insert_s + 2.5

def apply_volume_drop(y, sr, start_s, end_s):
    start_idx = int(start_s * sr)
    end_idx = int(end_s * sr)
    y_new = y.copy()
    y_new[start_idx:end_idx] = y_new[start_idx:end_idx] * 0.15  # drop volume significantly
    return y_new, start_s, end_s

def apply_monotone(y, sr, start_s, end_s):
    if pw is None:
        return y, start_s, end_s
    start_idx = int(start_s * sr)
    end_idx = int(end_s * sr)
    segment = y[start_idx:end_idx].astype(np.float64)
    
    # Extract pyworld features
    f0, t = pw.dio(segment, sr)
    f0 = pw.stonemask(segment, f0, t, sr)
    sp = pw.cheaptrick(segment, f0, t, sr)
    ap = pw.d4c(segment, f0, t, sr)
    
    # Flatten F0 to its non-zero mean
    f0_mean = np.mean(f0[f0 > 0]) if np.any(f0 > 0) else 150.0
    f0[f0 > 0] = f0_mean
    
    synthesized = pw.synthesize(f0, sp, ap, sr).astype(np.float32)
    
    if len(synthesized) > len(segment):
        synthesized = synthesized[:len(segment)]
    elif len(synthesized) < len(segment):
        synthesized = np.pad(synthesized, (0, len(segment) - len(synthesized)))
        
    y_new = y.copy()
    y_new[start_idx:end_idx] = synthesized
    return y_new, start_s, end_s

def apply_clarity(y, sr, start_s, end_s):
    # Add white noise and simulate low quality / mumbling
    start_idx = int(start_s * sr)
    end_idx = int(end_s * sr)
    segment = y[start_idx:end_idx]
    
    noise = np.random.normal(0, 0.02, len(segment))
    y_new = y.copy()
    y_new[start_idx:end_idx] = segment * 0.6 + noise
    return y_new, start_s, end_s

def main():
    print("Generating Synthetic Flawed Dataset...")
    
    raw_good_dir = Path("e:/SpeechCoach/dataset/raw/good")
    raw_flawed_dir = Path("e:/SpeechCoach/dataset/raw/flawed")
    metadata_dir = Path("e:/SpeechCoach/dataset/metadata")
    
    flaws_csv_path = metadata_dir / "flaws.csv"
    recordings_csv_path = metadata_dir / "recordings.csv"
    
    # Ensure dirs exist
    raw_flawed_dir.mkdir(parents=True, exist_ok=True)
    
    # Track the flaws we generate
    flaws_data = []
    
    # Map Text IDs to flaw types for deterministic generation
    flaw_map = {
        "T01": ("PACE_FAST", apply_pace_fast),
        "T02": ("PACE_SLOW", apply_pace_slow),
        "T03": ("PAUSE_EXCESS", lambda y, sr: apply_pause_excess(y, sr, 10.0)),
        "T04": ("MONOTONE", apply_monotone),
        "T05": ("VOLUME_DROP", apply_volume_drop),
        "T06": ("CLARITY", apply_clarity),
        "T07": ("PACE_FAST", apply_pace_fast),
        "T08": ("MONOTONE", apply_monotone)
    }
    
    with open(recordings_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        recordings = list(reader)
        
    for row in recordings:
        if row.get('quality') != 'GOOD':
            continue
            
        speaker_id = row['speaker_id']
        file_id = row['file_id']
        text_id = row['text_id']
        
        audio_path = raw_good_dir / speaker_id / f"{file_id}.wav"
        if not audio_path.exists():
            continue
            
        if text_id not in flaw_map:
            continue
            
        flaw_type, flaw_func = flaw_map[text_id]
        
        print(f"Applying {flaw_type} to {file_id}...")
        y, sr = librosa.load(audio_path, sr=16000, mono=True)
        
        # Apply the flaw (defaults: from 5.0s to 15.0s unless it's a pause excess which takes 10.0s)
        if flaw_type == "PAUSE_EXCESS":
            y_new, flaw_start, flaw_end = flaw_func(y, sr)
        else:
            y_new, flaw_start, flaw_end = flaw_func(y, sr, 5.0, 15.0)
            
        # Create output directory for this speaker
        out_speaker_dir = raw_flawed_dir / speaker_id
        out_speaker_dir.mkdir(exist_ok=True)
        
        # Generate new file ID and save
        new_file_id = file_id.replace("_GOOD", f"_{flaw_type}")
        out_path = out_speaker_dir / f"{new_file_id}.wav"
        
        sf.write(out_path, y_new, sr)
        
        # Log the flaw
        flaws_data.append({
            "file_id": new_file_id,
            "speaker_id": speaker_id,
            "text_id": text_id,
            "flaw_type": flaw_type,
            "start_time": round(flaw_start, 3),
            "end_time": round(flaw_end, 3),
            "severity": np.random.randint(2, 5) # Random severity 2, 3, or 4
        })
        
    # Write to flaws.csv
    file_exists = flaws_csv_path.exists()
    with open(flaws_csv_path, 'a' if file_exists else 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["file_id", "speaker_id", "text_id", "flaw_type", "start_time", "end_time", "severity"])
        if not file_exists:
            writer.writeheader()
        for row in flaws_data:
            writer.writerow(row)
            
    print(f"\nSuccessfully generated {len(flaws_data)} flawed audio recordings!")
    print(f"Flaw metadata saved to {flaws_csv_path}")

if __name__ == "__main__":
    main()
