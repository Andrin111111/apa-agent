"""
Entscheidungsprotokoll: Jeder bearbeitete Fall wird mit allen Schritten als eine
Zeile JSON gespeichert (JSONL). Das ist die Grundlage für Nachvollziehbarkeit
und Evaluation: Was wusste der Agent, was hat er getan, und warum?
"""
from __future__ import annotations

import json
from datetime import datetime

import config


class Protokoll:
    def __init__(self, modus: str):
        config.PROTOKOLLE.mkdir(exist_ok=True)
        self.lauf_id = f"{datetime.now():%Y-%m-%d_%H-%M-%S}_{modus}"
        self.pfad = config.PROTOKOLLE / f"lauf_{self.lauf_id}.jsonl"

    def schreibe(self, eintrag: dict) -> None:
        zeile = {"lauf_id": self.lauf_id, "zeit": datetime.now().isoformat(timespec="seconds"), **eintrag}
        with open(self.pfad, "a", encoding="utf-8") as f:
            f.write(json.dumps(zeile, ensure_ascii=False) + "\n")


def lies(pfad) -> list[dict]:
    with open(pfad, encoding="utf-8") as f:
        return [json.loads(zeile) for zeile in f if zeile.strip()]
