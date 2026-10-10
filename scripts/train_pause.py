import os
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from speechcoach.models.pause_model import PauseModel

def main():
    print("Loading GOOD alignments for training...")
    align_dir = Path("e:/SpeechCoach/dataset/alignments/good")
    all_words = []
    
    for file_path in align_dir.glob("*.json"):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'words' in data:
                all_words.append(data['words'])
                
    if not all_words:
        print("No alignment files found.")
        return
        
    print(f"Found {len(all_words)} recordings.")
    
    # Initialize and train
    print("Training PauseModel (IsolationForest) on pause duration, punctuation, and frequency...")
    model = PauseModel()
    model.train(all_words)
    
    # Save the model
    models_dir = Path("e:/SpeechCoach/src/speechcoach/models")
    models_dir.mkdir(exist_ok=True)
    model_path = models_dir / "pause_model.pkl"
    model.save(model_path)
    print(f"Saved model to {model_path}")
    
    # Test on one recording to show output
    test_file = all_words[0]
    print("\nTesting on first recording...")
    flaws = model.detect_flaws(test_file)
    
    if not flaws:
        print("No pausing flaws detected in this GOOD recording (as expected).")
    else:
        print(f"Detected {len(flaws)} potential flaws:")
        for flaw in flaws:
            print(f"  - {flaw['type']} from {flaw['start']}s to {flaw['end']}s "
                  f"(Duration: {flaw['evidence']['pause_duration_s']}s, "
                  f"Punctuation: {flaw['evidence']['had_punctuation']})")

if __name__ == "__main__":
    main()
