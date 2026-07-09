"""Curriculum integrity: every catalog entry is well-formed, every available
lesson has a real file behind it."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from tutor import curriculum


def test_index_loads_and_is_nonempty():
    lessons = curriculum.load_index()
    assert len(lessons) >= 3


def test_every_lesson_is_well_formed():
    for l in curriculum.load_index():
        assert l.id and l.title and l.summary, f"incomplete entry: {l.id or '(no id)'}"
        assert l.track in config.TRACKS, f"{l.id}: unknown track '{l.track}'"
        assert l.status in ("available", "planned"), f"{l.id}: bad status '{l.status}'"


def test_available_lessons_have_files():
    for l in curriculum.load_index():
        if l.status == "available":
            assert l.path.exists(), f"{l.id} is 'available' but {l.path.name} is missing"
            text = curriculum.lesson_text(l)
            assert "## Quiz" in text, f"{l.id}: lesson has no Quiz section"


def test_ids_are_unique():
    ids = [l.id for l in curriculum.load_index()]
    assert len(ids) == len(set(ids))
