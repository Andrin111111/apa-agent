"""
Startpunkt des Agent-Gerüsts.

  python main.py                                 # alle Meldungen, Regel-Baseline (ohne API-Key)
  python main.py --modus claude                  # alle Meldungen mit Claude
  python main.py --modus claude --fall P2P-1004  # nur ein Fall
"""
from __future__ import annotations

import argparse
import os
import sys

import daten
import evaluieren
from agent import bearbeite_fall, leerer_eintrag
from protokoll import Protokoll


def drucke_fall(e: dict) -> None:
    a = e["ausnahme"]
    print(f"\n[{e['case_id']}] {a['ausnahme_typ']}: {a.get('beschreibung', '')}")
    for s in e["schritte"]:
        if s["art"] == "tool":
            hinweis = "  -> ABGELEHNT: " + s["ergebnis"].get("fehler", "") if s["abgelehnt"] else ""
            print(f"   {s['schritt']}. {s['name']}{hinweis}")
        elif s["art"] == "erinnerung":
            print(f"   {s['schritt']}. (keine Massnahme gewählt, Agent wird erinnert)")
    m = e["massnahme"]
    if m:
        schluessel = [k for k in m["parameter"] if k != "nachricht"]
        status = evaluieren.STATUS_TEXT.get(m["status"], m["status"])
        print(f"   => {evaluieren.kurz(m['name'], m['parameter'], schluessel)} [{status}]")
        print(f"   Begründung: {m['begruendung']}")
    else:
        print(f"   => keine Massnahme ({e['status']})")
        if e.get("fehlermeldung"):
            print(f"   {e['fehlermeldung'][:300]}")


def main() -> None:
    try:  # Windows-Konsolen: unbekannte Sonderzeichen ersetzen statt abstürzen
        sys.stdout.reconfigure(errors="replace")
    except AttributeError:
        pass

    parser = argparse.ArgumentParser(description="Agentic Process Automation: Agent-Gerüst")
    parser.add_argument(
        "--modus", choices=["regel", "claude"], default="regel",
        help="regel = Baseline ohne KI (Standard), claude = Entscheidungen über die Claude API",
    )
    parser.add_argument("--fall", help="nur diese Fall-ID bearbeiten, z. B. P2P-1004")
    args = parser.parse_args()

    if args.modus == "claude":
        if not os.getenv("ANTHROPIC_API_KEY"):
            sys.exit("Kein ANTHROPIC_API_KEY gefunden. Kopiere .env.example nach .env und trage den Key ein.")
        from llm import ClaudeLLM

        llm = ClaudeLLM()
    else:
        from llm import RegelLLM

        llm = RegelLLM()

    meldungen = daten.ausnahmemeldungen()
    if args.fall:
        meldungen = [m for m in meldungen if m["case_id"] == args.fall]
        if not meldungen:
            sys.exit(f"Keine Meldung für {args.fall} in daten/ausnahmen.json.")

    protokoll = Protokoll(args.modus)
    print(f"Agent: {llm.name} | {len(meldungen)} Meldung(en)")
    for meldung in meldungen:
        try:
            eintrag = bearbeite_fall(meldung, llm)
        except Exception as fehler:  # z. B. API-Fehler: protokollieren, weiter mit dem nächsten Fall
            eintrag = leerer_eintrag(meldung, llm)
            eintrag["status"] = f"fehler: {type(fehler).__name__}"
            eintrag["fehlermeldung"] = str(fehler)
            if type(fehler).__name__ in ("AuthenticationError", "PermissionDeniedError"):
                protokoll.schreibe(eintrag)
                sys.exit(f"API-Zugang abgelehnt ({type(fehler).__name__}). Ist der API-Key in .env korrekt?")
        protokoll.schreibe(eintrag)
        drucke_fall(eintrag)

    print(f"\nProtokoll: {protokoll.pfad}\n")
    evaluieren.auswerten(protokoll.pfad)


if __name__ == "__main__":
    main()
