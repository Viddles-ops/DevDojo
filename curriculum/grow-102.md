# Type hints + ruff: cheap correctness

Tests catch bugs by running code; hints and linters catch a whole class of
bugs **without running anything**. You already half-do this — the gap is
making it systematic.

## Type hints: contracts you can read

Your best-hinted project is DeployGuard. A real signature from
`deployguard/checks.py`:

```python
def pre_deploy_check(project: Project) -> list[tuple[str, str]]:
```

Without reading the body you know what goes in and exactly what comes out
(a list of `(severity, message)` pairs, presumably) — and your editor knows
too, so it flags `check_result.split()` as nonsense *while you type it*.
Compare the actual state of po_intake's utility modules: `sheets_utils.py`
has 31 functions, 20 with return hints; `drive_utils.py` 8 and 5. The
unhinted third is where a caller has to open the body to learn whether it
returns a list, a dict, or None — exactly the reading tax hints exist to
remove.

The pragmatic rules:
- Hint **signatures** (params + return). Local variables rarely need it.
- New code gets hints always; old code gets them when touched (additive
  over invasive — same doctrine as everything else here).
- `X | None` is the honest signature for "may not find it" — it forces
  callers to handle the miss. DevDojo's `get_lesson(lesson_id: str) ->
  Lesson | None` makes the redirect-on-missing pattern in app.py obvious.

## ruff: the linter that costs nothing

ruff is one Rust binary that replaces flake8 + isort + most of pylint, fast
enough to run on every save:

```powershell
.\.venv\Scripts\pip.exe install ruff
.\.venv\Scripts\ruff.exe check .        # lint
.\.venv\Scripts\ruff.exe check . --fix  # auto-fix the safe ones
```

It catches unused imports/variables, undefined names (the classic
crash-at-runtime typo), comparison mistakes, and dead code. Start with the
defaults — zero config — and only add a `[tool.ruff]` section to
`pyproject.toml` when a rule genuinely fights the codebase. The discipline
that matters: **a clean `ruff check` before every commit**, same
reflex as pytest.

## Where they meet

Hints make ruff (and later, a real type checker like mypy or pyright)
smarter. The adoption path for this workspace, cheapest first: (1) ruff
defaults on every project — minutes each; (2) hints on all *new* function
signatures — free at write time; (3) a type checker on the two projects
where wrong shapes cost real money — the pipelines (OSKA, PO Intake).

## Try it

Run ruff against this repo: `.\.venv\Scripts\pip.exe install ruff` then
`.\.venv\Scripts\ruff.exe check .` — is DevDojo clean? Then open
`deployguard/checks.py` and `po_intake_automation/drive_utils.py` side by
side and find one unhinted function whose return type you had to read the
body to learn.

## Quiz

1. What does `-> list[tuple[str, str]]` buy a caller that a docstring
   saying the same thing doesn't?
2. Why is `Lesson | None` a *better* return type than raising an exception
   for "lesson not found" in DevDojo's loader?
3. What's the cheapest-first adoption order proposed for this workspace,
   and why do the pipelines get the type checker first?
