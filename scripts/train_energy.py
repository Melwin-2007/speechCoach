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
from speechcoach.models.energy_model import EnergyModel

def main():
    print("Loading globally LUFS-normalized recordings for Energy training...")
    meta_path = Path("e:/SpeechCoach/dataset/metadata/recordings.csv")
    
    if not meta_path.exists():
        print("recordings.csv not found!")
        return
        
    all_words = []
    
    with open(meta_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('quality', 'GOOD') == 'GOOD':
                speaker_id = row['speaker_id']
                file_id = row['file_id']
                audio_path = f"e:/SpeechCoach/dataset/raw/good/{speaker_id}/{file_id}.wav"
                align_path = f"e:/SpeechCoach/dataset/alignments/good/{file_id}.json"
                
                if not os.path.exists(audio_path) or not os.path.exists(align_path):
                    continue
                    
                print(f"  Processing {file_id}...")
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    # load_audio inherently normalizes to -23.0 LUFS globally
                    y = load_audio(audio_path)
                    # frame_features generates db_rel, which normalizes locally to the 95th percentile peak
                    g = frame_features(y)
                    
                    with open(align_path, 'r', encoding='utf-8') as af:
                        align_data = json.load(af)
                        words = align_data['words']
                        
                    w_table = word_table(words, g)
                    all_words.append(w_table)
                
    if not all_words:
        print("No valid recordings processed.")
        return
        
    print(f"\nExtracted acoustic energy features for {len(all_words)} recordings.")
    
    # Initialize and train
    print("Training EnergyModel (IsolationForest) on relative db_mean and dynamic_range...")
    model = EnergyModel()
    model.train(all_words)
    
    # Save the model
    models_dir = Path("e:/SpeechCoach/src/speechcoach/models")
    models_dir.mkdir(exist_ok=True)
    model_path = models_dir / "energy_model.pkl"
    model.save(model_path)
    print(f"Saved model to {model_path}")
    
    # Test on one recording to show output
    test_file = all_words[0]
    print("\nTesting on first recording...")
    flaws = model.detect_flaws(test_file)
    
    if not flaws:
        print("No volume/energy flaws detected in this GOOD recording (as expected!).")
    else:
        print(f"Detected {len(flaws)} potential flaws:")
        for flaw in flaws:
            print(f"  - {flaw['type']} from {flaw['start']}s to {flaw['end']}s "
                  f"(Energy Mean: {flaw['evidence']['energy_mean_relative_db']}dB, "
                  f"Dynamic Range: {flaw['evidence']['dynamic_range_db']}dB)")

if __name__ == "__main__":
    main()
