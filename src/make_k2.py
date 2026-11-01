#!/usr/bin/env python3
"""
make_k2.py | WI-Projekt Thema 75 | Schritt 2 (AP2) | v0.2 (kompakt)

Erzeugt k2_stichprobe.md: 10 zufaellige Faelle pro Typ, eine Zeile pro Fall.
Optional wird out/k2_befunde.md (Review-Ergebnis) an den Anfang gestellt.

Aufruf aus dem Repo-Root:
  python src/make_k2.py
"""

import zlib
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
FMT = "%Y-%m-%d %H:%M:%S"
TYPES = ["none", "E2", "E3", "E5", "E6", "E7"]
N_PER_TYPE = 10
ABBR = {"Auftrag erfassen": "ERF", "Kreditpruefung": "KRED", "Auftrag bestaetigen": "BEST",
        "Auftrag aendern": "AEND", "Kommissionieren": "KOMM", "Teillieferung": "TEIL", "Versenden": "VERS",
        "Rechnung stellen": "RECH", "Zahlungserinnerung": "ERIN", "Zahlungseingang": "ZAHL",
        "Fall abschliessen": "ABS"}
SETS = {'[["A0"]]': "A0", '[["A6"]]': "A6", '[["A4"],["A2"],["A4","A2"]]': "A4 / A2 / A4+A2",
        '[["A6","A7"]]': "A6+A7", '[["A5"]]': "A5", '[["A3"]]': "A3", "": "(leer)"}


def main():
    spec = yaml.safe_load((ROOT / "spec" / "spec.yaml").read_text(encoding="utf-8"))
    rd = lambda f: pd.read_csv(ROOT / "data" / f, dtype=str, keep_default_na=False)
    ev, cs, gt = rd("event_log.csv"), rd("cases.csv"), rd("ground_truth.csv")
    seed = int(spec["meta"]["seed"])
    rng = np.random.default_rng(np.random.SeedSequence(entropy=seed, spawn_key=(zlib.crc32(b"k2"),)))
    cs_i, gt_i = cs.set_index("case_id"), gt.set_index("case_id")
    evg = {k: g for k, g in ev.groupby("case_id", sort=False)}

    L = ["# K2-Stichprobe (kompakt)", ""]
    bef = ROOT / "out" / "k2_befunde.md"
    if bef.exists():
        L += [bef.read_text(encoding="utf-8").strip(), ""]
    L += ["## Legende", "",
          "Verlauf: Aktivitaeten in Kurzform, Zahl in Klammern = Kalendertage seit dem vorherigen Event. "
          "ERF erfassen, KRED Kreditpruefung, BEST bestaetigen, AEND aendern, KOMM kommissionieren, TEIL Teillieferung, "
          "VERS versenden, RECH Rechnung, ERIN Zahlungserinnerung, ZAHL Zahlungseingang, ABS abschliessen.",
          "Kennwerte: Seg = Segment, Q = (Auftragswert + offene Posten) / Kreditlimit, Hist = Zahlungshistorie, "
          "Ziel = Zahlungsziel, Lief = Liefertermin minus Stichtag (Tage), Verzug = Tage ueber Faelligkeit, "
          "Warte = Tage vom letzten Event bis Stichtag.", ""]
    for t in TYPES:
        ids = sorted(gt[gt.exception_type == t].case_id)
        pick = sorted(ids[j] for j in rng.choice(len(ids), size=N_PER_TYPE, replace=False))
        L += [f"## {t}", "", "| Fall | Verlauf | Kennwerte | Freitext | Soll |", "|---|---|---|---|---|"]
        for cid in pick:
            r, g, e = cs_i.loc[cid], gt_i.loc[cid], evg[cid]
            ts = [datetime.strptime(x, FMT) for x in e.timestamp]
            parts = [ABBR[e.activity.iloc[0]]]
            for i in range(1, len(ts)):
                parts.append(f"{ABBR[e.activity.iloc[i]]}({(ts[i].date() - ts[i - 1].date()).days})")
            snap = datetime.strptime(r.snapshot_time, FMT)
            q = (int(r.order_value) + int(r.open_items)) / int(r.credit_limit)
            lief = (date.fromisoformat(r.promised_delivery_date) - snap.date()).days
            acts = list(e.activity)
            kv = f"Seg {r.customer_segment}, Q {q:.2f}, Hist {r.payment_history}, Ziel {r.payment_terms_days}"
            if "Versenden" not in acts:
                kv += f", Lief {lief:+d}"
            if "Rechnung stellen" in acts and "Zahlungseingang" not in acts:
                inv = ts[acts.index("Rechnung stellen")].date()
                kv += f", Verzug {(snap.date() - inv).days - int(r.payment_terms_days)}"
            kv += f", Warte {(snap.date() - ts[-1].date()).days}"
            txt = r.free_text if r.free_text else "-"
            if t == "E7":
                soll = "(Labeling)"
            else:
                soll = SETS.get(g.allowed_action_sets, g.allowed_action_sets)
                if g.free_text_category != "none":
                    soll += f" ({g.free_text_category})"
            L.append(f"| {cid} | {' > '.join(parts)} | {kv} | {txt.replace('|', '/')} | {soll} |")
        L.append("")
    (ROOT / "k2_stichprobe.md").write_text("\n".join(L), encoding="utf-8")
    print("geschrieben: k2_stichprobe.md")


if __name__ == "__main__":
    main()
