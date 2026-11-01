#!/usr/bin/env python3
"""
keyword_labeler.py | WI-Projekt Thema 75 | v0.1

Regelbasierter Freitext-Klassifikator (Schluesselwoerter). Zwei Zwecke:
  1. Zweiter, unabhaengiger Labeler im simulierten Doppellabeling (deterministisch, kein LLM).
  2. Kandidat fuer die E6-Komponente der Baseline in Schritt 3 (Regel statt Agent).

Die Schluesselwortlisten wurden aus den Kategoriedefinitionen abgeleitet und vor dem
Labeling festgelegt. Sie werden nicht nachtraeglich auf die Vorlagen optimiert
(sonst waere der Vergleich mit dem Agenten verzerrt). Einschraenkung: Der Autor kannte die Vorlagen.

Aufruf:
  python src/keyword_labeler.py --items data/labeling/label_items.csv --out out/labels_keyword.txt
"""

import argparse
import re
from pathlib import Path

import pandas as pd

KEYWORDS = {
    "payment_difficulty": ["rate", "raten", "liquidit", "engpass", "aufschub", "zahlungsschwierig", "stundung",
                           "konkurs", "nachlass", "mehr zeit", "nicht bezahlen", "nicht begleichen",
                           "nicht fristgerecht", "reicht es", "abzahlen", "teilzahlung"],
    "complaint": ["reklam", "mangel", "maengel", "beanstand", "beschaedigt", "defekt", "kaputt", "falsch",
                  "fehlt", "fehlen", "unvollstaendig", "ausgefallen", "funktioniert nicht", "unzufrieden"],
    "payment_announced": ["zahlung ist veranlasst", "ueberweisung", "ueberwiesen", "bezahlt", "beglichen",
                          "zahlungslauf", "valuta", "angewiesen", "ausgeloest", "terminiert", "zahlung erfolgt",
                          "zahlung fuer", "bezahlen"],
}
PRIORITY = ["payment_difficulty", "complaint", "payment_announced"]   # bei Gleichstand


def classify(text):
    t = text.lower()
    hits = {c: sum(1 for k in kws if re.search(r"\b" + re.escape(k), t)) for c, kws in KEYWORDS.items()}
    best = max(hits.values())
    if best == 0:
        return "irrelevant", hits
    for c in PRIORITY:
        if hits[c] == best:
            return c, hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    items = pd.read_csv(a.items, dtype=str)
    lines = ["item_id|label|unsicher|begruendung"]
    for r in items.itertuples():
        lab, hits = classify(r.text)
        n = sum(hits.values())
        why = ", ".join(f"{c}:{v}" for c, v in hits.items() if v) or "keine Treffer"
        lines.append(f"{r.item_id}|{lab}|{'ja' if n == 0 or sorted(hits.values())[-2] > 0 else 'nein'}|{why}")
    Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(items)} Eintraege gelabelt -> {a.out}")


if __name__ == "__main__":
    main()
