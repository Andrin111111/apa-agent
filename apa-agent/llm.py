"""
Das «Gehirn» des Agenten, austauschbar.

  ClaudeLLM  Echtes Sprachmodell über die Claude API (braucht einen API-Key).
  RegelLLM   Baseline ohne KI: wählt pro Ausnahmetyp stur dieselbe Massnahme
             («starre Regel»). Läuft ohne API-Key und dient als Vergleich in
             der Evaluation: Was bringt der Agent gegenüber festen Regeln?

Beide liefern dieselbe Antwort-Struktur. So muss die Agent-Schleife (agent.py)
nicht wissen, welches Gehirn dahintersteckt. Ein weiteres Modell (z. B. OpenAI
oder lokal) bindet ihr an, indem ihr eine dritte Klasse mit denselben zwei
Methoden schreibt: neuer_fall() und antworte().
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import config


@dataclass
class ToolAufruf:
    id: str
    name: str
    eingabe: dict


@dataclass
class Antwort:
    inhalt: list[Any]  # geht UNVERÄNDERT zurück in den Gesprächsverlauf
    tool_aufrufe: list[ToolAufruf]
    texte: list[str] = field(default_factory=list)  # sichtbarer Text des Modells
    gedanken: list[str] = field(default_factory=list)  # Zusammenfassung des Denkprozesses
    stop_grund: str = ""
    tokens_in: int = 0
    tokens_out: int = 0


class ClaudeLLM:
    def __init__(self, modell: str = config.MODELL):
        import anthropic  # erst hier: der Regel-Modus braucht das Paket nicht

        self.client = anthropic.Anthropic()  # liest ANTHROPIC_API_KEY aus der Umgebung
        self.modell = modell
        self.name = f"Claude ({modell})"

    def neuer_fall(self, meldung: dict) -> None:
        pass  # nichts vorzubereiten: alles Nötige steht im Gesprächsverlauf

    def antworte(self, system: str, verlauf: list, tools: list) -> Antwort:
        anfrage = {
            "model": self.modell,
            "max_tokens": config.MAX_TOKENS,
            "system": system,
            "tools": tools,
            "messages": verlauf,
        }
        if config.THINKING:
            anfrage["thinking"] = config.THINKING
        if config.EFFORT:
            anfrage["output_config"] = {"effort": config.EFFORT}
        # Hinweis: temperature & Co. setzen die aktuellen Modelle nicht mehr
        # (400-Fehler), und Tool-Aufrufe lassen sich nicht erzwingen.
        r = self.client.messages.create(**anfrage)

        tool_aufrufe, texte, gedanken = [], [], []
        for block in r.content:
            if block.type == "tool_use":
                tool_aufrufe.append(ToolAufruf(block.id, block.name, dict(block.input)))
            elif block.type == "text" and block.text.strip():
                texte.append(block.text.strip())
            elif block.type == "thinking" and block.thinking.strip():
                gedanken.append(block.thinking.strip())
        return Antwort(
            # Nicht umbauen: Denk-Blöcke müssen unverändert zurück an die API.
            inhalt=r.content,
            tool_aufrufe=tool_aufrufe,
            texte=texte,
            gedanken=gedanken,
            stop_grund=r.stop_reason or "",
            tokens_in=r.usage.input_tokens,
            tokens_out=r.usage.output_tokens,
        )


class RegelLLM:
    """Baseline ohne KI: feste Regel «Ausnahmetyp -> Massnahme», ohne Blick auf den Kontext."""

    REGELN = {
        "VERZOEGERUNG": ("fall_priorisieren", {"prioritaet": "hoch"}),
        "FEHLENDE_INFO": (
            "info_nachfordern",
            {"empfaenger": "Lieferant", "nachricht": "Bitte senden Sie uns die angefragten Informationen."},
        ),
        "REWORK": ("neu_zuweisen", {"neue_rolle": "Senior-Einkauf"}),
        "ABWEICHUNG": ("eskalieren", {"an_rolle": "Compliance"}),
    }

    def __init__(self):
        self.modell = None
        self.name = "Regel-Baseline (ohne KI)"
        self.meldung: dict = {}
        self.schritt = 0

    def neuer_fall(self, meldung: dict) -> None:
        self.meldung = meldung
        self.schritt = 0

    def antworte(self, system: str, verlauf: list, tools: list) -> Antwort:
        self.schritt += 1
        case_id = self.meldung["case_id"]
        typ = self.meldung["ausnahme_typ"]

        if self.schritt == 1:
            # Wie ein Sachbearbeiter: kurz den Verlauf ansehen ...
            name, eingabe = "fallverlauf_abrufen", {"case_id": case_id}
        else:
            # ... und dann stur die Regel anwenden (wird sie abgelehnt: keine Massnahme)
            name, felder = self.REGELN.get(typ, ("keine_massnahme", {}))
            if self.schritt > 2:
                name, felder = "keine_massnahme", {}
            eingabe = {
                "case_id": case_id,
                **felder,
                "begruendung": f"Feste Regel: {typ} -> {name}.",
                "entscheidende_fakten": [f"ausnahme_typ = {typ}"],
            }

        aufruf = ToolAufruf(f"regel_{case_id}_{self.schritt}", name, eingabe)
        inhalt = [{"type": "tool_use", "id": aufruf.id, "name": name, "input": eingabe}]
        return Antwort(inhalt=inhalt, tool_aufrufe=[aufruf], stop_grund="tool_use")
