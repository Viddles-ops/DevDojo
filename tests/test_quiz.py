"""Quiz engine (ADR-022): parser round-trips, verdict-parsing robustness, and
result recording to a temp progress file. No LLM required for any test here."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from tutor import curriculum, quiz

SYNTHETIC = """# Some lesson

Body text with a numbered list that must NOT be parsed as quiz questions:

1. a step
2. another step

## Quiz

1. First question?
2. Second question
   spanning two wrapped lines?
3. Third?
"""


def test_parse_quiz_synthetic():
    qs = quiz.parse_quiz(SYNTHETIC)
    assert qs == ["First question?",
                  "Second question spanning two wrapped lines?",
                  "Third?"]


def test_parse_quiz_ignores_text_without_section():
    assert quiz.parse_quiz("# Lesson\n\n1. numbered\n2. list\n") == []


def test_parse_quiz_stops_at_next_heading():
    text = SYNTHETIC + "\n## After\n\n4. Not a quiz question\n"
    assert len(quiz.parse_quiz(text)) == 3


def test_every_available_lesson_has_parseable_quiz():
    for l in curriculum.load_index():
        if l.is_available:
            qs = quiz.parse_quiz(curriculum.lesson_text(l))
            assert len(qs) >= 2, f"{l.id}: expected >=2 quiz questions, got {len(qs)}"


def test_parse_verdict_clean_json():
    v = quiz._parse_verdict('{"correct": true, "feedback": "ok"}')
    assert v == {"correct": True, "feedback": "ok"}


def test_parse_verdict_json_with_noise():
    noisy = 'Sure! {"correct": false, "feedback": "missed the rescue tag"} hope that helps'
    v = quiz._parse_verdict(noisy)
    assert v["correct"] is False
    assert "rescue" in v["feedback"]


def test_parse_verdict_garbage_fails_safe():
    v = quiz._parse_verdict("not json at all")
    assert v["correct"] is False
    assert v["feedback"]


def test_record_quiz_result(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "PROGRESS_PATH", tmp_path / "progress.json")
    quiz.record_quiz_result("stack-101", 0, True)
    quiz.record_quiz_result("stack-101", 1, False)
    data = json.loads((tmp_path / "progress.json").read_text(encoding="utf-8"))
    entries = data["quiz"]["stack-101"]
    assert len(entries) == 2
    assert entries[0]["q"] == 0 and entries[0]["correct"] is True and entries[0]["ts"]
    assert entries[1]["q"] == 1 and entries[1]["correct"] is False
    assert "completed" in data  # progress.py's key preserved
