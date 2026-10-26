"""
Werkzeuge (Tools) des Agenten und Prüfung der Leitplanken.

  Info-Tools     Der Agent holt sich Informationen (nur lesen).
  Aktions-Tools  Der Handlungskatalog aus der Aufgabenstellung. Jede Aktion
                 verlangt eine Begründung und die ausschlaggebenden Fakten.

Die Aktionen sind im Gerüst simuliert: Sie werden nur protokolliert. Später
könnt ihr sie an echte Systeme anbinden (Ticket, E-Mail, Workflow-Engine).
"""
from __future__ import annotations

from dataclasses import dataclass

import config
import daten

# --- Tool-Definitionen (Format der Claude API) ----------------------------------

_CASE_ID = {"type": "string", "description": "Fall-ID aus der Meldung, z. B. P2P-1001"}

# Pflichtfelder jeder Aktion: machen die Entscheidung nachvollziehbar
_BEGRUENDUNG = {
    "begruendung": {
        "type": "string",
        "description": "Warum diese Massnahme? 1-3 Sätze mit Bezug auf die zutreffende Geschäftsregel.",
    },
    "entscheidende_fakten": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Fakten aus Meldung und Tool-Ergebnissen, die für die Entscheidung ausschlaggebend waren.",
    },
}


def _tool(name: str, beschreibung: str, felder: dict) -> dict:
    return {
        "name": name,
        "description": beschreibung,
        "input_schema": {"type": "object", "properties": felder, "required": list(felder)},
    }


def _aktion(name: str, beschreibung: str, felder: dict | None = None) -> dict:
    return _tool(name, beschreibung, {"case_id": _CASE_ID, **(felder or {}), **_BEGRUENDUNG})


INFO_TOOLS = [
    _tool(
        "fallverlauf_abrufen",
        "Liefert alle bisherigen Events des Falls in zeitlicher Reihenfolge (Aktivität, Zeitpunkt, "
        "Person, Rolle) sowie die Tage seit Fallstart und seit dem letzten Event, bezogen auf den Stichtag.",
        {"case_id": _CASE_ID},
    ),
    _tool(
        "fallkontext_abrufen",
        "Liefert Stammdaten zum Fall: Bezeichnung, Bestellwert, Lieferant, ob produktionskritisch, "
        "ob Rahmenvertrag, Zuständigkeit, offene Rückfragen und bisher gesendete Erinnerungen.",
        {"case_id": _CASE_ID},
    ),
    _tool(
        "prozesswissen_abrufen",
        "Liefert das Prozesswissen: Soll-Ablauf, SLA, typische Dauern, Rollen und die geltenden "
        "Geschäftsregeln (R1, R2, ...). Prüfe hier, welche Regel auf den Fall zutrifft.",
        {},
    ),
]

AKTIONS_TOOLS = [
    _aktion(
        "info_nachfordern",
        "Fordert fehlende Informationen an, z. B. mit einer Erinnerung an den Lieferanten.",
        {
            "empfaenger": {"type": "string", "enum": config.EMPFAENGER},
            "nachricht": {"type": "string", "description": "Kurzer Text der Anfrage"},
        },
    ),
    _aktion(
        "fall_priorisieren",
        "Erhöht die Priorität des Falls, damit er vor anderen bearbeitet wird.",
        {"prioritaet": {"type": "string", "enum": config.PRIORITAETEN}},
    ),
    _aktion(
        "eskalieren",
        "Eskaliert den Fall an eine verantwortliche Rolle. Wird nicht direkt ausgeführt, "
        "sondern einem Menschen zur Freigabe vorgelegt.",
        {"an_rolle": {"type": "string", "enum": config.ROLLEN, "description": "Rolle, an die eskaliert wird"}},
    ),
    _aktion(
        "neu_zuweisen",
        "Weist den Fall einer anderen Rolle zu.",
        {"neue_rolle": {"type": "string", "enum": config.ROLLEN, "description": "Rolle, die den Fall übernimmt"}},
    ),
    _aktion(
        "naechsten_schritt_empfehlen",
        "Empfiehlt der zuständigen Person den nächsten Prozessschritt.",
        {"aktivitaet": {"type": "string", "description": "Aktivität aus dem Soll-Ablauf, z. B. 'Create Purchase Order'"}},
    ),
    _aktion(
        "keine_massnahme",
        "Schliesst die Meldung ohne Massnahme ab, z. B. bei einem Fehlalarm oder wenn der Fall planmässig läuft.",
    ),
]

TOOLS = INFO_TOOLS + AKTIONS_TOOLS
AKTIONEN = {t["name"] for t in AKTIONS_TOOLS}


# --- Ausführung und Leitplanken -------------------------------------------------


@dataclass
class ToolErgebnis:
    inhalt: dict  # geht als Tool-Ergebnis zurück an das Modell
    fehler: bool = False
    massnahme: dict | None = None  # gesetzt, sobald eine Aktion ausgeführt wurde


def _abgelehnt(grund: str) -> ToolErgebnis:
    return ToolErgebnis({"fehler": grund}, fehler=True)


class Werkzeugkasten:
    """Führt die Tool-Aufrufe für genau eine Meldung aus und setzt die Leitplanken durch."""

    def __init__(self, meldung: dict):
        self.case_id = meldung["case_id"]
        self.typ = meldung["ausnahme_typ"]
        self.erlaubt = config.ERLAUBTE_MASSNAHMEN.get(self.typ, ["keine_massnahme"])
        self.massnahme_gewaehlt = False

    def ausfuehren(self, name: str, eingabe: dict) -> ToolErgebnis:
        if name == "prozesswissen_abrufen":
            return ToolErgebnis(daten.prozesswissen())
        if name not in AKTIONEN and name not in ("fallverlauf_abrufen", "fallkontext_abrufen"):
            return _abgelehnt(f"Unbekanntes Tool '{name}'.")
        if eingabe.get("case_id") != self.case_id:
            return _abgelehnt(f"Nur der Fall aus der Meldung ({self.case_id}) darf bearbeitet werden.")
        if name == "fallverlauf_abrufen":
            return self._fallverlauf()
        if name == "fallkontext_abrufen":
            return ToolErgebnis(daten.fallkontext().get(self.case_id, {"hinweis": "Kein Kontext vorhanden."}))
        return self._aktion(name, eingabe)

    def _fallverlauf(self) -> ToolErgebnis:
        events = daten.event_log().get(self.case_id)
        if not events:
            return _abgelehnt(f"Keine Events für {self.case_id} im Event Log.")
        verlauf, vorher = [], None
        for e in events:
            verlauf.append({
                "aktivitaet": e["activity"],
                "zeitpunkt": e["timestamp"],
                "person": e["resource"],
                "rolle": e["role"],
                "tage_seit_vorherigem_event": daten.tage_zwischen(vorher, e["timestamp"]) if vorher else 0.0,
            })
            vorher = e["timestamp"]
        return ToolErgebnis({
            "case_id": self.case_id,
            "stichtag": config.STICHTAG,
            "tage_seit_fallstart": daten.tage_zwischen(events[0]["timestamp"], config.STICHTAG),
            "tage_seit_letztem_event": daten.tage_zwischen(vorher, config.STICHTAG),
            "events": verlauf,
        })

    def _aktion(self, name: str, eingabe: dict) -> ToolErgebnis:
        if self.massnahme_gewaehlt:
            return _abgelehnt("Für diesen Fall wurde bereits eine Massnahme gewählt. Pro Fall ist nur eine erlaubt.")
        if name not in self.erlaubt:
            return _abgelehnt(
                f"'{name}' liegt für {self.typ} nicht im Handlungsspielraum. Erlaubt: {', '.join(self.erlaubt)}."
            )
        problem = _pruefe_felder(name, eingabe)
        if problem:
            return _abgelehnt(problem)

        self.massnahme_gewaehlt = True
        status = "zur_freigabe" if name in config.FREIGABEPFLICHTIG else "ausgefuehrt_simuliert"
        massnahme = {
            "name": name,
            "parameter": {
                k: v for k, v in eingabe.items() if k not in ("case_id", "begruendung", "entscheidende_fakten")
            },
            "begruendung": eingabe["begruendung"],
            "entscheidende_fakten": eingabe["entscheidende_fakten"],
            "status": status,
        }
        return ToolErgebnis({"ok": True, "massnahme": name, "status": status}, massnahme=massnahme)


def _pruefe_felder(name: str, eingabe: dict) -> str | None:
    """Prüft die Eingaben einer Aktion. Gibt den Ablehnungsgrund zurück oder None."""
    if not str(eingabe.get("begruendung", "")).strip():
        return "Begründung fehlt."
    fakten = eingabe.get("entscheidende_fakten")
    if not isinstance(fakten, list) or not any(str(f).strip() for f in fakten):
        return "Mindestens ein ausschlaggebender Fakt ist nötig."

    feste_werte = {
        "info_nachfordern": ("empfaenger", config.EMPFAENGER),
        "fall_priorisieren": ("prioritaet", config.PRIORITAETEN),
        "eskalieren": ("an_rolle", config.ROLLEN),
        "neu_zuweisen": ("neue_rolle", config.ROLLEN),
    }
    if name in feste_werte:
        feld, erlaubt = feste_werte[name]
        if eingabe.get(feld) not in erlaubt:
            return f"Ungültiger Wert für '{feld}'. Erlaubt: {', '.join(erlaubt)}."
    if name == "info_nachfordern" and not str(eingabe.get("nachricht", "")).strip():
        return "Nachricht fehlt."
    if name == "naechsten_schritt_empfehlen":
        pw = daten.prozesswissen()
        if eingabe.get("aktivitaet") not in pw["soll_ablauf"] + pw["weitere_aktivitaeten"]:
            return "Unbekannte Aktivität. Nutze eine Aktivität aus dem Soll-Ablauf (siehe prozesswissen_abrufen)."
    return None
