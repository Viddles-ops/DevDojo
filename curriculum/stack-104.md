# Local LLMs with Ollama: three patterns from your own apps

Every AI app in this workspace talks to the same local endpoint — Ollama at
`http://localhost:11434` — but three projects use it three different ways.
The pattern choice follows one question: **what is the LLM allowed to be
wrong about?**

## Pattern 1 — Compute-then-narrate (OSKA: `oska_app.py` + `oska_metrics.py`)

The LLM is *never allowed to produce a number*. Every governed metric is
computed in Python (`oska_metrics.py` is the single source of truth); the
model only routes the question to a metric and narrates the already-computed
figures. Charts are fixed computations, not LLM output. Decision ADR-012.
Use this when answers must be defensible: a hallucinated stat about health
outcomes isn't a bug, it's a liability. (Bonus: PHI never leaves the machine
— local-only inference is the OSKA rule, ADR-011.)

## Pattern 2 — Grounded Q&A (DevDojo: `tutor/ollama_client.py`)

The LLM may explain, but only *from supplied text*. The interface is one
function: `ask(question, grounding)` — the selected lesson's markdown is
passed as grounding, and anything beyond it must be labeled ("beyond the
lesson: ..."). Curriculum files are ground truth; the model narrates them.
Use this when you have curated content and want conversational access to it
without letting the model freelance.

## Pattern 3 — Backend switching, local-first (jAIme: `config.py`; VetterGoat: `ask.py`)

Non-sensitive apps keep the *backend* pluggable but default local:

```python
LLM_BACKEND = os.getenv("LLM_BACKEND", "ollama")   # ollama | openai | vertexai  (jAIme)
BACKEND = os.getenv("VETTERGOAT_LLM_BACKEND", "ollama").lower()  # ollama | claude | gemini
```

One env var flips providers; code paths stay identical. VetterGoat adds the
sharpest refinement — an **escalation pipeline** where the LLM is the
*fallback, not the first resort*: cache hit (<15ms) → regex intent router
(<100ms, answers ~80% of questions with zero LLM) → local Ollama (1–4s) →
optional cloud. The cheapest thing that can answer correctly, answers.

## The common floor

All three read `OLLAMA_URL`/`OLLAMA_MODEL` from env with local defaults —
no keys, nothing to leak (see stack-103). Model choice is a hardware fit:
`qwen2.5:7b-instruct` is the largest model that runs fully inside the RTX
4070's 8 GB VRAM, which is why OSKA, DevDojo, and jAIme all default to it.

## Try it

Run `ollama list` (or `curl http://localhost:11434/api/tags`) and match the
installed models against each project's default. Then open
`tutor/ollama_client.py` in this repo and find where the grounding text is
injected into the prompt — that one spot is the whole Pattern-2 guarantee.

## Quiz

1. In OSKA, what computes the numbers, what does the LLM do, and why is that
   split non-negotiable for health-outcome answers?
2. VetterGoat answers ~80% of questions without any LLM call. What two
   layers sit in front of Ollama, and what does each cost in latency?
3. Which pattern would you pick for a new app over curated policy documents,
   and what single function signature implements it here?
