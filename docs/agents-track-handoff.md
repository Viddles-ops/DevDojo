# DevDojo "Agents" Track — Handoff Prompt (2026-07-23)

Paste everything below the line into a fresh Claude Code session.

---

Project: DevDojo — C:\Users\natee\OneDrive\Documents\Claude\Projects\DevDojo
Task: Write the new "agents" curriculum track (9 lessons, agent-101..agent-109).
Read DevDojo's CLAUDE.md first — it is authoritative. Then execute:

STEP 0 — Track registration (do first; tests depend on it):
- In config.py, add to TRACKS: "agents": "Agents — design, build, and ship AI agents"
- In curriculum/index.yaml, add a "# ── Track: agents ──" section with all 9
  entries (id, title, track: agents, status: planned, summary, sources),
  matching the existing YAML style exactly.
- Run `python -m pytest` — must pass before writing any lesson.

STEP 1 — Write lessons one at a time, flipping each index.yaml status
planned → available as its curriculum/<id>.md lands. One commit per lesson.

THE 9 LESSONS (id / title / what it teaches / sources to mine):
1. agent-101 "What an agent actually is: model + tools + loop + state" —
   demystify: LLM in a perceive→decide→act loop. Compare OpsForge's coded
   loop (OpsForge\opsforge\core\loop.py, triggers.py, decision.py) with the
   chief-operator's prose loop (Orient→Decide→Decompose→Lane→Execute→Gate→
   Record, in C:\Users\natee\.claude\agents\chief-operator.md).
2. agent-102 "Tool use: how an LLM does things" — tool schemas, call/result
   round trip, narrow tool surfaces. Worked example: deploy-guard
   (C:\Users\natee\.claude\agents\deploy-guard.md) — one CLI + doctrine; its
   frontmatter tools: list as a permission boundary.
3. agent-103 "The framework landscape: Claude Agent SDK, LangGraph, or plain
   Python" — honest survey: Claude Agent SDK (what Claude Code runs on),
   LangChain/LangGraph, and plain-Python loops. Key point: OpsForge uses NO
   agent framework (Pydantic + SQLite + a loop; see its CLAUDE.md "Stack" —
   "complexity must be earned"). Teach when a framework pays for itself.
4. agent-104 "MCP: the USB port for agent tools" — what MCP is, servers vs
   tools, decoupling agents from integrations. Contrast with OpsForge's
   MessageChannel transport abstraction (opsforge\transport\) — same
   decoupling instinct built by hand.
5. agent-105 "Agent memory I: the context window and summarization" —
   short-term memory = what fits in the prompt. Grounding (DevDojo's own
   /ask), context assembly (opsforge\memory\context.py), summarization
   (opsforge\memory\summary.py).
6. agent-106 "Agent memory II: persistent state, files vs DB, retrieval" —
   OpsForge's SQLite + ledger (opsforge\memory\ledger.py, published-snapshot
   pattern per its ADR-003/operator ADR-026) vs the operator's markdown
   memory (_operator\HANDOFF.md/BACKLOG.md/DECISIONS.md — one home per fact)
   vs RAG-as-memory (link to stack-105, don't repeat it). When each fits.
7. agent-107 "Orchestration: one agent driving others" — the operator's
   delegation model (fresh-context executors fed a written plan + CLAUDE.md,
   model routing by task shape, never two subagents in the same files) and
   OpsForge's peer-coordination stance (recommend-never-assign, 4-agent
   InterAgentLab experiment). Orchestrator vs peer topologies.
8. agent-108 "Shipping an agent: guardrails, logging, human in the loop" —
   OpsForge's JSON-log-everything rule (incl. decisions to stay silent),
   safety\ gating, LLM-free decision core; deploy-guard's
   check→record→mark→restore protocol as human-in-the-loop design; local vs
   cloud placement (HIPAA forces Ollama-local for OSKA/PO-Intake data).
9. agent-109 "Do agents learn? Evals, feedback loops, honest mental models" —
   capstone. Agents do NOT machine-learn from use. Improvement = eval-driven
   iteration (OpsForge verify\ checklists + analysis\ deterministic Monte
   Carlo forecasts), feedback loops that update prompts/curriculum/memory,
   and the decision tree: prompt change vs RAG vs memory write vs
   fine-tuning (and why fine-tuning is rarely the answer locally). Must
   leave the reader with an accurate mental model — no "self-improving AI"
   hype.

CONVENTIONS (from DevDojo CLAUDE.md — non-negotiable):
- Curriculum is ground truth; the LLM narrates it. Every factual claim about
  Nate's projects must come from a file you actually read — teach the
  pattern, cite the file path.
- Each lesson: self-contained, ~1 screen, ends with a "## Try it" exercise
  against a real repo (a file to open, a command to run) followed by a
  "## Quiz" section with 2-3 questions answerable from the lesson text.
  Match the voice and structure of curriculum/cc-104.md.
- Filename = lesson id (curriculum/agent-101.md).
- Lessons may TEACH cloud tools (Claude Agent SDK, Anthropic API) but the
  DevDojo app itself stays Ollama-local — no cloud calls, no API keys.

PHI / DATA GUARDRAILS:
- Mine code and docs ONLY. Never read data directories: oska_platform
  bronze_sensitive/raw_inputs/crosswalk, po_intake data, and OpsForge's
  runtime\ directory (live .db files, logs, opsforge_memory.json — real
  experiment data). Never quote runtime or sheet contents into a lesson.
- No secrets, keys, or .env contents in any lesson.

DONE-CHECK (run after the last lesson):
- `python -m pytest` passes (tests validate every index entry's track and
  that available lessons' files exist).
- `python app.py` → http://localhost:5057 shows the new "Agents" track with
  9 lessons, and the page renders with Ollama stopped.
- All 9 index.yaml entries are status: available; one commit per lesson plus
  one for step 0.
