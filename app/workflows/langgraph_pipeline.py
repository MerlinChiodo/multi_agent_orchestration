"""
LangGraph Pipeline: Graph-basierte Ausführung mit expliziter Graph-Struktur.
"""

from __future__ import annotations

from typing import TypedDict, Dict, Any, Optional, Callable
from time import perf_counter
import concurrent.futures as cf
import re
from collections import Counter

from langgraph.graph import StateGraph, END

from agents.reader import run as run_reader
from agents.summarizer import run as run_summarizer
from agents.critic import run as run_critic
from agents.integrator import run as run_integrator
from llm import configure, llm
from telemetry import log_row
from utils import build_analysis_context, truncate_text
from langchain_core.prompts import ChatPromptTemplate


class PipelineState(TypedDict):
    """State des LangGraph-Workflows."""
    input_text: str
    analysis_context: str
    notes: str
    summary: str
    critic: str
    meta: str
    reader_s: float
    summarizer_s: float
    critic_s: float
    integrator_s: float
    translator_s: float
    keyword_s: float
    summary_translated: str
    keywords: str
    judge_aggregate: float
    critic_score: float
    critic_loops: int
    quality_f1: float
    judge_score: float
    _timeout: int
    _config: Dict[str, Any]


def _execute_with_timeout(
    function: Callable,
    timeout_seconds: int,
    timeout_default_value: str = "__TIMEOUT__"
) -> Any:
    """Führt Funktion mit Timeout aus, schützt gegen hängende LLM-Requests."""
    with cf.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(function)
        try:
            return future.result(timeout=max(1, int(timeout_seconds)))
        except cf.TimeoutError:
            return timeout_default_value


def _execute_retriever_node(state: PipelineState) -> PipelineState:
    """Graph-Knoten: Preprocessing/Abschnittsauswahl (Retrieval/Guard)."""
    config = state.get("_config", {}) or {}
    raw_input = state.get("input_text", "") or ""
    truncate_chars_limit = config.get("truncate_chars")
    preprocessed_text = truncate_text(raw_input, truncate_chars_limit) if truncate_chars_limit else raw_input
    analysis_context = build_analysis_context(preprocessed_text, config)
    state["analysis_context"] = analysis_context
    return state


def _execute_reader_node(state: PipelineState) -> PipelineState:
    """Graph-Knoten: Reader-Agent ausführen."""
    start_time = perf_counter()
    timeout_seconds = state.get("_timeout", 45)
    input_for_reader = state.get("analysis_context") or state.get("input_text") or ""
    notes_output = _execute_with_timeout(lambda: run_reader(input_for_reader), timeout_seconds)
    state["notes"] = notes_output
    state["reader_s"] = round(perf_counter() - start_time, 2)
    return state


def _execute_summarizer_node(state: PipelineState) -> PipelineState:
    """Graph-Knoten: Summarizer-Agent ausführen."""
    start_time = perf_counter()
    timeout_seconds = state.get("_timeout", 45)
    summary_output = _execute_with_timeout(lambda: run_summarizer(state["notes"]), timeout_seconds)
    state["summary"] = summary_output
    state["summarizer_s"] = round(perf_counter() - start_time, 2)
    return state


def _execute_critic_node(state: PipelineState) -> PipelineState:
    """Graph-Knoten: Critic-Agent ausführen."""
    start_time = perf_counter()
    timeout_seconds = state.get("_timeout", 45)
    critic_result = _execute_with_timeout(
        lambda: run_critic(notes=state["notes"], summary=state["summary"]),
        timeout_seconds
    )
    
    if isinstance(critic_result, dict):
        critic_text = critic_result.get("critic") or critic_result.get("critique") or ""
    else:
        critic_text = str(critic_result)
    
    state["critic"] = critic_text
    state["critic_s"] = round(perf_counter() - start_time, 2)
    return state


def _extract_critic_score(state: PipelineState) -> float:
    """Schätzung eines numerischen Kritiker-Scores aus dem Critic-Text."""
    text = state.get("critic", "") or ""
    match = re.search(r"([0-9]+(?:\\.[0-9]+)?)", text)
    if match:
        score = float(match.group(1))
    else:
        score = state.get("quality_f1", 0.0)
    if score > 1.0:
        score = min(score / 5.0, 1.0)
    score = max(0.0, min(score, 1.0))
    state["critic_score"] = round(score, 3)
    return state["critic_score"]


def _execute_translator_node(state: PipelineState) -> PipelineState:
    """Graph-Knoten: Dummy-Übersetzer (Deutsch/Englisch) plus Kürzung."""
    start_time = perf_counter()
    summary = state.get("summary", "") or ""
    cfg = state.get("_config", {}) or {}
    language = cfg.get("translator_language", "DE").upper()
    style = cfg.get("translator_style", "short")
    max_chars = len(summary)
    if style == "short":
        max_chars = min(120, len(summary))
    elif style == "ultra_short":
        max_chars = min(80, len(summary))
    truncated = summary if not max_chars else summary[:max_chars]
    truncated = truncated.strip()
    translation = f"[{language}] {truncated}"
    if len(truncated) < len(summary):
        translation = f"{translation}…"
    state["summary_translated"] = translation
    state["translator_s"] = round(perf_counter() - start_time, 2)
    return state


def _execute_keyword_node(state: PipelineState) -> PipelineState:
    """Graph-Knoten: Extrahiert Keywords aus der Summary."""
    start_time = perf_counter()
    summary = state.get("summary", "") or ""
    tokens = [token.lower() for token in re.findall(r"\\w+", summary) if len(token) > 3]
    freq = Counter(tokens)
    most_common = [token for token, _ in freq.most_common(6)]
    state["keywords"] = ", ".join(most_common)
    state["keyword_s"] = round(perf_counter() - start_time, 2)
    return state


def _critic_post_path(state: PipelineState) -> str:
    """Entscheidet nach dem Critic-Node über den nächsten Schritt."""
    _extract_critic_score(state)
    summary = state.get("summary", "") or ""
    loops = state.get("critic_loops", 0)
    cfg = state.get("_config", {}) or {}
    max_loops = max(0, int(cfg.get("max_critic_loops", 1)))
    if state["critic_score"] < 0.5 and loops < max_loops:
        state["critic_loops"] = loops + 1
        return "summarizer"
    if len(summary) < 100:
        return "judge"
    return "quality"


def _tokens(s: str) -> set[str]:
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return {t for t in s.split() if len(t) > 2}


def _execute_quality_node(state: PipelineState) -> PipelineState:
    """Graph-Knoten: Einfaches Qualitäts-Maß (Unigram-F1) zwischen NOTES und SUMMARY."""
    gold = _tokens(state.get("notes", "") or "")
    pred = _tokens(state.get("summary", "") or "")
    if not gold or not pred:
        state["quality_f1"] = 0.0
        return state
    inter = len(gold & pred)
    prec = inter / len(pred)
    rec = inter / len(gold)
    f1 = 0.0 if (prec + rec) == 0 else (2 * prec * rec) / (prec + rec)
    state["quality_f1"] = round(f1, 3)
    return state


def _execute_judge_node(state: PipelineState) -> PipelineState:
    """Graph-Knoten: LLM-as-a-judge (ein Gesamt-Score 0-5, nur Zahl)."""
    prompt = ChatPromptTemplate.from_template(
        "Score the SUMMARY against NOTES for coherence, groundedness, and coverage. "
        "Return a single integer 0-5 (0=worst, 5=best). No extra text.\n\n"
        "NOTES:\n{notes}\n\nSUMMARY:\n{summary}"
    )
    chain = prompt | llm
    try:
        llm_resp = chain.invoke({
            "notes": state.get("notes", "") or "",
            "summary": state.get("summary", "") or ""
        })
        raw = getattr(llm_resp, "content", llm_resp) or ""
        m = re.search(r"(-?\d+)", str(raw))
        score = float(m.group(1)) if m else 0.0
    except Exception:
        score = 0.0
    score = max(0.0, min(5.0, score))
    state["judge_score"] = round(score, 2)
    return state


def _execute_aggregator_node(state: PipelineState) -> PipelineState:
    """Graph-Knoten: Aggregiert Judge-, Quality- und Critic Scores."""
    quality = state.get("quality_f1", 0.0)
    judge_norm = state.get("judge_score", 0.0) / 5.0
    critic = state.get("critic_score", 0.0)
    candidates = [value for value in (quality, judge_norm, critic) if value is not None and value > 0]
    aggregate = round(sum(candidates) / len(candidates), 3) if candidates else 0.0
    state["judge_aggregate"] = aggregate
    return state


def _execute_integrator_node(state: PipelineState) -> PipelineState:
    """Graph-Knoten: Integrator-Agent ausführen."""
    start_time = perf_counter()
    timeout_seconds = state.get("_timeout", 45)
    meta_output = _execute_with_timeout(
        lambda: run_integrator(notes=state["notes"], summary=state["summary"], critic=state["critic"]),
        timeout_seconds
    )
    state["meta"] = meta_output
    state["integrator_s"] = round(perf_counter() - start_time, 2)
    return state


def _generate_graph_visualization_dot(state: Optional[PipelineState] = None) -> str:
    """Generiert Graphviz DOT-Darstellung des Workflows mit optionalen dynamischen Werten."""
    if state is None:
        return r"""
digraph G {
  rankdir=LR;
  node [shape=box, style="rounded,filled", color="#9ca3af", fillcolor="#f9fafb", fontname="Inter"];

  input      [label="Input (raw text/PDF extract)"];
  retriever  [label="Retriever/Preprocess"];
  reader     [label="Reader - Notes"];
  summarizer [label="Summarizer"];
  translator [label="Translator (DE/EN)"];
  keyword    [label="Keyword Extraction"];
  critic_node [label="Critic - Review"];
  quality    [label="Quality (F1)"];
  judge      [label="LLM Judge"];
  aggregator [label="Judge Aggregator"];
  integrator [label="Integrator - Meta Summary"];
  output     [label="Output (notes, summary, critic, meta, f1, judge)"];

  input -> retriever -> reader -> summarizer -> translator -> keyword -> critic_node;
  critic_node -> quality [label="long summary"];
  critic_node -> judge [label="short summary", style="dashed"];
  critic_node -> summarizer [label="rework (low critic)", style="dotted"];
  quality -> judge -> aggregator -> integrator -> output;
  judge -> aggregator;
}
""".strip()

    reader_time = state.get("reader_s", 0.0)
    summarizer_time = state.get("summarizer_s", 0.0)
    critic_time = state.get("critic_s", 0.0)
    integrator_time = state.get("integrator_s", 0.0)
    translator_time = state.get("translator_s", 0.0)
    keyword_time = state.get("keyword_s", 0.0)
    f1_score = state.get("quality_f1", 0.0)
    judge_score = state.get("judge_score", 0.0)
    judge_aggregate = state.get("judge_aggregate", 0.0)
    translation_preview = (state.get("summary_translated", "") or "").replace('"', "'")
    translation_preview = translation_preview[:40] + ("…" if len(translation_preview) > 40 else "")
    keywords_label = state.get("keywords", "") or "no keywords"
    critic_label = f"Critic - Review\\n{critic_time:.2f}s"

    reader_label = f"Reader - Notes\\n{reader_time:.2f}s"
    summarizer_label = f"Summarizer - Summary\\n{summarizer_time:.2f}s"
    translator_label = f"Translator\\n{translation_preview}\\n{translator_time:.2f}s"
    keyword_label = f"Keywords\\n{keywords_label}\\n{keyword_time:.2f}s"
    quality_label = f"Quality (F1)\\n{f1_score:.3f}"
    judge_label = f"LLM Judge\\n{judge_score:.1f}/5"
    aggregator_label = f"Judge Aggregate\\n{judge_aggregate:.3f}"
    integrator_label = f"Integrator - Meta Summary\\n{integrator_time:.2f}s"

    return f"""
digraph G {{
  rankdir=LR;
  node [shape=box, style="rounded,filled", color="#667eea", fillcolor="#f0f4ff", fontname="Inter"];
  edge [color="#9ca3af"];

  input      [label="Input\\n(raw text/PDF)", fillcolor="#e0e7ff", color="#667eea"];
  retriever  [label="Retriever/Preprocess\\nAnalysis Context", fillcolor="#f0f4ff"];
  reader     [label="{reader_label}", fillcolor="#dbeafe"];
  summarizer [label="{summarizer_label}", fillcolor="#dbeafe"];
  translator [label="{translator_label}", fillcolor="#fde68a"];
  keyword    [label="{keyword_label}", fillcolor="#fef3c7"];
  critic_node [label="{critic_label}", fillcolor="#dbeafe"];
  quality    [label="{quality_label}", fillcolor="#d1fae5"];
  judge      [label="{judge_label}", fillcolor="#c7d2fe"];
  aggregator [label="{aggregator_label}", fillcolor="#c5fde2"];
  integrator [label="{integrator_label}", fillcolor="#dbeafe"];
  output     [label="Output\\n(all results)", fillcolor="#e0e7ff", color="#667eea"];

  input -> retriever -> reader -> summarizer -> translator -> keyword -> critic_node;
  critic_node -> quality [label="long summary", style="solid"];
  critic_node -> judge [label="short summary", style="dashed"];
  critic_node -> summarizer [label="rework (low critic)", style="dotted"];
  quality -> judge -> aggregator -> integrator -> output;
  judge -> aggregator;
}}
""".strip()


def _build_langgraph_workflow() -> Any:
    """Baut LangGraph-Workflow mit Retrieval/Preprocessing, vier Agenten und Qualitäts-Metrik."""
    graph = StateGraph(PipelineState)
    graph.add_node("retriever", _execute_retriever_node)
    graph.add_node("reader", _execute_reader_node)
    graph.add_node("summarizer", _execute_summarizer_node)
    graph.add_node("translator", _execute_translator_node)
    graph.add_node("keyword", _execute_keyword_node)
    graph.add_node("critic_node", _execute_critic_node)  # Umbenannt: Node-Name != State-Key
    graph.add_node("quality", _execute_quality_node)
    graph.add_node("judge", _execute_judge_node)
    graph.add_node("aggregator", _execute_aggregator_node)
    graph.add_node("integrator", _execute_integrator_node)
    graph.set_entry_point("retriever")
    graph.add_edge("retriever", "reader")
    graph.add_edge("reader", "summarizer")
    graph.add_edge("summarizer", "translator")
    graph.add_edge("translator", "keyword")
    graph.add_edge("keyword", "critic_node")
    graph.add_conditional_edges("critic_node", _critic_post_path)
    graph.add_edge("quality", "judge")
    graph.add_edge("judge", "aggregator")
    graph.add_edge("aggregator", "integrator")
    graph.add_edge("integrator", END)
    return graph.compile()


def run_pipeline(input_text: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Führt LangGraph-Pipeline aus. Gibt Dictionary mit structured, summary, critic, meta, Timings und graph_dot zurück."""
    config_dict = config or {}
    configure(config_dict)
    timeout_seconds = int(config_dict.get("timeout", 45))
    start_total = perf_counter()
    
    workflow = _build_langgraph_workflow()
    initial_state = {
        "input_text": input_text or "",
        "analysis_context": "",
        "notes": "",
        "summary": "",
        "critic": "",
        "meta": "",
        "reader_s": 0.0,
        "summarizer_s": 0.0,
        "critic_s": 0.0,
        "translator_s": 0.0,
        "keyword_s": 0.0,
        "summary_translated": "",
        "keywords": "",
        "judge_aggregate": 0.0,
        "critic_score": 0.0,
        "critic_loops": 0,
        "integrator_s": 0.0,
        "quality_f1": 0.0,
        "judge_score": 0.0,
        "_timeout": timeout_seconds,
        "_config": config_dict,
    }
    
    final_state = workflow.invoke(initial_state)
    total_duration = round(perf_counter() - start_total, 2)
    input_chars = len(final_state.get("analysis_context") or input_text or "")
    
    log_row({
        "engine": "langgraph",
        "input_chars": input_chars,
        "summary_len": len(str(final_state.get("summary", ""))),
        "meta_len": len(str(final_state.get("meta", ""))),
        "latency_s": total_duration,
        "reader_s": final_state.get("reader_s", 0.0),
        "summarizer_s": final_state.get("summarizer_s", 0.0),
        "critic_s": final_state.get("critic_s", 0.0),
        "translator_s": final_state.get("translator_s", 0.0),
        "keyword_s": final_state.get("keyword_s", 0.0),
        "integrator_s": final_state.get("integrator_s", 0.0),
        "quality_f1": final_state.get("quality_f1", 0.0),
        "judge_score": final_state.get("judge_score", 0.0),
        "judge_aggregate": final_state.get("judge_aggregate", 0.0),
        "critic_score": final_state.get("critic_score", 0.0),
        "critic_loops": final_state.get("critic_loops", 0),
    })
    
    return {
        "structured": final_state.get("notes", ""),
        "summary": final_state.get("summary", ""),
        "summary_translated": final_state.get("summary_translated", ""),
        "keywords": final_state.get("keywords", ""),
        "critic": final_state.get("critic", ""),
        "meta": final_state.get("meta", ""),
        "reader_s": final_state.get("reader_s", 0.0),
        "summarizer_s": final_state.get("summarizer_s", 0.0),
        "critic_s": final_state.get("critic_s", 0.0),
        "translator_s": final_state.get("translator_s", 0.0),
        "keyword_s": final_state.get("keyword_s", 0.0),
        "integrator_s": final_state.get("integrator_s", 0.0),
        "quality_f1": final_state.get("quality_f1", 0.0),
        "judge_score": final_state.get("judge_score", 0.0),
        "judge_aggregate": final_state.get("judge_aggregate", 0.0),
        "critic_score": final_state.get("critic_score", 0.0),
        "critic_loops": final_state.get("critic_loops", 0),
        "latency_s": total_duration,
        "input_chars": input_chars,
        "graph_dot": _generate_graph_visualization_dot(final_state),  # Dynamisch mit Werten
    }
