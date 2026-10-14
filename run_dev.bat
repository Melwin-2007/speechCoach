@echo off
setlocal enabledelayedexpansion
title SpeechCoach - Development Environment (Vite + FastAPI)

echo ===============================================================================
echo            SPEECHCOACH: DEVELOPMENT MODE (HOT RELOAD)
echo     Backend: http://127.0.0.1:8000  ^|  Frontend: http://localhost:5173
echo ===============================================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [*] Setting up virtual environment (.venv)...
    python -m venv .venv
    .\.venv\Scripts\pip install -r requirements.txt
)

where npm >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js / npm is required for development mode.
    echo Please install Node.js from https://nodejs.org/ or use run_speechcoach.bat instead.
    pause
    exit /b 1
)

if not exist "app\node_modules" (
    echo [*] Installing frontend npm packages...
    cd app && call npm install && cd ..
)

echo [*] Starting Backend API on port 8000 (with hot reload)...
start "SpeechCoach API (Port 8000)" cmd /k ".\.venv\Scripts\python.exe -m uvicorn --app-dir src speechcoach.api.main:app --port 8000 --reload"

echo [*] Starting Frontend Vite server on port 5173 (with hot reload)...
start "SpeechCoach UI (Port 5173)" cmd /k "cd app && npm run dev"

echo [*] Opening dashboard in browser in 3 seconds...
start "" cmd /c "timeout /t 3 /nobreak >nul & start http://localhost:5173"

echo.
echo Both servers are running in separate terminal windows.
echo Close those windows or press CTRL+C to terminate.
echo.
pause
