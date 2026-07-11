"""Jett Marketing Agent — Flask routes only, no business logic (ADR-003).

Callers:
  - OSKA insights platform (oska_app):  POST /generate  → PDF bytes
  - Browser / manual use:               GET  /          → tiny picker UI
  - Scripts & agents:                   python -m marketer.cli
"""
from __future__ import annotations

import io

from flask import Flask, abort, jsonify, render_template_string, request, send_file

import config
from marketer import narrator, pdf_writer, stats

app = Flask(__name__)

INDEX_HTML = """
<!doctype html><title>Jett Marketing Agent</title>
<body style="font-family:sans-serif;max-width:640px;margin:3rem auto">
<h1>Jett Marketing Agent</h1>
<p>Generate a Jett-branded PDF from an aggregate dataset
   ({{ 'Ollama up' if ollama else 'Ollama down — deterministic narrative' }}).</p>
<ul>
{% for d in datasets %}
  <li><a href="/generate/{{ d }}.pdf">{{ d }}</a></li>
{% else %}
  <li>No datasets in {{ gold_dir }} — set OSKA_GOLD_DIR.</li>
{% endfor %}
</ul></body>
"""


@app.get("/")
def index():
    return render_template_string(
        INDEX_HTML,
        datasets=stats.list_datasets(),
        ollama=narrator.is_up(),
        gold_dir=str(config.GOLD_DIR),
    )


@app.get("/health")
def health():
    return jsonify(status="ok", ollama=narrator.is_up(), datasets=len(stats.list_datasets()))


@app.get("/datasets")
def datasets():
    return jsonify(datasets=stats.list_datasets())


def _build_pdf(dataset_id: str):
    try:
        ds = stats.load_dataset(dataset_id)
    except FileNotFoundError:
        abort(404, f"Unknown dataset: {dataset_id}")
    except (stats.PHIError, ValueError) as exc:
        abort(422, str(exc))
    narrative, _ = narrator.narrate(ds)
    pdf = pdf_writer.render_pdf(ds, narrative)
    return send_file(
        io.BytesIO(pdf),
        mimetype="application/pdf",
        download_name=f"{dataset_id}.pdf",
    )


@app.post("/generate")
def generate():
    payload = request.get_json(silent=True) or {}
    dataset_id = payload.get("dataset")
    if not dataset_id:
        abort(400, "JSON body must include 'dataset'")
    return _build_pdf(dataset_id)


@app.get("/generate/<dataset_id>.pdf")
def generate_get(dataset_id: str):
    return _build_pdf(dataset_id)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=config.APP_PORT, debug=False)
