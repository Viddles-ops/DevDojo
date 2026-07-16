# Logging and error handling patterns

When a Cloud Function fails at 2am, the log *is* the debugger. PO Intake is
your best source of patterns because it talks to four unreliable things —
Drive, Gemini, UPS, Sheets — and stays up anyway. Five patterns, all real.

## 1. Log the cause AND the consequence

From `drive_utils.py`, when PDF text extraction fails:

```python
logger.warning(f"pypdf extraction failed ({exc}); returning empty string for vision fallback")
```

One line carries what broke, why, and *what happens next*. Compare
`print("error")` — at 2am, the difference is an hour of your life. Levels
carry meaning: `warning` = handled, degraded; `error` = a row/file failed;
`exception`/`error(..., exc_info=True)` = stack trace attached.

## 2. Fallback chains: degrade, don't die

The same failure above *feeds a plan B*: too little text from pypdf →
send the raw PDF bytes to Gemini vision instead. Same idea elsewhere:
`gemini_parser.py` keeps a `_PREFERRED_MODELS` list ordered
best-to-fallback (a new model is added at the top; old ones automatically
become fallbacks — no other code changes), and `tracking_update.py` parses
undocumented UPS status codes with two layers: match the description text,
and if that fails, infer from the delivery-date record type. The shape:
**every external call has a cheaper/cruder answer behind it.**

## 3. Fail loud when there's no plan B

Fallbacks are for degradable paths only. When the Gemini key is missing,
`gemini_parser.py` raises `RuntimeError` with a message that says exactly
what to fix — no silent skip, no empty result pretending to be data.
The distinction to internalize: **recoverable → log + degrade;
misconfiguration → crash with instructions.**

## 4. Don't trust your own AI — verify its output

`verify_address_grounding()` checks that the address Gemini extracted
actually appears in the source document — catching the model deviating
from the PO before a package ships to a hallucinated street. Downstream,
the UPS Address Validation API confirms the address is real. LLM output is
input like any other: validate it against ground truth you hold.

## 5. Design for the re-run

Errors *will* happen mid-batch, so every batch is resumable: failed rows
are logged and skipped (not retried forever, never blocking the rest),
work is written incrementally, and idempotent writes (stack-108) make the
re-run safe. A Cloud Function adds a hard deadline — the row cap exists
because a 6-minute timeout mid-write is worse than a smaller batch.

## Try it

Open `po_intake_automation/gemini_parser.py` and find `_PREFERRED_MODELS`
and the missing-key `RuntimeError`. Classify each of the five patterns
above as "degrade" or "fail loud". Then grep DevDojo's `tutor/` for its
one deliberate fail-safe default — what does `_parse_verdict` do with
garbage model output, and which pattern is that?

## Quiz

1. A dependency call fails. What decides whether you log-and-degrade or
   raise immediately, per patterns 2 and 3?
2. What does `verify_address_grounding()` protect against, and what
   general rule about LLM output does it encode?
3. Why does a batch job skip failed rows and write incrementally instead
   of retrying each failure until it succeeds?
