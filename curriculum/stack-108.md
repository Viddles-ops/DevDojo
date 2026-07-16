# Google Sheets/Drive APIs + Apps Script buttons

PO Intake's UI for the logistics team is... a Google Sheet. That's a real
architecture: the sheet is the database *and* the frontend, Apps Script
buttons are the triggers, and Cloud Functions are the backend. The patterns
below are what make it survive real use. (Files: `sheets_utils.py`,
`drive_utils.py`, `tracking_update.py`, and the Apps Script section of
`po_intake_automation/CLAUDE.md`.)

## The trigger path: button → Apps Script → Cloud Function

A drawing/button in the sheet is bound to an Apps Script function
(`runPOIntake`, etc.). The script calls the Cloud Function over HTTP,
authenticating with a **service-account identity token** — so the function
stays `--no-allow-unauthenticated` and the person clicking never handles a
credential. One operational rule with its own scar tissue: when editing the
bound script, always paste a **complete replacement** of the file — pasting
a section deletes every function you didn't paste.

## Writing to a sheet humans also edit

A bot sharing a table with people needs manners, all of them explicit:

- **Column ownership.** Every column is designated bot-written, manual, or
  shared — the bot never writes outside its columns. Shared ones have write
  rules (e.g. the delivery column is written once, on terminal status only,
  in the team's exact manual format).
- **Mark bot writes.** Bot values carry a `~` prefix (`BOT_PREFIX`), and a
  conditional-formatting rule highlights them — humans can see at a glance
  what the bot did.
- **Replace vs append, decided per column.** The status-log column is
  *replaced* every run (latest state, no scroll); the delivery column is
  *append-once, then frozen*.
- **Terminal filter.** A non-empty terminal column takes the row out of all
  future runs — the bot converges instead of re-touching everything.
- **Sentinels.** Humans write values like `N/A` / `Not a match` to tell the
  matcher "stop trying this row" — a manual override channel *inside* the
  data.

## Idempotency: safe to run twice

Every automation assumes it will be re-run: a registry tab records each
processed PO for duplicate detection *before* new processing; the tracking
handoff tab is keyed by tracking number so a re-run can't create duplicate
rows; Drive files are *moved* to a Processed folder so the intake folder is
always exactly the backlog. The test for every write you design here:
**run it twice — the second run must change nothing.**

## Try it

Read the column write rules and the Tracking_Registry description in
`po_intake_automation/CLAUDE.md`, then design (on paper) a bot that adds a
"follow-up date" to a human-edited sheet: which of the five manners above
does it need, and what's its idempotency key?

## Quiz

1. Trace a button click from the sheet to code running in GCP — what
   authenticates the call, and why does the human never see a credential?
2. Why does the bot prefix its writes with `~`, and who is that for?
3. An automation re-runs after a crash halfway through. Name two mechanisms
   in this project that make that safe rather than duplicating work.
