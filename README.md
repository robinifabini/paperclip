# PaperClub AI 🤖📚

Automatically fetches AI/ML papers from paperswithcode.com, summarises them with **Gemini 2.0 Flash** (free tier), and serves a clean web digest.

## Setup (5 minutes)

### 1. Get a free Gemini API Key
1. Go to https://aistudio.google.com/apikey
2. Click **Create API Key**
3. Copy the key

### 2. Push to GitHub
```bash
git init
git add .
git commit -m "Initial PaperClub AI"
git remote add origin https://github.com/YOUR_USERNAME/paperclub-ai
git push -u origin main
```

### 3. Deploy on Railway
1. Go to https://railway.app → New Project → GitHub Repo
2. Select this repo
3. Go to **Variables** and add:

| Variable | Value |
|---|---|
| `GEMINI_API_KEY` | your key from step 1 |
| `PAPERS_TOPIC` | e.g. `machine learning` or `computer vision` |
| `MAX_PAPERS` | `5` (free tier) |
| `RUN_ON_START` | `true` |

4. Click **Deploy** → Railway builds and starts the app

### 4. Open your app
Railway gives you a public URL like `https://paperclub-ai-production.up.railway.app`

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | required | Google AI Studio key |
| `PAPERS_TOPIC` | `machine learning` | Search topic |
| `MAX_PAPERS` | `5` | Papers per digest |
| `CRON_HOUR` | `8` | UTC hour to run daily |
| `CRON_MINUTE` | `0` | Minute to run |
| `RUN_ON_START` | `true` | Run digest on deploy |

## API Endpoints

- `GET /` – Web digest (human-readable)
- `GET /api/digest` – JSON digest (for integrations)
- `GET /health` – Health check

## Optional: Add Claude API
Set `ANTHROPIC_API_KEY` and switch `summarise_paper()` in `main.py` to use Claude Haiku for higher quality summaries.
