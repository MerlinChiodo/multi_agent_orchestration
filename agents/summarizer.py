from __future__ import annotations
from langchain_core.prompts import ChatPromptTemplate
from llm import llm

PROMPT = ChatPromptTemplate.from_template(
    "Produce a concise scientific summary (200-300 words) of the paper described in the NOTES. "
    "Cover, in this order: Objective -> Method (what/how) -> Results (numbers if present; otherwise say 'not reported') "
    "-> Limitations -> 3-5 Practical Takeaways (bulleted). "
    "Avoid speculation or citations.\n\n"
    "NOTES:\n{notes}"
)

def _clean(text: str) -> str:
    """Minimal cleanup: trim whitespace, no citation stripping."""
    return (text or "").strip()

def run(notes: str) -> str:
    """Generate summary text from structured notes."""
    chain = PROMPT | llm
    out = chain.invoke({"notes": notes})
    return _clean(getattr(out, "content", out))
