from __future__ import annotations

import re
from langchain_core.prompts import ChatPromptTemplate
from llm import llm

PROMPT = ChatPromptTemplate.from_template(
    "Create an executive Meta Summary by fusing SUMMARY with the reviewer signal (CRITIC), "
    "grounded strictly in NOTES. Do not invent metrics or citations.\n\n"
    "Summarize the scientific contribution, novelty, and limitations based on the critic feedback."
    "Output:\n"
    "1) Five bullets with **bold labels**: Objective, Method, Results, Limitations, Takeaways\n"
    "2) Two open technical questions\n"
    "3) A one-line Confidence (High/Medium/Low) based on rubric: High if all ≥4; Medium if any 3; Low if any ≤2.\n\n"
    "NOTES:\n{notes}\n\nSUMMARY:\n{summary}\n\nCRITIC:\n{critic}"
)

def _clean(text: str) -> str:
    """Minimal cleanup: trim whitespace."""
    return (text or "").strip()

def run(*args, **kwargs) -> str:
    """
    Preferred: run(notes=<reader_output>, summary=<summarizer_output>, critic=<critic_text>)
    Back-compat: run(summary, critic)
    """
    if args and not kwargs:
        notes = args[0]
        summary = args[0]
        critic = args[1] if len(args) > 1 else ""
    else:
        notes = kwargs.get("notes") or ""
        summary = kwargs.get("summary") or ""
        critic = kwargs.get("critic") or ""

    chain = PROMPT | llm
    out = chain.invoke({"notes": notes, "summary": summary, "critic": critic})
    return _clean(getattr(out, "content", out))
