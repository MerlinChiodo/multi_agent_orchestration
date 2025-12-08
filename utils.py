# utils.py
from __future__ import annotations
import re
from typing import Dict, List, Tuple

# ---------- Basic utilities ----------

def _normalize_text(text: str) -> str:
    """
    Light PDF cleanup:
    - join hyphenated line breaks ("algo-\nrithm" -> "algorithm")
    - collapse multiple spaces
    - trim extra blank lines
    """
    t = text or ""
    # fix hyphenation at line breaks
    t = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", t)
    # join hard-wrapped lines when the next line starts lowercase/number/punct
    t = re.sub(r"(?<!\n)\n(?!\n)", "\n", t)  # keep paragraph breaks
    # collapse spaces
    t = re.sub(r"[ \t]+", " ", t)
    # trim trailing spaces per line
    t = "\n".join([ln.rstrip() for ln in t.splitlines()])
    # collapse >2 newlines
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def truncate_text(text: str, max_chars: int | None) -> str:
    """Truncate input text to a maximum number of characters."""
    text = text or ""
    if not max_chars:
        return text
    return text[:max_chars] if len(text) > max_chars else text


# ---------- Metadata / boilerplate cleanup ----------

_META_KWS = r"(?:university|institute|faculty|department|school of|affiliation|corresponding author|preprint|arxiv|doi|copyright|acknowledg(e)?ments?)"

def strip_meta_head(text: str) -> str:
    """
    Remove front-matter lines (authors, emails, affiliations, all-caps banners)
    that often dominate the first PDF page. Aggressive only for the first ~200 lines.
    Preserves an 'Abstract' heading even if uppercase.
    """
    lines = (text or "").splitlines()
    cleaned: List[str] = []
    for idx, ln in enumerate(lines[:200]):
        s = ln.strip()
        if not s:
            continue
        # keep ABSTRACT/Abstract if present
        if re.fullmatch(r"(abstract|ABSTRACT)", s):
            cleaned.append("Abstract")
            continue
        # emails / ORCID / URLs
        if re.search(r"@|orcid\.org|https?://", s, re.I):
            continue
        # affiliations & boilerplate
        if re.search(_META_KWS, s, re.I):
            continue
        # all-caps banners (but avoid short tokens)
        if s.isupper() and len(s) > 6:
            continue
        # typical author-lines like "Omar Khattab, Matei Zaharia"
        if re.match(r"^[A-Z][a-z]+(?: [A-Z]\.)?(?: [A-Z][a-z]+)+(?:, [A-Z][a-z]+.*)*$", s):
            continue
        # page headers like "Proceedings of ..." / "ICLR 2025"
        if re.search(r"(proceedings of|iclr|neurips|icml|acl|emnlp)\b", s, re.I):
            continue
        cleaned.append(ln)
    # keep the rest as-is
    cleaned += lines[200:]
    return _normalize_text("\n".join(cleaned))


def strip_references_tail(text: str) -> str:
    """
    If a clear References/Bibliography header is present, drop everything after it.
    Safe default: only cut when a strong header is detected near the end.
    """
    t = text or ""
    m = re.search(r"\n\s*(references|bibliography)\s*\n", t, re.I)
    if m and len(t) - m.start() > 800:  # avoid cutting if it's too early in the doc
        return t[:m.start()].rstrip()
    return t


# ---------- Section detection ----------

# core patterns
_SECTION_PATTERNS: List[Tuple[str, str]] = [
    ("abstract",     r"\babstract\b"),
    ("introduction", r"\b(introduction|background)\b"),
    ("methods",      r"\b(methods?|methodology|materials? and methods?)\b"),
    ("experiments",  r"\b(experiments?|experimental setup)\b"),
    ("evaluation",   r"\b(evaluation|metrics?)\b"),
    ("results",      r"\bresults?\b"),
    ("discussion",   r"\bdiscussion(s| and results)?\b"),
    ("conclusion",   r"\b(conclusion|conclusions|concluding remarks|summary)\b"),
    ("related",      r"\brelated work\b"),
    ("limitations",  r"\blimitations?\b"),
]

# numeric headings like "1 Introduction", "2.1 Methods", etc.
_NUMERIC_HEADER = (
    r"^\s*(?:\d+(?:\.\d+){0,2})\s+"
    r"(abstract|introduction|background|methods?|methodology|materials? and methods?|"
    r"experiments?|experimental setup|evaluation|metrics?|results?|discussion(?:s| and results)?|"
    r"conclusion|conclusions|concluding remarks|summary|related work|limitations?)\b"
)

def split_sections(text: str) -> Dict[str, str]:
    """
    Split text into approximate sections based on header keywords and numeric headings.
    Returns {section_name: content}. Falls back to {'body': text}.
    """
    t = text or ""
    if not t:
        return {}

    marks: List[Tuple[int, str]] = []

    # keyword-based (anywhere)
    for name, pat in _SECTION_PATTERNS:
        for m in re.finditer(pat, t, flags=re.I):
            marks.append((m.start(), name))

    # numeric headings (multiline)
    for m in re.finditer(_NUMERIC_HEADER, t, flags=re.I | re.M):
        marks.append((m.start(), m.group(1).lower()))

    marks.sort(key=lambda x: x[0])
    if not marks:
        return {"body": t}

    sections: Dict[str, str] = {}
    for i, (pos, name) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(t)
        chunk = t[pos:end].strip()
        # unify 'conclusions' to 'conclusion', etc.
        name = (
            "conclusion" if "conclusion" in name else
            "methods" if name.startswith("method") or "materials" in name else
            "results" if name.startswith("result") else
            "discussion" if name.startswith("discussion") else
            "introduction" if name.startswith("background") else
            name
        )
        sections[name] = (sections.get(name, "") + "\n\n" + chunk).strip()

    return sections


def _select_sections(sections: Dict[str, str], preferred: List[str], budget: int) -> Tuple[str, Dict[str, int]]:
    """
    Select preferred sections up to the character budget.
    Returns (combined_text, usage_map[section -> used_chars]).
    """
    if not sections:
        return "", {}

    chosen: List[str] = []
    remaining = budget
    usage: Dict[str, int] = {}

    # Preferred sections first
    for key in preferred:
        if remaining <= 0:
            break
        txt = sections.get(key, "")
        if not txt:
            continue
        take = txt[:remaining]
        chosen.append(take)
        usage[key] = len(take)
        remaining -= len(take)

    # Then longest remaining ones
    if remaining > 0:
        others = [(k, v) for k, v in sections.items() if k not in preferred and v]
        others.sort(key=lambda kv: len(kv[1]), reverse=True)
        for k, txt in others:
            if remaining <= 0:
                break
            take = txt[:remaining]
            chosen.append(take)
            usage[k] = len(take)
            remaining -= len(take)

    # Fallback: longest paragraphs if only "body"
    if not chosen and "body" in sections:
        paras = [p.strip() for p in sections["body"].split("\n\n") if len(p.strip()) > 80]
        paras.sort(key=len, reverse=True)
        buf: List[str] = []
        cur = 0
        for p in paras:
            if cur + len(p) > budget:
                break
            buf.append(p)
            cur += len(p)
        usage["body"] = cur
        return "\n\n".join(buf).strip(), usage

    return "\n\n".join(chosen).strip(), usage


# ---------- Public API ----------

def build_analysis_context(raw_text: str, cfg: dict) -> str:
    """
    Front-matter cleanup → (optional) References cut → section splitting →
    preferred section selection. If the selected context is too short and
    auto-expansion is enabled, expand to additional sections or fall back to
    full text.
    """
    auto_expand = bool(cfg.get("auto_expand_if_short", True))
    min_chars = int(cfg.get("min_analysis_chars", 800))

    sections_enabled = bool(cfg.get("sections_enabled", True))
    section_budget = int(cfg.get("section_budget_chars", cfg.get("truncate_chars", 2400)))
    preferred = cfg.get("sections_preferred") or ["abstract", "introduction", "methods", "results", "discussion", "conclusion"]

    # Normalize + strip head + (optionally) cut references tail
    cleaned = _normalize_text(raw_text or "")
    cleaned = strip_meta_head(cleaned)
    cleaned = strip_references_tail(cleaned)

    # No sectioning → plain truncate
    if not sections_enabled:
        return truncate_text(cleaned, section_budget)

    # Sectioning path
    sections = split_sections(cleaned)
    ctx, usage = _select_sections(sections, preferred, section_budget)

    # --- AUTO-EXPAND LOGIC ---
    if auto_expand and len(ctx) < min_chars:
        # 1) expand with non-preferred sections
        if sections:
            remaining_budget = section_budget - len(ctx)
            extra_chunks = []
            if remaining_budget > 0:
                others = [(k, v) for k, v in sections.items() if k not in preferred and v]
                others.sort(key=lambda kv: len(kv[1]), reverse=True)
                for _, txt in others:
                    if remaining_budget <= 0:
                        break
                    take = txt[:remaining_budget]
                    if take:
                        extra_chunks.append(take)
                        remaining_budget -= len(take)
            if extra_chunks:
                ctx = (ctx + ("\n\n" if ctx else "") + "\n\n".join(extra_chunks)).strip()

        # 2) still too short → fall back to plain truncated full text
        if len(ctx) < min_chars:
            ctx = truncate_text(cleaned, section_budget)

    return ctx


def preview_sections(raw_text: str, cfg: dict) -> Dict[str, int]:
    """
    Return how many characters per section would be included in the analysis context.
    Useful for UI preview (keeps the same contract as before).
    """
    sections_enabled = bool(cfg.get("sections_enabled", True))
    section_budget = int(cfg.get("section_budget_chars", cfg.get("truncate_chars", 2400)))
    preferred = cfg.get("sections_preferred") or ["abstract", "introduction", "methods", "results", "discussion", "conclusion"]

    cleaned = _normalize_text(raw_text or "")
    cleaned = strip_meta_head(cleaned)
    cleaned = strip_references_tail(cleaned)

    if not sections_enabled:
        return {"body": min(len(cleaned), section_budget)}

    sections = split_sections(cleaned)
    _, usage = _select_sections(sections, preferred, section_budget)
    return usage
