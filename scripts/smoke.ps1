Write-Host "=== SpeechCoach Smoke Test (Day 1 / Task C1) ==="

Write-Host "[1/3] Verifying mock data generator..."
python scripts/make_mock_result.py --preset botched --out app/public/mock_result.json
python scripts/make_mock_result.py --preset ideal --out app/public/demo/ideal.json
python scripts/make_mock_result.py --preset almost --out app/public/demo/almost.json

Write-Host "[2/3] Running pytest test suite..."
pytest tests/test_health.py tests/test_mock_result.py

Write-Host "[3/3] Checking design system compliance..."
Push-Location app
node scripts/check-design.mjs
Pop-Location

Write-Host "=== All smoke checks passed successfully! ==="
