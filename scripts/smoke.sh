#!/usr/bin/env bash
set -e

echo "=== SpeechCoach Smoke Test (Day 1 / Task C1) ==="

# 1. Verify mock data generation
echo "[1/3] Verifying mock data generator..."
python scripts/make_mock_result.py --preset botched --out app/public/mock_result.json
python scripts/make_mock_result.py --preset ideal --out app/public/demo/ideal.json
python scripts/make_mock_result.py --preset almost --out app/public/demo/almost.json

# 2. Run API & Mock tests
echo "[2/3] Running pytest test suite..."
pytest tests/test_health.py tests/test_mock_result.py

# 3. Check design linter
echo "[3/3] Checking design system compliance..."
cd app && node scripts/check-design.mjs

echo "=== All smoke checks passed successfully! ==="
