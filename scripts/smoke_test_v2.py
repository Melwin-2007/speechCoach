import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from speechcoach.analyze import analyze

def main():
    audio = "e:/SpeechCoach/dataset/raw/flawed/S01/S01_T04_PACE_FAST.wav"
    align = "e:/SpeechCoach/dataset/transcripts/T04.txt"
    
    with open(align, 'r') as f:
        transcript = f.read()
        
    print(f"Testing analyze.py on {audio}...")
    res = analyze(audio, transcript)
    
    print(f"\nFound {len(res['flaws'])} flaws:")
    for f in res['flaws']:
        print(f"\n- {f['type']} [{f['start']}s - {f['end']}s]")
        print(f"  Explanation: {f['explanation']}")
        
if __name__ == "__main__":
    main()
