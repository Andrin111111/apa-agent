#!/usr/bin/env python3
"""
metrics.py | WI-Projekt Thema 75 | v0.1 (Schritt 3, AP6)

Auswertung fuer jede Aktionsdatei im Format agent_output_schema (Baseline jetzt, Agent in Schritt 4/5).
Optionales Feld 'run' (int) pro Zeile: mehrere Durchlaeufe pro Fall (k Runs, Reproduzierbarkeit).

Kennzahlen (Kontextdokument Abschnitt 10, spec ground_truth_schema):
  1 Erkennungsguete       Precision/Recall pro Typ (detections.csv gegen ground_truth.csv)
  2 Aktionskorrektheit    exakter Mengenvergleich (D5) plus Rollenpruefung bei A5/A6 (role_check)
  3 Fehlalarme            Ebene Erkennung: Grenzfaelle (generator_tag boundary_*) mit detected_type != none
                          Ebene Agent: Happy Path mit Freitext, Aktionsmenge != {A0}
  4 Enthaltungsquote      Anteil Ausgaben mit exception_type = unknown
  5 Schema/Guardrail-Vorpruefung  Pflichtfelder, Enums, Begruendung >= 20 Zeichen, unknown -> A6, Rolle bei A5/A6
  6 Reproduzierbarkeit    nur bei mehreren Runs: Anteil Faelle mit identischer Aktionsmenge (inkl. Rollen) ueber alle Runs
  Getrennt nach deterministisch (E2, E3, E5) und Ermessen (E6, E7), Happy Path separat.

Bewertungsregeln (Annahmen M1 bis M4, im Bericht genannt):
  M1 Bewertet werden Ground-Truth-Faelle der Typen E2, E3, E6 und none-mit-Freitext. E5 wird informativ
     ausgewiesen (concept_only), E7 nicht (Ground Truth leer).
  M2 Nenner ist end-to-end: Ein bewerteter Fall ohne Ausgabe (nicht geroutet oder fehlend) zaehlt als falsch.
  M3 Aktionsmengen werden als Menge von action_id verglichen (Reihenfolge und Duplikate egal).
     Rollenpruefung: jede A5/A6 muss target_role = expected_target_role haben.
  M4 Enthaltung (unknown) zaehlt als nicht korrekt (spec abstention.evaluation), auch wenn A6 Teil einer
     zulaessigen Menge waere.

Aufruf:
  python src/metrics.py --actions out/baseline_actions.jsonl --label baseline
  -> out/metrics_baseline.md, out/metrics_baseline.json

Erweiterung Schritt 4 (Baseline-Zahlen unveraendert, Standard wie bisher):
  --scopes all,pilot (Standard) | e6_full (alle E6 laut Ground Truth, 80) | covered (Faelle mit Ausgabe)
  Beispiel E6-Zusatzlauf: python src/metrics.py --actions out/agent_actions_e6_t0.jsonl --label e6_t0 --scopes e6_full
  Vergleich Baseline:      python src/metrics.py --actions out/baseline_actions.jsonl --label baseline_e6 --scopes e6_full
  errors_<label>.csv enthaelt die Fehler des ersten Umfangs.
  --strict-guardrails: von Guardrails blockierte Ausgaben zaehlen als falsch (Grund guardrail_blockiert).
    Ohne Schalter wird die Rohentscheidung des Agenten bewertet (Standard, Entscheid Jan an K4).
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
TYPES = ["E2", "E3", "E5", "E6", "E7", "none"]
DETERMINISTIC = ["E2", "E3", "E5"]
JUDGEMENT = ["E6", "E7"]
EVALUATED = ["E2", "E3", "E6"]          # M1 (plus none mit Freitext)


# ---------- Laden ----------

def load_gt():
    gt = pd.read_csv(ROOT / "data" / "ground_truth.csv", keep_default_na=False)
    gt["allowed"] = gt.allowed_action_sets.apply(lambda s: [frozenset(x) for x in json.loads(s)] if s else [])
    cases = pd.read_csv(ROOT / "data" / "cases.csv", dtype={"free_text": str}, keep_default_na=False)
    gt = gt.merge(cases[["case_id", "free_text"]], on="case_id")
    gt["has_text"] = gt.free_text.str.strip() != ""
    return gt.set_index("case_id")


def load_actions(path):
    recs = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                r = {"_parse_error": True, "_line": i}
            r.setdefault("run", 1)
            recs.append(r)
    return recs


def load_spec():
    return yaml.safe_load((ROOT / "spec" / "spec.yaml").read_text(encoding="utf-8"))


# ---------- Pruefungen ----------

def schema_errors(r, spec):
    """Leichte Schema- und Guardrail-Vorpruefung ohne jsonschema-Bibliothek."""
    if r.get("_parse_error"):
        return ["json_parse"]
    s = spec["agent_output_schema"]["properties"]
    err = []
    for k in spec["agent_output_schema"]["required"]:
        if k not in r:
            err.append(f"missing:{k}")
    if r.get("exception_type") not in s["exception_type"]["enum"]:
        err.append("enum:exception_type")
    acts = r.get("actions") or []
    if not isinstance(acts, list) or len(acts) < 1:
        err.append("actions_empty")
        acts = []
    roles = s["actions"]["items"]["properties"]["target_role"]["enum"]
    for a in acts:
        if a.get("action_id") not in s["actions"]["items"]["properties"]["action_id"]["enum"]:
            err.append("action_not_in_catalog")
        if a.get("action_id") in ("A5", "A6") and a.get("target_role") not in roles:
            err.append("target_role_missing")
        if "target_role" in a and a["target_role"] not in roles:
            err.append("target_role_unknown")
    if len(str(r.get("rationale", ""))) < s["rationale"]["minLength"]:
        err.append("rationale_short")
    if not isinstance(r.get("key_evidence", []), list):
        err.append("key_evidence_type")
    if r.get("exception_type") == "unknown" and {a.get("action_id") for a in acts} != {"A6"}:
        err.append("unknown_requires_A6")
    return err


def action_set(r):
    return frozenset(a.get("action_id") for a in (r.get("actions") or []))


def signature(r):
    """Vergleichsschluessel fuer Reproduzierbarkeit: Typ, Aktionen und Rollen."""
    return (r.get("exception_type"),
            tuple(sorted((a.get("action_id"), a.get("target_role") or "") for a in (r.get("actions") or []))))


def judge(r, g):
    """Bewertet eine Ausgabe gegen die Ground Truth eines Falls. Rueckgabe (korrekt, grund)."""
    if r is None:
        return False, "keine_ausgabe"
    if r.get("_blocked"):                                # nur mit --strict-guardrails (Schritt 4)
        return False, "guardrail_blockiert"
    if r.get("exception_type") == "unknown":
        return False, "enthaltung"                       # M4
    aset = action_set(r)
    if aset not in g.allowed:
        return False, "aktionsmenge"
    for a in r.get("actions") or []:
        if a.get("action_id") in ("A5", "A6") and a.get("target_role") != g.expected_target_role:
            return False, "rolle"
    return True, "ok"


# ---------- Auswertung ----------

def detection_metrics(det, gt):
    m = det.merge(gt[["exception_type", "generator_tag"]], left_on="case_id", right_index=True)
    rows = []
    for t in TYPES:
        tp = int(((m.detected_type == t) & (m.exception_type == t)).sum())
        fp = int(((m.detected_type == t) & (m.exception_type != t)).sum())
        fn = int(((m.detected_type != t) & (m.exception_type == t)).sum())
        rows.append({"typ": t, "n_gt": int((m.exception_type == t).sum()), "tp": tp, "fp": fp, "fn": fn,
                     "precision": tp / (tp + fp) if tp + fp else None,
                     "recall": tp / (tp + fn) if tp + fn else None})
    boundary = m[m.generator_tag.str.contains("boundary_")]
    fa = boundary[boundary.detected_type != "none"]
    # Routing-Vollstaendigkeit: jede Ausnahme und jeder Fall mit Freitext muss beim Agenten ankommen
    must_route = m[(m.exception_type != "none") | m.case_id.map(gt.has_text)]
    not_routed = must_route[must_route.routed_to_agent.astype(str) != "True"]
    return {"per_type": rows, "boundary_n": len(boundary), "boundary_false_alarms": len(fa),
            "boundary_false_alarm_ids": fa.case_id.tolist(),
            "routing_required": len(must_route), "routing_missing": len(not_routed),
            "routed_total": int((m.routed_to_agent.astype(str) == "True").sum()),
            "confusion": pd.crosstab(m.exception_type, m.detected_type).to_dict()}


def action_metrics(recs, gt, spec, case_ids, full=False):
    runs = sorted({r["run"] for r in recs})
    by_run = {k: {} for k in runs}
    dup = 0
    for r in recs:
        cid = r.get("case_id")
        if cid in by_run[r["run"]]:
            dup += 1
        by_run[r["run"]][cid] = r
    in_scope = [c for c in case_ids if c in gt.index]

    scope_set = set(in_scope)
    # Im Gesamtumfang zaehlen auch Ausgaben mit unbekannter case_id und unlesbare Zeilen
    checked = [r for r in recs if r.get("case_id") in scope_set
               or (full and (r.get("_parse_error") or r.get("case_id") not in gt.index))]
    schema = defaultdict(int)
    for r in checked:
        errs = schema_errors(r, spec)
        if not r.get("_parse_error") and r.get("case_id") not in gt.index:
            errs.append("unknown_case_id")
        for e in errs:
            schema[e] += 1
    n_out = len(checked)
    invalid = sum(1 for r in checked if schema_errors(r, spec) or r.get("case_id") not in gt.index)

    def group_of(cid):
        g = gt.loc[cid]
        if g.exception_type == "none":
            return "none_text" if g.has_text else None    # Happy Path ohne Freitext wird nicht bewertet
        return g.exception_type

    per_run = []
    detail = []
    for k in runs:
        res = defaultdict(lambda: {"n": 0, "ok": 0, "reasons": defaultdict(int)})
        for cid in in_scope:
            grp = group_of(cid)
            if grp is None or grp == "E7":
                continue
            g = gt.loc[cid]
            ok, why = judge(by_run[k].get(cid), g)
            keys = [grp]
            if grp == "E6":
                keys.append(f"E6:{g.free_text_category}")
            for key in keys:
                res[key]["n"] += 1
                res[key]["ok"] += int(ok)
                res[key]["reasons"][why] += 1
            if not ok:
                r = by_run[k].get(cid)
                detail.append({"run": k, "case_id": cid, "gt_type": g.exception_type,
                               "gt_category": g.free_text_category, "grund": why,
                               "gt_allowed": g.allowed_action_sets, "gt_role": g.expected_target_role,
                               "out_type": r.get("exception_type") if r else "",
                               "out_actions": ";".join(f"{a.get('action_id')}{'/' + a['target_role'] if a.get('target_role') else ''}"
                                                       for a in (r.get("actions") or [])) if r else "",
                               "baseline_category": r.get("_baseline_category", "") if r else ""})
        # Aggregate
        agg = {}
        for name, members in [("deterministisch (E2, E3)", ["E2", "E3"]), ("Ermessen (E6)", ["E6"]),
                              ("Happy Path mit Freitext", ["none_text"]),
                              ("bewertet gesamt", ["E2", "E3", "E6", "none_text"])]:
            n = sum(res[m]["n"] for m in members)
            ok = sum(res[m]["ok"] for m in members)
            agg[name] = {"n": n, "ok": ok, "acc": ok / n if n else None}
        outs = [by_run[k][c] for c in in_scope if c in by_run[k]]
        abst = sum(1 for r in outs if r.get("exception_type") == "unknown")
        fa = res["none_text"]
        type_match = sum(1 for c in in_scope if c in by_run[k] and gt.loc[c].exception_type != "E7"
                         and by_run[k][c].get("exception_type") == gt.loc[c].exception_type)
        type_n = sum(1 for c in in_scope if c in by_run[k] and gt.loc[c].exception_type != "E7")
        per_run.append({"run": k, "groups": {g: {"n": v["n"], "ok": v["ok"], "acc": v["ok"] / v["n"] if v["n"] else None,
                                                 "reasons": dict(v["reasons"])} for g, v in sorted(res.items())},
                        "aggregate": agg, "outputs": len(outs),
                        "abstention": abst, "abstention_rate": abst / len(outs) if outs else None,
                        "agent_false_alarms": fa["n"] - fa["ok"], "agent_false_alarm_n": fa["n"],
                        "type_match": type_match, "type_n": type_n})

    repro = None
    if len(runs) > 1:
        same = 0
        considered = 0
        for cid in in_scope:
            sigs = [signature(by_run[k][cid]) if cid in by_run[k] else None for k in runs]
            if all(s is None for s in sigs):
                continue
            considered += 1
            same += int(len(set(sigs)) == 1)
        repro = {"cases": considered, "identical": same, "rate": same / considered if considered else None}

    return {"runs": runs, "per_run": per_run, "schema_errors": dict(schema), "outputs_checked": n_out,
            "invalid_outputs": invalid, "duplicates": dup, "reproducibility": repro, "errors": detail}


def info_e5(recs, gt, case_ids):
    """E5 nur informativ (concept_only)."""
    by = {r.get("case_id"): r for r in recs if r["run"] == min(r2["run"] for r2 in recs)}
    ids = [c for c in case_ids if c in gt.index and gt.loc[c].exception_type == "E5"]
    ok = sum(judge(by.get(c), gt.loc[c])[0] for c in ids)
    return {"n": len(ids), "ok": ok}


# ---------- Bericht ----------

def pct(x):
    return "n/a" if x is None else f"{100 * x:.1f} %"


def render(label, scopes, out_md):
    L = [f"# Metriken: {label}", "",
         "Erzeugt von `src/metrics.py`. Bewertungsregeln M1 bis M4 siehe Modulkopf.", ""]
    for scope_name, s in scopes.items():
        d, a = s["detection"], s["actions"]
        L += [f"## Umfang: {scope_name}", "", "### Erkennung", "",
              "| Typ | n (GT) | TP | FP | FN | Precision | Recall |", "|---|---|---|---|---|---|---|"]
        for r in d["per_type"]:
            if r["n_gt"] == 0 and r["fp"] == 0:
                continue
            L.append(f"| {r['typ']} | {r['n_gt']} | {r['tp']} | {r['fp']} | {r['fn']} | {pct(r['precision'])} | {pct(r['recall'])} |")
        L += ["", f"- Fehlalarme Erkennung (Grenzfaelle): {d['boundary_false_alarms']} von {d['boundary_n']}",
              f"- Routing: {d['routed_total']} Faelle an den Agenten, davon fehlend (muesste geroutet sein): {d['routing_missing']} von {d['routing_required']}", ""]
        for pr in a["per_run"]:
            L += [f"### Aktionen (Run {pr['run']})", "",
                  "| Gruppe | n | korrekt | Anteil | Fehlergruende |", "|---|---|---|---|---|"]
            for g, v in pr["groups"].items():
                reasons = ", ".join(f"{k}: {c}" for k, c in v["reasons"].items() if k != "ok") or "-"
                L.append(f"| {g} | {v['n']} | {v['ok']} | {pct(v['acc'])} | {reasons} |")
            L += ["", "| Aggregat | n | korrekt | Anteil |", "|---|---|---|---|"]
            for g, v in pr["aggregate"].items():
                L.append(f"| {g} | {v['n']} | {v['ok']} | {pct(v['acc'])} |")
            L += ["", f"- Fehlalarme Agent (Happy Path mit Freitext, Aktion != A0): {pr['agent_false_alarms']} von {pr['agent_false_alarm_n']}",
                  f"- Enthaltungsquote: {pr['abstention']} von {pr['outputs']} ({pct(pr['abstention_rate'])})",
                  f"- Typ-Uebereinstimmung der Ausgabe (ohne E7): {pr['type_match']} von {pr['type_n']}", ""]
        L += [f"- Schema/Guardrail-Vorpruefung: {a['invalid_outputs']} von {a['outputs_checked']} Ausgaben mit Fehlern {a['schema_errors'] or ''}",
              f"- Doppelte Ausgaben (gleicher Fall, gleicher Run): {a['duplicates']}",
              f"- Reproduzierbarkeit: {'nur 1 Run' if a['reproducibility'] is None else str(a['reproducibility']['identical']) + ' von ' + str(a['reproducibility']['cases']) + ' (' + pct(a['reproducibility']['rate']) + ')'}",
              f"- E5 (nur informativ, concept_only): {s['e5']['ok']} von {s['e5']['n']} korrekt", ""]
    Path(out_md).write_text("\n".join(L) + "\n", encoding="utf-8")


def scope_ids(scope, gt, recs):
    """Umfang -> (Name, Fall-IDs). Erweiterung Schritt 4."""
    if scope == "all":
        return "alle Faelle (1000)", gt.index.tolist()
    if scope == "pilot":
        return "Pilot (20)", pd.read_csv(ROOT / "data" / "pilot_sample.csv").case_id.tolist()
    if scope == "e6_full":
        ids = gt.index[gt.exception_type == "E6"].tolist()
        return f"E6 alle ({len(ids)})", ids
    if scope == "covered":
        have = {r.get("case_id") for r in recs}
        ids = [c for c in gt.index if c in have]
        return f"abgedeckte Faelle ({len(ids)})", ids
    raise ValueError(f"unbekannter Umfang {scope}")


def evaluate_file(actions_path, label, det_path=ROOT / "out" / "detections.csv", scopes_sel=("all", "pilot"),
                  strict_guardrails=False):
    spec = load_spec()
    gt = load_gt()
    det = pd.read_csv(det_path, keep_default_na=False)
    recs = load_actions(actions_path)
    if strict_guardrails:     # end-to-end: von Guardrails blockierte Ausgaben zaehlen als falsch
        recs = [{"case_id": r.get("case_id"), "run": r["run"], "_blocked": True}
                if r.get("_guardrail_ok") is False or r.get("_parse_error") else r for r in recs]
    scopes = {}
    for name, ids in [scope_ids(sc, gt, recs) for sc in scopes_sel]:
        gsub = gt.loc[ids]
        dsub = det[det.case_id.isin(ids)]
        scopes[name] = {"detection": detection_metrics(dsub, gsub),
                        "actions": action_metrics(recs, gt, spec, ids, full=name.startswith("alle")),
                        "e5": info_e5(recs, gt, ids)}
    return scopes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--actions", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--detections", default=str(ROOT / "out" / "detections.csv"))
    ap.add_argument("--scopes", default="all,pilot", help="Komma-Liste aus all, pilot, e6_full, covered")
    ap.add_argument("--strict-guardrails", action="store_true",
                    help="blockierte Ausgaben (_guardrail_ok false) zaehlen als falsch (end-to-end)")
    a = ap.parse_args()
    scopes = evaluate_file(a.actions, a.label, a.detections, [x.strip() for x in a.scopes.split(",") if x.strip()],
                           a.strict_guardrails)
    out_md = ROOT / "out" / f"metrics_{a.label}.md"
    render(a.label, scopes, out_md)
    errs = next(iter(scopes.values()))["actions"]["errors"]
    pd.DataFrame(errs).to_csv(ROOT / "out" / f"errors_{a.label}.csv", index=False)
    for s in scopes.values():
        s["detection"].pop("confusion", None)
    (ROOT / "out" / f"metrics_{a.label}.json").write_text(json.dumps(scopes, indent=1, default=str), encoding="utf-8")
    for name, s in scopes.items():
        pr = s["actions"]["per_run"][0]
        print(name, {k: f"{v['ok']}/{v['n']}" for k, v in pr["aggregate"].items()})
    print(f"-> {out_md}, out/errors_{a.label}.csv")


if __name__ == "__main__":
    main()
