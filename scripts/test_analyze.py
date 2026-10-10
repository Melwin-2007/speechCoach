import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from speechcoach.analyze import analyze

def main():
    audio_path = "dataset/raw/good/S01/S01_T01.wav"
    transcript = open("dataset/transcripts/T01.txt", encoding="utf-8").read()
    
    # We use S01 bounds for S01 (or S04's bounds). 
    # exclude_speaker will load the LOO bound if it exists, otherwise it will try population_bounds.json
    res = analyze(audio_path, transcript, exclude_speaker="S01")
    
    with open("result.json", "w") as f:
        json.dump(res, f, indent=2)
        
    print("Saved result.json")

if __name__ == "__main__":
    main()
