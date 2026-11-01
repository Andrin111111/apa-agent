#!/usr/bin/env python3
"""
approval.py | WI-Projekt Thema 75 | v1.0 (Schritt 4, AP5)

Menschliche Freigabe (Human-in-the-Loop) fuer Aktionen mit autonomy = approval (A5, A6, A7) und fuer
jede Aktion bei Typen mit approval_required (E7). Welche Aktionen betroffen sind, bestimmt
Guardrails.approval_needed (spec-getrieben).

Modi:
  batch        Standard fuer Laeufe. Alle freigabepflichtigen Aktionen bleiben 'pending'. Nichts wird
               automatisch freigegeben und nichts davon ausgefuehrt.
  interactive  CLI fuer die Demo. Pro Aktion: j = freigeben, n = ablehnen, Enter = offen lassen.

Ausfuehrung (simuliert): autonome Aktionen sofort, freigabepflichtige nur mit Entscheid 'approved'.
Annahme A1: Autonome Aktionen eines Falls werden ausgefuehrt, auch wenn andere Aktionen desselben Falls auf
Freigabe warten. Ausnahme E7: dort ist jede Aktion freigabepflichtig, es laeuft nichts vorab.
"""

from datetime import datetime, timezone

EFFECTS = {
    "A0": "Fall protokolliert, keine Massnahme",
    "A1": "Informationsanfrage erstellt",
    "A2": "Kundeninformation versendet",
    "A3": "Empfehlung fuer den naechsten Schritt hinterlegt",
    "A4": "Fall priorisiert (sichtbar in der Arbeitsliste)",
    "A5": "Fall neu zugewiesen an {role}",
    "A6": "Fall eskaliert an {role}",
    "A7": "Fall gesperrt",
}


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def request_approval(case_id, parsed, needed, mode="batch", approver="", ask=input, show=print):
    """Rueckgabe: dict mit required, mode, status, decisions (pro freigabepflichtiger Aktion)."""
    acts = [a for a in parsed.get("actions") or [] if a.get("action_id") in set(needed)]
    if not acts:
        return {"required": False, "mode": mode, "status": "not_required", "decisions": []}
    decisions = []
    if mode == "interactive":
        show(f"\nFreigabe fuer Fall {case_id} ({parsed.get('exception_type')})")
        show(f"  Begruendung: {parsed.get('rationale')}")
        show(f"  Belege: {', '.join(parsed.get('key_evidence') or [])}")
    for a in acts:
        d = {"action_id": a["action_id"], "target_role": a.get("target_role"), "decision": "pending",
             "by": "", "ts": _now(), "comment": ""}
        if mode == "interactive":
            label = a["action_id"] + (f" an {a['target_role']}" if a.get("target_role") else "")
            ans = ask(f"  {label} freigeben? [j/n/Enter=offen] ").strip().lower()
            if ans in ("j", "ja", "y"):
                d["decision"] = "approved"
            elif ans in ("n", "nein"):
                d["decision"] = "rejected"
                d["comment"] = ask("  Grund (optional): ").strip()
            d["by"] = approver or "cli"
            d["ts"] = _now()
        elif mode != "batch":
            raise ValueError("mode: batch | interactive")
        decisions.append(d)
    states = {d["decision"] for d in decisions}
    status = states.pop() if len(states) == 1 else "mixed"
    return {"required": True, "mode": mode, "status": status, "decisions": decisions}


def execute(parsed, needed, decisions):
    """Simulierte Ausfuehrung. Gibt (ausgefuehrt, offen, abgelehnt) als Listen von dicts zurueck."""
    need = set(needed)
    dec = {d["action_id"]: d["decision"] for d in decisions}
    done, pending, rejected = [], [], []
    for a in parsed.get("actions") or []:
        aid = a.get("action_id")
        item = {"action_id": aid, "target_role": a.get("target_role"),
                "effect": EFFECTS.get(aid, "?").format(role=a.get("target_role") or "?") + " (simuliert)"}
        if aid not in need or dec.get(aid) == "approved":
            done.append(item)
        elif dec.get(aid) == "rejected":
            rejected.append(item)
        else:
            pending.append(item)
    return done, pending, rejected
