"""
Datenzugriff für den Agenten.

Im Gerüst kommt alles aus Testdateien im Ordner daten/. Später ersetzt ihr sie
durch eure echten Ergebnisse (siehe README, Abschnitt «Dateien»).
"""
from __future__ import annotations

import csv
import json
from datetime import datetime
from functools import lru_cache

from config import DATEN


def _json(dateiname: str):
    with open(DATEN / dateiname, encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=None)
def event_log() -> dict[str, list[dict]]:
    """Event Log, gruppiert pro Fall: {case_id: [Events in zeitlicher Reihenfolge]}."""
    faelle: dict[str, list[dict]] = {}
    with open(DATEN / "event_log.csv", newline="", encoding="utf-8") as f:
        for zeile in csv.DictReader(f):
            faelle.setdefault(zeile["case_id"], []).append(zeile)
    for events in faelle.values():
        events.sort(key=lambda e: e["timestamp"])
    return faelle


@lru_cache(maxsize=None)
def fallkontext() -> dict:
    return _json("fallkontext.json")


@lru_cache(maxsize=None)
def prozesswissen() -> dict:
    return _json("prozesswissen.json")


def ausnahmemeldungen() -> list[dict]:
    return _json("ausnahmen.json")


def erwartete_massnahmen() -> dict:
    return _json("erwartete_massnahmen.json")


def tage_zwischen(von: str, bis: str) -> float:
    """Tage zwischen zwei ISO-Zeitpunkten, auf eine Nachkommastelle gerundet."""
    delta = datetime.fromisoformat(bis) - datetime.fromisoformat(von)
    return round(delta.total_seconds() / 86400, 1)
