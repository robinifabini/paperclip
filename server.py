import os
import uuid
import asyncio
from typing import Dict
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from crew import run_task

app = FastAPI(title="KI-Firma")

aufgaben: Dict[str, dict] = {}

HTML = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>KI-Firma</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #0f0f13; color: #e2e8f0; min-height: 100vh; }
  header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
           padding: 20px 30px; }
  header h1 { font-size: 1.6rem; font-weight: 700; }
  header p  { font-size: 0.9rem; opacity: 0.85; margin-top: 4px; }
  .container { max-width: 900px; margin: 30px auto; padding: 0 20px; }
  .box { background: #1a1a2e; border-radius: 16px; padding: 25px;
         margin-bottom: 25px; border: 1px solid #2d2d4e; }
  .box h2 { font-size: 0.85rem; color: #a78bfa; margin-bottom: 18px;
            text-transform: uppercase; letter-spacing: 1px; }
  .ceo-box { background: linear-gradient(135deg, #667eea, #764ba2);
             border-radius: 10px; padding: 14px; text-align: center;
             font-weight: 700; margin-bottom: 12px; }
  .arrow { text-align: center; color: #555; margin: 6px 0; font-size: 1.2rem; }
  .agents-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; }
  .agent-card { background: #252540; border-radius: 10px; padding: 14px;
                border: 2px solid #3a3a5c; cursor: pointer; transition: all 0.2s; text-align: center; }
  .agent-card:hover { border-color: #667eea; }
  .agent-card.active { border-color: #667eea; background: #2d2d55; }
  .agent-card .icon { font-size: 2rem; margin-bottom: 6px; }
  .agent-card .name { font-weight: 600; font-size: 0.9rem; }
  .agent-card .desc { font-size: 0.75rem; color: #888; margin-top: 3px; }
  .selected-info { background: #252540; border-radius: 8px; padding: 10px 14px;
                   margin-bottom: 12px; font-size: 0.9rem; color: #a78bfa; border: 1px solid #3a3a5c; }
  textarea { width: 100%; background: #252540; border: 1px solid #3a3a5c;
             border-radius: 10px; padding: 14px; color: #e2e8f0; font-size: 1rem;
             resize: vertical; min-height: 110px; outline: none; font-family: inherit; }
  textarea:focus { border-color: #667eea; }
  .btn { background: linear-gradient(135deg, #667eea, #764ba2);
         border: none; color: white; padding: 14px; border-radius: 10px;
         font-size: 1rem; font-weight: 600; cursor: pointer; margin-top: 12px;
         width: 100%; }
  .btn:disabled { opacity: 0.5; cursor: not-allowed; }
  .result-content { background: #252540; border-radius: 10px; padding: 20px;
                    white-space: pre-wrap; line-height: 1.7; }
  .badge { display: inline-block; padding: 4px 12px; border-radius: 20px;
           font-size: 0.8rem; font-weight: 600; margin-bottom: 12px; }
  .badge-run { background: #f59e0b22; color: #f59e0b; border: 1px solid #f59e0b55; }
  .badge-ok  { background: #10b98122; color: #10b981; border: 1px solid #10b98155; }
  .badge-err { background: #ef444422; color: #ef4444; border: 1px solid #ef444455; }
  #resultBox { display: none; }
</style>
</head>
<body>

<header>
  <h1>🤖 KI-Firma</h1>
  <p>Dein CEO koordiniert Developer, Researcher, Marketing &amp; Analyst</p>
</header>

<div class="container">

  <div class="box">
    <h2>📋 Dein Team</h2>
    <div class="ceo-box">👔 CEO – koordiniert alles</div>
    <div class="arrow">↓ delegiert an ↓</div>
    <div class="agents-grid">
      <div class="agent-card active" onclick="select_dept(this,'auto')">
        <div class="icon">🧠</div>
        <div class="name">Automatisch</div>
        <div class="desc">CEO entscheidet selbst</div>
      </div>
      <div class="agent-card" onclick="select_dept(this,'developer')">
        <div class="icon">👨‍💻</div>
        <div class="name">Developer</div>
        <div class="desc">Apps &amp; Code bauen</div>
      </div>
      <div class="agent-card" onclick="select_dept(this,'researcher')">
        <div class="icon">🔍</div>
        <div class="name">Researcher</div>
        <div class="desc">Themen recherchieren</div>
      </div>
      <div class="agent-card" onclick="select_dept(this,'marketing')">
        <div class="icon">📣</div>
        <div class="name">Marketing</div>
        <div class="desc">Texte &amp; Kampagnen</div>
      </div>
      <div class="agent-card" onclick="select_dept(this,'analyst')">
        <div class="icon">📊</div>
        <div class="name">Analyst</div>
        <div class="desc">Analysen &amp; Strategien</div>
      </div>
    </div>
  </div>

  <div class="box">
    <h2>✏️ Aufgabe eingeben</h2>
    <div class="selected-info" id="selectedInfo">🧠 CEO entscheidet automatisch, wer die Aufgabe übernimmt</div>
    <textarea id="taskInput" placeholder="z.B. Erstelle eine Landing Page für meine KI-Firma... oder: Schreib einen LinkedIn-Post über KI-Trends..."></textarea>
    <button class="btn" id="submitBtn" onclick="submit_task()">🚀 Aufgabe starten</button>
  </div>

  <div class="box" id="resultBox">
    <h2>📬 Ergebnis</h2>
    <div id="badge" class="badge badge-run">⟳ Agenten arbeiten...</div>
    <div class="result-content" id="resultContent">Dein Team analysiert die Aufgabe...\n\nDas kann 1–2 Minuten dauern.</div>
  </div>

</div>

<script>
var current_dept = 'auto';
var poll_id = null;

var dept_labels = {
  'auto': '🧠 CEO entscheidet automatisch, wer die Aufgabe übernimmt',
  'developer': '👨‍💻 Developer übernimmt – CEO reviewed das Ergebnis',
  'researcher': '🔍 Researcher übernimmt – CEO reviewed das Ergebnis',
  'marketing': '📣 Marketing übernimmt – CEO reviewed das Ergebnis',
  'analyst': '📊 Analyst übernimmt – CEO reviewed das Ergebnis'
};

function select_dept(el, dept) {
  var cards = document.querySelectorAll('.agent-card');
  for (var i = 0; i < cards.length; i++) {
    cards[i].classList.remove('active');
  }
  el.classList.add('active');
  current_dept = dept;
  document.getElementById('selectedInfo').textContent = dept_labels[dept];
}

function submit_task() {
  var aufgabe = document.getElementById('taskInput').value.trim();
  if (!aufgabe) {
    alert('Bitte eine Aufgabe eingeben!');
    return;
  }

  var btn = document.getElementById('submitBtn');
  btn.disabled = true;
  btn.textContent = '⏳ Agenten arbeiten...';

  var resultBox = document.getElementById('resultBox');
  resultBox.style.display = 'block';
  document.getElementById('badge').className = 'badge badge-run';
  document.getElementById('badge').textContent = '⟳ Agenten arbeiten...';
  document.getElementById('resultContent').textContent = 'Dein Team analysiert die Aufgabe...\n\nDas kann 1-2 Minuten dauern.';

  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/api/aufgabe', true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.onload = function() {
    if (xhr.status === 200) {
      var data = JSON.parse(xhr.responseText);
      poll_id = setInterval(function() { check_status(data.aufgabe_id); }, 3000);
    } else {
      document.getElementById('badge').className = 'badge badge-err';
      document.getElementById('badge').textContent = 'Fehler beim Starten';
      document.getElementById('resultContent').textContent = xhr.responseText;
      btn.disabled = false;
      btn.textContent = '🚀 Aufgabe starten';
    }
  };
  xhr.onerror = function() {
    document.getElementById('badge').className = 'badge badge-err';
    document.getElementById('badge').textContent = 'Verbindungsfehler';
    btn.disabled = false;
    btn.textContent = '🚀 Aufgabe starten';
  };
  xhr.send(JSON.stringify({aufgabe: aufgabe, abteilung: current_dept}));
}

function check_status(id) {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', '/api/aufgabe/' + id, true);
  xhr.onload = function() {
    if (xhr.status === 200) {
      var data = JSON.parse(xhr.responseText);
      if (data.status === 'done') {
        clearInterval(poll_id);
        document.getElementById('badge').className = 'badge badge-ok';
        document.getElementById('badge').textContent = '✅ Fertig';
        document.getElementById('resultContent').textContent = data.ergebnis;
        var btn = document.getElementById('submitBtn');
        btn.disabled = false;
        btn.textContent = '🚀 Neue Aufgabe starten';
      } else if (data.status === 'fehler') {
        clearInterval(poll_id);
        document.getElementById('badge').className = 'badge badge-err';
        document.getElementById('badge').textContent = '❌ Fehler';
        document.getElementById('resultContent').textContent = data.ergebnis;
        var btn = document.getElementById('submitBtn');
        btn.disabled = false;
        btn.textContent = '🚀 Nochmal versuchen';
      }
    }
  };
  xhr.send();
}
</script>
</body>
</html>"""


class AufgabeRequest(BaseModel):
    aufgabe: str
    abteilung: str = "auto"


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML


@app.head("/")
async def home_head():
    return HTMLResponse(content="", status_code=200)


@app.post("/api/aufgabe")
async def neue_aufgabe(req: AufgabeRequest, background_tasks: BackgroundTasks):
    aufgabe_id = str(uuid.uuid4())[:8]
    aufgaben[aufgabe_id] = {"status": "laeuft", "ergebnis": None}
    background_tasks.add_task(_execute, aufgabe_id, req.aufgabe, req.abteilung)
    return {"aufgabe_id": aufgabe_id}


@app.get("/api/aufgabe/{aufgabe_id}")
async def aufgabe_status(aufgabe_id: str):
    if aufgabe_id not in aufgaben:
        return JSONResponse({"fehler": "Nicht gefunden"}, status_code=404)
    return aufgaben[aufgabe_id]


@app.get("/health")
async def health():
    return {"status": "ok"}


async def _execute(aufgabe_id: str, aufgabe: str, abteilung: str):
    try:
        loop = asyncio.get_event_loop()
        ergebnis = await loop.run_in_executor(None, run_task, aufgabe, abteilung)
        aufgaben[aufgabe_id] = {"status": "done", "ergebnis": ergebnis}
    except Exception as e:
        aufgaben[aufgabe_id] = {"status": "fehler", "ergebnis": f"Fehler: {e}"}
