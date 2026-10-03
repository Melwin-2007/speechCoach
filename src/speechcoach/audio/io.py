import numpy as np
from pathlib import Path
import librosa
import pyloudnorm as pyln

def load_audio(path: str | Path, sr: int = 16000, target_lufs: float = -23.0) -> np.ndarray:
    """
    Load an audio file, resample to `sr`, convert to mono, and normalize to `target_lufs`.
    
    Args:
        path: Path to the audio file.
        sr: Target sample rate.
        target_lufs: Target loudness in LUFS.
        
    Returns:
        np.ndarray: Audio data as a float32 mono array.
    """
    path_str = str(path)
    # Load with librosa to handle resampling and mono conversion
    y, _ = librosa.load(path_str, sr=sr, mono=True)
    
    # Measure the loudness and normalize
    meter = pyln.Meter(sr) # create BS.1770 meter
    loudness = meter.integrated_loudness(y)
    
    # Perform loudness normalization
    y_norm = pyln.normalize.loudness(y, loudness, target_lufs)
    
    return y_norm.astype(np.float32)
