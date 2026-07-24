# What an agent actually is: model + tools + loop + state

Strip away the marketing and an agent is four things wired together:

- **A model** — an LLM that turns text into text. That's all it does.
- **Tools** — functions the model can ask to have run (read a file, query a
  DB, send a message). The model never *does* anything; it emits a request
  and your code executes it.
- **A loop** — something that runs repeatedly: take input, decide, act,
  record, wait for the next input.
- **State** — what survives between passes of the loop.

Remove the loop and you have a chatbot. Remove the state and you have an
agent with amnesia. Remove the tools and you have an agent that can only
talk. You already own two working agents that prove the shape — and they
look nothing alike.

## Anatomy 1: OpsForge — the loop as code

`opsforge\core\loop.py` is a class named `CoreLoop` with one real method,
`process(event)`. Its docstring states the pipeline exactly:

> extract → apply → triggers → decide (pure) → compose (template) →
> SafetyGate → send+archive

Read that as the four parts in order. The **model** appears once, early:
`self._engine.process(msg, uow)` extracts structured facts from the incoming
message. The **state** is SQLite, and every pass runs inside one
transaction — `with self._state.uowf.begin(loop_record_id) as uow:` — so an
event is applied completely or not at all. The **tools** here are the
transport (`self._channel.send(...)`) and the repositories that write state.
And the **loop** is the whole method, run once per inbound message.

Two details worth stealing. First, the loop guards its own entrance: it
refuses to process its own outbound messages (`msg.sender_handle ==
self._self_handle`) and skips any `external_id` it has already handled.
Without those two checks an agent will happily talk to itself forever.
Second — and this is the design that makes OpsForge unusual — **the decision
is not made by the LLM**. `opsforge\core\decision.py` is a pure function:
"no LLM, no I/O, no clock," first-match-wins over an ordered rulebook, and
*silence is the fall-through, not a rule*. The model reads and extracts;
deterministic code decides. That split is why the agent's behavior is
testable.

## Anatomy 2: chief-operator — the loop as prose

Open `C:\Users\natee\.claude\agents\chief-operator.md` and you find the same
four parts with none of the code. Its loop is written in English:
**Orient → Decide → Decompose → Lane → Execute → Gate → Record**. Its state
is a folder of markdown (`_operator\HANDOFF.md`, `BACKLOG.md`,
`DECISIONS.md`). Its tools are declared in YAML frontmatter. Its model is
whatever Claude Code is running.

Same anatomy, different substrate: OpsForge's loop is enforced by the Python
interpreter; the operator's is enforced by an LLM following written
instructions. The tradeoff is exactly what you'd expect — the operator was
far cheaper to build and can handle work nobody anticipated, but it can also
skip a step, and only a human reading the transcript would notice. OpsForge
cannot skip a step, and can only do what was coded.

## The useful mental model

When you design an agent, design the four parts separately and ask of each:
*what happens when this fails?* A dead model, a tool that errors, a loop
that reenters, state that's half-written. OpsForge answers all four
explicitly — degrade to silence, log it, skip duplicates, one transaction
per event. Most agent bugs are one of those four questions left unanswered.

## Try it

Open `opsforge\core\loop.py` and find the three places an event can exit
without the agent ever speaking. Then open `opsforge\core\decision.py` and
read `_RULEBOOK` top to bottom — note that the *order* of that tuple is the
agent's priority system, and that returning `_SILENT` requires no rule at
all. Ask yourself what would change if `decide()` were replaced by a prompt.

## Quiz

1. What are the four parts of an agent, and which one is missing if an agent
   can hold a conversation but forgets everything between runs?
2. In OpsForge, which component makes the decision to speak — the LLM or
   deterministic code? Quote the rule from `decision.py` that makes silence
   the default.
3. `CoreLoop.process()` returns early in two cases before any work happens.
   What are they, and what failure does each prevent?
4. The chief-operator and OpsForge have the same anatomy but different
   substrates. Name one thing the prose loop can do that the coded loop
   can't, and one guarantee the coded loop gives that the prose loop can't.
