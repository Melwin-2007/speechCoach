import json
import numpy as np
from pathlib import Path
from speechcoach.audio.io import load_audio
from speechcoach.align.transcript import parse_transcript
from speechcoach.align.aligner import align_words
from speechcoach.features.frame import frame_features
from speechcoach.features.words import word_table

def get_data(audio_path, transcript, align=True):
    y = load_audio(audio_path, sr=16000, target_lufs=-23.0)
    words = align_words(y, parse_transcript(transcript)) if align else []
    g = frame_features(y)
    return {"y": y, "g": g, "words": words}

def main():
    metadata_dir = Path("e:/SpeechCoach/dataset/metadata")
    with open(metadata_dir / "flaws.json") as f:
        flaws = json.load(f)
        
    with open(metadata_dir / "recordings.csv") as f:
        import csv
        recordings = list(csv.DictReader(f))
        rec_map = {r["file_id"]: r for r in recordings}
        
    good_cache = {}
    
    print(f"{'File':<25} | {'Flaw':<15} | {'Expected':<10} | {'Measured':<10} | {'Status':<6}")
    print("-" * 75)
    
    fails = 0
    for flaw in flaws:
        file_id = flaw["file_id"]
        speaker = flaw["speaker_id"]
        good_id = file_id.split("_")[0] + "_" + file_id.split("_")[1] + "_GOOD"
        
        audio_path = Path(f"e:/SpeechCoach/dataset/raw/flawed/{speaker}/{file_id}.wav")
        good_audio = Path(f"e:/SpeechCoach/dataset/raw/good/{speaker}/{good_id}.wav")
        
        if not audio_path.exists() or not good_audio.exists():
            continue
            
        text_id = rec_map[good_id]["text_id"]
        with open(f"e:/SpeechCoach/dataset/transcripts/{text_id}.txt", "r", encoding="utf-8") as f:
            transcript = f.read()
            
        typ = flaw["flaw_type"]
        needs_align = typ in ["PACE_FAST", "PACE_SLOW", "PAUSE_EXCESS"]
        if good_id not in good_cache:
            good_cache[good_id] = get_data(good_audio, transcript, align=True)
            
        d_good = good_cache[good_id]
        d_inj = get_data(audio_path, transcript, align=needs_align)
        
        start, end = flaw["start_time"], flaw["end_time"]
        expected = flaw["expected_val"]
        measured = None
        
        # We find the physical frames based on time
        t_good = d_good["g"]["t"]
        t_inj = d_inj["g"]["t"]
        
        if typ in ["PACE_FAST", "PACE_SLOW"]:
            orig_end = start + (end - start) * expected
            win_good = (t_good >= start) & (t_good <= orig_end)
            win_inj = (t_inj >= start) & (t_inj <= end)
            # just measure the duration of words in that span
            good_w = [w for w in d_good["words"] if w['start'] >= start - 0.2 and w['end'] <= orig_end + 0.2]
            inj_w = [w for w in d_inj["words"] if w['start'] >= start - 0.2 and w['end'] <= end + 0.2]
            if good_w and inj_w:
                g_dur = good_w[-1]['end'] - good_w[0]['start']
                i_dur = inj_w[-1]['end'] - inj_w[0]['start']
                if i_dur > 0:
                    measured = g_dur / i_dur
                else:
                    measured = 0.0
        
        elif typ == "VOLUME_DROP":
            win_good = (t_good >= start) & (t_good <= end)
            win_inj = (t_inj >= start) & (t_inj <= end)
            if win_good.any() and win_inj.any():
                measured = np.median(d_inj["g"]["db_rel"][win_inj]) - np.median(d_good["g"]["db_rel"][win_good])
            
        elif typ == "PITCH_FLAT" or typ == "PITCH_ERRATIC":
            win_good = (t_good >= start) & (t_good <= end)
            win_inj = (t_inj >= start) & (t_inj <= end)
            if win_good.any() and win_inj.any():
                g_f0 = d_good["g"]["f0"][win_good]
                i_f0 = d_inj["g"]["f0"][win_inj]
                g_std = np.std(g_f0[g_f0>0]) if (g_f0>0).any() else 0.0
                i_std = np.std(i_f0[i_f0>0]) if (i_f0>0).any() else 0.0
                measured = i_std / (g_std + 1e-6)
            
        elif typ == "PAUSE_EXCESS":
            # For pause, start == end in the good file. We just find the gap between the two words around it
            inj_w = d_inj["words"]
            # find the gap closest to `start`
            gaps = []
            for i in range(len(inj_w)-1):
                gap = inj_w[i+1]['start'] - inj_w[i]['end']
                dist = abs(inj_w[i]['end'] - start)
                gaps.append((dist, gap))
            gaps.sort()
            if gaps:
                measured = gaps[0][1]
            else:
                measured = 0.0
            
        if expected is None or measured is None:
            continue
            
        diff = abs(measured - expected) / (abs(expected) + 1e-6)
        status = "PASS" if diff <= 0.25 else "FAIL"
        if status == "FAIL": fails += 1
        
        print(f"{file_id:<25} | {typ:<15} | {expected:<10.2f} | {measured:<10.2f} | {status:<6}")
        
    if fails > 0:
        print(f"FAILED: {fails} labels failed verification!")
    else:
        print("All labels verified successfully!")

if __name__ == '__main__':
    main()
