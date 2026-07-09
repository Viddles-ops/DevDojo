# DevDojo — Local Coding Tutor

A local web app that teaches you the tools, skills, and practices behind your
own projects — and the ones you should learn next. Runs entirely on this
machine: Flask UI + local Ollama for the tutor voice. No cloud, no API keys.

## What it does

- **Curriculum** mined from the real Viddles-ops projects: how your GCP
  deploys work, how DeployGuard protects you, how the OSKA medallion
  pipeline is built, how Claude Code agents and skills operate — each lesson
  cites the project it came from.
- **Growth track**: practices you haven't adopted yet (testing, typing,
  linting, CI) with concrete first steps against your own repos.
- **Ask the tutor**: questions answered by local Ollama, grounded in the
  lesson content — the model narrates the curriculum, it doesn't freelance.

## Run it

```powershell
cd DevDojo
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
# → http://localhost:5057
```

Requires [Ollama](https://ollama.com) running locally (`qwen2.5:7b-instruct`)
for Ask-the-tutor; lesson browsing works without it.

## Layout

```
app.py                  # Flask routes only
tutor/curriculum.py     # load/index lessons
tutor/ollama_client.py  # local LLM calls
tutor/progress.py       # completion tracking (data/progress.json)
curriculum/index.yaml   # lesson catalog (id, track, status, sources)
curriculum/*.md         # one lesson per file
docs/                   # roadmap + design notes
```

Part of the Viddles-ops workspace — see `PROJECTS.md` at the projects root.
