import numpy as np

def frame_features(y: np.ndarray) -> dict:
    """
    Extract acoustic features on a 10 ms grid.
    
    Args:
        y: Audio data (16kHz float32).
        
    Returns:
        dict: Keys must be: 't', 'f0', 'st', 'db', 'db_rel', 'flux', 'mfcc', 'hnr'.
              All values must be 1D numpy arrays of the same length (except mfcc which is 2D),
              representing frames every 0.01 seconds.
    """
    import librosa
    import parselmouth
    from scipy.signal import butter, filtfilt
    
    sr = 16000
    hop_length = 160  # 10 ms
    
    # 1. Loudness (Energy)
    rms = librosa.feature.rms(y=y, frame_length=320, hop_length=hop_length, center=True)[0]
    db = 20 * np.log10(np.clip(rms, 1e-10, None))
    db_95 = np.percentile(db, 95)
    db_rel = db - db_95
    
    t = librosa.frames_to_time(np.arange(len(db)), sr=sr, hop_length=hop_length)
    n_frames = len(t)
    
    # 2. Pitch (F0) via Praat/Parselmouth
    snd = parselmouth.Sound(y.astype(np.float64), sr)
    
    # Pass 1
    pitch_pass1 = snd.to_pitch(time_step=0.01, pitch_floor=75, pitch_ceiling=600)
    f0_1 = pitch_pass1.selected_array['frequency']
    voiced_f0 = f0_1[f0_1 > 0]
    
    if len(voiced_f0) > 0:
        q1, q3 = np.percentile(voiced_f0, [25, 75])
        floor2 = max(60.0, 0.75 * q1)
        ceil2 = min(800.0, 1.5 * q3)
    else:
        floor2, ceil2 = 75.0, 600.0
        
    # Pass 2
    pitch_pass2 = snd.to_pitch_ac(time_step=0.01, pitch_floor=floor2, pitch_ceiling=ceil2, very_accurate=True)
    f0 = pitch_pass2.selected_array['frequency']
    
    f0[f0 == 0] = np.nan
    
    # Align Parselmouth time grid to librosa
    idx = np.searchsorted(pitch_pass2.xs(), t)
    idx = np.clip(idx, 0, len(f0) - 1)
    f0_aligned = f0[idx]
    
    valid_f0 = f0_aligned[~np.isnan(f0_aligned)]
    if len(valid_f0) > 0:
        median_f0 = np.median(valid_f0)
        st = 12 * np.log2(f0_aligned / median_f0)
    else:
        st = np.full_like(f0_aligned, np.nan)
        
    # 3. Spectral features on band-passed copy (80-4000 Hz)
    nyq = sr / 2
    b, a = butter(4, [80 / nyq, 4000 / nyq], btype='bandpass')
    y_bp = filtfilt(b, a, y).astype(np.float32)
    
    mfcc = librosa.feature.mfcc(y=y_bp, sr=sr, n_mfcc=13, hop_length=hop_length, center=True)
    mfcc_mean = np.mean(mfcc, axis=1, keepdims=True)
    mfcc_std = np.std(mfcc, axis=1, keepdims=True) + 1e-8
    mfcc_cmvn = (mfcc - mfcc_mean) / mfcc_std
    
    flux = librosa.onset.onset_strength(y=y_bp, sr=sr, hop_length=hop_length, center=True)
    
    harm = snd.to_harmonicity_cc(time_step=0.01)
    hnr = harm.values[0, :]
    hnr_aligned = np.interp(t, harm.xs(), hnr)
    
    def fix_len(arr):
        if arr.ndim == 1:
            if len(arr) < n_frames:
                return np.pad(arr, (0, n_frames - len(arr)), mode='edge')
            return arr[:n_frames]
        else:
            if arr.shape[1] < n_frames:
                return np.pad(arr, ((0,0), (0, n_frames - arr.shape[1])), mode='edge')
            return arr[:, :n_frames]

    return {
        't': t,
        'f0': fix_len(f0_aligned),
        'st': fix_len(st),
        'db': fix_len(db),
        'db_rel': fix_len(db_rel),
        'flux': fix_len(flux),
        'mfcc': fix_len(mfcc_cmvn),
        'hnr': fix_len(hnr_aligned)
    }
