#!/usr/bin/env python3
"""
validate_log.py | WI-Projekt Thema 75 | Schritt 2 (AP2) | v0.1

Prueft die generierten Daten gegen die Ground Truth. Die Triggerlogik ist hier
unabhaengig vom Generator implementiert (kein Import aus generate_log.py) und
arbeitet nur auf den CSV-Dateien.

Triggerauswertung auf Tagesbasis (Annahme, siehe Bericht):
  E2: order_value + open_items > credit_limit
  E3: (promised_delivery_date - Datum(snapshot_time)).days < days_threshold und kein "Versenden"
  E5: "Rechnung stellen" vorhanden und ("Versenden" fehlt oder liegt danach)
  E6: Datum(erste "Rechnung stellen") + payment_terms_days < Datum(snapshot_time) und kein "Zahlungseingang"
  E7: E2 und E3

Aufruf aus dem Repo-Root:
  python src/validate_log.py            # schreibt out/generation_report.md
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
GENERATED = ["event_log.csv", "cases.csv", "ground_truth.csv", "pilot_sample.csv", "labeling_e6_blind.csv"]
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
FMT = "%Y-%m-%d %H:%M:%S"
EXPECTED = {"none": set(), "E2": {"E2"}, "E3": {"E3"}, "E5": {"E5"}, "E6": {"E6"}, "E7": {"E2", "E3"}}

ERF, VERS, RECH, ZAHL, ERIN, TEIL, ABS = ("Auftrag erfassen", "Versenden", "Rechnung stellen",
                                         "Zahlungseingang", "Zahlungserinnerung", "Teillieferung",
                                         "Fall abschliessen")


class Report:
    def __init__(self):
        self.rows = []

    def check(self, name, ok, detail=""):
        self.rows.append((name, bool(ok), detail))
        return ok


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(data, name):
    return pd.read_csv(data / name, dtype=str, keep_default_na=False, encoding="utf-8")


def triggers(row, ev, thr):
    acts = list(ev["activity"])
    sd = datetime.strptime(row["snapshot_time"], FMT).date()
    t = set()
    if int(row["order_value"]) + int(row["open_items"]) > int(row["credit_limit"]):
        t.add("E2")
    if (date.fromisoformat(row["promised_delivery_date"]) - sd).days < thr and VERS not in acts:
        t.add("E3")
    if RECH in acts:
        ts = list(ev["ts"])
        t_r = ts[acts.index(RECH)]
        if VERS not in acts or t_r < ts[acts.index(VERS)]:
            t.add("E5")
        if ZAHL not in acts and t_r.date() + timedelta(days=int(row["payment_terms_days"])) < sd:
            t.add("E6")
    return t


def template_regexes(tpl):
    out = []
    for cat, lst in tpl["categories"].items():
        for t in lst:
            esc = re.escape(t["text"])
            pat = re.sub(r"\\\{(\w+)\\\}", ".+?", esc)
            out.append((cat, t["id"], re.compile("^" + pat + "$")))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default=str(ROOT / "spec" / "spec.yaml"))
    ap.add_argument("--data", default=str(ROOT / "data"))
    ap.add_argument("--report", default=str(ROOT / "out" / "generation_report.md"))
    ap.add_argument("--skip-repro", action="store_true")
    a = ap.parse_args()

    spec = yaml.safe_load(Path(a.spec).read_text(encoding="utf-8"))
    data = Path(a.data)
    tpl = yaml.safe_load((data / "freitext_vorlagen.yaml").read_text(encoding="utf-8"))
    thr = int(spec["exceptions"]["E3"]["params"]["days_threshold"])
    R = Report()

    ev = read(data, "event_log.csv")
    cs = read(data, "cases.csv")
    gt = read(data, "ground_truth.csv")
    pilot = read(data, "pilot_sample.csv")
    lab = read(data, "labeling_e6_blind.csv")

    # --- Struktur -----------------------------------------------------------
    R.check("event_log.csv Spalten", list(ev.columns) == ["case_id", "activity", "timestamp", "resource", "role"],
            ", ".join(ev.columns))
    exp_cols = ["case_id"] + list(spec["case_attributes"])
    R.check("cases.csv Spalten = case_id + spec.case_attributes", list(cs.columns) == exp_cols, ", ".join(cs.columns))
    leak_cols = [c for c in cs.columns if re.search(r"type|exception|label|tag|categ|truth", c, re.I)]
    R.check("cases.csv ohne typverratende Spalte", not leak_cols, ", ".join(leak_cols) or "keine")
    R.check("ground_truth.csv Spalten",
            list(gt.columns) == ["case_id", "exception_type", "free_text_category", "allowed_action_sets",
                                 "expected_target_role", "generator_tag"],
            ", ".join(gt.columns))
    R.check("case_id eindeutig (cases, ground_truth)", cs.case_id.is_unique and gt.case_id.is_unique)
    R.check("case_id-Mengen identisch (cases, ground_truth, event_log)",
            set(cs.case_id) == set(gt.case_id) == set(ev.case_id))
    R.check("Timestamp-Format YYYY-MM-DD HH:MM:SS (event_log, snapshot_time)",
            ev.timestamp.str.match(TS_RE).all() and cs.snapshot_time.str.match(TS_RE).all())
    R.check("event_log ohne leere Felder", (ev != "").all().all())
    non_ascii = [f for f in GENERATED if not (data / f).read_bytes().isascii()]
    R.check("Daten rein ASCII", not non_ascii, ", ".join(non_ascii) or "alle ASCII")

    # --- Mengen -------------------------------------------------------------
    n = int(spec["data_generation"]["n_cases"])
    dist = spec["data_generation"]["distribution"]
    exp_counts = {("none" if k == "happy_path" else k): int(round(v * n)) for k, v in dist.items()}
    got = gt.exception_type.value_counts().to_dict()
    R.check("Anzahl pro Typ exakt", got == exp_counts,
            "; ".join(f"{k}: {got.get(k, 0)}/{v}" for k, v in exp_counts.items()))

    # --- Events -------------------------------------------------------------
    ev["ts"] = pd.to_datetime(ev.timestamp, format=FMT)
    snaps = dict(zip(cs.case_id, pd.to_datetime(cs.snapshot_time, format=FMT)))
    mono_bad, after_snap, off_hours, first_bad, order_bad = [], [], [], [], []
    for cid, g in ev.groupby("case_id", sort=False):
        ts = list(g.ts)
        if any(ts[i] >= ts[i + 1] for i in range(len(ts) - 1)):
            mono_bad.append(cid)
        if ts[-1] > snaps[cid]:
            after_snap.append(cid)
        if g.activity.iloc[0] != ERF:
            first_bad.append(cid)
    wd = ev.ts.dt.weekday
    hr = ev.ts.dt.hour
    off_hours = ev[(wd >= 5) | (hr < 8) | (hr >= 17)].case_id.unique().tolist()
    R.check("Timestamps pro Fall streng monoton", not mono_bad, f"{len(mono_bad)} Verstoesse")
    R.check("Keine Events nach dem Stichtag", not after_snap, f"{len(after_snap)} Verstoesse")
    R.check("Events nur Mo bis Fr, 08:00 bis 17:00", not off_hours, f"{len(off_hours)} Faelle betroffen")
    R.check("Erstes Event = Auftrag erfassen", not first_bad, f"{len(first_bad)} Verstoesse")
    starts = ev.groupby("case_id").ts.min()
    R.check("Fallstart zwischen 2026-01-05 und 2026-06-30",
            (starts.dt.date >= date(2026, 1, 5)).all() and (starts.dt.date <= date(2026, 6, 30)).all(),
            f"{starts.min():%Y-%m-%d} bis {starts.max():%Y-%m-%d}")
    snap_max = max(snaps.values())
    R.check("Kein Stichtag nach dem Datenabzug 2026-10-31", snap_max.date() <= date(2026, 10, 31),
            f"spaetester Stichtag {snap_max:%Y-%m-%d}")
    role_map = ev.groupby("activity").role.unique()
    one_role = all(len(v) == 1 for v in role_map)
    R.check("Genau eine Rolle pro Aktivitaet", one_role,
            "; ".join(f"{k}: {v[0]}" for k, v in role_map.items()))
    res_per_role = ev.groupby("role").resource.nunique()
    R.check("3 bis 4 Ressourcen pro Rolle", res_per_role.between(3, 4).all(),
            "; ".join(f"{k}: {v}" for k, v in res_per_role.items()))
    acts_ok = set(ev.activity) <= set(spec["process"]["happy_path"]) | set(spec["process"]["allowed_variants"])
    R.check("Nur Aktivitaeten aus spec.process", acts_ok)

    # --- Trigger gegen Ground Truth ----------------------------------------
    evg = {cid: g.reset_index(drop=True) for cid, g in ev.groupby("case_id", sort=False)}
    cs_i = cs.set_index("case_id")
    gt_i = gt.set_index("case_id")
    mism = []
    trig = {}
    for cid in cs.case_id:
        row = cs_i.loc[cid]
        t = triggers(row, evg[cid], thr)
        trig[cid] = t
        et = gt_i.loc[cid, "exception_type"]
        if t != EXPECTED[et]:
            mism.append(f"{cid} ({et}): {sorted(t)}")
    R.check("Trigger je Fall entsprechen Ground Truth (unabhaengige Logik)", not mism,
            f"{len(mism)} Abweichungen" + (": " + ", ".join(mism[:10]) if mism else ""))

    # --- Aktionsmengen ------------------------------------------------------
    ex = spec["exceptions"]
    bad_sets = []
    for cid, r in gt_i.iterrows():
        et, cat, s = r.exception_type, r.free_text_category, r.allowed_action_sets
        if et == "none":
            exp = [["A0"]]
        elif et == "E6":
            exp = ex["E6"]["free_text_categories"][cat]["allowed_action_sets"]
        elif et == "E7":
            exp = None
        else:
            exp = ex[et]["allowed_action_sets"]
        if (exp is None and s != "") or (exp is not None and json.loads(s) != exp):
            bad_sets.append(cid)
    exp_role = {"E2": "Credit Management", "E5": "Buchhaltung"}
    role_bad = []
    for cid, r in gt_i.iterrows():
        if r.exception_type == "E6":
            e = {"complaint": "Kundendienst", "payment_difficulty": "Credit Management"}.get(r.free_text_category, "")
        else:
            e = exp_role.get(r.exception_type, "")
        if r.expected_target_role != e:
            role_bad.append(cid)
    R.check("expected_target_role korrekt (E2, E5, E6 complaint/difficulty, sonst leer)", not role_bad,
            f"{len(role_bad)} Abweichungen; " + "; ".join(f"{k or '(leer)'}: {v}" for k, v in gt.expected_target_role.value_counts().items()))
    R.check("allowed_action_sets entsprechen spec (none = [[A0]], E7 leer)", not bad_sets, f"{len(bad_sets)} Abweichungen")

    # --- Freitexte und Kategorien ------------------------------------------
    regs = template_regexes(tpl)
    cat_bad, multi = [], []
    for cid in cs.case_id:
        txt = cs_i.loc[cid, "free_text"]
        cat = gt_i.loc[cid, "free_text_category"]
        if txt == "":
            if cat != "none":
                cat_bad.append(cid)
            continue
        hits = {c for c, _, rg in regs if rg.match(txt)}
        if len(hits) != 1:
            multi.append(cid)
        elif hits.pop() != cat:
            cat_bad.append(cid)
    R.check("Freitext-Kategorie = Vorlagen-Kategorie (Regex-Abgleich)", not cat_bad and not multi,
            f"{len(cat_bad)} falsch, {len(multi)} nicht eindeutig")
    e6 = gt[gt.exception_type == "E6"]
    e6c = e6.free_text_category.value_counts().to_dict()
    R.check("E6: 20 Faelle je Kategorie", all(v == 20 for v in e6c.values()) and len(e6c) == 4,
            "; ".join(f"{k}: {v}" for k, v in sorted(e6c.items())))
    R.check("E6: jeder Fall hat Freitext", (cs_i.loc[e6.case_id, "free_text"] != "").all())
    hp_ids = gt[gt.exception_type == "none"].case_id
    hp_text = (cs_i.loc[hp_ids, "free_text"] != "")
    R.check("Happy Path: Rauschen 10 % mit irrelevantem Freitext",
            hp_text.sum() == round(0.10 * len(hp_ids)) and
            (gt_i.loc[hp_ids[hp_text.values], "free_text_category"] == "irrelevant").all(),
            f"{hp_text.sum()} von {len(hp_ids)}")
    noise_other = gt[(~gt.exception_type.isin(["none", "E6"])) & (cs_i.loc[gt.case_id, "free_text"].values != "")]
    R.check("Info: irrelevanter Freitext in E2/E3/E5/E7 (Abweichung)", True,
            f"{len(noise_other)} Faelle: " + "; ".join(f"{k}: {v}" for k, v in noise_other.exception_type.value_counts().sort_index().items()))

    # Vorlagen
    tcheck = []
    for cat, lst in tpl["categories"].items():
        styles = pd.Series([t["stil"] for t in lst]).value_counts().to_dict()
        n_ind = styles.get("indirekt", 0) + styles.get("distraktor", 0)
        meta_ok = all(isinstance(t.get("source"), str) and t["source"] and t.get("reviewed_by_jan") in (True, False) for t in lst)
        ascii_ok = all(t["text"].isascii() for t in lst)
        tcheck.append((cat, len(lst), n_ind, meta_ok, ascii_ok))
    R.check("Vorlagen: ca. 10 je Kategorie, mind. 3 indirekt/Distraktor, Metadaten, ASCII",
            all(8 <= n_ <= 12 and ni >= 3 and m and s for _, n_, ni, m, s in tcheck),
            "; ".join(f"{c}: {n_} Vorlagen, {ni} indirekt/Distraktor" for c, n_, ni, _, _ in tcheck))

    # --- Happy-Path-Struktur ------------------------------------------------
    hp_acts = {cid: list(evg[cid].activity) for cid in hp_ids}
    completed = sum(ABS in v for v in hp_acts.values())
    with_var = sum(any(x in v for x in ("Auftrag aendern", TEIL, ERIN)) for v in hp_acts.values())
    R.check("Happy Path: ca. 60 % abgeschlossen", abs(completed / len(hp_ids) - 0.6) <= 0.02,
            f"{completed} von {len(hp_ids)} ({completed / len(hp_ids):.1%})")
    R.check("Happy Path: ca. 25 % mit Variante", abs(with_var / len(hp_ids) - 0.25) <= 0.02,
            f"{with_var} von {len(hp_ids)} ({with_var / len(hp_ids):.1%})")
    erin_bad = [c for c, v in hp_acts.items() if ERIN in v and (ZAHL not in v or v.index(ERIN) > v.index(ZAHL))]
    R.check("Zahlungserinnerung nur mit Zahlungseingang vor Stichtag", not erin_bad, f"{len(erin_bad)} Verstoesse")
    e6_rem = sum(ERIN in list(evg[c].activity) for c in gt[gt.exception_type == "E6"].case_id)
    R.check("Info: E6 mit Zahlungserinnerung (ab 11 Tagen Verzug)", True, f"{e6_rem} von 80")
    teil_bad = [c for c, g in evg.items() if TEIL in list(g.activity) and VERS not in list(g.activity)]
    R.check("Teillieferung nur zusammen mit Versenden (keine E3-Mehrdeutigkeit)", not teil_bad, f"{len(teil_bad)} Verstoesse")
    max_aend = max(list(g.activity).count("Auftrag aendern") for g in evg.values())
    R.check("Auftrag aendern hoechstens 2 mal (E4 nicht erzeugt)", max_aend <= 2, f"Maximum {max_aend}")

    # Grenzfaelle aus den Daten (nicht aus den Tags)
    b_e2 = b_e3 = b_e6 = 0
    for cid in hp_ids:
        r = cs_i.loc[cid]
        g = evg[cid]
        acts = list(g.activity)
        sd = datetime.strptime(r.snapshot_time, FMT).date()
        if int(r.order_value) + int(r.open_items) == int(r.credit_limit):
            b_e2 += 1
        if VERS not in acts and (date.fromisoformat(r.promised_delivery_date) - sd).days == thr:
            b_e3 += 1
        if RECH in acts and ZAHL not in acts:
            inv = g.ts[acts.index(RECH)].date()
            if inv + timedelta(days=int(r.payment_terms_days)) == sd:
                b_e6 += 1
    R.check("Happy Path: ca. 5 % Grenzfaelle knapp unter der Schwelle", 30 <= b_e2 + b_e3 + b_e6 <= 40,
            f"Summe = Limit: {b_e2}; Liefertermin = Stichtag + {thr} Tage: {b_e3}; Stichtag = Faelligkeit: {b_e6}")

    # E-Typ-Details
    e3_ids = gt[gt.exception_type == "E3"].case_id
    deltas = [(date.fromisoformat(cs_i.loc[c, "promised_delivery_date"]) -
               datetime.strptime(cs_i.loc[c, "snapshot_time"], FMT).date()).days for c in e3_ids]
    neg = sum(d < 0 for d in deltas)
    R.check("E3: negative Differenzen (Termin ueberschritten) vorhanden", neg > 0,
            f"Delta min {min(deltas)}, max {max(deltas)}, negativ: {neg} von {len(deltas)}")
    e3_stage = pd.Series([evg[c].activity.iloc[-1] for c in e3_ids]).value_counts().to_dict()
    R.check("E3: Fall steht in Kommissionieren oder davor", "Versenden" not in e3_stage,
            "; ".join(f"{k}: {v}" for k, v in e3_stage.items()))
    e6_od = []
    for c in e6.case_id:
        g = evg[c]
        inv = g.ts[list(g.activity).index(RECH)].date()
        sd = datetime.strptime(cs_i.loc[c, "snapshot_time"], FMT).date()
        e6_od.append((sd - inv).days - int(cs_i.loc[c, "payment_terms_days"]))
    R.check("E6: ueberfaellig 1 bis 45 Tage", min(e6_od) >= 1 and max(e6_od) <= 45,
            f"min {min(e6_od)}, max {max(e6_od)}, Median {pd.Series(e6_od).median():.0f}")
    for t in ("E2", "E7"):
        ids = gt[gt.exception_type == t].case_id
        rr = [(int(cs_i.loc[c, "order_value"]) + int(cs_i.loc[c, "open_items"])) / int(cs_i.loc[c, "credit_limit"]) for c in ids]
        R.check(f"{t}: Ueberschreitung von knapp bis stark", min(rr) > 1 and max(rr) > 1.25,
                f"Quote min {min(rr):.4f}, Median {pd.Series(rr).median():.3f}, max {max(rr):.3f}")

    # --- Pilot --------------------------------------------------------------
    p = gt_i.loc[pilot.case_id]
    pc = p.exception_type.value_counts().to_dict()
    p_e6_cats = set(p[p.exception_type == "E6"].free_text_category)
    p_hp = p[p.exception_type == "none"]
    p_hp_noise = int((cs_i.loc[p_hp.index, "free_text"] != "").sum())
    ok = (len(pilot) == spec["pilot"]["n_cases"] and pc.get("E2") == 4 and pc.get("E3") == 4 and pc.get("E6") == 6
          and pc.get("none") == 6 and p_hp_noise == 3 and len(p_e6_cats) == 4
          and not (set(pc) & set(spec["pilot"]["exclude_types"])))
    p_e6 = p[p.exception_type == "E6"].free_text_category.value_counts().sort_index().to_dict()
    p_other_noise = int(((p.exception_type.isin(["E2", "E3"])) & (cs_i.loc[p.index, "free_text"] != "")).sum())
    R.check("pilot_sample.csv: 4 E2, 4 E3, 6 E6 (alle Kategorien), 6 HP (3 mit Freitext), kein E5/E7", ok,
            f"{pc}; E6: {p_e6}; HP mit Freitext: {p_hp_noise}; E2/E3 mit Freitext: {p_other_noise}")

    # --- Labeling -----------------------------------------------------------
    lab_ok = (list(lab.columns) == ["case_id", "free_text", "label"] and len(lab) == 15
              and (gt_i.loc[lab.case_id, "exception_type"] == "E6").all() and (lab.label == "").all()
              and (cs_i.loc[lab.case_id, "free_text"].values == lab.free_text.values).all())
    lab_cats = gt_i.loc[lab.case_id, "free_text_category"].value_counts().sort_index().to_dict()
    R.check("labeling_e6_blind.csv: 15 E6-Faelle, ohne Kategorie, Label leer", lab_ok,
            f"Kategorien (nur im Bericht sichtbar): {lab_cats}")

    # --- Reproduzierbarkeit -------------------------------------------------
    hashes = {f: sha(data / f) for f in GENERATED}
    if not a.skip_repro:
        same = True
        for run in (1, 2):
            with tempfile.TemporaryDirectory() as td:
                subprocess.run([sys.executable, str(ROOT / "src" / "generate_log.py"), "--spec", a.spec,
                                "--templates", str(data / "freitext_vorlagen.yaml"), "--out", td],
                               check=True, capture_output=True)
                for f in GENERATED:
                    same &= sha(Path(td) / f) == hashes[f]
        R.check("Wiederholbarkeit: 2 weitere Laeufe byte-identisch (SHA-256)", same,
                "; ".join(f"{f}: {h[:12]}" for f, h in hashes.items()))

    # --- Verteilungsvergleich (Leakage) ------------------------------------
    m = cs.merge(gt[["case_id", "exception_type"]], on="case_id")
    for col in ("order_value", "credit_limit", "open_items", "payment_terms_days"):
        m[col] = m[col].astype(int)
    m["quote"] = (m.order_value + m.open_items) / m.credit_limit
    m["n_events"] = m.case_id.map(ev.groupby("case_id").size())
    m["has_text"] = m.free_text != ""
    m["lead_days"] = [(date.fromisoformat(r.promised_delivery_date) - starts[r.case_id].date()).days for r in m.itertuples()]
    order = ["none", "E2", "E3", "E5", "E6", "E7", "alle"]

    def stats(df):
        n_ = len(df)
        sh = lambda col, v: f"{(df[col] == v).mean():.0%}"
        return [n_, sh("customer_segment", "A"), sh("customer_segment", "B"), sh("customer_segment", "C"),
                sh("payment_history", "gut"), sh("payment_history", "mittel"), sh("payment_history", "schlecht"),
                f"{df.payment_terms_days.mean():.1f}", f"{df.order_value.median():,.0f}".replace(",", "'"),
                f"{df.order_value.mean():,.0f}".replace(",", "'"),
                f"{df.credit_limit.median():,.0f}".replace(",", "'"), f"{df.quote.median():.2f}",
                f"{df.has_text.mean():.0%}", f"{df.n_events.mean():.1f}", f"{df.lead_days.median():.0f}"]

    hdr = ["Typ", "n", "Seg A", "Seg B", "Seg C", "Hist gut", "mittel", "schlecht", "Ziel (Tage)",
           "Wert Median", "Wert Mittel", "Limit Median", "Quote Median", "Freitext", "Events", "Lieferfrist Median (Tage)"]
    rows = []
    for t in order:
        df = m if t == "alle" else m[m.exception_type == t]
        rows.append([t] + stats(df))

    # --- Bericht ------------------------------------------------------------
    n_ok = sum(ok for _, ok, _ in R.rows)
    L = ["# Generation Report (Schritt 2, Log-Generator)", "",
         f"Spec: `{Path(a.spec).name}` v{spec['meta']['version']}, Seed {spec['meta']['seed']}. "
         f"Faelle: {len(cs)}, Events: {len(ev)}.", "",
         f"**Ergebnis: {n_ok} von {len(R.rows)} Pruefungen bestanden.**", "",
         "Triggerlogik in `src/validate_log.py` unabhaengig vom Generator, Auswertung auf Tagesbasis.", "",
         "## Pruefungen", "", "| # | Pruefung | Ergebnis | Detail |", "|---|---|---|---|"]
    for i, (nm, ok, det) in enumerate(R.rows, 1):
        L.append(f"| {i} | {nm} | {'OK' if ok else 'FEHLER'} | {det.replace('|', '/')} |")
    L += ["", "## Verteilungsvergleich der Kernattribute (Leakage-Pruefung)", "",
          "Quote = (order_value + open_items) / credit_limit. Lieferfrist = promised_delivery_date minus Fallstart.", "",
          "| " + " | ".join(hdr) + " |", "|" + "---|" * len(hdr)]
    for r in rows:
        L.append("| " + " | ".join(str(x) for x in r) + " |")
    L += ["", "Erwartete Unterschiede (durch Trigger bestimmt): Quote bei E2/E7 > 1; Freitext bei E6 100 %; "
          "Eventanzahl und Lieferfrist haengen vom Prozessstand zum Stichtag ab.", ""]
    last_act = ev.groupby("case_id").activity.last()
    m["last"] = m.case_id.map(last_act)
    st = pd.crosstab(m["last"], m.exception_type)
    L += ["## Letzte Aktivitaet zum Stichtag je Typ", "", "| Letzte Aktivitaet | " + " | ".join(st.columns) + " |",
          "|---|" + "---|" * len(st.columns)]
    for idx, r in st.iterrows():
        L.append(f"| {idx} | " + " | ".join(str(v) for v in r.values) + " |")
    L.append("")
    Path(a.report).parent.mkdir(parents=True, exist_ok=True)
    Path(a.report).write_text("\n".join(L), encoding="utf-8")
    print(f"{n_ok}/{len(R.rows)} Pruefungen bestanden -> {a.report}")
    for nm, ok, det in R.rows:
        if not ok:
            print("FEHLER:", nm, "|", det)
    sys.exit(0 if n_ok == len(R.rows) else 1)


if __name__ == "__main__":
    main()
