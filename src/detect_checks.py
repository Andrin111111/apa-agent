#!/usr/bin/env python3
"""
detect_checks.py | WI-Projekt Thema 75 | v0.1 (Schritt 3, K3)

Prueft, ob die Grenzfaelle im Log die Vergleichsoperatoren der Erkennung tatsaechlich testen.
Dazu werden absichtlich falsche Regelvarianten (Mutanten) gegen die Ground Truth gerechnet.
Ein guter Testdatensatz muss jeden Mutanten mit mindestens einem Fehler entlarven.
Zusaetzlich: Gleichzeitigkeit von 'Rechnung stellen' und 'Versenden' (relevant fuer E5, Annahme AN4).

Aufruf:
  python src/detect_checks.py      -> out/detect_checks.md
"""

from datetime import datetime, timedelta
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import detect  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def mutant(case, events, now, variant):
    r = detect.evaluate(case, events, now)
    hard = set(r["hard_triggers"])
    today = now.date()
    ev = [e for e in events if e["timestamp"] <= now]
    shipped = any(e["activity"] == "Versenden" for e in ev)
    inv = min([e["timestamp"] for e in ev if e["activity"] == "Rechnung stellen"], default=None)
    paid = any(e["activity"] == "Zahlungseingang" for e in ev)
    promised = pd.Timestamp(case["promised_delivery_date"]).to_pydatetime()
    terms = int(case["payment_terms_days"])
    s = int(case["order_value"]) + int(case["open_items"])
    if variant == "E2 >= statt >":
        hard.discard("E2")
        if s >= int(case["credit_limit"]):
            hard.add("E2")
    elif variant == "E3 <= 2 statt < 2":
        hard.discard("E3")
        if (promised.date() - today).days <= 2 and not shipped:
            hard.add("E3")
    elif variant == "E6 <= statt <":
        hard.discard("E6")
        if inv is not None and not paid and inv.date() + timedelta(days=terms) <= today:
            hard.add("E6")
    elif variant == "Zeitpunkt statt Tagesbasis (E3, E6)":
        hard.discard("E3")
        hard.discard("E6")
        if (promised - now) < timedelta(days=2) and not shipped:
            hard.add("E3")
        if inv is not None and not paid and inv + timedelta(days=terms) < now:
            hard.add("E6")
    elif variant == "keine Vorrangregel E7":
        pass
    if variant == "keine Vorrangregel E7":
        order = ["E5", "E6", "E2", "E3"]
    else:
        if "E2" in hard and "E3" in hard:
            return "E7"
        order = ["E5", "E6", "E2", "E3"]
    return next((t for t in order if t in hard), "none")


def main():
    cases, events = detect.load()
    gt = pd.read_csv(ROOT / "data" / "ground_truth.csv", keep_default_na=False).set_index("case_id")
    variants = ["Referenz (detect.py)", "E2 >= statt >", "E3 <= 2 statt < 2", "E6 <= statt <",
                "Zeitpunkt statt Tagesbasis (E3, E6)", "keine Vorrangregel E7"]
    L = ["# Sensitivitaet der Erkennung (Mutanten)", "",
         "Falsche Regelvarianten gegen die Ground Truth. Fehler > 0 heisst: Die Daten entlarven den Mutanten.", "",
         "| Variante | falsch erkannt | davon Grenzfaelle (boundary_*) | Beispiel-Faelle |", "|---|---|---|---|"]
    recs = cases.to_dict("records")
    for v in variants:
        wrong = []
        for c in recs:
            now = datetime.strptime(c["snapshot_time"], "%Y-%m-%d %H:%M:%S")
            evs = events.get(c["case_id"], [])
            t = detect.evaluate(c, evs, now)["detected_type"] if v.startswith("Referenz") else mutant(c, evs, now, v)
            if t != gt.loc[c["case_id"], "exception_type"]:
                wrong.append(c["case_id"])
        nb = sum("boundary_" in gt.loc[w, "generator_tag"] for w in wrong)
        L.append(f"| {v} | {len(wrong)} | {nb} | {', '.join(wrong[:4])} |")
    # Gleichzeitigkeit E5
    ev = pd.read_csv(ROOT / "data" / "event_log.csv", parse_dates=["timestamp"])
    inv = ev[ev.activity == "Rechnung stellen"].groupby("case_id").timestamp.min()
    shp = ev[ev.activity == "Versenden"].groupby("case_id").timestamp.min()
    both = pd.concat([inv, shp], axis=1, keys=["inv", "shp"]).dropna()
    same_ts = int((both.inv == both.shp).sum())
    same_day = int((both.inv.dt.date == both.shp.dt.date).sum())
    L += ["", f"- E5: Faelle mit Rechnung und Versand zum selben Zeitstempel: {same_ts}, am selben Tag: {same_day} "
          f"(AN4 Zeitstempel statt Tag ist {'relevant' if same_day else 'im Log nicht relevant'})"]
    out = ROOT / "out" / "detect_checks.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
