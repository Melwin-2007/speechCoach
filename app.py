import sys
from pathlib import Path

# Add src to python path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import uvicorn
from speechcoach.api.main import app

try:
    import gradio as gr
    # For Hugging Face Spaces (Gradio SDK):
    # Mount Gradio onto the existing FastAPI app at /gradio so HF recognizes the space,
    # while the main root / serves the full SpeechCoach React Dashboard.
    demo = gr.Blocks(title="SpeechCoach")
    with demo:
        gr.Markdown("# SpeechCoach — Contrastive Speech Analytics")
        gr.Markdown("Dashboard running at the root URL.")
    app = gr.mount_gradio_app(app, demo, path="/gradio")
except ImportError:
    pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
