#!/usr/bin/env python3
"""
scripts/make_mock_result.py
Deterministic mock data generator for SpeechCoach (Member C, Task C1 / Prompt D0a).
Generates contract-valid AnalysisResult JSON (docs/CONTRACTS.md section 6)
and synthetic 16 kHz mono WAVs.
"""

import argparse
import json
import math
import os
from pathlib import Path
import struct
import wave
import numpy as np


SAMPLE_TEXT = (
    "Where the mind is without fear and the head is held high. "
    "Where knowledge is free. "
    "Where the world has not been broken up into fragments by narrow domestic walls. "
    "Where words come out from the depth of truth. "
    "Where tireless striving stretches its arms towards perfection. "
    "Where the clear stream of reason has not lost its way into the dreary desert sand of dead habit. "
    "Where the mind is led forward by thee into ever-widening thought and action. "
    "Into that heaven of freedom, my Father, let my country awake. "
    "We speak not only for ourselves, but for generations yet unborn who look to us for courage, clarity, and truth."
)


def count_syllables(word: str) -> int:
    w = word.lower().strip(".,!?;:")
    if not w:
        return 1
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for char in w:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if w.endswith("e") and count > 1 and not w.endswith("le"):
        count -= 1
    return max(1, count)


def generate_words(text: str, total_duration: float = 58.4, seed: int = 1234) -> list[dict]:
    rng = np.random.RandomState(seed)
    raw_tokens = text.split()
    words = []
    
    # Estimate base durations
    base_durations = []
    pause_after = []
    
    for token in raw_tokens:
        clean_word = token.rstrip(".,!?;:")
        punct = token[len(clean_word):] if len(token) > len(clean_word) else ""
        syl = count_syllables(clean_word)
        # Base speech rate ~4.3 syl/sec
        dur = max(0.16, syl / 4.3 + rng.uniform(-0.03, 0.03))
        base_durations.append(dur)
        
        if punct in [".", "!", "?"]:
            pause_after.append(rng.uniform(0.55, 0.70))
        elif punct in [",", ";", ":"]:
            pause_after.append(rng.uniform(0.30, 0.45))
        else:
            pause_after.append(rng.uniform(0.04, 0.08))
            
    # Scale to fit total_duration with safety margins
    total_raw = sum(base_durations) + sum(pause_after)
    start_margin = 0.8
    end_margin = 0.9
    available_duration = total_duration - start_margin - end_margin
    scale = available_duration / total_raw
    
    current_time = start_margin
    for i, token in enumerate(raw_tokens):
        clean_word = token.rstrip(".,!?;:")
        punct = token[len(clean_word):] if len(token) > len(clean_word) else ""
        dur = round(base_durations[i] * scale, 4)
        start_t = round(current_time, 4)
        end_t = round(start_t + dur, 4)
        conf = round(float(rng.uniform(0.88, 0.98)), 2)
        
        words.append({
            "i": i,
            "w": clean_word.lower(),
            "start": start_t,
            "end": end_t,
            "punct": punct,
            "conf": conf,
            "z": {
                "pace": 0.0,
                "pause": 0.0,
                "pitch": 0.0,
                "energy": 0.0,
                "clarity": 0.0,
            }
        })
        current_time = end_t + (pause_after[i] * scale)
        
    return words


def build_mock_dataset(preset: str = "botched", seed: int = 1234) -> dict:
    duration_s = 58.4
    fps = 20
    num_points = int(round(duration_s * fps)) + 1
    t = [round(i / fps, 4) for i in range(num_points)]
    
    rng = np.random.RandomState(seed)
    words = generate_words(SAMPLE_TEXT, duration_s, seed)
    
    # Baseline series
    # Pitch contour with natural undulating melody
    base_pitch = []
    base_pitch_lo = []
    base_pitch_hi = []
    base_energy = []
    base_rate = []
    
    for time_pt in t:
        # Natural speech baseline
        p_val = math.sin(time_pt * 0.8) * 1.5 + math.cos(time_pt * 0.25) * 0.8
        base_pitch.append(round(p_val, 4))
        base_pitch_lo.append(round(p_val - 1.15, 4))
        base_pitch_hi.append(round(p_val + 1.15, 4))
        
        # Energy baseline (-14 dB average)
        e_val = -14.0 + math.sin(time_pt * 0.5) * 2.5
        base_energy.append(round(e_val, 4))
        
        # Rate baseline ~ 4.1 syl/s
        r_val = 4.1 + math.sin(time_pt * 0.3) * 0.2
        base_rate.append(round(r_val, 4))
        
    # Participant series initialized from baseline
    part_pitch = list(base_pitch)
    part_energy = list(base_energy)
    part_rate = list(base_rate)
    
    # Introduce unvoiced pitch segments (null) ~20%
    for idx, time_pt in enumerate(t):
        # Check if time_pt falls in a pause between words
        in_word = any(w["start"] <= time_pt <= w["end"] for w in words)
        if not in_word or (idx % 9 == 0):
            part_pitch[idx] = None
        else:
            # Small random variation
            part_pitch[idx] = round(part_pitch[idx] + rng.normal(0, 0.2), 4)
            
        part_energy[idx] = round(min(0.0, part_energy[idx] + rng.normal(0, 0.4)), 4)
        part_rate[idx] = round(max(1.0, part_rate[idx] + rng.normal(0, 0.15)), 4)

    flaws = []
    warnings = []
    
    if preset == "botched":
        warnings = ["Some words near 0:49.0 had low alignment confidence due to hesitation sounds."]
        
        # Flaw 1: PACE_FAST (major)
        f1_start, f1_end = 8.5, 16.2
        f1_w_start = next(w["i"] for w in words if w["start"] >= f1_start)
        f1_w_end = next(w["i"] for w in words if w["end"] >= f1_end)
        for i in range(len(t)):
            if f1_start <= t[i] <= f1_end:
                part_rate[i] = round(5.9 + rng.uniform(-0.2, 0.2), 4)
        for w in words[f1_w_start:f1_w_end + 1]:
            w["z"]["pace"] = -4.8
            
        flaws.append({
            "id": 1,
            "type": "PACE_FAST",
            "start": f1_start,
            "end": f1_end,
            "first_word": f1_w_start,
            "last_word": f1_w_end,
            "severity": 0.7333,
            "band": "major",
            "evidence": {"participant": 5.9, "baseline": 4.1, "z": -4.8, "unit": "syl/s"},
            "explanation": {
                "observed": "Speaking rate increased to 5.9 syl/s (baseline 4.1 syl/s).",
                "deviation": "Rushing 44% faster than standard tempo (z = −4.8).",
                "where": "From 0:08.5 to 0:16.2 on 'by narrow domestic walls'.",
                "why": "Rushing compresses important syllables and harms listener comprehension.",
                "fix": "Slow down on key transitions and let phrasing breathe."
            }
        })
        
        # Flaw 2: MONOTONE (major, overlaps Flaw 1 by ~3.2s)
        f2_start, f2_end = 13.0, 22.5
        f2_w_start = next(w["i"] for w in words if w["start"] >= f2_start)
        f2_w_end = next(w["i"] for w in words if w["end"] >= f2_end)
        for i in range(len(t)):
            if f2_start <= t[i] <= f2_end and part_pitch[i] is not None:
                part_pitch[i] = round(0.1 + rng.normal(0, 0.05), 4)
        for w in words[f2_w_start:f2_w_end + 1]:
            w["z"]["pitch"] = -4.6
            
        flaws.append({
            "id": 2,
            "type": "MONOTONE",
            "start": f2_start,
            "end": f2_end,
            "first_word": f2_w_start,
            "last_word": f2_w_end,
            "severity": 0.6889,
            "band": "major",
            "evidence": {"participant": 0.8, "baseline": 2.9, "z": -4.6, "unit": "st"},
            "explanation": {
                "observed": "Pitch variation dropped to 0.8 semitones (baseline 2.9 semitones).",
                "deviation": "Pitch standard deviation is 72% narrower than reference (z = −4.6).",
                "where": "From 0:13.0 to 0:22.5 on 'words come out from the depth of truth'.",
                "why": "Flat pitch creates a monotone delivery that reduces listener engagement.",
                "fix": "Add melodic inflection to content words and key adjectives."
            }
        })
        
        # Flaw 3: VOLUME_DROP (moderate)
        f3_start, f3_end = 27.0, 35.5
        f3_w_start = next(w["i"] for w in words if w["start"] >= f3_start)
        f3_w_end = next(w["i"] for w in words if w["end"] >= f3_end)
        for i in range(len(t)):
            if f3_start <= t[i] <= f3_end:
                part_energy[i] = round(-22.4 + rng.normal(0, 0.5), 4)
        for w in words[f3_w_start:f3_w_end + 1]:
            w["z"]["energy"] = -3.5
            
        flaws.append({
            "id": 3,
            "type": "VOLUME_DROP",
            "start": f3_start,
            "end": f3_end,
            "first_word": f3_w_start,
            "last_word": f3_w_end,
            "severity": 0.4444,
            "band": "moderate",
            "evidence": {"participant": -22.4, "baseline": -13.8, "z": -3.5, "unit": "dB"},
            "explanation": {
                "observed": "Loudness dropped to −22.4 dB (baseline −13.8 dB).",
                "deviation": "Volume dipped 8.6 dB below expected dynamics (z = −3.5).",
                "where": "From 0:27.0 to 0:35.5 on 'dreary desert sand of dead habit'.",
                "why": "Unexpected volume drops make final phrases difficult to hear in larger spaces.",
                "fix": "Maintain breath support through the end of the sentence."
            }
        })
        
        # Flaw 4: PAUSE_MISSING (moderate)
        f4_start, f4_end = 41.2, 45.8
        f4_w_start = next(w["i"] for w in words if w["start"] >= f4_start)
        f4_w_end = next(w["i"] for w in words if w["end"] >= f4_end)
        for w in words[f4_w_start:f4_w_end + 1]:
            w["z"]["pause"] = -3.2
            
        flaws.append({
            "id": 4,
            "type": "PAUSE_MISSING",
            "start": f4_start,
            "end": f4_end,
            "first_word": f4_w_start,
            "last_word": f4_w_end,
            "severity": 0.3778,
            "band": "moderate",
            "evidence": {"participant": 0.08, "baseline": 0.55, "z": -3.2, "unit": "s"},
            "explanation": {
                "observed": "Pause duration was 0.08 s (baseline 0.55 s).",
                "deviation": "Punctuation pause was 0.47 s shorter than reference (z = −3.2).",
                "where": "From 0:41.2 to 0:45.8 across the semicolon break.",
                "why": "Skipping structural pauses prevents listeners from absorbing the previous point.",
                "fix": "Take a full breath and pause deliberately for at least half a second at major punctuation."
            }
        })
        
        # Flaw 5: FILLERS (minor)
        f5_start, f5_end = 49.0, 51.5
        f5_w_start = next(w["i"] for w in words if w["start"] >= f5_start)
        f5_w_end = next(w["i"] for w in words if w["end"] >= f5_end)
        for w in words[f5_w_start:f5_w_end + 1]:
            w["z"]["clarity"] = -2.3
            
        flaws.append({
            "id": 5,
            "type": "FILLERS",
            "start": f5_start,
            "end": f5_end,
            "first_word": f5_w_start,
            "last_word": f5_w_end,
            "severity": 0.1778,
            "band": "minor",
            "evidence": {"participant": 2.0, "baseline": 0.0, "z": 2.3, "unit": "count"},
            "explanation": {
                "observed": "Detected 2 filler vocalizations ('um' / 'uh').",
                "deviation": "Hesitation sounds detected during thought transition (z = +2.3).",
                "where": "From 0:49.0 to 0:51.5 before 'let my country awake'.",
                "why": "Filler sounds distract from your authority and disrupt speaking flow.",
                "fix": "Replace vocalized fillers with silent pauses when searching for the next phrase."
            }
        })
        
        scores = {
            "overall": 42.1,
            "dimensions": {
                "pacing": 38.0,
                "pausing": 46.0,
                "pitch": 35.0,
                "energy": 44.0,
                "emphasis": 48.0,
                "clarity": 52.0,
                "fluency": 39.0
            }
        }
        
    elif preset == "almost":
        # Single minor flaw
        f1_start, f1_end = 12.0, 17.5
        f1_w_start = next(w["i"] for w in words if w["start"] >= f1_start)
        f1_w_end = next(w["i"] for w in words if w["end"] >= f1_end)
        for i in range(len(t)):
            if f1_start <= t[i] <= f1_end:
                part_rate[i] = round(5.1 + rng.uniform(-0.1, 0.1), 4)
        for w in words[f1_w_start:f1_w_end + 1]:
            w["z"]["pace"] = -2.4
            
        flaws.append({
            "id": 1,
            "type": "PACE_FAST",
            "start": f1_start,
            "end": f1_end,
            "first_word": f1_w_start,
            "last_word": f1_w_end,
            "severity": 0.2000,
            "band": "minor",
            "evidence": {"participant": 5.1, "baseline": 4.1, "z": -2.4, "unit": "syl/s"},
            "explanation": {
                "observed": "Speaking rate increased to 5.1 syl/s (baseline 4.1 syl/s).",
                "deviation": "Slight rush through the clause (z = −2.4).",
                "where": "From 0:12.0 to 0:17.5 on 'narrow domestic walls'.",
                "why": "Minor acceleration slightly rushed the transition.",
                "fix": "Pace the phrase steadily to keep full clarity."
            }
        })
        scores = {
            "overall": 88.4,
            "dimensions": {
                "pacing": 82.0,
                "pausing": 91.0,
                "pitch": 92.0,
                "energy": 90.0,
                "emphasis": 87.0,
                "clarity": 93.0,
                "fluency": 94.0
            }
        }
    else:  # ideal
        flaws = []
        scores = {
            "overall": 94.2,
            "dimensions": {
                "pacing": 94.0,
                "pausing": 96.0,
                "pitch": 93.0,
                "energy": 95.0,
                "emphasis": 92.0,
                "clarity": 96.0,
                "fluency": 97.0
            }
        }

    # Ensure flaws are sorted by start time
    flaws = sorted(flaws, key=lambda x: x["start"])

    result = {
        "meta": {
            "mode": "reference",
            "baseline_id": "T4",
            "duration_s": duration_s,
            "version": "1.0",
            "warnings": warnings
        },
        "words": words,
        "series": {
            "t": t,
            "participant": {
                "pitch_st": part_pitch,
                "energy_db": part_energy,
                "rate_sps": part_rate
            },
            "baseline": {
                "pitch_st": base_pitch,
                "pitch_lo": base_pitch_lo,
                "pitch_hi": base_pitch_hi,
                "energy_db": base_energy,
                "rate_sps": base_rate
            }
        },
        "flaws": flaws,
        "scores": scores
    }
    
    return result


def validate_analysis_result(res: dict) -> None:
    assert "meta" in res, "Missing meta key"
    assert "words" in res, "Missing words key"
    assert "series" in res, "Missing series key"
    assert "flaws" in res, "Missing flaws key"
    assert "scores" in res, "Missing scores key"
    
    t = res["series"]["t"]
    n_t = len(t)
    assert n_t > 0, "series.t cannot be empty"
    
    # Check all series array lengths
    for owner in ["participant", "baseline"]:
        for k, v in res["series"][owner].items():
            assert len(v) == n_t, f"series.{owner}.{k} length ({len(v)}) != series.t length ({n_t})"
            
    dur = res["meta"]["duration_s"]
    for w in res["words"]:
        assert 0.0 <= w["start"] < w["end"] <= dur, f"Word {w['w']} time bounds invalid: [{w['start']}, {w['end']}] vs {dur}"
        
    for idx, f in enumerate(res["flaws"]):
        assert 0.0 <= f["start"] < f["end"] <= dur, f"Flaw {f['id']} out of bounds"
        assert 0 <= f["first_word"] <= f["last_word"] < len(res["words"]), f"Flaw {f['id']} word index invalid"
        if idx > 0:
            assert f["start"] >= res["flaws"][idx - 1]["start"], "Flaws must be sorted by start time"
            
    assert 0.0 <= res["scores"]["overall"] <= 100.0, "Overall score out of 0-100 range"
    for d, s in res["scores"]["dimensions"].items():
        assert 0.0 <= s <= 100.0, f"Dimension {d} score {s} out of range"


def generate_audio_wav(result: dict, out_path: str, sample_rate: int = 16000) -> None:
    duration_s = result["meta"]["duration_s"]
    num_samples = int(duration_s * sample_rate)
    audio = np.zeros(num_samples, dtype=np.float32)
    
    t_series = np.array(result["series"]["t"])
    p_pitch = result["series"]["participant"]["pitch_st"]
    p_energy = np.array(result["series"]["participant"]["energy_db"])
    
    # Render audio words
    for w in result["words"]:
        start_idx = int(w["start"] * sample_rate)
        end_idx = min(num_samples, int(w["end"] * sample_rate))
        if start_idx >= end_idx:
            continue
            
        seg_len = end_idx - start_idx
        seg_t = np.linspace(w["start"], w["end"], seg_len, endpoint=False)
        
        # Interpolate pitch and energy
        # Default pitch 150 Hz if unvoiced
        idx_mid = int(np.searchsorted(t_series, (w["start"] + w["end"]) / 2.0))
        idx_mid = min(len(p_pitch) - 1, max(0, idx_mid))
        
        st_val = p_pitch[idx_mid]
        if st_val is None:
            st_val = 0.0
        f0 = 150.0 * (2.0 ** (st_val / 12.0))
        
        db_val = p_energy[idx_mid]
        amp = max(0.01, min(0.9, 10.0 ** (db_val / 20.0)))
        
        # Harmonic synthesis (rich tone)
        phase = 2.0 * np.pi * f0 * seg_t
        signal = (0.5 * np.sin(phase) + 
                  0.3 * np.sin(2.0 * phase) + 
                  0.15 * np.sin(3.0 * phase) +
                  0.05 * np.sin(4.0 * phase))
                  
        # Apply 15 ms envelope fade-in / fade-out
        fade_len = min(seg_len // 2, int(0.015 * sample_rate))
        envelope = np.ones(seg_len, dtype=np.float32)
        if fade_len > 0:
            fade = np.linspace(0.0, 1.0, fade_len)
            envelope[:fade_len] = fade
            envelope[-fade_len:] = fade[::-1]
            
        audio[start_idx:end_idx] = signal * amp * envelope
        
    # Add quiet comfort dither
    dither = np.random.RandomState(42).normal(0.0, 0.0005, num_samples).astype(np.float32)
    audio = np.clip(audio + dither, -1.0, 1.0)
    
    # Write 16-bit PCM WAV
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    audio_int16 = (audio * 32767.0).astype(np.int16)
    
    with wave.open(out_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())


def main():
    parser = argparse.ArgumentParser(description="Generate deterministic mock AnalysisResult and audio for SpeechCoach.")
    parser.add_argument("--preset", choices=["botched", "almost", "ideal"], default="botched", help="Mock preset")
    parser.add_argument("--out", required=True, help="Output JSON path")
    parser.add_argument("--audio", help="Optional output WAV path")
    parser.add_argument("--seed", type=int, default=1234, help="Random seed for determinism")
    
    args = parser.parse_args()
    
    result = build_mock_dataset(preset=args.preset, seed=args.seed)
    validate_analysis_result(result)
    
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True)
        
    if args.audio:
        generate_audio_wav(result, args.audio)
        
    print(f"[{args.preset}] Generated {out_path} | Words: {len(result['words'])}, Flaws: {len(result['flaws'])} ({[f['type'] for f in result['flaws']]}), Overall: {result['scores']['overall']}, Series t: {len(result['series']['t'])}")


if __name__ == "__main__":
    main()
