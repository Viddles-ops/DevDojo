# Testing with pytest: your biggest gap

Here's the honest assessment: across seven projects, almost nothing has
automated tests. OSKA lists `pytest` in requirements but the safety comes
from manual verification (`pii_guard.py` is the notable exception — a real
automated check that fails the build). Everything else is "run it and look."

That works until a change breaks something you *didn't* look at. Tests are
how a change to `sheets_utils.py` tells you it broke `qb_export.py` before
your logistics team finds out.

## The 80/20 of pytest

A test is just a function that asserts something:

```python
# tests/test_billing_code.py
from drive_utils import _billing_code_from_po

def test_standard_po():
    assert _billing_code_from_po("546-R62176") == "546"

def test_gemini_ocr_variant():
    assert _billing_code_from_po("546 R62176") == "546"   # space, not hyphen

def test_garbage_returns_none():
    assert _billing_code_from_po("TEST DO NOT PROCESS") is None
```

Run all of them with one command: `python -m pytest`. Green = safe, red =
you just caught a bug before production.

## What to test FIRST in your projects

Not everything — the highest-value targets are **pure functions that encode
business rules**:

1. **PO Intake:** `_billing_code_from_po()` and the false-match sentinels —
   quiet failure = misfiled veteran POs.
2. **OSKA:** `usage_to_days()` range handling ("3-4" → 4) and `canon_areas()`
   normalization — these were tuned from human curation; a regression would
   silently corrupt outcomes.
3. **DeployGuard:** the reinvention thresholds in `checks.py`.

Skip (for now): anything needing live Google APIs or Ollama. Testing those
means mocking, which is lesson-after-next territory.

## The habit

When Claude Code fixes a bug for you, say: *"add a pytest test that would
have caught this."* Bugs make the best test cases — each one is a regression
that can never come back.

## Try it

DevDojo itself ships with `tests/test_curriculum.py`. Run `python -m pytest`
in the DevDojo folder and watch it pass. Then break `index.yaml` on purpose
(delete a title), run it again, and see how the failure points you to the
problem.

## Quiz

1. Which single automated check in your projects already "fails the build," and why is that valuable?
2. What kind of function makes the best first test target?
3. What should you ask Claude Code for every time it fixes a bug?
