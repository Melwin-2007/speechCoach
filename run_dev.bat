@echo off
setlocal
title SpeechCoach - Development Environment (Vite + FastAPI)
cd /d "%~dp0"

echo ===============================================================================
echo            SPEECHCOACH: DEVELOPMENT MODE (HOT RELOAD)
echo     Backend: http://127.0.0.1:8000   Frontend: http://localhost:5173
echo ===============================================================================
echo.

:: 1. Check virtual environment
if exist ".venv\Scripts\python.exe" goto :check_npm

echo [*] Checking system Python...
where python >nul 2>nul
if errorlevel 1 goto :no_python

echo [*] Setting up virtual environment at .venv...
python -m venv .venv
.\.venv\Scripts\pip.exe install -r requirements-cpu.txt
if errorlevel 1 goto :pip_fail

:check_npm
where npm >nul 2>nul
if errorlevel 1 goto :no_npm

if exist "app\node_modules" goto :start_servers
echo [*] Installing frontend npm packages...
pushd app
call npm install
popd

:start_servers
echo [*] Starting Backend API on port 8000 (with hot reload)...
start "SpeechCoach API (Port 8000)" cmd /k "cd /d ""%~dp0"" && .\.venv\Scripts\python.exe -m uvicorn --app-dir src speechcoach.api.main:app --port 8000 --reload"

echo [*] Starting Frontend Vite server on port 5173 (with hot reload)...
start "SpeechCoach UI (Port 5173)" cmd /k "cd /d ""%~dp0app"" && npm run dev"

echo [*] Opening dashboard in browser in 3 seconds...
start "" cmd /c "timeout /t 3 /nobreak >nul & start http://localhost:5173"

echo.
echo Both servers are running in separate terminal windows.
echo Close those windows or press CTRL+C to terminate.
echo.
pause
goto :eof

:no_python
echo [ERROR] Python was not found in your system PATH.
pause
exit /b 1

:no_npm
echo [ERROR] Node.js / npm is required for development mode.
echo Please install Node.js from https://nodejs.org/ or use run_speechcoach.bat instead.
pause
exit /b 1

:pip_fail
echo [ERROR] Failed to install dependencies.
pause
exit /b 1
