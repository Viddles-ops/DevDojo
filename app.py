"""DevDojo — local coding tutor. Routes only; logic lives in tutor/ modules."""
from flask import Flask, jsonify, redirect, render_template_string, request, url_for
import markdown as md

import config
from tutor import curriculum, ollama_client, progress, quiz

app = Flask(__name__)

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DevDojo</title>
<style>
 body{font-family:Segoe UI,system-ui,sans-serif;max-width:860px;margin:2rem auto;
      padding:0 1rem;background:#101418;color:#e6e6e6;line-height:1.55}
 a{color:#7ec8ff;text-decoration:none} a:hover{text-decoration:underline}
 h1{color:#fff} h2{color:#a9d18e;margin-top:1.6rem}
 .lesson{padding:.45rem .7rem;border-left:3px solid #333;margin:.3rem 0}
 .lesson.available{border-color:#a9d18e}
 .lesson.done{border-color:#7ec8ff}
 .tag{font-size:.75rem;color:#888;margin-left:.5rem}
 .card{background:#181e24;border-radius:8px;padding:1rem 1.4rem;margin:1rem 0}
 pre{background:#0b0e11;padding:.8rem;border-radius:6px;overflow-x:auto}
 code{background:#0b0e11;padding:.1rem .3rem;border-radius:4px}
 textarea,button{font:inherit} textarea{width:100%;background:#0b0e11;color:#e6e6e6;
      border:1px solid #333;border-radius:6px;padding:.6rem}
 button{background:#a9d18e;color:#101418;border:0;border-radius:6px;
      padding:.5rem 1.1rem;margin-top:.5rem;cursor:pointer;font-weight:600}
 .muted{color:#888;font-size:.85rem}
</style></head><body>
<h1>🥋 DevDojo</h1>
{{ body|safe }}
</body></html>"""


@app.route("/")
def index():
    lessons = curriculum.load_index()
    done = progress.completed_ids()
    grouped = curriculum.by_track(lessons)
    parts = [f"<p class='muted'>Tutor model: {config.OLLAMA_MODEL} — "
             f"{'🟢 Ollama up' if ollama_client.is_up() else '🔴 Ollama down (browsing still works)'}"
             f" &nbsp;·&nbsp; {len(done)}/{len(lessons)} lessons complete</p>"]
    for track, title in config.TRACKS.items():
        parts.append(f"<h2>{title}</h2>")
        for l in grouped.get(track, []):
            cls = "done" if l.id in done else ("available" if l.is_available else "")
            mark = "✅ " if l.id in done else ""
            link = (f"<a href='{url_for('lesson', lesson_id=l.id)}'>{mark}{l.title}</a>"
                    if l.is_available else f"<span class='muted'>{l.title}</span>")
            src = f"<span class='tag'>from: {', '.join(l.sources)}</span>" if l.sources else ""
            planned = "<span class='tag'>planned</span>" if not l.is_available else ""
            parts.append(f"<div class='lesson {cls}'>{link} {src} {planned}"
                         f"<br><span class='muted'>{l.summary}</span></div>")
    return render_template_string(PAGE, body="".join(parts))


@app.route("/lesson/<lesson_id>")
def lesson(lesson_id):
    l = curriculum.get_lesson(lesson_id)
    if not l or not l.is_available:
        return redirect(url_for("index"))
    body = f"""
    <p><a href='/'>&larr; all lessons</a></p>
    <div class='card'>{md.markdown(curriculum.lesson_text(l), extensions=['fenced_code', 'tables'])}</div>
    <form method='post' action='{url_for("complete", lesson_id=l.id)}'>
      <button>Mark complete ✅</button></form>
    <p><a href='{url_for("quiz_page", lesson_id=l.id)}'>Take the quiz 📝</a></p>
    <h2>Ask the tutor about this lesson</h2>
    <textarea id='q' rows='3' placeholder='e.g. Why does the rescue tag matter?'></textarea>
    <button onclick='askTutor()'>Ask</button>
    <div class='card' id='answer' style='display:none'></div>
    <script>
    async function askTutor() {{
      const box = document.getElementById('answer');
      box.style.display = 'block'; box.textContent = 'Thinking (local model)…';
      const r = await fetch('/ask', {{method:'POST',
        headers:{{'Content-Type':'application/json'}},
        body: JSON.stringify({{question: document.getElementById('q').value,
                               lesson_id: '{l.id}'}})}});
      const data = await r.json();
      box.textContent = data.answer || data.error;
    }}
    </script>"""
    return render_template_string(PAGE, body=body)


@app.route("/lesson/<lesson_id>/complete", methods=["POST"])
def complete(lesson_id):
    progress.mark_complete(lesson_id)
    return redirect(url_for("index"))


@app.route("/quiz/<lesson_id>")
def quiz_page(lesson_id):
    l = curriculum.get_lesson(lesson_id)
    if not l or not l.is_available:
        return redirect(url_for("index"))
    questions = quiz.parse_quiz(curriculum.lesson_text(l))
    if not questions:
        return redirect(url_for("lesson", lesson_id=l.id))
    status = ("" if ollama_client.is_up() else
              "<p class='muted'>🔴 Tutor offline — questions are readable, "
              "but grading needs Ollama running.</p>")
    blocks = []
    for i, q in enumerate(questions):
        blocks.append(
            f"<div class='card'><b>Q{i + 1}.</b> {q}"
            f"<textarea id='a{i}' rows='2' placeholder='Your answer…'></textarea>"
            f"<button onclick='grade({i})'>Check answer</button>"
            f"<div id='r{i}' class='muted' style='display:none'></div></div>")
    body = f"""
    <p><a href='{url_for("lesson", lesson_id=l.id)}'>&larr; back to lesson</a></p>
    <h2>Quiz — {l.title}</h2>
    {status}
    {''.join(blocks)}
    <script>
    async function grade(i) {{
      const r = document.getElementById('r' + i);
      r.style.display = 'block'; r.textContent = 'Grading (local model)…';
      const resp = await fetch('/quiz/{l.id}/answer', {{method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{question_idx: i,
                               answer: document.getElementById('a' + i).value}})}});
      const data = await resp.json();
      if (data.error) {{ r.textContent = data.error; return; }}
      r.textContent = (data.correct ? '✅ Correct — ' : '❌ Not quite — ') + data.feedback;
    }}
    </script>"""
    return render_template_string(PAGE, body=body)


@app.route("/quiz/<lesson_id>/answer", methods=["POST"])
def quiz_answer(lesson_id):
    l = curriculum.get_lesson(lesson_id)
    if not l or not l.is_available:
        return jsonify({"error": "Unknown lesson."}), 404
    lesson_body = curriculum.lesson_text(l)
    questions = quiz.parse_quiz(lesson_body)
    payload = request.get_json(force=True)
    try:
        idx = int(payload.get("question_idx", -1))
    except (TypeError, ValueError):
        idx = -1
    answer = (payload.get("answer") or "").strip()
    if not 0 <= idx < len(questions):
        return jsonify({"error": "Unknown question."}), 400
    if not answer:
        return jsonify({"error": "Write an answer first."}), 400
    if not ollama_client.is_up():
        return jsonify({"error": "Tutor offline — start Ollama to grade answers."}), 503
    verdict = quiz.grade_answer(questions[idx], answer, lesson_body)
    quiz.record_quiz_result(l.id, idx, verdict["correct"])
    return jsonify(verdict)


@app.route("/ask", methods=["POST"])
def ask():
    payload = request.get_json(force=True)
    question = (payload.get("question") or "").strip()
    if not question:
        return jsonify({"error": "Ask something first."}), 400
    if not ollama_client.is_up():
        return jsonify({"error": "Ollama isn't running — start it and try again."}), 503
    grounding = ""
    l = curriculum.get_lesson(payload.get("lesson_id", ""))
    if l and l.is_available:
        grounding = curriculum.lesson_text(l)
    return jsonify({"answer": ollama_client.ask(question, grounding)})


if __name__ == "__main__":
    app.run(port=config.APP_PORT, debug=False)
