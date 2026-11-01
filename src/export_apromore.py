#!/usr/bin/env python3
"""
export_apromore.py | WI-Projekt Thema 75 | v0.1 (AP7, Apromore-Visualisierung)

Bereitet data/event_log.csv fuer den manuellen Import in Apromore vor. Nur Visualisierung fuer die
Folien. Erkennung und Auswertung laufen weiterhin ueber PM4Py bzw. src/detect.py und src/metrics.py.

Ausgaben (Ordner out/apromore/):
  apromore_events.csv         alle 1000 Faelle, Events angereichert mit Fallattributen
  apromore_events_closed.csv  nur abgeschlossene Faelle (letzte Aktivitaet "Fall abschliessen")
  export_report.md            Kennzahlen und haeufigste Varianten zum Abgleich mit der Apromore-Ansicht

Zusatzspalten pro Event (aus cases.csv und ground_truth.csv, je Fall konstant):
  order_value, customer_segment, credit_limit, open_items, payment_history, payment_terms_days,
  promised_delivery_date, has_free_text (ja/nein, Freitext selbst wird nicht exportiert),
  case_status (abgeschlossen/laufend), exception_type (none, E2, E3, E5, E6, E7),
  exception_class (happy_path, deterministisch, ermessen)
  Mit --no-labels entfallen exception_type und exception_class (z.B. fuer eine neutrale Ansicht).

Nur Standardbibliothek. Daten werden nicht veraendert, nur gelesen.

Aufruf (aus dem Repo-Root):
  python src/export_apromore.py
  python src/export_apromore.py --no-labels
"""

import argparse
import csv
import os
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLOSING_ACTIVITY = "Fall abschliessen"
CASE_ATTRS = [
    "order_value", "customer_segment", "credit_limit", "open_items", "payment_history",
    "payment_terms_days", "promised_delivery_date",
]
EXCEPTION_CLASS = {
    "none": "happy_path",
    "E2": "deterministisch", "E3": "deterministisch", "E5": "deterministisch",
    "E6": "ermessen", "E7": "ermessen",
}


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def build(events, cases, truth, with_labels):
    case_info = {c["case_id"]: c for c in cases}
    truth_info = {t["case_id"]: t for t in truth}

    by_case = defaultdict(list)
    for e in events:
        by_case[e["case_id"]].append(e)
    for evs in by_case.values():
        evs.sort(key=lambda e: e["timestamp"])  # stabil: Reihenfolge im Log bei gleichem Zeitstempel

    missing = sorted(set(by_case) - set(case_info))
    if missing:
        raise SystemExit(f"FEHLER: Faelle ohne Eintrag in cases.csv: {missing[:5]}")

    rows, closed_ids, ties = [], set(), []
    for cid in sorted(by_case):
        evs = by_case[cid]
        status = "abgeschlossen" if evs[-1]["activity"] == CLOSING_ACTIVITY else "laufend"
        if status == "abgeschlossen":
            closed_ids.add(cid)
        stamps = [e["timestamp"] for e in evs]
        if len(stamps) != len(set(stamps)):
            ties.append(cid)
        c = case_info[cid]
        extra = {k: c[k] for k in CASE_ATTRS}
        extra["has_free_text"] = "ja" if c.get("free_text", "").strip() else "nein"
        extra["case_status"] = status
        if with_labels:
            et = truth_info.get(cid, {}).get("exception_type", "none")
            extra["exception_type"] = et
            extra["exception_class"] = EXCEPTION_CLASS.get(et, "unbekannt")
        for e in evs:
            rows.append({**{k: e[k] for k in ("case_id", "activity", "timestamp", "resource", "role")}, **extra})
    return rows, closed_ids, ties


def variants(rows):
    seq = defaultdict(list)
    for r in rows:
        seq[r["case_id"]].append(r["activity"])
    return Counter(" > ".join(s) for s in seq.values())


def report(path, rows, closed_rows, ties, with_labels):
    n_cases = len({r["case_id"] for r in rows})
    n_closed = len({r["case_id"] for r in closed_rows})
    v_all, v_closed = variants(rows), variants(closed_rows)
    lines = [
        "# Apromore-Export (AP7)",
        "",
        "Erzeugt mit `python src/export_apromore.py`" + ("" if with_labels else " --no-labels") + ".",
        "Zahlen dienen dem Abgleich: Apromore sollte nach dem Import dieselben Werte zeigen.",
        "",
        "| Datei | Faelle | Events | Varianten |",
        "|---|---|---|---|",
        f"| `apromore_events.csv` | {n_cases} | {len(rows)} | {len(v_all)} |",
        f"| `apromore_events_closed.csv` | {n_closed} | {len(closed_rows)} | {len(v_closed)} |",
        "",
        f"Zeitraum: {min(r['timestamp'] for r in rows)} bis {max(r['timestamp'] for r in rows)}.",
        f"Faelle mit gleichem Zeitstempel bei zwei Events: {len(ties)}"
        + (f" (z.B. {', '.join(ties[:5])}). Apromore kann die Reihenfolge dort anders zeigen." if ties else "."),
        "",
        "Aktivitaeten:",
        "",
        "| Aktivitaet | Events |",
        "|---|---|",
    ]
    for act, n in Counter(r["activity"] for r in rows).most_common():
        lines.append(f"| {act} | {n} |")
    for title, v, total in (("alle Faelle", v_all, n_cases), ("abgeschlossene Faelle", v_closed, n_closed)):
        lines += ["", f"Top 10 Varianten, {title}:", "", "| # | Faelle | Anteil | Abfolge |", "|---|---|---|---|"]
        for i, (s, n) in enumerate(v.most_common(10), 1):
            lines.append(f"| {i} | {n} | {n / total:.1%} | {s} |")
    if with_labels:
        lines += ["", "Faelle pro Ausnahmetyp (alle / abgeschlossen):", "", "| Typ | alle | abgeschlossen |", "|---|---|---|"]
        per_all = Counter({r["case_id"]: r["exception_type"] for r in rows}.values())
        per_closed = Counter({r["case_id"]: r["exception_type"] for r in closed_rows}.values())
        for et in sorted(per_all):
            lines.append(f"| {et} | {per_all[et]} | {per_closed.get(et, 0)} |")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser(description="Event Log fuer Apromore aufbereiten (AP7)")
    ap.add_argument("--data", default=os.path.join(ROOT, "data"))
    ap.add_argument("--out", default=os.path.join(ROOT, "out", "apromore"))
    ap.add_argument("--no-labels", action="store_true", help="exception_type/exception_class weglassen")
    args = ap.parse_args()
    with_labels = not args.no_labels

    events = read_csv(os.path.join(args.data, "event_log.csv"))
    cases = read_csv(os.path.join(args.data, "cases.csv"))
    truth = read_csv(os.path.join(args.data, "ground_truth.csv")) if with_labels else []

    rows, closed_ids, ties = build(events, cases, truth, with_labels)
    closed_rows = [r for r in rows if r["case_id"] in closed_ids]
    fields = list(rows[0].keys())

    os.makedirs(args.out, exist_ok=True)
    write_csv(os.path.join(args.out, "apromore_events.csv"), rows, fields)
    write_csv(os.path.join(args.out, "apromore_events_closed.csv"), closed_rows, fields)
    report(os.path.join(args.out, "export_report.md"), rows, closed_rows, ties, with_labels)

    rel = os.path.relpath(args.out, ROOT)
    print(f"{rel}/apromore_events.csv: {len({r['case_id'] for r in rows})} Faelle, {len(rows)} Events")
    print(f"{rel}/apromore_events_closed.csv: {len(closed_ids)} Faelle, {len(closed_rows)} Events")
    print(f"{rel}/export_report.md geschrieben. Faelle mit gleichem Zeitstempel: {len(ties)}")


if __name__ == "__main__":
    main()
