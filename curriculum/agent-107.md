# Orchestration: one agent driving others

Once one agent works, the temptation is to build a team. Two topologies are
available, and you happen to run one of each — which makes the choice
unusually easy to see.

- **Orchestrator** — one agent decomposes work and drives subordinates.
  Hierarchical. The chief-operator.
- **Peer** — agents coordinate as equals; none commands. OpsForge.

The deciding factor is not sophistication. It's **authority**.

## The orchestrator: chief-operator

Read `C:\Users\natee\.claude\agents\chief-operator.md`. It holds real
authority over your repos — you gave it that — so it delegates. Five rules
carry the design:

**1. Fresh context executes the plan.** The pipeline lane goes plan artifact
→ plan gate → fresh executor → diff gate, and the planner does not execute
its own plan: "fresh context executes from the written plan." A planner
grading its own work shares its blind spots.

**2. The plan gate is adversarial.** Before code, a fresh-context agent that
did *not* write the plan critiques it. Review is only worth something when
the reviewer can actually disagree.

**3. Route by task shape.** Its routing table is explicit — cheap read-only
model for file sweeps and inventory, mid-tier for well-specified microtasks,
top-tier for ambiguous refactors and debugging. Matching model to task is
most of cost control in a multi-agent system.

**4. Don't delegate judgment.** The same table sends architecture decisions,
decomposition, risk calls, and HIPAA-adjacent design to **"do it
yourself"** — "judgment is your job — don't delegate decisions." An
orchestrator that delegates deciding isn't orchestrating.

**5. Isolate writers.** "Never send more than one subagent into the same
files concurrently." Two agents editing one file is a lost-update race with
no merge tool.

And the constraint that makes it all work: "Every delegated prompt must be
self-contained: project path, the relevant ADR/convention, the deliverable,
and the done-check. **Subagents start cold.**" A subagent inherits none of
your conversation. Anything you don't write down doesn't exist. Finally,
nothing is called done on a subagent's word alone — the diff gate reads the
actual diff and runs the tests.

## The peer: OpsForge

OpsForge coordinates four independently-built agents in the InterAgentLab
experiment, and its very first locked decision (ADR-001) defines it as a
"coordination peer + closeout owner + disciplined divergence — **not an
orchestrator**."

Because it has no authority, its architecture rule is **"recommend, never
assign"**: no unilateral task assignment; it records acceptance or refusal
(PRD NG2). It publishes structure — shared task state, decision log, risk
register — and lets peers choose. It cannot command, so it doesn't pretend
to.

Two mechanisms make that stance work in practice. **Silence is a first-class
output**: every outbound message must clear an intervention bar, and the
default engine action is update-state-silently (agent-101). And its influence
is exercised through *structure* rather than instruction — a published board
everyone can see, plus one budgeted, evidence-tagged probe per conflict
episode.

## Choosing

Ask who owns the work:

- **You own the workers** (subagents you spawn, in repos you control) →
  orchestrator. Decompose, delegate, gate.
- **You don't** (peers built by others, humans, external teams) → peer.
  Publish structure, recommend, record.

The failure mode is a peer-shaped situation with orchestrator-shaped code: an
agent issuing assignments to parties who never agreed to receive them. It
produces noise, gets ignored, and burns the trust that would have made
recommendations land.

## Try it

Open `chief-operator.md` and find the model-routing table. Pick a task you
did this week and route it — then check the row that says do it yourself, and
ask whether you'd have delegated it. Then open OpsForge's `CLAUDE.md`,
find "Recommend, never assign," and consider: what would break in the
experiment if OpsForge started assigning tasks to the other three agents?

## Quiz

1. What single factor decides between orchestrator and peer topology, and
   which does each of your two agents use?
2. Why does the operator require that a *fresh* agent execute a plan, and a
   *different* fresh agent critique it before execution?
3. "Subagents start cold." What must every delegated prompt therefore
   contain, and what happens to context you didn't write down?
4. OpsForge has no authority over its peers. Name the two mechanisms it uses
   to influence outcomes anyway.
