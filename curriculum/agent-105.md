# Agent memory I: the context window and summarization

An LLM remembers nothing. Each call is a fresh start, and the *only* thing
the model knows is what you put in the prompt. "Short-term memory" is
therefore not a feature you enable — it's a budget you manage. The window is
finite, and every token you spend on history is one you can't spend on the
task.

Three moves cover almost everything: **ground** the answer, **assemble** the
context, **compact** it when it overflows.

## Move 1: grounding

Give the model the source material and require it to answer *from* that.
DevDojo does exactly this — `tutor\ollama_client.py` builds:

```
LESSON CONTENT:
{grounding}

STUDENT QUESTION: {question}
```

The lesson text is injected fresh on every ask. The model isn't recalling
the curriculum; it's reading it. That's the architectural rule in DevDojo's
CLAUDE.md — "curriculum is ground truth; the LLM narrates it" — and it's the
cheapest, most reliable memory there is: don't remember, just re-read.

## Move 2: context assembly

When there's more state than fits, something must choose what goes in.
Open `opsforge\memory\context.py`. Its docstring names the philosophy:
"Deterministic, query-based, explainable — **no embeddings**."

`build_extract_context()` assembles a `PromptContext` from four sources:

- `roster` — who's in the room
- `state_slice` — open tasks, open questions, recent decisions, rendered by
  SQL with `LIMIT 20 / 10 / 5`
- `recent_window` — the last `N_VERBATIM = 15` messages, verbatim
- `summary` — the rolling summary (move 3)

Every one is capped: `MAX_SLICE_CHARS = 6000`, `MAX_WINDOW_CHARS = 8000`,
`MAX_SUMMARY_CHARS = 6000`. And when the window overflows, `_recent_window`
keeps the newest and drops oldest-first. That's a *policy*, written down and
testable — not "hope it fits."

Two design choices worth copying. First, the budget is explicit and per-slot,
so no single section can crowd out the others. Second, look at
`PromptContext` in `opsforge\llm\provider.py`: it's `frozen=True`, and the
docstring says "assembled by memory/context.py; **providers only format,
never query**." Deciding *what* the model sees and *how* it's rendered are
different jobs, in different modules. That's why you can swap providers
without changing what the agent remembers.

## Move 3: compaction

Eventually history exceeds any budget. You summarize — and where you do it
matters. Open `opsforge\memory\summary.py`.

The clever part is that summary lines are produced as a **byproduct** of
work already happening: each pass of the loop writes a `summary_line` onto
its `loop_records` row. The docstring is explicit — "cheap, **no extra LLM
call**." Only when unfolded lines exceed `N_FOLD_THRESHOLD = 60` does
`maybe_fold()` spend one call to compress the oldest of them into a standing
summary, keeping `N_KEEP_RECENT = 20` verbatim.

So the memory has two resolutions at once: recent history in full detail, older
history compressed. `current()` returns standing summary + unfolded lines —
exactly what prompts should see.

Then note the failure handling:

```python
except ExtractionFailed:
    return False  # degrade: keep old summary, lines keep accumulating
```

If compression fails, nothing breaks — the old summary stands and it retries
next cycle. "**Memory maintenance never blocks the loop.**" Summarization is
lossy and can fail; treat it as best-effort maintenance, never as a step the
agent depends on to function.

## Try it

Open `opsforge\memory\context.py` and add up the character caps — that's the
agent's entire short-term memory budget in four numbers. Then find the line
in `_recent_window` that decides *which* messages get dropped when the window
is full. Finally, open `summary.py` and trace how many LLM calls a single
loop pass costs for summarization when no fold is due. Compare that to
calling the model to summarize every message.

## Quiz

1. Why is "short-term memory" better described as a budget than a feature,
   and what is the only thing an LLM actually knows on any given call?
2. Name the four slots `build_extract_context()` assembles, and explain what
   the per-slot character caps prevent.
3. `PromptContext` is frozen and providers "only format, never query." What
   separation does that enforce, and what does it let you swap freely?
4. How does OpsForge produce summary lines without spending an extra LLM
   call per message, and what happens when a fold fails?
