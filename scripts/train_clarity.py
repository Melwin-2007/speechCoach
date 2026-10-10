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
from speechcoach.models.clarity_model import ClarityModel

def main():
    print("Loading recordings for Voice Quality/Clarity training...")
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
                    y = load_audio(audio_path)
                    g = frame_features(y)
                    
                    with open(align_path, 'r', encoding='utf-8') as af:
                        align_data = json.load(af)
                        words = align_data['words']
                        
                    w_table = word_table(words, g)
                    all_words.append(w_table)
                
    if not all_words:
        print("No valid recordings processed.")
        return
        
    print(f"\nExtracted voice quality features for {len(all_words)} recordings.")
    
    # Initialize and train
    print("Training ClarityModel (IsolationForest) on HNR, Spectral Flux, and 13 MFCCs...")
    model = ClarityModel()
    model.train(all_words)
    
    # Save the model
    models_dir = Path("e:/SpeechCoach/src/speechcoach/models")
    models_dir.mkdir(exist_ok=True)
    model_path = models_dir / "clarity_model.pkl"
    model.save(model_path)
    print(f"Saved model to {model_path}")
    
    # Test on one recording to show output
    test_file = all_words[0]
    print("\nTesting on first recording...")
    flaws = model.detect_flaws(test_file)
    
    if not flaws:
        print("No clarity flaws detected in this GOOD recording (as expected!).")
    else:
        print(f"Detected {len(flaws)} potential flaws:")
        for flaw in flaws:
            print(f"  - {flaw['type']} from {flaw['start']}s to {flaw['end']}s "
                  f"(HNR: {flaw['evidence']['hnr_mean']}, "
                  f"Flux: {flaw['evidence']['spectral_flux_mean']})")

if __name__ == "__main__":
    main()
