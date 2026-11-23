#!/usr/bin/env python3
"""
validate_log_v2.py | WI-Projekt Thema 75 | Prozess v2 (Entwurf) | v0.1

Prueft data/v2 gegen spec/spec_v2.yaml und die Ground Truth. Die Triggerauswertung kommt
aus src/detect_v2.py (unabhaengig vom Generator implementiert). Anders als v1 gibt es keine
dritte Triggerimplementierung: Generator und Erkennung muessen uebereinstimmen.

Aufruf aus dem Repo-Root:
  python src/validate_log_v2.py           # schreibt out/v2/generation_report.md
"""

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import yaml

from detect_v2 import evaluate
from validate_log import FMT, TS_RE, Report, read, sha, template_regexes

ROOT = Path(__file__).resolve().parent.parent
GENERATED = ["event_log.csv", "cases.csv", "ground_truth.csv"]
EXPECTED = {"none": set(), "E2": {"E2"}, "E3": {"E3"}, "E5": {"E5"}, "E6": {"E6"}, "E7": {"E2", "E3"},
            "E8": {"E8"}, "E9": {"E9"}, "E10": {"E10"}, "E11": {"E11"}, "E12": {"E12"}}
NEW_ACTS = ["Verfuegbarkeitspruefung", "Zahlung zuordnen", "Mahnung Stufe 2", "Ware nachbestellen",
            "Wareneingang Lager", "Reklamation erfassen", "Retoure erfassen", "Gutschrift erstellen",
            "Rechnung korrigieren", "Auftrag stornieren"]
AMOUNT_EVENT = {"invoice_amount": "Rechnung stellen", "credit_note_amount": "Gutschrift erstellen",
                "paid_amount": "Zahlungseingang"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default=str(ROOT / "spec" / "spec_v2.yaml"))
    ap.add_argument("--data", default=str(ROOT / "data" / "v2"))
    ap.add_argument("--templates", default=str(ROOT / "data" / "freitext_vorlagen.yaml"))
    ap.add_argument("--report", default=str(ROOT / "out" / "v2" / "generation_report.md"))
    ap.add_argument("--skip-repro", action="store_true")
    a = ap.parse_args()

    spec = yaml.safe_load(Path(a.spec).read_text(encoding="utf-8"))
    tpl = yaml.safe_load(Path(a.templates).read_text(encoding="utf-8"))
    data = Path(a.data)
    R = Report()

    ev = read(data, "event_log.csv")
    cs = read(data, "cases.csv")
    gt = read(data, "ground_truth.csv")

    # --- Struktur -----------------------------------------------------------
    R.check("event_log.csv Spalten", list(ev.columns) == ["case_id", "activity", "timestamp", "resource", "role"],
            ", ".join(ev.columns))
    R.check("cases.csv Spalten = case_id + spec.case_attributes",
            list(cs.columns) == ["case_id"] + list(spec["case_attributes"]), ", ".join(cs.columns))
    R.check("ground_truth.csv Spalten",
            list(gt.columns) == ["case_id", "exception_type", "free_text_category", "allowed_action_sets",
                                 "expected_target_role", "generator_tag"], ", ".join(gt.columns))
    R.check("case_id eindeutig und identisch in allen Dateien",
            cs.case_id.is_unique and gt.case_id.is_unique and set(cs.case_id) == set(gt.case_id) == set(ev.case_id))
    R.check("Timestamp-Format YYYY-MM-DD HH:MM:SS",
            ev.timestamp.str.match(TS_RE).all() and cs.snapshot_time.str.match(TS_RE).all())
    R.check("event_log ohne leere Felder", (ev != "").all().all())
    non_ascii = [f for f in GENERATED if not (data / f).read_bytes().isascii()]
    R.check("Daten rein ASCII", not non_ascii, ", ".join(non_ascii) or "alle ASCII")

    # --- Mengen -------------------------------------------------------------
    n = int(spec["data_generation"]["n_cases"])
    exp_counts = {("none" if k == "happy_path" else k): int(round(v * n))
                  for k, v in spec["data_generation"]["distribution"].items()}
    got = gt.exception_type.value_counts().to_dict()
    R.check("Anzahl pro Typ exakt", got == exp_counts,
            "; ".join(f"{k}: {got.get(k, 0)}/{v}" for k, v in exp_counts.items()))

    # --- Events -------------------------------------------------------------
    ev["ts"] = pd.to_datetime(ev.timestamp, format=FMT)
    snaps = dict(zip(cs.case_id, pd.to_datetime(cs.snapshot_time, format=FMT)))
    evg = {cid: g.reset_index(drop=True) for cid, g in ev.groupby("case_id", sort=False)}
    mono_bad = [c for c, g in evg.items() if (g.ts.diff().dropna() <= pd.Timedelta(0)).any()]
    after_snap = [c for c, g in evg.items() if g.ts.iloc[-1] > snaps[c]]
    first_bad = [c for c, g in evg.items() if g.activity.iloc[0] != "Auftrag erfassen"]
    off = ev[(ev.ts.dt.weekday >= 5) | (ev.ts.dt.hour < 8) | (ev.ts.dt.hour >= 17)].case_id.nunique()
    R.check("Timestamps pro Fall streng monoton", not mono_bad, f"{len(mono_bad)} Verstoesse")
    R.check("Keine Events nach dem Stichtag", not after_snap, f"{len(after_snap)} Verstoesse")
    R.check("Events nur Mo bis Fr, 08:00 bis 17:00", off == 0, f"{off} Faelle betroffen")
    R.check("Erstes Event = Auftrag erfassen", not first_bad, f"{len(first_bad)} Verstoesse")
    starts = ev.groupby("case_id").ts.min()
    R.check("Fallstart zwischen 2026-01-05 und 2026-06-30",
            starts.dt.date.between(date(2026, 1, 5), date(2026, 6, 30)).all(),
            f"{starts.min():%Y-%m-%d} bis {starts.max():%Y-%m-%d}")
    R.check("Kein Stichtag nach dem Datenabzug 2026-10-31", max(snaps.values()).date() <= date(2026, 10, 31),
            f"spaetester Stichtag {max(snaps.values()):%Y-%m-%d}")
    roles = spec["process"]["role_by_activity"]
    role_bad = ev[ev.activity.map(roles) != ev.role]
    R.check("Rolle je Aktivitaet = spec.process.role_by_activity", role_bad.empty, f"{len(role_bad)} Verstoesse")
    res_per_role = ev.groupby("role").resource.nunique()
    R.check("3 bis 4 Ressourcen pro Rolle", res_per_role.between(3, 4).all(),
            "; ".join(f"{k}: {v}" for k, v in res_per_role.items()))
    allowed = set(spec["process"]["happy_path"]) | set(spec["process"]["allowed_variants"])
    R.check("Nur Aktivitaeten aus spec.process", set(ev.activity) <= allowed,
            ", ".join(sorted(set(ev.activity) - allowed)) or "ok")
    missing = [x for x in NEW_ACTS if x not in set(ev.activity)]
    R.check("Alle neuen Aktivitaeten kommen im Log vor", not missing, ", ".join(missing) or "alle 10")

    # --- Attribute v2 -------------------------------------------------------
    acts = {c: set(g.activity) for c, g in evg.items()}
    cs_i = cs.set_index("case_id")
    gt_i = gt.set_index("case_id")
    amt_bad = []
    for col, act in AMOUNT_EVENT.items():
        for cid, v in cs_i[col].items():
            if (int(v) > 0) != (act in acts[cid]):
                amt_bad.append(f"{cid}:{col}")
    R.check("Betraege > 0 genau dann, wenn das zugehoerige Event im Log steht", not amt_bad,
            f"{len(amt_bad)} Verstoesse" + (": " + ", ".join(amt_bad[:5]) if amt_bad else ""))
    rs_bad = [c for c, v in cs_i.restock_date.items() if (v != "") != ("Ware nachbestellen" in acts[c])]
    R.check("restock_date gesetzt genau dann, wenn 'Ware nachbestellen' im Log steht", not rs_bad,
            f"{len(rs_bad)} Verstoesse")
    st_bad = [c for c, g in evg.items() if "Auftrag stornieren" in acts[c]
              and set(g.activity.iloc[list(g.activity).index("Auftrag stornieren") + 1:]) - {"Fall abschliessen"}]
    R.check("Nach 'Auftrag stornieren' hoechstens 'Fall abschliessen'", not st_bad, f"{len(st_bad)} Verstoesse")

    # --- Trigger gegen Ground Truth ----------------------------------------
    mism, type_bad, det = [], [], {}
    for cid in cs.case_id:
        r = evaluate(cs_i.loc[cid].to_dict(), [{"activity": x.activity, "timestamp": x.ts.to_pydatetime()}
                                               for x in evg[cid].itertuples()], snaps[cid].to_pydatetime())
        det[cid] = r
        et = gt_i.loc[cid, "exception_type"]
        exp = EXPECTED[et] | ({"E6"} if "chain_e6" in gt_i.loc[cid, "generator_tag"].split(";") else set())
        if set(r["hard_triggers"]) != exp:
            mism.append(f"{cid} ({et}): {sorted(r['hard_triggers'])}")
        if r["detected_type"] != et:
            type_bad.append(f"{cid} ({et} -> {r['detected_type']})")
    R.check("Trigger je Fall = Ground Truth (inkl. Ketten mit E6)", not mism,
            f"{len(mism)} Abweichungen" + (": " + ", ".join(mism[:8]) if mism else ""))
    R.check("Erkannter Typ nach Prioritaet = exception_type", not type_bad,
            f"{len(type_bad)} Abweichungen" + (": " + ", ".join(type_bad[:8]) if type_bad else ""))
    chains = gt[gt.generator_tag.str.contains("chain_e6")].exception_type.value_counts().to_dict()
    R.check("Kausale Ketten vorhanden (E8, E9, E11 jeweils mit E6)", all(chains.get(t, 0) > 0 for t in ("E8", "E9", "E11")),
            "; ".join(f"{k}+E6: {v}" for k, v in sorted(chains.items())))

    # --- Aktionsmengen und Zielrollen --------------------------------------
    ex = spec["exceptions"]
    set_bad, role_bad = [], []
    for cid, r in gt_i.iterrows():
        et, cat = r.exception_type, r.free_text_category
        if et == "none":
            exp, role = [["A0"]], ""
        elif et == "E6":
            exp = ex["E6"]["free_text_categories"][cat]["allowed_action_sets"]
            role = ex["E6"]["free_text_categories"][cat].get("target_role", "")
        else:
            exp = None if et == "E7" else ex[et]["allowed_action_sets"]
            role = ex[et].get("escalation_target") or ex[et].get("target_role") or ""
        if (exp is None and r.allowed_action_sets != "") or (exp is not None and json.loads(r.allowed_action_sets) != exp):
            set_bad.append(cid)
        if r.expected_target_role != role:
            role_bad.append(cid)
    R.check("allowed_action_sets entsprechen spec_v2", not set_bad, f"{len(set_bad)} Abweichungen")
    R.check("expected_target_role entspricht spec_v2", not role_bad,
            f"{len(role_bad)} Abweichungen; " + "; ".join(f"{k or '(leer)'}: {v}" for k, v in gt.expected_target_role.value_counts().items()))

    # --- Freitexte ----------------------------------------------------------
    regs = template_regexes(tpl)
    cat_bad = []
    for cid in cs.case_id:
        txt, cat = cs_i.loc[cid, "free_text"], gt_i.loc[cid, "free_text_category"]
        hits = {c for c, _, rg in regs if rg.match(txt)} if txt else {"none"}
        if hits != {cat}:
            cat_bad.append(cid)
    R.check("Freitext-Kategorie = Vorlagen-Kategorie (Regex-Abgleich)", not cat_bad, f"{len(cat_bad)} Abweichungen")
    e6c = gt[gt.exception_type == "E6"].free_text_category.value_counts().to_dict()
    R.check("E6: 20 Faelle je Kategorie", sorted(e6c.values()) == [20] * 4, "; ".join(f"{k}: {v}" for k, v in sorted(e6c.items())))

    # --- Happy Path ---------------------------------------------------------
    hp = gt[gt.exception_type == "none"]
    tags = hp.generator_tag.str.split(";")
    var_counts = pd.Series([t[8:] for ts in tags for t in ts if t.startswith("variant_")]).value_counts()
    bnd_counts = pd.Series([t[9:] for ts in tags for t in ts if t.startswith("boundary_")]).value_counts()
    done = sum("Fall abschliessen" in acts[c] for c in hp.case_id)
    R.check("Happy Path: alle 8 Varianten vorhanden", len(var_counts) == 8,
            "; ".join(f"{k}: {v}" for k, v in var_counts.items()))
    R.check("Happy Path: Grenzfaelle fuer E2, E3, E6, E9, E10, E11, E12", len(bnd_counts) == 7 and bnd_counts.min() >= 10,
            "; ".join(f"{k}: {v}" for k, v in bnd_counts.sort_index().items()))
    R.check("Info: Happy Path abgeschlossen", True, f"{done} von {len(hp)} ({done / len(hp):.1%})")

    # --- Reproduzierbarkeit -------------------------------------------------
    hashes = {f: sha(data / f) for f in GENERATED}
    if not a.skip_repro:
        same = True
        with tempfile.TemporaryDirectory() as td:
            subprocess.run([sys.executable, str(ROOT / "src" / "generate_log_v2.py"), "--spec", a.spec,
                            "--templates", a.templates, "--out", td], check=True, capture_output=True)
            for f in GENERATED:
                same &= sha(Path(td) / f) == hashes[f]
        R.check("Wiederholbarkeit: weiterer Lauf byte-identisch (SHA-256)", same,
                "; ".join(f"{f}: {h[:12]}" for f, h in hashes.items()))

    # --- Bericht ------------------------------------------------------------
    n_ok = sum(ok for _, ok, _ in R.rows)
    L = ["# Generation Report v2 (erweiterter Prozess, Entwurf)", "",
         f"Spec: `{Path(a.spec).name}` v{spec['meta']['version']}, Seed {spec['meta']['seed']}. "
         f"Faelle: {len(cs)}, Events: {len(ev)}, Aktivitaeten: {ev.activity.nunique()}.", "",
         f"**Ergebnis: {n_ok} von {len(R.rows)} Pruefungen bestanden.**", "",
         "Triggerlogik aus `src/detect_v2.py` (unabhaengig vom Generator).", "",
         "## Pruefungen", "", "| # | Pruefung | Ergebnis | Detail |", "|---|---|---|---|"]
    for i, (nm, ok, d) in enumerate(R.rows, 1):
        L.append(f"| {i} | {nm} | {'OK' if ok else 'FEHLER'} | {d.replace('|', '/')} |")
    m = cs.merge(gt[["case_id", "exception_type"]], on="case_id")
    m["n_events"] = m.case_id.map(ev.groupby("case_id").size())
    m["last"] = m.case_id.map(ev.groupby("case_id").activity.last())
    order = ["none", "E2", "E3", "E5", "E6", "E7", "E8", "E9", "E10", "E11", "E12"]
    L += ["", "## Typen", "", "| Typ | n | Events Mittel | Freitext |", "|---|---|---|---|"]
    for t in order:
        df = m[m.exception_type == t]
        L.append(f"| {t} | {len(df)} | {df.n_events.mean():.1f} | {(df.free_text != '').mean():.0%} |")
    st = pd.crosstab(m["last"], m.exception_type)[[t for t in order if t in set(m.exception_type)]]
    L += ["", "## Letzte Aktivitaet zum Stichtag je Typ", "",
          "| Letzte Aktivitaet | " + " | ".join(st.columns) + " |", "|---|" + "---|" * len(st.columns)]
    for idx, r in st.iterrows():
        L.append(f"| {idx} | " + " | ".join(str(v) for v in r.values) + " |")
    L.append("")
    Path(a.report).parent.mkdir(parents=True, exist_ok=True)
    Path(a.report).write_text("\n".join(L), encoding="utf-8")
    print(f"{n_ok}/{len(R.rows)} Pruefungen bestanden -> {a.report}")
    for nm, ok, d in R.rows:
        if not ok:
            print("FEHLER:", nm, "|", d)
    sys.exit(0 if n_ok == len(R.rows) else 1)


if __name__ == "__main__":
    main()
