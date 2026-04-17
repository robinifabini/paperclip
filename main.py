"""
KI-Firma – Einstiegspunkt

Starte den Web-Server:
  uvicorn main:app --host 0.0.0.0 --port 10000

Oder direkt eine Aufgabe per CLI:
  python main.py "Erstelle eine Landing Page für meine KI-Firma"
"""
import sys
from server import app  # noqa – exportiert für uvicorn

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # CLI-Modus
        from crew import run_task
        aufgabe = " ".join(sys.argv[1:])
        print(f"\n🚀 Aufgabe: {aufgabe}\n")
        ergebnis = run_task(aufgabe)
        print(f"\n✅ Ergebnis:\n{ergebnis}")
    else:
        # Server-Modus
        import uvicorn
        uvicorn.run("server:app", host="0.0.0.0", port=10000, reload=False)
