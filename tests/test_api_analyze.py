import io
import json
import pytest
from fastapi.testclient import TestClient
from speechcoach.api.main import app
from speechcoach.api.models import AnalysisResult

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}

def test_baselines():
    res = client.get("/baselines")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    for item in data:
        assert "id" in item
        assert "title" in item
        assert "n_ideals" in item

def test_demo_presets():
    for preset in ["ideal", "almost", "botched"]:
        res = client.get(f"/demo/{preset}")
        assert res.status_code == 200
        data = res.json()
        # Verify pydantic model parses without error
        result = AnalysisResult.model_validate(data)
        assert result.meta.duration_s > 0
        assert result.scores.overall >= 0
        assert isinstance(result.flaws, list)

def test_demo_audio():
    res = client.get("/demo-audio/botched.wav")
    assert res.status_code == 200
    assert "audio/wav" in res.headers.get("content-type", "")

def test_demo_not_found():
    res = client.get("/demo/invalid_name")
    assert res.status_code == 404
    data = res.json()
    assert "error" in data
    assert "Traceback" not in json.dumps(data)

def test_analyze_empty_transcript():
    fake_wav = io.BytesIO(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00")
    files = {"audio": ("test.wav", fake_wav, "audio/wav")}
    data = {"transcript": "   "}
    res = client.post("/analyze", files=files, data=data)
    assert res.status_code == 400
    res_data = res.json()
    assert "error" in res_data

def test_analyze_oversize_file():
    big_file = io.BytesIO(b"0" * (26 * 1024 * 1024))
    files = {"audio": ("large.wav", big_file, "audio/wav")}
    data = {"transcript": "Where the mind is without fear"}
    res = client.post("/analyze", files=files, data=data)
    assert res.status_code == 413
    res_data = res.json()
    assert "error" in res_data
    assert "exceeds" in res_data["error"] or "25 MB" in res_data["error"]

def test_analyze_success_and_caching():
    # 1 second 16kHz mono 16-bit PCM WAV
    sample_rate = 16000
    num_samples = 16000
    byte_rate = sample_rate * 2
    data_size = num_samples * 2
    riff_size = 36 + data_size
    
    header = bytearray()
    header.extend(b"RIFF")
    header.extend(riff_size.to_bytes(4, "little"))
    header.extend(b"WAVE")
    header.extend(b"fmt ")
    header.extend((16).to_bytes(4, "little")) # PCM format size
    header.extend((1).to_bytes(2, "little"))  # PCM format code
    header.extend((1).to_bytes(2, "little"))  # Mono
    header.extend(sample_rate.to_bytes(4, "little"))
    header.extend(byte_rate.to_bytes(4, "little"))
    header.extend((2).to_bytes(2, "little"))  # Block align
    header.extend((16).to_bytes(2, "little")) # Bits per sample
    header.extend(b"data")
    header.extend(data_size.to_bytes(4, "little"))
    pcm_data = b"\x00\x00" * num_samples
    wav_bytes = bytes(header) + pcm_data

    files = {"audio": ("sample_test.wav", io.BytesIO(wav_bytes), "audio/wav")}
    data = {
        "transcript": "Where the mind is without fear and the head is held high",
        "baseline_id": "T04",
        "mode": "reference"
    }

    # First call: computes and caches
    res1 = client.post("/analyze", files=files, data=data)
    assert res1.status_code == 200
    result1 = res1.json()
    parsed1 = AnalysisResult.model_validate(result1)
    assert parsed1.meta.duration_s > 0
    assert len(parsed1.words) > 0

    # Second call with same payload: hits SHA-256 cache
    files2 = {"audio": ("sample_test.wav", io.BytesIO(wav_bytes), "audio/wav")}
    res2 = client.post("/analyze", files=files2, data=data)
    assert res2.status_code == 200
    result2 = res2.json()
    assert result1 == result2
