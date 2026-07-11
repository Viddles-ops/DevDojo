# CLAUDE.md — Jett Marketing Agent

On-demand generator of Jett Medical–branded, customer-facing PDF documents
(study-synopsis style) from aggregate OSKA pipeline stats. Flask + local
Ollama, port **5058**. Local only — no cloud deployment, like DevDojo/oska_app.

## Architecture rules

1. **PHI firewall — aggregates only.** Document data enters ONLY through
   `marketer/stats.py`, which reads Gold-layer aggregate exports
   (`OSKA_GOLD_DIR`). It rejects any dataset with record-level/identifying
   keys (PHIError) and suppresses metrics with n < 11 (small-cell rule).
   Never point `OSKA_GOLD_DIR` at Bronze/Silver — PHI stops at Bronze.
2. **Compute-then-narrate** (workspace ADR-012): every number in a PDF comes
   from stats.py. Ollama only writes prose around the provided metrics; the
   narrator system prompt forbids invented numbers and medical claims, and a
   deterministic fallback keeps generation working when Ollama is down.
3. **Local AI only** (ADR-011): Ollama at `http://localhost:11434`, default
   `qwen2.5:7b-instruct`. No cloud LLM calls, no API keys anywhere.
4. **Modular** (ADR-003): routes in `app.py`; logic in `marketer/` modules.

## Module map

| File | Role |
|---|---|
| `run.ps1` | One-command launch: `.\run.ps1`. |
| `marketer/launcher.py` | Bootstrap + launch, **stdlib only** — creates `.venv`, runs app.py. |
| `app.py` | Flask routes only: `/`, `/health`, `/datasets`, `POST /generate`, `GET /generate/<id>.pdf`. |
| `config.py` | Port, `OSKA_GOLD_DIR`, Ollama settings, `MIN_CELL_SIZE`. No secrets. |
| `marketer/stats.py` | Gold adapter + PHI guard + small-cell suppression. **Adapter seam.** |
| `marketer/narrator.py` | Compute-then-narrate via Ollama; deterministic fallback. |
| `marketer/branding.py` | Jett brand tokens (colors/fonts/disclaimer). **TODO: real palette.** |
| `marketer/pdf_writer.py` | Dataset + narrative → branded PDF. **Synopsis layout seam.** |
| `marketer/cli.py` | `python -m marketer.cli <dataset>` for scripts/agents. |
| `sample_gold/` | Fictional demo dataset so the app runs out of the box. |
| `agents/jett-marketing-agent.md` | Claude Code agent definition → copy to `~\.claude\agents\`. |

## Integration points

- **OSKA insights platform**: `POST http://localhost:5058/generate` with
  `{"dataset": "<id>"}` → PDF bytes. Add a button in oska_app that calls this.
- **Ollama**: consumed by `narrator.py` (this service calls Ollama, not the
  reverse). Any local LLM tool can trigger generation via the HTTP API or CLI.

## Open seams (mine the real repos before customer use)

- `pdf_writer.py`: match the real jAIme study-synopsis layout (pemf_bot_v2).
- `branding.py`: real Jett Medical palette + logo from jett_automations.
- `stats.py`: point `OSKA_GOLD_DIR` at real OSKA gold exports; extend schema
  to whatever the gold layer actually emits.

## Testing

`python -m pytest` (tests/ — PHI guard, small-cell suppression, PDF render).
Smoke test: `python app.py` → http://localhost:5058 must list the sample
dataset and produce a PDF with Ollama stopped (fallback narrative).
