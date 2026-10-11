import sys
import csv
from pathlib import Path
from collections import defaultdict
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from speechcoach.analyze import analyze

def main():
    recordings_path = Path("dataset/metadata/recordings.csv")
    with open(recordings_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        
    good_files = [r for r in reader if r.get("quality") == "GOOD" and r["speaker_id"] in ["S01", "S02", "S03"]]
    
    fp_by_channel = defaultdict(int)
    all_fps = []
    total_dur_s = 0.0
    
    for r in good_files:
        fid = r["file_id"]
        spk = r["speaker_id"]
        text_id = r["text_id"]
        audio_path = f"dataset/raw/good/{spk}/{fid}.wav"
        transcript = open(f"dataset/transcripts/{text_id}.txt", encoding="utf-8").read()
        
        res = analyze(audio_path, transcript, exclude_speaker=spk)
        total_dur_s += res["meta"]["duration_s"]
        
        for reg in res.get("regions", []):
            fp_by_channel[reg["type"]] += 1
            all_fps.append((fid, spk, reg))
            
    print("=== PER-CHANNEL FP COUNTS ON CLEAN FILES (S01-S03) ===")
    print(f"Total clean duration: {total_dur_s:.1f} s ({total_dur_s/60:.2f} min)")
    total_fps = sum(fp_by_channel.values())
    print(f"Total FPs: {total_fps} ({total_fps / total_dur_s * 60:.2f} FP/min)")
    for ch, count in sorted(fp_by_channel.items(), key=lambda x: -x[1]):
        print(f"  {ch:<15}: {count} FPs ({count / total_dur_s * 60:.2f} FP/min)")
        
    print("\n=== 10 SAMPLE FP REGIONS (DIAGNOSTIC DETAILS) ===")
    print(f"{'File':<16} | {'Channel':<13} | {'Start-End':<11} | {'PhraseDur':<9} | {'Syllables':<9} | {'VoicedFrac':<10} | {'Reliable':<8} | {'Src':<6}")
    print("-" * 95)
    for fid, spk, reg in all_fps[:10]:
        pdur = reg.get("phrase_dur", reg["end"] - reg["start"])
        sylls = reg.get("syllable_count", 0)
        vf = reg.get("voiced_frac", 0.0)
        rel = reg.get("reliable", True)
        src = reg.get("source", "?")
        print(f"{fid:<16} | {reg['type']:<13} | {reg['start']:.1f}-{reg['end']:.1f}s   | {pdur:<9.2f} | {sylls:<9} | {vf:<10.2f} | {str(rel):<8} | {src:<6}")

if __name__ == "__main__":
    main()
