from crewai import Task, Crew, Process
from agents import ceo_agent, AVAILABLE_AGENTS


def run_task(aufgabe: str, abteilung: str = "auto") -> str:
    """
    Führt eine Aufgabe aus.
    - abteilung="auto": CEO analysiert und delegiert selbst
    - abteilung="developer" / "researcher" / etc.: Direkt an diese Abteilung
    """
    ceo = ceo_agent()

    if abteilung == "auto" or abteilung not in AVAILABLE_AGENTS:
        # CEO entscheidet selbst, wer die Aufgabe übernimmt
        alle_agenten = [ceo] + [info["fn"]() for info in AVAILABLE_AGENTS.values()]

        ceo_task = Task(
            description=f"""
Ein Kunde hat folgende Anfrage gestellt:

"{aufgabe}"

Als CEO:
1. Analysiere was für eine Aufgabe das ist
2. Entscheide welche Teammitglieder du einsetzen willst
3. Koordiniere die Arbeit
4. Liefere ein vollständiges, poliertes Ergebnis an den Kunden
            """,
            expected_output=(
                "Ein vollständiges, gut strukturiertes Ergebnis auf die Anfrage des Kunden. "
                "Auf Deutsch, es sei denn, der Kunde schreibt auf Englisch."
            ),
            agent=ceo,
        )

        crew = Crew(
            agents=alle_agenten,
            tasks=[ceo_task],
            process=Process.sequential,
            verbose=True,
        )

    else:
        # Direkt an eine bestimmte Abteilung + CEO Review
        mitarbeiter = AVAILABLE_AGENTS[abteilung]["fn"]()

        arbeit_task = Task(
            description=aufgabe,
            expected_output="Eine detaillierte, hochwertige Antwort auf die Aufgabe.",
            agent=mitarbeiter,
        )

        review_task = Task(
            description=(
                f"Überprüfe und verfeinere das Ergebnis deines {mitarbeiter.role}. "
                "Stelle sicher, dass es die Erwartungen des Kunden erfüllt und "
                "präsentiere es in einer klaren, professionellen Form."
            ),
            expected_output="Eine finale, kundenfertige Version der Arbeit.",
            agent=ceo,
        )

        crew = Crew(
            agents=[mitarbeiter, ceo],
            tasks=[arbeit_task, review_task],
            process=Process.sequential,
            verbose=True,
        )

    ergebnis = crew.kickoff()
    return str(ergebnis)
