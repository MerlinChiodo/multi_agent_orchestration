@echo off
setlocal enabledelayedexpansion
title Multi-Agent Orchestration - Runner
cd /d "%~dp0"

call "venv\Scripts\activate.bat"
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt

REM Hinweis: Für GPT-4.1 wird ein gueltiger OPENAI_API_KEY erwartet (z. B. in .env)

python -m streamlit run app.py
endlocal
