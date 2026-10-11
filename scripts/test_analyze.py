import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from speechcoach.analyze import analyze

def main():
    audio_path = "dataset/raw/good/S01/S01_T01_GOOD.wav"
    transcript = open("dataset/transcripts/T01.txt", encoding="utf-8").read()
    
    print(f"Running pipeline on {audio_path}...")
    res = analyze(audio_path, transcript, exclude_speaker="S01")
    
    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
        
    print("-" * 60)
    print(f"Overall Delivery Score: {res.get('score', 0.0)} / 100.0")
    print(f"Scoring Model Hash:     {res.get('model_hash', 'unknown')}")
    print(f"Population Bounds Hash: {res.get('bounds_hash', 'unknown')}")
    print(f"Flaws Detected:         {len(res.get('regions', []))}")
    for r in res.get("regions", []):
        print(f"  [{r['start']}s - {r['end']}s] {r['type']} ({r['tier']}): {r['explanation']}")
    print("-" * 60)
    print("Full result saved to result.json")

if __name__ == "__main__":
    main()
