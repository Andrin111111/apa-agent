#!/usr/bin/env python3
"""
step5_eval.py | WI-Projekt Thema 75 | v1.0 (Schritt 5, AP6)

Zusatzauswertung der Agentenlaeufe, die metrics.py nicht liefert. Liest nur, aendert keine Eingaben.
Bewertung identisch mit metrics.py (judge, M1 bis M4), roh und strikt (blockierte Ausgabe = falsch).

  1 Aktionskorrektheit nach Typ und Run (roh, strikt), Laeufe pilot_t0, pilot_t07 (Pilot) und e6_t0 (E6 alle)
  2 E6 nach Textstil (direkt, indirekt, distraktor) und Kategorie, Agent vs. Baseline, gepaarter Vergleich
    (exakter McNemar-Test), zusaetzlich pro Vorlage (Faelle teilen Vorlagen)
  3 Reproduzierbarkeit: identische Ausgabe (Typ, Aktionen, Rollen) ueber k Runs, T = 0 und T = 0,7,
    dazu Querpruefung gleicher Konfiguration ueber Sitzungen (smoke_v12, pilot_t0, e6_t0)
  4 Enthaltungen, Guardrails, Dispositionen, Laufzeit und Tokens aus dem Audit-Log
  5 Fehlerliste (alle falschen Rohentscheidungen) -> out/step5_errors.csv
  6 Stichprobe K5 (Begruendungsraster 0 bis 2): out/k5_stichprobe.md|csv (blind), out/k5_key.csv (Schluessel)

Aufruf:  python src/step5_eval.py   -> out/step5_tables.md, out/step5_errors.csv, out/k5_*
"""

import json
import math
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

import metrics

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
RUNS = {"pilot_t0": "pilot", "pilot_t07": "pilot", "e6_t0": "e6_full"}
GROUP_ORDER = ["E2", "E3", "E6", "none_text"]
GROUP_NAME = {"E2": "E2", "E3": "E3", "E6": "E6", "none_text": "Happy Path mit Freitext"}
K5_SEED = 42


# ---------- Laden ----------

def load_gt():
    gt = metrics.load_gt()
    tags = gt.generator_tag.str.split(";")
    gt["stil"] = tags.apply(lambda t: next((x[5:] for x in t if x.startswith("text_")), ""))
    gt["tpl"] = tags.apply(lambda t: next((x[4:] for x in t if x.startswith("tpl_")), ""))
    return gt


def load_audit(labels):
    """Letzter fehlerfreier Eintrag pro (Label, Fall, Run). Transportfehler separat gezaehlt."""
    entries, errors = {}, Counter()
    with open(OUT / "audit_log.jsonl", encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)
            if e.get("label") not in labels:
                continue
            if e.get("error"):
                errors[e["label"]] += 1
                continue
            entries[(e["label"], e["case_id"], e["run"])] = e
    return entries, errors


def group_of(g):
    if g.exception_type == "none":
        return "none_text" if g.has_text else None
    return g.exception_type if g.exception_type in metrics.EVALUATED else None


def scope_ids(scope, gt):
    if scope == "pilot":
        return pd.read_csv(ROOT / "data" / "pilot_sample.csv").case_id.tolist()
    return gt.index[gt.exception_type == "E6"].tolist()


def by_run(recs):
    d = defaultdict(dict)
    for r in recs:
        d[r["run"]][r.get("case_id")] = r
    return d


def strict(r):
    if r is None:
        return None
    if r.get("_guardrail_ok") is False or r.get("_parse_error"):
        return {"case_id": r.get("case_id"), "run": r["run"], "_blocked": True}
    return r


def fmt_actions(r):
    if not r:
        return ""
    if r.get("_parse_error"):
        return "PARSEFEHLER"
    return "+".join(f"{a.get('action_id')}{'/' + a['target_role'] if a.get('target_role') else ''}"
                    for a in sorted(r.get("actions") or [], key=lambda a: a.get("action_id") or ""))


def pct(ok, n):
    return "n/a" if not n else f"{100 * ok / n:.1f} %"


def mcnemar_exact(b, c):
    """Zweiseitiger exakter McNemar-Test (Binomial auf diskordanten Paaren, p = 0,5)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * p)


# ---------- 1 Aktionskorrektheit ----------

def correctness(gt, data):
    rows = []
    for label, scope in RUNS.items():
        ids = scope_ids(scope, gt)
        br = by_run(data[label])
        for k in sorted(br):
            for cid in ids:
                g = gt.loc[cid]
                grp = group_of(g)
                if grp is None:
                    continue
                r = br[k].get(cid)
                ok_raw, why_raw = metrics.judge(r, g)
                ok_str, why_str = metrics.judge(strict(r), g)
                rows.append({"label": label, "run": k, "case_id": cid, "group": grp,
                             "category": g.free_text_category, "stil": g.stil, "tpl": g.tpl,
                             "ok_raw": ok_raw, "why_raw": why_raw, "ok_strict": ok_str, "why_strict": why_str,
                             "out_type": (r or {}).get("exception_type", ""), "out_actions": fmt_actions(r),
                             "gt_allowed": g.allowed_action_sets, "gt_role": g.expected_target_role,
                             "gt_type": g.exception_type, "rationale": (r or {}).get("rationale", ""),
                             "key_evidence": " | ".join((r or {}).get("key_evidence") or []),
                             "violations": ";".join((r or {}).get("_violations") or [])})
    return pd.DataFrame(rows)


def table_correctness(df):
    L = ["## 1 Aktionskorrektheit nach Typ (roh / strikt)", "",
         "Pro Run: korrekt von n. Pilot: 3 Runs. E6-Zusatzlauf: 1 Run.", "",
         "| Lauf | Gruppe | n | Run 1 roh | Run 2 roh | Run 3 roh | Summe roh | Summe strikt | Fehlergruende (roh) |",
         "|---|---|---|---|---|---|---|---|---|"]
    for label in RUNS:
        sub = df[df.label == label]
        if sub.empty:
            continue
        for grp in GROUP_ORDER + ["gesamt"]:
            s = sub if grp == "gesamt" else sub[sub.group == grp]
            if s.empty:
                continue
            runs = sorted(s.run.unique())
            n = int((s.run == runs[0]).sum())
            per = [f"{int(s[s.run == k].ok_raw.sum())}/{n}" for k in runs] + [""] * (3 - len(runs))
            why = Counter(s[~s.ok_raw].why_raw)
            L.append(f"| {label} | {GROUP_NAME.get(grp, grp)} | {n} | {' | '.join(per)} | "
                     f"{int(s.ok_raw.sum())}/{len(s)} ({pct(s.ok_raw.sum(), len(s))}) | "
                     f"{int(s.ok_strict.sum())}/{len(s)} ({pct(s.ok_strict.sum(), len(s))}) | "
                     f"{', '.join(f'{k}: {v}' for k, v in why.items()) or '-'} |")
    L.append("")
    # E6 nach Kategorie
    L += ["### E6 nach Kategorie (roh, alle Runs zusammen)", "",
          "| Lauf | Kategorie | korrekt | Anteil |", "|---|---|---|---|"]
    for label in RUNS:
        s = df[(df.label == label) & (df.group == "E6")]
        for cat, c in s.groupby("category"):
            L.append(f"| {label} | {cat} | {int(c.ok_raw.sum())}/{len(c)} | {pct(c.ok_raw.sum(), len(c))} |")
    return L + [""]


# ---------- 2 E6 nach Stil, Agent vs. Baseline ----------

def table_e6(df, gt, base):
    a = df[(df.label == "e6_t0") & (df.run == 1)].set_index("case_id")
    if a.empty:
        return ["## 2 E6 nach Stil: kein e6_t0-Lauf", ""], None
    bb = by_run(base)[1]
    ids = a.index.tolist()
    b_ok = {c: metrics.judge(bb.get(c), gt.loc[c])[0] for c in ids}
    a["base_ok"] = [b_ok[c] for c in ids]
    a["base_actions"] = [fmt_actions(bb.get(c)) for c in ids]
    L = ["## 2 E6 nach Textstil: Agent (e6_t0) vs. Baseline (80 Faelle)", "",
         "| Stil | n | Agent roh | Agent strikt | Baseline | nur Agent korrekt | nur Baseline korrekt | beide falsch |",
         "|---|---|---|---|---|---|---|---|"]
    for stil in ["direkt", "indirekt", "distraktor", "gesamt"]:
        s = a if stil == "gesamt" else a[a.stil == stil]
        n = len(s)
        ao, so, bo = int(s.ok_raw.sum()), int(s.ok_strict.sum()), int(s.base_ok.sum())
        only_a = int((s.ok_raw & ~s.base_ok).sum())
        only_b = int((~s.ok_raw & s.base_ok).sum())
        both_w = int((~s.ok_raw & ~s.base_ok).sum())
        L.append(f"| {stil} | {n} | {ao} ({pct(ao, n)}) | {so} ({pct(so, n)}) | {bo} ({pct(bo, n)}) | {only_a} | {only_b} | {both_w} |")
    only_a = int((a.ok_raw & ~a.base_ok).sum())
    only_b = int((~a.ok_raw & a.base_ok).sum())
    L += ["", f"- Exakter McNemar-Test (roh, alle 80): diskordant {only_a} (nur Agent) vs. {only_b} (nur Baseline), "
              f"p = {mcnemar_exact(only_a, only_b):.4f}. Faelle teilen Vorlagen, die Unabhaengigkeitsannahme ist verletzt (siehe pro Vorlage).", ""]
    for stil in ["indirekt"]:
        s = a[a.stil == stil]
        oa, ob = int((s.ok_raw & ~s.base_ok).sum()), int((~s.ok_raw & s.base_ok).sum())
        L += [f"- Nur indirekt: {oa} vs. {ob}, p = {mcnemar_exact(oa, ob):.4f}", ""]
    # Kategorie x Stil
    L += ["### E6 nach Kategorie und Stil (roh)", "",
          "| Kategorie | Stil | n | Agent | Baseline |", "|---|---|---|---|---|"]
    for (cat, stil), s in a.groupby(["category", "stil"]):
        L.append(f"| {cat} | {stil} | {len(s)} | {int(s.ok_raw.sum())} | {int(s.base_ok.sum())} |")
    # Pro Vorlage
    t = a.groupby("tpl").agg(n=("ok_raw", "size"), agent=("ok_raw", "mean"), base=("base_ok", "mean"),
                             stil=("stil", "first"))
    mixed = t[(t.agent > 0) & (t.agent < 1)]
    L += ["", "### Pro Vorlage (Cluster)", "",
          f"- Vorlagen: {len(t)}. Mittel der Vorlagen-Trefferquoten: Agent {100 * t.agent.mean():.1f} %, Baseline {100 * t.base.mean():.1f} %.",
          f"- Agent pro Vorlage: immer korrekt {int((t.agent == 1).sum())}, immer falsch {int((t.agent == 0).sum())}, gemischt {len(mixed)}"
          + (f" ({', '.join(mixed.index)})" if len(mixed) else "") + ".",
          f"- Indirekte Vorlagen: {int((t.stil == 'indirekt').sum())}, davon Agent immer korrekt {int(((t.stil == 'indirekt') & (t.agent == 1)).sum())}, "
          f"Baseline immer korrekt {int(((t.stil == 'indirekt') & (t.base == 1)).sum())}."]
    better, worse = int((t.agent > t.base).sum()), int((t.agent < t.base).sum())
    L += [f"- Vorzeichentest auf Vorlagenebene (Vorlage = Einheit): Agent besser {better}, schlechter {worse}, "
          f"gleich {len(t) - better - worse}, p = {mcnemar_exact(better, worse):.4f} (exakt, zweiseitig).", ""]
    return L, a


# ---------- 3 Reproduzierbarkeit ----------

def table_repro(data, gt, audit):
    L = ["## 3 Reproduzierbarkeit", "",
         "Identisch = gleicher Typ, gleiche Aktionsmenge, gleiche Rollen ueber alle Runs (wie metrics.py).", "",
         "| Lauf | Faelle | identisch (Signatur) | identisch (Rohtext) | Korrektheit 3/3 | 2/3 | 1/3 | 0/3 |",
         "|---|---|---|---|---|---|---|---|"]
    detail = []
    for label in ["pilot_t0", "pilot_t07"]:
        br = by_run(data[label])
        runs = sorted(br)
        if len(runs) < 2:
            continue
        ids = [c for c in scope_ids("pilot", gt) if any(c in br[k] for k in runs)]
        same_sig = same_raw = 0
        okc = Counter()
        for cid in ids:
            sigs = [metrics.signature(br[k][cid]) if cid in br[k] else None for k in runs]
            raws = [audit.get((label, cid, k), {}).get("raw_output") for k in runs]
            same_sig += len(set(sigs)) == 1
            same_raw += len(set(raws)) == 1
            g = gt.loc[cid]
            if group_of(g) is not None:
                okc[sum(metrics.judge(br[k].get(cid), g)[0] for k in runs)] += 1
            if len(set(sigs)) > 1:
                detail.append(f"- {label} {cid} ({g.exception_type}/{g.free_text_category}): "
                              + " | ".join(f"R{k} {fmt_actions(br[k].get(cid))} ({br[k].get(cid, {}).get('exception_type')})" for k in runs))
        n_eval = sum(okc.values())
        L.append(f"| {label} | {len(ids)} | {same_sig}/{len(ids)} | {same_raw}/{len(ids)} | "
                 f"{okc[3]}/{n_eval} | {okc[2]} | {okc[1]} | {okc[0]} |")
    L += [""] + (["Abweichende Faelle:", ""] + detail + [""] if detail else ["Keine abweichenden Faelle.", ""])
    # Querpruefung gleicher Konfiguration ueber Sitzungen (T = 0, Seed 42)
    L += ["### Querpruefung ueber Sitzungen (gleiche Konfiguration, T = 0, Seed 42)", ""]
    pairs = []
    for cid in ["C0317", "C0067", "C0880"]:
        pairs.append(("smoke_v12", "pilot_t0", cid))
    p0 = by_run(data["pilot_t0"])
    for cid in scope_ids("pilot", gt):
        if gt.loc[cid].exception_type == "E6":
            pairs.append(("pilot_t0", "e6_t0", cid))
    same_raw = same_sig = n = 0
    for la, lb, cid in pairs:
        ea, eb = audit.get((la, cid, 1)), audit.get((lb, cid, 1))
        if not ea or not eb:
            continue
        n += 1
        same_raw += ea["raw_output"] == eb["raw_output"]
        same_sig += metrics.signature(ea.get("parsed_output") or {}) == metrics.signature(eb.get("parsed_output") or {})
        if ea["case_object_hash"] != eb["case_object_hash"] or ea["prompt_hash"] != eb["prompt_hash"]:
            L.append(f"- Achtung {cid}: Fallobjekt- oder Prompt-Hash verschieden ({la} vs. {lb})")
    L += [f"- {n} Paare (smoke_v12 vs. pilot_t0 Run 1: 3 Faelle; pilot_t0 Run 1 vs. e6_t0: 6 E6-Pilotfaelle): "
          f"Signatur identisch {same_sig}/{n}, Rohtext identisch {same_raw}/{n}.", ""]
    # T = 0 vs. T = 0,7 (Run 1 hat bei beiden Seed 42)
    t07 = by_run(data["pilot_t07"])
    if t07:
        ids = [c for c in scope_ids("pilot", gt) if c in p0.get(1, {}) and c in t07.get(1, {})]
        diff = [c for c in ids if metrics.signature(p0[1][c]) != metrics.signature(t07[1][c])]
        L += [f"- pilot_t0 Run 1 vs. pilot_t07 Run 1 (beide Seed 42): Signatur verschieden in {len(diff)} von {len(ids)} Faellen"
              + (f" ({', '.join(diff)})" if diff else "") + ".", ""]
    return L


# ---------- 4 Audit: Enthaltungen, Guardrails, Laufzeit ----------

def table_audit(data, audit, errors):
    L = ["## 4 Enthaltungen, Guardrails, Dispositionen, Laufzeit", "",
         "| Lauf | Aufrufe | Transportfehler | Parsefehler | blockiert | Enthaltungen | Typ = Erkennung | Hinweise (nicht blockierend) | Dispositionen |",
         "|---|---|---|---|---|---|---|---|---|"]
    T = ["", "| Lauf | Aufrufe | Mittel s | Median s | P95 s | Max s | Summe min | Tokens ein (Mittel) | Tokens aus (Mittel / Max) | done_reason |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for label in ["smoke_v12"] + list(RUNS):
        es = [e for (lb, _, _), e in audit.items() if lb == label]
        if not es:
            continue
        recs = data.get(label, [])
        parse = sum(1 for r in recs if r.get("_parse_error"))
        blocked = sum(1 for e in es if not (e.get("guardrail") or {}).get("passed", True))
        viol = Counter(v["rule"] for e in es for v in (e.get("guardrail") or {}).get("violations", []))
        warn = Counter(w["rule"] for e in es for w in (e.get("guardrail") or {}).get("warnings", []))
        abst = sum(1 for e in es if (e.get("parsed_output") or {}).get("exception_type") == "unknown")
        tmatch = sum(1 for e in es if (e.get("parsed_output") or {}).get("exception_type")
                     == (e.get("case_object") or {}).get("detection", {}).get("detected_type"))
        disp = Counter(e.get("disposition") for e in es)
        L.append(f"| {label} | {len(es)} | {errors.get(label, 0)} | {parse} | {blocked}"
                 + (f" ({', '.join(f'{k}: {v}' for k, v in viol.items())})" if viol else "")
                 + f" | {abst} | {tmatch}/{len(es)} | {', '.join(f'{k}: {v}' for k, v in warn.items()) or '-'} | "
                 + ", ".join(f"{k}: {v}" for k, v in sorted(disp.items())) + " |")
        d = sorted(e["duration_ms"] / 1000 for e in es)
        meta = [e.get("llm_meta") or {} for e in es]
        tin = [m.get("prompt_eval_count") or 0 for m in meta]
        tout = [m.get("eval_count") or 0 for m in meta]
        dr = Counter(m.get("done_reason") for m in meta)
        p95 = d[min(len(d) - 1, math.ceil(0.95 * len(d)) - 1)]
        T.append(f"| {label} | {len(es)} | {statistics.mean(d):.1f} | {statistics.median(d):.1f} | {p95:.1f} | {max(d):.1f} | "
                 f"{sum(d) / 60:.1f} | {statistics.mean(tin):.0f} | {statistics.mean(tout):.0f} / {max(tout)} | "
                 + ", ".join(f"{k}: {v}" for k, v in dr.items()) + " |")
    return L + T + [""]


# ---------- 6 Stichprobe K5 ----------

def k5_sample(df, audit, gt):
    """18 Begruendungen, geschichtet nach Typ und (bei E6) Kategorie und Stil, Zufall mit festem Seed.
    Auswahl unabhaengig vom Ergebnis (korrekt/falsch), damit der Mittelwert nicht verzerrt wird."""
    rng = random.Random(K5_SEED)
    pick = []
    p = df[(df.label == "pilot_t0") & (df.run == 1)]
    for grp in ["E2", "E3", "none_text"]:
        ids = sorted(p[p.group == grp].case_id)
        pick += [("pilot_t0", 1, c) for c in rng.sample(ids, min(2, len(ids)))]
    e = df[(df.label == "e6_t0") & (df.run == 1)]

    def draw(ids, n, used):
        """n Faelle zufaellig, hoechstens einer pro Vorlage (breitere Abdeckung der Texte)."""
        out = []
        for cid in rng.sample(ids, len(ids)):
            tpl = gt.loc[cid].tpl
            if tpl not in used and len(out) < n:
                out.append(cid)
                used.add(tpl)
        return out

    used = set()
    for cat in sorted(e.category.unique()):
        c = e[e.category == cat]
        chosen = draw(sorted(c[c.stil == "indirekt"].case_id), 2, used)
        chosen += draw(sorted(c[c.stil != "indirekt"].case_id), 3 - len(chosen), used)
        pick += [("e6_t0", 1, x) for x in chosen]
    rng.shuffle(pick)
    # Zusatz: alle falschen Rohentscheidungen, bewusst gewaehlt, nicht im Mittelwert (Treue falscher Begruendungen)
    wrong = df[~df.ok_raw].sort_values(["label", "case_id", "run"])
    extra = [(r.label, int(r.run), r.case_id) for r in wrong.itertuples()
             if (r.label, int(r.run), r.case_id) not in pick]
    rows, key = [], []
    for i, (label, run, cid) in enumerate(pick + extra, 1):
        ent = audit[(label, cid, run)]
        co = ent["case_object"]
        po = ent.get("parsed_output") or {}
        dv = co.get("derived") or {}
        at = co.get("attributes") or {}
        facts = (f"Limit {at.get('credit_limit')}, Exposure {dv.get('credit_exposure')}, Headroom {dv.get('credit_headroom')}; "
                 f"Liefertermin {at.get('promised_delivery_date')} (in {dv.get('days_to_promised_delivery')} T); "
                 f"Tage ueberfaellig {dv.get('days_overdue')}; Zahlungshistorie {at.get('payment_history')}; "
                 f"letzte Aktivitaet {dv.get('last_activity')}")
        item = f"K5-{i:02d}" if i <= len(pick) else f"K5-Z{i - len(pick)}"
        rows.append({"item": item, "case_id": cid, "lauf": label, "run": run,
                     "detected_type": co.get("detection", {}).get("detected_type"),
                     "hard_triggers": ";".join(co.get("detection", {}).get("hard_triggers") or []),
                     "free_text": co.get("free_text") or "", "fakten": facts,
                     "agent_typ": po.get("exception_type"), "agent_aktionen": fmt_actions(po),
                     "key_evidence": " | ".join(po.get("key_evidence") or []), "rationale": po.get("rationale", ""),
                     "score_0_2": "", "kommentar": ""})
        g = gt.loc[cid]
        row = df[(df.label == label) & (df.run == run) & (df.case_id == cid)].iloc[0]
        key.append({"item": item, "case_id": cid, "gt_type": g.exception_type, "gt_category": g.free_text_category,
                    "stil": g.stil, "tpl": g.tpl, "gt_allowed": g.allowed_action_sets, "gt_role": g.expected_target_role,
                    "agent_korrekt_roh": bool(row.ok_raw), "grund": row.why_raw})
    pd.DataFrame(rows).to_csv(OUT / "k5_stichprobe.csv", index=False)
    pd.DataFrame(key).to_csv(OUT / "k5_key.csv", index=False)
    M = ["# K5: Stichprobe Begruendungen (Raster 0 bis 2)", "",
         "Erzeugt von `src/step5_eval.py` (Seed 42). Bewertung durch Jan, blind: Ground Truth und Korrektheit stehen erst in `out/k5_key.csv`.",
         "Bewertet wird die Begruendung (`rationale` und `key_evidence`), nicht die Aktion. Eintrag in `out/k5_stichprobe.csv`, Spalten `score_0_2` und `kommentar`.", "",
         "## Raster (Entscheid Jan 01.11.2026: Option A, Anker mit Klarstellungen)", "",
         "| Punkte | Anker |", "|---|---|",
         "| 2 | Nennt die ausschlaggebende Information korrekt und verbindet sie mit der gewaehlten Aktion ueber die richtige Regel (Zuordnung). Keine falschen oder erfundenen Fakten. |",
         "| 1 | Ausschlaggebende Information korrekt, aber: nur teilweise oder generisch (z. B. nur \"Typ laut Erkennung\", Freitext nicht inhaltlich wiedergegeben), ODER falscher Regelbezug (z. B. Ermessensrichtlinie statt Zuordnung), ODER falsche Nebenaussage, die die Entscheidung nicht traegt. |",
         "| 0 | Ausschlaggebende Information fehlt oder ist falsch (Freitext falsch gedeutet, falsche Zahlen, erfundene Fakten zum Kern), oder die Begruendung widerspricht der Aktion. |", "",
         "Ausschlaggebend ist: E2 Kreditueberschreitung; E3 Liefertermin nah oder verpasst und nicht versendet; E6 Inhalt des Freitexts (Mangel, Zahlungsankuendigung, Zahlungsschwierigkeit, ohne Bezug); none: kein harter Trigger, Freitext ohne Ausnahme.", "",
         "Zusammensetzung: 2 E2, 2 E3, 2 Happy Path mit Freitext (pilot_t0 Run 1), 12 E6 (e6_t0, je Kategorie 3, davon bis zu 2 indirekt, jede Vorlage hoechstens einmal). Auswahl unabhaengig vom Ergebnis.",
         f"Zusatzitems K5-Z*: {len(extra)} falsche Rohentscheidungen, bewusst gewaehlt (nicht blind, nicht im Mittelwert). Frage dort: Traegt die Begruendung die falsche Aktion, und ist sie dem Fall treu?", ""]
    for i, r in enumerate(rows):
        if i == len(pick):
            M += ["## Zusatzitems (falsche Entscheidungen, nicht im Mittelwert)", ""]
        M += [f"### {r['item']} ({r['case_id']}, {r['lauf']}, Run {r['run']})", "",
              f"- Erkennung: {r['detected_type']} {r['hard_triggers'] or ''}",
              f"- Freitext: {r['free_text'] or '-'}",
              f"- Fakten: {r['fakten']}",
              f"- Agent: Typ {r['agent_typ']}, Aktionen {r['agent_aktionen']}",
              f"- Belege: {r['key_evidence']}",
              f"- Begruendung: {r['rationale']}",
              "- Punkte: __  Kommentar: ", ""]
    (OUT / "k5_stichprobe.md").write_text("\n".join(M), encoding="utf-8")
    return f"{len(pick)} plus {len(extra)} Zusatz"


# ---------- main ----------

def main():
    gt = load_gt()
    labels = list(RUNS)
    data = {lb: metrics.load_actions(OUT / f"agent_actions_{lb}.jsonl") for lb in labels + ["smoke_v12"]
            if (OUT / f"agent_actions_{lb}.jsonl").exists()}
    for lb in labels:
        data.setdefault(lb, [])
    base = metrics.load_actions(OUT / "baseline_actions.jsonl")
    audit, errors = load_audit(set(labels) | {"smoke_v12"})
    df = correctness(gt, data)
    L = ["# Schritt 5: Tabellen (erzeugt von `src/step5_eval.py`)", ""]
    L += table_correctness(df)
    e6, _ = table_e6(df, gt, base)
    L += e6
    L += table_repro(data, gt, audit)
    L += table_audit(data, audit, errors)
    err = df[~df.ok_raw | ~df.ok_strict].copy()
    err.to_csv(OUT / "step5_errors.csv", index=False)
    L += ["## 5 Fehlerliste", "", f"{len(err)} Zeilen (roh oder strikt falsch) in `out/step5_errors.csv`.", "",
          "| Lauf | Run | Fall | GT | Kategorie | Stil | Ausgabe Typ | Ausgabe Aktionen | Soll | Grund roh | Grund strikt |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in err.sort_values(["label", "case_id", "run"]).iterrows():
        L.append(f"| {r.label} | {r.run} | {r.case_id} | {r.gt_type} | {r.category} | {r.stil} | {r.out_type} | {r.out_actions} | "
                 f"{r.gt_allowed.replace('|', '/')}{' ' + r.gt_role if r.gt_role else ''} | {r.why_raw} | {r.why_strict} |")
    L.append("")
    if not df[(df.label == "e6_t0")].empty and not df[(df.label == "pilot_t0")].empty:
        n = k5_sample(df, audit, gt)
        L += [f"## 6 K5-Stichprobe: {n} Begruendungen in `out/k5_stichprobe.md|csv`, Schluessel `out/k5_key.csv`", ""]
    (OUT / "step5_tables.md").write_text("\n".join(L), encoding="utf-8")
    print("-> out/step5_tables.md, out/step5_errors.csv, out/k5_stichprobe.md|csv, out/k5_key.csv")


if __name__ == "__main__":
    main()
