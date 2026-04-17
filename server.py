"""
Lightweight Flask server – shows the latest digest as a web page.
Railway needs a running web process; this also lets you view results in the browser.
"""
import os
import json
from flask import Flask, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)
OUTPUT_FILE = "output/digest.json"

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PaperClub AI</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 860px; margin: 40px auto; padding: 0 20px; background: #0f0f12; color: #e2e2e8; }
    h1 { color: #a78bfa; }
    .meta { color: #888; font-size: .85em; margin-bottom: 2rem; }
    .paper { background: #1a1a24; border-left: 3px solid #7c3aed; padding: 1.2rem 1.5rem; margin-bottom: 1.5rem; border-radius: 6px; }
    .paper h2 { font-size: 1.1rem; margin: 0 0 .4rem; }
    .paper h2 a { color: #c4b5fd; text-decoration: none; }
    .paper h2 a:hover { text-decoration: underline; }
    .authors { color: #888; font-size: .82em; margin-bottom: .6rem; }
    .summary { white-space: pre-line; font-size: .92rem; line-height: 1.6; color: #ccc; }
    .empty { color: #888; margin-top: 3rem; }
    .badge { display:inline-block; background:#7c3aed22; color:#a78bfa; border:1px solid #7c3aed44; padding:2px 10px; border-radius:20px; font-size:.8em; }
  </style>
</head>
<body>
  <h1>📚 PaperClub AI</h1>
  {% if digest %}
    <p class="meta">
      Topic: <span class="badge">{{ digest.topic }}</span>
      &nbsp;·&nbsp; Generated: {{ digest.generated_at[:19].replace('T',' ') }} UTC
      &nbsp;·&nbsp; {{ digest.papers|length }} papers
    </p>
    {% for p in digest.papers %}
    <div class="paper">
      <h2><a href="{{ p.url }}" target="_blank">{{ p.title }}</a></h2>
      {% if p.authors %}<p class="authors">{{ p.authors | join(', ') }}</p>{% endif %}
      <div class="summary">{{ p.summary }}</div>
    </div>
    {% endfor %}
  {% else %}
    <p class="empty">No digest yet. The scheduler runs daily – check back soon!<br>
    Or trigger a run: <code>python main.py</code></p>
  {% endif %}
</body>
</html>
"""

def load_digest():
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            return json.load(f)
    return None

@app.route("/")
def index():
    digest = load_digest()
    return render_template_string(HTML, digest=digest)

@app.route("/api/digest")
def api_digest():
    digest = load_digest()
    if digest:
        return jsonify(digest)
    return jsonify({"error": "No digest yet"}), 404

@app.route("/health")
def health():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
