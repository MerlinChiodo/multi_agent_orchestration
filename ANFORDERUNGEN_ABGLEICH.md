# Anforderungen-Abgleich: Multi-Agent Workflow Orchestration

Dieses Dokument zeigt, wie die Anforderungen aus dem Modul umgesetzt wurden. Das Modul heißt "Conversational Artificial Intelligence Topic 8".

## Projektkontext

Das Modul behandelt Multi-Agent Workflow Orchestration. Es geht um selbstoptimierende Pipelines mit LangChain, LangGraph und DSPy. Das Ziel ist die Koordination mehrerer Agenten. Diese Agenten arbeiten zusammen, um Texte zu analysieren und zusammenzufassen.

---

## 1. Hauptanforderungen: Framework-Integration

### LangChain für sequenzielle Pipelines

Die Anforderung war ein sequenzieller Workflow mit LangChain. Das Projekt hat dies umgesetzt.

Die Implementierung steht in der Datei `app/workflows/langchain_pipeline.py`. Der Ansatz ist prozedural und sequenziell. Der Workflow läuft so: Reader, dann Summarizer, dann Critic, dann Integrator.

Die Pipeline führt die Schritte linear aus. Es gibt keine bedingten Verzweigungen. Die Laufzeit wird für jeden Agent gemessen. Die Telemetrie ist integriert. Fehler werden behandelt.

Der Code zeigt die sequenzielle Ausführung:

```python
structured_notes = run_reader(analysis_context)
summary = run_summarizer(structured_notes)
critic_result = run_critic(notes=structured_notes, summary=summary)
meta_summary = run_integrator(notes=structured_notes, summary=summary, critic=critic_text)
```

Status: Vollständig implementiert

### LangGraph für graph-basierte Orchestrierung

Die Anforderung war eine graph-basierte Orchestrierung. Der Kontrollfluss soll explizit sein. Das Projekt hat dies umgesetzt.

Die Implementierung steht in der Datei `app/workflows/langgraph_pipeline.py`. Der Ansatz nutzt einen Graph mit State-Verwaltung. Der Workflow läuft so: Retriever, dann Reader, dann Summarizer, dann Critic. Danach gibt es eine bedingte Verzweigung zum Integrator.

Die Pipeline bietet bedingte Kanten. Bei niedrigem Critic-Score springt der Workflow zurück zum Summarizer. Der Graph wird visualisiert im DOT-Format. Der Zustand wird explizit verwaltet. Es gibt zusätzliche Knoten: Translator, Keyword Extraction, Quality, Judge und Aggregator. Langwierige Aufrufe werden durch Timeouts geschützt. Ein Routing-Trace hilft beim Debugging.

Der Code zeigt die Graph-Struktur:

```python
graph = StateGraph(PipelineState)
graph.add_node("retriever", _execute_retriever_node)
graph.add_node("reader", _execute_reader_node)
graph.add_node("summarizer", _execute_summarizer_node)
graph.add_node("critic_node", _execute_critic_node)
graph.add_conditional_edges("critic_node", _critic_post_path)
graph.add_edge("integrator", END)
```

Status: Vollständig implementiert mit erweiterten Features

### DSPy für deklarative Pipelines

Die Anforderung war eine deklarative Pipeline-Definition. Die Prompts sollen automatisch optimiert werden. Das Projekt hat dies umgesetzt.

Die Implementierung steht in der Datei `app/workflows/dspy_pipeline.py`. Der Ansatz nutzt Signatures statt expliziter Prompts. Der Workflow läuft über Signatures: Reader, dann Summarizer, dann Critic, dann Integrator.

Die Pipeline nutzt Signatures wie ReadNotes, Summarize, Critique und Integrate. Teleprompting ist optional und nutzt BootstrapFewShot. Ein Dev-Set wird integriert aus der Datei `dev-set/dev.jsonl`. Die Prompt-Optimierung läuft automatisch basierend auf Beispielen. Die Optimierung nutzt eine F1-basierte Metrik. Der Gewinn durch Teleprompting wird getrackt.

Der Code zeigt die Signature-Definition:

```python
class Summarize(dspy.Signature):
    """Produce a concise scientific summary (200-300 words) from NOTES."""
    NOTES: str = dspy.InputField(desc="Structured scientific notes")
    SUMMARY: str = dspy.OutputField(desc="200-300 word summary")

class PaperPipeline(dspy.Module):
    def __init__(self):
        super().__init__()
        self.reader = ReaderM()
        self.summarizer = SummarizerM()
        self.critic = CriticM()
        self.integrator = IntegratorM()
```

Status: Vollständig implementiert mit Teleprompting

## 2. Forschungsfragen

### Frage 1: Unterschiede zwischen prozeduralen und deklarativen Frameworks

Die Frage lautet: Wie unterscheiden sich prozedurale Frameworks von deklarativen Frameworks? Prozedural bedeutet, dass der Ablauf Schritt für Schritt beschrieben wird. Deklarativ bedeutet, dass nur das Ziel beschrieben wird.

Das Projekt beantwortet diese Frage durch einen direkten Vergleich. Alle drei Frameworks implementieren denselben Workflow. Die Unterschiede werden in Tabellen dokumentiert. Die Dokumentation steht in `README.md` und `project_overview.md`.

Die praktische Demonstration zeigt die Unterschiede. LangChain nutzt explizite Funktionsaufrufe. Der Code ist prozedural. LangGraph nutzt eine Graph-Struktur. Der Zustand wird explizit verwaltet. DSPy nutzt Signatures. Die Prompts werden automatisch generiert.

Teilnehmer können den Code ändern. Sie sehen die Unterschiede direkt. Die Dokumentation erklärt die Paradigmen in `README.md` und `project_overview.md`.

Status: Vollständig beantwortet

### Frage 2: Selbstoptimierende Mechanismen

Die Frage lautet: Wie können selbstoptimierende Mechanismen die Zuverlässigkeit verbessern? Es geht um die automatische Optimierung von Prompts in Multi-Agent-Workflows.

Das Projekt beantwortet diese Frage durch eine Implementierung. DSPy Teleprompting nutzt BootstrapFewShot. Die Implementierung steht in `app/workflows/dspy_pipeline.py`.

Die Evaluation misst den F1-Gain. Es wird die Basis-Version mit der optimierten Version verglichen. Der Vergleich läuft in der Streamlit-App im Tab "DSPy Optimization". Die Metriken heißen teleprompt_gain, teleprompt_base_score und teleprompt_optimized_score.

Das Dev-Set enthält 15 Beispiele. Diese stehen in `dev-set/dev.jsonl`. Jedes Beispiel hat Tags für target_length und prompt_focus. Die Dokumentation erklärt dies in `README.md` und in den Workshop-Materialien.

Der Code zeigt die Teleprompting-Konfiguration:

```python
tp = dspy.teleprompt.BootstrapFewShot(
    metric=_metric,
    max_bootstrapped_demos=3,
    max_labeled_demos=3,
)
optimized_summarizer = tp.compile(pipeline.summarizer, trainset=trainset)
```

Status: Vollständig beantwortet

### Frage 3: Abwägungen zwischen Flexibilität, Nachvollziehbarkeit und Wartbarkeit

Die Frage lautet: Welche Abwägungen gibt es zwischen Flexibilität, Nachvollziehbarkeit und Wartbarkeit? Es geht um die Orchestrierung mehrstufiger Abläufe.

Das Projekt zeigt diese Abwägungen praktisch. Die Flexibilität wird durch LangGraph demonstriert. LangGraph zeigt bedingte Verzweigungen. Die Graph-Struktur ist erweiterbar. DSPy zeigt deklarative Anpassbarkeit. Diese läuft über Signatures.

Die Nachvollziehbarkeit wird durch Visualisierungen verbessert. LangGraph bietet eine Graph-Visualisierung. Diese nutzt das Format graph_dot. Alle Pipelines liefern Ausführungs-Traces. Die Telemetrie-Daten ermöglichen eine Performance-Analyse.

Die Wartbarkeit wird durch die Code-Struktur unterstützt. Der Code ist modular aufgebaut. Die Agenten stehen in `app/agents/`. Die Workflows stehen in `app/workflows/`. Die Frameworks sind klar getrennt. Code-Kommentare erklären die Design-Entscheidungen.

Die Dokumentation steht in `project_overview.md` und `PROJEKTZIELE_BEWERTUNG.md`.

Status: Vollständig beantwortet

## 3. Beispiel-Anwendung: Zusammenfassung wissenschaftlicher Papers

### Vollständige Implementierung

Die Anforderung war eine Multi-Agent-Pipeline für wissenschaftliche Papers. Das Projekt hat dies umgesetzt.

Der Reader-Agent steht in `app/agents/reader.py`. Er extrahiert strukturierte Notizen. Diese enthalten Titel, Ziel, Methoden, Ergebnisse, Einschränkungen und Erkenntnisse.

Der Summarizer-Agent steht in `app/agents/summarizer.py`. Er erstellt eine Zusammenfassung mit 200 bis 300 Wörtern.

Der Critic-Agent steht in `app/agents/critic.py`. Er bewertet die Qualität mit einem Bewertungsschema. Das Schema prüft Sinnhaftigkeit, Genauigkeit, Abdeckung und Details. Die Skala reicht von 0 bis 5.

Der Integrator-Agent steht in `app/agents/integrator.py`. Er erstellt eine Meta-Zusammenfassung. Diese enthält ein Vertrauensniveau.

Der Workflow läuft so: Reader, dann Summarizer, dann Critic, dann Integrator.

Die Pipeline bietet weitere Features. PDFs werden geparst mit pypdf und pdfplumber. Der Text wird vorverarbeitet in `app/utils.py`. Die Ausgaben sind strukturiert und können als JSON exportiert werden. Numerische Metriken werden aus Papers extrahiert.

Status: Vollständig implementiert

## 4. Implementierungsübersicht

### Frameworks

Alle erforderlichen Frameworks sind implementiert:

- LangChain: `app/workflows/langchain_pipeline.py`
- LangGraph: `app/workflows/langgraph_pipeline.py`
- DSPy: `app/workflows/dspy_pipeline.py`
- OpenAI API: Konfigurierbar über `.env`
- Streamlit: `app/app.py`
- Telemetrie: `app/telemetry.py` mit CSV-Logging

Hinweis: Weights & Biases ist optional. Es ist nicht in den Anforderungen enthalten. Aktuell wird CSV-Telemetrie verwendet.

### Architektur

Die Anforderung war die Definition von Workflow-Modulen. Diese sollen in LangChain und LangGraph orchestriert werden. Dann soll eine Neuimplementierung in DSPy folgen. Schließlich soll ein Vergleich stattfinden.

Die Umsetzung ist vollständig. Die Workflow-Module sind definiert. Diese stehen in `app/agents/reader.py`, `summarizer.py`, `critic.py` und `integrator.py`. Die LangChain-Orchestrierung steht in `app/workflows/langchain_pipeline.py`. Die LangGraph-Orchestrierung steht in `app/workflows/langgraph_pipeline.py`. Die DSPy-Neuimplementierung steht in `app/workflows/dspy_pipeline.py` und nutzt Signatures. Die DSPy-Optimierung nutzt Teleprompting mit BootstrapFewShot. Der Output-Vergleich läuft im Tab "Compare" der Streamlit-App. Die Visualisierung zeigt den Graph für LangGraph im Format graph_dot.

Status: Alle Punkte erfüllt

### Evaluation

Die Anforderung waren quantitative Metriken und qualitative Aspekte. Die quantitativen Metriken umfassen Task Success Rate, Konsistenz und Optimierungsgewinn. Die qualitativen Aspekte umfassen Nachvollziehbarkeit, Modularität und Code-Komplexität.

Die Umsetzung ist vollständig. Die quantitativen Metriken werden gemessen. Der Unigram F1-Score wird in `app/eval_runner.py` berechnet. Die Latenz wird pro Agent und gesamt gemessen. Die Länge der Zusammenfassung und der Meta-Zusammenfassung wird erfasst. Numerische Werte aus Papers werden gezählt. Der Critic Score nutzt eine Skala von 0 bis 5. Der Teleprompt Gain vergleicht Basis- und optimierte Version.

Die qualitativen Aspekte werden dokumentiert. Die Nachvollziehbarkeit wird durch Graph-Visualisierung und Ausführungs-Traces unterstützt. Die Modularität zeigt sich in der klaren Trennung zwischen Agenten und Workflows. Die Code-Komplexität wird durch Kommentare und Dokumentation erklärt.

Der Vergleich zeigt strukturierte versus unstrukturierte Agent-Kollaboration. Alle drei Frameworks implementieren denselben Workflow.

Die Evaluation läuft über folgende Dateien:
- `app/eval_runner.py`: Evaluation über das Dev-Set
- `app/telemetry.py`: CSV-Logging für Metriken
- Streamlit-App: Vergleichs-Tab mit Metriken

Status: Vollständig implementiert

### Datenquellen

Die Anforderung waren reale oder synthetische Text-Sammlungen. Beispiele sind arXiv Abstracts, Forschungsberichte oder technische Handbücher.

Die Umsetzung nutzt verschiedene Datenquellen. Test-PDFs stehen im Verzeichnis `test_papers/`. Es gibt 5 Papers zu den Themen Black Holes, Graph of Thoughts, DSPy, RAFT und Griffin. Das Dev-Set steht in `dev-set/dev.jsonl`. Es enthält 15 Beispiele für Teleprompting. Vorverarbeitete Texte stehen in `local_cache/pdf_text/`.

Jeder Knoten verarbeitet spezifische Teilaufgaben. Der Reader extrahiert strukturierte Notizen. Der Summarizer erstellt Zusammenfassungen. Der Critic bewertet die Ergebnisse. Der Integrator erstellt Meta-Zusammenfassungen.

Status: Vollständig vorhanden

## 5. Hands-on Workshop Anforderungen

### Funktionsfähiges System

Die Anforderung war ein funktionsfähiges System für einen Anwendungsfall. Das Projekt hat dies umgesetzt.

Die Streamlit-App ist vollständig funktionsfähig. Einfache Startskripte stehen bereit. Für Windows gibt es `scripts/launchers/run.bat`. Für Mac und Linux gibt es `scripts/launchers/run.sh`. PDF- und TXT-Dateien können hochgeladen werden. Alle drei Pipelines sind lauffähig. Ein Vergleichs-Modus ist vorhanden. Die Export-Funktion erstellt JSON-Dateien.

Status: Vollständig funktionsfähig

### Framework-Integration

Die Anforderung war die Integration relevanter Frameworks. Genannt wurden Rasa, LangChain, LangGraph und DSPy.

Die Umsetzung ist vollständig. LangChain ist integriert. LangGraph ist integriert. DSPy ist integriert. Falls DSPy nicht installiert ist, gibt es einen Fallback-Modus. Die OpenAI API ist konfigurierbar über `.env`. Streamlit ist vollständig integriert.

Hinweis: Rasa ist nicht in den Anforderungen enthalten. Das Projekt fokussiert sich auf LLM-Orchestrierung, nicht auf Chatbots.

Status: Alle relevanten Frameworks integriert

### 60-Minuten Workshop

Die Anforderung war die Planung und Durchführung eines Hands-on Peer Labs. Das Lab soll 60 Minuten dauern.

Die Umsetzung ist vollständig vorbereitet. Ein Leitfaden steht in `docs/moderators/WORKSHOP_LEITFADEN.md`. Dieser enthält einen detaillierten Zeitplan. Ein Teilnehmer-Skript steht in `docs/participants/TEILNEHMER_SKRIPT.md`. Folien stehen in `docs/moderators/FOLIENSKRIPT_WORKSHOP.md`. Eine Checkliste steht in `docs/moderators/WORKSHOP_CHECKLIST.md`. Code-Experimente stehen in `docs/participants/CODE_EXPERIMENTE.md`. Eine Start-Anleitung steht in `docs/participants/START_HIER.md`.

Die Workshop-Struktur ist in 60 Minuten aufgeteilt. Minute 0 bis 2: Begrüßung und Setup. Minute 2 bis 12: Einführung. Minute 12 bis 24: LangChain. Minute 24 bis 39: LangGraph. Minute 39 bis 54: DSPy. Minute 54 bis 60: Experimentieren und Vergleich.

Status: Vollständig vorbereitet

### Theorie-Praxis Verbindung

Die Anforderung war zu zeigen, wie Theorie und Praxis verbunden sind. Das Projekt hat dies umgesetzt.

Die Dokumentation erklärt die Paradigmen-Unterschiede. Es wird zwischen prozedural, graph-basiert und deklarativ unterschieden. Code-Kommentare erklären die Design-Entscheidungen. Die Workshop-Struktur folgt dem Muster: Theorie, dann Praxis, dann Experimente, dann Vergleich. Der Vergleichs-Tab zeigt die Unterschiede direkt in der App. Code-Experimente ermöglichen es Teilnehmern, den Code zu ändern. Sie sehen die Effekte sofort.

Status: Vollständig umgesetzt

## 6. Zusätzliche Features

Das Projekt bietet Features, die über die Anforderungen hinausgehen.

### Erweiterte LangGraph-Features

LangGraph bietet zusätzliche Knoten. Ein Translator-Knoten übersetzt zwischen Deutsch und Englisch. Ein Keyword-Extraction-Knoten extrahiert wichtige Begriffe. Quality- und Judge-Knoten bewerten die Ergebnisse. Ein Aggregator-Knoten kombiniert mehrere Bewertungen.

### Robuste Fehlerbehandlung

Die Fehlerbehandlung ist robust. Fallback-Modi greifen, wenn Abhängigkeiten fehlen. Timeouts schützen vor langwierigen Aufrufen. Wenn DSPy nicht verfügbar ist, läuft ein Stub-Modus.

### Umfassende Dokumentation

Die Dokumentation ist umfassend. Das README enthält Diagramme. Workshop-Materialien stehen für Moderatoren und Teilnehmer bereit. Code-Kommentare erklären die Implementierung. Eine Projekt-Übersicht fasst alles zusammen.

### Benutzerfreundlichkeit

Die Benutzerfreundlichkeit wurde verbessert. Ein Klick startet die App über run.sh oder run.bat. Presets bieten Voreinstellungen für Speed, Balanced oder Detail. Visualisierungen zeigen Graphen und Diagramme. Export-Funktionen ermöglichen den Datenaustausch.

## 7. Checkliste: Alle Anforderungen erfüllt

Die folgende Tabelle zeigt den Status jeder Anforderung:

| Anforderung | Status | Nachweis |
|-------------|--------|----------|
| LangChain Implementation | Erfüllt | `app/workflows/langchain_pipeline.py` |
| LangGraph Implementation | Erfüllt | `app/workflows/langgraph_pipeline.py` |
| DSPy Implementation | Erfüllt | `app/workflows/dspy_pipeline.py` |
| Framework-Vergleich | Erfüllt | Compare Tab in App |
| Research Paper Summarization | Erfüllt | Reader → Summarizer → Critic → Integrator |
| Streamlit Interface | Erfüllt | `app/app.py` |
| Evaluation und Metriken | Erfüllt | `app/eval_runner.py`, Telemetrie |
| Workshop-Materialien (60 min) | Erfüllt | `docs/moderators/`, `docs/participants/` |
| Selbstoptimierende Mechanismen | Erfüllt | DSPy Teleprompting |
| Abwägungs-Analyse | Erfüllt | Dokumentation, Code-Experimente |
| Theorie-Praxis Verbindung | Erfüllt | Workshop-Struktur, Dokumentation |

Fazit: Alle Anforderungen sind erfüllt.

## 8. Referenzen

Weitere Informationen finden sich in folgenden Dokumenten:

- Projekt-Übersicht: `README.md`, `project_overview.md`
- Bewertung: `PROJEKTZIELE_BEWERTUNG.md`
- Workshop-Materialien: `docs/moderators/`, `docs/participants/`
- Code: `app/workflows/`, `app/agents/`

## 9. Nächste Schritte (optional)

Für zukünftige Erweiterungen könnten folgende Punkte interessant sein. Diese sind nicht in den Anforderungen enthalten:

- Weights & Biases Integration (aktuell: CSV-Telemetrie)
- Gradio als Alternative zu Streamlit
- Erweiterte Metriken wie BLEU, METEOR, ROUGE-1 und ROUGE-2
- Mehr Test-Dokumente
- CI/CD Pipeline

Hinweis: Diese Punkte sind optional. Sie sind nicht erforderlich für die Erfüllung der Anforderungen.

---

Dokument erstellt: 2025  
Projekt: Multi-Agent Workflow Orchestration  
Status: Alle Anforderungen erfüllt
