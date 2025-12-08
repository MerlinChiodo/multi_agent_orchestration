# telemetry.py
import time, os, csv
from contextlib import contextmanager
from typing import Iterable

_DEFAULT_FIELDS: list[str] = [
    "engine",          # "langchain" | "langgraph" | "dspy"
    "input_chars",     # Länge des Eingabetextes
    "summary_len",     # Länge der Summary
    "meta_len",        # Länge der Meta-Summary
    "latency_s",       # Gesamtzeit in Sekunden
    "reader_s",        # Stage-Zeiten optional (werden oft gesetzt)
    "summarizer_s",
    "critic_s",
    "integrator_s",
]

def _ensure_fields(row: dict) -> list[str]:
    """Nimmt die Default-Spalten und erweitert sie um evtl. zusätzliche Keys aus row (stabile Reihenfolge)."""
    fields = list(_DEFAULT_FIELDS)
    for k in row.keys():
        if k not in fields:
            fields.append(k)
    return fields

@contextmanager
def timer():
    """Context-Manager für einfache Zeitmessung in Sekunden."""
    t0 = time.perf_counter()
    data = {}
    try:
        yield data
    finally:
        data["elapsed_s"] = time.perf_counter() - t0
        print(f"[Telemetry] elapsed: {data['elapsed_s']:.2f}s")

def log_row(row: dict, path: str = "telemetry.csv"):
    """
    Schreibt eine Zeile Telemetrie. Wenn neue Keys auftauchen, werden sie in die Spaltenliste aufgenommen.
    Bestehende CSVs bleiben kompatibel (zusätzliche Spalten erscheinen dann hinten).
    """
    row = dict(row or {})
    fields = _ensure_fields(row)

    exists = os.path.exists(path)
    # Falls Datei existiert, versuchen wir die bestehende Kopfzeile einzulesen und zu vereinen
    if exists:
        try:
            with open(path, "r", encoding="utf-8", newline="") as f:
                r = csv.reader(f)
                first = next(r, None)
                if first:
                    old_fields = list(first)
                    # merge, preserving old order
                    for k in fields:
                        if k not in old_fields:
                            old_fields.append(k)
                    fields = old_fields
        except Exception:
            # Wenn Lesen fehlschlägt, schreiben wir einfach mit neuen Feldern weiter
            pass

    # Schreiben
    write_header = not exists
    # Wenn Datei existiert, aber wir neue Felder entdeckt haben, schreiben wir zur Sicherheit die Header erneut
    if exists:
        try:
            with open(path, "r", encoding="utf-8", newline="") as f:
                rd = csv.reader(f)
                first = next(rd, None)
                write_header = (not first) or (first != fields)
        except Exception:
            write_header = True

    # Wenn Header sich geändert hat, rotieren wir auf eine neue Datei (verlustfrei)
    if exists and write_header:
        base, ext = os.path.splitext(path)
        rotated = f"{base}.bak"
        try:
            os.replace(path, rotated)
            exists = False  # damit unten Header neu geschrieben wird
        except Exception:
            pass

    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        if not exists:
            w.writeheader()
        w.writerow(row)
