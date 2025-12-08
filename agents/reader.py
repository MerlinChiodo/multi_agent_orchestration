from __future__ import annotations
from langchain_core.prompts import ChatPromptTemplate
from llm import llm

PROMPT = ChatPromptTemplate.from_template(
    "You are a precise scientific note-taker. Work ONLY with the TEXT below. "
    "If an item is not explicitly stated, write 'not reported'. "
    "Do NOT invent facts. Do NOT include author names, emails, or affiliations.\n\n"
    "Return notes in EXACTLY this Markdown schema (keep the headings as written):\n\n"
    "Title: <paper title or 'not reported'>\n"
    "Objective: <1-2 sentences>\n"
    "Methods:\n"
    "- <technique/model>\n"
    "- <training/eval setup>\n"
    "- <tooling/frameworks>\n"
    "Datasets/Corpora: <names or 'not reported'>\n"
    "Results (key numbers if present):\n"
    "- <metric: value on dataset>\n"
    "- <ablation/comparison>\n"
    "Contributions:\n"
    "- <main contribution>\n"
    "- <secondary>\n"
    "Limitations: <short phrase or 'not reported'>\n"
    "Applications/Use-cases: <short phrase or 'not reported'>\n"
    "Notes:\n"
    "- <any other salient detail>\n\n"
    "TEXT:\n{content}"
)

def _clean(text: str) -> str:
    """Minimal cleanup: trim whitespace, no citation stripping."""
    return (text or "").strip()

def run(content: str) -> str:
    """Generate structured notes from text."""
    chain = PROMPT | llm
    out = chain.invoke({"content": content})
    return _clean(getattr(out, "content", out))
