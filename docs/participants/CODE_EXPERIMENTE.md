# Code Experimente

Diese Datei liefert kurze Code Beispiele, die ihr direkt übernehmen oder anpassen könnt.

## 1. Summarizer kürzer oder länger machen
- Datei: `app/agents/summarizer.py`
- Sucht das Prompt in Zeile 10 und passt den Text an (z. B. „very brief“ oder „detailed“).
- Ergebnis: GPT erzeugt eine kürzere oder längere Zusammenfassung.

## 2. Critic um Klarheit erweitern
- Datei: `app/agents/critic.py`
- Erweitert die Rubric um „Clarity“ und schreibt das Ausgabeformat entsprechend neu.
- Ergebnis: Der Critic gibt zusätzlich einen Klarheitswert aus.

## 3. LangChain Reihenfolge testen
- Datei: `app/workflows/langchain_pipeline.py`
- Führt den Critic vor dem Summarizer aus (Summary als leere Zeichenkette).
- Ergebnis: Ihr seht, dass die Reihenfolge die Logik bricht und warum LangChain die Abhängigkeiten nicht automatisch steuert.

## 4. Translator- & Keyword-Nodes beobachten und konfigurieren
- Datei: `app/workflows/langgraph_pipeline.py`
- Schaut euch `_execute_translator_node` an: Übersetzung wird bereits erzeugt, es gibt `translator_language` und `translator_style`, außerdem landet das Ergebnis in `state["summary_translated"]`.
- Modifiziert die Defaults, z. B. `translator_style="ultra_short"` oder `translator_language="EN"` und beobachtet, wie sich die Visualisierung und `summary_translated` verändern.
- Untersucht `_execute_keyword_node`: Dabei entstehen `state["keywords"]`. Ihr könnt z. B. die Länge der Tokens ändern oder mehr Keywords extrahieren.
- Ergebnis: Ihr erlebt live, wie neue Nodes die Graph-Visualisierung verändern und zusätzliche Informationen liefern.

## 5. Conditional Flow & Judge-Aggregator
- Datei: `app/workflows/langgraph_pipeline.py`
- Die Funktion `_critic_post_path` entscheidet, ob der Graph zu `quality`, direkt zu `judge` (für <100 Zeichen) oder zurück zum `summarizer` springt, wenn `critic_score < 0.5`.
- Anpassbar: Schwellenwerte ändern, `max_critic_loops` im `_config` verwenden oder weitere Bedingungen ergänzen.
- Der neue `aggregator` fasst `quality_f1`, `judge_score` und `critic_score` zusammen (`state["judge_aggregate"]`), die ihr für Vergleiche nutzen könnt.
- Ergebnis: Der Graph zeigt dynamische Verzweigungen und aggregierte Bewertungen, die ihr im Workshop diskutieren könnt.

## 6. DSPy Signature variieren
- Datei: `app/workflows/dspy_pipeline.py`
- Passt die Beschreibung der `Summarize`-Signature an (z. B. „focused on RESULTS“, „very brief summary“).
- DSPy erstellt automatisch den Prompt neu.

## 7. Ziel Länge als Input für DSPy
- `Summarize`-Signature um `TARGET_LENGTH` erweitern (InputField mit Beschreibung).
- In den `forward`-Methoden `target_length` übergeben und in der Pipeline `self.summarizer(notes, "short")` nutzen.
- Ergebnis: Ihr steuert die Länge über einen Parameter.

## Tipps
1. Speichern, dann testen.
2. Bei Syntaxfehlern auf Einrückungen und Anführungszeichen achten.
3. App neu starten, wenn Änderungen nicht wirken.
4. Nur eine Änderung pro Test.
5. Backup der Original Dateien behalten.
