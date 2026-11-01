#!/usr/bin/env python3
"""
baseline.py | WI-Projekt Thema 75 | v0.1 (Schritt 3, AP6)

Regelbasierte Baseline: feste Zuordnung Ausnahmetyp -> Aktion, auf denselben Faellen wie der Agent.
Ausgabe im Format agent_output_schema (spec.yaml), damit metrics.py Agent und Baseline gleich auswertet.
Liest out/detections.csv (Erkennung) und data/cases.csv (Freitext). Nie die Ground Truth.

Regeln:
  E2  -> [A6 Credit Management]                       (spec, einzige zulaessige Menge)
  E3  -> [A4, A2]                                     (feste Variante, Begruendung siehe B1)
  E5  -> [A6 Buchhaltung, A7]                         (spec, Konzept, nur informativ ausgewertet)
  E6  -> Kategorie per keyword_labeler.classify (unveraendert), dann Zuordnung laut spec:
         complaint -> [A5 Kundendienst], payment_announced -> [A0],
         payment_difficulty -> [A6 Credit Management], irrelevant -> [A3]
  E7  -> [A6 Credit Management], exception_type E7    (B2, nicht bewertet)
  nur weicher Trigger (Freitext ohne harten Trigger) -> [A0], exception_type none

Annahmen:
  B1 E3: [A4, A2]. Alle drei Varianten gelten laut D2 als korrekt, die Wahl beeinflusst die Korrektheit
     der Baseline daher nicht. Gewaehlt wird die umfassendste autonome Variante: Eine Regel kennt den
     Grund der Verzoegerung nicht und kann nicht abwaegen, ob interne Beschleunigung (A4) oder
     Kundentransparenz (A2) genuegt. Beide Aktionen sind autonom, kosten also keine Freigabe.
     Bei ueberschrittenem Liefertermin (im Log vorhanden) waere A4 allein fachlich schwach.
  B2 E7: Eine feste Regel hat keine Abwaegungslogik. Sie uebergibt an einen Menschen (A6). Zielrolle
     Credit Management, weil das Kreditsignal die Lieferung blockieren kann. Ground Truth fuer E7 ist
     leer, daher wird die Zeile ausgegeben, aber nicht bewertet.
  B3 Die Baseline enthaelt sich nie (kein 'unknown'): Jeder erkannte Typ hat eine feste Regel.

Aufruf:
  python src/baseline.py            -> out/baseline_actions.jsonl
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from keyword_labeler import classify  # noqa: E402  (bestehender Klassifikator, nicht nachgetunt)

E6_RULES = {
    "complaint": [{"action_id": "A5", "target_role": "Kundendienst"}],
    "payment_announced": [{"action_id": "A0"}],
    "payment_difficulty": [{"action_id": "A6", "target_role": "Credit Management"}],
    "irrelevant": [{"action_id": "A3"}],
}

TYPE_RULES = {
    "E2": ([{"action_id": "A6", "target_role": "Credit Management"}],
           "Kreditlimit ueberschritten (Auftragswert + offene Posten > Kreditlimit), Regel: Eskalation an Credit Management.",
           ["order_value", "open_items", "credit_limit"]),
    "E3": ([{"action_id": "A4"}, {"action_id": "A2"}],
           "Liefertermin in weniger als 2 Tagen oder ueberschritten, nicht versendet. Regel: priorisieren und Kunde informieren.",
           ["promised_delivery_date", "snapshot_time", "event:Versenden fehlt"]),
    "E5": ([{"action_id": "A6", "target_role": "Buchhaltung"}, {"action_id": "A7"}],
           "Rechnung vor Versand (Conformance-Verstoss). Regel: Eskalation an Buchhaltung und Fall sperren.",
           ["event:Rechnung stellen", "event:Versenden"]),
    "E7": ([{"action_id": "A6", "target_role": "Credit Management"}],
           "Kreditlimit ueberschritten und Lieferverzoegerung zugleich. Regel ohne Abwaegung: Uebergabe an Mensch.",
           ["order_value", "open_items", "credit_limit", "promised_delivery_date"]),
}


def decide(case_id, detected_type, free_text):
    """Feste Regel pro erkanntem Typ. Rueckgabe im Format agent_output_schema."""
    if detected_type in TYPE_RULES:
        actions, why, ev = TYPE_RULES[detected_type]
        return {"case_id": case_id, "exception_type": detected_type, "actions": actions,
                "rationale": why, "key_evidence": ev}
    if detected_type == "E6":
        cat, hits = classify(free_text)
        hit_txt = ", ".join(f"{c}:{v}" for c, v in hits.items() if v) or "keine Schluesselwoerter"
        return {"case_id": case_id, "exception_type": "E6", "actions": E6_RULES[cat],
                "rationale": f"Rechnung ueberfaellig ohne Zahlungseingang. Freitext per Schluesselwoertern als '{cat}' eingeordnet ({hit_txt}).",
                "key_evidence": ["invoice_date", "payment_terms_days", "event:Zahlungseingang fehlt", "free_text"],
                "_baseline_category": cat}
    # nur weicher Trigger
    return {"case_id": case_id, "exception_type": "none", "actions": [{"action_id": "A0"}],
            "rationale": "Freitext eingegangen, aber kein harter Trigger. Regel: keine Massnahme, protokollieren.",
            "key_evidence": ["free_text", "keine harten Trigger"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--detections", default=str(ROOT / "out" / "detections.csv"))
    ap.add_argument("--out", default=str(ROOT / "out" / "baseline_actions.jsonl"))
    a = ap.parse_args()
    det = pd.read_csv(a.detections, keep_default_na=False)
    cases = pd.read_csv(ROOT / "data" / "cases.csv", dtype={"free_text": str}, keep_default_na=False)
    ft = dict(zip(cases.case_id, cases.free_text))
    routed = det[det.routed_to_agent.astype(str) == "True"]
    with open(a.out, "w", encoding="utf-8") as f:
        for r in routed.itertuples():
            f.write(json.dumps(decide(r.case_id, r.detected_type, ft.get(r.case_id, "")), ensure_ascii=True) + "\n")
    print(f"{len(routed)} Zeilen -> {a.out}")


if __name__ == "__main__":
    main()
