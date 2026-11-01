#!/usr/bin/env python3
"""
detect.py | WI-Projekt Thema 75 | v0.1 (Schritt 3, AP3)

Deterministische Erkennung gemaess spec.yaml (Abschnitte detection, exceptions).
Unabhaengig vom Generator implementiert: kein Import aus generate_log.py oder validate_log.py.
Liest nur data/event_log.csv und data/cases.csv, nie die Ground Truth.

Kern: evaluate(case, events, now) -> dict
  case   : dict mit Fallattributen (Zeile aus cases.csv)
  events : Liste von dicts (activity, timestamp als datetime, resource, role) dieses Falls
  now    : datetime, Zeitpunkt der Auswertung (im Offline-Experiment = snapshot_time)

Hinweis zur Signatur: spec nennt evaluate(case, now). Die Events werden hier als eigener Parameter
uebergeben, damit die Funktion ohne globale Daten testbar bleibt. Fachlich gehoeren sie zum Fall.

Regeln (Tagesbasis: Trigger vergleichen Kalenderdaten, Uhrzeit von now wird ignoriert):
  E2  order_value + open_items > credit_limit
  E3  (promised_delivery_date - date(now)).days < 2 AND 'Versenden' nicht in events
  E5  'Rechnung stellen' in events AND ('Versenden' nicht in events OR erstes 'Rechnung stellen' vor erstem 'Versenden')
  E6  invoice_date + payment_terms_days < date(now) AND 'Zahlungseingang' nicht in events
      invoice_date = Datum des ersten Events 'Rechnung stellen'
  E7  E2 AND E3 (Vorrang: Fall gilt als E7, nicht zusaetzlich als E2 oder E3)
  weicher Trigger free_text_present: free_text nicht leer

Annahmen (im Bericht genannt, nicht in spec geregelt):
  AN1 Nur Events mit timestamp <= now zaehlen (zeitparametrisierte Auswertung, im Log ohnehin erfuellt).
  AN2 E2 ohne Stadiumsbedingung (spec open_point, wortgetreu umgesetzt).
  AN3 E3: 'Teillieferung' zaehlt nicht als 'Versenden' (spec open_point, wortgetreu, kommt im Log nicht vor).
  AN4 E5: Reihenfolge nach vollem Zeitstempel (nicht Tagesbasis), da es um Ereignisreihenfolge geht.
  AN5 Mehrere harte Trigger ausser E2+E3: detected_type nach Prioritaet E5 > E6 > E2 > E3
      (Conformance-Verstoss vor Zahlungsthema). Kommt im Log nicht vor, siehe Bericht.

Aufruf:
  python src/detect.py              -> out/detections.csv
"""

import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
E3_DAYS_THRESHOLD = 2          # spec exceptions.E3.params.days_threshold
TYPE_PRIORITY = ["E5", "E6", "E2", "E3"]   # AN5


def _first(events, activity):
    ts = [e["timestamp"] for e in events if e["activity"] == activity]
    return min(ts) if ts else None


def _has(events, activity):
    return any(e["activity"] == activity for e in events)


def _free_text(case):
    v = case.get("free_text")
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return str(v).strip()


def evaluate(case, events, now):
    """Wertet einen Fall zum Zeitpunkt now aus. Gibt Trigger, Typ und Routing zurueck."""
    today = now.date()
    ev = sorted([e for e in events if e["timestamp"] <= now], key=lambda e: e["timestamp"])   # AN1

    hard = []
    # E2
    if int(case["order_value"]) + int(case["open_items"]) > int(case["credit_limit"]):
        hard.append("E2")
    # E3
    promised = pd.Timestamp(case["promised_delivery_date"]).date()
    if (promised - today).days < E3_DAYS_THRESHOLD and not _has(ev, "Versenden"):   # AN3
        hard.append("E3")
    # E5
    first_inv = _first(ev, "Rechnung stellen")
    first_ship = _first(ev, "Versenden")
    if first_inv is not None and (first_ship is None or first_inv < first_ship):     # AN4
        hard.append("E5")
    # E6
    if first_inv is not None and not _has(ev, "Zahlungseingang"):
        due = first_inv.date() + pd.Timedelta(days=int(case["payment_terms_days"]))
        if due < today:
            hard.append("E6")

    soft = _free_text(case) != ""

    if "E2" in hard and "E3" in hard:
        detected = "E7"
    else:
        detected = next((t for t in TYPE_PRIORITY if t in hard), "none")

    return {
        "detected_type": detected,
        "hard_triggers": hard,
        "soft_trigger": soft,
        "routed_to_agent": bool(hard) or soft,
        "invoice_date": first_inv.date().isoformat() if first_inv is not None else "",
    }


def load(data_dir=ROOT / "data"):
    cases = pd.read_csv(data_dir / "cases.csv", dtype={"free_text": str}, keep_default_na=False)
    ev = pd.read_csv(data_dir / "event_log.csv", parse_dates=["timestamp"])
    events = {cid: [{"activity": r.activity, "timestamp": r.timestamp.to_pydatetime(),
                     "resource": r.resource, "role": r.role} for r in g.itertuples()]
              for cid, g in ev.groupby("case_id")}
    return cases, events


def run(data_dir=ROOT / "data"):
    cases, events = load(data_dir)
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
    ap.add_argument("--out", default=str(ROOT / "out" / "detections.csv"))
    a = ap.parse_args()
    df = run()
    df.to_csv(a.out, index=False)
    multi = df[df.hard_triggers.str.count(";") >= 1]
    print(f"{len(df)} Faelle ausgewertet -> {a.out}")
    print("detected_type:", df.detected_type.value_counts().to_dict())
    print("geroutet:", int(df.routed_to_agent.sum()), "| nur weicher Trigger:",
          int((df.soft_trigger & (df.hard_triggers == "")).sum()))
    print("Mehrfachtrigger:", multi.hard_triggers.value_counts().to_dict())


if __name__ == "__main__":
    main()
