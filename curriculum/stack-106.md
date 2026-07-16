# Medallion + master data: the OSKA pipeline

OSKA ingests messy operational reports about veterans using a medical device
and turns them into numbers you can defend. Two architectures work together:
a **medallion** (layers of decreasing sensitivity) and **master data**
(golden records as the system of truth). Canonical reference:
`oska_platform/ARCHITECTURE.md`.

## The layers — sensitivity decreases as you go right

| Layer | What | Identifiers? |
|---|---|---|
| Raw | source files as exported | yes |
| **Bronze** | re-identified, full detail — audit + AI note-extraction reads here | **yes — local only** |
| **Silver** | identifiers stripped to RPID; notes sanitized | none |
| **Gold** | governed, small-cell-suppressed (n ≥ 11), LLM-safe | none |

**PHI stops at Bronze.** The enforcement is layered, not hopeful:
- **RPID** = `HMAC-SHA256(secret, login)` — a deterministic, name-free key.
  The login is the *match* key (allowed only in Bronze + the crosswalk); the
  RPID is the *published* key everything downstream joins on.
- **`pii_guard.py` fails the build** if an identifier column ever reaches
  Silver or Gold. A leak is a broken build, not a discovered incident.
- AI access follows the layers (ADR-011): note-extraction (local Ollama)
  reads Bronze; anything hosted or shared sees Gold only.
- Small-cell suppression at Gold (`min_cell_size: 11`) so aggregates can't
  re-identify a rare cohort by arithmetic.

## Master data: golden records, amended not rebuilt

Raw reports *amend* persistent curated masters (`masters/master_veteran.csv`
et al.) — they never bulk-replace them. The engine (`src/masters/mdm.py`
`reconcile()`) handles auto-add / enrich-blank / locked fields / conflict
queue / audit trail. Rule: **never hand-edit a generated table** — durable
fixes go in the master (locked fields) or `config/overrides/`.

## The upsert with a curation overlay (`build_consolidated_master.py`)

The subtlest piece. Two ideas:
1. **Population upsert** — veterans new since the curation seed are
   *appended* with a lifecycle status (`auto_added` → `reviewed` once a
   human curates them → `review_stale` if their notes later change).
2. **Curation overlay = priority truth** — human-curated values *win* over
   machine-mined values for every curated field, with explicit precedence
   (curated > manual update > mined > legacy). Consequence: re-running the
   LLM miners can **never overwrite a human decision**. Machine output is a
   draft; curation is a commit.

## Try it

Read the layer table in `oska_platform/ARCHITECTURE.md`, then answer: a new
report arrives with veteran names and note text — trace which layers it
touches before a number derived from it can be quoted to anyone outside the
building. Then find the precedence list in `build_consolidated_master.py`.

## Quiz

1. Why is the RPID an HMAC of the login rather than just a random ID or the
   login itself?
2. What does `pii_guard.py` turn a PHI leak into, and why is that better
   than an access policy alone?
3. A curator fixed a veteran's pain score last month; today the note miner
   re-runs. What happens to the curated value, and which mechanism
   guarantees it?
