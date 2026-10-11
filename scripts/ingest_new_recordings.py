#!/usr/bin/env python3
"""scripts/ingest_new_recordings.py
Ingest raw recordings from data/interim/ into dataset/raw/good/,
standardize audio (16 kHz mono WAV), update dataset/metadata/recordings.csv,
and generate word alignments in dataset/alignments/good/.
"""

import csv
import json
import re
import sys
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))

from speechcoach.audio.io import load_audio
from speechcoach.align.transcript import parse_transcript
from speechcoach.align.aligner import align_words
from scripts.prepare_audio import (
    find_ffmpeg,
    convert_to_wav_ffmpeg,
    read_wav_samples,
    trim_silence,
    write_wav_samples,
    compute_audio_stats,
)


def main():
    print("=" * 60)
    print("SpeechCoach: Ingesting new recordings from data/interim/")
    print("=" * 60)

    interim_dir = REPO_ROOT / "data" / "interim"
    good_dir = REPO_ROOT / "dataset" / "raw" / "good"
    align_dir = REPO_ROOT / "dataset" / "alignments" / "good"
    transcripts_dir = REPO_ROOT / "dataset" / "transcripts"
    recordings_csv = REPO_ROOT / "dataset" / "metadata" / "recordings.csv"

    good_dir.mkdir(parents=True, exist_ok=True)
    align_dir.mkdir(parents=True, exist_ok=True)

    ffmpeg_bin = find_ffmpeg()
    if not ffmpeg_bin:
        print("ERROR: ffmpeg binary not found on system PATH.")
        sys.exit(1)

    # Read existing recordings
    existing_fids = set()
    rows = []
    if recordings_csv.exists():
        with open(recordings_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_fids.add(row["file_id"])
                rows.append(row)

    # Find interim files
    interim_files = sorted(list(interim_dir.rglob("*.ogg")) + list(interim_dir.rglob("*.wav")))
    print(f"Found {len(interim_files)} files in data/interim/")

    converted_count = 0
    aligned_count = 0
    new_csv_rows = []

    import tempfile

    for audio_file in interim_files:
        # Match pattern T01-S01 or T02=S04 or S01_T01
        stem = audio_file.stem
        m = re.match(r"(T\d+)[\-=](S\d+)", stem)
        if m:
            text_id, speaker_id = m.groups()
        else:
            m2 = re.match(r"(S\d+)[_\-](T\d+)", stem)
            if m2:
                speaker_id, text_id = m2.groups()
            else:
                continue

        file_id = f"{speaker_id}_{text_id}_GOOD"
        target_spk_dir = good_dir / speaker_id
        target_spk_dir.mkdir(parents=True, exist_ok=True)
        target_wav = target_spk_dir / f"{file_id}.wav"
        target_align = align_dir / f"{file_id}.json"
        text_file = transcripts_dir / f"{text_id}.txt"

        if not text_file.exists():
            print(f"[WARN] Transcript {text_file.name} missing for {file_id}. Skipping.")
            continue

        # 1. Convert to 16 kHz mono WAV with edge silence trimmed if not exists
        if not target_wav.exists():
            print(f"[CONVERT] {audio_file.name} -> {target_wav.relative_to(REPO_ROOT)}")
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_f:
                tmp_path = Path(tmp_f.name)
            try:
                convert_to_wav_ffmpeg(ffmpeg_bin, audio_file, tmp_path)
                samples, sr = read_wav_samples(tmp_path)
                trimmed = trim_silence(samples, sr=sr, threshold_db=-40.0, keep_silence_s=0.5)
                write_wav_samples(target_wav, trimmed, framerate=16000)
                converted_count += 1
            finally:
                if tmp_path.exists():
                    tmp_path.unlink()

        # 2. Get duration
        samples, sr = read_wav_samples(target_wav)
        duration_s = round(len(samples) / float(sr), 3)

        # 3. Add to CSV rows if missing
        if file_id not in existing_fids:
            new_row = {
                "file_id": file_id,
                "text_id": text_id,
                "speaker_id": speaker_id,
                "quality": "GOOD",
                "duration_s": f"{duration_s:.3f}",
                "license": "CC-BY-4.0",
                "redistributable": "true",
            }
            rows.append(new_row)
            existing_fids.add(file_id)
            new_csv_rows.append(new_row)

        # 4. Generate Alignment JSON if missing
        if not target_align.exists():
            print(f"[ALIGN] Aligning {file_id} via MMS_FA...")
            y = load_audio(target_wav, sr=16000)
            transcript_text = text_file.read_text(encoding="utf-8")
            raw_words = parse_transcript(transcript_text)
            words = align_words(y, raw_words)

            align_data = {
                "file_id": file_id,
                "text_id": text_id,
                "sr": 16000,
                "duration_s": duration_s,
                "words": words,
            }
            target_align.write_text(json.dumps(align_data, indent=2), encoding="utf-8")
            aligned_count += 1

    # Save updated CSV if there are new rows
    if new_csv_rows:
        fieldnames = ["file_id", "text_id", "speaker_id", "quality", "duration_s", "license", "redistributable"]
        with open(recordings_csv, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"[CSV] Added {len(new_csv_rows)} recordings to {recordings_csv.name}")

    print("-" * 60)
    print(f"Ingestion complete!")
    print(f"  Audio converted: {converted_count}")
    print(f"  Alignments generated: {aligned_count}")
    print(f"  Total recordings in catalog: {len(rows)}")
    print("-" * 60)


if __name__ == "__main__":
    main()
