# Projekt Erklärung: Multi Agent Paper Analyzer

## Projektüberblick

Wir analysieren wissenschaftliche Texte mit vier spezialisierten Agenten:
- **Reader** liest das Dokument und extrahiert Notizen.
- **Summarizer** fasst die wichtigsten Aussagen zusammen.
- **Critic** bewertet, wie gut die Zusammenfassung ist.
- **Integrator** erstellt eine Meta-Zusammenfassung aus allem.

Der Workflow läuft in drei Frameworks:
- **LangChain**: Simple, sequenzielle Schritte.
- **LangGraph**: Graph-basierte Steuerung und Visualisierung.
- **DSPy**: Deklarativ und automatisch optimierend (optional mit Teleprompting).

## Agenten-Pipeline (konzeptionell)

**LangChain (linear)**
```mermaid
flowchart LR
  R[Reader] --> S[Summarizer] --> C[Critic] --> I[Integrator]
```

**LangGraph (Graph + Conditional Edges)**
```mermaid
flowchart LR
  R[Reader] --> S[Summarizer] --> C[Critic]
  C -- "ok" --> I[Integrator]
  C -- "low score / rework" --> S
```
Hinweis: Der reale Graph im Projekt enthält zusätzliche Nodes (Translator/Keyword/Quality/Judge/Aggregator) und erzeugt `graph_dot` zur Visualisierung (`app/workflows/langgraph_pipeline.py`).

**DSPy (deklarativ via Signatures)**
- DSPy arbeitet nicht primär mit „Prompt-Strings pro Step“, sondern mit `dspy.Signature` (Inputs/Outputs + Regeln). DSPy generiert die Prompts daraus automatisch und kann sie via Teleprompting optimieren (`app/workflows/dspy_pipeline.py`).

## Framework-Vergleich (Trade-offs)

| Framework | Paradigma | Vorteile | Nachteile | Beispiel im Projekt |
|---|---|---|---|---|
| LangChain | Sequenziell | Einfach, gut für Einsteiger | Kein Conditional Flow / Looping | `app/workflows/langchain_pipeline.py:run_pipeline()` |
| LangGraph | Graph-based | Conditional Edges, visualisierbar, erweiterbar | Mehr Boilerplate (State + Routing) | `app/workflows/langgraph_pipeline.py:_build_langgraph_workflow()` |
| DSPy | Deklarativ / Self-Improving | Signatures + (optional) automatische Prompt-Optimierung | Braucht Dev-Set, oft höhere Latenz | `app/workflows/dspy_pipeline.py` (`dspy.Signature`, `run_pipeline()`) |

## Mini-Beispielausgabe (Form der Ergebnisse)

| Framework | Ergebnis-Felder (Auszug) | Projekt-spezifische Extras |
|---|---|---|
| LangChain | `structured`, `summary`, `critic`, `meta`, `latency_s`, `reader_s`… | — |
| LangGraph | `structured`, `summary`, `critic`, `meta`, `latency_s`, `reader_s`… | `summary_translated`, `keywords`, `critic_loops`, `graph_dot` |
| DSPy | `structured`, `summary`, `critic`, `meta`, `latency_s`, `reader_s`… | `dspy_available` (+ optional Teleprompting) |

## Designentscheidungen

### Warum mehrere Agenten?
Ein großer Prompt → schwer zu kontrollieren. Mit einzelnen Agenten bleibt jede Aufgabe klar getrennt. Das erleichtert Debugging und Anpassung.

### Warum drei Frameworks?
- LangChain geht schnell und bleibt übersichtlich.
- LangGraph zeigt den Ablauf als Graph und lässt sich besser erweitern.
- DSPy übernimmt Optimierungsschritte automatisch durch Signaturen.

So lernen Teilnehmer verschiedene Stile kennen und entscheiden, welcher Ansatz zu ihrer Idee passt.

### Warum Streamlit?
Streamlit startet mit einem Befehl, zeigt Uploads, Buttons und Vergleiche direkt im Browser und macht die Arbeit interaktiv.

### Warum Text Vorverarbeitung?
PDFs enthalten oft störende Elemente (Metadaten, Literaturverzeichnis, seltsame Zeilenumbrüche). `utils.py` normalisiert den Text, damit die Agenten sauber arbeiten.

### Warum Telemetrie?
`telemetry.py` schreibt Laufzeiten und Textlängen in eine CSV. So kann man sehen, welche Pipeline schneller ist und wie groß die Outputs werden.

### Warum Doppelklick Start?
`run.bat` und `run.sh` übernehmen Setup, pip, `.env` und starten Streamlit. Das ist für Workshop-Teilnehmer der einfachste Weg.
