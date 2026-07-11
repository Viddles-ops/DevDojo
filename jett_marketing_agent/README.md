# Jett Marketing Agent

Generates Jett Medical–branded, customer-facing PDF documents on demand —
study-synopsis style — from **aggregate** stats produced by the OSKA data
pipeline. Runs entirely locally: Flask API + local Ollama for the narrative
voice. No cloud, no API keys.

> **This folder is a standalone project.** It lives inside the DevDojo repo
> only for delivery — move the whole `jett_marketing_agent/` folder to the
> Viddles-ops projects root and it runs as its own app with its own `.venv`.

## Run it

```powershell
cd jett_marketing_agent
.\run.ps1
# → http://localhost:5058
```

Open the page, click a dataset, get a branded PDF. Works with Ollama stopped
(a deterministic narrative built from the metrics is used instead).

## Calling it

```bash
# From the OSKA insights platform (or anything else, incl. Ollama-driven tools):
curl -X POST http://localhost:5058/generate \
     -H "Content-Type: application/json" \
     -d '{"dataset": "sample-q2-2026-outcomes"}' -o synopsis.pdf

# From a script or agent:
python -m marketer.cli sample-q2-2026-outcomes --out synopsis.pdf
```

A Claude Code agent definition is included at
`agents/jett-marketing-agent.md` — copy it to `C:\Users\natee\.claude\agents\`
to summon it by name, the same way chief-operator and deploy-guard work.

## Wiring it to real data (the three seams)

1. **Stats** — set `OSKA_GOLD_DIR` to the OSKA pipeline's Gold-layer export
   folder (one JSON per dataset; schema documented in `marketer/stats.py`).
   Bronze/Silver are off-limits: the loader hard-rejects record-level keys
   and suppresses metrics with n < 11.
2. **Synopsis layout** — `marketer/pdf_writer.py` approximates the jAIme
   study-synopsis structure; adjust section order/wording to match
   pemf_bot_v2's real documents.
3. **Brand** — replace the placeholder palette in `marketer/branding.py`
   with the real Jett Medical colors and drop a logo at
   `assets/jett_logo.png`.

## PHI stance

Customer-facing documents are built exclusively from Gold-layer aggregates.
The loader (`marketer/stats.py`) refuses datasets containing identifying or
record-level keys, suppresses small cells (n < 11), and every PDF carries a
provenance + no-PHI disclaimer in the footer.

## Test

```bash
python -m pytest
```
