# Secrets done right: Secret Manager + os.environ

One rule governs every project in this workspace (decision ADR-002): **code
reads credentials via `os.environ.get("NAME")` — values live somewhere safer
than the code.** Key files (`*-sa-key.json`, `.env`, `desktop-oauth.json`)
are never committed; every `.gitignore` blocks them. Where the value actually
lives depends on where the code runs.

## The three tiers, from your own projects

**Tier 0 — need no secret at all (OSKA, DevDojo).** Local Ollama at
`localhost:11434` requires no API key. That's not an accident: the AI-backend
policy (ADR-011) routes the most sensitive data to the backend with the
smallest credential surface. The best secret is the one that doesn't exist.

**Tier 1 — Secret Manager, bound at deploy (PO Intake, done right).**
`UPS_CLIENT_ID`/`UPS_CLIENT_SECRET` are Secret Manager secrets, attached in
the deploy command:

```powershell
gcloud functions deploy po-intake ... `
  --set-secrets=UPS_CLIENT_ID=UPS_CLIENT_ID:latest,UPS_CLIENT_SECRET=UPS_CLIENT_SECRET:latest
```

The function sees them as env vars; `gcloud functions describe` shows only
the *binding* (`UPS_CLIENT_ID:latest`), never the value. Note they exist
separately in **both** GCP projects — rotating means updating both.

**Tier 2 — plain env var: the cautionary tale.** `GEMINI_API_KEY` on the
`po-intake` function is set with `--update-env-vars`, not `--set-secrets`.
Consequence, straight from that project's CLAUDE.md: **`gcloud functions
deploy`/`describe` output prints it in cleartext.** Every deploy log, every
terminal transcript, every pasted troubleshooting session is a potential
leak. The standing rule: treat any value seen in a log as exposed — rotate
it, then migrate to Secret Manager. That migration is open backlog item
PO-001. The key was never committed to git, and it's still considered
exposed — "not in the repo" is a much lower bar than "secret".

## Local dev without key files

For local runs against GCP, prefer **ADC with impersonation**
(`gcloud auth application-default login --impersonate-service-account=...`)
— no key file exists on disk at all. Fallback: a downloaded key whose *path*
is passed via env var (`$env:SERVICE_ACCOUNT_KEY_FILE`), so the path
convention is shareable while the file itself stays out of git.

## Try it

In `po_intake_automation\`, run
`git grep -n "os.environ"` — confirm every credential read goes through
`os.environ.get()` with no literal secret as a fallback default. Then find
`GEMINI_API_KEY` in that repo's CLAUDE.md and read exactly how it's flagged.

## Quiz

1. `GEMINI_API_KEY` was never committed to git. Why is it still treated as
   exposed?
2. In a `gcloud functions deploy` command, what's the security difference
   between `--set-secrets` and `--update-env-vars`?
3. Why do OSKA and DevDojo need no API keys at all, and how does that follow
   from the tiered AI-backend policy?
