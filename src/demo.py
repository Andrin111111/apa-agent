#!/usr/bin/env python3
"""
demo.py | WI-Projekt Thema 75 | v1.0 (Schritt 6, AP8)

Live-Demo fuer Folie 6. Duenner Wrapper um run_agent.run (keine zweite Logik): pro Fall ein Aufruf der
Pipeline mit k = 1, Freigabe interaktiv. demo.py zeigt nur an und vergleicht:
  Fallkern (Erkennung, Trigger, 2 bis 3 Kennzahlen, Freitext)  -> vor dem LLM-Aufruf
  Entscheid des Agenten, Guardrails, Freigabe                   -> Hook on_decision (vor der Freigabe)
  Ergebnis (Disposition), Vergleich mit Baseline und Evaluation -> nach dem Aufruf

Modi:
  --client ollama   live, lokales LLM, gleiche Konfiguration wie die Evaluation (Prompt v1.2a, T 0, Seed 42)
  --client replay   Fallback ohne LLM: spielt die Rohausgaben einer Aufzeichnung (Label demo_ref) ab.
                    Anzeige identisch, nur Kopfzeile und Zeitangaben nennen die Aufzeichnung.
  --check           Vorabpruefung und Aufwaermen (Ollama, Digest, Hashes, Schema, Modell laden, Replay bereit).
                    Schreibt nichts ins Audit-Log.
Anzeige: --baseline (Entscheidung der Regel), --truth (Soll laut Ground Truth, nur Anzeige, Bewertung mit
metrics.judge), --clear (jeder Fall oben am Bildschirm), --verbose (Belege und Rohausgabe).
Aenderung an bestehendem Code: nur der optionale Hook on_decision in run_agent.run (Standard None).

Dateien (eigenes Verzeichnis, out/audit_log.jsonl der Auswertung wird nur gelesen):
  out/demo/audit_log_demo.jsonl          Audit-Log der Demo (alle Demo-Labels, angehaengt)
  out/demo/agent_actions_<label>.jsonl   wie run_agent, pro Demo-Lauf ein Label (Standard mit Zeitstempel)

Beispiele (aus dem Repo-Root, venv):
  python src/demo.py --check
  python src/demo.py --client ollama --approver Jan --baseline --truth --clear
  python src/demo.py --client replay --approver Jan --baseline --truth --clear
  python src/demo.py --client ollama --cases C0776 --approver Jan --baseline --truth   # Reserve: echter Fehler
  printf 'j\\nj\\n' | python src/demo.py --client ollama --label demo_ref --no-pause   # Aufzeichnung erstellen
  python src/audit_view.py --audit out/demo/audit_log_demo.jsonl --label <label>
"""

import argparse
import json
import os
import subprocess
import sys
import textwrap
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_agent  # noqa: E402
from case_object import CaseStore, object_hash, sha256  # noqa: E402
from guardrails import load_spec, ollama_format_schema  # noqa: E402
import llm_client  # noqa: E402
import metrics  # noqa: E402  (nur --truth: Bewertung wie in der Evaluation)

ROOT = Path(__file__).resolve().parent.parent
DEMO_DIR = ROOT / "out" / "demo"
EVAL_AUDIT = ROOT / "out" / "audit_log.jsonl"
BASELINE = ROOT / "out" / "baseline_actions.jsonl"
DEFAULT_CASES = "C0902,C0537,C0244"
MODEL = "qwen3.5:9b-q4_K_M"
EVAL_LABELS = ("pilot_t0", "e6_t0")          # Evaluationslaeufe mit gleicher Konfiguration (T 0, Seed 42)
REF_LABEL = "demo_ref"
ROLE_ACTIONS = {"A5", "A6"}

DISPOSITION_TEXT = {
    "executed": "alles ausgefuehrt",
    "pending_approval": "wartet auf Freigabe, nichts ausgefuehrt",
    "partially_executed_pending_approval": "autonome Aktionen ausgefuehrt, Rest wartet auf Freigabe",
    "rejected_by_human": "vom Menschen abgelehnt, nicht ausgefuehrt",
    "blocked_to_human": "von Guardrail blockiert, Fall geht an einen Menschen",
    "llm_error": "LLM-Fehler, keine Ausgabe",
}


# ---------------------------------------------------------------- Anzeige

class Screen:
    CODES = {"b": "1", "ok": "32", "warn": "33", "bad": "31", "head": "1;36", "dim": "2"}

    def __init__(self, write=print, color=False, width=78):
        self.write, self.color, self.width = write, color, width

    def c(self, style, s):
        return f"\033[{self.CODES[style]}m{s}\033[0m" if self.color else s

    def __call__(self, s=""):
        self.write(s)

    def rule(self, ch="="):
        self.write(self.c("dim", ch * self.width))

    def section(self, title, value="", right=""):
        left = f" {self.c('head', f'{title:<11}')} {value}"
        if right:
            pad = self.width - len(f" {title:<11} {value}") - len(right)
            left += " " * max(2, pad) + self.c("dim", right)
        self.write(left)

    def kv(self, key, value):
        lead = f"    {key:<12}: " if key else " " * 18
        body = textwrap.wrap(str(value), self.width - len(lead)) or ["-"]
        self.write(lead + body[0])
        for x in body[1:]:
            self.write(" " * len(lead) + x)

    def para(self, text, indent=6):
        for x in textwrap.wrap(str(text), self.width - indent):
            self.write(" " * indent + x)


def chf(n):
    return "CHF " + f"{int(n):,}".replace(",", "'")


def pct(x):
    return f"{100 * x:.1f} %".replace(".", ",")


def secs(ms):
    return "-" if ms is None else f"{ms / 1000:.1f} s".replace(".", ",")


def days_phrase(d):
    if d is None:
        return "-"
    if d > 1:
        return f"in {d} Tagen"
    if d == 1:
        return "morgen (in 1 Tag)"
    if d == 0:
        return "heute"
    return "seit 1 Tag verpasst" if d == -1 else f"seit {-d} Tagen verpasst"


def dmy(s):
    try:
        return datetime.strptime(str(s)[:10], "%Y-%m-%d").strftime("%d.%m.%Y")
    except ValueError:
        return str(s)


def local_time(ts):
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).astimezone().strftime("%H:%M:%S")
    except (TypeError, ValueError):
        return str(ts)


class Names:
    def __init__(self, spec):
        self.types = {k: v["name"] for k, v in spec["exceptions"].items()}
        self.types.update({"none": "kein harter Trigger", "unknown": "Enthaltung"})
        self.actions = {k: v["name"] for k, v in spec["action_catalog"].items()}

    def action(self, a, detected_type=None, long=True):
        aid = a.get("action_id")
        s = aid + (f" {self.actions.get(aid, '?')}" if long else "")
        if long and aid == "A3" and detected_type == "E6":
            s += " (Mahnung)"
        if a.get("target_role"):
            s += f" an {a['target_role']}"
        return s

    def actions_short(self, acts):
        return "+".join(a.get("action_id", "?") + (f"/{a['target_role']}" if a.get("target_role") else "")
                        for a in acts or [] if isinstance(a, dict)) or "-"


def action_set(acts):
    return {(a.get("action_id"), a.get("target_role") if a.get("action_id") in ROLE_ACTIONS else None)
            for a in acts or [] if isinstance(a, dict)}


def case_lines(obj, names):
    a, d, det = obj["attributes"], obj["derived"], obj["detection"]
    t = det["detected_type"]
    trig = ", ".join(det.get("hard_triggers") or []) or "kein harter Trigger"
    if det.get("soft_trigger_free_text"):
        trig += " + Freitext eingegangen"
    L = [("Erkennung", f"{t} per Regel (deterministisch, ohne LLM)"),
         ("Trigger", f"{trig} | Stichtag {dmy(obj['snapshot_date'])}")]
    if t in ("E2", "E7"):
        L.append(("Kredit", f"Limit {chf(a['credit_limit'])}, Engagement {chf(d['credit_exposure'])} "
                            f"(+{pct(d['overshoot_ratio'] or 0)})"))
        L.append(("Kunde", f"Zahlungshistorie {a['payment_history']}, Segment {a['customer_segment']}"))
    if t in ("E3", "E7"):
        L.append(("Liefertermin", f"{dmy(a['promised_delivery_date'])}, {days_phrase(d['days_to_promised_delivery'])}, "
                                  f"{'versendet' if d['shipped'] else 'nicht versendet'}"))
        L.append(("Stand", f"letzte Aktivitaet: {d['last_activity']}"))
    if t == "E6":
        L.append(("Rechnung", f"{d['days_overdue']} Tage ueberfaellig (faellig {dmy(d['due_date'])}), "
                              f"{'bezahlt' if d['payment_received'] else 'nicht bezahlt'}"))
        L.append(("Kunde", f"Zahlungshistorie {a['payment_history']}, Mahnungen bisher {d['n_payment_reminders']}"))
    if t not in ("E2", "E3", "E6", "E7"):
        L.append(("Stand", f"letzte Aktivitaet: {d['last_activity']}"))
    L.append(("Freitext", f'"{obj["free_text"]}"' if obj.get("free_text") else "-"))
    return L


# ---------------------------------------------------------------- Vergleichsdaten (nur lesen)

def read_jsonl(path):
    p = Path(path)
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def eval_index(path=EVAL_AUDIT):
    """Letzter Eintrag pro Fall aus den Evaluationslaeufen (Run 1)."""
    idx = {}
    for e in read_jsonl(path):
        if e.get("label") in EVAL_LABELS and e.get("run") == 1 and e.get("raw_output") is not None:
            idx[e["case_id"]] = e
    return idx


def label_index(path, label):
    return {e["case_id"]: e for e in read_jsonl(path) if e.get("label") == label and e.get("raw_output") is not None}


def baseline_index(path=BASELINE):
    return {r["case_id"]: r for r in read_jsonl(path)}


def repro_status(entry, ev):
    """Vergleich der Rohausgabe mit dem Evaluationslauf. Rueckgabe (status, text)."""
    if ev is None:
        return "none", "kein Evaluationslauf fuer diesen Fall"
    keys = ("prompt_hash", "schema_hash", "case_object_hash", "temperature", "seed")
    diff = [k for k in keys if entry.get(k) != ev.get(k)]
    if diff:
        return "config", f"andere Konfiguration als {ev['label']} ({', '.join(diff)}), kein Vergleich"
    day = datetime.strptime(ev["ts"][:10], "%Y-%m-%d").strftime("%d.%m.%Y")
    if entry.get("raw_output") == ev.get("raw_output"):
        return "same", f"Ausgabe bytegleich mit Evaluationslauf {ev['label']} vom {day}"
    return "diff", f"Ausgabe weicht von {ev['label']} vom {day} ab (Rohtext verschieden)"


# ---------------------------------------------------------------- Demo-Lauf

def parse_args(argv=None):
    ap = argparse.ArgumentParser(description="Demo Folie 6 (Wrapper um run_agent.run)")
    ap.add_argument("--client", choices=["ollama", "replay"], default="ollama")
    ap.add_argument("--cases", default=DEFAULT_CASES, help=f"Fall-IDs, Komma (Standard {DEFAULT_CASES})")
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--approver", default="Demo", help="Name fuer die Freigabe im Audit-Log")
    ap.add_argument("--baseline", action="store_true", help="Entscheidung der Regel-Baseline zum Vergleich zeigen")
    ap.add_argument("--truth", action="store_true",
                    help="Soll laut Ground Truth zeigen (nur Anzeige, der Agent sieht sie nie), Bewertung mit metrics.judge")
    ap.add_argument("--label", default="", help="Standard demo_live_<Zeit> bzw. demo_replay_<Zeit>")
    ap.add_argument("--replay-label", default=REF_LABEL)
    ap.add_argument("--demo-dir", default=str(DEMO_DIR))
    ap.add_argument("--eval-audit", default=str(EVAL_AUDIT))
    ap.add_argument("--baseline-file", default=str(BASELINE))
    ap.add_argument("--no-pause", action="store_true", help="nicht auf Enter warten (Tests, Aufzeichnung)")
    ap.add_argument("--no-color", action="store_true")
    ap.add_argument("--clear", action="store_true", help="Bildschirm vor jedem Fall leeren (Beamer)")
    ap.add_argument("--width", type=int, default=78)
    ap.add_argument("--timeout", type=int, default=30, help="Sekunden pro LLM-Aufruf (Demo: kurz, normal 6 bis 11 s)")
    ap.add_argument("--url", default=llm_client.DEFAULT_URL)
    ap.add_argument("--verbose", action="store_true", help="Rohausgabe und Belege zeigen")
    ap.add_argument("--check", action="store_true", help="Vorabpruefung und Aufwaermen, keine Demo")
    ap.add_argument("--keep-alive", default="90m", help="nur --check: Modell so lange geladen halten")
    return ap.parse_args(argv)


def use_color(a):
    return not a.no_color and not os.environ.get("NO_COLOR") and sys.stdout.isatty()


def run_demo(a, ask=input, write=print, echo=None):
    scr = Screen(write, use_color(a), a.width)
    if echo is None:
        echo = ask is input and not sys.stdin.isatty()
    spec = load_spec()
    names = Names(spec)
    demo_dir = Path(a.demo_dir)
    demo_dir.mkdir(parents=True, exist_ok=True)
    audit = demo_dir / "audit_log_demo.jsonl"
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    label = a.label or f"demo_{'live' if a.client == 'ollama' else 'replay'}_{stamp}"
    if (demo_dir / f"agent_actions_{label}.jsonl").exists():
        raise SystemExit(f"Label '{label}' existiert bereits in {demo_dir}. Anderes Label waehlen.")
    cases = [c.strip() for c in a.cases.split(",") if c.strip()]
    store = CaseStore()
    unknown = [c for c in cases if c not in store.cases]
    if unknown:
        raise SystemExit(f"Unbekannte Fall-IDs: {unknown}")
    ev_idx = eval_index(a.eval_audit)
    base_idx = baseline_index(a.baseline_file) if a.baseline else {}
    gt = metrics.load_gt() if a.truth else None
    ref_idx = {}
    if a.client == "replay":
        ref_idx = label_index(audit, a.replay_label)
        missing = [c for c in cases if c not in ref_idx]
        if missing:
            scr(scr.c("bad", f"Keine Aufzeichnung '{a.replay_label}' fuer {missing} in {audit}."))
            scr("Aufzeichnung erstellen (live): printf 'j\\nj\\n' | python src/demo.py --client ollama "
                f"--label {a.replay_label} --no-pause")
            return 2
    _, p_version, p_hash = run_agent.load_prompt("a")
    schema_hash = sha256(json.dumps(ollama_format_schema(spec), sort_keys=True))
    temp, seed = spec["meta"]["llm"]["temperature"], spec["meta"]["llm"]["seed"]
    same_cfg = all(ev_idx.get(c) is None or (ev_idx[c]["prompt_hash"] == p_hash and ev_idx[c]["schema_hash"] == schema_hash)
                   for c in cases)

    scr.rule()
    mode = (scr.c("ok", "LIVE") + ": lokales LLM (Ollama), offline" if a.client == "ollama" else
            scr.c("warn", "AUFZEICHNUNG") + f": Replay von '{a.replay_label}', kein LLM-Aufruf")
    scr(f" {scr.c('b', 'APA-Agent Demo')} | Order-to-Cash, Ausnahmefaelle")
    scr(f" Modus {mode}")
    scr(f" Modell {a.model if a.client == 'ollama' else next(iter(ref_idx.values())).get('model')} | "
        f"Prompt v{p_version}a | T={temp} | Seed {seed}")
    scr(" " + (scr.c("ok", "Konfiguration wie Evaluation") if same_cfg else scr.c("warn", "Konfiguration WEICHT AB"))
        + " (Prompt, Schema, Modell, T, Seed)")
    scr(scr.c("dim", " Erkennung > Fallobjekt > LLM > Guardrails > Freigabe > Aktion > Audit-Log"))
    scr.rule()

    rows, code = [], 0
    for i, cid in enumerate(cases, 1):
        obj, det = store.get(cid)
        t = det["detected_type"]
        if not a.no_pause:
            ask(scr.c("dim", f"[Enter] Fall {i}/{len(cases)}: {cid} ") )
        if a.clear:
            write("\033[2J\033[H")
        else:
            scr()
        scr.rule("-")
        scr(f" {scr.c('b', f'Fall {i}/{len(cases)}  {cid}')}   {t} {names.types.get(t, '')}")
        scr.rule("-")
        scr.section("FALL", "was die Regel-Erkennung liefert")
        for k, v in case_lines(obj, names):
            scr.kv(k, v)
        scr()
        if a.client == "ollama":
            scr(scr.c("dim", "    ... lokales LLM entscheidet (ca. 7 s)"))
        else:
            scr(scr.c("dim", "    ... Aufzeichnung wird abgespielt"))
        captured = {}

        def on_decision(entry, gr, _t=t, _cid=cid):
            captured["entry"], captured["gr"] = entry, gr
            p = gr.parsed or {}
            if a.client == "ollama":
                right = f"{secs((entry.get('llm_meta') or {}).get('wall_ms'))}"
                src = f"{entry.get('model')}, lokal, T={entry['temperature']}, Seed {entry['seed']}"
            else:
                ref = ref_idx.get(_cid, {})
                right = f"{secs((ref.get('llm_meta') or {}).get('wall_ms'))}"
                src = f"{entry.get('model')}, aufgezeichnet, T={entry['temperature']}, Seed {entry['seed']}"
            scr.section("AGENT", src, right)
            mism = (entry.get("llm_meta") or {}).get("replay_mismatch")
            if mism:
                scr.kv("Achtung", scr.c("warn", f"Aufzeichnung passt nicht zur Konfiguration ({', '.join(mism)})"))
            if gr.parsed is None:
                scr.kv("Ausgabe", scr.c("bad", "nicht lesbar"))
                scr.para((entry.get("raw_output") or "")[:300])
            else:
                et = p.get("exception_type", "-")
                scr.kv("Typ", f"{et} {names.types.get(et, '')}")
                need = set(gr.requires_approval)
                for j, act in enumerate(p.get("actions") or []):
                    if not isinstance(act, dict):
                        continue
                    tag = scr.c("warn", "[Freigabe noetig]") if act.get("action_id") in need else scr.c("ok", "[autonom]")
                    scr.kv("Aktionen" if j == 0 else "", f"{names.action(act, _t)}  {tag}")
                scr(f"    Begruendung {scr.c('dim', '(Text des Modells, nicht geprueft)')}:")
                scr.para(p.get("rationale", "-"))
                if a.verbose:
                    scr.kv("Belege", "; ".join(p.get("key_evidence") or []))
            if a.baseline:
                b = base_idx.get(_cid)
                if b is None:
                    scr.section("REGEL", "keine Baseline-Ausgabe")
                else:
                    same = action_set(b["actions"]) == action_set(p.get("actions"))
                    verdict = scr.c("ok", "gleich wie Agent") if same else scr.c("warn", "ANDERS als Agent")
                    scr.section("REGEL", f"{', '.join(names.action(x, _t) for x in b['actions'])}  -> {verdict}")
                    if b.get("_baseline_category"):
                        scr.kv("", f"Keyword-Regel ordnet den Freitext als '{b['_baseline_category']}' ein")
            if gt is not None and _cid in gt.index:
                g_row = gt.loc[_cid]
                soll = " oder ".join("+".join(sorted(x)) for x in g_row.allowed) + (
                    f" an {g_row.expected_target_role}" if g_row.expected_target_role else "")
                ok_agent, why = metrics.judge(p if gr.parsed is not None else None, g_row)
                v_agent = scr.c("ok", "Agent korrekt") if ok_agent else scr.c("bad", f"Agent FALSCH ({why})")
                if a.baseline and _cid in base_idx:
                    ok_b, _ = metrics.judge(base_idx[_cid], g_row)
                    v_agent += ", " + (scr.c("ok", "Regel korrekt") if ok_b else scr.c("bad", "Regel FALSCH"))
                scr.section("SOLL", f"{soll} (Ground Truth)  -> {v_agent}")
            if gr.passed:
                g = scr.c("ok", "bestanden") + scr.c("dim", " (prueft Form, nicht fachliche Richtigkeit)")
            else:
                g = scr.c("bad", "BLOCKIERT ") + ", ".join(v["rule"] for v in gr.violations) + " -> an einen Menschen"
            scr.section("GUARDRAILS", g)
            if gr.warnings:
                scr.kv("Hinweise", ", ".join(w["rule"] for w in gr.warnings))
            if a.verbose:
                scr.section("ROH", "")
                scr.para(entry.get("raw_output") or "")
            if gr.passed and gr.requires_approval:
                scr.section("FREIGABE", scr.c("warn", f"Mensch entscheidet ({', '.join(gr.requires_approval)}, "
                                                      "Autonomiestufe 'Freigabe')"))
            elif gr.passed:
                scr.section("FREIGABE", "nicht noetig, Aktionen sind autonom (laufen sofort)")

        argv = ["--cases", cid, "--k", "1", "--client", a.client, "--label", label,
                "--approval", "interactive", "--approver", a.approver, "--out-dir", str(demo_dir),
                "--audit-log", str(audit), "--timeout", str(a.timeout), "--url", a.url]
        argv += ["--model", a.model] if a.client == "ollama" else ["--replay-label", a.replay_label]
        def ask_approval(p):
            ans = ask("    " + p.strip() + " ")
            if echo:                                              # Eingabe per Pipe: Antwort sichtbar machen
                scr(ans)
            return ans

        try:
            run_agent.run(run_agent.parse_args(argv), ask=ask_approval,
                          show=(lambda *x: scr(" ".join(map(str, x)))) if a.verbose else (lambda *x: None),
                          on_decision=on_decision)
        except ValueError as e:                                   # z. B. Replay ohne Aufzeichnung
            scr(scr.c("bad", f"Fehler: {e}"))
            return 2
        entry = captured.get("entry")
        if entry is None or "disposition" not in entry:
            err = [e for e in read_jsonl(audit) if e.get("label") == label and e.get("case_id") == cid and e.get("error")]
            scr(scr.c("bad", "    Kein Ergebnis: " + (err[-1]["error"][:200] if err else "abgebrochen")))
            scr("    Fallback: python src/demo.py --client replay --approver " + a.approver
                + (" --baseline" if a.baseline else ""))
            code = 2
            break
        disp = entry["disposition"]
        style = {"executed": "ok", "rejected_by_human": "bad", "blocked_to_human": "bad", "llm_error": "bad"}.get(disp, "warn")
        scr.section("ERGEBNIS", scr.c(style, disp) + f" ({DISPOSITION_TEXT.get(disp, '')})")
        for x in entry.get("executed_actions") or []:
            scr.kv("ausgefuehrt", x["effect"])
        for x in entry.get("pending_actions") or []:
            scr.kv("offen", names.action(x, t))
        for x in entry.get("rejected_actions") or []:
            scr.kv("abgelehnt", names.action(x, t))
        for d in (entry.get("approval") or {}).get("decisions") or []:
            word = {"approved": "freigegeben", "rejected": "abgelehnt"}.get(d["decision"], "offen gelassen")
            scr.kv("Freigabe", f"{d['action_id']} {word} von {d['by']} um {local_time(d['ts'])}"
                               + (f", Grund: {d['comment']}" if d.get("comment") else ""))
        st, txt = repro_status(entry, ev_idx.get(cid))
        scr.section("REPRO", scr.c({"same": "ok", "diff": "warn"}.get(st, "dim"), txt))
        appr = (entry.get("approval") or {}).get("status")
        rows.append((cid, t, names.actions_short((entry.get("parsed_output") or {}).get("actions")),
                     {"approved": "freigegeben", "rejected": "abgelehnt", "pending": "offen", "mixed": "gemischt",
                      "not_required": "autonom"}.get(appr, appr or "-"), disp))

    scr()
    scr.rule()
    scr(f" {scr.c('b', 'ZUSAMMENFASSUNG')}  {len(rows)} Faelle | Label {label}")
    for r in rows:
        scr(f"    {r[0]}  {r[1]:<4} {r[2]:<24} {r[3]:<12} {r[4]}")
    scr(f" Audit-Log: {_rel(audit)}")
    scr(scr.c("dim", f" Nachlesen: python src/audit_view.py --audit {_rel(audit)} \\"))
    scr(scr.c("dim", f"            --label {label}"))
    scr.rule()
    return code


def _rel(p):
    try:
        return str(Path(p).resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


# ---------------------------------------------------------------- Vorabpruefung

def power_source():
    try:
        out = subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True, timeout=5).stdout
        first = out.splitlines()[0] if out else ""
        return "Netzteil" if "AC Power" in first else ("Akku" if "Battery" in first else "unbekannt")
    except (OSError, subprocess.SubprocessError):
        return "unbekannt"


def preflight(a, write=print):
    scr = Screen(write, use_color(a), a.width)
    ok_all = True

    def res(name, ok, detail):
        nonlocal ok_all
        ok_all &= bool(ok)
        scr(f"  {scr.c('ok', 'OK  ') if ok else scr.c('bad', 'FEHLT')} {name:<22} {detail}")

    spec = load_spec()
    cases = [c.strip() for c in a.cases.split(",") if c.strip()]
    ev_idx = eval_index(a.eval_audit)
    ev_any = next(iter(ev_idx.values()), {})
    # gleiche Optionen wie die Pipeline (num_ctx 8192, sonst laedt Ollama das Modell beim ersten Demo-Aufruf neu)
    c = llm_client.OllamaClient(a.model, base_url=a.url, think=False, timeout=max(a.timeout, 120),
                                keep_alive=a.keep_alive)
    scr(scr.c("b", "Vorabpruefung Demo"))
    ver = c.server_version()
    res("Ollama erreichbar", bool(ver), f"Version {ver or '-'} (Evaluation: "
        f"{(ev_any.get('llm_meta') or {}).get('server_version', '?')})")
    dig = c.model_digest()
    res("Modell-Digest", dig and dig == ev_any.get("model_digest"), f"{a.model} {dig[:12] or 'nicht gefunden'}")
    _, p_version, p_hash = run_agent.load_prompt("a")
    schema_hash = sha256(json.dumps(ollama_format_schema(spec), sort_keys=True))
    res("Prompt und Schema", all(ev_idx.get(x, {}).get("prompt_hash") == p_hash and
                                 ev_idx.get(x, {}).get("schema_hash") == schema_hash for x in cases),
        f"v{p_version}a {p_hash[:12]}, Schema {schema_hash[:12]} wie Evaluation")
    store = CaseStore()
    res("Fallobjekte", all(ev_idx.get(x, {}).get("case_object_hash") == object_hash(store.get(x)[0]) for x in cases),
        ", ".join(f"{x} ({ev_idx.get(x, {}).get('label', 'kein Lauf')})" for x in cases))
    if ver:
        t0 = time.monotonic()
        try:
            r = c.complete("Antworte immer ausfuehrlich in Prosa, niemals als JSON.", "Beschreibe Blau.",
                           llm_client.PROBE_SCHEMA)
            obj = json.loads(r.raw)
            ok = isinstance(obj, dict) and set(obj) == {"wort", "anzahl"}
        except (llm_client.LLMTransportError, json.JSONDecodeError):
            ok = False
        res("Schema erzwungen", ok, f"Probeaufruf {secs(int(1000 * (time.monotonic() - t0)))} (laedt das Modell)")
        # Aufwaermen mit dem echten Systemprompt (Prompt-Cache), an einem Fall ausserhalb der Demo, ohne Audit-Log
        warm = next(x for x in ("C0556", "C0671", "C0166") if x not in cases)
        system, _, _ = run_agent.load_prompt("a")
        t0 = time.monotonic()
        try:
            r = c.complete(system, run_agent.user_message(store.get(warm)[0]), ollama_format_schema(spec),
                           {"seed": int(spec["meta"]["llm"]["seed"])})
            res("Aufwaermen Agent", bool(r.raw), f"{warm}, {secs(int(1000 * (time.monotonic() - t0)))} "
                                                 "(nicht im Audit-Log)")
        except llm_client.LLMTransportError as e:
            res("Aufwaermen Agent", False, str(e)[:120])
        try:
            ps = c._request("/api/ps", timeout=10).get("models", [])
            m = next((x for x in ps if x.get("name") == a.model or x.get("model") == a.model), None)
            if m:
                gpu = m.get("size_vram", 0) / max(m.get("size", 1), 1)
                res("Modell geladen (GPU)", gpu > 0.99, f"{pct(gpu)} GPU, Kontext {m.get('context_length')}, "
                    f"bleibt geladen bis {str(m.get('expires_at', ''))[11:16]} (keep_alive {a.keep_alive})")
        except llm_client.LLMTransportError:
            pass
    ref = label_index(Path(a.demo_dir) / "audit_log_demo.jsonl", a.replay_label)
    rep_ok = all(x in ref and ref[x].get("raw_output") == ev_idx.get(x, {}).get("raw_output") for x in cases)
    res("Replay-Fallback", rep_ok, f"Aufzeichnung '{a.replay_label}': {sum(x in ref for x in cases)}/{len(cases)} "
        f"Faelle{', bytegleich mit Evaluation' if rep_ok else ''}")
    scr(f"  INFO  {'Stromversorgung':<22} {power_source()} (Netzteil anschliessen)")
    scr(scr.c("ok", "BEREIT") if ok_all else scr.c("bad", "NICHT BEREIT: siehe FEHLT oben (Notfallplan in docs/demo_drehbuch.md)"))
    return 0 if ok_all else 1


def main(argv=None, ask=input, write=print):
    a = parse_args(argv)
    try:
        return preflight(a, write) if a.check else run_demo(a, ask, write)
    except KeyboardInterrupt:
        write("\nAbgebrochen. Fallback: python src/demo.py --client replay --approver " + a.approver)
        return 130


if __name__ == "__main__":
    sys.exit(main())
