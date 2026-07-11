import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from marketer import narrator, pdf_writer, stats


def test_sample_dataset_renders_pdf(monkeypatch):
    monkeypatch.setattr(config, "GOLD_DIR", Path(__file__).resolve().parent.parent / "sample_gold")
    ds = stats.load_dataset("sample-q2-2026-outcomes")
    narrative = narrator._fallback(ds)  # deterministic — no Ollama in CI
    pdf = pdf_writer.render_pdf(ds, narrative)
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000


def test_fallback_narrative_uses_real_numbers(monkeypatch):
    monkeypatch.setattr(config, "GOLD_DIR", Path(__file__).resolve().parent.parent / "sample_gold")
    ds = stats.load_dataset("sample-q2-2026-outcomes")
    text = narrator._fallback(ds)
    assert "38%" in text and ds.period in text
