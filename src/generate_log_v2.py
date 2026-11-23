#!/usr/bin/env python3
"""
generate_log_v2.py | WI-Projekt Thema 75 | Prozess v2 (Entwurf) | v0.2

Erzeugt das erweiterte Order-to-Cash Event Log (spec/spec_v2.yaml) mit Ground Truth.
v1 (src/generate_log.py, data/) bleibt unveraendert. Wiederverwendet werden nur die
Hilfsfunktionen fuer Kalender, Attribute und Freitexte.

Neu gegenueber v1:
  Schritte    Verfuegbarkeitspruefung, Zahlung zuordnen (Happy Path), dazu die Varianten
              Mahnung Stufe 2, Ware nachbestellen, Wareneingang Lager, Reklamation erfassen,
              Retoure erfassen, Gutschrift erstellen, Rechnung korrigieren, Auftrag stornieren
  Attribute   restock_date, invoice_amount, credit_note_amount, paid_amount (Stand am Stichtag)
  Ausnahmen   E8 Stornierung nach Versand, E9 Preisabweichung, E10 Unterzahlung,
              E11 Retoure ohne Gutschrift, E12 Verfuegbarkeitsengpass
  Ketten      E8, E9, E11 teils zusammen mit E6 (Tag chain_e6), Erkennung muss die Ursache waehlen

Aufruf aus dem Repo-Root:
  python src/generate_log_v2.py
  python src/generate_log_v2.py --spec spec/spec_v2.yaml --templates data/freitext_vorlagen.yaml --out data/v2

Deterministisch: gleiche Eingaben ergeben byte-identische Dateien.
"""

import argparse
import json
import math
from datetime import date, datetime, time, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from generate_log import (GEN, TS_FMT, add_work_minutes, bday_on_or_after, business_days, credit_exceed,
                          credit_ok, delayed_promise, draw_common, first_ts, maybe_noise, office_time_on,
                          pick_template, rng_for, text_params, uint)

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Generator-Konfiguration v2 (zusaetzlich zu GEN aus v1, nicht in spec_v2.yaml geregelt)
# ---------------------------------------------------------------------------
GEN2 = {
    "hp": {"completed_share": 0.60, "variant_share": 0.30, "boundary_share": 0.05, "noise_share": 0.10},
    "hp_variant_weights": {
        "aendern": 0.30, "teillieferung": 0.12, "erinnerung": 0.12, "mahnung2": 0.08,
        "nachbestellung": 0.12, "reklamation": 0.10, "rechnungskorrektur": 0.08, "storno": 0.08,
    },
    "boundary_kinds": ["e2", "e3", "e6", "e9", "e10", "e11", "e12"],
    "edge_share": 0.10,                    # Anteil Grenzfaelle knapp ueber der Schwelle in E9 bis E12
    "restock_days": (5, 20),               # Wiederbeschaffungszeit ab 'Ware nachbestellen'
    "invoice_dev": (0.02, 0.15),           # E9: relative Abweichung des Rechnungsbetrags
    "credit_share": (0.10, 0.60),          # Gutschrift als Anteil des Rechnungsbetrags
    "shortfall_share": (0.02, 0.50),       # E10: fehlender Anteil der Zahlung
    "complaint_days": (1, 10),             # Reklamation nach der Rechnung
    "storno_days": (1, 10),                # Stornierung nach Versand bzw. Rechnung
    "mahnung2_gap_days": (10, 14),         # Mahnstufe 2 nach Zahlungserinnerung
    "e6_mahnung2_min_overdue": 25,         # ab so vielen Tagen Verzug ist Mahnstufe 2 moeglich
    "step_hours": dict(GEN["step_hours"], **{
        "Verfuegbarkeitspruefung": (1, 0.6),
        "Ware nachbestellen": (2, 0.6),
        "Zahlung zuordnen": (3, 0.6),
        "Retoure erfassen": (10, 0.7),
        "Gutschrift erstellen": (8, 0.7),
        "Rechnung korrigieren": (4, 0.6),
        "Auftrag stornieren": (2, 0.6),
    }),
    "resources": dict(GEN["resources"], **{"Kundendienst": ["Roth I.", "Kaufmann V.", "Ammann H."]}),
}

TYPE_ORDER = ["none", "E2", "E3", "E5", "E6", "E7", "E8", "E9", "E10", "E11", "E12"]


# ---------------------------------------------------------------------------
# Kontext aus spec_v2.yaml
# ---------------------------------------------------------------------------
class Ctx:
    def __init__(self, spec, templates):
        self.spec = spec
        self.seed = int(spec["meta"]["seed"])
        hp = spec["process"]["happy_path"]
        (self.ERF, self.KRED, self.VERF, self.BEST, self.KOMM,
         self.VERS, self.RECH, self.ZAHL, self.ZUORD, self.ABS) = hp
        (self.AEND, self.TEIL, self.ERIN, self.MAHN, self.NACH, self.WE,
         self.REKL, self.RET, self.GUTS, self.RKORR, self.STORNO) = spec["process"]["allowed_variants"]
        self.base = list(hp)
        self.role_by_activity = spec["process"]["role_by_activity"]
        self.ex = spec["exceptions"]
        self.thr = int(self.ex["E3"]["params"]["days_threshold"])
        self.thr11 = int(self.ex["E11"]["params"]["days_threshold"])
        self.e6_cats = list(self.ex["E6"]["free_text_categories"].keys())
        self.templates = templates

        acts = set(hp) | set(spec["process"]["allowed_variants"])
        assert acts == set(self.role_by_activity), "spec.process.role_by_activity passt nicht zu den Aktivitaeten"
        for role in self.role_by_activity.values():
            assert role in spec["process"]["roles"], f"Rolle {role} fehlt in spec.process.roles"
            assert role in GEN2["resources"], f"Keine Ressourcen fuer Rolle {role}"
        assert set(templates) == set(self.e6_cats), "Vorlagen-Kategorien passen nicht zu spec E6"

    def counts(self):
        dist = self.spec["data_generation"]["distribution"]
        n = int(self.spec["data_generation"]["n_cases"])
        out = {("none" if k == "happy_path" else k): int(round(v * n)) for k, v in dist.items()}
        assert sum(out.values()) == n, f"Verteilung ergibt {sum(out.values())} statt {n}"
        return out

    def target_role(self, etype, cat):
        if etype == "none":
            return ""
        if etype == "E6":
            return self.ex["E6"]["free_text_categories"][cat].get("target_role", "")
        e = self.ex[etype]
        return e.get("escalation_target") or e.get("target_role") or ""

    def action_sets(self, etype, cat):
        if etype == "none":
            return [["A0"]]
        if etype == "E6":
            return self.ex["E6"]["free_text_categories"][cat]["allowed_action_sets"]
        if etype == "E7":
            return None
        return self.ex[etype]["allowed_action_sets"]


# ---------------------------------------------------------------------------
# Ereignisspur
# ---------------------------------------------------------------------------
class Track:
    def __init__(self, rng, ctx):
        self.rng = rng
        self.ctx = ctx
        self.events = []

    def _add(self, act, ts):
        role = self.ctx.role_by_activity[act]
        pool = GEN2["resources"][role]
        self.events.append({"activity": act, "timestamp": ts, "role": role,
                            "resource": pool[int(self.rng.integers(0, len(pool)))]})

    @property
    def last(self):
        return self.events[-1]["timestamp"]

    def start(self, act, ts):
        self._add(act, ts)

    def work(self, act, key=None):
        med, sig = GEN2["step_hours"][key or act]
        minutes = max(10, int(round(self.rng.lognormal(math.log(med * 60), sig))))
        self._add(act, add_work_minutes(self.last, minutes))

    def on_date(self, act, d):
        ts = datetime.combine(bday_on_or_after(d), time(GEN["office_start_h"])) + \
            timedelta(minutes=uint(self.rng, 0, (GEN["office_end_h"] - GEN["office_start_h"]) * 60 - 30))
        if ts <= self.last:
            ts = add_work_minutes(self.last, 30)
        self._add(act, ts)


def sequence(rng, ctx, c, n_aendern=0, aendern_late=True, backorder=False, teil=False, e5=False,
             storno=None, inv_fix=False, complaint=None, reminder=0, partial=False):
    """Vollstaendiger Verlauf, wird danach abgeschnitten.

    storno     None | before_ship | after_ship | after_invoice
    complaint  None | (invoice, credited|pending); Reklamation nach der Rechnung, pending endet nach der Retoure
    reminder   0 | 1 (Zahlungserinnerung) | 2 (zusaetzlich Mahnung Stufe 2)
    partial    Teilzahlung: endet nach 'Zahlung zuordnen' ohne Abschluss
    Rueckgabe  (events, meta) mit meta = {restock, due}
    """
    tr = Track(rng, ctx)
    meta = {"restock": None, "due": None}
    tr.start(ctx.ERF, c["start"])
    if n_aendern and not aendern_late:
        for _ in range(n_aendern):
            tr.work(ctx.AEND)
    tr.work(ctx.KRED)
    tr.work(ctx.VERF)
    if backorder:
        tr.work(ctx.NACH)
        meta["restock"] = bday_on_or_after(tr.last.date() + timedelta(days=uint(rng, *GEN2["restock_days"])))
    tr.work(ctx.BEST)
    if n_aendern and aendern_late:
        for _ in range(n_aendern):
            tr.work(ctx.AEND)
    if storno == "before_ship":
        tr.work(ctx.STORNO)
        tr.work(ctx.ABS)
        return tr.events, meta
    if backorder:
        tr.on_date(ctx.WE, meta["restock"])
    tr.work(ctx.KOMM)
    if e5:
        tr.work(ctx.RECH)
        tr.work(ctx.VERS)
    else:
        if teil:
            tr.work(ctx.TEIL)
            tr.work(ctx.VERS, key="Versenden_nach_Teillieferung")
        else:
            tr.work(ctx.VERS)
        if storno == "after_ship":
            tr.on_date(ctx.STORNO, tr.last.date() + timedelta(days=uint(rng, *GEN2["storno_days"])))
            return tr.events, meta
        tr.work(ctx.RECH)
    inv = first_ts(tr.events, ctx.RECH).date()
    meta["due"] = due = inv + timedelta(days=c["payment_terms_days"])
    if storno == "after_invoice":
        tr.on_date(ctx.STORNO, inv + timedelta(days=uint(rng, *GEN2["storno_days"])))
        return tr.events, meta
    if inv_fix:
        tr.work(ctx.RKORR)
    if complaint and complaint[0] == "invoice":
        tr.on_date(ctx.REKL, inv + timedelta(days=uint(rng, *GEN2["complaint_days"])))
        tr.work(ctx.RET)
        if complaint[1] == "pending":
            return tr.events, meta
        tr.work(ctx.GUTS)
    if reminder:
        rem = due + timedelta(days=uint(rng, 3, 10))
        tr.on_date(ctx.ERIN, rem)
        if reminder >= 2:
            rem = rem + timedelta(days=uint(rng, *GEN2["mahnung2_gap_days"]))
            tr.on_date(ctx.MAHN, rem)
        tr.on_date(ctx.ZAHL, rem + timedelta(days=uint(rng, 2, 12)))
    else:
        k = uint(rng, 0, min(10, c["payment_terms_days"] - 1))
        tr.on_date(ctx.ZAHL, max(due - timedelta(days=k), inv + timedelta(days=1)))
    tr.work(ctx.ZUORD)
    if not partial:
        tr.work(ctx.ABS)
    return tr.events, meta


def cut_before(events, act):
    """Events vor dem ersten Auftreten von act (alle, wenn act fehlt)."""
    for k, e in enumerate(events):
        if e["activity"] == act:
            return events[:k]
    return events


def cut_stage(ctx, events, stage):
    """Abschneiden nach dem Happy-Path-Schritt stage (Varianten davor bleiben erhalten)."""
    i = ctx.base.index(stage)
    return events if i == len(ctx.base) - 1 else cut_before(events, ctx.base[i + 1])


def has(events, act):
    return any(e["activity"] == act for e in events)


def last_date(events):
    return events[-1]["timestamp"].date()


# ---------------------------------------------------------------------------
# Betraege und Fallobjekt
# ---------------------------------------------------------------------------
def amounts(c, invoice=None, credit_share=None, paid_delta=0):
    """Plant die Betraege: Rechnung (Standard = Auftragswert), Gutschrift, Zahlung = Rest minus paid_delta."""
    inv = c["order_value"] if invoice is None else int(invoice)
    credit = int(round(inv * credit_share)) if credit_share else 0
    return {"invoice": inv, "credit": credit, "paid": inv - credit - int(paid_delta)}


def make_case(ctx, etype, c, events, snap, promised, tags, plan, meta, text=None, cat="none"):
    """Attribute v2 gelten zum Stichtag: ein Betrag zaehlt erst, wenn sein Event im Log steht."""
    a = dict(c)
    a["invoice_amount"] = plan["invoice"] if has(events, ctx.RECH) else 0
    if has(events, ctx.RKORR):
        a["invoice_amount"] = c["order_value"]
    a["credit_note_amount"] = plan["credit"] if has(events, ctx.GUTS) else 0
    a["paid_amount"] = plan["paid"] if has(events, ctx.ZAHL) else 0
    a["restock_date"] = meta["restock"].isoformat() if has(events, ctx.NACH) else ""
    return {"etype": etype, "attrs": a, "events": events, "snap": snap, "promised": promised,
            "tags": tags, "text": text, "cat": cat}


def promised_from_ship(rng, ctx, events):
    return bday_on_or_after(first_ts(events, ctx.VERS).date() + timedelta(days=uint(rng, 1, 5)))


def unshipped_snapshot(rng, ctx, events, meta, max_days=4):
    """Stichtag und Liefertermin fuer nicht versendete Faelle ohne Ausloesung von E3 oder E12."""
    last = last_date(events)
    restock = meta["restock"] if has(events, ctx.NACH) else None
    hi = max_days
    if restock and not has(events, ctx.WE):
        hi = min(hi, (restock - last).days - 1)       # Ware ist am Stichtag noch nicht eingetroffen
    snap = last + timedelta(days=uint(rng, 0, max(0, hi)))
    prom = bday_on_or_after(snap + timedelta(days=uint(rng, ctx.thr + 1, ctx.thr + 10)))
    if restock:
        prom = max(prom, bday_on_or_after(restock + timedelta(days=uint(rng, 1, 5))))
    return snap, prom


# ---------------------------------------------------------------------------
# Happy Path
# ---------------------------------------------------------------------------
VARIANT_KW = {
    "aendern": lambda rng, ctx, si: {"n_aendern": uint(rng, 1, 2), "aendern_late": si >= ctx.base.index(ctx.BEST)},
    "teillieferung": lambda rng, ctx, si: {"teil": True},
    "erinnerung": lambda rng, ctx, si: {"reminder": 1},
    "mahnung2": lambda rng, ctx, si: {"reminder": 2},
    "nachbestellung": lambda rng, ctx, si: {"backorder": True},
    "reklamation": lambda rng, ctx, si: {"complaint": ("invoice", "credited")},
    "rechnungskorrektur": lambda rng, ctx, si: {"inv_fix": True},
    "storno": lambda rng, ctx, si: {"storno": "before_ship"},
}


def eligible_variants(ctx, si):
    """Varianten, deren Events zum erreichten Schritt passen (keine Mehrdeutigkeit mit E-Typen)."""
    b = ctx.base.index
    out = ["aendern", "storno"]
    if si >= b(ctx.VERF):
        out.append("nachbestellung")
    if si >= b(ctx.VERS):
        out.append("teillieferung")
    if si >= b(ctx.RECH):
        out.append("rechnungskorrektur")
    if si >= b(ctx.ZAHL):
        out += ["erinnerung", "mahnung2", "reklamation"]
    return out


def build_none(rng, ctx, n, bdays):
    hp = GEN2["hp"]
    thr = ctx.thr
    n_b = int(round(n * hp["boundary_share"]))
    kinds_all = GEN2["boundary_kinds"]
    perm = rng.permutation(n)
    kind = {int(perm[i]): kinds_all[i % len(kinds_all)] for i in range(n_b)}
    rest = [i for i in range(n) if i not in kind]
    rest = [rest[j] for j in rng.permutation(len(rest))]
    completed = set(rest[:int(round(n * hp["completed_share"]))])
    var_pool = [int(x) for x in rng.permutation(n) if int(x) not in kind]
    var_idx = set(var_pool[:int(round(n * hp["variant_share"]))])
    noise_idx = set(int(x) for x in rng.permutation(n)[:int(round(n * hp["noise_share"]))])
    running = ctx.base[:-1]
    b = ctx.base.index

    cases = []
    for i in range(n):
        k = kind.get(i)
        c = draw_common(rng, bdays)
        credit_ok(rng, c, boundary=(k == "e2"))
        kw, plan_kw, tags = {}, {}, []

        # Schritt (Stand am Stichtag)
        if k == "e3":
            stage = running[uint(rng, 0, b(ctx.KOMM))]
        elif k in ("e6", "e11"):
            stage = ctx.RECH
        elif k == "e9":
            stage = ctx.base[uint(rng, b(ctx.RECH), b(ctx.ABS))]
        elif k == "e10":
            stage = ctx.base[uint(rng, b(ctx.ZAHL), b(ctx.ABS))]
        elif k == "e12":
            stage = ctx.BEST
        elif i in completed:
            stage = ctx.ABS
        else:
            stage = running[uint(rng, 0, len(running) - 1)]
        si = b(stage)

        # Variante
        var = None
        if i in var_idx:
            elig = eligible_variants(ctx, si)
            w = np.array([GEN2["hp_variant_weights"][e] for e in elig])
            var = elig[int(rng.choice(len(elig), p=w / w.sum()))]
            kw.update(VARIANT_KW[var](rng, ctx, si))
            tags.append("variant_" + var)
            if var == "reklamation":
                plan_kw["credit_share"] = rng.uniform(*GEN2["credit_share"])
        if k == "e11":
            kw["complaint"] = ("invoice", "pending")
        if k == "e12":
            kw["backorder"] = True
        if k == "e9":
            plan_kw["invoice"] = c["order_value"] + (1 if rng.random() < 0.5 else -1)   # genau Toleranz
        if k == "e10":
            plan_kw["paid_delta"] = 1                                                    # genau Toleranz

        ev, meta = sequence(rng, ctx, c, **kw)
        plan = amounts(c, **plan_kw)

        if var == "storno":
            if stage != ctx.ABS:
                ev = cut_before(ev, ctx.ABS)
            tags.insert(0, "completed" if has(ev, ctx.ABS) else "running")
            snap = last_date(ev) + timedelta(days=uint(rng, 0, 20))
            prom = bday_on_or_after(last_date(ev) + timedelta(days=uint(rng, -5, 15)))   # darf verstreichen
        elif k == "e12":
            ev = cut_before(ev, ctx.WE)
            snap = last_date(ev) + timedelta(days=uint(rng, 0, 2))
            prom = bday_on_or_after(snap + timedelta(days=uint(rng, thr + 1, thr + 8)))
            meta["restock"] = prom - timedelta(days=1)                                   # knapp rechtzeitig
            tags.insert(0, "running")
        elif k == "e11":
            ev = cut_before(ev, ctx.ZAHL)
            snap = first_ts(ev, ctx.RET).date() + timedelta(days=ctx.thr11)
            terms = [t for t in GEN["payment_terms_days"] if first_ts(ev, ctx.RECH).date() + timedelta(days=t) >= snap]
            c["payment_terms_days"] = min(terms)                                          # kein E6 am Stichtag
            prom = promised_from_ship(rng, ctx, ev)
            tags.insert(0, "running")
        else:
            ev = cut_stage(ctx, ev, stage)
            tags.insert(0, "completed" if stage == ctx.ABS else "running")
            last = last_date(ev)
            if stage == ctx.ABS:
                snap = last + timedelta(days=uint(rng, 0, 20))
                prom = promised_from_ship(rng, ctx, ev)
            elif not has(ev, ctx.VERS):
                if k == "e3":
                    prom = bday_on_or_after(last + timedelta(days=thr + uint(rng, 0, 3)))
                    snap = prom - timedelta(days=thr)
                else:
                    snap, prom = unshipped_snapshot(rng, ctx, ev, meta)
            elif stage == ctx.RECH:
                due = first_ts(ev, ctx.RECH).date() + timedelta(days=c["payment_terms_days"])
                snap = due if k == "e6" else last + timedelta(days=uint(rng, 0, max(0, (due - last).days)))
                prom = promised_from_ship(rng, ctx, ev)
            else:
                snap = last + timedelta(days=uint(rng, 0, 3))
                prom = promised_from_ship(rng, ctx, ev)
        if k:
            tags.append("boundary_" + k)

        text, cat = None, "none"
        if i in noise_idx:
            tpl = pick_template(rng, ctx, "irrelevant")
            text, cat = (tpl, text_params(rng, ctx, ev, snap, c)), "irrelevant"
            tags.append("noise_text")
        cases.append(make_case(ctx, "none", c, ev, snap, prom, tags, plan, meta, text, cat))
    return cases


# ---------------------------------------------------------------------------
# Ausnahmetypen aus v1 (an den Prozess v2 angepasst)
# ---------------------------------------------------------------------------
def variant_aendern(rng, tags):
    if rng.random() < GEN["other_variant_share"]:
        tags.append("variant_aendern")
        return uint(rng, 1, 2)
    return 0


def build_e2(rng, ctx, n, bdays, e7=False):
    cases = []
    for _ in range(n):
        tags = ["running"]
        c = draw_common(rng, bdays)
        credit_exceed(rng, c, tags)
        stage = ctx.ERF if rng.random() < 0.3 else ctx.KRED
        ev, meta = sequence(rng, ctx, c, n_aendern=variant_aendern(rng, tags), aendern_late=False)
        ev = cut_stage(ctx, ev, stage)
        last = last_date(ev)
        if e7:
            prom, snap, t2 = delayed_promise(rng, ctx, c, last)
            tags += t2
        else:
            snap = last + timedelta(days=uint(rng, 0, 5))
            prom = bday_on_or_after(snap + timedelta(days=uint(rng, ctx.thr, ctx.thr + 15)))
        text, cat, t3 = maybe_noise(rng, ctx, ev, snap, c, GEN["other_noise_share"])
        cases.append(make_case(ctx, "E7" if e7 else "E2", c, ev, snap, prom, tags + t3, amounts(c), meta, text, cat))
    return cases


def build_e3(rng, ctx, n, bdays):
    cases = []
    for _ in range(n):
        tags = ["running"]
        c = draw_common(rng, bdays)
        credit_ok(rng, c)
        u = rng.random()
        stage = ctx.KRED if u < 0.2 else ctx.VERF if u < 0.3 else ctx.BEST if u < 0.6 else ctx.KOMM
        n_aend = variant_aendern(rng, tags)
        ev, meta = sequence(rng, ctx, c, n_aendern=n_aend, aendern_late=ctx.base.index(stage) >= ctx.base.index(ctx.BEST))
        ev = cut_stage(ctx, ev, stage)
        prom, snap, t2 = delayed_promise(rng, ctx, c, last_date(ev))
        text, cat, t3 = maybe_noise(rng, ctx, ev, snap, c, GEN["other_noise_share"])
        cases.append(make_case(ctx, "E3", c, ev, snap, prom, tags + t2 + t3, amounts(c), meta, text, cat))
    return cases


def build_e5(rng, ctx, n, bdays):
    cases = []
    for _ in range(n):
        c = draw_common(rng, bdays)
        credit_ok(rng, c)
        done = rng.random() < 0.5
        tags = ["completed" if done else "running"]
        ev, meta = sequence(rng, ctx, c, n_aendern=variant_aendern(rng, tags), e5=True)
        if done:
            snap = last_date(ev) + timedelta(days=uint(rng, 0, 20))
        else:
            ev = cut_before(ev, ctx.ZAHL)
            last = last_date(ev)
            snap = last + timedelta(days=uint(rng, 0, min(5, (meta["due"] - last).days)))
        prom = promised_from_ship(rng, ctx, ev)
        text, cat, t3 = maybe_noise(rng, ctx, ev, snap, c, GEN["other_noise_share"])
        cases.append(make_case(ctx, "E5", c, ev, snap, prom, tags + t3, amounts(c), meta, text, cat))
    return cases


def build_e6(rng, ctx, n, bdays):
    per = n // len(ctx.e6_cats)
    cats = []
    for k in ctx.e6_cats:
        cats += [k] * per
    cats += ctx.e6_cats[: n - len(cats)]
    cats = [cats[j] for j in rng.permutation(n)]
    lo, hi = GEN["e6_overdue_days"]
    cases = []
    for i in range(n):
        tags = ["running"]
        c = draw_common(rng, bdays)
        credit_ok(rng, c)
        teil, n_aend = False, 0
        if rng.random() < GEN["other_variant_share"]:
            if rng.random() < 0.5:
                n_aend = uint(rng, 1, 2)
                tags.append("variant_aendern")
            else:
                teil = True
                tags.append("variant_teillieferung")
        od = uint(rng, lo, hi)
        rem = 0
        if od >= GEN["e6_reminder_min_overdue"] and rng.random() < GEN["e6_reminder_share"]:
            rem = 1
            if od >= GEN2["e6_mahnung2_min_overdue"] and rng.random() < 0.5:
                rem = 2
        if rem:
            tags.append("variant_erinnerung" if rem == 1 else "variant_mahnung2")
        ev, meta = sequence(rng, ctx, c, n_aendern=n_aend, teil=teil, reminder=rem)
        ev = cut_before(ev, ctx.ZAHL)
        snap = meta["due"] + timedelta(days=od)
        tags.append(f"overdue_{od}d")
        if od == lo:
            tags.append("edge_e6")
        prom = promised_from_ship(rng, ctx, ev)
        tpl = pick_template(rng, ctx, cats[i])
        text = (tpl, text_params(rng, ctx, ev, snap, c))
        tags.append("text_" + tpl["stil"])
        cases.append(make_case(ctx, "E6", c, ev, snap, prom, tags, amounts(c), meta, text, cats[i]))
    return cases


# ---------------------------------------------------------------------------
# Neue Ausnahmetypen E8 bis E12
# ---------------------------------------------------------------------------
def overdue_snapshot(rng, ctx, ev, meta, chain, tags):
    """Stichtag vor oder nach Faelligkeit. chain = True erzeugt bewusst zusaetzlich E6."""
    last = last_date(ev)
    if chain:
        tags.append("chain_e6")
        return max(last, meta["due"] + timedelta(days=uint(rng, 1, 30)))
    return last + timedelta(days=uint(rng, 0, max(0, (meta["due"] - last).days)))


def build_e8(rng, ctx, n, bdays):
    cases = []
    for _ in range(n):
        tags = ["running"]
        c = draw_common(rng, bdays)
        credit_ok(rng, c)
        when = "after_ship" if rng.random() < 0.6 else "after_invoice"
        tags.append("storno_" + when)
        ev, meta = sequence(rng, ctx, c, n_aendern=variant_aendern(rng, tags), storno=when)
        if when == "after_ship":
            snap = last_date(ev) + timedelta(days=uint(rng, 0, 5))
        else:
            snap = overdue_snapshot(rng, ctx, ev, meta, rng.random() < 0.5, tags)
        prom = promised_from_ship(rng, ctx, ev)
        text, cat, t3 = maybe_noise(rng, ctx, ev, snap, c, GEN["other_noise_share"])
        cases.append(make_case(ctx, "E8", c, ev, snap, prom, tags + t3, amounts(c), meta, text, cat))
    return cases


def build_e9(rng, ctx, n, bdays):
    cases = []
    for _ in range(n):
        c = draw_common(rng, bdays)
        credit_ok(rng, c)
        tags = []
        if rng.random() < GEN2["edge_share"]:
            diff = 2 if rng.random() < 0.5 else -2
            tags.append("edge_e9")
        else:
            dev = rng.uniform(*GEN2["invoice_dev"]) * (1 if rng.random() < 0.6 else -1)
            diff = int(round(c["order_value"] * dev))
            diff = diff if abs(diff) > 1 else (2 if dev > 0 else -2)
        tags.append("invoice_" + ("high" if diff > 0 else "low"))
        u = rng.random()
        mode = "open" if u < 0.5 else "chain" if u < 0.75 else "paid"
        ev, meta = sequence(rng, ctx, c, n_aendern=variant_aendern(rng, tags))
        if mode == "paid":
            tags.insert(0, "completed")
            snap = last_date(ev) + timedelta(days=uint(rng, 0, 20))
        else:
            tags.insert(0, "running")
            ev = cut_before(ev, ctx.ZAHL)
            snap = overdue_snapshot(rng, ctx, ev, meta, mode == "chain", tags)
        prom = promised_from_ship(rng, ctx, ev)
        text, cat, t3 = maybe_noise(rng, ctx, ev, snap, c, GEN["other_noise_share"])
        plan = amounts(c, invoice=c["order_value"] + diff)
        cases.append(make_case(ctx, "E9", c, ev, snap, prom, tags + t3, plan, meta, text, cat))
    return cases


def build_e10(rng, ctx, n, bdays):
    cases = []
    for _ in range(n):
        tags = ["running"]
        c = draw_common(rng, bdays)
        credit_ok(rng, c)
        kw, credit = {}, None
        u = rng.random()
        if u < 0.2:
            kw["complaint"] = ("invoice", "credited")
            credit = rng.uniform(*GEN2["credit_share"])
            tags.append("variant_reklamation")
        elif u < 0.4:
            kw["reminder"] = 1
            tags.append("variant_erinnerung")
        ev, meta = sequence(rng, ctx, c, partial=True, **kw)
        base = amounts(c, credit_share=credit)
        if rng.random() < GEN2["edge_share"]:
            short = 2
            tags.append("edge_e10")
        else:
            short = max(2, int(round((base["invoice"] - base["credit"]) * rng.uniform(*GEN2["shortfall_share"]))))
        plan = amounts(c, credit_share=credit, paid_delta=short)
        snap = last_date(ev) + timedelta(days=uint(rng, 0, 10))
        prom = promised_from_ship(rng, ctx, ev)
        text, cat, t3 = maybe_noise(rng, ctx, ev, snap, c, GEN["other_noise_share"])
        cases.append(make_case(ctx, "E10", c, ev, snap, prom, tags + t3, plan, meta, text, cat))
    return cases


def build_e11(rng, ctx, n, bdays):
    cases = []
    for _ in range(n):
        tags = ["running"]
        c = draw_common(rng, bdays)
        credit_ok(rng, c)
        ev, meta = sequence(rng, ctx, c, complaint=("invoice", "pending"))   # Gutschrift setzt eine Rechnung voraus
        ret = first_ts(ev, ctx.RET).date()
        if rng.random() < GEN2["edge_share"]:
            snap = ret + timedelta(days=ctx.thr11 + 1)
            tags.append("edge_e11")
        else:
            snap = ret + timedelta(days=ctx.thr11 + uint(rng, 1, 20))
        if snap > meta["due"]:
            tags.append("chain_e6")                     # Kunde haelt Zahlung bis zur Gutschrift zurueck
        prom = promised_from_ship(rng, ctx, ev)
        text, cat, t3 = maybe_noise(rng, ctx, ev, snap, c, GEN["other_noise_share"])
        cases.append(make_case(ctx, "E11", c, ev, snap, prom, tags + t3, amounts(c), meta, text, cat))
    return cases


def build_e12(rng, ctx, n, bdays):
    cases = []
    for _ in range(n):
        tags = ["running"]
        c = draw_common(rng, bdays)
        credit_ok(rng, c)
        ev, meta = sequence(rng, ctx, c, n_aendern=variant_aendern(rng, tags), aendern_late=False, backorder=True)
        ev = cut_before(ev, ctx.WE)
        snap = last_date(ev) + timedelta(days=uint(rng, 0, 2))
        prom = bday_on_or_after(snap + timedelta(days=uint(rng, ctx.thr, ctx.thr + 8)))   # E3 noch nicht erreicht
        if rng.random() < GEN2["edge_share"]:
            meta["restock"] = prom
            tags.append("edge_e12")
        else:
            meta["restock"] = bday_on_or_after(prom + timedelta(days=uint(rng, 1, 10)))
        tags.append(f"restock_late_{(meta['restock'] - prom).days}d")
        text, cat, t3 = maybe_noise(rng, ctx, ev, snap, c, GEN["other_noise_share"])
        cases.append(make_case(ctx, "E12", c, ev, snap, prom, tags + t3, amounts(c), meta, text, cat))
    return cases


# ---------------------------------------------------------------------------
# Hauptablauf
# ---------------------------------------------------------------------------
def generate(spec_path, tpl_path, out_dir):
    spec = yaml.safe_load(Path(spec_path).read_text(encoding="utf-8"))
    tpl_raw = yaml.safe_load(Path(tpl_path).read_text(encoding="utf-8"))
    ctx = Ctx(spec, tpl_raw["categories"])
    counts = ctx.counts()
    bdays = business_days(date.fromisoformat(GEN["start_from"]), date.fromisoformat(GEN["start_to"]))

    builders = {
        "none": build_none, "E2": build_e2, "E3": build_e3, "E5": build_e5, "E6": build_e6,
        "E7": lambda r, c, n, b: build_e2(r, c, n, b, e7=True),
        "E8": build_e8, "E9": build_e9, "E10": build_e10, "E11": build_e11, "E12": build_e12,
    }
    cases = []
    for t in TYPE_ORDER:
        cases += builders[t](rng_for(ctx.seed, "v2:type:" + t), ctx, counts[t], bdays)

    perm = rng_for(ctx.seed, "v2:shuffle").permutation(len(cases))
    cases = [cases[j] for j in perm]
    width = max(4, len(str(len(cases))))
    for k, cs in enumerate(cases, start=1):
        cs["case_id"] = f"C{k:0{width}d}"

    hh, mm, ss = GEN["snapshot_clock"]
    ev_rows, case_rows, gt_rows = [], [], []
    for cs in cases:
        cid = cs["case_id"]
        for e in cs["events"]:
            ev_rows.append({"case_id": cid, "activity": e["activity"],
                            "timestamp": e["timestamp"].strftime(TS_FMT),
                            "resource": e["resource"], "role": e["role"]})
        free_text = ""
        if cs["text"] is not None:
            tpl, params = cs["text"]
            free_text = tpl["text"].format_map(dict(params, auftragsnr=cid))
        a = cs["attrs"]
        row = {"case_id": cid}
        for col in spec["case_attributes"]:
            row[col] = a.get(col)
        row.update({"promised_delivery_date": cs["promised"].isoformat(), "free_text": free_text,
                    "snapshot_time": datetime.combine(cs["snap"], time(hh, mm, ss)).strftime(TS_FMT)})
        case_rows.append(row)
        sets = ctx.action_sets(cs["etype"], cs["cat"])
        tags = list(cs["tags"])
        if cs["text"] is not None:
            tags.append("tpl_" + cs["text"][0]["id"])
        gt_rows.append({
            "case_id": cid,
            "exception_type": cs["etype"],
            "free_text_category": cs["cat"],
            "allowed_action_sets": "" if sets is None else json.dumps(sets, separators=(",", ":")),
            "expected_target_role": ctx.target_role(cs["etype"], cs["cat"]),
            "generator_tag": ";".join(tags),
        })

    cutoff = date.fromisoformat(GEN["data_cutoff"])
    late = [cs["case_id"] for cs in cases if cs["snap"] > cutoff]
    assert not late, f"{len(late)} Stichtage nach dem Datenabzug {cutoff}"
    early = [cs["case_id"] for cs in cases if cs["events"][-1]["timestamp"].date() > cs["snap"]]
    assert not early, f"{len(early)} Faelle mit Events nach dem Stichtag"

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    kw = dict(index=False, encoding="utf-8", lineterminator="\n")
    pd.DataFrame(ev_rows, columns=["case_id", "activity", "timestamp", "resource", "role"]).to_csv(out / "event_log.csv", **kw)
    pd.DataFrame(case_rows)[["case_id"] + list(spec["case_attributes"])].to_csv(out / "cases.csv", **kw)
    pd.DataFrame(gt_rows).to_csv(out / "ground_truth.csv", **kw)
    return {"cases": len(case_rows), "events": len(ev_rows), "counts": counts}


def main():
    ap = argparse.ArgumentParser(description="Synthetischer O2C-Log-Generator v2 (Thema 75)")
    ap.add_argument("--spec", default=str(ROOT / "spec" / "spec_v2.yaml"))
    ap.add_argument("--templates", default=str(ROOT / "data" / "freitext_vorlagen.yaml"))
    ap.add_argument("--out", default=str(ROOT / "data" / "v2"))
    a = ap.parse_args()
    res = generate(a.spec, a.templates, a.out)
    print(f"Faelle: {res['cases']}, Events: {res['events']}, Verteilung: {res['counts']}")


if __name__ == "__main__":
    main()
