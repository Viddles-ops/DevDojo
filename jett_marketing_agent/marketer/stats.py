"""Gold-layer stats adapter — the ONLY place document data enters the agent.

Reads aggregate stats datasets (one JSON file per dataset) from
config.GOLD_DIR and enforces the PHI firewall: record-level or
identifier-shaped data is rejected outright, and small-cell metrics are
suppressed. Everything downstream (narrator, PDF) may only consume what
this module returns.

ADAPTER SEAM: point OSKA_GOLD_DIR at the real OSKA Gold-layer export
folder. Expected dataset schema:

    {
      "title": "Q2 2026 PEMF Therapy Outcomes",
      "period": "Apr-Jun 2026",
      "source": "oska gold: therapy_outcomes",
      "metrics": [
        {"label": "Avg pain score reduction", "value": 38, "unit": "%", "n": 214}
      ],
      "highlights": ["Optional pre-written headline facts."]
    }
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

import config


class PHIError(ValueError):
    """Raised when a dataset looks like it contains record-level/PHI data."""


# Keys that indicate record-level or identifying data. Substring match,
# case-insensitive — err on the side of rejecting.
_SUSPECT_KEY_PATTERN = re.compile(
    r"patient|member|subject|mrn|ssn|dob|birth|first_name|last_name|full_name"
    r"|email|phone|address|zip|postal|record_id",
    re.IGNORECASE,
)

_REQUIRED_TOP_LEVEL = {"title", "period", "metrics"}


@dataclass
class Dataset:
    dataset_id: str
    title: str
    period: str
    source: str
    metrics: list[dict] = field(default_factory=list)
    highlights: list[str] = field(default_factory=list)
    suppressed: int = 0  # metrics dropped by small-cell suppression


def _scan_for_phi(node, path="$") -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if _SUSPECT_KEY_PATTERN.search(str(key)):
                raise PHIError(
                    f"Refusing dataset: key '{key}' at {path} looks record-level/identifying. "
                    "Customer-facing documents may only use Gold-layer aggregates."
                )
            _scan_for_phi(value, f"{path}.{key}")
    elif isinstance(node, list):
        for i, item in enumerate(node):
            _scan_for_phi(item, f"{path}[{i}]")


def list_datasets() -> list[str]:
    if not config.GOLD_DIR.is_dir():
        return []
    return sorted(p.stem for p in config.GOLD_DIR.glob("*.json"))


def load_dataset(dataset_id: str) -> Dataset:
    if not re.fullmatch(r"[\w\-]+", dataset_id):
        raise ValueError(f"Invalid dataset id: {dataset_id!r}")
    path = config.GOLD_DIR / f"{dataset_id}.json"
    if not path.is_file():
        raise FileNotFoundError(f"No dataset '{dataset_id}' in {config.GOLD_DIR}")
    raw = json.loads(path.read_text(encoding="utf-8"))

    missing = _REQUIRED_TOP_LEVEL - raw.keys()
    if missing:
        raise ValueError(f"Dataset '{dataset_id}' missing keys: {sorted(missing)}")
    _scan_for_phi(raw)

    kept, suppressed = [], 0
    for metric in raw["metrics"]:
        n = metric.get("n")
        if n is not None and n < config.MIN_CELL_SIZE:
            suppressed += 1
            continue
        kept.append(metric)

    return Dataset(
        dataset_id=dataset_id,
        title=str(raw["title"]),
        period=str(raw["period"]),
        source=str(raw.get("source", f"gold: {dataset_id}")),
        metrics=kept,
        highlights=[str(h) for h in raw.get("highlights", [])],
        suppressed=suppressed,
    )
