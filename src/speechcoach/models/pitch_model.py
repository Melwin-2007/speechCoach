import json
import numpy as np
from pathlib import Path
from sklearn.ensemble import IsolationForest
import pickle

class PitchModel:
    """
    A standalone Pitch Detector model.
    It uses F0 standard deviation and Pitch Variation (range) over a sliding window.
    Currently uses IsolationForest for anomaly detection (unsupervised).
    """
    def __init__(self, window_size: int = 12):
        self.window_size = window_size
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.is_trained = False
        
    def extract_features(self, words: list[dict]) -> tuple[np.ndarray, list[dict]]:
        """
        Extracts pitch features for sliding windows.
        The words list must already have acoustic stats attached (e.g. 'st_mean').
        """
        X = []
        windows = []
        
        n = len(words)
        if n < self.window_size:
            return np.array([]), []
            
        for i in range(n - self.window_size + 1):
            window_words = words[i:i + self.window_size]
            
            # Extract the pitch in semitones for each word in the window
            st_values = [w.get('st_mean', np.nan) for w in window_words]
            # Filter out NaN values (e.g. unvoiced words)
            valid_st = [val for val in st_values if not np.isnan(val)]
            
            if len(valid_st) < 3:
                # Not enough voiced speech in this window to measure pitch
                continue
                
            pitch_std = float(np.std(valid_st))
            pitch_range = float(np.max(valid_st) - np.min(valid_st))
            
            X.append([pitch_std, pitch_range])
            windows.append({
                "start": window_words[0]['start'],
                "end": window_words[-1]['end'],
                "first_word": i,
                "last_word": i + self.window_size - 1,
                "pitch_std": pitch_std,
                "pitch_range": pitch_range
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
        print(f"PitchModel trained on {len(X_train)} windows.")
        
    def detect_flaws(self, words: list[dict]) -> list[dict]:
        """Detect pitch flaws in a new recording."""
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
                std = w['pitch_std']
                
                # Rule-based categorization:
                # If pitch variation is extremely low -> Monotone
                # If pitch variation is extremely high -> Erratic
                # Since we don't know the exact cutoff without supervised labels, 
                # we'll use a crude heuristic for now.
                flaw_type = "MONOTONE" if std < 1.0 else "PITCH_ERRATIC"
                
                flaws.append({
                    "type": flaw_type,
                    "start": w['start'],
                    "end": w['end'],
                    "first_word": w['first_word'],
                    "last_word": w['last_word'],
                    "evidence": {
                        "pitch_std_semitones": round(std, 2),
                        "pitch_range_semitones": round(w['pitch_range'], 2),
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
                prev['evidence']['pitch_std_semitones'] = (prev['evidence']['pitch_std_semitones'] + curr['evidence']['pitch_std_semitones']) / 2
            else:
                merged.append(curr)
        return merged
        
    def save(self, path: str | Path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)
            
    @classmethod
    def load(cls, path: str | Path) -> "PitchModel":
        with open(path, 'rb') as f:
            return pickle.load(f)
