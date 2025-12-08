# app.py  — upload-only, section-aware context for LC/LG/DSPy
import os, io, json
import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader

from workflows.langchain_pipeline import run_pipeline as run_lc
from workflows.langgraph_pipeline import run_pipeline as run_lg
from workflows.dspy_pipeline import run_pipeline as run_dspy
from utils import build_analysis_context, preview_sections

load_dotenv()
st.set_page_config(page_title="Multi-Agent Paper Analyzer", page_icon="🧠", layout="wide")
st.title("🧠 Multi-Agent Paper Analyzer")

# ---------- Hilfe / Überblick ----------
with st.expander("ℹ️ Hilfe / Überblick"):
    st.markdown(
        """
**Was macht diese App?**  
Lädt Paper (PDF/TXT), erstellt einen abschnittsbasierten Analyse-Kontext und führt drei Orchestrierungs-Varianten aus:

- **LangChain (sequenziell):** Lineare Pipeline (Reader → Summarizer → Critic → Integrator). Einfach & schnell, wenig Boilerplate.
- **LangGraph (Graph):** Expliziter Graph mit Knoten/Kanten, deterministischer Kontrollfluss, sehr transparent (Graph-Ansicht).
- **DSPy (deklarativ):** Pipelines per „Signatures/Modules“ definieren; optionales *Teleprompting* optimiert Prompts mit kleinem Dev-Set.

**Abschnittsauswahl:**  
Wenn aktiviert, werden typische Paper-Abschnitte (Abstract, Introduction, …) erkannt und priorisiert in ein **Analyse-Budget** (Zeichen) gefüllt.  
Ist der Auszug zu kurz, kann automatisch erweitert werden.

**Kontextfenster (LLM):**  
Große Dokumente passen evtl. nicht vollständig in das Modell-Kontextfenster. Das **Analyse-Budget** begrenzt deshalb den Input.  
Tipp: Um Trunkierung zu vermeiden, in der Umgebung `OLLAMA_NUM_CTX` auf z. B. 4096 setzen.

**Telemetry (CSV):**  
Schreibt u. a. `engine`, `input_chars`, `summary_len`, `meta_len`, `latency_s` sowie Schrittzeiten (`reader_s`, …) in `telemetry.csv`.

**DSPy-Teleprompting:**  
Mit Dev-Set (JSONL) kann die Summarizer-Stage leichtgewichtig optimiert werden (Few-Shot-Bootstrapping). Erst Dev-Set wählen, dann Häkchen setzen.
        """
    )

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    preset = st.segmented_control(
        "Preset", 
        ["Speed", "Balanced", "Detail"], 
        default="Balanced",
        help=(
            "Wählt ein Profil für Geschwindigkeit vs. Detailtiefe:\n"
            "• Speed: schnellere Laufzeit, weniger Kontext\n"
            "• Balanced: ausgewogener Standard\n"
            "• Detail: mehr Kontext, längere Antworten"
        )
    )

    if preset == "Speed":
        _def_max_tokens = 160; _def_temp = 0.0;  _def_trunc = 8000;  def_section_budget = 6000
    elif preset == "Balanced":
        _def_max_tokens = 256; _def_temp = 0.1;  _def_trunc = 12000; def_section_budget = 10000
    else:
        _def_max_tokens = 384; _def_temp = 0.15; _def_trunc = 16000; def_section_budget = 12000

    model = st.selectbox(
        "Model",
        ["llama3.2:1b", "qwen2.5:1.5b", "phi3:3.8b-mini", "qwen3:4b"],
        index=0,
        help=(
            "Wählt das Ollama-Modell für alle Schritte (Reader, Summarizer, Critic, Integrator). "
            "Kleinere Modelle sind schneller, größere oft präziser."
        ),
    )


    max_tokens = st.slider(
        "Max tokens per step",
        64, 1024, _def_max_tokens, 32,
        help=(
            "Begrenzt die Länge der **Antwort** je Agent-Schritt. "
            "Höhere Werte erlauben ausführlichere Ausgaben, kosten aber Zeit."
        ),
    )
    temperature = st.slider(
        "Temperature",
        0.0, 1.0, _def_temp, 0.05,
        help=(
            "Steuert Kreativität/Varianz des Modells. "
            "0.0 = deterministischer, 1.0 = kreativer (u. U. weniger stabil)."
        ),
    )

    timeout_s = st.slider(
        "Timeout per step (sec)",
        10, 300, 60, 5,
        help=(
            "Maximale Rechenzeit pro Agent-Schritt. "
            "Schützt gegen Hänger; zu knapp kann Abbrüche verursachen."
        ),
    )

    truncate_chars = st.slider(
        "Input truncation (chars)",
        500, 16000, _def_trunc, 250,
        help=(
            "Schneidet den **Rohtext** auf diese Länge, bevor Abschnitte ermittelt werden. "
            "Höher = mehr Kontext, aber eventuell langsamer."
        ),
    )

    st.markdown("---")
    st.markdown("#### Section selection")

    sections_enabled = st.checkbox(
        "Enable section-aware input",
        value=True,
        help=(
            "Wenn aktiv: Es werden typische Paper-Abschnitte (Abstract, Introduction, …) "
            "erkannt und priorisiert, statt reinen Volltext zu nutzen."
        ),
    )
    section_budget_chars = st.slider(
        "Analysis budget (chars)",
        1000, 15000, def_section_budget, 500,
        help=(
            "Maximale Zeichenanzahl, die nach Abschnitts-Selektion an die Pipelines übergeben wird. "
            "Begrenzt den **effektiven** Kontext."
        ),
    )
    sections_pref = st.multiselect(
        "Preferred sections (priority order)",
        ["abstract", "introduction", "methods", "results", "discussion", "conclusion", "related", "limitations"],
        default=["abstract", "introduction", "methods", "results", "discussion", "conclusion"],
        help=(
            "Diese Abschnitte werden zuerst in das Analyse-Budget aufgenommen. "
            "Übrige Abschnitte folgen, sofern noch Budget frei ist."
        ),
    )
    auto_expand = st.checkbox(
        "Auto-expand beyond short abstracts",
        value=True,
        help=(
            "Falls der gewählte Abschnitts-Auszug zu kurz ist, werden zusätzliche Abschnitte/Absätze ergänzt, "
            "bis das Budget ausgeschöpft ist."
        ),
    )
    min_analysis_chars = st.slider(
        "Minimum analysis length (chars)",
        200, 6000, 1000, 100,
        help=(
            "Untergrenze für die Kontextlänge nach Selektion. "
            "Bei zu wenig Inhalt wird automatisch mehr Text einbezogen."
        ),
    )

    st.sidebar.markdown("### DSPy")

    use_dspy_opt = st.checkbox(
        "DSPy Teleprompting (optimize)",
        value=False,
        help=(
            "Aktiviert ein kleines, datengetriebenes Prompt-Tuning (Few-Shot-Bootstrapping) für die DSPy-Pipeline. "
            "Benötigt ein Dev-Set (JSONL)."
        ),
    )
    dspy_dev_path = st.text_input(
        "Path to Dev-Set",
        value="eval/dev.jsonl",
        help=(
            "JSONL-Datei mit Zeilen im Format: "
            "{\"text\": \"<Eingabedokument>\", \"target_summary\": \"<Gold-Zusammenfassung>\"}."
        ),
    )
     
    st.markdown("---")
    show_debug = st.toggle("Show debug output", value=False)

cfg = {
    "model": model,
    "max_tokens": int(max_tokens),
    "temperature": float(temperature),
    "timeout": int(timeout_s),
    "truncate_chars": int(truncate_chars),
    "sections_enabled": bool(sections_enabled),
    "section_budget_chars": int(section_budget_chars),
    "sections_preferred": sections_pref,
    "api_base": os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
    "debug": bool(show_debug),
    "auto_expand_if_short": bool(auto_expand),
    "min_analysis_chars": int(min_analysis_chars),
    
    "dspy_teleprompt": use_dspy_opt,
    "dspy_dev_path": dspy_dev_path,
}

# ---------- Pipeline choice ----------
mode = st.radio(
    "Choose pipeline:",
    ["LangChain (sequential)", "LangGraph (graph)", "DSPy (self-improving)"],
    horizontal=True,
    help=(
        "• LangChain: lineare Abfolge (einfach, schnell)\n"
        "• LangGraph: expliziter Graph mit Knoten (deterministisch, sehr transparent)\n"
        "• DSPy: deklarativ mit optionalem Prompt-Tuning (Teleprompting)"
    ),
)


# ---------- Upload-only input ----------
uploaded_files = st.file_uploader(
    "Upload PDF/TXT file(s)",
    type=["pdf", "txt"],
    accept_multiple_files=True,
    help=(
        "Lade ein oder mehrere Paper (PDF oder TXT) hoch. "
        "Der Text wird extrahiert, bereinigt und für die Abschnitts-Auswahl genutzt."
    ),
)

def _extract_pdf_text(file_like) -> str:
    try:
        reader = PdfReader(file_like)
        return "\n\n".join((p.extract_text() or "") for p in reader.pages).strip()
    except Exception as e:
        return f"[PDF error] {e}"

def _read_uploads(files) -> str:
    if not files:
        return ""
    chunks = []
    for f in files:
        try:
            data = f.read()
            if f.type == "application/pdf" or f.name.lower().endswith(".pdf"):
                chunks.append(_extract_pdf_text(io.BytesIO(data)))
            else:
                chunks.append(data.decode("utf-8", errors="ignore"))
        except Exception as e:
            chunks.append(f"[Error reading {f.name}: {e}]")
    return "\n\n".join(x for x in chunks if x).strip()

raw_text = _read_uploads(uploaded_files)

if uploaded_files:
    st.caption("Uploads:")
    for f in uploaded_files:
        st.write("•", f.name)

# ---------- Build section-aware analysis context ----------
analysis_context = ""
usage_map = {}
if raw_text:
    truncated = raw_text[: cfg["truncate_chars"]] if len(raw_text) > cfg["truncate_chars"] else raw_text
    analysis_context = build_analysis_context(truncated, cfg)
    usage_map = preview_sections(truncated, cfg)

# ---------- Preview ----------
show_preview = st.checkbox(
    "Show input preview / section mapping",
    value=True,
    help=(
        "Zeigt an, welcher Text effektiv in die Analyse einfließt "
        "und wie viele Zeichen pro Abschnitt genutzt wurden."
    ),
)

if show_preview:
    st.markdown("#### Preview")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.caption(f"Characters in analysis context: {len(analysis_context)}")
        st.text(analysis_context[:1200] + ("..." if len(analysis_context) > 1200 else ""))
    with c2:
        st.caption("Section mapping (chars used)")
        if usage_map:
            for name in usage_map:
                st.write(f"- **{name}**: {usage_map[name]}")
        else:
            st.write("No sections detected – fallback to longest paragraphs.")

# ---------- Run ----------
col_run, col_clear, _ = st.columns([1, 1, 6])
run_btn = col_run.button(
    "🚀 Run",
    type="primary",
    help="Startet die gewählte Pipeline auf Basis des vorbereiteten Analyse-Kontexts.",
)

if col_clear.button("🧹 Clear"):
    st.session_state.clear()

if run_btn:
    if not analysis_context.strip():
        st.warning("Please upload at least one PDF/TXT so we can build the analysis context.")
    else:
        with st.status("Analyzing document ... please wait ⏳", expanded=False) as status:
            try:
                # Feed *the same* section-aware context to all pipelines
                if mode.startswith("LangChain"):
                    result = run_lc(analysis_context, cfg)   # notes→summary→critic→meta (LC).  See LC runner.
                elif mode.startswith("LangGraph"):
                    result = run_lg(analysis_context, cfg)   # LG receives identical context and returns DOT.
                else:
                    result = run_dspy(analysis_context, cfg) # DSPy module pipeline.

                status.update(label="Done.", state="complete")

                st.markdown("### Results")
                st.markdown("**Meta Summary**")
                st.write(result.get("meta", ""))

                st.markdown("**Summary**")
                st.code(result.get("summary", ""), language="")

                st.markdown("**Structured Notes**")
                st.code(result.get("structured", ""), language="")

                st.markdown("**Critic Evaluation**")
                st.code(result.get("critic", ""), language="")

                st.markdown("**Timing (seconds)**")
                st.write({
                    "reader_s": result.get("reader_s", 0),
                    "summarizer_s": result.get("summarizer_s", 0),
                    "critic_s": result.get("critic_s", 0),
                    "integrator_s": result.get("integrator_s", 0),
                })

                # LangGraph: show DOT if provided
                dot = result.get("graph_dot")
                if dot and mode.startswith("LangGraph"):
                    st.markdown("### Graph (LangGraph)")
                    st.graphviz_chart(dot, use_container_width=True)

                st.download_button(
                    "⬇️ Download results as JSON",
                    data=json.dumps(result, ensure_ascii=False, indent=2),
                    file_name="paper_analysis.json",
                    mime="application/json",
                )
            except Exception as e:
                status.update(label=f"Error: {e}", state="error")
                st.error(str(e))
