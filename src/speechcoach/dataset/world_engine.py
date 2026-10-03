"""speechcoach.dataset.world_engine - WORLD vocoder analysis, synthesis, and flaw injection.

Implements the frozen CONTRACTS.md Section 5 interfaces:
- analyze_world(y) -> tuple[np.ndarray, np.ndarray, np.ndarray]
- inject(base_file_id, flaw, level, seed) -> tuple[np.ndarray, dict]
"""

import argparse
import hashlib
import json
import logging
import math
import random
from pathlib import Path
from typing import Any

import numpy as np
import pyworld as pw
import scipy.interpolate
import yaml
import soundfile as sf

from speechcoach.audio.io import load_audio

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def stable_hash(text: str) -> int:
    """Return a deterministic integer seed offset from a string."""
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)


def analyze_world(
    y: np.ndarray,
    fs: int = 16000,
    cache_path: Path | None = None,
    f0_floor: float = 60.0,
    f0_ceil: float = 600.0,
    frame_period: float = 5.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Extract F0, spectral envelope (sp), and aperiodicity (ap) using pyworld.
    
    Caches analysis to .npz file if cache_path is provided.
    """
    if cache_path and cache_path.exists():
        data = np.load(cache_path)
        return data["f0"], data["sp"], data["ap"]

    x = np.ascontiguousarray(y, dtype=np.float64)

    # 1. F0 estimation with Harvest
    f0, temporal_positions = pw.harvest(
        x,
        fs,
        f0_floor=f0_floor,
        f0_ceil=f0_ceil,
        frame_period=frame_period,
    )

    # 2. Spectral envelope with CheapTrick
    sp = pw.cheaptrick(x, f0, temporal_positions, fs)

    # 3. Aperiodicity with D4C
    ap = pw.d4c(x, f0, temporal_positions, fs)

    if cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(cache_path, f0=f0, sp=sp, ap=ap)

    return f0, sp, ap


def render_time_program(
    f0: np.ndarray,
    sp: np.ndarray,
    ap: np.ndarray,
    fs: int,
    start_s: float,
    end_s: float,
    speed: float,
    frame_period: float = 5.0,
) -> tuple[np.ndarray, float, float]:
    """
    Speed up or slow down a time region [start_s, end_s] by factor 'speed'.
    
    Returns:
        tuple: (synthesized_audio, new_start_s, new_end_s)
    """
    hop_s = frame_period / 1000.0
    n_frames = len(f0)
    orig_duration_s = (n_frames - 1) * hop_s

    if speed == 1.0 or start_s >= end_s:
        y_synth = pw.synthesize(f0, sp, ap, fs, frame_period=frame_period)
        return y_synth.astype(np.float32), start_s, end_s

    orig_region_dur = end_s - start_s
    new_region_dur = orig_region_dur / speed
    duration_delta = orig_region_dur - new_region_dur
    new_total_duration_s = orig_duration_s - duration_delta

    new_timeaxis = np.arange(0.0, new_total_duration_s, hop_s)
    orig_timeaxis = np.arange(0.0, n_frames * hop_s, hop_s)[:n_frames]

    # Map each new timestamp to original timestamp
    def map_new_to_source(t_new: float) -> float:
        if t_new < start_s:
            return t_new
        elif t_new < start_s + new_region_dur:
            return start_s + (t_new - start_s) * speed
        else:
            return end_s + (t_new - (start_s + new_region_dur))

    source_t = np.array([map_new_to_source(t) for t in new_timeaxis])
    source_t = np.clip(source_t, 0.0, orig_timeaxis[-1])

    # Interpolate vocoder features
    f0_interp = scipy.interpolate.interp1d(
        orig_timeaxis, f0, kind="nearest", fill_value="extrapolate"
    )(source_t)

    sp_interp = scipy.interpolate.interp1d(
        orig_timeaxis, sp, axis=0, kind="linear", fill_value="extrapolate"
    )(source_t)

    ap_interp = scipy.interpolate.interp1d(
        orig_timeaxis, ap, axis=0, kind="linear", fill_value="extrapolate"
    )(source_t)

    y_synth = pw.synthesize(f0_interp, sp_interp, ap_interp, fs, frame_period=frame_period)

    new_start_s = start_s
    new_end_s = start_s + new_region_dur

    return y_synth.astype(np.float32), new_start_s, new_end_s


def map_word_times(
    words: list[dict],
    start_s: float,
    end_s: float,
    speed: float,
) -> list[dict]:
    """Map word boundary timestamps through the time modification program."""
    orig_region_dur = end_s - start_s
    new_region_dur = orig_region_dur / speed
    duration_delta = orig_region_dur - new_region_dur

    mapped_words = []
    for w in words:
        w_start = w["start"]
        w_end = w["end"]

        # Map start
        if w_start <= start_s:
            mapped_start = w_start
        elif w_start < end_s:
            mapped_start = start_s + (w_start - start_s) / speed
        else:
            mapped_start = w_start - duration_delta

        # Map end
        if w_end <= start_s:
            mapped_end = w_end
        elif w_end < end_s:
            mapped_end = start_s + (w_end - start_s) / speed
        else:
            mapped_end = w_end - duration_delta

        mapped_words.append({
            "i": w["i"],
            "raw": w["raw"],
            "norm": w["norm"],
            "punct": w["punct"],
            "start": round(max(0.0, mapped_start), 3),
            "end": round(max(0.0, mapped_end), 3),
            "conf": w.get("conf", 1.0),
        })

    return mapped_words


def inject(
    base_file_id: str,
    flaw: str,
    level: int,
    seed: int = 42,
) -> tuple[np.ndarray, dict]:
    """
    Inject a flaw into a base recording per CONTRACTS.md Section 5.
    
    Args:
        base_file_id: Identifier of the base ideal recording (e.g. 'T4__orig-lincoln__ideal')
        flaw: Flaw type (e.g. 'PACE_FAST' or 'resynth_control')
        level: Severity level 0 to 5 (0 = control)
        seed: Master random seed
        
    Returns:
        tuple[np.ndarray, dict]: (audio array float32, label dict per CONTRACTS §3)
    """
    # Parse base_file_id
    parts = base_file_id.split("__")
    text_id = parts[0]
    base_speaker = parts[1]

    # Load configurations
    flaws_cfg_path = REPO_ROOT / "configs" / "flaws.yaml"
    with open(flaws_cfg_path, "r", encoding="utf-8") as f:
        flaws_cfg = yaml.safe_load(f)

    # Audio & Alignment paths
    audio_path = REPO_ROOT / "dataset" / "audio" / "ideal" / f"{base_file_id}.wav"
    if not audio_path.exists():
        raise FileNotFoundError(f"Base audio file not found: {audio_path}")

    align_path = REPO_ROOT / "dataset" / "alignments" / f"{base_file_id}.json"
    if not align_path.exists():
        raise FileNotFoundError(f"Base alignment file not found: {align_path}")

    with open(align_path, "r", encoding="utf-8") as f:
        align_data = json.load(f)

    words = align_data["words"]
    y = load_audio(audio_path, sr=16000, target_lufs=-23.0)
    fs = 16000

    # WORLD cache
    cache_path = REPO_ROOT / "data" / "interim" / f"{base_file_id}.npz"
    f0, sp, ap = analyze_world(y, fs=fs, cache_path=cache_path)

    # Derive variant and target file_id
    if level == 0 or flaw == "resynth_control":
        variant = "resynth_control"
        synth_flaw_type = None
    else:
        variant = f"{flaw}_L{level}"
        synth_flaw_type = flaw

    target_file_id = f"{text_id}__synth-{base_speaker}__{variant}"

    # Deterministic file seed
    file_seed = seed + stable_hash(target_file_id)
    rng = random.Random(file_seed)

    # Determine split
    split = "test" if text_id in ["T3", "T6"] else "dev"

    if level == 0 or flaw == "resynth_control":
        # Pass through WORLD with no modifications
        y_synth = pw.synthesize(f0, sp, ap, fs, frame_period=5.0).astype(np.float32)
        duration_s = round(float(len(y_synth) / fs), 2)
        flaws_list = []
        new_words = [{**w, "conf": round(w.get("conf", 1.0), 3)} for w in words]
    else:
        if flaw == "PACE_FAST":
            speed_params = flaws_cfg["params"]["PACE_FAST"]["speed"]
            speed = float(speed_params[level - 1])
            extent_fractions = flaws_cfg["extent_fraction"]
            extent_frac = float(extent_fractions[level - 1])

            # Select region starting at a phrase boundary (word following punct or word 0)
            phrase_starts = [0]
            for i, w in enumerate(words[:-1]):
                if w.get("punct"):
                    phrase_starts.append(i + 1)

            total_duration_s = float(len(y) / fs)
            target_dur = total_duration_s * extent_frac

            # Pick suitable start from phrase_starts
            valid_starts = [
                idx for idx in phrase_starts
                if words[idx]["start"] + target_dur <= total_duration_s
            ]
            first_word_idx = rng.choice(valid_starts) if valid_starts else phrase_starts[0]

            # Find last word to cover target_dur
            start_s = words[first_word_idx]["start"]
            target_end_s = start_s + target_dur

            last_word_idx = first_word_idx
            for i in range(first_word_idx, len(words)):
                if words[i]["end"] >= target_end_s:
                    last_word_idx = i
                    break
                last_word_idx = i

            end_s = words[last_word_idx]["end"]

            # Render audio
            y_synth, new_start_s, new_end_s = render_time_program(
                f0, sp, ap, fs, start_s, end_s, speed, frame_period=5.0
            )
            duration_s = round(float(len(y_synth) / fs), 2)

            # Map words
            new_words = map_word_times(words, start_s, end_s, speed)

            flaws_list = [
                {
                    "type": "PACE_FAST",
                    "start_s": round(new_start_s, 2),
                    "end_s": round(new_end_s, 2),
                    "first_word": first_word_idx,
                    "last_word": last_word_idx,
                    "params": {"speed": speed},
                }
            ]
        elif flaw == "PACE_SLOW":
            speed_params = flaws_cfg["params"]["PACE_SLOW"]["speed"]
            speed = float(speed_params[level - 1])
            extent_fractions = flaws_cfg["extent_fraction"]
            extent_frac = float(extent_fractions[level - 1])

            phrase_starts = [0]
            for i, w in enumerate(words[:-1]):
                if w.get("punct"):
                    phrase_starts.append(i + 1)

            total_duration_s = float(len(y) / fs)
            target_dur = total_duration_s * extent_frac

            valid_starts = [
                idx for idx in phrase_starts
                if words[idx]["start"] + target_dur <= total_duration_s
            ]
            first_word_idx = rng.choice(valid_starts) if valid_starts else phrase_starts[0]

            start_s = words[first_word_idx]["start"]
            target_end_s = start_s + target_dur

            last_word_idx = first_word_idx
            for i in range(first_word_idx, len(words)):
                if words[i]["end"] >= target_end_s:
                    last_word_idx = i
                    break
                last_word_idx = i

            end_s = words[last_word_idx]["end"]

            y_synth, new_start_s, new_end_s = render_time_program(
                f0, sp, ap, fs, start_s, end_s, speed, frame_period=5.0
            )
            duration_s = round(float(len(y_synth) / fs), 2)
            new_words = map_word_times(words, start_s, end_s, speed)

            flaws_list = [
                {
                    "type": "PACE_SLOW",
                    "start_s": round(new_start_s, 2),
                    "end_s": round(new_end_s, 2),
                    "first_word": first_word_idx,
                    "last_word": last_word_idx,
                    "params": {"speed": speed},
                }
            ]
        elif flaw == "MONOTONE":
            alpha_params = flaws_cfg["params"]["MONOTONE"]["alpha"]
            alpha = float(alpha_params[level - 1])
            extent_fractions = flaws_cfg["extent_fraction"]
            extent_frac = float(extent_fractions[level - 1])

            phrase_starts = [0]
            for i, w in enumerate(words[:-1]):
                if w.get("punct"):
                    phrase_starts.append(i + 1)

            total_duration_s = float(len(y) / fs)
            target_dur = total_duration_s * extent_frac

            valid_starts = [
                idx for idx in phrase_starts
                if words[idx]["start"] + target_dur <= total_duration_s
            ]
            first_word_idx = rng.choice(valid_starts) if valid_starts else phrase_starts[0]

            start_s = words[first_word_idx]["start"]
            target_end_s = start_s + target_dur

            last_word_idx = first_word_idx
            for i in range(first_word_idx, len(words)):
                if words[i]["end"] >= target_end_s:
                    last_word_idx = i
                    break
                last_word_idx = i

            end_s = words[last_word_idx]["end"]

            hop_s = 0.005
            n_frames = len(f0)
            frame_times = np.arange(n_frames) * hop_s

            voiced_f0 = f0[f0 > 0]
            ref_f0 = float(np.median(voiced_f0)) if len(voiced_f0) > 0 else 120.0
            log_ref = math.log(max(ref_f0, 1.0))

            f0_mod = f0.copy()
            in_region = (frame_times >= start_s) & (frame_times <= end_s) & (f0 > 0)
            f0_mod[in_region] = np.exp(log_ref + alpha * (np.log(f0[in_region]) - log_ref))

            y_synth = pw.synthesize(f0_mod, sp, ap, fs, frame_period=5.0).astype(np.float32)
            duration_s = round(float(len(y_synth) / fs), 2)
            new_words = [{**w, "conf": round(w.get("conf", 1.0), 3)} for w in words]

            flaws_list = [
                {
                    "type": "MONOTONE",
                    "start_s": round(start_s, 2),
                    "end_s": round(end_s, 2),
                    "first_word": first_word_idx,
                    "last_word": last_word_idx,
                    "params": {"alpha": alpha},
                }
            ]
        elif flaw == "VOLUME_DROP":
            gain_params = flaws_cfg["params"]["VOLUME_DROP"]["gain_db"]
            gain_db = float(gain_params[level - 1])
            gain_factor = 10.0 ** (gain_db / 20.0)
            extent_fractions = flaws_cfg["extent_fraction"]
            extent_frac = float(extent_fractions[level - 1])

            total_duration_s = float(len(y) / fs)
            target_dur = total_duration_s * extent_frac
            target_start_s = max(0.0, total_duration_s - target_dur)

            first_word_idx = 0
            for i, w in enumerate(words):
                if w["start"] >= target_start_s:
                    first_word_idx = i
                    break
            last_word_idx = len(words) - 1

            start_s = words[first_word_idx]["start"]
            end_s = words[last_word_idx]["end"]

            y_raw = pw.synthesize(f0, sp, ap, fs, frame_period=5.0)

            envelope = np.ones(len(y_raw), dtype=np.float32)
            fade_samples = int(fs * 0.200)  # 200 ms fade-in
            drop_start_sample = int(start_s * fs)

            if drop_start_sample < len(envelope):
                fade_len = min(fade_samples, len(envelope) - drop_start_sample)
                fade = np.linspace(1.0, gain_factor, fade_len, dtype=np.float32)
                envelope[drop_start_sample : drop_start_sample + fade_len] = fade
                envelope[drop_start_sample + fade_len :] = gain_factor

            y_synth = (y_raw * envelope).astype(np.float32)
            duration_s = round(float(len(y_synth) / fs), 2)
            new_words = [{**w, "conf": round(w.get("conf", 1.0), 3)} for w in words]

            flaws_list = [
                {
                    "type": "VOLUME_DROP",
                    "start_s": round(start_s, 2),
                    "end_s": round(end_s, 2),
                    "first_word": first_word_idx,
                    "last_word": last_word_idx,
                    "params": {"gain_db": gain_db},
                }
            ]
        else:
            raise NotImplementedError(f"Flaw type '{flaw}' not yet implemented.")


    label_dict = {
        "file_id": target_file_id,
        "text_id": text_id,
        "source": "synthetic",
        "base_file_id": base_file_id,
        "reference_file_ids": [base_file_id],
        "severity_level": level,
        "split": split,
        "duration_s": duration_s,
        "flaws": flaws_list,
        "words": new_words,
        "license": "Public Domain / CC0 derivative",
    }

    return y_synth, label_dict


def main():
    parser = argparse.ArgumentParser(description="WORLD Vocoder Engine and Flaw Injector.")
    parser.add_argument("--text", default="T4", help="Text ID to generate (default: T4)")
    parser.add_argument("--base-speaker", default="orig-lincoln", help="Base speaker ID (default: orig-lincoln)")
    parser.add_argument("--flaw", default="PACE_FAST", help="Flaw type (default: PACE_FAST)")
    parser.add_argument("--levels", default="1,2,3,4,5", help="Comma-separated levels to generate")
    parser.add_argument("--with-control", action="store_true", default=True, help="Include resynth_control (L0)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")

    args = parser.parse_args()

    levels = [int(x.strip()) for x in args.levels.split(",") if x.strip()]
    if args.with_control and 0 not in levels:
        levels = [0] + levels

    base_file_id = f"{args.text}__{args.base_speaker}__ideal"
    print(f"Base file: {base_file_id}")

    synth_audio_dir = REPO_ROOT / "dataset" / "audio" / "synthetic"
    synth_audio_dir.mkdir(parents=True, exist_ok=True)

    labels_dir = REPO_ROOT / "dataset" / "labels"
    labels_dir.mkdir(parents=True, exist_ok=True)

    for lvl in levels:
        flaw_name = "resynth_control" if lvl == 0 else args.flaw
        print(f"Generating {flaw_name} (Level {lvl})...")
        y_synth, label_data = inject(base_file_id, flaw_name, lvl, seed=args.seed)

        target_file_id = label_data["file_id"]
        out_wav = synth_audio_dir / f"{target_file_id}.wav"
        out_label = labels_dir / f"{target_file_id}.json"

        # Save WAV
        sf.write(str(out_wav), y_synth, 16000, subtype="PCM_16")

        # Save Label
        with open(out_label, "w", encoding="utf-8") as f:
            json.dump(label_data, f, indent=2)

        print(f"  Saved WAV:   {out_wav.name} ({label_data['duration_s']}s)")
        print(f"  Saved Label: {out_label.name} ({len(label_data['flaws'])} flaws)")


if __name__ == "__main__":
    main()
