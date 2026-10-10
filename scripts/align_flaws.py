import os
import json
from pathlib import Path
import warnings

# Suppress torchaudio warnings
warnings.filterwarnings("ignore")

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from speechcoach.align.transcript import parse_transcript
from speechcoach.align.aligner import align_words
from speechcoach.audio.io import load_audio

def main():
    print("Starting batch forced alignment for 144 flawed recordings...")
    flawed_dir = Path("e:/SpeechCoach/dataset/raw/flawed")
    text_dir = Path("e:/SpeechCoach/dataset/transcripts")
    out_dir = Path("e:/SpeechCoach/dataset/alignments/flawed")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    files = list(flawed_dir.rglob("*.wav"))
    
    for idx, audio_path in enumerate(files):
        # Example: S01_T01_PACE_FAST.wav
        parts = audio_path.stem.split("_")
        text_id = parts[1]
        text_path = text_dir / f"{text_id}.txt"
        out_json = out_dir / f"{audio_path.stem}.json"
        
        if out_json.exists():
            continue
            
        print(f"[{idx+1}/{len(files)}] Aligning {audio_path.stem}...")
        y = load_audio(audio_path)
        words = parse_transcript(text_path.read_text(encoding="utf-8"))
        aligned_words = align_words(y, words)
        
        out_data = {
            "file_id": audio_path.stem,
            "text_id": text_id,
            "sr": 16000,
            "duration_s": round(len(y) / 16000.0, 3),
            "words": aligned_words
        }
        out_json.write_text(json.dumps(out_data, indent=2))
        
    print("Finished aligning all flawed recordings.")

if __name__ == "__main__":
    main()
