import os
import uuid
import asyncio
from typing import Dict
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from crew import run_task
from agents import AVAILABLE_AGENTS

app = FastAPI(title="KI-Firma")

# Aufgaben-Speicher (im RAM – reicht für den Start)
aufgaben: Dict[str, dict] = {}


# ── HTML UI ──────────────────────────────────────────────────────────────────

HTML = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>KI-Firma 🤖</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #0f0f13; color: #e2e8f0; min-height: 100vh; }
  header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
           padding: 20px 30px; display: flex; align-items: center; gap: 15px; }
  header h1 { font-size: 1.6rem; font-weight: 700; }
  header p  { font-size: 0.9rem; opacity: 0.85; }
  .container { max-width: 900px; margin: 30px auto; padding: 0 20px; }

  /* Organigramm */
  .org { background: #1a1a2e; border-radius: 16px; padding: 25px;
         margin-bottom: 30px; border: 1px solid #2d2d4e; }
  .org h2 { font-size: 1rem; color: #a78bfa; margin-bottom: 20px; text-transform: uppercase;
            letter-spacing: 1px; }
  .ceo-box { background: linear-gradient(135deg, #667eea, #764ba2);
             border-radius: 12px; padding: 15px 20px; text-align: center;
             margin-bottom: 15px; font-weight: 700; font-size: 1.1rem; }
  .arrow { text-align: center; color: #4a4a6a; font-size: 1.5rem; margin: 5px 0; }
  .agents-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }
  .agent-card { background: #252540; border-radius: 10px; padding: 12px 15px;
                border: 1px solid #3a3a5c; cursor: pointer; transition: all 0.2s;
                text-align: center; }
  .agent-card:hover, .agent-card.selected { border-color: #667eea; background: #2d2d55; }
  .agent-card .icon { font-size: 1.8rem; margin-bottom: 5px; }
  .agent-card .name { font-weight: 600; font-size: 0.9rem; }
  .agent-card .desc { font-size: 0.75rem; color: #888; margin-top: 3px; }

  /* Aufgaben-Eingabe */
  .task-box { background: #1a1a2e; border-radius: 16px; padding: 25px;
              margin-bottom: 30px; border: 1px solid #2d2d4e; }
  .task-box h2 { font-size: 1rem; color: #a78bfa; margin-bottom: 15px;
                 text-transform: uppercase; letter-spacing: 1px; }
  textarea { width: 100%; background: #252540; border: 1px solid #3a3a5c;
             border-radius: 10px; padding: 14px; color: #e2e8f0; font-size: 1rem;
             resize: vertical; min-height: 100px; outline: none;
             font-family: inherit; transition: border-color 0.2s; }
  textarea:focus { border-color: #667eea; }
  .btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
         border: none; color: white; padding: 13px 30px; border-radius: 10px;
         font-size: 1rem; font-weight: 600; cursor: pointer; margin-top: 12px;
         width: 100%; transition: opacity 0.2s; }
  .btn:hover { opacity: 0.9; }
  .btn:disabled { opacity: 0.5; cursor: not-allowed; }

  /* Ergebnis */
  .result-box { background: #1a1a2e; border-radius: 16px; padding: 25px;
                border: 1px solid #2d2d4e; display: none; }
  .result-box h2 { font-size: 1rem; color: #a78bfa; margin-bottom: 15px;
                   text-transform: uppercase; letter-spacing: 1px; }
  .result-content { background: #252540; border-radius: 10px; padding: 20px;
                    white-space: pre-wrap; line-height: 1.7; font-size: 0.95rem; }
  .status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px;
                  font-size: 0.8rem; font-weight: 600; margin-bottom: 12px; }
  .status-running { background: #f59e0b22; color: #f59e0b; border: 1px solid #f59e0b44; }
  .status-done { background: #10b98122; color: #10b981; border: 1px solid #10b98144; }
  .status-error { background: #ef444422; color: #ef4444; border: 1px solid #ef444444; }
  .spinner { display: inline-block; animation: spin 1s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .selected-agent { background: #2d2d55; border: 1px solid #667eea;
                    border-radius: 8px; padding: 8px 14px; margin-bottom: 10px;
                    font-size: 0.9rem; color: #a78bfa; }
</style>
</head>
<body>

<header>
  <div>
    <h1>🤖 KI-Firma</h1>
    <p>Dein CEO koordiniert Developer, Researcher, Marketing & Analyst</p>
  </div>
</header>

<div class="container">

  <!-- Organigramm -->
  <div class="org">
    <h2>📋 Dein Team</h2>
    <div class="ceo-box">👔 CEO – koordiniert alles</div>
    <div class="arrow">↓ delegiert an ↓</div>
    <div class="agents-grid" id="agentsGrid">
      <div class="agent-card selected" data-dept="auto" onclick="selectDept(this, 'auto')">
        <div class="icon">🧠</div>
        <div class="name">Automatisch</div>
        <div class="desc">CEO entscheidet selbst</div>
      </div>
    </div>
  </div>

  <!-- Aufgaben-Eingabe -->
  <div class="task-box">
    <h2>✏️ Aufgabe eingeben</h2>
    <div class="selected-agent" id="selectedLabel">🧠 CEO entscheidet automatisch, wer die Aufgabe übernimmt</div>
    <textarea id="taskInput" placeholder="z.B. Erstelle eine Landing Page für meine KI-Firma... oder: Schreib einen LinkedIn-Post über KI-Trends... oder: Analysiere die Konkurrenz im KI-Markt..."></textarea>
    <button class="btn" id="submitBtn" onclick="submitTask()">🚀 Aufgabe starten</button>
  </div>

  <!-- Ergebnis -->
  <div class="result-box" id="resultBox">
    <h2>📬 Ergebnis</h2>
    <div id="statusBadge" class="status-badge status-running"><span class="spinner">⟳</span> Agenten arbeiten...</div>
    <div class="result-content" id="resultContent"></div>
  </div>

</div>

<script>
let selectedDept = 'auto';
let pollInterval = null;

// Agenten laden
const agents = """ + str({k: {"label": v["label"], "beschreibung": v["beschreibung"]} for k, v in AVAILABLE_AGENTS.items()}).replace("True","true").replace("False","false") + """;

const grid = document.getElementById('agentsGrid');
for (const [dept, info] of Object.entries(agents)) {
  const card = document.createElement('div');
  card.className = 'agent-card';
  card.dataset.dept = dept;
  card.onclick = () => selectDept(card, dept);
  card.innerHTML = `
    <div class="icon">${info.label.split(' ')[0]}</div>
    <div class="name">${info.label.split(' ').slice(1).join(' ')}</div>
    <div class="desc">${info.beschreibung}</div>
  `;
  grid.appendChild(card);
}

function selectDept(el, dept) {
  document.querySelectorAll('.agent-card').forEach(c => c.classList.remove('selected'));
  el.classList.add('selected');
  selectedDept = dept;
  const label = document.getElementById('selectedLabel');
  if (dept === 'auto') {
    label.textContent = '🧠 CEO entscheidet automatisch, wer die Aufgabe übernimmt';
  } else {
    label.textContent = agents[dept].label + ' übernimmt die Aufgabe, CEO reviewed';
  }
}

async function submitTask() {
  const aufgabe = document.getElementById('taskInput').value.trim();
  if (!aufgabe) { alert('Bitte eine Aufgabe eingeben!'); return; }

  const btn = document.getElementById('submitBtn');
  btn.disabled = true;
  btn.textContent = '⏳ Agenten arbeiten...';

  const resultBox = document.getElementById('resultBox');
  resultBox.style.display = 'block';
  document.getElementById('statusBadge').className = 'status-badge status-running';
  document.getElementById('statusBadge').innerHTML = '<span class="spinner">⟳</span> Agenten arbeiten...';
  document.getElementById('resultContent').textContent = 'Dein Team analysiert die Aufgabe...\n\nDas kann 30–90 Sekunden dauern.';

  const resp = await fetch('/api/aufgabe', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ aufgabe, abteilung: selectedDept })
  });
  const { aufgabe_id } = await resp.json();

  pollInterval = setInterval(() => checkStatus(aufgabe_id), 3000);
}

async function checkStatus(id) {
  const resp = await fetch(`/api/aufgabe/${id}`);
  const data = await resp.json();

  if (data.status === 'done') {
    clearInterval(pollInterval);
    document.getElementById('statusBadge').className = 'status-badge status-done';
    document.getElementById('statusBadge').textContent = '✅ Fertig';
    document.getElementById('resultContent').textContent = data.ergebnis;
    const btn = document.getElementById('submitBtn');
    btn.disabled = false;
    btn.textContent = '🚀 Neue Aufgabe starten';
  } else if (data.status === 'fehler') {
    clearInterval(pollInterval);
    document.getElementById('statusBadge').className = 'status-badge status-error';
    document.getElementById('statusBadge').textContent = '❌ Fehler';
    document.getElementById('resultContent').textContent = data.ergebnis;
    const btn = document.getElementById('submitBtn');
    btn.disabled = false;
    btn.textContent = '🚀 Nochmal versuchen';
  }
}
</script>
</body>
</html>"""


# ── API ──────────────────────────────────────────────────────────────────────

class AufgabeRequest(BaseModel):
    aufgabe: str
    abteilung: str = "auto"


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML


@app.post("/api/aufgabe")
async def neue_aufgabe(req: AufgabeRequest, background_tasks: BackgroundTasks):
    aufgabe_id = str(uuid.uuid4())[:8]
    aufgaben[aufgabe_id] = {"status": "läuft", "ergebnis": None}
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
