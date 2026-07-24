# Do agents learn? Evals, feedback loops, and honest mental models

The most common wrong belief about agents: *"it'll get better as it goes."*

It won't. Not on its own. Getting this right is the difference between an
agent that genuinely improves and one you keep expecting to.

## What actually happens at runtime

A deployed model's weights are **frozen**. Every call runs the same
arithmetic over the same numbers. The model that answers you tomorrow is
byte-identical to the one that answered today, no matter how many
corrections you gave it in between. Nothing about normal operation changes
the model.

So when an agent appears to learn, exactly one of these happened:

- **Its context got better** — memory, retrieval, or a summary put better
  information in the prompt (agent-105/106).
- **Its instructions got better** — a human edited the prompt, doctrine, or
  rules.
- **Its code or tools got better** — a human changed what it can do.
- **Its weights actually changed** — a separate, offline fine-tuning job that
  someone deliberately ran.

The first three are the ones you'll use. The agent didn't get smarter; the
system around it did. That reframe is the whole lesson: **improvement is an
engineering loop with a human in it, not an autonomous property.**

Memory is the sharpest illusion. An agent that recalls your preference feels
like it learned. It didn't — it retrieved. Useful, but the model is
unchanged, and the moment retrieval fails, the "learning" vanishes.

## You cannot improve what you don't measure

Which means evals come first. OpsForge's `verify\engine.py` holds what it
calls VERIFICATION authority — `done -> verified` "happens here or nowhere."
Three properties make it an eval system rather than a vibe:

- **Mechanical evaluation** — verdicts derive from recorded state, not from
  asking a model whether it did well.
- **Honest `unverifiable`** — when the record can't answer, it says so.
  A grader that must produce pass/fail invents one.
- **No silent upgrades** — LLM-assisted verification is "a documented later
  step, never a silent upgrade." How you grade cannot drift quietly, or your
  metrics stop being comparable over time.

`opsforge\analysis\forecast.py` goes further: each MUST criterion's observed
pass/fail record becomes a Beta posterior — `Beta(passes+1, fails+1)`, so no
runs means a genuine coin flip — and a seeded Monte Carlo estimates the
probability of a clean closeout. "Every number is a deterministic function of
(state, seed)," no LLM involved. Note what that buys: the *measurement* of an
unpredictable system is itself fully reproducible.

## The feedback loop that actually works

OpsForge's M5 rehearsal is the real worked example. A persona simulator
drove thousands of synthetic messages through the agent; the run surfaced
concrete findings — contradiction rows not deduped, extraction-hygiene
problems; a tuning pass fixed six of them; a re-run confirmed a clean board.

That's the loop, and none of it is autonomous:

1. **Exercise** the agent against realistic input (simulate; don't wait for
   production to teach you).
2. **Measure** with mechanical checks that can fail.
3. **Diagnose** specific findings, not "it feels off."
4. **Change one layer** — prompt, memory, tool, or code.
5. **Re-run** the same eval and compare.

Step 5 is what makes it engineering. Without a repeatable eval you aren't
improving an agent, you're redecorating it.

## The decision tree: which layer do you change?

When an agent is wrong, diagnose *what kind* of wrong before reaching for a
fix:

| Symptom | Fix | Why |
|---|---|---|
| Wrong tone, format, or ignores a rule | **Prompt / doctrine** | Cheapest, instant, reversible. Try first. |
| Doesn't know facts from a large corpus | **RAG** | Facts belong in retrievable data, not weights. |
| Doesn't know facts about *this* user/project | **Memory write** | One home per fact (agent-106). |
| Logic is wrong or unsafe | **Code** | Deterministic problems deserve deterministic fixes. |
| Output *shape* is consistently wrong across hundreds of examples, and prompting has plateaued | **Fine-tuning** | Last resort. |

Be skeptical of the last row. Fine-tuning changes weights, but it teaches
*form* far better than *facts*; it needs a curated dataset; and it must be
redone whenever the base model or your requirements move. For nearly
everything you'd build, better context beats new weights — and it's
debuggable.

There's a reason OpsForge lands so often in the "code" row: its decision core
is a pure function (agent-101). Improving it means editing an ordered
rulebook and running tests. **The more of your agent is code, the more its
improvement is engineering rather than hope.**

## The honest summary

Agents don't learn from use. Systems around agents improve when humans
measure, diagnose, and change one layer at a time. Anyone promising a
self-improving agent is describing a research problem, not a feature — and
you should ask them what their eval suite looks like.

## Try it

Open `opsforge\verify\engine.py` and find the sentence granting it sole
authority over `done -> verified`. Then open `analysis\forecast.py` and read
the `beta` property — explain why zero recorded runs yields a coin flip
rather than optimism. Finally, take DevDojo itself: your quiz scores in
`data\progress.json` are an eval signal. If they show a lesson is
consistently misunderstood, which row of the decision tree applies — and why
is it *never* the fine-tuning row?

## Quiz

1. A user corrects an agent ten times in one session and it improves. The
   next day it makes the same mistake. Explain exactly what did and did not
   change.
2. Name the four things that can change when an agent "gets better," and say
   which one does *not* happen during normal operation.
3. Why does OpsForge's verification engine need an honest `unverifiable`
   verdict, and what goes wrong with a grader forced to output pass/fail?
4. Walk the decision tree for: (a) the agent's summaries are too long, (b) it
   doesn't know your VA contract terms, (c) it double-posts to a channel.
5. Why is "the more of your agent is code, the more improvement is
   engineering" true — and what does OpsForge's decision core demonstrate?
