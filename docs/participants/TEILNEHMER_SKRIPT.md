# Workshop Skript für Teilnehmer

## Ziel

- Ihr experimentiert mit drei Frameworks für den gleichen Multi Agent Workflow (Reader, Summarizer, Critic, Integrator) und versteht dadurch folgende Punkte:
- Was Multi Agent Orchestrierung ist und warum sie hilft
- Wie LangChain (Sequenziell), LangGraph (Graph) und DSPy (Deklarativ) sich unterscheiden
- Wie sich Code Anpassungen auf das Verhalten auswirken
- Wie ihr neue Nodes oder Signatures ergänzt

## Ablauf (60 Minuten)
1. Setup & Einführung (5-10 min)
2. LangChain: Pipeline ausführen, Prompts anpassen, Reihenfolge verstehen (12 min)
3. LangGraph: Graph prüfen, Node hinzufügen, Conditional Edge testen (15 min)
4. DSPy: Signatures anpassen, zusätzliche Inputs nutzen (15 min)
5. Vergleich & Fragen (3 min)

## Vorbereitungen
- Streamlit App per Doppelklick auf `launchers/run.*` starten oder manuell `python -m streamlit run app/app.py`
- Editor öffnen und folgende Dateien laden:
  - `app/agents/reader.py`
  - `app/agents/summarizer.py`
  - `app/agents/critic.py`
  - `app/workflows/langchain_pipeline.py`
  - `app/workflows/langgraph_pipeline.py`
  - `app/workflows/dspy_pipeline.py`
- Optional: `docs/participants/CODE_EXPERIMENTE.md` für schnelle Beispiele verwenden
- Testdokument hochladen (PDF oder TXT, 2-3 Seiten)

## Teil 1: LangChain verstehen
### Was passiert?
- Die Pipeline läuft strikt sequenziell: Reader → Summarizer → Critic → Integrator
- Jeder Agent führt sich erst aus, wenn der vorherige fertig ist
- Abhängigkeiten entstehen durch die Reihenfolge, nicht durch explizite Verbindungen

### Aufgabe: Prompt ändern
- Öffnet `app/agents/summarizer.py` und sucht den Prompt Text (ca. Zeile 9)
- Ändert die Anweisung, z. B. „very brief summary (50-100 words)“ statt „200-300 words“
- Speichert die Datei und führt LangChain erneut aus
- Beobachtet, wie sich die Summary Länge verändert

### Aufgabe: Critic Rubric erweitern
- Öffnet `app/agents/critic.py`
- Fügt unter der Rubric eine neue Kategorie hinzu, z. B. `Clarity` oder `Relevance`
- Ergänzt dafür auch den Abschnitt `OUTPUT FORMAT`, damit der Critic den neuen Score liefert
- Startet die Pipeline neu und schaut, welche Werte ausgegeben werden

### Aufgabe: Reihenfolge testen
- Öffnet `app/workflows/langchain_pipeline.py`
- Macht den Critic Aufruf vor den Summarizer (Summary Parameter zunächst leer)
- Startet die Pipeline und beobachtet, warum das nicht funktioniert oder welche Fehlermeldung erscheint
- Das zeigt, warum die Reihenfolge wichtig ist

## Teil 2: LangGraph erweitern
### Struktur ansehen
- LangGraph definiert Nodes und Edges in `app/workflows/langgraph_pipeline.py`
- Ihr seht, wie Inputs, Reader, Summarizer, Critic und Integrator verknüpft sind

### Aufgabe: Translator- & Keyword-Nodes beobachten
- Die Nodes existieren bereits. Schaut euch `_execute_translator_node` an: Erzeugt `state["summary_translated"]`, der sich durch `translator_language` und `translator_style` beeinflussen lässt.
- Probiert unterschiedliche Einstellungen aus (z. B. `translator_style="ultra_short"` oder `translator_language="EN"`) und beobachtet die neuen Labels in der Visualisierung.
- Der Keyword-Node (`_execute_keyword_node`) füllt `state["keywords"]` und zeigt die wichtigsten Begriffe. Ihr könnt z. B. die Token-Länge oder Anzahl ändern.
- Wichtig: Die Ausgabe zeigt nun bereits `summary_translated` und `keywords`, ohne dass ihr etwas neu anschließt.

### Aufgabe: Conditional Flow & Judge-Aggregator
- In `_critic_post_path` steckt die Logik, die entscheidet:
  - Kurze Summaries (<100 Zeichen) springen zu `judge`,
  - Schlechte Critic-Scores (<0.5) führen zur Loop zurück zum Summarizer (maximal `max_critic_loops`, Default 1),
  - Sonst geht es zu `quality`.
- Der Judge-Node liefert einen Score 0-5, `aggregator` verrechnet Judge, Quality und Critic zu `state["judge_aggregate"]`.
- Versucht, Schwellenwerte oder `max_critic_loops` in `_config` anzupassen und beobachtet in der Visualisierung, wie sich die Zweige verändern.

## Teil 3: DSPy anpassen
### Signatures variieren
- DSPy nutzt `dspy.Signature`, z. B. `class Summarize(dspy.Signature)`
- Ändert die Beschreibung (Short Summary, Fokus auf Results etc.) und beobachtet, wie DSPy den Prompt automatisch anpasst

### Zusätzlichen Input ergänzen
- Fügt `TARGET_LENGTH` als InputField hinzu (`short`, `medium`, `long`)
- In der `forward`-Methode den Parameter berücksichtigen und an `self.gen` übergeben
- In der Pipeline (`PaperPipeline.forward`) z. B. `self.summarizer(notes, "short")` aufrufen
- Startet DSPy und seht, wie die Länge gesteuert werden kann

## Teil 4: Zusammenfassung & Vergleich
- Vergleicht die drei Pipelines in der App mit verschiedenen Dokumenten
- Diskutiert:
  - Welche Pipeline ist einfacher zu verstehen?
  - Wo ist mehr Kontrolle nötig?
  - Wo lohnt sich automatische Optimierung?
- Dokumentiert wichtige Erkenntnisse und Fragen

## Fragen & Hilfe
- Nutzt `logs/telemetry.csv` (falls vorhanden) oder den Telemetry Tab für Laufzeiten
- Falls die App hängt: Strg+C im Terminal und neu starten
- Für Code Beispiele: `docs/participants/CODE_EXPERIMENTE.md`
