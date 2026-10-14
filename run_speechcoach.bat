@echo off
setlocal enabledelayedexpansion
title SpeechCoach - Multimodal Speech Evaluation System

echo ===============================================================================
echo            SPEECHCOACH: 1-CLICK LAUNCHER FOR JUDGES & EVALUATORS
echo       Track C: Contrastive Speech Analytics & Temporal Flaw Grounding
echo ===============================================================================
echo.

:: 1. Locate Python executable
set "PY_CMD="

where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PY_CMD=python"
) else (
    if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
        set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
        set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    ) else if exist "C:\Python311\python.exe" (
        set "PY_CMD=C:\Python311\python.exe"
    ) else if exist "C:\Program Files\Python311\python.exe" (
        set "PY_CMD=C:\Program Files\Python311\python.exe"
    )
)

if "%PY_CMD%"=="" (
    echo [ERROR] Python was not found on your system or in your PATH.
    echo Please install Python 3.11 from: https://www.python.org/downloads/
    echo (Make sure to check "Add Python to PATH" during installation)
    echo.
    pause
    exit /b 1
)

echo [*] Python detected:
%PY_CMD% --version
echo.

:: 2. Check and configure Python Virtual Environment (.venv)
if not exist ".venv\Scripts\python.exe" (
    echo [*] Setting up virtual environment (.venv)...
    %PY_CMD% -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [*] Virtual environment created successfully.
)

set "VENV_PY=.\.venv\Scripts\python.exe"
set "VENV_PIP=.\.venv\Scripts\pip.exe"

:: 3. Check dependencies
echo [*] Checking required dependencies...
%VENV_PY% -c "import fastapi, uvicorn, torch, torchaudio, librosa, parselmouth, soundfile" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [*] Installing required Python libraries from requirements.txt...
    echo [*] (This only happens on first launch; please wait a few moments)
    %VENV_PIP% install --upgrade pip
    %VENV_PIP% install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Dependency installation encountered an issue.
        pause
        exit /b 1
    )
    echo [*] All dependencies installed successfully.
) else (
    echo [*] All required dependencies are already installed.
)

:: 4. Verify Frontend Assets
if not exist "app\dist\index.html" (
    echo [*] Frontend pre-build not detected. Checking for Node.js / npm...
    where npm >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo [*] Building React dashboard...
        cd app
        call npm install
        call npm run build
        cd ..
    ) else (
        echo [WARNING] app\dist\index.html is missing and npm is not found.
    )
)

echo.
echo ===============================================================================
echo   [*] Starting SpeechCoach Unified Server on http://localhost:7860
echo   [*] Opening interactive dashboard in your default browser in 3 seconds...
echo   [*] Press CTRL+C in this terminal window to stop the server at any time.
echo ===============================================================================
echo.

:: Automatically open browser once server is initialized
start "" cmd /c "timeout /t 3 /nobreak >nul & start http://localhost:7860"

:: Start Uvicorn Server (Serves both API and Built Dashboard on Port 7860)
%VENV_PY% -m uvicorn --app-dir src speechcoach.api.main:app --host 127.0.0.1 --port 7860

pause
