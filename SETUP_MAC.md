# Setup auf macOS

## Voraussetzungen

### 1. OpenAI API-Key setzen
Lege deine OpenAI-Creds in `.env` oder Shell:
```bash
export OPENAI_API_KEY="sk-..."
# optional eigener Endpoint:
# export OPENAI_BASE_URL="https://api.openai.com/v1"
```

### 2. Virtuelles Environment neu erstellen
Falls das venv von Windows stammt, neu anlegen:

```bash
cd /Users/canturhan/Documents/multi_agent_orchestration
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## App starten

### Option 1: Mit dem Shell-Skript (einfach)
```bash
./run.sh
```

### Option 2: Manuell
```bash
# 1. Virtual Environment aktivieren
source venv/bin/activate

# 2. Streamlit starten
streamlit run app.py
```

## DSPy (Optional)
Die DSPy-Pipeline ist optional. Falls du DSPy nutzen möchtest, versuche:
```bash
source venv/bin/activate
pip install dspy litellm
```
Falls es Dependency-Konflikte gibt, funktioniert die App trotzdem mit LangChain und LangGraph.

## Troubleshooting

### OpenAI Auth
- Sicherstellen, dass `OPENAI_API_KEY` gesetzt ist (z. B. in `.env`).
- Optional eigener Endpoint: `OPENAI_BASE_URL=https://api.openai.com/v1`

### Python-Version Probleme
- Stelle sicher, dass Python 3.8+ installiert ist: `python3 --version`
- Falls nötig: `brew install python3`

### Dependencies Fehler
- Aktualisiere pip: `pip install --upgrade pip`
- Installiere neu: `pip install -r requirements.txt`

