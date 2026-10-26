"""
Evaluation: Vergleicht die Entscheidungen eines Laufs mit den erwarteten
Massnahmen (Ground Truth) und misst Korrektheit, Nachvollziehbarkeit und Aufwand.
Schreibt zusätzlich einen lesbaren Bericht (.md) neben das Protokoll, z. B. für
den Anhang oder die Präsentation.

  python evaluieren.py                              # neuester Lauf
  python evaluieren.py protokolle/lauf_<...>.jsonl  # bestimmter Lauf
"""
from __future__ import annotations

import sys
from pathlib import Path

import config
import daten
from protokoll import lies

STATUS_TEXT = {
    "ausgefuehrt_simuliert": "ausgeführt (simuliert)",
    "zur_freigabe": "zur Freigabe an einen Menschen",
}


def kurz(name: str | None, parameter: dict | None, schluessel: list[str]) -> str:
    """Massnahme kompakt, z. B. 'eskalieren: Einkaufsleitung'."""
    if not name:
        return "-"
    parameter = parameter or {}
    werte = [str(parameter[k]) for k in schluessel if parameter.get(k) is not None]
    return f"{name}: {', '.join(werte)}" if werte else name


def ist_korrekt(massnahme: dict | None, soll: dict) -> bool:
    """Richtige Massnahme und, wo vorgegeben, richtige Parameter (z. B. Rolle)."""
    if not massnahme or massnahme["name"] != soll["massnahme"]:
        return False
    return all(massnahme["parameter"].get(k) == v for k, v in soll.get("parameter", {}).items())


def ist_nachvollziehbar(massnahme: dict | None) -> bool:
    return bool(
        massnahme and str(massnahme.get("begruendung", "")).strip() and massnahme.get("entscheidende_fakten")
    )


def auswerten(pfad) -> dict:
    pfad = Path(pfad)
    eintraege = lies(pfad)
    soll_alle = daten.erwartete_massnahmen()

    zeilen = []
    for e in eintraege:
        soll = soll_alle.get(e["case_id"])
        m = e.get("massnahme")
        schluessel = list(soll.get("parameter", {})) if soll else []
        if m and (not soll or m["name"] != soll["massnahme"]):
            schluessel = [s for s in m["parameter"] if s != "nachricht"]  # andere Massnahme: eigene Werte zeigen
        zeilen.append({
            "fall": e["case_id"],
            "typ": e["ausnahme"]["ausnahme_typ"],
            "erwartet": kurz(soll["massnahme"], soll.get("parameter"), list(soll.get("parameter", {}))) if soll else "-",
            "gewaehlt": kurz(m["name"], m["parameter"], schluessel) if m else "- (" + e["status"] + ")",
            "korrekt": None if not soll else ist_korrekt(m, soll),
        })

    bewertet = [z for z in zeilen if z["korrekt"] is not None]
    korrekt = sum(1 for z in bewertet if z["korrekt"])
    k = {
        "faelle": len(eintraege),
        "bewertet": len(bewertet),
        "korrekt": korrekt,
        "quote_prozent": round(100 * korrekt / len(bewertet)) if bewertet else 0,
        "nachvollziehbar": sum(1 for e in eintraege if ist_nachvollziehbar(e.get("massnahme"))),
        "abgelehnte_aufrufe": sum(e.get("abgelehnte_aufrufe", 0) for e in eintraege),
        "modell_antworten_schnitt": round(
            sum(e.get("modell_antworten", 0) for e in eintraege) / max(len(eintraege), 1), 1
        ),
        "tokens_in": sum(e.get("tokens_in", 0) for e in eintraege),
        "tokens_out": sum(e.get("tokens_out", 0) for e in eintraege),
    }
    modell = next((e.get("modell") for e in eintraege if e.get("modell")), None)
    if modell in config.PREISE:
        preis_in, preis_out = config.PREISE[modell]
        k["kosten_usd"] = round(k["tokens_in"] / 1e6 * preis_in + k["tokens_out"] / 1e6 * preis_out, 3)

    print(f"Auswertung {pfad.stem}")
    _drucke_tabelle(zeilen)
    zusammenfassung = (
        f"Korrekt: {k['korrekt']}/{k['bewertet']} ({k['quote_prozent']} %) | "
        f"nachvollziehbar begründet: {k['nachvollziehbar']}/{k['faelle']} | "
        f"abgelehnte Aufrufe: {k['abgelehnte_aufrufe']} | "
        f"Ø Modell-Antworten pro Fall: {k['modell_antworten_schnitt']}"
    )
    if k["tokens_in"] or k["tokens_out"]:
        zusammenfassung += f" | Tokens: {k['tokens_in']} in / {k['tokens_out']} out"
        if "kosten_usd" in k:
            zusammenfassung += f" | Kosten: ca. {k['kosten_usd']} USD"
    print("\n" + zusammenfassung)
    print(f"Bericht: {_schreibe_bericht(pfad, eintraege, zeilen, k, soll_alle)}")
    return k


def _korrekt_text(wert) -> str:
    return "-" if wert is None else ("ja" if wert else "NEIN")


def _drucke_tabelle(zeilen: list[dict]) -> None:
    if not zeilen:
        print("Keine Fälle im Protokoll.")
        return
    kopf = {"fall": "Fall", "typ": "Typ", "erwartet": "Erwartet", "gewaehlt": "Gewählt", "korrekt": "Korrekt"}
    zellen = [{**z, "korrekt": _korrekt_text(z["korrekt"])} for z in zeilen]
    breite = {s: max(len(kopf[s]), max(len(z[s]) for z in zellen)) for s in kopf}
    print("  ".join(kopf[s].ljust(breite[s]) for s in kopf))
    for z in zellen:
        print("  ".join(z[s].ljust(breite[s]) for s in kopf))


def _schreibe_bericht(pfad: Path, eintraege: list[dict], zeilen: list[dict], k: dict, soll_alle: dict) -> Path:
    agent = eintraege[0]["agent"] if eintraege else "-"
    md = [
        f"# Auswertung {pfad.stem}",
        "",
        f"**Agent:** {agent}",
        "",
        f"**Korrekt:** {k['korrekt']}/{k['bewertet']} ({k['quote_prozent']} %) · "
        f"**nachvollziehbar begründet:** {k['nachvollziehbar']}/{k['faelle']} · "
        f"**abgelehnte Aufrufe:** {k['abgelehnte_aufrufe']} · "
        f"**Ø Modell-Antworten pro Fall:** {k['modell_antworten_schnitt']}",
        "",
        "| Fall | Typ | Erwartet | Gewählt | Korrekt |",
        "|---|---|---|---|---|",
    ]
    for z in zeilen:
        md.append(f"| {z['fall']} | {z['typ']} | {z['erwartet']} | {z['gewaehlt']} | {_korrekt_text(z['korrekt'])} |")
    md += ["", "## Entscheidungen im Detail"]

    for e in eintraege:
        a = e["ausnahme"]
        md += ["", f"### {e['case_id']} ({a['ausnahme_typ']})", "", f"**Meldung:** {a.get('beschreibung', '')}", ""]
        soll = soll_alle.get(e["case_id"])
        if soll:
            erwartet = kurz(soll["massnahme"], soll.get("parameter"), list(soll.get("parameter", {})))
            md += [f"**Erwartet:** `{erwartet}`. {soll.get('warum', '')}", ""]
        tools = [s["name"] + (" (abgelehnt)" if s["abgelehnt"] else "") for s in e["schritte"] if s["art"] == "tool"]
        md += ["**Tool-Aufrufe:** " + (" → ".join(tools) if tools else "-"), ""]
        ueberlegungen = [s["text"] for s in e["schritte"] if s["art"] in ("gedanke", "text")]
        if ueberlegungen:
            md += ["**Überlegungen des Agenten:**", ""]
            for text in ueberlegungen:
                md += ["> " + text.replace("\n", "\n> "), ""]
        m = e.get("massnahme")
        if m:
            schluessel = [s for s in m["parameter"] if s != "nachricht"]
            status = STATUS_TEXT.get(m["status"], m["status"])
            md += [f"**Massnahme:** `{kurz(m['name'], m['parameter'], schluessel)}`, {status}", ""]
            if m["parameter"].get("nachricht"):
                md += [f"**Nachricht:** {m['parameter']['nachricht']}", ""]
            md += [f"**Begründung:** {m['begruendung']}", "", "**Ausschlaggebende Fakten:**", ""]
            md += [f"- {fakt}" for fakt in m["entscheidende_fakten"]]
        else:
            md.append(f"**Keine Massnahme gewählt** (Status: {e['status']})")

    ziel = pfad.with_suffix(".md")
    ziel.write_text("\n".join(md) + "\n", encoding="utf-8")
    return ziel


if __name__ == "__main__":
    if len(sys.argv) > 1:
        auswerten(sys.argv[1])
    else:
        laeufe = sorted(config.PROTOKOLLE.glob("lauf_*.jsonl"))
        if not laeufe:
            sys.exit("Noch keine Läufe im Ordner protokolle/. Zuerst: python main.py")
        auswerten(laeufe[-1])
