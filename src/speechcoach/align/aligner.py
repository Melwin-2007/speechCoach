import numpy as np
import torch
import torchaudio

def align_words(y: np.ndarray, words: list[dict]) -> list[dict]:
    """
    Run forced alignment using torchaudio MMS_FA model.
    
    Args:
        y: Audio data as a float32 mono array (16 kHz).
        words: List of word dictionaries from parse_transcript.
        
    Returns:
        list[dict]: The input word dictionaries, each appended with:
            - start: float (start time in seconds)
            - end: float (end time in seconds)
            - conf: float (confidence score)
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    bundle = torchaudio.pipelines.MMS_FA
    model = bundle.get_model().to(device)
    dictionary = bundle.get_dict()
    
    word_norms = [w["norm"] for w in words]
    tokenized_transcript = []
    word_spans = []
    
    for word in word_norms:
        start_idx = len(tokenized_transcript)
        for char in word:
            if char in dictionary:
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
        
    return out_words
