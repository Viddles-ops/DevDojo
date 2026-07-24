# Agent memory II: persistent state, files vs DB, retrieval

Context-window memory (agent-105) dies when the process does. Persistent
memory is what's still true tomorrow. The question isn't *whether* to store
state — it's **what shape**, and **who reads it when**. Your workspace has
four answers running side by side.

## Shape 1: a database — structured, transactional, queryable

OpsForge's source of truth is one private SQLite file (ADR-003 locally,
ADR-026 in the operator store). Use a DB when state has *relationships* and
*invariants*: tasks own decisions, findings gate verification, and a
half-written update would corrupt meaning. Recall from agent-101 that every
loop pass runs inside one transaction — that guarantee is only available
because the store is a real database.

Its companion rule is as important as the choice: **private store, published
snapshots**. The DB is OpsForge's alone; what others see is rendered markdown
(`opsforge\publish\`). No shared writable store, so no other agent can
corrupt its state, and humans still get something readable.

## Shape 2: a plain file — legible, diffable, human-editable

Open `opsforge\memory\ledger.py`. It's the operator-side session ledger, and
it is deliberately *not* in the database:

> One small JSON file, appended at run-end.

`record_session()` appends one record per run — messages processed, silence
rate, probes fired, tasks verified. `summary()` renders a lifetime view. No
schema migration, no transaction, no ceremony, because none is needed for an
append-only log nobody else writes.

## The scoping rule — the most important idea here

Read that docstring's first paragraph again:

> DELIBERATELY separate from any experiment/run DB and **NEVER injected into
> the boardroom context mid-run**: this is the operator's lab notebook ABOUT
> OpsForge, not part of any team's state.

Persistent memory is not automatically prompt material. This memory exists,
is written every run, and is *deliberately never shown to the model during a
run* — because injecting "you have run 14 times and stayed silent 98% of the
time" would contaminate the experiment it's measuring.

So every store needs two decisions, not one: **what goes in**, and **who
reads it when**. Agents that dump all persistent memory into context are
answering only the first.

## Shape 3: markdown — memory the human and the model share

The chief-operator's memory is a folder of markdown: `_operator\HANDOFF.md`
(what happened, what's next), `BACKLOG.md` (microtasks with done-checks),
`DECISIONS.md` (ADRs). Your Claude Code memory directory works the same way —
one fact per file, plus a `MEMORY.md` index loaded each session.

The governing discipline is **one home per fact**. Handoffs *point to* facts
rather than duplicating them, so nothing can disagree with itself. That
matters more for markdown than for a DB: a database has constraints, while a
folder of prose has only your discipline.

Markdown wins when a human must read and edit the same memory the agent
uses. It loses when you need queries, integrity, or scale.

## Shape 4: retrieval — memory too big to load

When the corpus dwarfs the window, store everything and fetch only what's
relevant per query. That's RAG, and `pemf_bot_v2` is your worked example —
chunking, embeddings, MMR retrieval (covered in stack-105).

Worth noting the contrast: OpsForge's context assembly deliberately uses
**no embeddings** — "deterministic, query-based, explainable." When your
state is a few hundred structured rows, SQL beats vector search on
predictability and debuggability. Retrieval earns its complexity at corpus
scale, not before.

## Choosing

| Need | Reach for |
|---|---|
| Relationships, invariants, transactions | Database |
| Append-only log, no schema, tiny | JSON/JSONL file |
| Human reads and edits it too | Markdown, one home per fact |
| Corpus far exceeds the window | Retrieval (RAG) |

Then ask the scoping question separately: does this get injected into
context, and *when*?

## Try it

Open `opsforge\memory\ledger.py` and find every reason it isn't a database
table — then find the sentence forbidding it from entering the boardroom
context. Now look at your own `MEMORY.md` index and pick one entry: which
shape is it, who reads it, and would it be better as a row in a table? Ask
the same of `_operator\DECISIONS.md`.

## Quiz

1. Give the two decisions every persistent store requires, and explain why
   OpsForge's session ledger answers the second one with "never, mid-run."
2. What does "private store, published snapshots" (ADR-026) protect against,
   and what do other participants actually read?
3. Why is "one home per fact" a stricter requirement for markdown memory
   than for a database?
4. OpsForge's context assembly uses no embeddings while `pemf_bot_v2` does.
   What makes each the right call for its situation?
