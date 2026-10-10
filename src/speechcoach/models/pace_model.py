import json
import numpy as np
from pathlib import Path
from sklearn.ensemble import IsolationForest
import pickle
from speechcoach.features.syllables import count_syllables

class PaceModel:
    """
    A standalone Pace Detector model.
    It uses syllables/sec and words/sec over a sliding window.
    Currently uses IsolationForest for anomaly detection (unsupervised), 
    but can be swapped to a supervised classifier once we have labeled flaws.
    """
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.is_trained = False
        
    def extract_features(self, words: list[dict]) -> tuple[np.ndarray, list[dict]]:
        """
        Extracts syllables/sec and words/sec for sliding windows.
        Returns:
            X (np.ndarray): Feature matrix shape (N, 2)
            windows (list[dict]): Metadata about each window for mapping back to time
        """
        X = []
        windows = []
        
        n = len(words)
        if n < self.window_size:
            return np.array([]), []
            
        for i in range(n - self.window_size + 1):
            window_words = words[i:i + self.window_size]
            start_time = window_words[0]['start']
            end_time = window_words[-1]['end']
            duration = end_time - start_time
            
            if duration <= 0:
                continue
                
            # Calculate words/sec
            wps = self.window_size / duration
            
            # Calculate syllables/sec
            total_syllables = sum(count_syllables(w.get('norm', w.get('raw', ''))) for w in window_words)
            sps = total_syllables / duration
            
            X.append([wps, sps])
            windows.append({
                "start": start_time,
                "end": end_time,
                "first_word": i,
                "last_word": i + self.window_size - 1,
                "wps": wps,
                "sps": sps
            })
            
        return np.array(X), windows
        
    def train(self, all_words_lists: list[list[dict]]):
        """Train the anomaly detector on a list of GOOD word alignments."""
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
        print(f"PaceModel trained on {len(X_train)} windows.")
        
    def detect_flaws(self, words: list[dict]) -> list[dict]:
        """Detect pacing flaws in a new recording."""
        if not self.is_trained:
            raise RuntimeError("Model must be trained before calling detect_flaws.")
            
        X, windows = self.extract_features(words)
        if len(X) == 0:
            return []
            
        # Predict: 1 = normal, -1 = anomaly
        preds = self.model.predict(X)  # type: ignore
        scores = self.model.decision_function(X) # type: ignore # lower score = more anomalous
        
        flaws = []
        for i, (pred, score) in enumerate(zip(preds, scores)):
            if pred == -1:
                w = windows[i]
                # Determine if it's too fast or too slow based on typical human speech
                # A crude heuristic until we switch to a supervised model
                flaw_type = "PACE_FAST" if w['sps'] > 5.0 else "PACE_SLOW"
                
                flaws.append({
                    "type": flaw_type,
                    "start": w['start'],
                    "end": w['end'],
                    "first_word": w['first_word'],
                    "last_word": w['last_word'],
                    "evidence": {
                        "sps": round(w['sps'], 2),
                        "wps": round(w['wps'], 2),
                        "anomaly_score": round(score, 3)
                    }
                })
                
        # Merge overlapping flaws
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
                prev['evidence']['sps'] = (prev['evidence']['sps'] + curr['evidence']['sps']) / 2
                prev['evidence']['wps'] = (prev['evidence']['wps'] + curr['evidence']['wps']) / 2
            else:
                merged.append(curr)
        return merged
        
    def save(self, path: str | Path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)
            
    @classmethod
    def load(cls, path: str | Path) -> "PaceModel":
        with open(path, 'rb') as f:
            return pickle.load(f)
