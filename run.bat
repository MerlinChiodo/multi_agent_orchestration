@echo off
setlocal enabledelayedexpansion
title Multi-Agent Orchestration - Runner
cd /d "%~dp0"

call "venv\Scripts\activate.bat"
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt

REM Prüfen, ob Ollama bereits läuft (Port 11434)
powershell -Command "$p=(Get-NetTCPConnection -LocalPort 11434 -State Listen -ErrorAction SilentlyContinue); if(-not $p){Start-Process cmd -ArgumentList '/k','ollama serve' -WindowStyle Normal}"

REM etwas mehr Zeit geben
timeout /t 8 >nul

python -m streamlit run app.py
endlocal
