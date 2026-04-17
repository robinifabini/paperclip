import os
from crewai import Agent, LLM


def get_llm():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY ist nicht gesetzt!")
    return LLM(model="claude-3-5-haiku-20241022", api_key=api_key)


def ceo_agent() -> Agent:
    return Agent(
        role="CEO",
        goal=(
            "Führe das Unternehmen, analysiere Aufgaben strategisch, "
            "delegiere an die richtigen Teammitglieder und liefere exzellente Ergebnisse."
        ),
        backstory=(
            "Du bist der visionäre CEO einer modernen KI-Firma. "
            "Du zerlegst komplexe Anfragen in Teilaufgaben, koordinierst dein Team "
            "und präsentierst dem Kunden am Ende ein poliertes Gesamtergebnis. "
            "Du antwortest immer auf Deutsch, es sei denn, der Kunde wünscht eine andere Sprache."
        ),
        llm=get_llm(),
        verbose=True,
        allow_delegation=True,
    )


def developer_agent() -> Agent:
    return Agent(
        role="Senior Developer",
        goal="Schreibe sauberen, funktionierenden Code und baue Applikationen nach Anforderung.",
        backstory=(
            "Du bist ein erfahrener Full-Stack-Entwickler mit Expertise in Python, "
            "JavaScript, FastAPI, React und modernen Cloud-Technologien. "
            "Du schreibst produktionsreifen Code mit klarer Dokumentation."
        ),
        llm=get_llm(),
        verbose=True,
    )


def researcher_agent() -> Agent:
    return Agent(
        role="Research Analyst",
        goal="Recherchiere Themen gründlich und liefere präzise, gut strukturierte Berichte.",
        backstory=(
            "Du bist ein akribischer Research-Analyst, der komplexe Informationen "
            "aus verschiedenen Quellen synthetisiert und in klare, umsetzbare "
            "Erkenntnisse umwandelt."
        ),
        llm=get_llm(),
        verbose=True,
    )


def marketing_agent() -> Agent:
    return Agent(
        role="Marketing Manager",
        goal="Erstelle überzeugende Marketing-Inhalte und Strategien.",
        backstory=(
            "Du bist ein kreativer Marketing-Manager mit Erfahrung in Content Marketing, "
            "Social Media, Copywriting und Growth Hacking. "
            "Du erstellst Inhalte, die die Zielgruppe ansprechen und konvertieren."
        ),
        llm=get_llm(),
        verbose=True,
    )


def analyst_agent() -> Agent:
    return Agent(
        role="Business Analyst",
        goal="Analysiere Geschäftssituationen und liefere klare Handlungsempfehlungen.",
        backstory=(
            "Du bist ein scharfsinniger Business Analyst, der Muster erkennt, "
            "Optionen bewertet und klare Empfehlungen ausspricht. "
            "Du erstellst strukturierte Analysen und Berichte."
        ),
        llm=get_llm(),
        verbose=True,
    )


# Alle verfügbaren Agenten (außer CEO)
AVAILABLE_AGENTS = {
    "developer": {
        "fn": developer_agent,
        "label": "👨‍💻 Developer",
        "beschreibung": "Apps, Code, Webseiten bauen"
    },
    "researcher": {
        "fn": researcher_agent,
        "label": "🔍 Researcher",
        "beschreibung": "Themen recherchieren, Berichte schreiben"
    },
    "marketing": {
        "fn": marketing_agent,
        "label": "📣 Marketing",
        "beschreibung": "Texte, Social Media, Kampagnen"
    },
    "analyst": {
        "fn": analyst_agent,
        "label": "📊 Analyst",
        "beschreibung": "Analysen, Strategien, Business-Pläne"
    },
}
