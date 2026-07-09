"""Local Ollama client. The tutor narrates the curriculum — it never freelances
facts about Nate's projects (see CLAUDE.md rule 1)."""
from __future__ import annotations

import requests

import config

SYSTEM_PROMPT = """You are DevDojo, a friendly coding tutor for one developer.
Answer using ONLY the lesson content provided. Be concrete and encouraging.
If the question goes beyond the lesson, first say what the lesson does cover,
then answer from general knowledge prefixed with 'Beyond the lesson:'.
Keep answers under 250 words. Never invent details about the user's projects."""


def is_up() -> bool:
    try:
        return requests.get(f"{config.OLLAMA_URL}/api/tags", timeout=3).ok
    except requests.RequestException:
        return False


def ask(question: str, grounding: str = "") -> str:
    prompt = (
        f"LESSON CONTENT:\n{grounding or '(no lesson selected)'}\n\n"
        f"STUDENT QUESTION: {question}"
    )
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
    return resp.json().get("response", "").strip()
