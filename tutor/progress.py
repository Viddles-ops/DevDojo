"""Lesson completion tracking — local JSON, gitignored."""
from __future__ import annotations

import json
from datetime import date

import config


def _load() -> dict:
    if config.PROGRESS_PATH.exists():
        return json.loads(config.PROGRESS_PATH.read_text(encoding="utf-8"))
    return {"completed": {}}


def completed_ids() -> set[str]:
    return set(_load()["completed"])


def mark_complete(lesson_id: str) -> None:
    data = _load()
    data["completed"][lesson_id] = date.today().isoformat()
    config.DATA_DIR.mkdir(exist_ok=True)
    config.PROGRESS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
