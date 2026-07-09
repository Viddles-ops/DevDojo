# Two ways to ship: Cloud Functions vs Cloud Run

PO Intake runs the **same codebase** on two different GCP compute products.
Understanding why makes every deploy decision obvious. (Everything here is
mined from `po_intake_automation/CLAUDE.md` — its Architecture and Deploy
Commands sections are the authoritative reference.)

## The two targets

| | Cloud Functions Gen2 | Cloud Run |
|---|---|---|
| GCP project | `gen-lang-client-0687448191` (us-east1) | `gleaming-scene-492321-s4` (us-central1) |
| Unit of deploy | **one entry-point function** from source | **one container** holding the whole app |
| Who calls it | Apps Script buttons in Google Sheets (HTTP) | Humans, via the IAP-protected Streamlit UI |
| Examples | `po-intake`, `jumpstart-matcher`, `jumpstart-reporter` | `jett-automations` (all five automations, live logs) |

## Why the deploy shapes differ

**Cloud Functions deploys source.** `gcloud functions deploy po-intake
--entry-point=po_intake --source=. ...` uploads the directory and GCP builds
it, but only *that one HTTP entry point* is exposed. Each function carries its
own memory/timeout flags and its own `--set-secrets` bindings. Change
`jumpstart_matcher.py` and you must redeploy the `jumpstart-matcher` function
specifically — the others still run the old code.

**Cloud Run deploys a container.** `jett_automations/Dockerfile` copies
*every* `.py` file into the image; `gcloud builds submit` builds it, then
`gcloud run deploy` swaps the service to the new image. Consequence, straight
from the project's CLAUDE.md: *redeploying Cloud Run after any change is
always safe and never wrong* — the whole directory ships every time. The
per-file "which target needs redeploying" table exists only because Apps
Script buttons call the Cloud Functions directly, bypassing Cloud Run.

## When each fits

- **Cloud Function** — a single HTTP-triggered job invoked by another system
  (a Sheet button, a webhook). Scales to zero, no UI, hard timeout (540s max
  here), config pinned per function.
- **Cloud Run** — a real web app: Streamlit UI, sessions, streaming logs,
  auth via IAP, bigger CPU/memory, anything long-running or interactive.

## Docs vs reality — always verify

The CLAUDE.md documents a `tracking-update` function that was **never
actually deployed** (Secret Manager wasn't even enabled in that project until
2026-06-26). UPS tracking only ever ran via Cloud Run. Lesson inside the
lesson: deploy docs describe intent — `gcloud functions list` describes
reality.

## Try it

Read the "Which file changes require redeploying what" table in
`po_intake_automation/CLAUDE.md`, then answer without looking: you just
edited `tracking_update.py` — what needs redeploying? Verify your answer
against reality with:
`gcloud functions list --project=gen-lang-client-0687448191` and
`gcloud run services list --project=gleaming-scene-492321-s4`.

## Quiz

1. Why is redeploying Cloud Run "always safe and never wrong" after any file
   change, while Cloud Functions need selective redeploys?
2. An Apps Script button in AutoLogistics triggers PO intake. Which deploy
   target does it hit, and why doesn't a Cloud Run redeploy update it?
3. The docs list a `tracking-update` Cloud Function. What single command
   proves whether it actually exists, and what's the real answer?
