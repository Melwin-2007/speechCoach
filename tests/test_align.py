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
