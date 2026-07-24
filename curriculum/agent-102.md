# Tool use: how an LLM does things

A language model cannot read your disk, call an API, or push to GitHub. It
can only produce text. Tool use is the protocol that turns that limitation
into a capability: you describe some functions to the model, and it replies
with a *request* to run one.

## The round trip

Every tool call is four steps, and the model only participates in two:

1. **You declare the tools.** Each gets a name, a description, and a
   parameter schema (usually JSON Schema). This declaration goes into the
   model's context — the description *is* the documentation the model reads.
2. **The model emits a call.** Not a result — a request: "run `read_file`
   with `{path: 'config.py'}`." It has executed nothing.
3. **Your code executes it.** This is where the actual power lives, and
   where every safety check belongs. The model asked; you decide.
4. **You return the result** as a message, and the loop continues with that
   result now in context.

The critical property: **step 3 is yours.** The model's "permission" to do
something is entirely determined by which functions you expose and what your
code does before running them. An agent is exactly as dangerous as its tool
layer allows — never more.

## Narrow surfaces beat broad ones

The instinct is to give an agent everything and let it figure things out.
Resist it. A smaller tool surface means fewer ways to be wrong, a shorter
context, and a boundary you can reason about. Your own deploy-guard is the
cleanest example in the workspace.

Open `C:\Users\natee\.claude\agents\deploy-guard.md` and read the YAML
frontmatter:

```
tools: Bash, PowerShell, Read, Grep, Glob
```

Notice what is **absent**: no `Write`, no `Edit`. DeployGuard is an agent
whose entire job is protecting your code — backups, deploy tags, restores —
and it structurally *cannot modify a source file*. That isn't a promise in a
prompt; it's a capability boundary. Even a confused or manipulated
DeployGuard cannot edit `app.py`, because the function was never handed to
it.

Then notice how narrow its real toolkit is. Despite having a shell, its
actual interface is essentially **one CLI**:

```
python -m deployguard <command>
```

with nine subcommands (`status`, `backup`, `check`, `record`, `run`, `mark`,
`history`, `restore-points`, `restore`). All the domain logic — what counts
as a restore point, how a rescue tag gets written — lives in tested Python,
not in the model's head. The agent decides *which* command fits the request;
the CLI decides what that command means.

## Two layers of boundary

DeployGuard shows both kinds, and they are not equivalent:

- **Hard boundary** — the `tools:` frontmatter. Enforced by the harness. The
  agent cannot cross it, no matter what it decides.
- **Soft boundary** — the doctrine in the prose body: "never run `restore
  --yes` without Nate explicitly confirming," "never `--yes` past a
  reinvention warning on your own," "never print file contents from their
  data directories" (the HIPAA rule). These are *followed*, not enforced.

Put anything irreversible behind the hard boundary where you can, and behind
a human confirmation where you can't. Notice that DeployGuard's riskiest
operation — `restore` — is guarded twice: doctrine requires explicit
confirmation, and the CLI itself auto-commits current state to a
`rescue/<timestamp>` tag first, so even an unauthorized restore is
recoverable. That's the pattern: don't rely on the model's judgment for
anything you'd hate to undo.

## Try it

Open `deploy-guard.md` and list every tool it has. For each one, write down
the worst thing a badly-behaved agent could do with it — then check whether
`restore`'s auto-rescue tag would save you. Now look at DevDojo's `/ask`
route in `app.py`: it has no tools at all. What can it therefore never do,
and why is that the right call for a tutor?

## Quiz

1. Walk through the four steps of a tool round trip. Which two does the
   model participate in, and who is responsible for actually executing the
   call?
2. DeployGuard's frontmatter omits `Write` and `Edit`. Why is that a
   stronger guarantee than an instruction in its prompt saying "don't edit
   files"?
3. What's the difference between a hard boundary and a soft boundary in an
   agent definition, and where should an irreversible operation live?
