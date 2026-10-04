from pydantic import BaseModel
from typing import List, Dict, Optional

class MetaData(BaseModel):
    mode: str
    baseline_id: Optional[str] = None
    duration_s: float
    version: str
    warnings: List[str] = []

class WordZScores(BaseModel):
    pace: Optional[float] = None
    pause: Optional[float] = None
    pitch: Optional[float] = None
    energy: Optional[float] = None
    clarity: Optional[float] = None

class Word(BaseModel):
    i: int
    w: str
    start: float
    end: float
    punct: str = ""
    conf: float
    z: Optional[WordZScores] = None

class SeriesParticipant(BaseModel):
    pitch_st: List[Optional[float]] = []
    energy_db: List[Optional[float]] = []
    rate_sps: List[Optional[float]] = []

class SeriesBaseline(BaseModel):
    pitch_st: List[Optional[float]] = []
    pitch_lo: List[Optional[float]] = []
    pitch_hi: List[Optional[float]] = []
    energy_db: List[Optional[float]] = []
    rate_sps: List[Optional[float]] = []

class SeriesData(BaseModel):
    t: List[float] = []
    participant: Optional[SeriesParticipant] = None
    baseline: Optional[SeriesBaseline] = None

class Evidence(BaseModel):
    participant: float
    baseline: float
    z: float
    unit: str

class Explanation(BaseModel):
    observed: str
    deviation: str
    where: str
    why: str
    fix: str

class Flaw(BaseModel):
    id: int
    type: str
    start: float
    end: float
    first_word: int
    last_word: int
    severity: float
    band: str
    evidence: Evidence
    explanation: Explanation

class Dimensions(BaseModel):
    pacing: float
    pausing: float
    pitch: float
    energy: float
    emphasis: float
    clarity: float
    fluency: float

class Scores(BaseModel):
    overall: float
    dimensions: Dimensions

class AnalysisResult(BaseModel):
    meta: MetaData
    words: List[Word] = []
    series: Optional[SeriesData] = None
    flaws: List[Flaw] = []
    scores: Scores
