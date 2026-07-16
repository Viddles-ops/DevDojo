# Flask vs Streamlit: picking a front door

You run one of each in production, wrapping similar Python logic — which
makes the trade-offs concrete instead of theoretical. Compare
`oska_platform/oska_app.py` (Flask) with
`po_intake_automation/jett_automations/app.py` (Streamlit).

## Flask: you own the whole request

Flask gives you **routes** — functions bound to URLs that return whatever
you build: HTML, JSON, a PNG. oska_app carries its own inline HTML/CSS/JS
templates, a `/ask` JSON endpoint, base64-encoded matplotlib charts, and a
`@app.before_request` auth gate with sessions. Nothing is provided; nothing
is imposed. DevDojo itself is the same shape.

**Buy it when:** you need a real API (other code calls your endpoints),
custom interaction (the quiz page's per-question fetch calls), or precise
control over what a page is.

## Streamlit: the script *is* the UI

`jett_automations/app.py` has no routes and no HTML. It's a Python script
that runs **top to bottom on every interaction** — a button click reruns
the whole file, and `st.session_state` is what survives between runs.
Widgets are one-liners (`st.button`, `st.text_input`, `st.code`), so five
automations with output panes cost barely more code than the automations'
argument lists.

The rerun model has teeth, though: to stream live logs while a job runs,
the app can't just print — it runs the job in a **background thread** and
pumps log records through a `queue` into an `st.code` block
(`_run_streaming()`), because the script itself is being rerun, not
long-running. The framework's one abstraction leaks exactly where the app
does something interactive-and-long.

**Buy it when:** the whole UI is "buttons, forms, tables, logs" for an
internal audience and shipping this week beats owning the layout.

## Auth lives at the edge in both

Neither app trusts itself as the only gate. oska_app refuses to bind to a
non-local address without a password set; Jett Automations sits behind
**Google IAP** on Cloud Run (only granted accounts reach the app at all)
and keeps a local `APP_PASSWORD` gate purely for dev, which no-ops when
unset. Same doctrine, two mechanisms: authenticate *before* the app when
the platform offers it, *at startup* when it doesn't.

## Try it

Open both files side by side. Find where each one "shows output from a
long job": oska_app returns computed results from a route; the Streamlit
app needs `_run_streaming()`'s thread + queue. Then answer: which app
could serve DevDojo's quiz-grading JSON endpoint, and why can't the other
(without fighting it)?

## Quiz

1. What happens to a Streamlit script when the user clicks a button, and
   what mechanism preserves state across that?
2. Why does live log streaming in the Streamlit app require a background
   thread and a queue?
3. You're adding an endpoint other software will call with JSON. Which
   framework, and what specifically makes the other a bad fit?
