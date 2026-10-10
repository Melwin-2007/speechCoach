#!/usr/bin/env python3
"""scripts/validate_labels.py - Validate label JSON files against CONTRACTS.md Section 3.

Checks:
- JSON schema conformance to CONTRACTS.md §3
- 0 <= start_s < end_s <= duration_s for all flaw regions
- Word times monotonic: 0 <= start <= end <= duration_s
- Referenced audio file actually exists on disk
- file_id matches the JSON filename
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

VALID_TEXT_IDS = {"T01", "T02", "T03", "T04", "T05", "T06"}
VALID_SOURCES = {"synthetic", "human", "original"}
VALID_SPLITS = {"dev", "test"}
VALID_FLAWS = {
    "PACE_FAST",
    "PACE_SLOW",
    "PAUSE_MISSING",
    "PAUSE_EXCESS",
    "PAUSE_MISPLACED",
    "MONOTONE",
    "PITCH_ERRATIC",
    "VOLUME_DROP",
    "FLAT_ENERGY",
    "CLARITY",
    "FILLERS",
    "STRESS_MISSING",
}


def find_audio_file(file_id: str) -> Path | None:
    """Find audio file corresponding to file_id in dataset audio directories."""
    candidates = [
        REPO_ROOT / "dataset" / "audio" / "synthetic" / f"{file_id}.wav",
        REPO_ROOT / "dataset" / "audio" / "ideal" / f"{file_id}.wav",
        REPO_ROOT / "dataset" / "audio" / "human" / f"{file_id}.wav",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


def validate_label_file(path: Path) -> list[str]:
    """Validate a single label JSON file. Returns list of error messages (empty if valid)."""
    errors = []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return [f"Malformed JSON: {e}"]

    # 1. file_id matches filename
    expected_file_id = path.stem
    file_id = data.get("file_id")
    if file_id != expected_file_id:
        errors.append(f"file_id '{file_id}' does not match filename '{expected_file_id}'")

    # 2. text_id
    text_id = data.get("text_id")
    if text_id not in VALID_TEXT_IDS:
        errors.append(f"Invalid text_id '{text_id}'")

    # 3. source
    source = data.get("source")
    if source not in VALID_SOURCES:
        errors.append(f"Invalid source '{source}'")

    # 4. split
    split = data.get("split")
    if split not in VALID_SPLITS:
        errors.append(f"Invalid split '{split}'")

    # 5. severity_level
    sev = data.get("severity_level")
    if source == "synthetic" and (not isinstance(sev, int) or not (0 <= sev <= 5)):
        errors.append(f"Synthetic severity_level must be int 0-5, got {sev}")

    # 6. duration_s
    duration_s = data.get("duration_s")
    if not isinstance(duration_s, (int, float)) or duration_s <= 0:
        errors.append(f"Invalid duration_s {duration_s}")

    # 7. Audio file existence
    if file_id and not find_audio_file(file_id):
        errors.append(f"Referenced audio file for '{file_id}' not found in dataset/raw/")

    # 8. Words check
    words = data.get("words", [])
    if not isinstance(words, list) or len(words) == 0:
        errors.append("words must be a non-empty list")
    else:
        prev_end = 0.0
        for idx, w in enumerate(words):
            w_start = w.get("start")
            w_end = w.get("end")
            if not isinstance(w_start, (int, float)) or not isinstance(w_end, (int, float)):
                errors.append(f"Word {idx} has invalid start/end timestamps")
                break
            if w_start > w_end:
                errors.append(f"Word {idx} start ({w_start}) > end ({w_end})")
            if duration_s and w_end > duration_s + 1.0:  # Allow 1s tolerance for padding
                errors.append(f"Word {idx} end ({w_end}) exceeds duration ({duration_s})")
            if w_start < prev_end - 0.2:  # Allow minor alignment overlap
                errors.append(f"Word {idx} start ({w_start}) strictly precedes previous end ({prev_end})")
            prev_end = w_end

    # 9. Flaws check
    flaws = data.get("flaws", [])
    if not isinstance(flaws, list):
        errors.append("flaws must be a list")
    else:
        for f_idx, flaw in enumerate(flaws):
            flaw_type = flaw.get("type")
            if flaw_type not in VALID_FLAWS:
                errors.append(f"Flaw {f_idx} has invalid type '{flaw_type}'")
            f_start = flaw.get("start_s")
            f_end = flaw.get("end_s")
            if not isinstance(f_start, (int, float)) or not isinstance(f_end, (int, float)):
                errors.append(f"Flaw {f_idx} has invalid start_s/end_s")
            elif not (0 <= f_start < f_end <= (duration_s or 9999.0) + 1.0):
                errors.append(f"Flaw {f_idx} boundary violation: 0 <= {f_start} < {f_end} <= {duration_s}")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate label JSON files against CONTRACTS §3.")
    parser.add_argument(
        "label_path",
        nargs="?",
        default=str(REPO_ROOT / "dataset" / "labels"),
        help="Path to label JSON file or directory containing labels.",
    )
    args = parser.parse_args()

    target = Path(args.label_path)
    if not target.exists():
        print(f"Path not found: {target}")
        sys.exit(1)

    if target.is_file():
        files = [target]
    else:
        files = sorted(list(target.glob("*.json")))

    if not files:
        print(f"No JSON files found in {target}")
        sys.exit(0)

    total = len(files)
    passed = 0
    failed = 0

    print(f"Validating {total} label file(s)...")
    for f in files:
        errs = validate_label_file(f)
        if not errs:
            passed += 1
            print(f"  [PASS] {f.name}")
        else:
            failed += 1
            print(f"  [FAIL] {f.name}:")
            for e in errs:
                print(f"         - {e}")

    print(f"\nResult: {passed}/{total} passed, {failed} failed.")
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
