#!/usr/bin/env python3
"""
detect_v2.py | WI-Projekt Thema 75 | Prozess v2 (Entwurf) | v0.2

Deterministische Erkennung gemaess spec/spec_v2.yaml. Wie v1 unabhaengig vom Generator
implementiert: kein Import aus generate_log*.py, liest nur data/v2/event_log.csv und
data/v2/cases.csv, nie die Ground Truth. src/detect.py (v1) bleibt unveraendert.

Kern: evaluate(case, events, now) -> dict (gleiche Schnittstelle wie v1)

Regeln (Tagesbasis, nur Events mit timestamp <= now):
  E2   order_value + open_items > credit_limit
  E3   (promised_delivery_date - date(now)).days < 2 AND kein 'Versenden' AND kein 'Auftrag stornieren'
  E5   'Rechnung stellen' AND ('Versenden' fehlt OR erstes 'Rechnung stellen' vor erstem 'Versenden')
  E6   invoice_date + payment_terms_days < date(now) AND kein 'Zahlungseingang'
  E7   E2 AND E3 (Vorrang, wie v1)
  E8   erstes 'Auftrag stornieren' nach dem ersten 'Versenden' oder 'Teillieferung'
  E9   invoice_amount > 0 AND |invoice_amount - order_value| > 1
  E10  'Zahlungseingang' AND invoice_amount - credit_note_amount - paid_amount > 1
  E11  erstes 'Rechnung stellen' vor der letzten 'Retoure erfassen' AND kein 'Gutschrift erstellen' danach
       AND (date(now) - date(letzte Retoure)).days > 10
  E12  'Ware nachbestellen' AND kein 'Wareneingang Lager' AND kein 'Versenden' AND kein 'Auftrag stornieren'
       AND restock_date >= promised_delivery_date
Mehrfachtrigger: Ursache vor Symptom, Prioritaet E8 > E5 > E11 > E9 > E10 > E6 > E2 > E3 > E12.

Aufruf:
  python src/detect_v2.py           -> out/v2/detections.csv
"""

import argparse
from datetime import date, datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
E3_DAYS_THRESHOLD = 2          # spec_v2 exceptions.E3.params.days_threshold
E11_DAYS_THRESHOLD = 10        # spec_v2 exceptions.E11.params.days_threshold
TOLERANCE_CHF = 1              # spec_v2 exceptions.E9/E10.params.tolerance_chf
TYPE_PRIORITY = ["E8", "E5", "E11", "E9", "E10", "E6", "E2", "E3", "E12"]


def _first(events, activity):
    ts = [e["timestamp"] for e in events if e["activity"] == activity]
    return min(ts) if ts else None


def _last(events, activity):
    ts = [e["timestamp"] for e in events if e["activity"] == activity]
    return max(ts) if ts else None


def _has(events, activity):
    return any(e["activity"] == activity for e in events)


def _num(case, key):
    v = case.get(key)
    if v is None or v == "" or (isinstance(v, float) and pd.isna(v)):
        return 0
    return int(v)


def _date(case, key):
    v = case.get(key)
    if v is None or v == "" or (isinstance(v, float) and pd.isna(v)):
        return None
    return pd.Timestamp(v).date()


def _free_text(case):
    v = case.get("free_text")
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return str(v).strip()


def evaluate(case, events, now):
    """Wertet einen Fall zum Zeitpunkt now aus. Gibt Trigger, Typ und Routing zurueck."""
    today = now.date()
    ev = sorted([e for e in events if e["timestamp"] <= now], key=lambda e: e["timestamp"])
    order_value = _num(case, "order_value")
    invoice = _num(case, "invoice_amount")
    promised = _date(case, "promised_delivery_date")
    first_inv = _first(ev, "Rechnung stellen")
    first_ship = _first(ev, "Versenden")
    storno = _first(ev, "Auftrag stornieren")

    hard = []
    if order_value + _num(case, "open_items") > _num(case, "credit_limit"):
        hard.append("E2")
    if promised is not None and (promised - today).days < E3_DAYS_THRESHOLD and first_ship is None and storno is None:
        hard.append("E3")
    if first_inv is not None and (first_ship is None or first_inv < first_ship):
        hard.append("E5")
    if first_inv is not None and not _has(ev, "Zahlungseingang"):
        if first_inv.date() + pd.Timedelta(days=_num(case, "payment_terms_days")) < today:
            hard.append("E6")
    shipped = [t for t in (first_ship, _first(ev, "Teillieferung")) if t is not None]
    if storno is not None and shipped and min(shipped) < storno:
        hard.append("E8")
    if invoice > 0 and abs(invoice - order_value) > TOLERANCE_CHF:
        hard.append("E9")
    if _has(ev, "Zahlungseingang") and invoice - _num(case, "credit_note_amount") - _num(case, "paid_amount") > TOLERANCE_CHF:
        hard.append("E10")
    ret = _last(ev, "Retoure erfassen")
    if ret is not None and first_inv is not None and first_inv < ret:
        credited = any(e["activity"] == "Gutschrift erstellen" and e["timestamp"] > ret for e in ev)
        if not credited and (today - ret.date()).days > E11_DAYS_THRESHOLD:
            hard.append("E11")
    restock = _date(case, "restock_date")
    if _has(ev, "Ware nachbestellen") and not _has(ev, "Wareneingang Lager") and first_ship is None \
            and storno is None and restock is not None and promised is not None and restock >= promised:
        hard.append("E12")

    if "E2" in hard and "E3" in hard:
        detected = "E7"
    else:
        detected = next((t for t in TYPE_PRIORITY if t in hard), "none")

    return {
        "detected_type": detected,
        "hard_triggers": hard,
        "soft_trigger": _free_text(case) != "",
        "routed_to_agent": bool(hard) or _free_text(case) != "",
        "invoice_date": first_inv.date().isoformat() if first_inv is not None else "",
    }


def load(data_dir=ROOT / "data" / "v2"):
    cases = pd.read_csv(data_dir / "cases.csv", dtype=str, keep_default_na=False)
    ev = pd.read_csv(data_dir / "event_log.csv", parse_dates=["timestamp"])
    events = {cid: [{"activity": r.activity, "timestamp": r.timestamp.to_pydatetime(),
                     "resource": r.resource, "role": r.role} for r in g.itertuples()]
              for cid, g in ev.groupby("case_id")}
    return cases, events


def run(data_dir=ROOT / "data" / "v2"):
    cases, events = load(Path(data_dir))
    rows = []
    for c in cases.to_dict("records"):
        now = datetime.strptime(c["snapshot_time"], "%Y-%m-%d %H:%M:%S")
        r = evaluate(c, events.get(c["case_id"], []), now)
        rows.append({"case_id": c["case_id"], "detected_type": r["detected_type"],
                     "hard_triggers": ";".join(r["hard_triggers"]),
                     "soft_trigger": r["soft_trigger"], "routed_to_agent": r["routed_to_agent"]})
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data" / "v2"))
    ap.add_argument("--out", default=str(ROOT / "out" / "v2" / "detections.csv"))
    a = ap.parse_args()
    df = run(a.data)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(a.out, index=False, lineterminator="\n")
    multi = df[df.hard_triggers.str.count(";") >= 1]
    print(f"{len(df)} Faelle ausgewertet -> {a.out}")
    print("detected_type:", df.detected_type.value_counts().to_dict())
    print("geroutet:", int(df.routed_to_agent.sum()), "| nur weicher Trigger:",
          int((df.soft_trigger & (df.hard_triggers == "")).sum()))
    print("Mehrfachtrigger:", multi.hard_triggers.value_counts().to_dict())


if __name__ == "__main__":
    main()
