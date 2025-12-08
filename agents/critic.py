from __future__ import annotations
from typing import Any, Dict
from langchain_core.prompts import ChatPromptTemplate
from llm import llm

PROMPT = ChatPromptTemplate.from_template(
    "You are a rigorous scientific reviewer. Judge the SUMMARY only against the NOTES (the ground truth). "
    "Penalize any claim not supported by NOTES.\n\n"
    "RUBRIC (0-5 integers):\n"
    "- Coherence: logical flow, no contradictions.\n"
    "- Groundedness: claims are supported by NOTES.\n"
    "- Coverage: objective, method, results, limitations are covered.\n"
    "- Specificity: salient details included when NOTES provide them.\n\n"
    "OUTPUT FORMAT (exactly, no extra text):\n"
    "Coherence: <0-5>\n"
    "Groundedness: <0-5>\n"
    "Coverage: <0-5>\n"
    "Specificity: <0-5>\n"
    "Improvements:\n"
    "- <short fix #1>\n"
    "- <short fix #2>\n"
    "- <optional fix #3>\n\n"
    "NOTES:\n{notes}\n\nSUMMARY:\n{summary}"
)

def _clean(text: str) -> str:
    """Minimal cleanup: trim whitespace."""
    return (text or "").strip()

def run(*args, **kwargs) -> Dict[str, Any]:
    """
    Preferred: run(notes=<reader_output>, summary=<summarizer_output>)
    Back-compat: run(<summary_only>) -> compares summary to itself.
    Returns {'critic': text, 'critique': text}
    """
    if args and not kwargs:
        notes = args[0]
        summary = args[0]
    else:
        notes = kwargs.get("notes") or ""
        summary = kwargs.get("summary") or ""

    chain = PROMPT | llm
    out = chain.invoke({"notes": notes, "summary": summary})
    text = _clean(getattr(out, "content", out))
    return {"critic": text, "critique": text}
