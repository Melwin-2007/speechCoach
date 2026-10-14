@echo off
setlocal
title SpeechCoach - Multimodal Speech Evaluation System
cd /d "%~dp0"

echo ===============================================================================
echo            SPEECHCOACH: 1-CLICK LAUNCHER FOR JUDGES AND EVALUATORS
echo       Track C: Contrastive Speech Analytics and Temporal Flaw Grounding
echo ===============================================================================
echo.

:: 1. Check or setup Python virtual environment
set "PYTHON_EXE="

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.\.venv\Scripts\python.exe"
    echo [*] Found existing virtual environment at .venv
    goto :check_dependencies
)

echo [*] Checking system Python...
where python >nul 2>nul
if errorlevel 1 goto :no_python

echo [*] Creating virtual environment at .venv...
python -m venv .venv
if errorlevel 1 goto :venv_fail

set "PYTHON_EXE=.\.venv\Scripts\python.exe"
echo [*] Virtual environment created successfully.

:check_dependencies
echo [*] Verifying dependencies...
%PYTHON_EXE% -c "import fastapi, uvicorn, torch, torchaudio, librosa, parselmouth, soundfile" >nul 2>nul
if not errorlevel 1 goto :check_frontend

echo [*] Installing required packages from requirements.txt...
echo [*] This only happens on first launch. Please wait...
.\.venv\Scripts\pip.exe install -r requirements.txt
if errorlevel 1 goto :pip_fail
echo [*] Dependencies installed successfully.

:check_frontend
if exist "app\dist\index.html" goto :launch

echo [*] Pre-building frontend dashboard...
where npm >nul 2>nul
if errorlevel 1 (
    echo [WARNING] app\dist\index.html is missing and npm was not found.
    goto :launch
)

pushd app
call npm install
call npm run build
popd

:launch
echo.
echo ===============================================================================
echo   [*] Starting SpeechCoach Unified Server on http://localhost:7860
echo   [*] Opening interactive dashboard in your default browser...
echo   [*] Press CTRL+C in this window to stop the server at any time.
echo ===============================================================================
echo.

:: Launch browser in background after 3 seconds
start "" cmd /c "timeout /t 3 /nobreak >nul & start http://localhost:7860"

:: Start Uvicorn Server (serves both API and Built Dashboard on port 7860)
%PYTHON_EXE% -m uvicorn --app-dir src speechcoach.api.main:app --host 127.0.0.1 --port 7860
goto :eof

:no_python
echo.
echo [ERROR] Python was not found in your system PATH.
echo Please install Python 3.11 from https://www.python.org/downloads/
echo Ensure you check 'Add python.exe to PATH' during installation.
echo.
pause
exit /b 1

:venv_fail
echo.
echo [ERROR] Failed to create virtual environment.
echo Please check your Python installation.
echo.
pause
exit /b 1

:pip_fail
echo.
echo [ERROR] Failed to install dependencies from requirements.txt.
echo.
pause
exit /b 1
