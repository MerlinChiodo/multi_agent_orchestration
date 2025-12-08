# Multi-Agent Orchestration Demo

Paper-Analyzer mit drei Orchestrierungs-Varianten:
- **LangChain**: Sequenziell (Reader → Summarizer → Critic → Integrator)
- **LangGraph**: Expliziter Graph mit DOT-Visualisierung
- **DSPy**: Deklarativ mit optionalem Teleprompting (Few-Shot-Bootstrap)

## Quickstart
1) Installiere Abhängigkeiten (optional DSPy manuell, siehe `requirements.txt`):
```bash
pip install -r requirements.txt
# optional
# pip install dspy-ai litellm
```
2) Setze `OPENAI_API_KEY` (und optional `OPENAI_BASE_URL` für eigene Endpoints).

3) Starte die Streamlit-App:
```bash
streamlit run app.py
```

## Nutzung
- Lade PDF/TXT hoch, die App erstellt einen abschnittsbasierten Analyse-Kontext (Budget konfigurierbar).
- Wähle Pipeline (LangChain/LangGraph/DSPy) und Modell/Parameter in der Sidebar.
- Button **Starten** führt die gewählte Pipeline aus.
- Button **Alle Pipelines vergleichen** führt LC/LG/DSPy nacheinander aus und zeigt Metriken/Outputs nebeneinander.
- Button **DSPy Teleprompt Gain** vergleicht DSPy-Base vs. Teleprompting (Dev-Set nötig).
- Expander **Telemetry (CSV)** zeigt gesammelte Laufzeiten pro Engine (`telemetry.csv`).
- Optionales W&B-Logging aktivierbar via Env `WANDB_ENABLED=1` (Projekt/Entity per `WANDB_PROJECT`/`WANDB_ENTITY`).

## DSPy
- Aktivierbar über Sidebar-Checkbox „DSPy optimieren“ (Teleprompting), nutzt `eval/dev.jsonl` als Dev-Set.
- Falls `dspy-ai` oder `litellm` fehlen, wird ein Stub ausgeführt und im UI gewarnt.

## Evaluierung
- `eval_runner.py` führt ein Dev-Set über alle Pipelines aus und berechnet ein simples unigram-F1 zwischen Kontext und Summary.

## Struktur
- `agents/`: Einzel-Agenten (Reader, Summarizer, Critic, Integrator)
- `workflows/`: Pipelines für LangChain, LangGraph, DSPy
- `telemetry.py`: CSV-Logging
- `utils.py`: Text-Normalisierung und Abschnittslogik

