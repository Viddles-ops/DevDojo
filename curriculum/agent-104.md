# MCP: the USB port for agent tools

*Protocol landscape current as of mid-2026.*

You have N agents and M systems they might touch — GitHub, Slack, a
database, a browser. Wire them directly and you write N×M integrations, each
one bespoke, each one rewritten when you switch agents. **Model Context
Protocol** exists to turn that multiplication into addition: write one MCP
*server* for a system, and every MCP-speaking agent can use it. Write one
MCP *client* into an agent, and it can use every server anyone has published.

Hence the USB analogy. USB didn't make devices better; it made the connector
standard, so any device works with any host.

## Servers, clients, and what crosses the wire

- An **MCP server** wraps a system and exposes a typed surface: **tools**
  (things to call), **resources** (things to read), and **prompts**
  (reusable templates). It's a separate process.
- An **MCP client** lives inside the agent host — Claude Code is one — and
  connects to servers over stdio or HTTP.
- The agent's model sees the server's tools as ordinary tools (see
  agent-102). The round trip is unchanged; only the *plumbing* is standard.

Two consequences matter more than the schema details. First, **the server is
a process boundary**: tools run in their own address space with their own
credentials, which is a security seam, not just a tidiness one. Second,
**capability becomes configuration** — connecting a new system is a config
entry, not a code change.

You're already using this. Your Claude Code sessions connect MCP servers for
things like browser control and workspace integrations; the ones needing a
login are exactly the ones whose *server* holds the credentials, which is
why authorizing happens outside the agent.

## You built the same instinct by hand

Before reaching for the standard, look at what OpsForge did. Open
`opsforge\transport\channel.py`:

```python
class MessageChannel(ABC):
    @abstractmethod
    def send(self, msg: OutboundMessage) -> None: ...
```

One method. The docstring states the discipline: "core imports this module
only, **never an adapter**." Behind it sit four implementations —
`CollectingChannel` (a test double that records instead of transmitting),
`ConsoleChannel` (prints), `HumanRelayChannel`, and a Discord adapter.

`HumanRelayChannel` is the one to sit with. Its "transport" is *a person*:
it frames a copy-paste block, writes it to `runtime/outbox.log`, and a human
pastes it into the real room. The core loop cannot tell the difference
between that and a socket. When the abstraction is right, even a human is a
valid adapter — and OpsForge got a working live transport with zero
integration work while waiting on a channel spec.

## Where the two differ

Same instinct, different blast radius:

| | `MessageChannel` | MCP |
|---|---|---|
| Scope | Private to OpsForge | Open standard |
| Who can write an adapter | You | Anyone, for any client |
| Cost | ~15 lines | A protocol to learn |
| Reuse | Within one project | Across every MCP host |

The honest read: for *one* outbound direction in *one* project, OpsForge's
hand-built seam was the right call — MCP would have been unearned complexity
by its own CLAUDE.md rule. MCP wins when the integration is one you'd
otherwise rewrite per agent, or when you want someone else's server for free.

The transferable lesson is the one both share: **an agent should never import
its integrations directly.** Put an interface between the core and the
outside world. Whether that interface is a 15-line ABC or an open protocol
is a scope decision, not a philosophical one.

## Try it

Open `opsforge\transport\channel.py` and confirm the core-facing surface is a
single method. Then find where `CoreLoop` actually sends
(`self._channel.send(...)` in `opsforge\core\loop.py`) and note that
`channel` is an optional constructor argument — the loop runs fine with
*no* transport at all. Ask: which of your other projects imports an
integration directly into its core, and what would a seam cost there?

## Quiz

1. What problem does MCP solve, and why is "N×M becomes N+M" the right way
   to describe it?
2. An MCP server runs as a separate process. Name one security benefit and
   one operational benefit of that boundary.
3. `HumanRelayChannel` uses a person as the transport. What does that reveal
   about how well-designed the `MessageChannel` interface is, and what did it
   let OpsForge do while blocked on a channel spec?
4. When is a hand-built seam like `MessageChannel` the better choice than
   adopting MCP, and which OpsForge rule decides it?
