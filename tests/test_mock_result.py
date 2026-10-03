import json
import pytest
from scripts.make_mock_result import build_mock_dataset, validate_analysis_result


def test_mock_presets_schema():
    for preset in ["botched", "almost", "ideal"]:
        res = build_mock_dataset(preset=preset, seed=1234)
        validate_analysis_result(res)
        
        # Check series array lengths
        t_len = len(res["series"]["t"])
        assert t_len == 1169  # 58.4s * 20 fps + 1
        for owner in ["participant", "baseline"]:
            for name, arr in res["series"][owner].items():
                assert len(arr) == t_len


def test_mock_botched_flaws():
    res = build_mock_dataset(preset="botched", seed=1234)
    assert len(res["flaws"]) == 5
    flaw_types = [f["type"] for f in res["flaws"]]
    assert "PACE_FAST" in flaw_types
    assert "MONOTONE" in flaw_types
    assert "VOLUME_DROP" in flaw_types
    assert "PAUSE_MISSING" in flaw_types
    assert "FILLERS" in flaw_types
    assert res["scores"]["overall"] < 50.0
    assert len(res["meta"]["warnings"]) == 1


def test_mock_determinism():
    res1 = build_mock_dataset(preset="botched", seed=1234)
    res2 = build_mock_dataset(preset="botched", seed=1234)
    assert json.dumps(res1, sort_keys=True) == json.dumps(res2, sort_keys=True)
