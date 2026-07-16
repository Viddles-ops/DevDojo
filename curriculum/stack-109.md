# On-demand branded documents: the Jett Marketing Agent

The Jett Marketing Agent turns OSKA pipeline numbers into Jett Medical–branded,
customer-facing PDFs (study-synopsis style, like jAIme's) **on demand**. It
lives in its own repo (`jett-marketing-agent`) and is a compact case study in
three patterns you already use — plus one new guardrail worth stealing.

## 1. Compute-then-narrate, reused (ADR-012)

Same rule as OSKA: Python owns the numbers, the LLM owns the prose. Every
figure in a PDF comes from `marketer/stats.py`; `marketer/narrator.py` sends
those numbers to local Ollama with a system prompt that forbids inventing
numbers or making medical claims — and falls back to a deterministic,
templated narrative when Ollama is down, so PDF generation never stops.

## 2. The PHI firewall (the new idea)

Customer-facing docs must never leak PHI, so document data enters through
exactly one door — `marketer/stats.py` — which reads only Gold-layer
*aggregate* exports and does two things no other module may skip:

- **Rejects record-level data:** any dataset carrying identifying keys
  (`patient`, `mrn`, `dob`, `email`…) raises `PHIError`.
- **Suppresses small cells:** any metric computed over n < 11 records is dropped.

Every PDF then carries a provenance + no-PHI footer. The teachable move: put
the safety rule *inside the single module that owns the data door*, so every
caller inherits it for free — the same principle as deploy-guard owning the
risky tool (cc-102).

## 3. One capability, three front doors

The same generation logic is reachable as an HTTP endpoint (`POST /generate`
— for the OSKA insights platform), a CLI (`python -m marketer.cli` — for
scripts), and a Claude Code agent (`agents/jett-marketing-agent.md`). Routes
in `app.py` stay logic-free (ADR-003); everything real lives in `marketer/`.

## Adapter seams

Three placeholders keep it honest until it's wired to reality: `OSKA_GOLD_DIR`
(point at real gold exports), `pdf_writer.py` (match the real jAIme synopsis
layout), and `branding.py` (real Jett palette + logo).

## Try it

Clone `jett-marketing-agent`, run `.\run.ps1`, and generate the sample PDF with
Ollama stopped. Then open `marketer/stats.py` and find the two lines that make
it impossible for a customer PDF to contain a single patient's data.

## Quiz

1. Where do the numbers in a PDF come from, and what is the LLM's only job?
2. Name the two things the stats loader does to enforce the PHI firewall.
3. Why does putting the suppression rule in `stats.py` — not in each caller —
   matter, and which earlier lesson uses the same principle?
