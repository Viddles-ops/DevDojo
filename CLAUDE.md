# CLAUDE.md — DevDojo

Local coding tutor for Nate. Flask + local Ollama, port **5057**. Teaches the
tools/skills/approaches used across the Viddles-ops projects plus new
practices worth learning. No cloud deployment — local only, like oska_app.

## Architecture rules

1. **Curriculum is ground truth; the LLM narrates it.** Same philosophy as
   OSKA's compute-then-narrate (ADR-012): lessons in `curriculum/*.md` are
   curated content; `/ask` grounds every answer in the selected lesson text.
   If the model goes beyond the lesson, the answer must say so explicitly
   ("beyond the lesson: ..."). Never let the tutor invent facts about Nate's
   projects — mine them into a lesson first.
2. **Local AI only** (ADR-011): Ollama at `http://localhost:11434`, default
   `qwen2.5:7b-instruct`. No cloud LLM calls, no API keys anywhere.
3. **Curriculum mining reads code + docs ONLY.** When mining lessons from
   oska_platform or po_intake_automation, never read their data directories
   (`bronze_sensitive/`, `raw_inputs/`, `crosswalk/`, etc.) and never quote
   sheet contents — PHI. Lessons teach the *pattern*, cite the *file*.
4. **Modular** (ADR-003): routes in `app.py`; logic in `tutor/` modules with
   narrow interfaces; new features = new modules.

## Module map

| File | Role |
|---|---|
| `run.ps1` | One-command launch: `.\run.ps1`. Thin wrapper over the launcher. |
| `tutor/launcher.py` | Bootstrap + launch, **stdlib only** — creates/refreshes `.venv`, then runs app.py with the venv python. Must never import third-party packages (it runs before they're installed, possibly under another project's Python). |
| `app.py` | Flask routes + inline templates. No business logic. |
| `config.py` | Ports, paths, Ollama settings. No secrets (none needed). |
| `tutor/curriculum.py` | Loads `curriculum/index.yaml`, reads lesson markdown. |
| `tutor/ollama_client.py` | `ask(question, grounding)` → Ollama /api/generate. |
| `tutor/progress.py` | Lesson completion → `data/progress.json` (gitignored). |
| `curriculum/index.yaml` | Catalog: id, title, track, status, source projects. |
| `curriculum/<id>.md` | One lesson per file. Filename = lesson id. |

## Curriculum model

Three tracks:
- **stack** — how Nate's projects actually work (mined per project)
- **claude-code** — Claude Code itself: agents, skills, CLAUDE.md, handoffs
- **grow** — practices not yet adopted: pytest, typing, ruff, CI, logging

Lesson `status` in index.yaml: `available` (file exists) | `planned` (backlog
item exists — write the lesson by mining the named source project). Adding a
lesson = write `curriculum/<id>.md` + set status available. Keep lessons
self-contained, ~1 screen, ending with a **Try it** exercise against a real
repo and 2–3 quiz questions under `## Quiz`.

## Testing

`python -m pytest` (tests/ — start with curriculum loader round-trip).
Smoke test: `python app.py` then open http://localhost:5057 — lesson list
must render with Ollama stopped (Ask degrades gracefully, browsing works).
