<!--
OPERATOR ARTIFACT — not part of the app.
Append this ADR to your workspace _operator/DECISIONS.md on your laptop.
Number is a DRAFT: ADR-012 is the highest referenced in the DevDojo curriculum;
bump to the next free number if your DECISIONS.md is further along.
-->

## ADR-013 — Jett Marketing Agent: aggregates-only, local, standalone

**Status:** Draft / proposed (2026-07-16) — accept after review on the laptop
**Relates to:** ADR-003 (modular), ADR-011 (local AI only), ADR-012 (compute-then-narrate)

### Context
We want on-demand generation of Jett Medical–branded, customer-facing PDF
documents — study-synopsis style, modeled on the jAIme / `pemf_bot_v2` synopsis
documents — populated with stats and insights from the OSKA data pipeline, and
callable both by the OSKA insights platform and by local Ollama-driven tooling.
OSKA data carries PHI at Bronze/Silver; these documents are customer-facing, so
the data path is the primary risk.

### Decision
1. **Standalone project**, not a module of `oska-platform` or `jett-automations`
   (`jett_marketing_agent/`, port 5058). Single responsibility, own `.venv` and
   release cadence, matches the one-project-per-folder convention. Delivered
   inside the DevDojo repo for convenience; to be moved to the projects root.
2. **Aggregates-only PHI firewall.** All document data enters through one adapter
   (`marketer/stats.py`) that reads only Gold-layer aggregate exports, hard-rejects
   any record-level/identifying keys (`PHIError`), and suppresses metrics with
   n < 11. Bronze/Silver are off-limits. Every PDF carries a provenance + no-PHI
   disclaimer in the footer.
3. **Reuse compute-then-narrate (ADR-012).** Every number originates in `stats.py`;
   local Ollama only writes prose around those numbers; the narrator system prompt
   forbids invented numbers and medical/efficacy claims; a deterministic fallback
   keeps generation working when Ollama is down.
4. **Local-only (upholds ADR-011).** Local Ollama, no cloud LLM, no API keys, no
   hosted endpoint. "Production" for now means running on the laptop. A hosted or
   shared deployment, if ever wanted, requires its own ADR — it is not a default.

### Consequences
- (+) Customer documents structurally cannot contain PHI; enforced in code and
  covered by tests.
- (+) Works offline / with Ollama down via the deterministic narrative path.
- (+) Clear integration surface (`POST /generate`) for the OSKA platform.
- (−) Real branding, real synopsis layout, and real gold-data wiring are deferred
  to three explicit seams; the agent is NOT customer-ready until those are closed
  and a human signs off on brand + numbers.
- (−) Narrative quality depends on the local model; fallback prose is plain.
