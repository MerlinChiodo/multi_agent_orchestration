#!/bin/bash
# Multi-Agent Orchestration - Runner (macOS/Linux)

# Wechsle ins Script-Verzeichnis
cd "$(dirname "$0")"

# Aktiviere das virtuelle Environment
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Kein virtuelles Environment gefunden. Erstelle eines..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Upgrade pip und installiere Dependencies
echo "Installiere/aktualisiere Dependencies..."
python -m pip install --upgrade pip > /dev/null 2>&1
python -m pip install -r requirements.txt

# Hinweis: Für GPT-4.1 wird nur ein gültiger OPENAI_API_KEY benötigt.
# Starte Streamlit
echo "Starte Streamlit App..."
python -m streamlit run app.py

