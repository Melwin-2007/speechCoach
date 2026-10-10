import os
import sys
import csv
import json
import warnings
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from speechcoach.audio.io import load_audio
from speechcoach.features.frame import frame_features
from speechcoach.features.words import word_table
from speechcoach.features.syllables import count_syllables
from speechcoach.models.pause_model import PauseModel
from speechcoach.models.energy_model import EnergyModel
from speechcoach.models.clarity_model import ClarityModel

def load_flaws_csv():
    meta_path = Path("e:/SpeechCoach/dataset/metadata/flaws.csv")
    flaws = {}
    if not meta_path.exists(): return flaws
    with open(meta_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            flaws[row['file_id']] = row
    return flaws

def is_flawed_window(file_id, w_start, w_end, flaw_dict, target_flaw_types):
    if file_id not in flaw_dict:
        return 0
    f = flaw_dict[file_id]
    if f['flaw_type'] not in target_flaw_types:
        return 0
    f_start = float(f['start_time'])
    f_end = float(f['end_time'])
    
    overlap = max(0, min(w_end, f_end) - max(w_start, f_start))
    if overlap > 0.3: # Threshold
        return 1
    return 0

def get_data(speakers):
    recordings_csv = Path("e:/SpeechCoach/dataset/metadata/recordings.csv")
    flaws_csv = load_flaws_csv()
    
    ideals = {}
    for i in range(1, 9):
        text_id = f"T{i:02d}"
        file_id = f"S01_{text_id}_GOOD"
        audio_path = f"e:/SpeechCoach/dataset/raw/good/S01/{file_id}.wav"
        align_path = f"e:/SpeechCoach/dataset/alignments/good/{file_id}.json"
        if os.path.exists(align_path) and os.path.exists(audio_path):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                y_b = load_audio(audio_path)
                g_b = frame_features(y_b)
                with open(align_path, 'r') as f:
                    b_words = json.load(f)['words']
                b_table = word_table(b_words, g_b)
                ideals[text_id] = b_table
    
    files_to_load = []
    
    if recordings_csv.exists():
        with open(recordings_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['speaker_id'] in speakers and row.get('quality') == 'GOOD':
                    files_to_load.append({
                        'file_id': row['file_id'],
                        'audio_path': f"e:/SpeechCoach/dataset/raw/good/{row['speaker_id']}/{row['file_id']}.wav",
                        'align_path': f"e:/SpeechCoach/dataset/alignments/good/{row['file_id']}.json"
                    })
                    
    flawed_dir = Path("e:/SpeechCoach/dataset/alignments/flawed")
    if flawed_dir.exists():
        for fpath in flawed_dir.glob("*.json"):
            parts = fpath.stem.split("_")
            speaker_id = parts[0]
            if speaker_id in speakers:
                files_to_load.append({
                    'file_id': fpath.stem,
                    'audio_path': f"e:/SpeechCoach/dataset/raw/flawed/{speaker_id}/{fpath.stem}.wav",
                    'align_path': str(fpath)
                })
                
    all_words = []
    for f_info in files_to_load:
        if not os.path.exists(f_info['audio_path']) or not os.path.exists(f_info['align_path']):
            continue
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            y = load_audio(f_info['audio_path'])
            g = frame_features(y)
            with open(f_info['align_path'], 'r') as af:
                words = json.load(af)['words']
            w_table = word_table(words, g)
            
            text_id = f_info['file_id'].split('_')[1]
            baseline_words = ideals.get(text_id)
            
            if w_table and baseline_words:
                w_table[0]['_file_id'] = f_info['file_id']
                all_words.append((w_table, baseline_words))
                
    return all_words, flaws_csv

def extract_aligned_pace(words, baseline_words):
    X, windows = [], []
    n = min(len(words), len(baseline_words))
    for i in range(n):
        w, b = words[i], baseline_words[i]
        dur = w['end'] - w['start']
        b_dur = b['end'] - b['start']
        if dur <= 0 or b_dur <= 0: continue
        X.append([dur / b_dur, dur - b_dur])
        windows.append({"start": w['start'], "end": w['end']})
    return np.array(X), windows

def extract_aligned_pitch(words, baseline_words):
    X, windows = [], []
    n = min(len(words), len(baseline_words))
    for i in range(n):
        w, b = words[i], baseline_words[i]
        w_p, b_p = w.get('f0_mean', 0), b.get('f0_mean', 0)
        diff = (w_p - b_p) if (w_p > 0 and b_p > 0) else 0.0
        ratio = (w_p / b_p) if (w_p > 0 and b_p > 0) else 1.0
        X.append([diff, ratio])
        windows.append({"start": w['start'], "end": w['end']})
    return np.array(X), windows

def build_dataset(model_or_func, pairs, flaws_dict, target_flaw_types):
    X_all, y_all = [], []
    for words, baseline_words in pairs:
        file_id = words[0]['_file_id']
        
        if hasattr(model_or_func, 'extract_features'):
            X, windows = model_or_func.extract_features(words)
        else:
            X, windows = model_or_func(words, baseline_words)
            
        if len(X) == 0: continue
        
        y = []
        for w in windows:
            y.append(is_flawed_window(file_id, w['start'], w['end'], flaws_dict, target_flaw_types))
        X_all.append(X)
        y_all.extend(y)
        
    if not X_all:
        return np.array([]), np.array([])
    return np.vstack(X_all), np.array(y_all)

def main():
    print("Loading TRAIN dataset (GOOD + FLAWED for S01, S02, S03)...")
    train_pairs, flaws_dict = get_data(['S01', 'S02', 'S03'])
    
    print("\nLoading TEST dataset (GOOD + FLAWED for S04)...")
    test_pairs, _ = get_data(['S04'])
    
    models = {
        "PaceModel (Word-Aligned)": (extract_aligned_pace, ["PACE_FAST", "PACE_SLOW"]),
        "PitchModel (Word-Aligned)": (extract_aligned_pitch, ["MONOTONE", "PITCH_ERRATIC"]),
        "PauseModel (Raw Windows)": (PauseModel(), ["PAUSE_EXCESS"]),
        "EnergyModel (Raw Windows)": (EnergyModel(), ["VOLUME_DROP"]),
        "ClarityModel (Raw Windows)": (ClarityModel(), ["CLARITY"])
    }
    
    for name, (extractor, targets) in models.items():
        print(f"\n=========================================")
        print(f"Training {name}")
        print(f"=========================================")
        
        X_train, y_train = build_dataset(extractor, train_pairs, flaws_dict, targets)
        X_test, y_test = build_dataset(extractor, test_pairs, flaws_dict, targets)
        
        print(f"Train shapes: X={X_train.shape}, Y={y_train.shape} (Flawed instances: {sum(y_train)})")
        print(f"Test shapes:  X={X_test.shape}, Y={y_test.shape} (Flawed instances: {sum(y_test)})")
        
        if len(X_train) == 0 or len(np.unique(y_train)) < 2:
            print("Skipping: Not enough labeled data (need both classes).")
            continue
            
        clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight='balanced')
        clf.fit(X_train, y_train)  # type: ignore
        
        preds = clf.predict(X_test)  # type: ignore
        print("\nTest Set Classification Report:")
        print(classification_report(y_test, preds, target_names=['GOOD', 'FLAWED'], zero_division=0))  # type: ignore

if __name__ == "__main__":
    main()
