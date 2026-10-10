import os
import sys
import csv
import json
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from speechcoach.audio.io import load_audio
from speechcoach.features.frame import frame_features
from speechcoach.features.words import word_table
from speechcoach.models.pace_model import PaceModel
from speechcoach.models.pause_model import PauseModel
from speechcoach.models.pitch_model import PitchModel
from speechcoach.models.energy_model import EnergyModel
from speechcoach.models.clarity_model import ClarityModel

def extract_rich_words(speaker_list):
    """Loads audio and alignments for the given speakers, and returns fully populated word lists."""
    meta_path = Path("e:/SpeechCoach/dataset/metadata/recordings.csv")
    all_words = []
    
    with open(meta_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('quality', 'GOOD') == 'GOOD' and row['speaker_id'] in speaker_list:
                file_id = row['file_id']
                audio_path = f"e:/SpeechCoach/dataset/raw/good/{row['speaker_id']}/{file_id}.wav"
                align_path = f"e:/SpeechCoach/dataset/alignments/good/{file_id}.json"
                
                if not os.path.exists(audio_path) or not os.path.exists(align_path):
                    continue
                    
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    y = load_audio(audio_path)
                    g = frame_features(y)
                    
                    with open(align_path, 'r', encoding='utf-8') as af:
                        align_data = json.load(af)
                        words = align_data['words']
                        
                    w_table = word_table(words, g)
                    # Add file_id to the first word just so we can track it later
                    if w_table:
                        w_table[0]['_file_id'] = file_id
                    all_words.append(w_table)
    return all_words

def main():
    print("Loading TRAIN dataset (S01, S02, S03)...")
    train_words = extract_rich_words(['S01', 'S02', 'S03'])
    print(f"Extracted features for {len(train_words)} training recordings.")
    
    print("\nLoading TEST dataset (S04)...")
    test_words = extract_rich_words(['S04'])
    print(f"Extracted features for {len(test_words)} testing recordings.\n")
    
    models = {
        "PaceModel": PaceModel(),
        "PauseModel": PauseModel(),
        "PitchModel": PitchModel(),
        "EnergyModel": EnergyModel(),
        "ClarityModel": ClarityModel()
    }
    
    for name, model in models.items():
        print(f"--- Testing {name} ---")
        try:
            model.train(train_words)
        except Exception as e:
            print(f"Error training {name}: {e}")
            continue
            
        total_false_positives = 0
        for test_file in test_words:
            file_id = test_file[0].get('_file_id', 'Unknown')
            flaws = model.detect_flaws(test_file)
            
            if flaws:
                total_false_positives += len(flaws)
                print(f"  [FALSE POSITIVE] {file_id}: Detected {len(flaws)} flaws.")
                for flaw in flaws:
                    print(f"    -> {flaw['type']} at {flaw['start']}s - {flaw['end']}s")
                    
        if total_false_positives == 0:
            print(f"  Result: PERFECT! 0 false positives on S04.")
        else:
            print(f"  Result: {total_false_positives} false positives detected across S04.")
        print()

if __name__ == "__main__":
    main()
