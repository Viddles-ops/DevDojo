# Your safety net: git, GCM, and DeployGuard

Every project in this workspace is protected by three layers. Understanding
them means you can experiment freely — nothing is ever more than one command
from recoverable.

## Layer 1 — git: the time machine

Every project folder is a git repository. A **commit** is a permanent
snapshot; until you commit, changes exist only in your working files.
The three commands that matter daily:

```powershell
git status          # what's changed since the last snapshot?
git add -A          # stage everything
git commit -m "..." # take the snapshot
```

## Layer 2 — GitHub via Git Credential Manager (no PATs!)

Pushing copies your commits to GitHub (private repos, Viddles-ops org).
Authentication is handled by **Git Credential Manager** — it stores an OAuth
token in Windows Credential Manager, so `git push` just works. You never
paste a Personal Access Token, which also means one can never leak from a
terminal. (The old PAT-prompt script broke precisely because pasting secrets
into terminals is fragile — that failure retired the whole approach,
recorded as decision ADR-020.)

## Layer 3 — DeployGuard: portfolio-wide protection

From `DeployGuard\`, one command watches every project:

```powershell
python -m deployguard status    # who's dirty? who's unpushed?
python -m deployguard backup    # commit + push everything
python -m deployguard check X   # pre-deploy sanity: is this an increment or a rewrite?
python -m deployguard record X  # tag this exact code as "what's deployed"
python -m deployguard restore X # roll back to the last deploy — safely
```

The key design idea: **restores can't lose work.** Before rolling back,
DeployGuard auto-commits anything uncommitted and tags the current state as
`rescue/<timestamp>`. The rollback is itself reversible.

The second idea: the **reinvention check**. Before a deploy it compares the
code against the last deployed tag — if more than half the files changed or a
quarter were deleted, it warns you that this looks like a rewrite, not an
increment. That's a guardrail against a session quietly replacing a working
project.

## Try it

Run `python -m deployguard status` right now. For any repo that isn't
"clean & pushed", figure out *why* before running backup — `git -C <path>
status` shows exactly which files changed.

## Quiz

1. What happens to uncommitted changes when you run `restore`?
2. Why is Git Credential Manager safer than a PAT in a prompt?
3. What two ratios trigger a REINVENTION RISK warning?
