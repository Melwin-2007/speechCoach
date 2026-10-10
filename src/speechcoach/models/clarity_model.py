import json
import numpy as np
from pathlib import Path
from sklearn.ensemble import IsolationForest
import pickle

class ClarityModel:
    """
    A standalone Voice Quality & Clarity Detector model.
    It uses Harmonics-to-Noise Ratio (HNR), Spectral Flux, and MFCC features 
    to detect CLARITY flaws (mumbling, hoarseness, poor articulation).
    """
    def __init__(self, window_size: int = 12):
        self.window_size = window_size
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.is_trained = False
        
    def extract_features(self, words: list[dict]) -> tuple[np.ndarray, list[dict]]:
        """
        Extracts voice quality features for sliding windows.
        The words list must already have acoustic stats attached (hnr_mean, flux_mean, mfcc_mean).
        """
        X = []
        windows = []
        
        n = len(words)
        if n < self.window_size:
            return np.array([]), []
            
        for i in range(n - self.window_size + 1):
            window_words = words[i:i + self.window_size]
            
            # Extract HNR and Flux
            hnr_values = [w.get('hnr_mean', np.nan) for w in window_words]
            flux_values = [w.get('flux_mean', np.nan) for w in window_words]
            
            valid_hnr = [v for v in hnr_values if not np.isnan(v)]
            valid_flux = [v for v in flux_values if not np.isnan(v)]
            
            if len(valid_hnr) < 3 or len(valid_flux) < 3:
                continue
                
            window_hnr = float(np.mean(valid_hnr))
            window_flux = float(np.mean(valid_flux))
            
            # Extract MFCCs (average across the window)
            mfcc_list = []
            for w in window_words:
                mfcc = w.get('mfcc_mean')
                if mfcc is not None and not np.isnan(mfcc[0]):
                    mfcc_list.append(mfcc)
                    
            if not mfcc_list:
                continue
                
            # Average the 13 MFCC coefficients across the valid words in the window
            window_mfcc = np.mean(mfcc_list, axis=0) # shape: (13,)
            
            # Combine scalar features with the 13 MFCC features
            feature_vector = [window_hnr, window_flux] + window_mfcc.tolist()
            
            X.append(feature_vector)
            windows.append({
                "start": window_words[0]['start'],
                "end": window_words[-1]['end'],
                "first_word": i,
                "last_word": i + self.window_size - 1,
                "hnr": window_hnr,
                "flux": window_flux
            })
            
        return np.array(X, dtype=np.float32), windows
        
    def train(self, all_words_lists: list[list[dict]]):
        """Train the anomaly detector on GOOD recordings."""
        X_train = []
        for words in all_words_lists:
            X, _ = self.extract_features(words)
            if len(X) > 0:
                X_train.append(X)
                
        if not X_train:
            raise ValueError("No valid features extracted for training.")
            
        X_train = np.vstack(X_train)
        self.model.fit(X_train)  # type: ignore
        self.is_trained = True
        print(f"ClarityModel trained on {len(X_train)} windows using {X_train.shape[1]} features.")
        
    def detect_flaws(self, words: list[dict]) -> list[dict]:
        """Detect clarity flaws in a new recording."""
        if not self.is_trained:
            raise RuntimeError("Model must be trained before calling detect_flaws.")
            
        X, windows = self.extract_features(words)
        if len(X) == 0:
            return []
            
        preds = self.model.predict(X)  # type: ignore
        scores = self.model.decision_function(X)  # type: ignore
        
        flaws = []
        for i, (pred, score) in enumerate(zip(preds, scores)):
            if pred == -1:
                w = windows[i]
                
                # If HNR is extremely low (noisy/hoarse) or Flux is very low (mumbling/soft onsets)
                flaws.append({
                    "type": "CLARITY",
                    "start": w['start'],
                    "end": w['end'],
                    "first_word": w['first_word'],
                    "last_word": w['last_word'],
                    "evidence": {
                        "hnr_mean": round(w['hnr'], 2),
                        "spectral_flux_mean": round(w['flux'], 2),
                        "anomaly_score": round(score, 3)
                    }
                })
                
        return self._merge_flaws(flaws)
        
    def _merge_flaws(self, flaws: list[dict]) -> list[dict]:
        if not flaws: return []
        flaws.sort(key=lambda x: x['start'])
        merged = [flaws[0]]
        for curr in flaws[1:]:
            prev = merged[-1]
            if curr['start'] <= prev['end'] and curr['type'] == prev['type']:
                prev['end'] = max(prev['end'], curr['end'])
                prev['last_word'] = max(prev['last_word'], curr['last_word'])
                # Average the metrics
                prev['evidence']['hnr_mean'] = (prev['evidence']['hnr_mean'] + curr['evidence']['hnr_mean']) / 2
                prev['evidence']['spectral_flux_mean'] = (prev['evidence']['spectral_flux_mean'] + curr['evidence']['spectral_flux_mean']) / 2
            else:
                merged.append(curr)
        return merged
        
    def save(self, path: str | Path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)
            
    @classmethod
    def load(cls, path: str | Path) -> "ClarityModel":
        with open(path, 'rb') as f:
            return pickle.load(f)
