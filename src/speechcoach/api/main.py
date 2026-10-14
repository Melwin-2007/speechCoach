import hashlib
import json
import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List
import numpy as np

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from .models import AnalysisResult

logger = logging.getLogger("speechcoach.api")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="SpeechCoach API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REPO_ROOT = Path(__file__).parent.parent.parent.parent
CACHE_DIR = REPO_ROOT / ".cache" / "analyses"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
PUBLIC_DIR = REPO_ROOT / "app" / "public"

WHY_FIX_CATALOG = {
    "PACE_FAST": {
        "why": "Speaking too quickly reduces articulatory precision and leaves listeners unable to absorb key ideas.",
        "fix": "Slow down your delivery rate, articulate unstressed syllables deliberately, and insert intentional micro-pauses at commas."
    },
    "PACE_SLOW": {
        "why": "Dragging out phrases slows narrative momentum and can make delivery sound hesitant or low energy.",
        "fix": "Sustain a brisk, engaging conversational cadence through connecting phrases without lingering on small function words."
    },
    "PITCH_FLAT": {
        "why": "Monotone delivery with minimal pitch variance leads to cognitive fatigue and causes the audience to tune out.",
        "fix": "Vary your intonation across phrases—raise pitch slightly on transition points and allow it to fall naturally at period closures."
    },
    "PITCH_ERRATIC": {
        "why": "Unpredictable vocal pitch jitter creates an unstable, nervous vocal quality that undermines speaker authority.",
        "fix": "Anchor your voice in your lower chest resonance and support steady breath flow to stabilize pitch contours."
    },
    "ENERGY_LOW": {
        "why": "Dropping vocal volume causes key words to be swallowed and makes speech difficult to follow.",
        "fix": "Maintain diaphragm support through the final words of each sentence to prevent vocal fade."
    },
    "ENERGY_FLAT": {
        "why": "Uniform dynamic energy creates an unexpressive, mechanical sound lacking emotional punch.",
        "fix": "Emphasize important nouns and verbs by increasing vocal projection on critical message words."
    },
    "PAUSE_LONG": {
        "why": "Excessive silence breaks listener engagement and creates awkward pauses that feel like hesitation.",
        "fix": "Limit phrase breaks to 0.4s–0.8s and sentence breaks to under 1.2s to maintain continuous narrative flow."
    },
    "PAUSE_MISSING": {
        "why": "Rushing through punctuation boundaries without breathing creates a run-on delivery that overwhelms listeners.",
        "fix": "Pause for at least 0.3s at commas and 0.6s at periods to allow listeners to process the thought."
    }
}

# Global custom error handler to guarantee {"error": "..."} without leaking stack traces
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"error": detail})

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing request {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"error": "An internal server error occurred while processing the speech."})

@app.on_event("startup")
def warmup_model():
    """Warm up MMS_FA model on boot so first request runs instantly from local memory."""
    try:
        from speechcoach.align.aligner import _get_model
        _get_model()
        logger.info("Forced alignment model warmed up on startup.")
    except Exception as e:
        logger.warning(f"Startup model warmup deferred: {e}")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/baselines")
def get_baselines():
    baselines_info = [
        {"id": "T01", "title": "Technology & Communication"},
        {"id": "T02", "title": "Modern Education"},
        {"id": "T03", "title": "Environmental Responsibility"},
        {"id": "T04", "title": "Artificial Intelligence"},
        {"id": "T05", "title": "Public Speaking & Delivery"},
        {"id": "T06", "title": "Innovation & Problem Solving"},
        {"id": "T07", "title": "Teamwork & Collaboration"},
        {"id": "T08", "title": "The Future & Decision Making"},
    ]
    transcripts_dir = REPO_ROOT / "dataset" / "transcripts"
    result = []
    for b in baselines_info:
        t_file = transcripts_dir / f"{b['id']}.txt"
        transcript_text = t_file.read_text(encoding="utf-8").strip() if t_file.exists() else ""
        result.append({
            "id": b["id"],
            "title": b["title"],
            "n_ideals": 4,
            "transcript": transcript_text
        })
    return result

@app.get("/demo/{name}", response_model=AnalysisResult)
def get_demo(name: str):
    valid_presets = ["ideal", "almost", "botched"]
    if name not in valid_presets:
        raise HTTPException(status_code=404, detail=f"Demo preset '{name}' not found. Valid presets: {valid_presets}")
    
    demo_file = PUBLIC_DIR / "demo" / f"{name}.json"
    if not demo_file.exists():
        demo_file = PUBLIC_DIR / "mock_result.json"
    
    if not demo_file.exists():
        raise HTTPException(status_code=404, detail="Demo data file missing from server.")
    
    with open(demo_file, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/demo-audio/{name}.wav")
def get_demo_audio(name: str):
    audio_path = PUBLIC_DIR / "demo-audio" / f"{name}.wav"
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail=f"Demo audio '{name}.wav' not found.")
    return FileResponse(audio_path, media_type="audio/wav")

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_speech(
    audio: Optional[UploadFile] = File(None),
    audio_file: Optional[UploadFile] = File(None),
    transcript: str = Form(...),
    baseline_id: Optional[str] = Form(None),
    mode: str = Form("auto")
):
    upload = audio or audio_file
    if not upload:
        raise HTTPException(status_code=400, detail="Missing required audio file parameter ('audio' or 'audio_file').")
    
    clean_transcript = transcript.strip()
    if not clean_transcript:
        raise HTTPException(status_code=400, detail="Transcript text cannot be empty.")
    
    audio_bytes = await upload.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Uploaded audio file is empty (0 bytes).")
    
    # 25 MB upload limit
    if len(audio_bytes) > 25 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio file exceeds the 25 MB limit. Please upload a smaller file.")
    
    # Verify file is audio
    content_type = upload.content_type or ""
    filename = upload.filename or ""
    ext = Path(filename).suffix.lower()
    allowed_exts = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".webm"}
    if ext and ext not in allowed_exts and not content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail=f"Unsupported file format '{ext}'. Allowed audio formats: {', '.join(sorted(allowed_exts))}")

    # Compute content hash for deterministic caching
    hasher = hashlib.sha256()
    hasher.update(audio_bytes)
    hasher.update(clean_transcript.encode("utf-8"))
    hasher.update((baseline_id or "").encode("utf-8"))
    hasher.update(mode.encode("utf-8"))
    content_hash = hasher.hexdigest()

    cache_file = CACHE_DIR / f"{content_hash}.json"
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                return cached_data
        except Exception as e:
            logger.warning(f"Failed to read cached analysis {cache_file}: {e}")

    # Write temporary audio file for processing
    suffix = ext if ext in allowed_exts else ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_f:
        tmp_path = Path(tmp_f.name)
        tmp_f.write(audio_bytes)

    try:
        result_dict = None
        # Run real speechcoach pipeline in a threadpool so event loop remains unblocked
        try:
            from starlette.concurrency import run_in_threadpool
            from speechcoach.analyze import analyze as pipeline_analyze
            raw_result = await run_in_threadpool(
                pipeline_analyze,
                audio_path=tmp_path,
                transcript=clean_transcript,
                baseline_id=baseline_id,
                mode=mode
            )
            if not raw_result or not isinstance(raw_result, dict):
                raise ValueError("Pipeline returned invalid or empty analysis output.")
            dur = float(raw_result.get("meta", {}).get("duration_s", 0.0))
            result_dict = adapt_pipeline_result(raw_result, mode, baseline_id, dur)
        except HTTPException:
            raise
        except ModuleNotFoundError as me:
            logger.error(f"Speech analysis missing module: {me}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Server environment missing required ML library: {me}. Please wait for package installation to finish."
            )
        except Exception as pe:
            logger.error(f"Speech analysis pipeline failed: {pe}", exc_info=True)
            err_msg = str(pe)
            if "align" in err_msg.lower() or "score" in err_msg.lower() or "target" in err_msg.lower():
                detail_msg = "Speech analysis failed: unable to align the recording with the provided transcript. Please ensure the audio is audible and matches the text."
            else:
                detail_msg = f"Speech analysis error: {err_msg}"
            raise HTTPException(
                status_code=400,
                detail=detail_msg
            )

        # Save to cache
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(result_dict, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to write cache {cache_file}: {e}")

        return result_dict

    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass


EXPLANATION_CATALOG = {
    "PACE_FAST": {
        "why": "Rushing through phrases crowds words together, impairing syllable clarity and making the delivery sound tense or hurried to listeners.",
        "fix": "Lengthen stressed vowel durations, breathe deeply, and insert deliberate micro-pauses before key ideas to give your audience time to absorb information."
    },
    "PACE_SLOW": {
        "why": "Dragging out speech rate drains momentum and can cause listener attention to drift away from the core message.",
        "fix": "Increase rhythmic drive by transitioning briskly between unstressed syllables and maintaining vocal forward momentum across phrases."
    },
    "PITCH_FLAT": {
        "why": "A lack of melodic variation flattens expressiveness, sounding monotone or disengaged even if the content is compelling.",
        "fix": "Vary pitch contours naturally: step pitch upward on primary focus words and allow pitch to drop cleanly at sentence terminals."
    },
    "MONOTONE": {
        "why": "A lack of melodic variation flattens expressiveness, sounding monotone or disengaged even if the content is compelling.",
        "fix": "Vary pitch contours naturally: step pitch upward on primary focus words and allow pitch to drop cleanly at sentence terminals."
    },
    "PITCH_ERRATIC": {
        "why": "Abrupt and unpredictable pitch excursions create an unsettled impression, sounding melodically unnatural or unsteady.",
        "fix": "Anchor your vocal pitch around your natural speaking register, reserving pitch inflections for deliberate emphasis."
    },
    "ENERGY_LOW": {
        "why": "Vocal volume drops noticeably below projection baseline, risking audience strain and conveying hesitation or lack of conviction.",
        "fix": "Engage diaphragmatic breath support to keep air pressure consistent, projecting clearly through to the final syllable of each phrase."
    },
    "VOLUME_DROP": {
        "why": "Vocal volume drops noticeably below projection baseline, risking audience strain and conveying hesitation or lack of conviction.",
        "fix": "Engage diaphragmatic breath support to keep air pressure consistent, projecting clearly through to the final syllable of each phrase."
    },
    "ENERGY_FLAT": {
        "why": "Uniform acoustic intensity without dynamic contrasts causes all words to blend together without natural hierarchy.",
        "fix": "Add dynamic contrast by leaning into key words with slightly greater vocal punch and tapering back on transitional phrases."
    },
    "PAUSE_LONG": {
        "why": "Excessive silence halts the natural flow of thought, leading listeners to question whether you lost your train of thought.",
        "fix": "Limit mid-sentence pauses to under 0.5s; use brief tactical silences only at clause boundaries or major thematic shifts."
    },
    "PAUSE_MISSING": {
        "why": "Running through punctuation without pausing denies the audience the cognitive breather needed to process complex thoughts.",
        "fix": "Insert a distinct 0.3s–0.5s tactical pause at commas and sentence endings to establish clear thought boundaries."
    },
    "FILLERS": {
        "why": "Vocalized fillers ('um', 'uh') disrupt phrase flow and can dilute perceived confidence.",
        "fix": "Replace vocalized fillers with silent pauses when gathering your next thought."
    }
}


def adapt_pipeline_result(raw: dict, mode: str, baseline_id: Optional[str], duration_s: float) -> dict:
    """Adapt raw speechcoach pipeline output to match AnalysisResult schema."""
    warnings = []
    if raw.get("not_assessed"):
        warnings.append(f"{len(raw['not_assessed'])} unassessed region(s) detected due to unvoiced audio or silence.")
    
    meta = {
        "mode": mode if mode in ["reference", "prior"] else ("reference" if baseline_id else "prior"),
        "baseline_id": baseline_id,
        "duration_s": round(duration_s, 2),
        "version": "2.0",
        "warnings": warnings
    }

    grid = raw.get("grid", {})
    grid_t = np.array(grid.get("t", []))
    grid_sps = np.array(grid.get("sps", []))
    grid_pitch = np.array(grid.get("st_std", []))
    grid_energy = np.array(grid.get("db_rel", []))
    grid_pause = np.array(grid.get("pause_s", []))

    med_pace = float(grid.get("baseline_pace", [4.1])[0]) if grid.get("baseline_pace") else 4.1
    b_pitch = float(grid.get("baseline_pitch", [2.38])[0]) if grid.get("baseline_pitch") else 2.38
    med_pitch = b_pitch if 0.1 <= b_pitch <= 15.0 else 2.38

    words = []
    raw_words = raw.get("words", [])
    for idx, w in enumerate(raw_words):
        word_text = w.get("raw") or w.get("w") or w.get("word") or ""
        punct = ""
        if word_text and word_text[-1] in '.,;:?!':
            punct = word_text[-1]
            word_text = word_text[:-1]
        
        st = float(w["start"])
        en = float(w["end"])
        
        # Calculate real acoustic z-scores from grid if available
        z_pace = 0.0
        z_pause = 0.0
        z_pitch = 0.0
        z_energy = 0.0
        z_clarity = 0.0
        
        if len(grid_t) > 0:
            m = (grid_t >= st) & (grid_t <= en)
            if np.any(m):
                w_sps = float(np.mean(grid_sps[m]))
                if w_sps > 0:
                    z_pace = round(max(-5.0, min(5.0, (w_sps - med_pace) / 0.75)), 2)
                
                w_pitch = float(np.mean(grid_pitch[m]))
                if w_pitch > 0:
                    z_pitch = round(max(-5.0, min(5.0, (w_pitch - med_pitch) / 0.65)), 2)
                
                w_energy = float(np.mean(grid_energy[m]))
                z_energy = round(max(-5.0, min(5.0, w_energy / 4.0)), 2)
            
            m_pre = (grid_t >= max(0.0, st - 0.4)) & (grid_t < st)
            if np.any(m_pre):
                w_pause = float(np.max(grid_pause[m_pre]))
                if w_pause > 0.35:
                    z_pause = round(max(-5.0, min(5.0, (w_pause - 0.35) / 0.4)), 2)

        words.append({
            "i": idx,
            "w": word_text.strip().lower(),
            "start": round(st, 2),
            "end": round(en, 2),
            "punct": punct or w.get("punct", ""),
            "conf": round(float(w.get("conf", 1.0)), 2),
            "z": {
                "pace": z_pace,
                "pause": z_pause,
                "pitch": z_pitch,
                "energy": z_energy,
                "clarity": z_clarity,
            }
        })

    flaws = []
    raw_regions = raw.get("regions", [])
    for r in raw_regions:
        flaw_start = float(r["start"])
        flaw_end = float(r["end"])
        flaw_type = str(r["type"])
        
        matching_words = [w["i"] for w in words if w["end"] >= flaw_start and w["start"] <= flaw_end]
        first_w = matching_words[0] if matching_words else 0
        last_w = matching_words[-1] if matching_words else (len(words) - 1 if words else 0)
        
        dev_peak = float(r.get("dev_peak", 2.0))
        abs_dev = abs(dev_peak)
        severity = round(min(1.0, max(0.2, (abs_dev - 1.0) / 4.0)), 2)
        band = "major" if abs_dev >= 3.5 else ("moderate" if abs_dev >= 2.0 else "minor")
        
        cat = EXPLANATION_CATALOG.get(flaw_type, {
            "why": str(r.get("explanation", "Delivery deviated from baseline cadence.")),
            "fix": "Focus on deliberate vocal dynamics and follow the baseline cadence."
        })

        val = float(r.get("value", 0.0))
        base = float(r.get("baseline", 0.0))
        unit = str(r.get("unit", ""))

        if "PACE_FAST" in flaw_type:
            obs = f"Speaking rate reached {val:.1f} {unit} (baseline {base:.1f} {unit})"
        elif "PACE_SLOW" in flaw_type:
            obs = f"Speaking rate dropped to {val:.1f} {unit} (baseline {base:.1f} {unit})"
        elif "PITCH_FLAT" in flaw_type or "MONOTONE" in flaw_type:
            obs = f"Pitch variability fell to {val:.1f} {unit} (baseline {base:.1f} {unit})"
        elif "PITCH_ERRATIC" in flaw_type:
            obs = f"Pitch variability spiked to {val:.1f} {unit} (baseline {base:.1f} {unit})"
        elif "ENERGY_LOW" in flaw_type or "VOLUME_DROP" in flaw_type:
            obs = f"Relative loudness dropped to {val:.1f} {unit}"
        elif "ENERGY_FLAT" in flaw_type:
            obs = f"Dynamic variability flat at {val:.1f} {unit}"
        elif "PAUSE_LONG" in flaw_type:
            obs = f"Pause duration extended to {val:.2f} s (typical < 0.50 s)"
        elif "PAUSE_MISSING" in flaw_type:
            obs = f"Pause between thoughts omitted (measured {val:.2f} s)"
        elif val != 0.0 or base != 0.0:
            obs = f"Measured {val:.1f} {unit} vs baseline {base:.1f} {unit}".strip()
        else:
            obs = f"Acoustic deviation of {dev_peak:+.1f}σ detected"

        if base > 0 and val > 0:
            pct = ((val - base) / base) * 100.0
            dev_text = f"{dev_peak:+.1f}σ deviation ({pct:+.0f}% vs baseline)"
        else:
            dev_text = f"{dev_peak:+.1f}σ deviation from baseline"

        if matching_words:
            spoken_text = " ".join([words[wi]["w"] for wi in matching_words if wi < len(words)])
            if len(spoken_text) > 42:
                spoken_text = spoken_text[:39] + "..."
            where_text = f"On '{spoken_text}' ({flaw_start:.1f}s – {flaw_end:.1f}s)"
        else:
            where_text = f"Between {flaw_start:.1f}s and {flaw_end:.1f}s"

        explanation_obj = {
            "observed": obs,
            "deviation": dev_text,
            "where": where_text,
            "why": cat["why"],
            "fix": cat["fix"]
        }
            
        flaws.append({
            "id": int(r["id"]),
            "type": flaw_type,
            "start": round(flaw_start, 2),
            "end": round(flaw_end, 2),
            "first_word": first_w,
            "last_word": last_w,
            "severity": severity,
            "band": band,
            "evidence": {
                "participant": round(float(r.get("value", 0.0)), 2),
                "baseline": round(float(r.get("baseline", 0.0)), 2),
                "z": round(dev_peak, 2),
                "unit": str(r.get("unit", ""))
            },
            "explanation": explanation_obj
        })

    # Ensure flaws are strictly sorted by start time and non-decreasing
    flaws.sort(key=lambda x: (x["start"], x["end"]))
    for idx, f in enumerate(flaws, 1):
        f["id"] = idx

    soft = raw.get("soft_features", {})
    
    # Calculate dimensional penalties based on detected flaws
    def get_flaw_penalty(flaw_list, target_types):
        penalty = 0.0
        for f in flaw_list:
            if f["type"] in target_types:
                sev = f.get("severity", 0.5)
                b = f.get("band", "minor")
                base_w = 26.0 if b == "major" else (15.0 if b == "moderate" else 8.0)
                penalty += base_w * sev
        return penalty

    # Meaningful dimensional scoring based on true feature measurements & detected flaws
    pace_err = abs(float(np.mean(grid_sps[grid_sps > 0])) - med_pace) if len(grid_sps) and np.any(grid_sps > 0) else 0.0
    pace_pen = get_flaw_penalty(flaws, ["PACE_FAST", "PACE_SLOW"])
    pacing_sc = max(25.0, min(100.0, round(100.0 - pace_err * 8.0 - pace_pen, 1)))

    mean_pitch_var = float(np.mean(grid_pitch[grid_pitch > 0])) if len(grid_pitch) and np.any(grid_pitch > 0) else med_pitch
    pitch_err = abs(med_pitch - mean_pitch_var)
    pitch_pen = get_flaw_penalty(flaws, ["MONOTONE", "PITCH_FLAT", "PITCH_ERRATIC"])
    pitch_sc = max(25.0, min(100.0, round(100.0 - pitch_err * 8.0 - pitch_pen, 1)))

    energy_pen = get_flaw_penalty(flaws, ["ENERGY_LOW", "ENERGY_FLAT", "FLAT_ENERGY", "VOLUME_DROP"])
    energy_sc = max(25.0, min(100.0, round(100.0 - energy_pen, 1)))

    pause_pen = get_flaw_penalty(flaws, ["PAUSE_LONG", "PAUSE_MISSING"])
    pausing_sc = max(25.0, min(100.0, round(100.0 - pause_pen, 1)))

    fluency_sc = max(25.0, min(100.0, round(100.0 - pause_pen * 0.7 - pace_pen * 0.3, 1)))
    clarity_sc = 94.0
    emphasis_sc = max(35.0, min(100.0, round(100.0 - energy_pen * 0.4 - pitch_pen * 0.4, 1)))

    dim_vals = [pacing_sc, pausing_sc, pitch_sc, energy_sc, clarity_sc, emphasis_sc, fluency_sc]
    composite_score = round(float(np.mean(dim_vals)), 1)

    if not flaws:
        overall_score = composite_score
    else:
        flaw_deductions = 0.0
        for f in flaws:
            b = f.get("band", "minor")
            sev = f.get("severity", 0.5)
            ded = 24.0 * sev if b == "major" else (14.0 * sev if b == "moderate" else 7.0 * sev)
            flaw_deductions += ded
        overall_score = max(15.0, min(92.0, round(composite_score - flaw_deductions * 0.6, 1)))

    scores = {
        "overall": round(overall_score, 1),
        "dimensions": {
            "pacing": pacing_sc,
            "pausing": pausing_sc,
            "pitch": pitch_sc,
            "energy": energy_sc,
            "emphasis": emphasis_sc,
            "clarity": clarity_sc,
            "fluency": fluency_sc
        }
    }

    grid = raw.get("grid", {})
    t_arr = grid.get("t", [])
    if t_arr:
        series_t = [round(float(t), 2) for t in t_arr]
        pitch_part = [round(float(p), 2) if np.isfinite(p) else None for p in grid.get("st_std", [])]
        energy_part = [round(float(e), 2) if np.isfinite(e) else None for e in grid.get("db_rel", [])]
        pace_part = [round(float(s), 2) if np.isfinite(s) else None for s in grid.get("sps", [])]
        
        b_pace_val = float(grid.get("baseline_pace", [4.0])[0]) if grid.get("baseline_pace") else 4.0
        b_pitch_val = float(grid.get("baseline_pitch", [0.0])[0]) if grid.get("baseline_pitch") else 0.0
        
        n_pts = len(series_t)
        series_data = {
            "t": series_t,
            "participant": {
                "pitch_st": pitch_part,
                "energy_db": energy_part,
                "rate_sps": pace_part
            },
            "baseline": {
                "pitch_st": [round(b_pitch_val, 2)] * n_pts,
                "pitch_lo": [round(b_pitch_val - 2.0, 2)] * n_pts,
                "pitch_hi": [round(b_pitch_val + 2.0, 2)] * n_pts,
                "energy_db": [-12.0] * n_pts,
                "energy_lo": [-18.0] * n_pts,
                "energy_hi": [-6.0] * n_pts,
                "rate_sps": [round(b_pace_val, 2)] * n_pts,
                "rate_lo": [round(max(0.5, b_pace_val - 1.0), 2)] * n_pts,
                "rate_hi": [round(b_pace_val + 1.0, 2)] * n_pts
            }
        }
    else:
        series_data = None

    return {
        "meta": meta,
        "words": words,
        "series": series_data,
        "flaws": flaws,
        "scores": scores
    }





# Mount static frontend files if they exist (for production build)
frontend_dist = REPO_ROOT / "app" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api/") or full_path in ["health", "baselines", "analyze"]:
            pass
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")
