"""
Die Agent-Schleife: beobachten -> überlegen -> Tool aufrufen -> Ergebnis prüfen -> wiederholen.

Pro Ausnahmemeldung läuft die Schleife, bis der Agent genau eine Massnahme aus
dem Handlungskatalog gewählt hat oder eine Leitplanke die Bearbeitung beendet.
Jeder Schritt landet im Protokolleintrag, den die Funktion zurückgibt.
"""
from __future__ import annotations

import json
import time

import config
from tools import TOOLS, Werkzeugkasten

SYSTEM_PROMPT = """Du bist ein KI-Agent für die Bearbeitung von Ausnahmefällen im Beschaffungsprozess (Procure-to-Pay) eines Unternehmens.

Du erhältst jeweils eine Ausnahmemeldung aus der Prozessüberwachung zu genau einem Fall. So gehst du vor:
1. Verschaffe dir mit den Info-Tools ein Bild: bisheriger Fallverlauf, Fallkontext und Prozesswissen (Soll-Ablauf, SLA, Geschäftsregeln). Rufe ab, was du für eine fundierte Entscheidung brauchst.
2. Prüfe, ob die Meldung berechtigt ist. Meldungen können Fehlalarme sein, zum Beispiel wenn ein Fall planmässig wartet.
3. Wähle genau EINE Massnahme aus dem Handlungskatalog (die Aktions-Tools). Ist nichts zu tun, wähle keine_massnahme.
4. Begründe die Massnahme knapp mit Bezug auf die zutreffende Geschäftsregel und nenne die ausschlaggebenden Fakten.

Leitplanken:
- Stütze dich ausschliesslich auf die Meldung und die Tool-Ergebnisse. Erfinde keine Fakten.
- Handle nur im Fall aus der Meldung.
- Wird eine Massnahme abgelehnt, wähle eine erlaubte Alternative.
- Schreibe Begründungen auf Deutsch."""

ERINNERUNG = "Bitte schliesse den Fall ab, indem du genau eines der Aktions-Tools aufrufst (bei Bedarf keine_massnahme)."


def fall_nachricht(meldung: dict) -> str:
    """Erste Nachricht an den Agenten: die Meldung plus der erlaubte Handlungsspielraum."""
    erlaubt = config.ERLAUBTE_MASSNAHMEN.get(meldung["ausnahme_typ"], ["keine_massnahme"])
    return (
        "Neue Ausnahmemeldung aus der Prozessüberwachung:\n\n"
        + json.dumps(meldung, ensure_ascii=False, indent=2)
        + f"\n\nErlaubte Massnahmen für den Typ {meldung['ausnahme_typ']}: {', '.join(erlaubt)}.\n"
        + "Prüfe den Fall und entscheide."
    )


def leerer_eintrag(meldung: dict, llm) -> dict:
    return {
        "case_id": meldung["case_id"],
        "ausnahme": meldung,
        "agent": llm.name,
        "modell": llm.modell,
        "status": "abgebrochen_max_schritte",
        "massnahme": None,
        "schritte": [],
        "modell_antworten": 0,
        "abgelehnte_aufrufe": 0,
        "tokens_in": 0,
        "tokens_out": 0,
        "dauer_s": 0.0,
    }


def bearbeite_fall(meldung: dict, llm) -> dict:
    """Bearbeitet eine Ausnahmemeldung und gibt den vollständigen Ablauf als Protokolleintrag zurück."""
    start = time.perf_counter()
    llm.neuer_fall(meldung)
    werkzeuge = Werkzeugkasten(meldung)
    verlauf = [{"role": "user", "content": fall_nachricht(meldung)}]
    eintrag = leerer_eintrag(meldung, llm)

    for nr in range(1, config.MAX_SCHRITTE + 1):
        # 1. Überlegen: Das Modell entscheidet, welche Tools es aufruft
        antwort = llm.antworte(SYSTEM_PROMPT, verlauf, TOOLS)
        verlauf.append({"role": "assistant", "content": antwort.inhalt})
        eintrag["modell_antworten"] = nr
        eintrag["tokens_in"] += antwort.tokens_in
        eintrag["tokens_out"] += antwort.tokens_out
        for text in antwort.gedanken:
            eintrag["schritte"].append({"schritt": nr, "art": "gedanke", "text": text})
        for text in antwort.texte:
            eintrag["schritte"].append({"schritt": nr, "art": "text", "text": text})

        if not antwort.tool_aufrufe:
            if antwort.stop_grund == "max_tokens":
                eintrag["status"] = "abgebrochen_max_tokens"
                break
            # Das Modell hat ohne Massnahme aufgehört: an den Auftrag erinnern
            verlauf.append({"role": "user", "content": ERINNERUNG})
            eintrag["schritte"].append({"schritt": nr, "art": "erinnerung", "text": ERINNERUNG})
            continue

        # 2. Handeln: Tools ausführen, Leitplanken prüfen, Ergebnisse zurückgeben
        ergebnisse = []
        for aufruf in antwort.tool_aufrufe:
            ergebnis = werkzeuge.ausfuehren(aufruf.name, aufruf.eingabe)
            if ergebnis.fehler:
                eintrag["abgelehnte_aufrufe"] += 1
            if ergebnis.massnahme:
                eintrag["massnahme"] = ergebnis.massnahme
            eintrag["schritte"].append({
                "schritt": nr,
                "art": "tool",
                "name": aufruf.name,
                "eingabe": aufruf.eingabe,
                "ergebnis": ergebnis.inhalt,
                "abgelehnt": ergebnis.fehler,
            })
            block = {
                "type": "tool_result",
                "tool_use_id": aufruf.id,
                "content": json.dumps(ergebnis.inhalt, ensure_ascii=False),
            }
            if ergebnis.fehler:
                block["is_error"] = True
            ergebnisse.append(block)
        verlauf.append({"role": "user", "content": ergebnisse})

        # 3. Fertig, sobald genau eine Massnahme gewählt ist
        if eintrag["massnahme"]:
            eintrag["status"] = "entschieden"
            break

    eintrag["dauer_s"] = round(time.perf_counter() - start, 2)
    return eintrag
