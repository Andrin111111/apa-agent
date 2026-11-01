#!/usr/bin/env python3
"""
case_object.py | WI-Projekt Thema 75 | v1.0 (Schritt 4, AP4)

Baut das Fallobjekt, den einzigen fachlichen Input des Agenten.
Quellen: data/cases.csv, data/event_log.csv und detect.evaluate (deterministische Erkennung).
Nie enthalten: Ground Truth, generator_tag, Vorlagen-IDs, Freitext-Kategorie, Textstil.

Aufbau (Version CASE_OBJECT_VERSION):
  case_id, snapshot_time, snapshot_date
  attributes  Fallattribute laut spec.case_attributes (ohne free_text, snapshot_time)
  free_text   Freitext oder null
  history     Verlauf bis now: activity, timestamp (YYYY-MM-DD HH:MM), role (ohne Personennamen)
  derived     abgeleitete Werte (siehe derive), Tagesbasis wie in der Erkennung
  detection   detected_type, hard_triggers, soft_trigger_free_text (aus detect.evaluate)

Serialisierung: canonical_json (sortierte Schluessel, ASCII, ohne Leerzeichen) ist die Basis fuer den
Hash. Listen behalten ihre Reihenfolge (Verlauf chronologisch).

Annahmen:
  CO1 Verlauf mit Uhrzeit (Minuten) statt nur Datum, weil E5 die Reihenfolge nach Zeitstempel prueft.
  CO2 Ressource (Personenname) wird weggelassen: fachlich ohne Nutzen, nur Tokens.
  CO3 Abgeleitete Werte sind null, wenn sie nicht definiert sind (z. B. keine Rechnung).
  CO4 days_to_promised_delivery ist null, sobald versendet wurde (Frist erfuellt, sonst irrefuehrend).

Aufruf (Einzelfall ansehen):
  python src/case_object.py C0880
"""

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import detect  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CASE_OBJECT_VERSION = "1.0"
ATTRIBUTES = ["order_value", "customer_segment", "credit_limit", "open_items", "payment_history",
              "payment_terms_days", "promised_delivery_date"]
# Felder, die nie im Fallobjekt vorkommen duerfen (Ground Truth und Generatorwissen)
FORBIDDEN_KEYS = {"exception_type", "free_text_category", "allowed_action_sets", "expected_target_role",
                  "generator_tag", "template_id", "tpl", "stil", "category"}


def _int(v):
    return int(v)


def derive(case, events, now, det):
    """Abgeleitete Werte auf Tagesbasis. events: nur Events bis now, chronologisch."""
    today = now.date()
    exposure = _int(case["order_value"]) + _int(case["open_items"])
    limit = _int(case["credit_limit"])
    promised = pd.Timestamp(case["promised_delivery_date"]).date()
    acts = [e["activity"] for e in events]
    shipped = "Versenden" in acts
    paid = "Zahlungseingang" in acts
    inv = det["invoice_date"] or None
    due = None
    overdue = None
    if inv:
        due_d = pd.Timestamp(inv).date() + pd.Timedelta(days=_int(case["payment_terms_days"]))
        due = due_d.isoformat()
        if not paid:
            overdue = (today - due_d).days
    return {
        "credit_exposure": exposure,
        "credit_headroom": limit - exposure,
        "credit_utilization": round(exposure / limit, 3) if limit else None,
        "overshoot_ratio": round(max(0, exposure - limit) / limit, 3) if limit else None,
        "days_to_promised_delivery": None if shipped else (promised - today).days,   # CO4
        "shipped": shipped,
        "partially_shipped": "Teillieferung" in acts,
        "invoice_date": inv,
        "due_date": due,
        "days_overdue": overdue,
        "payment_received": paid,
        "n_order_changes": acts.count("Auftrag aendern"),
        "n_payment_reminders": acts.count("Zahlungserinnerung"),
        "last_activity": acts[-1] if acts else None,
    }


def build(case, events, now=None):
    """Fallobjekt fuer einen Fall. case: dict (Zeile aus cases.csv), events: Liste wie in detect.load."""
    if now is None:
        now = datetime.strptime(case["snapshot_time"], "%Y-%m-%d %H:%M:%S")
    det = detect.evaluate(case, events, now)
    ev = sorted([e for e in events if e["timestamp"] <= now], key=lambda e: e["timestamp"])   # wie AN1
    ft = detect._free_text(case)
    attrs = {}
    for k in ATTRIBUTES:
        v = case[k]
        attrs[k] = _int(v) if k in ("order_value", "credit_limit", "open_items", "payment_terms_days") else str(v)
    return {
        "case_object_version": CASE_OBJECT_VERSION,
        "case_id": str(case["case_id"]),
        "snapshot_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "snapshot_date": now.date().isoformat(),
        "attributes": attrs,
        "free_text": ft or None,
        "history": [{"activity": e["activity"], "timestamp": e["timestamp"].strftime("%Y-%m-%d %H:%M"),
                     "role": e["role"]} for e in ev],
        "derived": derive(case, ev, now, det),
        "detection": {"detected_type": det["detected_type"], "hard_triggers": list(det["hard_triggers"]),
                      "soft_trigger_free_text": bool(det["soft_trigger"])},
    }, det


def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def render_json(obj):
    """Deterministische Darstellung fuer den Prompt (eine Zeile, sortierte Schluessel, spart Tokens)."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=True, separators=(", ", ": "))


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def object_hash(obj):
    return sha256(canonical_json(obj))


def find_forbidden(obj, path=""):
    """Rekursive Pruefung auf verbotene Schluessel. Rueckgabe: Liste der Fundstellen."""
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in FORBIDDEN_KEYS:
                hits.append(f"{path}/{k}")
            hits += find_forbidden(v, f"{path}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits += find_forbidden(v, f"{path}[{i}]")
    return hits


class CaseStore:
    """Laedt Faelle und Events einmal und baut Fallobjekte auf Anfrage."""

    def __init__(self, data_dir=ROOT / "data"):
        cases, self.events = detect.load(data_dir)
        self.cases = {r["case_id"]: r for r in cases.to_dict("records")}

    def ids(self):
        return list(self.cases)

    def get(self, case_id):
        return build(self.cases[case_id], self.events.get(case_id, []))


def main():
    store = CaseStore()
    for cid in sys.argv[1:] or ["C0880"]:
        obj, _ = store.get(cid)
        print(render_json(obj))
        print("hash:", object_hash(obj))


if __name__ == "__main__":
    main()
