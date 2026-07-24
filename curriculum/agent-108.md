# Shipping an agent: guardrails, logging, and the human in the loop

A prototype agent and a deployed agent differ less in capability than in
what happens when they're wrong. A prototype misbehaves and you laugh. A
deployed one misbehaves at 3am, into a live channel, 400 times. Shipping is
mostly safety engineering.

## One chokepoint, no exceptions

Open `opsforge\safety\gate.py`. The first line of the docstring sets the
rule: "the last check before the wire. Every outbound message passes through
here, **no exceptions**." Recall from agent-101 that the gate is the only
path to the wire — every other branch falls through to silence.

`check()` applies six suppressions in order — `killswitch`, `budget`,
`cooldown`, `duplicate`, `consecutive`, `two_agent` — and returns a
`GateResult` naming which one fired. That naming matters: "we stayed quiet"
is useless in an incident; "suppressed_by=budget" is diagnosable.

Two details are worth more than the list:

**Budgets are derived, never cached.** Every check runs `COUNT(*)` over
outbound messages in the DB, because "a crash cannot desync the safety layer
from reality." Cached counters and crashes are how agents wake up believing
they have quota they already spent.

**The gate re-checks at send time.** The decision to speak already happened
upstream — so why check again? Because "composition takes time, budgets may
have moved." That's a time-of-check/time-of-use guard. In an agent, the gap
between deciding to act and acting can be several seconds of model latency,
and the world moves during it. **Check at the moment of action, not the
moment of intent.**

## The stop button belongs to the human

The killswitch is the sharpest human-in-the-loop design in your workspace.
It **latches**: once STOP is seen, the halt persists *past removal of the
STOP file*. Deleting the file does not resume the agent — only an explicit
`opsforge resume` does, recorded as a `killswitch_resume` event.

The asymmetry is the point. **The agent can stop itself; only a human can
start it again.** Any recovery an agent can perform on its own is not a
safety mechanism — it's a pause.

And note what the stop does *not* halt: ingestion keeps working, so the
agent keeps reading and recording while silent — "eyes on, mouth shut." A
stopped agent that also stops perceiving wakes up blind.

DeployGuard shows the same instinct in a different shape (agent-102): its
irreversible operation auto-commits current state to a `rescue/<timestamp>`
tag *before* restoring, so even an unauthorized rollback is reversible. Put
a human at irreversible steps — and where you can't, make the step
reversible.

## Log the silence too

`opsforge\logging\events.py` is 20 lines: append-only JSONL, one file per
day, every record carrying `at`, `kind`, and a `correlation` id that ties
every event from one message together.

What's logged is the interesting part. OpsForge's CLAUDE.md commits to JSON
logging for "every message in/out, state change, and intervention decision
(**including decisions to stay silent**)." An agent that logs only its
actions is unauditable, because most of what it did was *decline* to act.
When someone asks "why didn't it flag that contradiction?", the answer lives
in the suppression record.

One constraint travels with the log: "**No secrets ever pass through here** —
providers log token counts, not payload keys." Logs get copied, pasted into
tickets, and shipped to dashboards. Treat them as public.

## Where it runs

Placement is a safety decision too. Your HIPAA-constrained work forces it:
OSKA and PO Intake data must stay on **Ollama-local** models, never routed
to cloud providers. The operator's own routing rules encode it — delegating
*code* work is fine, delegating *data content* is not. Decide what may leave
the machine before you decide where the agent runs.

## Try it

Open `gate.py` and list the six suppression reasons in order — then ask what
you'd learn from a log full of `suppressed_by=duplicate` versus one full of
`suppressed_by=budget`. Find `engage_halt("killswitch")` and trace why
deleting the STOP file doesn't resume. Then open a JSONL file under
OpsForge's `runtime\` logs *directory listing* only (not the contents — that's
live experiment data) and note the daily-file naming.

## Quiz

1. Why are the gate's budgets derived by counting the database on every
   check instead of kept in a counter?
2. The gate re-checks conditions at send time even though the decision was
   already made. What class of bug does that prevent, and why is the gap
   between decision and action especially wide in an agent?
3. The killswitch latches. State the asymmetry that creates, and why an
   agent that can resume itself doesn't really have a stop button.
4. Why must an agent log its decisions to stay silent, and what must never
   appear in those logs?
