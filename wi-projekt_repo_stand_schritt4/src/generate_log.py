#!/usr/bin/env python3
"""
generate_log.py | WI-Projekt Thema 75 | Schritt 2 (AP2) | v0.2

Erzeugt das synthetische Order-to-Cash Event Log mit Ground Truth.

Quellen der Parameter:
  spec/spec.yaml               Seed, Fallzahl, Verteilung, Aktivitaeten, Varianten, Rollen,
                               E3-Schwelle, Aktionsmengen, E6-Kategorien, Pilotumfang
  data/freitext_vorlagen.yaml  Freitext-Vorlagen
  GEN (unten)                  Alles, was die Spec nicht regelt (Vorgaben aus dem Prompt
                               Schritt 2 bzw. Annahmen). Kandidaten fuer einen Abschnitt
                               "generator" in spec.yaml.

Aufruf aus dem Repo-Root:
  python src/generate_log.py
  python src/generate_log.py --spec spec/spec.yaml --templates data/freitext_vorlagen.yaml --out data

Deterministisch: gleiche Eingaben ergeben byte-identische Dateien.
Jeder Ausnahmetyp hat einen eigenen Zufallsstrom (abgeleitet aus dem Seed und dem Typnamen).
"""

import argparse
import json
import math
import zlib
from datetime import date, datetime, time, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Generator-Konfiguration (nicht in spec.yaml geregelt)
# ---------------------------------------------------------------------------
GEN = {
    "start_from": "2026-01-05",
    "start_to": "2026-06-30",            # so liegen alle Stichtage vor dem Datenabzug
    "data_cutoff": "2026-10-31",          # Annahme: Datenabzug, kein Stichtag danach
    "office_start_h": 8,
    "office_end_h": 17,
    "snapshot_clock": (18, 0, 0),          # Annahme: Stichtag = Tagesauswertung 18:00, nach Bueroschluss
    "segment_probs": {"A": 0.20, "B": 0.50, "C": 0.30},
    "credit_limits": {
        "A": [200000, 300000, 400000],
        "B": [60000, 80000, 100000],
        "C": [15000, 20000, 25000],
    },
    "order_value_median": {"A": 25000, "B": 9000, "C": 2500},
    "order_value_sigma": 0.7,
    "order_value_min": 200,
    "order_value_max_share_of_limit": 0.5,
    "utilization_beta": (2.0, 2.0),        # Auslastung (offene Posten) bei Kredit in Ordnung
    "payment_terms_days": [14, 30, 45, 60],
    "payment_terms_probs": [0.2, 0.4, 0.2, 0.2],
    "payment_history": ["gut", "mittel", "schlecht"],
    "payment_history_probs": [0.50, 0.35, 0.15],
    "overshoot_buckets": {"knapp": (0.0, 0.05), "mittel": (0.05, 0.25), "stark": (0.25, 0.80)},
    "edge_e2_share": 0.10,                 # E2/E7: Ueberschreitung um genau CHF 1
    "hp": {"completed_share": 0.60, "variant_share": 0.25, "boundary_share": 0.05, "noise_share": 0.10},
    "hp_variant_weights": {"aendern": 0.50, "teillieferung": 0.25, "erinnerung": 0.25},
    "other_variant_share": 0.15,           # Abweichung: Varianten auch in E-Typen (Leakage vermeiden)
    "other_noise_share": 0.10,             # Abweichung: irrelevanter Freitext auch in E2, E3, E5, E7
    "e3_delta_min_days": -5,               # promised - Stichtag; Obergrenze = days_threshold - 1 (aus spec)
    "e3_imminent_share": 0.5,              # Anteil drohend (Delta 0 bis Schwelle-1), Rest bereits ueberschritten
    "e6_overdue_days": (1, 45),
    "e6_reminder_min_overdue": 11,         # ab so vielen Tagen Verzug ist eine Zahlungserinnerung moeglich
    "e6_reminder_share": 0.5,              # Anteil mit Zahlungserinnerung (realistischer, weniger Leakage)
    "step_hours": {                        # Median Arbeitsstunden, Sigma (lognormal)
        "Kreditpruefung": (2, 0.6),
        "Auftrag bestaetigen": (3, 0.6),
        "Auftrag aendern": (6, 0.7),
        "Kommissionieren": (14, 0.7),
        "Teillieferung": (5, 0.6),
        "Versenden": (5, 0.6),
        "Versenden_nach_Teillieferung": (18, 0.6),
        "Rechnung stellen": (6, 0.7),
        "Fall abschliessen": (4, 0.6),
    },
    "role_by_activity": {
        "Auftrag erfassen": "Vertrieb",
        "Auftrag bestaetigen": "Vertrieb",
        "Auftrag aendern": "Vertrieb",
        "Kreditpruefung": "Credit Management",
        "Kommissionieren": "Lager/Logistik",
        "Versenden": "Lager/Logistik",
        "Teillieferung": "Lager/Logistik",
        "Rechnung stellen": "Buchhaltung",
        "Zahlungseingang": "Buchhaltung",
        "Zahlungserinnerung": "Buchhaltung",
        "Fall abschliessen": "Buchhaltung",
    },
    "resources": {
        "Vertrieb": ["Keller M.", "Brunner S.", "Meier L.", "Gerber R."],
        "Credit Management": ["Huber A.", "Frei D.", "Schmid N."],
        "Lager/Logistik": ["Baumann P.", "Widmer T.", "Steiner J.", "Moser K."],
        "Buchhaltung": ["Fischer E.", "Weber C.", "Zimmermann B."],
    },
    # Pilot: Fallback, falls spec.pilot.composition fehlt (spec < v0.3.0)
    "pilot_composition": {"E2": 4, "E3": 4, "E6": 6, "none": 6, "none_with_noise_text": 3},
    "labeling_e6_n": 15,
}

TS_FMT = "%Y-%m-%d %H:%M:%S"
TYPE_ORDER = ["none", "E2", "E3", "E5", "E6", "E7"]


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------
def rng_for(seed, name):
    key = zlib.crc32(name.encode("ascii"))
    return np.random.default_rng(np.random.SeedSequence(entropy=seed, spawn_key=(key,)))


def uint(rng, lo, hi):
    """Ganzzahl gleichverteilt in [lo, hi] (inklusive)."""
    return int(rng.integers(lo, hi + 1))


def is_bday(d):
    return d.weekday() < 5


def bday_on_or_after(d):
    while not is_bday(d):
        d += timedelta(days=1)
    return d


def bday_on_or_before(d):
    while not is_bday(d):
        d -= timedelta(days=1)
    return d


def next_bday(d):
    return bday_on_or_after(d + timedelta(days=1))


OFF_S = time(GEN["office_start_h"])
OFF_E = time(GEN["office_end_h"])
OFFICE_MIN = (GEN["office_end_h"] - GEN["office_start_h"]) * 60


def normalize(t):
    d = t.date()
    if not is_bday(d):
        return datetime.combine(bday_on_or_after(d), OFF_S)
    if t.time() >= OFF_E:
        return datetime.combine(next_bday(d), OFF_S)
    if t.time() < OFF_S:
        return datetime.combine(d, OFF_S)
    return t


def add_work_minutes(t, minutes):
    """Addiert Arbeitsminuten (nur Werktage, nur Buerozeit)."""
    t = normalize(t)
    rem = int(minutes)
    while True:
        end = datetime.combine(t.date(), OFF_E)
        avail = int((end - t).total_seconds() // 60)
        if rem < avail:
            return t + timedelta(minutes=rem)
        rem -= avail
        t = datetime.combine(next_bday(t.date()), OFF_S)


def office_time_on(rng, d):
    return datetime.combine(d, OFF_S) + timedelta(minutes=uint(rng, 0, OFFICE_MIN - 30))


def fmt_date(d):
    return d.strftime("%d.%m.%Y")


def fmt_chf(v):
    return "CHF " + f"{int(v):,}".replace(",", "'") + ".00"


# ---------------------------------------------------------------------------
# Kontext aus spec.yaml
# ---------------------------------------------------------------------------
class Ctx:
    def __init__(self, spec, templates):
        self.spec = spec
        self.seed = int(spec["meta"]["seed"])
        hp = spec["process"]["happy_path"]
        (self.ERF, self.KRED, self.BEST, self.KOMM,
         self.VERS, self.RECH, self.ZAHL, self.ABS) = hp
        self.AEND, self.TEIL, self.ERIN = spec["process"]["allowed_variants"]
        self.base = list(hp)
        self.base_e5 = [self.ERF, self.KRED, self.BEST, self.KOMM, self.RECH, self.VERS, self.ZAHL, self.ABS]
        self.thr = int(spec["exceptions"]["E3"]["params"]["days_threshold"])
        self.ex = spec["exceptions"]
        self.e6_cats = list(spec["exceptions"]["E6"]["free_text_categories"].keys())
        self.templates = templates

        # Konsistenz GEN vs. spec
        acts = set(hp) | set(spec["process"]["allowed_variants"])
        assert acts == set(GEN["role_by_activity"]), "GEN.role_by_activity passt nicht zu spec.process"
        for role in GEN["role_by_activity"].values():
            assert role in spec["process"]["roles"], f"Rolle {role} fehlt in spec.process.roles"
        assert set(templates) == set(self.e6_cats), "Vorlagen-Kategorien passen nicht zu spec E6"
        for t in templates["irrelevant"]:
            for ph in ("{rechnungsnr}", "{betrag}", "{lieferdatum}", "{datum}"):
                assert ph not in t["text"], f"{t['id']}: Platzhalter {ph} in irrelevant nicht erlaubt"

    def counts(self):
        dist = self.spec["data_generation"]["distribution"]
        n = int(self.spec["data_generation"]["n_cases"])
        out = {}
        for k, v in dist.items():
            key = "none" if k == "happy_path" else k
            out[key] = int(round(v * n))
        assert sum(out.values()) == n, f"Verteilung ergibt {sum(out.values())} statt {n}"
        return out

    def target_role(self, etype, cat):
        """Erwartete Zielrolle fuer A5/A6 (Entscheid Jan 01.11.2026). Leer, wenn keine Rolle verlangt."""
        if etype == "E6":
            return self.ex["E6"]["free_text_categories"][cat].get("target_role", "")
        if etype in ("E2", "E5"):
            return self.ex[etype].get("escalation_target", "")
        return ""

    def action_sets(self, etype, cat):
        if etype == "none":
            return [["A0"]]                      # Annahme (nicht explizit in spec)
        if etype == "E6":
            return self.ex["E6"]["free_text_categories"][cat]["allowed_action_sets"]
        if etype == "E7":
            return None                          # TBD_by_labeling, bleibt leer
        return self.ex[etype]["allowed_action_sets"]


# ---------------------------------------------------------------------------
# Ereignisspur
# ---------------------------------------------------------------------------
class Track:
    def __init__(self, rng):
        self.rng = rng
        self.events = []

    def _add(self, act, ts):
        role = GEN["role_by_activity"][act]
        pool = GEN["resources"][role]
        self.events.append({"activity": act, "timestamp": ts, "role": role,
                            "resource": pool[int(self.rng.integers(0, len(pool)))]})

    @property
    def last(self):
        return self.events[-1]["timestamp"]

    def start(self, act, ts):
        self._add(act, ts)

    def work(self, act, key=None):
        med, sig = GEN["step_hours"][key or act]
        minutes = max(10, int(round(self.rng.lognormal(math.log(med * 60), sig))))
        self._add(act, add_work_minutes(self.last, minutes))

    def on_date(self, act, d):
        ts = office_time_on(self.rng, bday_on_or_after(d))
        if ts <= self.last:
            ts = add_work_minutes(self.last, 30)
        self._add(act, ts)


def full_sequence(rng, ctx, c, n_aendern=0, aendern_late=True, teil=False, reminder=False, e5=False):
    """Vollstaendiger Verlauf. Wird danach am Stichtag abgeschnitten."""
    tr = Track(rng)
    tr.start(ctx.ERF, c["start"])
    if n_aendern and not aendern_late:
        for _ in range(n_aendern):
            tr.work(ctx.AEND)
    tr.work(ctx.KRED)
    tr.work(ctx.BEST)
    if n_aendern and aendern_late:
        for _ in range(n_aendern):
            tr.work(ctx.AEND)
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
        tr.work(ctx.RECH)
    inv = [e for e in tr.events if e["activity"] == ctx.RECH][0]["timestamp"].date()
    due = inv + timedelta(days=c["payment_terms_days"])
    if reminder:
        rem = due + timedelta(days=uint(rng, 3, 10))
        tr.on_date(ctx.ERIN, rem)
        tr.on_date(ctx.ZAHL, rem + timedelta(days=uint(rng, 2, 12)))
    else:
        k = uint(rng, 0, min(10, c["payment_terms_days"] - 1))
        pay = bday_on_or_before(due - timedelta(days=k))
        if pay <= inv:
            pay = next_bday(inv)
        tr.on_date(ctx.ZAHL, pay)
    tr.work(ctx.ABS)
    return tr.events


def truncate(events, base_order, last_stage):
    i = base_order.index(last_stage)
    if i == len(base_order) - 1:
        return events
    nxt = base_order[i + 1]
    for k, e in enumerate(events):
        if e["activity"] == nxt:
            return events[:k]
    return events


def first_ts(events, act):
    for e in events:
        if e["activity"] == act:
            return e["timestamp"]
    return None


# ---------------------------------------------------------------------------
# Attribute
# ---------------------------------------------------------------------------
def draw_common(rng, bdays):
    segs = list(GEN["segment_probs"])
    seg = segs[int(rng.choice(len(segs), p=list(GEN["segment_probs"].values())))]
    limit = int(rng.choice(GEN["credit_limits"][seg]))
    v = rng.lognormal(math.log(GEN["order_value_median"][seg]), GEN["order_value_sigma"])
    v = int(round(min(max(v, GEN["order_value_min"]), GEN["order_value_max_share_of_limit"] * limit)))
    hist = GEN["payment_history"][int(rng.choice(3, p=GEN["payment_history_probs"]))]
    terms = int(rng.choice(GEN["payment_terms_days"], p=GEN["payment_terms_probs"]))
    start = office_time_on(rng, bdays[int(rng.integers(0, len(bdays)))])
    return {"customer_segment": seg, "credit_limit": limit, "order_value": v,
            "payment_history": hist, "payment_terms_days": terms, "start": start}


def credit_ok(rng, c, boundary=False):
    L, V = c["credit_limit"], c["order_value"]
    if boundary:
        c["open_items"] = L - V                      # Summe == Limit, kein Trigger (strikt >)
    else:
        a, b = GEN["utilization_beta"]
        c["open_items"] = min(int(math.floor(rng.beta(a, b) * (L - V))), L - V - 1)


def credit_exceed(rng, c, tags):
    L, V = c["credit_limit"], c["order_value"]
    if rng.random() < GEN["edge_e2_share"]:
        c["open_items"] = L - V + 1
        tags += ["overshoot_knapp", "edge_e2"]
        return
    names = list(GEN["overshoot_buckets"])
    bucket = names[int(rng.integers(0, len(names)))]
    lo, hi = GEN["overshoot_buckets"][bucket]
    r = 1.0 + rng.uniform(lo, hi)
    c["open_items"] = max(int(math.ceil(r * L)) - V, L - V + 1)
    tags.append("overshoot_" + bucket)


def promised_from_ship(rng, ctx, events):
    ship = first_ts(events, ctx.VERS).date()
    return bday_on_or_after(ship + timedelta(days=uint(rng, 1, 5)))


def pick_template(rng, ctx, cat):
    lst = ctx.templates[cat]
    return lst[int(rng.integers(0, len(lst)))]


def text_params(rng, ctx, events, snap, c):
    p = {"datum": fmt_date(snap - timedelta(days=uint(rng, 1, 7))),
         "datum_zukunft": fmt_date(snap + timedelta(days=uint(rng, 3, 20)))}
    if first_ts(events, ctx.RECH) is not None:
        p["rechnungsnr"] = f"RE-26-{uint(rng, 10000, 99999)}"
        p["betrag"] = fmt_chf(c["order_value"])
    ship = first_ts(events, ctx.VERS)
    if ship is not None:
        p["lieferdatum"] = fmt_date(ship.date() + timedelta(days=uint(rng, 1, 2)))
    return p


def make_case(etype, c, events, snap, promised, tags, text=None, cat="none"):
    return {"etype": etype, "attrs": c, "events": events, "snap": snap, "promised": promised,
            "tags": tags, "text": text, "cat": cat}


def maybe_noise(rng, ctx, events, snap, c, share):
    if rng.random() < share:
        tpl = pick_template(rng, ctx, "irrelevant")
        return (tpl, text_params(rng, ctx, events, snap, c)), "irrelevant", ["noise_text"]
    return None, "none", []


# ---------------------------------------------------------------------------
# Builder pro Typ
# ---------------------------------------------------------------------------
def build_none(rng, ctx, n, bdays):
    hp = GEN["hp"]
    thr = ctx.thr
    n_b = int(round(n * hp["boundary_share"]))
    kinds = (["boundary_e2"] * (n_b - 2 * (n_b // 3)) + ["boundary_e3"] * (n_b // 3)
             + ["boundary_e6"] * (n_b // 3))
    perm = rng.permutation(n)
    kind = {int(perm[i]): kinds[i] for i in range(n_b)}
    forced_running = [i for i, k in kind.items() if k in ("boundary_e3", "boundary_e6")]
    rest = [i for i in range(n) if i not in set(forced_running)]
    rest = [rest[j] for j in rng.permutation(len(rest))]
    n_completed = int(round(n * hp["completed_share"]))
    completed = set(rest[:n_completed])

    running_stages = [ctx.ERF, ctx.KRED, ctx.BEST, ctx.KOMM, ctx.VERS, ctx.RECH, ctx.ZAHL]
    stage = {}
    for i in range(n):
        k = kind.get(i)
        if i in completed:
            stage[i] = ctx.ABS
        elif k == "boundary_e3":
            stage[i] = running_stages[uint(rng, 0, 3)]
        elif k == "boundary_e6":
            stage[i] = ctx.RECH
        else:
            stage[i] = running_stages[uint(rng, 0, 6)]

    n_var = int(round(n * hp["variant_share"]))
    var_idx = set(int(x) for x in rng.permutation(n)[:n_var])
    variant = {}
    for i in sorted(var_idx):
        si = ctx.base.index(stage[i])
        elig = ["aendern"]
        if si >= ctx.base.index(ctx.VERS):
            elig.append("teillieferung")
        if si >= ctx.base.index(ctx.ZAHL):
            elig.append("erinnerung")
        w = np.array([GEN["hp_variant_weights"][e] for e in elig])
        variant[i] = elig[int(rng.choice(len(elig), p=w / w.sum()))]

    n_noise = int(round(n * hp["noise_share"]))
    noise = set(int(x) for x in rng.permutation(n)[:n_noise])

    cases = []
    for i in range(n):
        k = kind.get(i)
        st = stage[i]
        var = variant.get(i)
        tags = ["completed" if st == ctx.ABS else "running"]
        if k:
            tags.append(k)
        if var:
            tags.append("variant_" + var)
        c = draw_common(rng, bdays)
        credit_ok(rng, c, boundary=(k == "boundary_e2"))
        si = ctx.base.index(st)
        ev = full_sequence(rng, ctx, c,
                           n_aendern=uint(rng, 1, 2) if var == "aendern" else 0,
                           aendern_late=si >= ctx.base.index(ctx.BEST),
                           teil=(var == "teillieferung"), reminder=(var == "erinnerung"))
        ev = truncate(ev, ctx.base, st)
        last = ev[-1]["timestamp"].date()
        if st == ctx.ABS:
            snap = last + timedelta(days=uint(rng, 0, 20))
            prom = promised_from_ship(rng, ctx, ev)
        elif si <= ctx.base.index(ctx.KOMM):
            if k == "boundary_e3":
                prom = bday_on_or_after(last + timedelta(days=thr + uint(rng, 0, 3)))
                snap = prom - timedelta(days=thr)
            else:
                snap = last + timedelta(days=uint(rng, 0, 4))
                prom = bday_on_or_after(snap + timedelta(days=uint(rng, thr + 1, thr + 10)))  # Grenzfall nur gezielt
        elif st == ctx.RECH:
            terms = c["payment_terms_days"]
            snap = last + timedelta(days=terms if k == "boundary_e6" else uint(rng, 0, terms))
            prom = promised_from_ship(rng, ctx, ev)
        else:  # VERS, ZAHL
            snap = last + timedelta(days=uint(rng, 0, 3))
            prom = promised_from_ship(rng, ctx, ev)
        text, cat = None, "none"
        if i in noise:
            tpl = pick_template(rng, ctx, "irrelevant")
            text, cat = (tpl, text_params(rng, ctx, ev, snap, c)), "irrelevant"
            tags.append("noise_text")
        cases.append(make_case("none", c, ev, snap, prom, tags, text, cat))
    return cases


def delayed_promise(rng, ctx, c, last):
    if rng.random() < GEN["e3_imminent_share"]:
        delta = uint(rng, 0, ctx.thr - 1)          # drohend
    else:
        delta = uint(rng, GEN["e3_delta_min_days"], -1)   # Termin bereits ueberschritten
    floor_ = max(last + timedelta(days=max(delta, 0) + uint(rng, 0, 3)),
                 c["start"].date() + timedelta(days=3))
    prom = bday_on_or_after(floor_)
    snap = prom - timedelta(days=delta)
    tags = [f"delivery_delta_{delta}d"]
    if delta < 0:
        tags.append("promise_passed")
    if delta == ctx.thr - 1:
        tags.append("edge_e3")
    return prom, snap, tags


def build_e2(rng, ctx, n, bdays, e7=False):
    cases = []
    for _ in range(n):
        tags = ["running"]
        c = draw_common(rng, bdays)
        credit_exceed(rng, c, tags)
        st = ctx.ERF if rng.random() < 0.3 else ctx.KRED
        n_aend = uint(rng, 1, 2) if rng.random() < GEN["other_variant_share"] else 0
        if n_aend:
            tags.append("variant_aendern")
        ev = truncate(full_sequence(rng, ctx, c, n_aendern=n_aend, aendern_late=False), ctx.base, st)
        last = ev[-1]["timestamp"].date()
        if e7:
            prom, snap, t2 = delayed_promise(rng, ctx, c, last)
            tags += t2
        else:
            snap = last + timedelta(days=uint(rng, 0, 5))
            prom = bday_on_or_after(snap + timedelta(days=uint(rng, ctx.thr, ctx.thr + 15)))
        text, cat, t3 = maybe_noise(rng, ctx, ev, snap, c, GEN["other_noise_share"])
        cases.append(make_case("E7" if e7 else "E2", c, ev, snap, prom, tags + t3, text, cat))
    return cases


def build_e3(rng, ctx, n, bdays):
    cases = []
    for _ in range(n):
        tags = ["running"]
        c = draw_common(rng, bdays)
        credit_ok(rng, c)
        u = rng.random()
        st = ctx.KRED if u < 0.2 else (ctx.BEST if u < 0.6 else ctx.KOMM)
        si = ctx.base.index(st)
        n_aend = uint(rng, 1, 2) if rng.random() < GEN["other_variant_share"] else 0
        if n_aend:
            tags.append("variant_aendern")
        ev = truncate(full_sequence(rng, ctx, c, n_aendern=n_aend,
                                    aendern_late=si >= ctx.base.index(ctx.BEST)), ctx.base, st)
        prom, snap, t2 = delayed_promise(rng, ctx, c, ev[-1]["timestamp"].date())
        text, cat, t3 = maybe_noise(rng, ctx, ev, snap, c, GEN["other_noise_share"])
        cases.append(make_case("E3", c, ev, snap, prom, tags + t2 + t3, text, cat))
    return cases


def build_e5(rng, ctx, n, bdays):
    cases = []
    for _ in range(n):
        c = draw_common(rng, bdays)
        credit_ok(rng, c)
        st = ctx.ABS if rng.random() < 0.5 else ctx.VERS
        tags = ["completed" if st == ctx.ABS else "running"]
        n_aend = uint(rng, 1, 2) if rng.random() < GEN["other_variant_share"] else 0
        if n_aend:
            tags.append("variant_aendern")
        ev = truncate(full_sequence(rng, ctx, c, n_aendern=n_aend, e5=True), ctx.base_e5, st)
        last = ev[-1]["timestamp"].date()
        if st == ctx.ABS:
            snap = last + timedelta(days=uint(rng, 0, 20))
        else:
            due = first_ts(ev, ctx.RECH).date() + timedelta(days=c["payment_terms_days"])
            snap = last + timedelta(days=uint(rng, 0, min(5, (due - last).days)))
        prom = promised_from_ship(rng, ctx, ev)
        text, cat, t3 = maybe_noise(rng, ctx, ev, snap, c, GEN["other_noise_share"])
        cases.append(make_case("E5", c, ev, snap, prom, tags + t3, text, cat))
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
        rem = od >= GEN["e6_reminder_min_overdue"] and rng.random() < GEN["e6_reminder_share"]
        if rem:
            tags.append("variant_erinnerung")
        # Erinnerung liegt laut full_sequence 3 bis 10 Tage nach Faelligkeit, also vor dem Stichtag
        ev = truncate(full_sequence(rng, ctx, c, n_aendern=n_aend, teil=teil, reminder=rem), ctx.base, ctx.RECH)
        inv = first_ts(ev, ctx.RECH).date()
        snap = inv + timedelta(days=c["payment_terms_days"] + od)
        tags.append(f"overdue_{od}d")
        if od == lo:
            tags.append("edge_e6")
        prom = promised_from_ship(rng, ctx, ev)
        tpl = pick_template(rng, ctx, cats[i])
        text = (tpl, text_params(rng, ctx, ev, snap, c))
        tags.append("text_" + tpl["stil"])
        cases.append(make_case("E6", c, ev, snap, prom, tags, text, cats[i]))
    return cases


# ---------------------------------------------------------------------------
# Hauptablauf
# ---------------------------------------------------------------------------
def business_days(d0, d1):
    out, d = [], d0
    while d <= d1:
        if is_bday(d):
            out.append(d)
        d += timedelta(days=1)
    return out


def generate(spec_path, tpl_path, out_dir):
    spec = yaml.safe_load(Path(spec_path).read_text(encoding="utf-8"))
    tpl_raw = yaml.safe_load(Path(tpl_path).read_text(encoding="utf-8"))
    ctx = Ctx(spec, tpl_raw["categories"])
    counts = ctx.counts()
    bdays = business_days(date.fromisoformat(GEN["start_from"]), date.fromisoformat(GEN["start_to"]))

    builders = {
        "none": lambda r, n: build_none(r, ctx, n, bdays),
        "E2": lambda r, n: build_e2(r, ctx, n, bdays),
        "E3": lambda r, n: build_e3(r, ctx, n, bdays),
        "E5": lambda r, n: build_e5(r, ctx, n, bdays),
        "E6": lambda r, n: build_e6(r, ctx, n, bdays),
        "E7": lambda r, n: build_e2(r, ctx, n, bdays, e7=True),
    }
    cases = []
    for t in TYPE_ORDER:
        cases += builders[t](rng_for(ctx.seed, "type:" + t), counts[t])

    # Mischen, dann IDs vergeben
    perm = rng_for(ctx.seed, "shuffle").permutation(len(cases))
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
            params = dict(params, auftragsnr=cid)
            free_text = tpl["text"].format_map(params)
        a = cs["attrs"]
        case_rows.append({
            "case_id": cid,
            "order_value": a["order_value"],
            "customer_segment": a["customer_segment"],
            "credit_limit": a["credit_limit"],
            "open_items": a["open_items"],
            "payment_history": a["payment_history"],
            "payment_terms_days": a["payment_terms_days"],
            "promised_delivery_date": cs["promised"].isoformat(),
            "free_text": free_text,
            "snapshot_time": datetime.combine(cs["snap"], time(hh, mm, ss)).strftime(TS_FMT),
        })
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
    cols = ["case_id"] + list(spec["case_attributes"])
    ev_df = pd.DataFrame(ev_rows, columns=["case_id", "activity", "timestamp", "resource", "role"])
    cs_df = pd.DataFrame(case_rows)[cols]
    gt_df = pd.DataFrame(gt_rows)

    # Pilot-Stichprobe
    prng = rng_for(ctx.seed, "pilot")
    pc = dict(GEN["pilot_composition"])
    if "composition" in spec["pilot"]:                       # ab spec v0.3.0 maschinenlesbar
        sc = spec["pilot"]["composition"]
        pc = {"E2": sc["E2"], "E3": sc["E3"], "E6": sc["E6"], "none": sc["none"],
              "none_with_noise_text": sc["none_with_free_text"]}
    excl = set(spec["pilot"]["exclude_types"])
    by = lambda t: sorted(gt_df.loc[gt_df.exception_type == t, "case_id"])
    pick = lambda lst, k: [lst[j] for j in sorted(prng.choice(len(lst), size=k, replace=False))]
    pilot = []
    pilot += pick(by("E2"), pc["E2"])
    pilot += pick(by("E3"), pc["E3"])
    e6 = gt_df[gt_df.exception_type == "E6"]
    one_each = []
    for cat in ctx.e6_cats:
        one_each += pick(sorted(e6.loc[e6.free_text_category == cat, "case_id"]), 1)
    extra_cats = [ctx.e6_cats[j] for j in sorted(prng.choice(len(ctx.e6_cats), size=pc["E6"] - len(ctx.e6_cats), replace=False))]
    for cat in extra_cats:
        pool = [x for x in sorted(e6.loc[e6.free_text_category == cat, "case_id"]) if x not in one_each]
        one_each += pick(pool, 1)
    pilot += one_each
    hp = gt_df[gt_df.exception_type == "none"].merge(cs_df[["case_id", "free_text"]], on="case_id")
    pilot += pick(sorted(hp.loc[hp.free_text != "", "case_id"]), pc["none_with_noise_text"])
    pilot += pick(sorted(hp.loc[hp.free_text == "", "case_id"]), pc["none"] - pc["none_with_noise_text"])
    assert len(pilot) == int(spec["pilot"]["n_cases"]), "Pilotumfang passt nicht zur spec"
    assert not (set(gt_df.set_index("case_id").loc[pilot, "exception_type"]) & excl)
    pilot_df = pd.DataFrame({"case_id": sorted(pilot)})

    # Blindes Labeling E6
    lrng = rng_for(ctx.seed, "labeling")
    e6_ids = by("E6")
    lab = sorted(e6_ids[j] for j in lrng.choice(len(e6_ids), size=GEN["labeling_e6_n"], replace=False))
    lab_df = cs_df.set_index("case_id").loc[lab, ["free_text"]].reset_index()
    lab_df["label"] = ""

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    kw = dict(index=False, encoding="utf-8", lineterminator="\n")
    ev_df.to_csv(out / "event_log.csv", **kw)
    cs_df.to_csv(out / "cases.csv", **kw)
    gt_df.to_csv(out / "ground_truth.csv", **kw)
    pilot_df.to_csv(out / "pilot_sample.csv", **kw)
    lab_df.to_csv(out / "labeling_e6_blind.csv", **kw)
    return {"cases": len(cs_df), "events": len(ev_df), "counts": counts}


def main():
    ap = argparse.ArgumentParser(description="Synthetischer O2C-Log-Generator (Thema 75)")
    ap.add_argument("--spec", default=str(ROOT / "spec" / "spec.yaml"))
    ap.add_argument("--templates", default=str(ROOT / "data" / "freitext_vorlagen.yaml"))
    ap.add_argument("--out", default=str(ROOT / "data"))
    a = ap.parse_args()
    res = generate(a.spec, a.templates, a.out)
    print(f"Faelle: {res['cases']}, Events: {res['events']}, Verteilung: {res['counts']}")


if __name__ == "__main__":
    main()
