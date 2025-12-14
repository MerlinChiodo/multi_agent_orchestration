# Multi-Agent Orchestration - Vollständige Projekt-Erklärung

## 📋 Inhaltsverzeichnis
1. [Projekt-Überblick](#projekt-überblick)
2. [Design-Entscheidungen & Gedanken](#design-entscheidungen--gedanken)
3. [Ordnerstruktur & Was ist wo?](#ordnerstruktur--was-ist-wo)
4. [Workshop-Planung](#workshop-planung)

---

## 🎯 Projekt-Überblick

### Was haben wir gebaut?

Ein **Multi-Agent Paper Analyzer** - ein System, das wissenschaftliche Paper automatisch analysiert, indem es mehrere spezialisierte LLM-Agenten orchestriert (koordiniert).

**Kernidee:** Statt einen riesigen Prompt zu schreiben ("Analysiere dieses Paper komplett"), teilen wir die Aufgabe auf vier spezialisierte Agenten auf:
- **Reader**: Extrahiert strukturierte Notizen
- **Summarizer**: Erstellt Zusammenfassung
- **Critic**: Bewertet Qualität
- **Integrator**: Erstellt finale Meta-Summary

**Besonderheit:** Wir haben den **gleichen Workflow** mit **drei verschiedenen Frameworks** implementiert, um die Unterschiede zu zeigen:
- **LangChain**: Sequenziell, einfach
- **LangGraph**: Graph-basiert, transparent
- **DSPy**: Deklarativ, selbstoptimierend

---

## 💡 Design-Entscheidungen & Gedanken

### 1. Warum Multi-Agent statt einem großen Prompt?

**Problem:** Ein einzelner riesiger Prompt ist schwer zu kontrollieren, zu debuggen und zu optimieren.

**Lösung:** Aufteilen in spezialisierte Agenten. Jeder Agent hat eine klare Aufgabe:
- **Reader** konzentriert sich nur auf Extraktion → bessere Struktur
- **Summarizer** konzentriert sich nur auf Zusammenfassung → bessere Lesbarkeit
- **Critic** konzentriert sich nur auf Bewertung → objektivere Kritik
- **Integrator** kombiniert alles → bessere Meta-Summary

**Vorteil:** Wie in einer Fabrik - jeder Arbeiter macht einen spezifischen Schritt, das Ergebnis ist besser als wenn einer alles macht.

---

### 2. Warum drei verschiedene Frameworks?

**Ziel:** Den gleichen Workflow mit unterschiedlichen Ansätzen zeigen, damit Teilnehmer die Trade-offs verstehen.

**LangChain (Sequenziell):**
- **Gedanke:** "Einfachheit zuerst" - für schnelle Prototypen
- **Design:** Einfache Funktionsaufrufe nacheinander
- **Vorteil:** Schnell zu verstehen, wenig Code
- **Nachteil:** Keine explizite Struktur, schwer zu erweitern

**LangGraph (Graph-basiert):**
- **Gedanke:** "Transparenz und Kontrolle" - für komplexe Workflows
- **Design:** Expliziter Graph mit Nodes und Edges
- **Vorteil:** Struktur ist sichtbar, leicht erweiterbar, Conditional Logic möglich
- **Nachteil:** Mehr Code, komplexere Konzepte

**DSPy (Deklarativ):**
- **Gedanke:** "Automatische Optimierung" - für reproduzierbare Systeme
- **Design:** Signatures statt explizite Prompts
- **Vorteil:** Framework optimiert Prompts automatisch
- **Nachteil:** Weniger Kontrolle über exakte Prompts

**Warum wichtig?** In der Praxis muss man entscheiden, welches Framework für welchen Use Case passt. Durch praktische Experimente versteht man die Unterschiede besser.

---

### 3. Warum Streamlit als UI?

**Gedanke:** Teilnehmer sollen sofort loslegen können, ohne komplexe Setup-Schritte.

**Vorteile:**
- **Einfach:** Ein Befehl startet die App
- **Interaktiv:** Upload, Buttons, Visualisierungen
- **Vergleich:** Alle drei Pipelines nebeneinander testen
- **Telemetrie:** CSV-Logging für Analyse

**Alternative wäre:** Command-Line-Tool, aber das ist weniger zugänglich für Workshop-Teilnehmer.

---

### 4. Warum Text-Vorverarbeitung (utils.py)?

**Problem:** PDFs sind oft schlecht formatiert:
- Getrennte Wörter durch Zeilenumbrüche
- Metadaten (Autoren, Affiliations) am Anfang
- Literaturverzeichnis am Ende
- Überflüssige Leerzeichen

**Lösung:** `utils.py` normalisiert den Text:
- **`_normalize_text()`**: Behebt PDF-Probleme (getrennte Wörter, Leerzeichen)
- **`strip_meta_head()`**: Entfernt Metadaten am Anfang
- **`strip_references_tail()`**: Entfernt Literaturverzeichnis
- **`split_sections()`**: Erkennt Abschnitte (Abstract, Methods, Results, etc.)

**Warum wichtig?** Sauberer Text = bessere LLM-Ergebnisse. Wenn der LLM mit Metadaten und Literaturverzeichnis konfrontiert wird, verliert er Fokus.

---

### 5. Warum Telemetrie (telemetry.py)?

**Gedanke:** Metriken sammeln, um Performance zu verstehen.

**Was wird geloggt:**
- Welche Pipeline (LangChain/LangGraph/DSPy)
- Laufzeiten pro Agent
- Text-Längen (Input, Summary, Meta)
- Qualitäts-Metriken (F1, Judge-Score)

**Warum CSV?** Einfach zu analysieren, keine externe Datenbank nötig. Optional: W&B-Integration für erweiterte Visualisierung.

**Nutzen:** Teilnehmer können sehen, welche Pipeline schneller ist, welche bessere Ergebnisse liefert, etc.

---

### 6. Warum Doppelklick-Start (run.bat / run.sh)?

**Gedanke:** Minimale Hürden für Workshop-Teilnehmer.

**Was macht das Skript automatisch?**
1. Prüft Python-Installation
2. Erstellt Virtual Environment (falls nötig)
3. Installiert Dependencies
4. Erstellt `.env` Datei (falls nötig)
5. Startet Streamlit-App

**Warum wichtig?** Teilnehmer sollen sich auf den Workshop konzentrieren, nicht auf Setup-Probleme. Ein Doppelklick = fertig.

---

### 7. Warum Quality- und Judge-Nodes nur in LangGraph?

**Gedanke:** Zeigen, dass LangGraph erweiterbarer ist.

**Quality Node:** Berechnet F1-Score zwischen Notes und Summary (automatische Metrik)

**Judge Node:** LLM-as-a-Judge bewertet Qualität (0-5 Score)

**Warum nur in LangGraph?**
- In LangChain müsste man sie manuell nach jedem Schritt einfügen
- In LangGraph sind sie einfach Nodes im Graph - Teil der Struktur
- Zeigt: Graph-basierte Struktur macht Erweiterungen einfacher

**Lernziel:** Teilnehmer sehen, dass LangGraph nicht nur komplexer ist, sondern auch mächtiger.

---

### 8. Warum DSPy Teleprompting optional?

**Gedanke:** Zeigen, dass DSPy selbstoptimierend ist, aber auch Zeit kostet.

**Teleprompting:** DSPy testet verschiedene Prompts basierend auf Trainingsdaten (`eval/dev.jsonl`) und wählt die beste Variante.

**Warum optional?**
- Dauert 1-2 Minuten (vs. 10-20 Sekunden ohne)
- Braucht Dev-Set (Trainingsdaten)
- Zeigt Trade-off: Bessere Ergebnisse vs. längere Laufzeit

**Lernziel:** Teilnehmer verstehen, dass Optimierung Zeit kostet, aber bessere Ergebnisse liefern kann.

---

## 📁 Ordnerstruktur & Was ist wo?

### Root-Verzeichnis

```
multi_agent_orchestration/
├── agents/              # Die vier spezialisierten Agenten
├── workflows/           # Die drei Pipeline-Implementierungen
├── docs/                # Workshop-Dokumentation
├── eval/                # Evaluierungsdaten für DSPy
├── test_papers/         # Beispiel-PDFs zum Testen
├── venv/                # Virtual Environment (wird automatisch erstellt)
├── app.py               # Streamlit-Hauptanwendung
├── llm.py               # LLM-Konfiguration
├── utils.py             # Text-Vorverarbeitung
├── telemetry.py         # Metriken-Logging
├── eval_runner.py       # Evaluierungs-Skript
├── requirements.txt     # Python-Dependencies
├── run.bat              # Windows-Start-Skript
├── run.sh               # Mac/Linux-Start-Skript
└── README.md            # Projekt-Übersicht
```

---

### `agents/` - Die vier Agenten

**Gedanke:** Jeder Agent ist eine separate Datei, damit man sie einzeln anpassen kann.

- **`reader.py`**: Extrahiert strukturierte Notizen aus Text
  - **Was macht es?** Nimmt rohen Text, gibt strukturierte Notizen zurück (Title, Objective, Methods, Results, etc.)
  - **Warum so?** Klare Aufgabe, einfacher zu debuggen

- **`summarizer.py`**: Erstellt Zusammenfassung aus Notizen
  - **Was macht es?** Nimmt strukturierte Notizen, gibt 200-300 Wörter Summary zurück
  - **Warum so?** Fokus auf Lesbarkeit, nicht auf Extraktion

- **`critic.py`**: Bewertet Summary gegen Notes
  - **Was macht es?** Prüft Coherence, Groundedness, Coverage, Specificity (je 0-5)
  - **Warum so?** Objektive Bewertung durch strukturiertes Rubric

- **`integrator.py`**: Erstellt finale Meta-Summary
  - **Was macht es?** Kombiniert Notes, Summary und Critic zu finaler Meta-Summary
  - **Warum so?** Ein Ort, wo alles zusammenkommt

**Design-Entscheidung:** Alle Agenten nutzen `llm.py` für LLM-Calls. Warum? Zentrale Konfiguration - wenn man das Modell ändert, ändert man es nur einmal.

---

### `workflows/` - Die drei Pipeline-Implementierungen

**Gedanke:** Drei verschiedene Ansätze für den gleichen Workflow.

- **`langchain_pipeline.py`**: Sequenzielle Ausführung
  - **Wie?** Einfache Funktionsaufrufe nacheinander
  - **Code-Struktur:** `run_reader()` → `run_summarizer()` → `run_critic()` → `run_integrator()`
  - **Warum so?** Zeigt: Einfach, aber limitiert

- **`langgraph_pipeline.py`**: Graph-basierte Ausführung
  - **Wie?** Expliziter Graph mit Nodes und Edges
  - **Code-Struktur:** `StateGraph` → `add_node()` → `add_edge()` → `compile()`
  - **Zusätzlich:** Quality-Node (F1), Judge-Node (LLM-as-a-Judge)
  - **Warum so?** Zeigt: Komplexer, aber mächtiger

- **`dspy_pipeline.py`**: Deklarative Ausführung
  - **Wie?** Signatures statt explizite Prompts
  - **Code-Struktur:** `dspy.Signature` → `dspy.Module` → `dspy.Predict()`
  - **Zusätzlich:** Optionales Teleprompting (BootstrapFewShot)
  - **Warum so?** Zeigt: Deklarativ, selbstoptimierend

**Design-Entscheidung:** Alle drei nutzen die gleichen Agent-Funktionen aus `agents/`. Warum? Zeigt, dass die Frameworks unterschiedlich orchestrieren, aber die Agenten gleich bleiben.

---

### `docs/` - Workshop-Dokumentation

**Gedanke:** Getrennte Dokumentation für Teilnehmer und Moderatoren.

```
docs/
├── teilnehmer/          # Für Workshop-Teilnehmer
│   ├── START_HIER.md           # Einstiegspunkt
│   ├── TEILNEHMER_SKRIPT.md    # Hauptskript mit Aufgaben
│   └── CODE_EXPERIMENTE.md     # Code-Snippets zum Kopieren
│
└── moderatoren/        # Für Workshop-Moderatoren
    ├── WORKSHOP_LEITFADEN.md           # Zeitplan & Ablauf
    ├── WORKSHOP_CHECKLIST.md           # Vorbereitung
    └── WORKSHOP_CODE_BEREITSTELLUNG.md # Code-Verteilung
```

**Warum getrennt?** Teilnehmer brauchen andere Infos als Moderatoren. Teilnehmer: "Wie starte ich?" Moderatoren: "Wie führe ich den Workshop durch?"

---

### `eval/` - Evaluierungsdaten

- **`dev.jsonl`**: Dev-Set für DSPy Teleprompting
  - **Format:** Jede Zeile = JSON mit `{"text": "...", "target_summary": "..."}`
  - **Warum JSONL?** Einfach zu erweitern, eine Zeile = ein Beispiel
  - **Warum wichtig?** DSPy braucht Trainingsdaten für Teleprompting

**Design-Entscheidung:** Nur kleine Beispiele im Repo. Warum? Zeigt das Konzept, aber für echte Optimierung braucht man größere Datensätze.

---

### `test_papers/` - Beispiel-PDFs

**Gedanke:** Teilnehmer sollen sofort testen können, ohne eigene PDFs suchen zu müssen.

- Verschiedene Paper-Längen (kurz, mittel, lang)
- Verschiedene Themen (LLM Agents, Graph Reasoning, DSPy, RAG)

**Warum wichtig?** Schneller Start, keine Suche nach Testdaten nötig.

---

### `app.py` - Streamlit-Hauptanwendung

**Gedanke:** Zentrale UI für alle drei Pipelines.

**Struktur:**
- **Sidebar:** Settings (Model, Temperature, Max Tokens, Presets)
- **Tab 1 (Analysis):** Einzelne Pipeline ausführen
- **Tab 2 (Compare):** Alle drei Pipelines parallel vergleichen
- **Tab 3 (DSPy Optimization):** Base vs. Teleprompt vergleichen
- **Expander (Telemetry):** CSV-Logs anzeigen

**Design-Entscheidungen:**
- **Presets:** Speed/Balanced/Detail - warum? Teilnehmer sollen nicht überfordert werden mit zu vielen Optionen
- **Vergleichs-Tab:** Warum? Zeigt Unterschiede direkt nebeneinander
- **Graph-Visualisierung:** Nur bei LangGraph - warum? Zeigt den Vorteil von Graph-basierter Struktur

---

### `llm.py` - LLM-Konfiguration

**Gedanke:** Zentrale Konfiguration für alle LLM-Calls.

**Was macht es?**
- Lädt `.env` Datei (API-Key, Base-URL)
- Erstellt `ChatOpenAI` Instanz
- Konfiguriert Model, Temperature, Max Tokens, Timeout

**Warum zentral?** Alle Agenten nutzen die gleiche LLM-Instanz. Wenn man das Modell ändert, ändert man es nur einmal.

**Design-Entscheidung:** Globale Instanz statt Parameter-Weiterreichung. Warum? Einfacher zu nutzen, weniger Boilerplate.

---

### `utils.py` - Text-Vorverarbeitung

**Gedanke:** Sauberer Text = bessere LLM-Ergebnisse.

**Funktionen:**
- **`_normalize_text()`**: Behebt PDF-Probleme
- **`strip_meta_head()`**: Entfernt Metadaten
- **`strip_references_tail()`**: Entfernt Literaturverzeichnis
- **`split_sections()`**: Erkennt Abschnitte
- **`build_analysis_context()`**: Hauptfunktion - kombiniert alles

**Warum wichtig?** LLMs sind empfindlich auf Formatierung. Sauberer Text = bessere Extraktion.

---

### `telemetry.py` - Metriken-Logging

**Gedanke:** Daten sammeln für Analyse.

**Was wird geloggt?**
- Pipeline-Typ (LangChain/LangGraph/DSPy)
- Laufzeiten (gesamt, pro Agent)
- Text-Längen (Input, Summary, Meta)
- Qualitäts-Metriken (F1, Judge-Score)

**Format:** CSV (`telemetry.csv`)

**Optional:** W&B-Integration (wenn `WANDB_ENABLED=1`)

**Warum CSV?** Einfach zu analysieren, keine externe Datenbank nötig.

---

### `eval_runner.py` - Evaluierungs-Skript

**Gedanke:** Automatische Evaluierung aller drei Pipelines.

**Was macht es?**
- Lädt `eval/dev.jsonl`
- Führt alle drei Pipelines aus
- Berechnet F1-Score für jede Pipeline
- Zeigt Vergleichstabelle

**Warum wichtig?** Objektiver Vergleich der Pipelines, nicht nur subjektive Beobachtung.

---

## 🎓 Workshop-Planung

### Überblick: 60-Minuten Workshop

**Ziel:** Teilnehmer lernen drei Frameworks durch praktische Experimente kennen.

**Struktur:**
1. **0-2 Min:** Setup (App öffnen)
2. **2-12 Min:** Einführung (Konzepte verstehen)
3. **12-24 Min:** LangChain (Sequenzielle Pipeline)
4. **24-39 Min:** LangGraph (Graph-Pipeline)
5. **39-54 Min:** DSPy (Deklarative Pipeline)
6. **54-60 Min:** Vergleich & Abschluss

---

### Teil 1: Setup (0-2 Minuten)

**Was passiert?**
- Teilnehmer öffnen App (Doppelklick auf `run.bat` / `run.sh`)
- App lädt automatisch (1-2 Minuten beim ersten Mal)
- Teilnehmer laden Test-PDF hoch

**Gedanke:** Minimale Hürden. Doppelklick = fertig. Keine komplexen Setup-Schritte.

**Checkliste:**
- [ ] Alle Teilnehmer haben App geöffnet
- [ ] Alle können PDF hochladen
- [ ] API-Key ist gesetzt (falls lokal)

---

### Teil 2: Einführung (2-12 Minuten)

**Was passiert?**
- Moderatoren erklären Multi-Agent Orchestration
- Live-Demo: Pipeline ausführen
- Framework-Überblick: LangChain vs. LangGraph vs. DSPy

**Gedanke:** Theorie vor Praxis, aber kurz. Teilnehmer sollen verstehen, warum man Multi-Agent nutzt.

**Lernziele:**
- Was ist Multi-Agent Orchestration?
- Warum drei Frameworks?
- Was ist der Unterschied?

---

### Teil 3: LangChain (12-24 Minuten)

**Was passiert?**
- Teilnehmer führen LangChain-Pipeline aus
- Code verstehen: `workflows/langchain_pipeline.py`
- **Experiment 1:** Prompt ändern (`agents/summarizer.py`)
- **Experiment 2:** Reihenfolge ändern (zeigt Abhängigkeiten)

**Gedanke:** Zeigt Einfachheit, aber auch Limitationen.

**Lernziele:**
- Wie funktioniert sequenzielle Ausführung?
- Wie ändert man Prompts?
- Was sind implizite Abhängigkeiten?

**Code-Experimente:**
1. **Prompt ändern:** "200-300 words" → "50-100 words"
   - **Was lernen Teilnehmer?** Prompts kontrollieren direkt das Verhalten
2. **Reihenfolge ändern:** Critic vor Summarizer
   - **Was lernen Teilnehmer?** Abhängigkeiten sind implizit, nicht explizit

---

### Teil 4: LangGraph (24-39 Minuten)

**Was passiert?**
- Teilnehmer führen LangGraph-Pipeline aus
- Graph-Visualisierung sehen
- Code verstehen: `workflows/langgraph_pipeline.py`
- **Experiment:** Neuen Node hinzufügen (z.B. Translator)

**Gedanke:** Zeigt Mächtigkeit von Graph-basierter Struktur.

**Lernziele:**
- Wie funktioniert Graph-basierte Orchestrierung?
- Wie fügt man neue Nodes hinzu?
- Was sind Conditional Edges?

**Code-Experimente:**
1. **Graph verstehen:** Nodes und Edges sehen
   - **Was lernen Teilnehmer?** Struktur ist explizit sichtbar
2. **Node hinzufügen:** Translator zwischen Summarizer und Critic
   - **Was lernen Teilnehmer?** Erweiterung ist einfach durch Graph-Struktur

---

### Teil 5: DSPy (39-54 Minuten)

**Was passiert?**
- Teilnehmer führen DSPy-Pipeline aus
- Code verstehen: Signatures statt Prompts
- **Experiment 1:** Signature ändern (zeigt deklaratives Paradigma)
- **Experiment 2:** Teleprompting aktivieren (zeigt Selbstoptimierung)

**Gedanke:** Zeigt deklaratives Paradigma und Selbstoptimierung.

**Lernziele:**
- Was ist deklarativ vs. prozedural?
- Wie funktioniert Teleprompting?
- Was sind Trade-offs?

**Code-Experimente:**
1. **Signature ändern:** "200-300 words" → "100-150 words"
   - **Was lernen Teilnehmer?** Beschreibung beeinflusst automatisch generierte Prompts
2. **Teleprompting:** Base vs. Optimized vergleichen
   - **Was lernen Teilnehmer?** Optimierung kostet Zeit, aber liefert bessere Ergebnisse

---

### Teil 6: Vergleich (54-60 Minuten)

**Was passiert?**
- Teilnehmer vergleichen alle drei Pipelines
- Entscheidungsmatrix ausfüllen
- Q&A

**Gedanke:** Zusammenfassung und Transfer.

**Lernziele:**
- Wann nutze ich welches Framework?
- Was sind die Trade-offs?

**Entscheidungsmatrix:**
| Kriterium | LangChain | LangGraph | DSPy |
|-----------|-----------|-----------|------|
| Einfachheit | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| Erweiterbarkeit | ⭐ | ⭐⭐⭐ | ⭐⭐ |
| Transparenz | ⭐⭐ | ⭐⭐⭐ | ⭐ |
| Selbstoptimierung | ❌ | ❌ | ✅ |

---

### Workshop-Materialien

**Für Teilnehmer:**
- `docs/teilnehmer/START_HIER.md`: Einstiegspunkt
- `docs/teilnehmer/TEILNEHMER_SKRIPT.md`: Hauptskript mit allen Aufgaben
- `docs/teilnehmer/CODE_EXPERIMENTE.md`: Code-Snippets zum Kopieren

**Für Moderatoren:**
- `docs/moderatoren/WORKSHOP_LEITFADEN.md`: Zeitplan & Ablauf
- `docs/moderatoren/WORKSHOP_CHECKLIST.md`: Vorbereitung
- `docs/moderatoren/WORKSHOP_CODE_BEREITSTELLUNG.md`: Code-Verteilung

**Gedanke:** Getrennte Dokumentation, damit jeder die richtigen Infos hat.

---

### Workshop-Vorbereitung (1 Woche vorher)

**Checkliste:**
- [ ] Code auf GitHub hochgeladen
- [ ] ZIP-Datei vorbereitet (Alternative)
- [ ] Online-App deployt (optional, aber empfohlen)
- [ ] Test-PDFs vorbereitet
- [ ] Dev-Set prüfen (`eval/dev.jsonl`)
- [ ] Präsentationsfolien erstellen

**Gedanke:** Vorbereitung ist wichtig. Technische Probleme während des Workshops sind frustrierend.

---

### Workshop-Tag (30 Min vorher)

**Checkliste:**
- [ ] Streamlit-App starten und testen
- [ ] API-Key funktioniert
- [ ] Beamer/Laptop-Verbindung prüfen
- [ ] Backup-Plan vorbereiten (Screenshots, vorgefertigte Ergebnisse)

**Gedanke:** Technische Probleme vorher beheben, nicht während des Workshops.

---

### Während des Workshops

**Kommunikation:**
- Klar und in angemessenem Tempo
- Regelmäßig Fragen: "Hat jemand Fragen?"
- Durch den Raum gehen und unterstützen

**Code-Experimente:**
- Teilnehmer ändern Code direkt
- Syntax-Fehler sind häufig - schnell helfen
- Code-Änderungen zeigen Unterschiede besser als Theorie

**Timing:**
- Zu schnell? Vertiefte Diskussionen, Bonus-Aufgaben
- Zu langsam? Kürzen, Fokus auf Kernpunkte

**Gedanke:** Flexibilität ist wichtig. Nicht starr am Zeitplan festhalten, sondern auf Teilnehmer reagieren.

---

### Nach dem Workshop

**Feedback sammeln:**
- Was hat gut funktioniert?
- Was war zu schwierig/einfach?
- Technische Probleme dokumentieren

**Dokumentation aktualisieren:**
- README verbessern (basierend auf Fragen)
- Code-Kommentare erweitern
- Known Issues dokumentieren

**Gedanke:** Kontinuierliche Verbesserung. Jeder Workshop ist eine Lerngelegenheit.

---

## 🎯 Zusammenfassung: Was haben wir uns dabei gedacht?

### Kern-Design-Prinzipien

1. **Einfachheit für Teilnehmer:** Doppelklick-Start, klare Dokumentation, sofort loslegen können
2. **Vergleichbarkeit:** Gleicher Workflow, drei Frameworks → Unterschiede werden klar
3. **Praktische Experimente:** Code ändern, Auswirkungen sehen → besseres Verständnis als Theorie
4. **Transparenz:** Graph-Visualisierung, Telemetrie, klare Struktur → Teilnehmer verstehen, was passiert
5. **Erweiterbarkeit:** Neue Nodes hinzufügen, Prompts ändern, Signatures anpassen → Teilnehmer können experimentieren

### Warum diese Struktur?

**Ordnerstruktur:**
- **`agents/`**: Getrennte Dateien → einzeln anpassbar
- **`workflows/`**: Drei Implementierungen → Vergleich möglich
- **`docs/`**: Getrennt für Teilnehmer/Moderatoren → richtige Infos für jeden
- **`eval/`**: Evaluierungsdaten → objektiver Vergleich

**Code-Struktur:**
- **Zentrale Konfiguration** (`llm.py`) → einmal ändern, überall wirksam
- **Wiederverwendbare Agenten** → alle Frameworks nutzen gleiche Agenten
- **Klare Trennung** → Agenten vs. Orchestrierung

**Workshop-Struktur:**
- **60 Minuten** → kompakt, aber vollständig
- **Praktische Experimente** → Code ändern, nicht nur zuschauen
- **Vergleich** → Unterschiede werden klar durch Experimente

---

## 🚀 Was können Teilnehmer nach dem Workshop?

- **Verstehen**, was Multi-Agent Orchestration ist
- **Erklären**, wie LangChain, LangGraph und DSPy sich unterscheiden
- **Code anpassen** in allen drei Frameworks
- **Entscheiden**, welches Framework für welchen Use Case passt
- **Einen neuen Node** zu LangGraph hinzufügen
- **Signatures** in DSPy anpassen
- **Prompts** in LangChain/LangGraph ändern

**Das ist das Ziel:** Nicht nur Theorie, sondern praktische Fähigkeiten, die man direkt anwenden kann.

---

*Viel Erfolg beim Workshop! 🎓*

