#!/usr/bin/env python3
"""scripts/prepare_audio.py - Standardize audio to 16 kHz mono WAV with edge silence trimmed.

Converts input audio/video (wav, mp3, m4a, mp4, etc.) to:
- Sample rate: 16000 Hz
- Channels: Mono (1 channel)
- Format: 16-bit PCM WAV
- Edge silence: Trimmed to at most 1.0 second leading and trailing
- Prints: duration, peak level (dBFS), estimated noise floor
"""

import argparse
import glob
import math
import os
import shutil
import subprocess
import sys
import tempfile
import wave
import struct
from pathlib import Path


def find_ffmpeg() -> str | None:
    """Find ffmpeg binary in system PATH or common installation directories."""
    which_ffmpeg = shutil.which("ffmpeg")
    if which_ffmpeg:
        return which_ffmpeg

    # Common Windows winget / appdata locations
    candidates = []
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        winget_pattern = os.path.join(
            local_app_data, "Microsoft", "WinGet", "Packages", "*ffmpeg*", "**", "ffmpeg.exe"
        )
        candidates.extend(glob.glob(winget_pattern, recursive=True))

    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    if program_files:
        pf_pattern = os.path.join(program_files, "**", "ffmpeg.exe")
        candidates.extend(glob.glob(pf_pattern, recursive=True))

    for c in candidates:
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def convert_to_wav_ffmpeg(ffmpeg_bin: str, input_path: Path, output_wav: Path) -> None:
    """Use ffmpeg to convert any media to 16 kHz mono 16-bit WAV."""
    cmd = [
        ffmpeg_bin,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(input_path),
        "-vn",               # Drop video stream if present
        "-acodec",
        "pcm_s16le",
        "-ac",
        "1",
        "-ar",
        "16000",
        str(output_wav),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg conversion failed: {res.stderr.strip()}")


def read_wav_samples(wav_path: Path) -> tuple[list[float], int]:
    """Read 16-bit mono WAV using standard library wave module."""
    with wave.open(str(wav_path), "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw_bytes = wf.readframes(n_frames)

    if sampwidth != 2:
        raise ValueError(f"Expected 16-bit audio (sampwidth=2), got {sampwidth}")

    n_samples = n_frames * n_channels
    fmt = f"<{n_samples}h"
    unpacked = struct.unpack(fmt, raw_bytes)

    if n_channels == 1:
        # Normalize to float in [-1.0, 1.0]
        samples = [s / 32768.0 for s in unpacked]
    else:
        # Mix down to mono
        samples = []
        for i in range(0, len(unpacked), n_channels):
            avg = sum(unpacked[i : i + n_channels]) / (n_channels * 32768.0)
            samples.append(avg)

    return samples, framerate


def write_wav_samples(wav_path: Path, samples: list[float], framerate: int = 16000) -> None:
    """Write float samples to 16-bit mono WAV file."""
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(framerate)
        int_samples = [max(-32768, min(32767, int(s * 32767.0))) for s in samples]
        data = struct.pack(f"<{len(int_samples)}h", *int_samples)
        wf.writeframes(data)


def compute_audio_stats(samples: list[float], sr: int = 16000) -> dict:
    """Compute duration, peak level in dBFS, and estimated noise floor."""
    if not samples:
        return {"duration_s": 0.0, "peak_db": -99.0, "noise_floor_db": -99.0}

    duration_s = len(samples) / float(sr)
    max_amp = max(abs(s) for s in samples)
    peak_db = 20.0 * math.log10(max(max_amp, 1e-6))

    # Frame-wise RMS (20 ms window, 10 ms hop)
    frame_len = int(sr * 0.02)
    hop_len = int(sr * 0.01)
    rms_vals = []
    for i in range(0, len(samples) - frame_len, hop_len):
        chunk = samples[i : i + frame_len]
        ms = sum(x * x for x in chunk) / float(frame_len)
        rms = math.sqrt(ms)
        rms_vals.append(max(rms, 1e-6))

    if rms_vals:
        rms_vals.sort()
        # Bottom 10th percentile as estimate for noise floor
        p10 = rms_vals[int(len(rms_vals) * 0.10)]
        noise_floor_db = 20.0 * math.log10(p10)
    else:
        noise_floor_db = -99.0

    return {
        "duration_s": round(duration_s, 2),
        "peak_db": round(peak_db, 2),
        "noise_floor_db": round(noise_floor_db, 2),
    }


def trim_silence(
    samples: list[float],
    sr: int = 16000,
    threshold_db: float = -40.0,
    keep_silence_s: float = 0.5,
) -> list[float]:
    """Trim leading and trailing silence so edge silence is <= keep_silence_s."""
    if not samples:
        return samples

    frame_len = int(sr * 0.02)  # 20ms
    hop_len = int(sr * 0.01)    # 10ms
    thresh_amp = 10.0 ** (threshold_db / 20.0)

    # Find first active frame
    first_active_sample = 0
    for i in range(0, len(samples) - frame_len, hop_len):
        chunk = samples[i : i + frame_len]
        rms = math.sqrt(sum(x * x for x in chunk) / frame_len)
        if rms >= thresh_amp:
            first_active_sample = i
            break

    # Find last active frame
    last_active_sample = len(samples)
    for i in range(len(samples) - frame_len, 0, -hop_len):
        chunk = samples[i : i + frame_len]
        rms = math.sqrt(sum(x * x for x in chunk) / frame_len)
        if rms >= thresh_amp:
            last_active_sample = i + frame_len
            break

    pad = int(sr * keep_silence_s)
    start_idx = max(0, first_active_sample - pad)
    end_idx = min(len(samples), last_active_sample + pad)

    if start_idx >= end_idx:
        return samples

    return samples[start_idx:end_idx]


def prepare_audio(
    input_path: str | Path,
    output_path: str | Path,
    keep_silence_s: float = 0.5,
    ffmpeg_bin: str | None = None,
) -> dict:
    """Standardize audio: convert to 16 kHz mono WAV, trim edge silence, compute stats."""
    input_path = Path(input_path).resolve()
    output_path = Path(output_path).resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input audio file not found: {input_path}")

    if ffmpeg_bin is None:
        ffmpeg_bin = find_ffmpeg()

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_wav = Path(tmp_dir) / "converted.wav"
        if ffmpeg_bin:
            convert_to_wav_ffmpeg(ffmpeg_bin, input_path, tmp_wav)
            samples, sr = read_wav_samples(tmp_wav)
        else:
            # If input is already wav
            if input_path.suffix.lower() == ".wav":
                samples, sr = read_wav_samples(input_path)
            else:
                raise RuntimeError(
                    f"FFmpeg not found and cannot convert non-WAV format '{input_path.suffix}'."
                )

        # Trim edge silence to keep_silence_s
        trimmed_samples = trim_silence(samples, sr=sr, threshold_db=-42.0, keep_silence_s=keep_silence_s)

        # Write output
        write_wav_samples(output_path, trimmed_samples, framerate=16000)

        stats = compute_audio_stats(trimmed_samples, sr=16000)

    print(f"File:        {output_path.name}")
    print(f"Duration:    {stats['duration_s']}s")
    print(f"Peak level:  {stats['peak_db']} dBFS")
    print(f"Noise floor: {stats['noise_floor_db']} dBFS")
    print(f"Saved:       {output_path}")

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Standardize speech audio into 16 kHz mono WAV with edge silence trimmed."
    )
    parser.add_argument("input", help="Path to input audio/video file (mp3, m4a, mp4, wav)")
    parser.add_argument("--out", "-o", required=True, help="Path to output standardized WAV file")
    parser.add_argument(
        "--silence",
        type=float,
        default=0.5,
        help="Max leading and trailing silence to keep in seconds (default: 0.5s)",
    )
    parser.add_argument("--ffmpeg", help="Custom path to ffmpeg binary")

    args = parser.parse_args()
    prepare_audio(args.input, args.out, keep_silence_s=args.silence, ffmpeg_bin=args.ffmpeg)


if __name__ == "__main__":
    main()
