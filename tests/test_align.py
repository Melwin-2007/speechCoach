import pytest
from speechcoach.align.transcript import parse_transcript

def test_parse_transcript_basic():
    text = "Hello, world!"
    words = parse_transcript(text)
    
    # According to CONTRACTS section 1 and 5
    assert len(words) == 2
    assert words[0] == {"i": 0, "raw": "Hello,", "norm": "hello", "punct": ","}
    assert words[1] == {"i": 1, "raw": "world!", "norm": "world", "punct": "!"}

def test_parse_transcript_no_punct():
    text = "Ask not"
    words = parse_transcript(text)
    
    assert len(words) == 2
    assert words[0] == {"i": 0, "raw": "Ask", "norm": "ask", "punct": ""}
    assert words[1] == {"i": 1, "raw": "not", "norm": "not", "punct": ""}

def test_proportional_align_fallback():
    import numpy as np
    from speechcoach.align.aligner import _proportional_align
    words = parse_transcript("Hello, this is a test.")
    y = np.ones(32000, dtype=np.float32) * 0.1  # 2.0s audio
    aligned = _proportional_align(y, words)
    assert len(aligned) == len(words)
    assert aligned[0]["start"] >= 0.0
    assert aligned[-1]["end"] <= 2.0
    assert all("start" in w and "end" in w and "conf" in w for w in aligned)

def test_proportional_align_silent_raises():
    import numpy as np
    from speechcoach.align.aligner import _proportional_align
    words = parse_transcript("Hello")
    y_silent = np.zeros(16000, dtype=np.float32)
    with pytest.raises(ValueError, match="silent or inaudible"):
        _proportional_align(y_silent, words)
