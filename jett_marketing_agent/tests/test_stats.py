import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from marketer import stats


def _write(tmp_path, name, payload):
    (tmp_path / f"{name}.json").write_text(json.dumps(payload), encoding="utf-8")


@pytest.fixture
def gold_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "GOLD_DIR", tmp_path)
    return tmp_path


VALID = {
    "title": "T",
    "period": "P",
    "metrics": [{"label": "Completion", "value": 91, "unit": "%", "n": 200}],
    "highlights": ["h1"],
}


def test_round_trip(gold_dir):
    _write(gold_dir, "ok", VALID)
    ds = stats.load_dataset("ok")
    assert ds.title == "T" and ds.metrics[0]["value"] == 91
    assert stats.list_datasets() == ["ok"]


def test_phi_key_rejected(gold_dir):
    bad = dict(VALID, patients=[{"patient_id": 1}])
    _write(gold_dir, "bad", bad)
    with pytest.raises(stats.PHIError):
        stats.load_dataset("bad")


def test_nested_phi_key_rejected(gold_dir):
    bad = dict(VALID, metrics=[{"label": "x", "value": 1, "by_member_email": []}])
    _write(gold_dir, "bad", bad)
    with pytest.raises(stats.PHIError):
        stats.load_dataset("bad")


def test_small_cell_suppressed(gold_dir):
    payload = dict(VALID, metrics=VALID["metrics"] + [{"label": "tiny", "value": 5, "n": 4}])
    _write(gold_dir, "sc", payload)
    ds = stats.load_dataset("sc")
    assert ds.suppressed == 1
    assert all(m["label"] != "tiny" for m in ds.metrics)


def test_missing_keys_rejected(gold_dir):
    _write(gold_dir, "bad", {"title": "T"})
    with pytest.raises(ValueError):
        stats.load_dataset("bad")


def test_bad_id_rejected(gold_dir):
    with pytest.raises(ValueError):
        stats.load_dataset("../escape")
