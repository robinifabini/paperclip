import os
import json
import requests
from datetime import datetime, timedelta
from typing import Optional
import google.generativeai as genai

# ── Config ──────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
PAPERS_TOPIC   = os.environ.get("PAPERS_TOPIC", "machine learning")
MAX_PAPERS     = int(os.environ.get("MAX_PAPERS", "5"))
OUTPUT_FILE    = "output/digest.json"

# ── Gemini setup ─────────────────────────────────────────────────────────────
def get_gemini_model():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY env var missing")
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel("gemini-2.0-flash")

# ── Fetch papers from paperswithcode ────────────────────────────────────────
def fetch_papers(topic: str, days_back: int = 7) -> list[dict]:
    print(f"[paperswithcode] Fetching papers on '{topic}' ...")
    url = "https://paperswithcode.com/api/v1/papers/"
    params = {
        "q": topic,
        "ordering": "-published",
        "items_per_page": MAX_PAPERS,
        "page": 1,
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        results = r.json().get("results", [])
        print(f"  → {len(results)} papers found")
        return results
    except Exception as e:
        print(f"  ✗ Error fetching papers: {e}")
        return []

# ── Summarise a single paper with Gemini ─────────────────────────────────────
def summarise_paper(model, paper: dict) -> Optional[str]:
    title    = paper.get("title", "Unknown")
    abstract = paper.get("abstract", "")
    if not abstract:
        return None

    prompt = f"""You are a research assistant. Summarise this ML/AI paper in 3 bullet points 
(each max 2 sentences). Be concrete – mention the key method and the key result.

Title: {title}
Abstract: {abstract}

Return ONLY the 3 bullet points, no preamble."""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"  ✗ Gemini error for '{title}': {e}")
        return None

# ── Build digest ──────────────────────────────────────────────────────────────
def build_digest(papers: list[dict], model) -> dict:
    digest = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "topic": PAPERS_TOPIC,
        "papers": [],
    }

    for i, paper in enumerate(papers, 1):
        title   = paper.get("title", "Unknown")
        url     = paper.get("url_abs") or f"https://paperswithcode.com/paper/{paper.get('id','')}"
        authors = [a.get("name","") for a in paper.get("authors", [])][:3]

        print(f"[{i}/{len(papers)}] Summarising: {title[:60]}...")
        summary = summarise_paper(model, paper)

        digest["papers"].append({
            "title":   title,
            "url":     url,
            "authors": authors,
            "summary": summary or "Summary unavailable.",
        })

    return digest

# ── Save output ───────────────────────────────────────────────────────────────
def save_digest(digest: dict):
    os.makedirs("output", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(digest, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Digest saved to {OUTPUT_FILE}")
    _print_digest(digest)

def _print_digest(digest: dict):
    print(f"\n{'═'*60}")
    print(f"📚 Paper Digest – {digest['topic'].upper()}")
    print(f"Generated: {digest['generated_at']}")
    print(f"{'═'*60}")
    for p in digest["papers"]:
        print(f"\n📄 {p['title']}")
        if p["authors"]:
            print(f"   Authors: {', '.join(p['authors'])}")
        print(f"   URL: {p['url']}")
        print(f"   Summary:\n{p['summary']}")

# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    print("🚀 PaperClub AI – starting digest generation")
    model  = get_gemini_model()
    papers = fetch_papers(PAPERS_TOPIC)
    if not papers:
        print("No papers found. Exiting.")
        return
    digest = build_digest(papers, model)
    save_digest(digest)

if __name__ == "__main__":
    main()
