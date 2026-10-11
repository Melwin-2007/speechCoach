import pytest
from speechcoach.compare.deviation import CHANNELS
from speechcoach.explain.templates import TEMPLATES, explain

def test_every_channel_has_a_template():
    """Phase 4 Acceptance: Every channel in CHANNELS must have a template in TEMPLATES."""
    for ch in CHANNELS:
        assert ch in TEMPLATES, f"Channel {ch} is missing a template in TEMPLATES"

def test_templates_formatting():
    """Verify that every template can be formatted with typical evidence."""
    for ch in CHANNELS:
        evidence = {
            "flaw": ch,
            "value": 4.5,
            "dev_peak": 3.2,
            "dev_mean": 2.5,
            "direction": "above" if "FAST" in ch or "ERRATIC" in ch or "LONG" in ch else "below",
            "source": "local",
            "unit": "syll/s" if "PACE" in ch else ("semitones" if "PITCH" in ch else "dB"),
            "band": [3.0, 5.0],
            "pct": 25.0
        }
        text = explain(evidence)
        assert text, f"Empty explanation for {ch}"
        assert "3.2" in text or "robust standard deviations" in text
