"""Quiz engine (ADR-022): parse '## Quiz' questions from a lesson, grade
free-text answers against the lesson text ONLY (local Ollama), and record
results under the 'quiz' key in data/progress.json.

Contract:
    parse_quiz(lesson_text)                     -> list[str]
    grade_answer(question, answer, lesson_text) -> {"correct": bool, "feedback": str}
    record_quiz_result(lesson_id, question_idx, correct) -> None
"""
from __future__ import annotations

import json
import re
from datetime import datetime

import config
from tutor import ollama_client

GRADER_SYSTEM = """You are grading a student's free-text answer to a quiz question.
Judge ONLY against the supplied lesson content — it is the sole ground truth.
The answer is correct if it captures the key point(s) the lesson gives for this
question, even if worded differently. Partial but essentially right = correct.
Reply with STRICT JSON and nothing else:
{"correct": true or false, "feedback": "one or two sentences: what was right, what was missed, per the lesson"}"""

_QUIZ_HEADING = re.compile(r"^##\s+Quiz\s*$", re.MULTILINE)
_QUESTION = re.compile(r"^\s*\d+\.\s+(.*)$")


def parse_quiz(lesson_text: str) -> list[str]:
    """Extract the numbered questions under '## Quiz'. Returns [] if absent."""
    heading = _QUIZ_HEADING.search(lesson_text)
    if not heading:
        return []
    section = lesson_text[heading.end():]
    next_heading = re.search(r"^##\s+", section, re.MULTILINE)
    if next_heading:
        section = section[: next_heading.start()]
    questions: list[str] = []
    for line in section.splitlines():
        m = _QUESTION.match(line)
        if m:
            questions.append(m.group(1).strip())
        elif questions and line.strip():
            questions[-1] += " " + line.strip()  # wrapped continuation line
    return questions


def grade_answer(question: str, answer: str, lesson_text: str) -> dict:
    """Grade one free-text answer against the lesson text via local Ollama."""
    prompt = (
        f"LESSON CONTENT:\n{lesson_text}\n\n"
        f"QUIZ QUESTION: {question}\n\n"
        f"STUDENT ANSWER: {answer}"
    )
    raw = ollama_client.generate(GRADER_SYSTEM, prompt, json_format=True)
    return _parse_verdict(raw)


def _parse_verdict(raw: str) -> dict:
    """Extract {"correct": bool, "feedback": str} from model output, robustly."""
    try:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        data = json.loads(m.group(0) if m else raw)
        return {"correct": bool(data.get("correct")),
                "feedback": str(data.get("feedback", "")).strip()}
    except (json.JSONDecodeError, AttributeError, TypeError):
        return {"correct": False,
                "feedback": raw.strip() or "The grader returned no feedback."}


def record_quiz_result(lesson_id: str, question_idx: int, correct: bool) -> None:
    """Append one graded result to progress.json under the 'quiz' key."""
    data: dict = {}
    if config.PROGRESS_PATH.exists():
        data = json.loads(config.PROGRESS_PATH.read_text(encoding="utf-8"))
    data.setdefault("completed", {})
    data.setdefault("quiz", {}).setdefault(lesson_id, []).append({
        "q": int(question_idx),
        "correct": bool(correct),
        "ts": datetime.now().isoformat(timespec="seconds"),
    })
    config.DATA_DIR.mkdir(exist_ok=True)
    config.PROGRESS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
