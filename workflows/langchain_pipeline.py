from agents.reader import run as run_reader
from agents.summarizer import run as run_summarizer
from agents.critic import run as run_critic
from agents.integrator import run as run_integrator
from telemetry import log_row
from llm import configure
from time import perf_counter


def _truncate_text(text: str, max_chars: int | None) -> str:
    """Truncate input text to n characters."""
    text = text or ""
    if not max_chars:
        return text
    return text[:max_chars] if len(text) > max_chars else text


def _extract_sections(input_text: str) -> dict:
    """
    Split paper into main sections if possible.
    Returns a dictionary with {section_name: text}.
    """
    sections = {
        "abstract": "",
        "introduction": "",
        "methods": "",
        "results": "",
        "discussion": "",
        "conclusion": "",
    }

    lowered = input_text.lower()
    positions = {}
    for key in sections.keys():
        idx = lowered.find(key)
        if idx != -1:
            positions[key] = idx

    keys_sorted = sorted(positions.items(), key=lambda x: x[1])

    for i, (key, start) in enumerate(keys_sorted):
        end = keys_sorted[i + 1][1] if i + 1 < len(keys_sorted) else len(input_text)
        sections[key] = input_text[start:end].strip()

    return sections


def run_pipeline(input_text: str, cfg: dict | None = None) -> dict:
    """Full LangChain pipeline (Reader → Summarizer → Critic → Integrator)."""
    cfg = cfg or {}
    configure(cfg)

    truncated_text = _truncate_text(input_text, cfg.get("truncate_chars"))

    if not truncated_text or len(truncated_text.strip()) < 100:
        return {
            "structured": "[Input empty or too short]",
            "summary": "",
            "critic": "",
            "meta": "⚠️ No valid text detected. Try disabling truncation or re-uploading the PDF.",
            "reader_s": 0.0,
            "summarizer_s": 0.0,
            "critic_s": 0.0,
            "integrator_s": 0.0,
        }

    # Extract sections if possible
    sections = _extract_sections(truncated_text)

    # Combine key sections for summarization
    combined_text = (
        sections["abstract"]
        + "\n\n"
        + sections["introduction"]
        + "\n\n"
        + sections["methods"]
        + "\n\n"
        + sections["results"]
        + "\n\n"
        + sections["discussion"]
        + "\n\n"
        + sections["conclusion"]
    ).strip() or truncated_text

    # --- Run agents sequentially ---
    t0 = perf_counter()
    reader_output = run_reader(combined_text)
    t1 = perf_counter()

    summarizer_output = run_summarizer(reader_output)
    t2 = perf_counter()

    # ✅ UPDATED: critic compares summary vs reader notes
    critic_dict = run_critic(notes=reader_output, summary=summarizer_output)
    critic_output = critic_dict.get("critic") or critic_dict.get("critique") or ""
    t3 = perf_counter()

    # ✅ UPDATED: integrator fuses notes + summary + critic
    integrator_output = run_integrator(
        notes=reader_output, summary=summarizer_output, critic=critic_output
    )
    t4 = perf_counter()

    # ✅ UPDATED timing
    timings = {
        "reader_s": round(t1 - t0, 2),
        "summarizer_s": round(t2 - t1, 2),
        "critic_s": round(t3 - t2, 2),
        "integrator_s": round(t4 - t3, 2),
    }
    total_time = round(t4 - t0, 2)

    log_row(
        {
            "engine": "langchain",
            "input_chars": len(truncated_text),
            "summary_len": len(str(summarizer_output)),
            "meta_len": len(str(integrator_output)),
            "latency_s": total_time,
            **timings,
        }
    )

    return {
        "structured": reader_output,
        "summary": summarizer_output,
        "critic": critic_output,
        "meta": integrator_output,
        **timings,
    }
