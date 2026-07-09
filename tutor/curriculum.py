"""Curriculum loader: index.yaml is the catalog, one markdown file per lesson."""
from __future__ import annotations

from dataclasses import dataclass

import yaml

import config


@dataclass
class Lesson:
    id: str
    title: str
    track: str
    status: str          # available | planned
    summary: str = ""
    sources: list = None  # project names this lesson was mined from

    @property
    def path(self):
        return config.CURRICULUM_DIR / f"{self.id}.md"

    @property
    def is_available(self) -> bool:
        return self.status == "available" and self.path.exists()


def load_index() -> list[Lesson]:
    with open(config.CURRICULUM_DIR / "index.yaml", "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    return [Lesson(sources=item.get("sources", []),
                   **{k: item[k] for k in ("id", "title", "track", "status", "summary") if k in item})
            for item in raw["lessons"]]


def get_lesson(lesson_id: str) -> Lesson | None:
    return next((l for l in load_index() if l.id == lesson_id), None)


def lesson_text(lesson: Lesson) -> str:
    return lesson.path.read_text(encoding="utf-8")


def by_track(lessons: list[Lesson]) -> dict[str, list[Lesson]]:
    grouped: dict[str, list[Lesson]] = {t: [] for t in config.TRACKS}
    for lesson in lessons:
        grouped.setdefault(lesson.track, []).append(lesson)
    return grouped
