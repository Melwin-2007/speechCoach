import json
import numpy as np
from pathlib import Path
from sklearn.ensemble import IsolationForest
import pickle

class PauseModel:
    """
    A standalone Pause Detector model.
    It uses pause duration, previous punctuation, and pause frequency.
    Currently uses IsolationForest for anomaly detection (unsupervised), 
    but can be swapped to a supervised classifier once we have labeled flaws.
    """
    def __init__(self, recent_window_size: int = 10, min_pause_detect: float = 0.15):
        self.recent_window_size = recent_window_size
        self.min_pause_detect = min_pause_detect
        # Lower contamination for pause because humans vary a lot, we only want egregious outliers
        self.model = IsolationForest(contamination=0.03, random_state=42)
        self.is_trained = False
        
    def extract_features(self, words: list[dict]) -> tuple[np.ndarray, list[dict]]:
        """
        Extracts pause features per word.
        Features: [pause_duration, has_punct_before, pause_frequency]
        """
        X = []
        windows = []
        
        n = len(words)
        for i, w in enumerate(words):
            pause_dur = w.get('pause_before', 0.0)
            
            # Did the previous word end with punctuation?
            has_punct = 0.0
            if i > 0 and words[i-1].get('punct', '') != "":
                has_punct = 1.0
                
            # Pause frequency in the recent N words
            start_idx = max(0, i - self.recent_window_size)
            recent_words = words[start_idx:i]
            if not recent_words:
                pause_freq = 0.0
            else:
                pauses_found = sum(1 for rw in recent_words if rw.get('pause_before', 0.0) > self.min_pause_detect)
                pause_freq = pauses_found / len(recent_words)
                
            X.append([pause_dur, has_punct, pause_freq])
            windows.append({
                "word_idx": i,
                "start": max(0.0, w['start'] - pause_dur),
                "end": w['start'],
                "pause_dur": pause_dur,
                "punct": has_punct,
                "freq": pause_freq
            })
            
        return np.array(X, dtype=np.float32), windows
        
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
        print(f"PauseModel trained on {len(X_train)} word pauses.")
        
    def detect_flaws(self, words: list[dict]) -> list[dict]:
        """Detect pausing flaws in a new recording."""
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
                dur = w['pause_dur']
                punct = w['punct']
                
                # Rule-based categorization of the statistical anomaly
                if dur > 0.4 and punct == 0.0:
                    flaw_type = "PAUSE_MISPLACED"
                elif dur > 1.2 and punct == 1.0:
                    flaw_type = "PAUSE_EXCESS"
                elif dur < 0.1 and punct == 1.0:
                    flaw_type = "PAUSE_MISSING"
                else:
                    # Ignore minor statistical outliers that don't fit our flaw schema
                    continue
                
                flaws.append({
                    "type": flaw_type,
                    "start": w['start'],
                    "end": w['end'],
                    "first_word": w['word_idx'],
                    "last_word": w['word_idx'],
                    "evidence": {
                        "pause_duration_s": round(dur, 3),
                        "had_punctuation": bool(punct),
                        "pause_frequency": round(w['freq'], 3),
                        "anomaly_score": round(score, 3)
                    }
                })
                
        return flaws
        
    def save(self, path: str | Path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)
            
    @classmethod
    def load(cls, path: str | Path) -> "PauseModel":
        with open(path, 'rb') as f:
            return pickle.load(f)
