"""
Zentrale Einstellungen des Agenten.

Das Wichtigste hier ist der HANDLUNGSSPIELRAUM: welche Massnahmen der Agent je
Ausnahmetyp wählen darf und welche ein Mensch freigeben muss. Änderungen wirken
sofort auf Agent, Regel-Baseline und die Prüfung in tools.py.
"""
from __future__ import annotations

import os
from pathlib import Path

BASIS = Path(__file__).resolve().parent
DATEN = BASIS / "daten"
PROTOKOLLE = BASIS / "protokolle"

try:  # .env laden (API-Key, Modell), falls python-dotenv installiert ist
    from dotenv import load_dotenv

    load_dotenv(BASIS / ".env")
except ImportError:
    pass

# Stichtag der Analyse. Im Betrieb wäre das "jetzt"; für reproduzierbare Tests
# ist er fix und passt zu den Testdaten im Ordner daten/.
STICHTAG = "2026-10-26T08:00:00"

# --- Sprachmodell (nur Claude-Modus) ------------------------------------------
MODELL = os.getenv("APA_MODELL", "claude-sonnet-5-5")

# Denkaufwand: leer = Standard des Modells, sonst z. B. "low", "medium", "high"
EFFORT = os.getenv("APA_EFFORT") or None

# Adaptives Denken mit lesbarer Zusammenfassung: landet im Protokoll und macht
# Entscheidungen nachvollziehbar. Kostet nicht mehr, denn Denk-Tokens werden
# ohnehin verrechnet; "summarized" macht sie nur lesbar.
THINKING = {"type": "adaptive", "display": "summarized"}

MAX_TOKENS = 16000  # Obergrenze pro Modell-Antwort inkl. Denkprozess

# Preise in USD pro 1 Mio. Tokens (Input, Output), nur für die Kostenschätzung
PREISE = {"claude-sonnet-5-5": (2.00, 10.00)}

# --- Leitplanken ---------------------------------------------------------------
MAX_SCHRITTE = 6  # max. Modell-Antworten pro Fall, danach Abbruch

# Handlungsspielraum: erlaubte Massnahmen je Ausnahmetyp
ERLAUBTE_MASSNAHMEN = {
    "VERZOEGERUNG": ["fall_priorisieren", "eskalieren", "keine_massnahme"],
    "FEHLENDE_INFO": ["info_nachfordern", "eskalieren", "keine_massnahme"],
    "REWORK": ["neu_zuweisen", "naechsten_schritt_empfehlen", "eskalieren", "keine_massnahme"],
    "ABWEICHUNG": ["eskalieren", "naechsten_schritt_empfehlen", "keine_massnahme"],
}

# Diese Massnahmen führt der Agent nicht selbst aus: Sie gehen als Vorschlag an
# einen Menschen zur Freigabe (Human in the Loop).
FREIGABEPFLICHTIG = {"eskalieren"}

# Feste Werte, damit der Agent keine Rollen, Empfänger oder Stufen erfindet
ROLLEN = ["Einkauf", "Senior-Einkauf", "Einkaufsleitung", "Compliance", "Fachabteilung", "Buchhaltung"]
EMPFAENGER = ["Lieferant", "Fachabteilung"]
PRIORITAETEN = ["hoch", "dringend"]
