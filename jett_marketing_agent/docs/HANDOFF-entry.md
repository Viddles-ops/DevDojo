<!--
OPERATOR ARTIFACT — not part of the app.
Prepend this block as the NEW TOP ENTRY of your workspace _operator/HANDOFF.md
on your laptop. chief-operator did not run in the remote session that produced
this work; this is the operator record backfilled to meet the cc-101 resume bar.
-->

## 2026-07-16 — Jett Marketing Agent scaffolded (remote session, started on mobile)

**Goal:** An agent that fills Jett Medical–branded, customer-facing PDFs
(study-synopsis style, like jAIme/pemf_bot_v2's synopses) **on demand** with
stats/insights from the OSKA data pipeline. Callable by the OSKA insights
platform, by local Ollama-driven tools, and by CLI.

**State: DONE (scaffold) — works end-to-end on fictional sample data. NOT yet
wired to real gold data, real synopsis layout, or real Jett branding.**
Pushed to DevDojo repo, branch `claude/jett-marketing-agent-m07ond`, folder
`jett_marketing_agent/`.

**Operator note:** chief-operator did NOT run — the session was a remote cloud
container with no access to `~/.claude/agents/` or this `_operator/` folder.
Claude orchestrated directly. Also: adds of `pemf-bot-v2` and `oska-platform`
were blocked by the platform, so the real synopsis format and gold schema were
NOT inspected — they're the seams below.

**Verified working:**
- Flask API on :5058 — `POST /generate {"dataset":"<id>"}` → PDF bytes;
  `GET /generate/<id>.pdf`; plus `/health`, `/datasets`.
- CLI: `python -m marketer.cli <dataset> --out file.pdf`.
- Compute-then-narrate: numbers from `marketer/stats.py`; local Ollama narrates;
  deterministic fallback when Ollama is down (that's how the sample PDF was made).
- PHI firewall in `stats.py`: rejects record-level/identifying keys, suppresses
  metrics with n < 11; every PDF carries a provenance + no-PHI footer.
- 8 new pytest tests pass; DevDojo's existing 4 still pass; live API smoke-tested
  (health, generate → valid %PDF, 400/404 error paths); real PDF rendered.

**Next — the three seams to close before real use (each is one file):**
1. **Data** — point `OSKA_GOLD_DIR` at the real OSKA Gold-layer export folder
   (schema documented in `marketer/stats.py`). Currently → bundled fictional
   `sample_gold/`. Confirm the real gold schema matches; extend loader if not.
   NEVER point at Bronze/Silver (PHI).
2. **Layout** — `marketer/pdf_writer.py` approximates the synopsis structure;
   mine the real jAIme layout from `pemf_bot_v2` and match it (code + docs only,
   never its data dirs — PHI).
3. **Brand** — `marketer/branding.py` has a PLACEHOLDER navy/teal palette + text
   wordmark. Replace with the real Jett Medical palette and drop the logo at
   `assets/jett_logo.png` (from `jett_automations` brand assets).

**Local rollout (what "available on my laptop" means):**
- Move `jett_marketing_agent/` out of the DevDojo repo to the projects root — it's
  fully self-contained (own `.venv` via `run.ps1`).
- Copy `agents/jett-marketing-agent.md` into `C:\Users\natee\.claude\agents\` to
  summon it by name (like chief-operator / deploy-guard).
- `.\run.ps1` → http://localhost:5058. Works with Ollama stopped (fallback prose).

**Open questions for next session:**
- Verify real gold-export schema vs `stats.py`'s expected shape.
- Human sign-off on brand + numbers required before ANY real customer document.
- A hosted/shared deployment (vs laptop-local) is out of scope and would need its
  own ADR — currently local-only per ADR-011.

**Resume test (cc-101 bar):** everything needed to continue is above, plus the
branch and `jett_marketing_agent/CLAUDE.md`. Start at the three seams.
