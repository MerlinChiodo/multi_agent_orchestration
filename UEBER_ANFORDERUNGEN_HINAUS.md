# Features die über die Anforderungen hinausgehen

Diese Liste zeigt alle Features, die **NICHT** in den ursprünglichen Anforderungen standen. Du kannst dann entscheiden, was entfernt werden soll.

---

## 1. LangGraph: Zusätzliche Nodes (über Reader→Summarizer→Critic→Integrator hinaus)

### **Translator Node**
- **Datei**: `app/workflows/langgraph_pipeline.py` (Zeile 257-283)
- **Was macht es**: Erstellt DE/EN Übersetzungs-Vorschau der Summary
- **Verwendung**: Wird zwischen Summarizer und Critic ausgeführt
- **Entfernen?**: [ ] JA  [ ] NEIN

### **Keyword Extraction Node**
- **Datei**: `app/workflows/langgraph_pipeline.py` (Zeile 286-306)
- **Was macht es**: Extrahiert häufigste Keywords aus der Summary
- **Verwendung**: Wird zwischen Translator und Critic ausgeführt
- **Entfernen?**: [ ] JA  [ ] NEIN

### **Results Extractor Node (Recovery-Pfad)**
- **Datei**: `app/workflows/langgraph_pipeline.py` (Zeile 172-196)
- **Was macht es**: Extrahiert quantitative Metriken, wenn Reader sie verpasst hat
- **Verwendung**: Conditional Edge nach Reader, wenn quantitative Signale erkannt wurden
- **Entfernen?**: [ ] JA  [ ] NEIN

### **Quality Node (F1/ROUGE-L Berechnung)**
- **Datei**: `app/workflows/langgraph_pipeline.py` (Zeile 334-352)
- **Was macht es**: Berechnet F1-Score und ROUGE-L zwischen Notes und Summary
- **Verwendung**: Conditional Edge nach Critic (für längere Summaries)
- **Entfernen?**: [ ] JA  [ ] NEIN

### **Judge Node (LLM-as-a-Judge)**
- **Datei**: `app/workflows/langgraph_pipeline.py` (Zeile 386-409)
- **Was macht es**: LLM bewertet Summary mit Score 0-5
- **Verwendung**: Conditional Edge nach Critic (für kurze Summaries) oder nach Quality
- **Entfernen?**: [ ] JA  [ ] NEIN

### **Aggregator Node**
- **Datei**: `app/workflows/langgraph_pipeline.py` (Zeile 410-420)
- **Was macht es**: Aggregiert Judge-, Quality- und Critic-Scores zu einem Gesamtwert
- **Verwendung**: Nach Judge, vor Integrator
- **Entfernen?**: [ ] JA  [ ] NEIN

---

## 2. Quantitative Signal Detection

### **Quantitative Signal Detection Funktion**
- **Datei**: `app/utils.py` (Zeile 306-359)
- **Was macht es**: Erkennt heuristisch, ob Text quantitative Metriken enthält
- **Verwendung**: 
  - Wird in allen Pipelines verwendet
  - Steuert Results Extractor Recovery-Pfad in LangGraph
  - Wird in UI angezeigt
- **Entfernen?**: [ ] JA  [ ] NEIN

### **Quantitative Signal Anzeige in UI**
- **Datei**: `app/app.py` (Zeile 374-384)
- **Was macht es**: Zeigt "Quantitative signal: YES/MAYBE/NO" im Execution Trace
- **Entfernen?**: [ ] JA  [ ] NEIN

---

## 3. Erweiterte Metriken (über F1 hinaus)

### **ROUGE-L Metrik**
- **Datei**: `app/eval_runner.py`, `app/workflows/langgraph_pipeline.py`
- **Was macht es**: Berechnet ROUGE-L (LCS-basiert) zusätzlich zu F1
- **Verwendung**: Wird in LangGraph Quality Node und Evaluation verwendet
- **Entfernen?**: [ ] JA  [ ] NEIN

### **Judge Score (0-5)**
- **Datei**: `app/workflows/langgraph_pipeline.py` (Judge Node)
- **Was macht es**: LLM-basierte Bewertung der Summary
- **Entfernen?**: [ ] JA  [ ] NEIN

### **Judge Aggregate Score**
- **Datei**: `app/workflows/langgraph_pipeline.py` (Aggregator Node)
- **Was macht es**: Kombiniert mehrere Scores zu einem Gesamtwert
- **Entfernen?**: [ ] JA  [ ] NEIN

---

## 4. UI Features (über Basis-Funktionalität hinaus)

### **Translator/Keyword Anzeige in UI**
- **Datei**: `app/app.py` (Zeile 407-415)
- **Was macht es**: Zeigt Translator-Note und Keywords im Execution Trace
- **Entfernen?**: [ ] JA  [ ] NEIN

### **Erweiterte Execution Trace Details**
- **Datei**: `app/app.py` (Zeile 386-416)
- **Was macht es**: Zeigt viele Details: quantitative signal, loops, routing, translator, keywords
- **Entfernen?**: [ ] JA  [ ] NEIN

### **ROUGE-L Metrik-Anzeige**
- **Datei**: `app/app.py` (Zeile 365-369)
- **Was macht es**: Zeigt ROUGE-L Score als Metrik
- **Entfernen?**: [ ] JA  [ ] NEIN

### **Critic Loops Anzeige**
- **Datei**: `app/app.py` (Zeile 371-372, 402-406)
- **Was macht es**: Zeigt wie oft LangGraph zurück zum Summarizer geloopt hat
- **Entfernen?**: [ ] JA  [ ] NEIN

---

## 5. Code-Features

### **Timeout-Mechanismus**
- **Datei**: `app/workflows/langgraph_pipeline.py` (Zeile 70-95)
- **Was macht es**: Timeout-Wrapper für alle Node-Ausführungen
- **Verwendung**: Verhindert hängende Nodes
- **Entfernen?**: [ ] JA  [ ] NEIN

### **Routing Trace**
- **Datei**: `app/workflows/langgraph_pipeline.py` (Zeile 60-68)
- **Was macht es**: Loggt welche Conditional Edges genommen wurden
- **Entfernen?**: [ ] JA  [ ] NEIN

### **Graph DOT Visualisierung (erweitert)**
- **Datei**: `app/workflows/langgraph_pipeline.py` (Zeile 440-520)
- **Was macht es**: Erweiterte Graph-Visualisierung mit allen zusätzlichen Nodes
- **Hinweis**: Basis-Graph-Visualisierung ist in Anforderungen, aber die erweiterte Version mit Translator/Keyword/Judge/Aggregator ist optional
- **Entfernen?**: [ ] JA  [ ] NEIN

### **LangGraph Visual Datei**
- **Datei**: `app/workflows/langgraph_visual.py`
- **Was macht es**: Separate Datei für Graph-Visualisierung (wird aber nicht verwendet)
- **Entfernen?**: [ ] JA  [ ] NEIN

---

## 6. Dokumentation (möglicherweise zu umfangreich)

### **CODE_EXPERIMENTE.md**
- **Datei**: `docs/participants/CODE_EXPERIMENTE.md`
- **Was macht es**: Zusätzliche Code-Beispiele für Experimente
- **Entfernen?**: [ ] JA  [ ] NEIN

### **WORKSHOP_CODE_BEREITSTELLUNG.md**
- **Datei**: `docs/moderators/WORKSHOP_CODE_BEREITSTELLUNG.md`
- **Was macht es**: Zusätzliche Anleitung für Code-Bereitstellung
- **Entfernen?**: [ ] JA  [ ] NEIN

### **generate_pptx.py**
- **Datei**: `docs/moderators/generate_pptx.py`
- **Was macht es**: Script zum Generieren von PowerPoint aus Markdown
- **Entfernen?**: [ ] JA  [ ] NEIN

### **FOLIENSKRIPT_WORKSHOP.pptx**
- **Datei**: `docs/moderators/FOLIENSKRIPT_WORKSHOP.pptx`
- **Was macht es**: PowerPoint-Präsentation (zusätzlich zu Markdown)
- **Entfernen?**: [ ] JA  [ ] NEIN

---

## 7. Test-Daten

### **Mehrere Test-PDFs**
- **Datei**: `test_papers/` (5 PDFs)
- **Was macht es**: Mehrere Beispiel-PDFs zum Testen
- **Anforderung**: Nur "real or synthetic text collections" erwähnt, keine spezifische Anzahl
- **Entfernen?**: [ ] JA  [ ] NEIN (welche behalten?)

---

## 8. Dev-Set Features

### **target_length und prompt_focus Tags im Dev-Set**
- **Datei**: `dev-set/dev.jsonl`
- **Was macht es**: Jedes Beispiel hat `target_length` (short/medium/long) und `prompt_focus` (Results/Method/Conclusion)
- **Verwendung**: Wird in DSPy Teleprompting verwendet, um zu zeigen wie DSPy adaptiert
- **Entfernen?**: [ ] JA  [ ] NEIN (vereinfachen zu nur text + target_summary?)

---

## Zusammenfassung: Minimal-Anforderung vs. Aktuell

### **Minimal-Anforderung (laut Modul):**
- Reader → Summarizer → Critic → Integrator
- LangChain: Sequenziell
- LangGraph: Graph mit Conditional Edges (Loop zurück bei schlechtem Critic)
- DSPy: Signatures + optional Teleprompting
- Basis-Evaluation: F1-Score
- Streamlit UI: Upload, Pipeline-Auswahl, Vergleich

### **Aktuell zusätzlich:**
- Translator Node
- Keyword Node
- Results Extractor Node
- Quality Node (F1 + ROUGE-L)
- Judge Node
- Aggregator Node
- Quantitative Signal Detection
- ROUGE-L Metrik
- Erweiterte UI-Anzeigen
- Timeout-Mechanismus
- Routing Trace
- Erweiterte Graph-Visualisierung

---

## Empfehlung für Vereinfachung

**Kern-Workflow beibehalten:**
- Reader → Summarizer → Critic → Integrator 
- Conditional Edge: Loop zurück bei schlechtem Critic 
- Basis-Metriken: F1-Score 

**Kandidaten zum Entfernen (wenn vereinfachen gewünscht):**
1. Translator Node (nicht in Anforderungen)
2. Keyword Node (nicht in Anforderungen)
3. Results Extractor Node (Recovery-Pfad, nicht in Anforderungen)
4. Quality Node (F1 könnte direkt im Critic berechnet werden)
5. Judge Node (nicht in Anforderungen)
6. Aggregator Node (nicht in Anforderungen)
7. ROUGE-L (nur F1 war gefordert)
8. Quantitative Signal Detection (nicht explizit gefordert)

**Behalten (wichtig für Workshop):**
- Conditional Edges (Loop zurück) 
- Graph-Visualisierung (Basis) 
- Telemetrie 
- Workshop-Materialien 

---

**Nächster Schritt:** Markiere oben mit [X] was entfernt werden soll, dann entferne ich es!
