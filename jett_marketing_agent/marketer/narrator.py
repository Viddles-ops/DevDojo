"""Compute-then-narrate (workspace ADR-012): every number comes from
stats.py; local Ollama only turns those numbers into brand-voice prose.
If Ollama is down, a deterministic fallback keeps PDFs generating —
the narrative is templated straight from the metrics.
"""
from __future__ import annotations

import requests

import config
from marketer.stats import Dataset

SYSTEM_PROMPT = """You write short marketing copy for Jett Medical, a PEMF
therapy device company. Voice: confident, warm, evidence-led, plain English.
Use ONLY the metrics provided — never invent, extrapolate, or round numbers,
and never make efficacy guarantees or medical claims beyond the data given.
Do not mention any individual person. Write 2 short paragraphs, no headings,
no bullet points, under 150 words total."""


def is_up() -> bool:
    try:
        return requests.get(f"{config.OLLAMA_URL}/api/tags", timeout=3).ok
    except requests.RequestException:
        return False


def _metrics_block(ds: Dataset) -> str:
    lines = [
        f"- {m['label']}: {m['value']}{m.get('unit', '')}"
        + (f" (n={m['n']})" if m.get("n") is not None else "")
        for m in ds.metrics
    ]
    return "\n".join(lines)


def _fallback(ds: Dataset) -> str:
    if not ds.metrics:
        return f"Results for {ds.period} are summarized below."
    parts = [
        f"{m['label'].lower()} of {m['value']}{m.get('unit', '')}" for m in ds.metrics[:3]
    ]
    return (
        f"Over {ds.period}, Jett Medical customers saw {', '.join(parts)}. "
        "All figures are aggregates from the OSKA data pipeline."
    )


def narrate(ds: Dataset) -> tuple[str, bool]:
    """Returns (narrative, used_llm)."""
    prompt = (
        f"DOCUMENT: {ds.title}\nPERIOD: {ds.period}\n"
        f"METRICS:\n{_metrics_block(ds)}\n"
        + (f"HIGHLIGHTS:\n" + "\n".join(f"- {h}" for h in ds.highlights) if ds.highlights else "")
    )
    try:
        resp = requests.post(
            f"{config.OLLAMA_URL}/api/generate",
            json={
                "model": config.OLLAMA_MODEL,
                "system": SYSTEM_PROMPT,
                "prompt": prompt,
                "stream": False,
            },
            timeout=config.OLLAMA_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        text = resp.json().get("response", "").strip()
        if text:
            return text, True
    except requests.RequestException:
        pass
    return _fallback(ds), False
