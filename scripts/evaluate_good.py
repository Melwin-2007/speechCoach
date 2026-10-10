import sys
import csv
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from speechcoach.analyze import analyze

def main():
    recordings_csv = Path("e:/SpeechCoach/dataset/metadata/recordings.csv")
    items = []
    with open(recordings_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('quality') == 'GOOD':
                items.append({
                    "audio": f"e:/SpeechCoach/dataset/raw/good/{row['speaker_id']}/{row['file_id']}.wav",
                    "transcript": open(f"e:/SpeechCoach/dataset/transcripts/{row['text_id']}.txt").read(),
                    "speaker": row["speaker_id"],
                    "file_id": row["file_id"]
                })
                
    items.sort(key=lambda x: x["audio"])
    
    total_flaws = 0
    s04_flaws = []
    
    print(f"Testing {len(items)} GOOD files for false positives...")
    for m in items:
        if not Path(m["audio"]).exists(): continue
        try:
            res = analyze(m["audio"], m["transcript"])
            flaws = res.get("flaws", [])
            total_flaws += len(flaws)
            
            if len(flaws) > 0:
                print(f"[{m['file_id']}] {len(flaws)} false positives detected.")
                if m["speaker"] == "S04":
                    for f in flaws:
                        s04_flaws.append((m['file_id'], f))
                        print(f"  - {f['type']} ({f['evidence']['source']}): {f['explanation']}")
        except Exception as e:
            print(f"Error on {m['file_id']}: {e}")
            
    print(f"\nTotal False Positives on GOOD data: {total_flaws}")
    print(f"Total False Positives on S04 (Hard Holdout): {len(s04_flaws)}")

if __name__ == "__main__":
    main()
