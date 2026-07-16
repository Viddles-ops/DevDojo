# GitHub Actions: your first CI pipeline

*(Sourcing note: no project here has CI yet — this lesson is the plan, not
a description of existing code. The worked example is real: DevDojo, the
one repo with a genuine test suite.)*

## What CI buys you

Right now, tests run when someone remembers to run them. CI (continuous
integration) makes GitHub run them **on every push** — a tireless reviewer
that catches "works on my machine" the moment it's pushed, on a clean
machine with no leftover state. You already have every prerequisite: private
repos on GitHub, pinned `requirements.txt` files, and one project — DevDojo
— with a real pytest suite (12 tests, all dependency-light: no Ollama, no
GCP, no data files needed).

## The anatomy (one file does everything)

A workflow is a YAML file at `.github/workflows/<name>.yml` in the repo.
The whole thing for DevDojo would be:

```yaml
name: tests
on: [push, pull_request]

jobs:
  pytest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: python -m pytest -q
```

Read it top to bottom: trigger (`on:`) → a fresh Ubuntu VM → check out the
code → install Python → install pinned deps → run the same command you run
locally. If pytest exits non-zero, the push gets a red ✗ on GitHub and an
email. Note what's *absent*: no secrets, no cloud credentials — the suite
was deliberately built to run anywhere (grounded tests, temp files,
no live Ollama), which is exactly what makes it CI-able for free.

## Why DevDojo first, and what doesn't fit

DevDojo is the pilot because its suite is hermetic. The others need thought
before CI makes sense: OSKA and po_intake tests would touch PHI-adjacent
data or GCP credentials — those need *fixtures* (synthetic data checked
into the repo) before a cloud runner should ever run them. The general
rule: **CI runs your hermetic tests; tests that need secrets or real data
stay local** until you've built safe substitutes. One more Windows-user
note: the runner is Linux, so path-separator and CRLF assumptions get
flushed out — a feature, not a nuisance.

## The adoption path

1. DevDojo: add the workflow above (a future microtask — it's deliberately
   *not* added by this lesson).
2. DeployGuard: same shape once it grows a test suite (grow-101's advice).
3. Branch protection: once green is normal, require the check to pass
   before merging to main.

## Try it

Without creating anything: run DevDojo's suite the way CI would —
fresh terminal, `.\.venv\Scripts\python.exe -m pytest -q` — and confirm it
needs nothing external. Then answer: which single test in `tests/` would
break if the runner had no network, and why is the answer "none"?

## Quiz

1. Where does a workflow file live, and what event in the YAML above
   triggers it?
2. Why is DevDojo's suite CI-ready while OSKA's tests wouldn't be, and
   what has to exist before a pipeline project gets CI?
3. What does `runs-on: ubuntu-latest` flush out for a Windows-developed
   codebase?
