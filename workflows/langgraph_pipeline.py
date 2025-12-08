# workflows/langgraph_pipeline.py
from __future__ import annotations

from typing import TypedDict, Dict, Any
from time import perf_counter
import concurrent.futures as cf

from langgraph.graph import StateGraph, END

from agents.reader import run as run_reader
from agents.summarizer import run as run_summarizer
from agents.critic import run as run_critic
from agents.integrator import run as run_integrator
from llm import configure

# ----- Graph State -----
class PipelineState(TypedDict):
    input_text: str
    notes: str
    summary: str
    critic: str
    meta: str
    reader_s: float
    summarizer_s: float
    critic_s: float
    integrator_s: float
    _timeout: int

# ----- Helpers -----
def _with_timeout(fn, timeout_seconds: int, default="__TIMEOUT__"):
    with cf.ThreadPoolExecutor(max_workers=1) as executor:
        fut = executor.submit(fn)
        try:
            return fut.result(timeout=max(1, int(timeout_seconds)))
        except cf.TimeoutError:
            return default

# ----- Node functions -----
def _reader(state: PipelineState) -> PipelineState:
    t0 = perf_counter()
    to = state.get("_timeout", 45)
    state["notes"] = _with_timeout(lambda: run_reader(state["input_text"]), to)
    state["reader_s"] = round(perf_counter() - t0, 2)
    return state

def _summarizer(state: PipelineState) -> PipelineState:
    t0 = perf_counter()
    to = state.get("_timeout", 45)
    state["summary"] = _with_timeout(lambda: run_summarizer(state["notes"]), to)
    state["summarizer_s"] = round(perf_counter() - t0, 2)
    return state

def _critic(state: PipelineState) -> PipelineState:
    t0 = perf_counter()
    to = state.get("_timeout", 45)
    res = _with_timeout(lambda: run_critic(notes=state["notes"], summary=state["summary"]), to)
    # critic agent returns {'critic': ..., 'critique': ...}
    if isinstance(res, dict):
        state["critic"] = res.get("critic") or res.get("critique") or ""
    else:
        state["critic"] = str(res)
    state["critic_s"] = round(perf_counter() - t0, 2)
    return state

def _integrator(state: PipelineState) -> PipelineState:
    t0 = perf_counter()
    to = state.get("_timeout", 45)
    state["meta"] = _with_timeout(
        lambda: run_integrator(notes=state["notes"], summary=state["summary"], critic=state["critic"]), to
    )
    state["integrator_s"] = round(perf_counter() - t0, 2)
    return state

def _graph_dot_static() -> str:
    # a readable, minimal DOT that mirrors the actual graph edges
    return r"""
digraph G {
  rankdir=LR;
  node [shape=box, style="rounded,filled", color="#9ca3af", fillcolor="#f9fafb", fontname="Inter"];

  input      [label="Input (text/PDF extract)"];
  reader     [label="Reader → Notes"];
  summarizer [label="Summarizer → Summary"];
  critic     [label="Critic → Review"];
  integrator [label="Integrator → Meta Summary"];
  output     [label="Output (notes, summary, critic, meta)"];

  input -> reader -> summarizer -> critic -> integrator -> output;
}
""".strip()

# ----- Build & Run -----
def _build_graph():
    g = StateGraph(PipelineState)
    g.add_node("reader", _reader)
    g.add_node("summarizer", _summarizer)
    g.add_node("critic", _critic)
    g.add_node("integrator", _integrator)
    g.set_entry_point("reader")
    g.add_edge("reader", "summarizer")
    g.add_edge("summarizer", "critic")
    g.add_edge("critic", "integrator")
    g.add_edge("integrator", END)
    return g.compile()

def run_pipeline(input_text: str, cfg: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Executes the LangGraph workflow and returns:
    {
      'structured': notes, 'summary': summary, 'critic': critic, 'meta': meta,
      'reader_s': float, 'summarizer_s': float, 'critic_s': float, 'integrator_s': float,
      'graph_dot': DOT string
    }
    """
    cfg = cfg or {}
    configure(cfg)  # uses llm.py; same as your LangChain pipeline

    timeout_s = int(cfg.get("timeout", 45))
    # We pass the *full* text here; your app already built a section-aware context for LC runs.
    # If you also want to feed the section-aware context to LangGraph, call the same builder in app before run_lg.
    workflow = _build_graph()
    state = workflow.invoke({
        "input_text": input_text or "",
        "notes": "",
        "summary": "",
        "critic": "",
        "meta": "",
        "reader_s": 0.0,
        "summarizer_s": 0.0,
        "critic_s": 0.0,
        "integrator_s": 0.0,
        "_timeout": timeout_s,
    })

    return {
        "structured": state.get("notes", ""),
        "summary": state.get("summary", ""),
        "critic": state.get("critic", ""),
        "meta": state.get("meta", ""),
        "reader_s": state.get("reader_s", 0.0),
        "summarizer_s": state.get("summarizer_s", 0.0),
        "critic_s": state.get("critic_s", 0.0),
        "integrator_s": state.get("integrator_s", 0.0),
        "graph_dot": _graph_dot_static(),
    }
