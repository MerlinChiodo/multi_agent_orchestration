@echo off
setlocal enabledelayedexpansion
title Multi-Agent Orchestration
REM Wechsel ins Projekt-Root (Startskripte liegen in scripts\launchers\)
cd /d "%~dp0..\.."

REM Sicherstellen, dass wir im Projekt-Root sind (requirements.txt muss existieren)
if not exist "requirements.txt" (
    echo FEHLER: requirements.txt nicht gefunden!
    echo Aktuelles Verzeichnis: %CD%
    echo Erwartet wird das Projekt-Root mit requirements.txt.
    pause
    exit /b 1
)

echo ========================================
echo Multi-Agent Orchestration Workshop
echo ========================================
echo.

REM Pruefe Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    where py >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo FEHLER: Python nicht gefunden!
        echo Bitte Python 3.9+ installieren: https://www.python.org/downloads/
        pause
        exit /b 1
    )
    set PYTHON_CMD=py -3
) else (
    set PYTHON_CMD=python
)

REM Pruefe Python-Version (>=3.9 und <=3.12, damit Binary-Wheels verfuegbar sind)
%PYTHON_CMD% -c "import sys; v=sys.version_info; sys.exit(0 if (v.major, v.minor) >= (3,9) and (v.major, v.minor) <= (3,12) else 1)"
if %ERRORLEVEL% NEQ 0 (
    echo FEHLER: Unterstuetzte Python-Versionen sind 3.9 bis 3.12.
    echo Empfohlen fuer den Kurs: Python 3.10 oder 3.11.
    echo Gefunden:
    %PYTHON_CMD% --version
    pause
    exit /b 1
)

REM Venv anlegen, falls nicht vorhanden
if not exist "venv\Scripts\activate.bat" (
    echo [1/4] Erstelle virtuelles Environment...
    %PYTHON_CMD% -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo FEHLER: Virtual Environment konnte nicht erstellt werden!
        pause
        exit /b 1
    )
) else (
    echo [1/4] Virtual Environment gefunden
)

call "venv\Scripts\activate.bat"
if %ERRORLEVEL% NEQ 0 (
    echo FEHLER: Virtual Environment konnte nicht aktiviert werden!
    pause
    exit /b 1
)

REM Dependencies installieren
echo [2/4] Installiere Abhaengigkeiten (dauert 1-2 Minuten)...
REM pip kann nach abgebrochenen Installs eine defekte "~penai*" Distribution warnen; cleanen wir vorab.
for /f "delims=" %%i in ('%PYTHON_CMD% -c "import site; print(site.getsitepackages()[0])"') do set "SITE_PACKAGES=%%i"
for /d %%d in ("%SITE_PACKAGES%\~penai*") do (
    rmdir /s /q "%%d" >nul 2>&1
)
%PYTHON_CMD% -m pip install --upgrade pip --quiet >nul 2>&1
%PYTHON_CMD% -m pip install -r requirements.txt --quiet
if %ERRORLEVEL% NEQ 0 (
    echo FEHLER: Installation fehlgeschlagen!
    pause
    exit /b 1
)

REM .env Datei erstellen, falls nicht vorhanden
if not exist ".env" (
    echo [3/4] Erstelle .env Datei...
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo WICHTIG: Bitte .env Datei oeffnen und OPENAI_API_KEY eintragen!
        echo.
    ) else (
        echo OPENAI_API_KEY= > .env
        echo WICHTIG: Bitte .env Datei oeffnen und API-Key eintragen!
        echo.
    )
) else (
    echo [3/4] .env Datei vorhanden
)

REM App starten
echo [4/4] Starte App...
echo.
echo ========================================
echo App startet jetzt im Browser!
echo Zum Beenden: Strg+C im Fenster
echo ========================================
echo.

%PYTHON_CMD% -m streamlit run app/app.py

endlocal
