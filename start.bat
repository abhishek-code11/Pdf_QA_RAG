@echo off
REM ==========================================================================
REM  start.bat  -  double-click this file to run the whole app.
REM
REM  What it does, in order:
REM    1. Checks that Python, Node.js and Ollama are installed.
REM    2. Makes sure Ollama is running (starts it if not).
REM    3. First run only: installs Python and React packages.
REM    4. Opens the BACKEND (Python, port 8000) in its own window.
REM    5. Opens the FRONTEND (React, port 5173) in its own window.
REM    6. Waits until the backend is ready, then opens the browser.
REM
REM  To STOP everything: close the "Backend" and "Frontend" windows.
REM ==========================================================================

REM %~dp0 = the folder this .bat file is in. cd there so relative paths work
REM no matter where you double-clicked from.
cd /d "%~dp0"

REM ---- 1. Check the tools exist ("where" finds a program on the PATH) ----
where python >nul 2>&1 || (echo [ERROR] Python not found. See understandingInstallation.md & pause & exit /b 1)
where npm    >nul 2>&1 || (echo [ERROR] Node.js not found. See understandingInstallation.md & pause & exit /b 1)
where ollama >nul 2>&1 || (echo [ERROR] Ollama not found. See understandingInstallation.md & pause & exit /b 1)

REM ---- 2. Is Ollama running? "ollama list" fails if the Ollama server is off ----
ollama list >nul 2>&1 || (
    echo Starting Ollama...
    start "Ollama" /min ollama serve
    timeout /t 5 /nobreak >nul
)

REM ---- 3a. First run: create the Python virtual environment + install packages ----
if not exist "backend\.venv" (
    echo First run: installing Python packages, please wait...
    python -m venv backend\.venv
    backend\.venv\Scripts\pip install -r backend\requirements.txt
)

REM ---- 3b. First run: install React packages ----
if not exist "frontend\node_modules" (
    echo First run: installing frontend packages, please wait...
    pushd frontend
    call npm install
    popd
)

REM ---- 4 + 5. Start both servers, each in its own window ----
REM "cmd /k" keeps the window open, so you can read any error messages.
REM "--reload" = uvicorn watches the backend .py files and restarts itself when you save one.
REM   (The frontend needs nothing: Vite updates the browser on save automatically.)
start "Backend (port 8000)"  cmd /k "cd /d %~dp0backend && .venv\Scripts\uvicorn main:app --port 8000 --reload"
start "Frontend (port 5173)" cmd /k "cd /d %~dp0frontend && npm run dev"

REM ---- 6. Wait for the backend (it reads + embeds the PDF on startup) ----
echo Waiting for the backend to load the PDF...
:wait_backend
timeout /t 2 /nobreak >nul
curl -s -o nul http://localhost:8000/pdf || goto wait_backend

echo Ready! Opening the browser...
start http://localhost:5173
