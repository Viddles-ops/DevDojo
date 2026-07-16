# Dependency hygiene: venvs, pinning, and uv

This lesson exists because the trap it teaches actually fired, in this repo.
You activated another project's environment, typed `python app.py` here, and
got `No module named flask` — because "python" is not one thing on your
machine. It's whichever interpreter is first on PATH, carrying *that
project's* installed packages.

## Why every project gets its own .venv

A virtual environment is a private copy of Python plus a private
`site-packages`. The workspace convention: every project has a `.venv/` in
its root, always gitignored. That means jAIme's heavy RAG stack, OSKA's
pandas/matplotlib, and DevDojo's small Flask setup can never collide — and
uninstalling in one can never break another. The rule that follows:

**Run project code with the project's interpreter, not with bare `python`.**

```powershell
.\.venv\Scripts\python.exe -m pytest     # always right
python -m pytest                          # whatever PATH says — roulette
```

## Pinning: requirements.txt is the contract

`pip freeze` captures exact versions; `requirements.txt` is what makes the
venv *reproducible* — delete `.venv/` and you can rebuild it identically.
A venv without a requirements file is a pet; with one, it's cattle.

## The fix that shipped here: a venv-proof launcher

DevDojo's `run.ps1` + `tutor/launcher.py` make the trap impossible. The
launcher is **stdlib-only** (it must run before anything is installed, under
*any* Python — even the wrong project's): it creates `.venv` if missing with
`sys.executable -m venv`, pip-installs `requirements.txt` into it, then
re-launches the app **with the venv's own python.exe**. Whatever broken
environment invokes it, the app always runs in the right one. That's the
generalizable pattern: don't document the footgun, write ~30 lines that
remove it.

## uv: the modern shortcut

`uv` is a Rust-based replacement for pip + venv: `uv venv` and
`uv pip install -r requirements.txt` are drop-in and 10–100x faster, and
`uv run script.py` resolves the project environment automatically — the
launcher pattern as a built-in. Worth adopting per-project as you touch
them; nothing about the .venv convention changes.

## Try it

Run `python -c "import sys; print(sys.executable)"` in this repo's folder
right now — which Python answered? Then run
`.\.venv\Scripts\python.exe -c "import sys; print(sys.executable)"` and
compare. If the first one surprised you, you're living the trap. Finally,
read `tutor/launcher.py` and find the line that guarantees the app never
runs on the wrong interpreter.

## Quiz

1. Bare `python app.py` failed in this repo with `No module named flask`
   even though Flask was installed here. What actually happened?
2. Why must `tutor/launcher.py` import only the standard library?
3. What makes a venv reproducible rather than a one-off, and which file
   provides it?
