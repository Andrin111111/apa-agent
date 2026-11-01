#!/usr/bin/env python3
"""
audit_view.py | WI-Projekt Thema 75 | v1.0 (Schritt 4)

Kompakte, lesbare Ansicht von out/audit_log.jsonl (fuer K4, K5 und die Demo). Liest nur, aendert nichts.

  python src/audit_view.py --label mock --case C0317 --run 1
  python src/audit_view.py --label smoke                  # alle Eintraege eines Labels
  python src/audit_view.py --label mock --disposition blocked_to_human
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def fmt_actions(acts):
    return ", ".join(f"{a.get('action_id')}{' an ' + a['target_role'] if a.get('target_role') else ''}"
                     for a in acts or [] if isinstance(a, dict)) or "-"


def show(e):
    p = e.get("parsed_output") or {}
    g = e.get("guardrail") or {}
    ap = e.get("approval") or {}
    co = e.get("case_object") or {}
    L = [f"=== {e['case_id']} | Run {e['run']} | {e['label']} | {e['ts']} ===",
         f"Lauf {e['run_id']} | {e['client']} {e['model']} {str(e.get('model_digest', ''))[:12]} | "
         f"T={e['temperature']} Seed={e['seed']} | Prompt v{e['prompt_version']}{e.get('prompt_variant', '')} "
         f"{e['prompt_hash'][:12]} | Fallobjekt {e['case_object_hash'][:12]} | {e.get('duration_ms')} ms",
         f"Erkennung : {co.get('detection', {}).get('detected_type')} {co.get('detection', {}).get('hard_triggers')}"
         f" | Freitext: {co.get('free_text') or '-'}"]
    if e.get("error"):
        L.append(f"FEHLER    : {e['error']}")
    else:
        L += [f"Agent     : Typ {p.get('exception_type', '-')} | Aktionen {fmt_actions(p.get('actions'))}",
              f"Begruendung: {p.get('rationale', '-')}",
              f"Belege    : {', '.join(p.get('key_evidence') or []) or '-'}",
              f"Guardrails: {'bestanden' if g.get('passed') else 'BLOCKIERT ' + '; '.join(v['rule'] + ' (' + str(v['detail']) + ')' for v in g.get('violations', []))}"
              + (f" | Hinweise: {', '.join(w['rule'] for w in g.get('warnings', []))}" if g.get("warnings") else ""),
              f"Freigabe  : {ap.get('status')} ({ap.get('mode')}) "
              + "; ".join(f"{d['action_id']}={d['decision']}" for d in ap.get("decisions", [])),
              f"Ausgefuehrt: {fmt_actions(e.get('executed_actions'))} | offen: {fmt_actions(e.get('pending_actions'))}"
              f" | Disposition: {e.get('disposition')}"]
        if p == {} and e.get("raw_output") is not None:
            L.append(f"Rohausgabe: {e['raw_output'][:300]}")
    print("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", default=str(ROOT / "out" / "audit_log.jsonl"))
    ap.add_argument("--label")
    ap.add_argument("--case")
    ap.add_argument("--run", type=int)
    ap.add_argument("--disposition")
    ap.add_argument("--n", type=int, default=0, help="hoechstens n Eintraege (0 = alle)")
    a = ap.parse_args()
    shown = 0
    for line in Path(a.audit).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        if (a.label and e.get("label") != a.label) or (a.case and e.get("case_id") != a.case) or \
                (a.run and e.get("run") != a.run) or (a.disposition and e.get("disposition") != a.disposition):
            continue
        show(e)
        shown += 1
        if a.n and shown >= a.n:
            break
    if not shown:
        print("Keine Eintraege gefunden.")


if __name__ == "__main__":
    main()
