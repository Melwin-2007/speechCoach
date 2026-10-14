# SpeechCoach — Local Setup & Installation Guide

This guide provides end-to-end instructions for installing, configuring, verifying, and running **SpeechCoach** locally on Windows, macOS, or Linux.

---

## 1. System Requirements & Prerequisites

Before starting, ensure your system has the following toolchains installed:

| Requirement | Minimum Version | Recommended | Notes |
|---|---|---|---|
| **Python** | `3.11.0` | `3.11.9` | 64-bit required. Ensure `python` and `pip` are on your system `PATH`. |
| **Node.js** | `18.0.0` | `20.x` or `22.x` (LTS) | Required for the React/Vite web application dashboard. |
| **npm** | `9.0.0` | `10.x+` | Bundled with Node.js. |
| **Git** | `2.30+` | Latest | For repository cloning and version control. |
| **NVIDIA GPU** | Optional | CUDA 12.4+ supported | MMS forced alignment and audio processing automatically fall back to CPU if no GPU is detected. |

---

## 2. Clone the Repository

Clone the project repository to your local machine and navigate into the root directory:

```bash
git clone https://github.com/Melwin-2007/speechCoach.git
cd speechCoach
```

---

## 3. Python Virtual Environment Setup

Always run the project inside an isolated virtual environment to prevent dependency conflicts.

### Step 3.1: Create the Virtual Environment
From the project root directory, run:

```bash
python -m venv .venv
```

### Step 3.2: Allow Script Execution (Windows Only)
If you encounter a `PSSecurityException` or script execution restriction in Windows PowerShell, grant execution rights for the current user:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
*(Type `Y` and press Enter when prompted).*

### Step 3.3: Activate the Virtual Environment

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.\.venv\Scripts\activate.bat
```

**macOS / Linux (bash / zsh):**
```bash
source .venv/bin/activate
```

Upon activation, your terminal prompt will be prefixed with `(.venv)`.

---

## 4. Install Python Dependencies

With the virtual environment activated, upgrade `pip` and install the locked dependencies from `requirements.txt`:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> **PyTorch & GPU Acceleration Note:**
> `requirements.txt` is pre-configured with the official PyTorch CUDA index (`https://download.pytorch.org/whl/cu124`).
> - Systems with an NVIDIA GPU and CUDA 12.4 drivers will automatically receive GPU-accelerated PyTorch.
> - Systems without a discrete GPU will run PyTorch seamlessly in CPU mode without manual configuration changes.

---

## 5. Verify Backend & ML Environment

Run this quick one-line diagnostic to confirm your Python environment, PyTorch, acoustic tools, and alignment models are functioning properly:

```bash
python -c "import torch, torchaudio, parselmouth, pyworld; print('PyTorch version:', torch.__version__); print('CUDA Available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU (fallback active)')"
```

Expected output:
- `PyTorch version: 2.5.1+cu124` (or CPU build)
- `CUDA Available: True` (if NVIDIA GPU installed) or `False`
- `Device: <Your GPU Name>` or `CPU (fallback active)`

---

## 6. Frontend Dashboard Setup (`app/`)

The frontend is built with React 19, Vite, WaveSurfer.js, and Lucide icons.

Open a new terminal, navigate to the `app/` directory, and install its Node packages:

```bash
cd app
npm install
```

### Run Frontend Quality Checks:
```bash
# Verify design tokens and styling compliance
npm run lint:design

# Build production bundle to verify asset compilation
npm run build
```

---

## 7. Running the Application Locally

You can run SpeechCoach in **Development Mode** (dual process with hot reloading) or **Single-Server Production Mode**.

### Option A: Development Mode (Recommended for Development)

Open two terminal windows from the repository root:

#### Terminal 1 — Backend API (FastAPI)
```bash
# Windows PowerShell / CMD
.\.venv\Scripts\activate
python -m uvicorn --app-dir src speechcoach.api.main:app --port 8000 --reload

# macOS / Linux
source .venv/bin/activate
python -m uvicorn --app-dir src speechcoach.api.main:app --port 8000 --reload
```
- API Base URL: [http://localhost:8000](http://localhost:8000)
- Interactive OpenAPI / Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

#### Terminal 2 — Frontend UI (Vite Dev Server)
```bash
cd app
npm run dev
```
- Web Application URL: [http://localhost:5173](http://localhost:5173)

---

### Option B: Single-Server Mode (Production Preview)

FastAPI can host the compiled React frontend directly, requiring only a single running process:

1. Build the frontend distribution bundle:
   ```bash
   cd app
   npm run build
   cd ..
   ```
2. Start the FastAPI server:
   ```bash
   python -m uvicorn --app-dir src speechcoach.api.main:app --host 0.0.0.0 --port 8000
   ```
3. Open [http://localhost:8000](http://localhost:8000) in your browser. Both the API and the web interface will be served together on port `8000`.

---

## 8. Running the Test Suite

SpeechCoach includes automated unit and integration tests covering forced alignment, feature extraction, scoring penalties, and REST API endpoints.

From the repository root (with `.venv` activated):

```bash
# Run all automated tests
pytest tests/

# Run tests with detailed verbosity
pytest tests/ -v
```

All 10 API integration tests should pass cleanly:
```
tests/test_api_analyze.py .......... [100%]
====================== 10 passed in ~60-80s ======================
```

---

## 9. Running Analysis via Command Line (CLI)

You can analyze any WAV recording against a transcript directly from the terminal without starting the web server:

```bash
# Set PYTHONPATH to src (PowerShell):
$env:PYTHONPATH="src"
python -m speechcoach.analyze dataset/raw/good/S01/S01_T01_GOOD.wav dataset/transcripts/T01.txt

# On Linux / macOS:
PYTHONPATH=src python -m speechcoach.analyze dataset/raw/good/S01/S01_T01_GOOD.wav dataset/transcripts/T01.txt
```

Example Output:
```
Overall Delivery Score: 64.3 / 100.0
Flaws Detected: 0
```

---

## 10. Troubleshooting & Common Issues

### 1. `PSSecurityException: File cannot be loaded because running scripts is disabled`
- **Cause:** PowerShell default execution policy blocks unauthenticated script execution.
- **Fix:** Run in PowerShell as administrator or current user:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### 2. `Address already in use` (Port 8000 or 5173)
- **Cause:** Another instance of `uvicorn` or `vite` is still bound to the port.
- **Fix (Windows PowerShell):**
  ```powershell
  Get-NetTCPConnection -LocalPort 8000, 5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
  ```
- **Fix (macOS / Linux):**
  ```bash
  lsof -ti:8000,5173 | xargs kill -9
  ```

### 3. PyTorch CUDA Out-of-Memory / CUDA Initialization Error
- **Cause:** GPU VRAM is constrained or driver version mismatch.
- **Fix:** SpeechCoach automatically falls back to CPU if CUDA fails. You can force CPU execution by setting:
  ```bash
  export CUDA_VISIBLE_DEVICES=""       # Linux / macOS
  $env:CUDA_VISIBLE_DEVICES=""         # Windows PowerShell
  ```

### 4. Audio Alignment Fails / HTTP 400 on `/analyze`
- **Cause:** The audio is silent, unintelligible, or deviates too drastically from the provided transcript text.
- **Fix:** Ensure the audio is audible (16 kHz mono PCM WAV recommended) and that the text in the transcript box matches the spoken words. Try using one of the pre-configured sample baseline texts (`T01`–`T08`).

---

## 11. Directory Structure at a Glance

```
SpeechCoach/
├── app/                  # React 19 + Vite frontend
│   ├── public/demo/      # Precomputed JSON analysis results
│   ├── public/demo-audio/# Verified sample audio takes (ideal, almost, botched)
│   └── src/              # React components, charts, and audio player
├── configs/              # Population bounds & sigma/tau thresholds
├── dataset/              # Reference recordings, transcripts, metadata
├── docs/                 # Architecture, contracts, tasks, and handoffs
├── src/speechcoach/      # Core ML analysis engine & FastAPI server
│   ├── align/            # Torchaudio MMS forced aligner
│   ├── api/              # FastAPI endpoints & Pydantic schemas
│   ├── compare/          # Hysteresis deviation detection
│   ├── features/         # Acoustic, pitch, and energy extractors
│   └── scoring/          # Dimensional and composite scoring
├── tests/                # Automated pytest suite
├── setup.md              # Setup & installation guide (this file)
└── README.md             # Project overview & architectural documentation
```
