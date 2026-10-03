import argparse
import json
import hashlib
from pathlib import Path

from speechcoach.audio.io import load_audio
from speechcoach.align.transcript import parse_transcript
from speechcoach.align.aligner import align_words

def get_hash(audio_path: Path, text_path: Path) -> str:
    """Helper to compute content hash of audio bytes and text string."""
    h = hashlib.sha256()
    h.update(audio_path.read_bytes())
    h.update(text_path.read_text(encoding="utf-8").encode("utf-8"))
    return h.hexdigest()

def main():
    parser = argparse.ArgumentParser(description="Run forced alignment")
    parser.add_argument("audio_path", type=Path, help="Path to the audio file")
    parser.add_argument("text_path", type=Path, help="Path to the transcript text file")
    parser.add_argument("output_json", type=Path, help="Path to save the Alignment JSON")
    
    args = parser.parse_args()
    
    cache_hash = get_hash(args.audio_path, args.text_path)
    
    text = args.text_path.read_text(encoding="utf-8")
    words = parse_transcript(text)
    
    y = load_audio(args.audio_path)
    aligned_words = align_words(y, words)
    
    out_data = {
        "file_id": args.audio_path.stem,
        "text_id": args.text_path.stem,
        "sr": 16000,
        "duration_s": round(len(y) / 16000.0, 3),
        "method": "torchaudio-MMS_FA",
        "hash": cache_hash,
        "words": aligned_words
    }
    
    args.output_json.write_text(json.dumps(out_data, indent=2))
    print(f"Alignment saved to {args.output_json}")

if __name__ == "__main__":
    main()
