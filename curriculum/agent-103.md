# The framework landscape: Claude Agent SDK, LangGraph, or plain Python

*Survey current as of mid-2026. Frameworks move fast — treat specific
version claims as expiring, and the reasoning below as durable.*

Three broad options when you build an agent, and the honest answer is that
you already shipped one using the third.

## 1. A vendor agent SDK (e.g. the Claude Agent SDK)

The SDK route hands you the loop. It manages the conversation turn cycle,
tool declaration and dispatch, context assembly, and usually retries and
streaming. Claude Code itself is built on this model — when you use a
subagent or a tool here, that machinery is doing the work.

**Buys you:** the fastest path from zero to a working tool-using agent, and
someone else maintaining the fiddly parts (tool schemas, token accounting,
context compaction).
**Costs you:** your loop is their loop. Coupling to one vendor's shape, and
when you need behavior the SDK didn't anticipate, you're working against it.

## 2. An orchestration framework (LangChain / LangGraph and relatives)

These model an agent as a **graph**: nodes are steps, edges are transitions,
and a state object flows through. LangGraph in particular exists because
real agents aren't a straight line — they branch, loop, and need checkpoints.

**Buys you:** explicit control flow for genuinely complex topologies,
plus a large integration ecosystem.
**Costs you:** a substantial abstraction to learn, indirection when
debugging, and dependency surface. The framework's mental model becomes
something every future reader must know.

## 3. Plain Python

Write the loop yourself. This is the road OpsForge took, and the evidence is
worth sitting with. Open `OpsForge\pyproject.toml`:

```toml
dependencies = [
    "pydantic>=2,<3",
]
```

**One runtime dependency.** No agent framework, no LangChain, not even an
HTTP library — and yet OpsForge runs four LLM providers, a divergence
protocol, a safety gate, a Monte Carlo forecaster, and 100+ tests. Its
`CLAUDE.md` states the governing rule plainly: "No Kubernetes, microservices,
vector DBs, or distributed systems — **complexity must be earned**."

## What replaces the framework

Not much, it turns out — mostly one well-placed interface. `opsforge\llm\
provider.py` defines an abstract base class with three methods (`extract`,
`compose`, `usage`) and a defaulted fourth (`reason`). Its docstring names
the rule: "Core imports this module only — **never a vendor SDK**." Behind
that seam sit a mock, Ollama, Anthropic, and an OpenAI-compatible provider.

Then look at `opsforge\llm\routing.py` for what the seam makes cheap.
`RoutingProvider` *is* an `LLMProvider` that wraps two others and implements
a cost ladder: normal → primary API; soft limit → routine extraction goes
local; hard limit → everything local; local down → stop. The class docstring
delivers the punchline: "Core components hold 'an LLMProvider' and **never
learn any of this exists**."

That is the whole trick. Provider independence, cost control, and graceful
degradation came from one abstract class and one delegating class — roughly
120 lines, no framework required.

## Choosing

Ask what you actually need:

- **Prototyping, or a standard tool-using assistant?** Use the vendor SDK.
  Rewriting its loop is not where your value is.
- **A genuinely complex branching workflow with checkpointing, built by a
  team that already knows the framework?** A graph framework earns its keep.
- **A long-lived agent with unusual rules, where behavior must be testable
  and dependencies must stay boring?** Plain Python. OpsForge's decision core
  is a pure function precisely because nothing was in the way of making it
  one.

The failure mode isn't picking wrong — it's picking a framework *first* and
discovering your requirements second.

## Try it

Open `OpsForge\pyproject.toml`, then `opsforge\llm\provider.py` and
`routing.py`. Count the lines that give OpsForge four interchangeable
providers plus a cost ladder. Then pick any project in your workspace that
calls an LLM directly — `pemf_bot_v2` or DevDojo's `tutor\ollama_client.py` —
and ask what it would take to add a second provider behind a seam like that.

## Quiz

1. What is OpsForge's only runtime dependency, and what does that fact
   demonstrate about needing a framework to build a real agent?
2. `RoutingProvider` implements the same interface it wraps. What does that
   let it change about cost and provider selection without the core loop
   knowing anything about it?
3. Give one situation where reaching for a vendor SDK is the right call, and
   one where writing the loop yourself is — and name the rule from OpsForge's
   CLAUDE.md that governs the decision.
