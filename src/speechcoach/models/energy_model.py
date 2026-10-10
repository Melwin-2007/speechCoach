import json
import numpy as np
from pathlib import Path
from sklearn.ensemble import IsolationForest
import pickle

class EnergyModel:
    """
    A standalone Volume/Energy Detector model.
    It uses globally LUFS-normalized audio and extracts relative RMS energy (dB_rel) 
    to detect VOLUME_DROP and FLAT_ENERGY over a sliding window.
    """
    def __init__(self, window_size: int = 12):
        self.window_size = window_size
        # Contamination is set very low (2%) to avoid false positives on natural volume dips
        self.model = IsolationForest(contamination=0.02, random_state=42)
        self.is_trained = False
        
    def extract_features(self, words: list[dict]) -> tuple[np.ndarray, list[dict]]:
        """
        Extracts energy features for sliding windows.
        The words list must already have acoustic stats attached (e.g. 'db_rel_mean').
        """
        X = []
        windows = []
        
        n = len(words)
        if n < self.window_size:
            return np.array([]), []
            
        for i in range(n - self.window_size + 1):
            window_words = words[i:i + self.window_size]
            
            # Extract the relative decibel level for each word
            db_values = [w.get('db_rel_mean', np.nan) for w in window_words]
            valid_db = [val for val in db_values if not np.isnan(val)]
            
            if len(valid_db) < 3:
                continue
                
            energy_mean = float(np.mean(valid_db))
            dynamic_range = float(np.std(valid_db))
            
            X.append([energy_mean, dynamic_range])
            windows.append({
                "start": window_words[0]['start'],
                "end": window_words[-1]['end'],
                "first_word": i,
                "last_word": i + self.window_size - 1,
                "energy_mean": energy_mean,
                "dynamic_range": dynamic_range
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
        print(f"EnergyModel trained on {len(X_train)} windows.")
        
    def detect_flaws(self, words: list[dict]) -> list[dict]:
        """Detect volume/energy flaws in a new recording."""
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
                mean_db = w['energy_mean']
                dyn_range = w['dynamic_range']
                
                # Rule-based filtering to prevent false positives:
                # - Only flag VOLUME_DROP if it's exceptionally quiet compared to their 95th percentile peak (<-15dB)
                # - Only flag FLAT_ENERGY if their dynamic variance is extremely low (<1.5dB)
                if mean_db < -15.0:
                    flaw_type = "VOLUME_DROP"
                elif dyn_range < 1.5:
                    flaw_type = "FLAT_ENERGY"
                else:
                    continue
                
                flaws.append({
                    "type": flaw_type,
                    "start": w['start'],
                    "end": w['end'],
                    "first_word": w['first_word'],
                    "last_word": w['last_word'],
                    "evidence": {
                        "energy_mean_relative_db": round(mean_db, 2),
                        "dynamic_range_db": round(dyn_range, 2),
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
                # Average the metrics for the merged region
                prev['evidence']['energy_mean_relative_db'] = (prev['evidence']['energy_mean_relative_db'] + curr['evidence']['energy_mean_relative_db']) / 2
            else:
                merged.append(curr)
        return merged
        
    def save(self, path: str | Path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)
            
    @classmethod
    def load(cls, path: str | Path) -> "EnergyModel":
        with open(path, 'rb') as f:
            return pickle.load(f)
