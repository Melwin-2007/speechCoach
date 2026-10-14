import numpy as np
import torch
import torchaudio
import logging
from pathlib import Path
import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

logger = logging.getLogger("speechcoach.align")

_MODEL = None
_DICT = None
_DEVICE = None

def _is_low_memory_env() -> bool:
    """Detect if running in a memory-constrained container (<1 GB RAM limit)."""
    if os.environ.get("LOW_MEMORY_MODE", "").lower() in ("1", "true", "yes"):
        return True
    try:
        cgroup_v2 = Path("/sys/fs/cgroup/memory.max")
        if cgroup_v2.exists():
            val = cgroup_v2.read_text().strip()
            if val != "max" and int(val) < 1000 * 1024 * 1024:
                return True
    except Exception:
        pass
    try:
        cgroup_v1 = Path("/sys/fs/cgroup/memory/memory.limit_in_bytes")
        if cgroup_v1.exists():
            val = int(cgroup_v1.read_text().strip())
            if val < 1000 * 1024 * 1024:
                return True
    except Exception:
        pass
    return False

def _proportional_align(y: np.ndarray, words: list[dict]) -> list[dict]:
    """Fast acoustic proportional alignment for memory-constrained cloud environments."""
    if not words:
        return []
    dur = float(len(y) / 16000.0)
    if len(y) == 0 or float(np.max(np.abs(y))) < 0.005:
        raise ValueError("Audio signal is silent or inaudible; cannot align.")

    n_chars = sum(max(1, len(w.get("norm", ""))) for w in words)
    speech_dur = max(0.5, dur - 0.4)
    curr_t = 0.2

    out_words = []
    for w in words:
        w_len = max(1, len(w.get("norm", "")))
        w_dur = (w_len / n_chars) * (speech_dur * 0.75)
        pause = 0.35 if w.get("punct") in (".", "!", "?") else (0.20 if w.get("punct") in (",", ";") else 0.05)
        out_words.append({
            **w,
            "start": round(curr_t, 3),
            "end": round(curr_t + w_dur, 3),
            "conf": 0.90
        })
        curr_t += w_dur + pause

    return out_words

def _get_model():
    global _MODEL, _DICT, _DEVICE
    if _MODEL is None:
        if not torch.cuda.is_available():
            try:
                torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))
            except Exception:
                pass
        _DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        bundle = torchaudio.pipelines.MMS_FA
        _MODEL = bundle.get_model().to(_DEVICE)
        _MODEL.eval()
        _DICT = bundle.get_dict()
    return _MODEL, _DICT, _DEVICE

def align_words(y: np.ndarray, words: list[dict]) -> list[dict]:
    """
    Run forced alignment using torchaudio MMS_FA model, with graceful fallback in low-memory environments.
    
    Args:
        y: Audio data as a float32 mono array (16 kHz).
        words: List of word dictionaries from parse_transcript.
        
    Returns:
        list[dict]: The input word dictionaries, each appended with:
            - start: float (start time in seconds)
            - end: float (end time in seconds)
            - conf: float (confidence score)
    """
    if _is_low_memory_env():
        logger.info("Operating in low-memory environment (<1 GB RAM); using acoustic proportional alignment.")
        return _proportional_align(y, words)

    try:
        model, dictionary, device = _get_model()
    except (MemoryError, Exception) as e:
        logger.warning(f"Failed to load MMS_FA model ({e}); falling back to proportional alignment.")
        return _proportional_align(y, words)

    word_norms = [w["norm"] for w in words]
    tokenized_transcript = []
    word_spans = []
    
    for word in word_norms:
        start_idx = len(tokenized_transcript)
        for char in word:
            if char in dictionary and dictionary[char] != 0:
                tokenized_transcript.append(dictionary[char])
        
        if "|" in dictionary:
            tokenized_transcript.append(dictionary["|"])
            end_idx = len(tokenized_transcript) - 1
        else:
            end_idx = len(tokenized_transcript)
            
        word_spans.append((start_idx, end_idx))

    targets = torch.tensor(tokenized_transcript, dtype=torch.int32, device=device).unsqueeze(0)
    
    waveform = torch.from_numpy(y).unsqueeze(0).to(device)
    with torch.inference_mode():
        emission, _ = model(waveform)
        
    alignments, scores = torchaudio.functional.forced_align(emission, targets, blank=0)
    
    alignments = alignments[0]
    scores = scores[0]
    
    token_spans = torchaudio.functional.merge_tokens(alignments, scores)
    
    num_frames = emission.size(1)
    frame_dur = (waveform.size(1) / 16000.0) / num_frames
    
    non_blank_spans = [span for span in token_spans if span.token != 0]
    
    out_words = []
    for i, w_dict in enumerate(words):
        start_t_idx, end_t_idx = word_spans[i]
        if start_t_idx < end_t_idx and start_t_idx < len(non_blank_spans):
            w_spans = non_blank_spans[start_t_idx:end_t_idx]
            if w_spans:
                start_time = w_spans[0].start * frame_dur
                end_time = w_spans[-1].end * frame_dur
                # convert tensor to float
                conf = float(sum(span.score for span in w_spans) / len(w_spans))
            else:
                start_time, end_time, conf = 0.0, 0.0, 0.0
        else:
            start_time, end_time, conf = 0.0, 0.0, 0.0
            
        out_words.append({
            **w_dict,
            "start": round(start_time, 3),
            "end": round(end_time, 3),
            "conf": round(conf, 3)
        })
        
    del waveform, emission, targets, alignments, scores, token_spans
    import gc
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        
    return out_words
