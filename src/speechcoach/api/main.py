from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional, List
from .models import AnalysisResult

import os
from pathlib import Path

app = FastAPI(title="SpeechCoach API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/baselines")
def get_baselines():
    return [
        {"id": "T1", "title": "JFK Inaugural", "n_ideals": 3},
        {"id": "T4", "title": "Tagore - Where the mind is without fear", "n_ideals": 2}
    ]

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_stub(
    audio_file: UploadFile = File(...),
    transcript: str = Form(...),
    baseline_id: Optional[str] = Form(None)
):
    import json
    from pathlib import Path
    mock_path = Path(__file__).parent.parent.parent.parent / "app" / "public" / "mock_result.json"
    with open(mock_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Mount static frontend files if they exist (for production)
frontend_dist = Path(__file__).parent.parent.parent.parent / "app" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Allow API routes to pass through (though they are defined before this)
        if full_path.startswith("api/") or full_path == "health" or full_path == "baselines" or full_path == "analyze":
            pass
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")

