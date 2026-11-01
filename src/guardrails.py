#!/usr/bin/env python3
"""
guardrails.py | WI-Projekt Thema 75 | v1.0 (Schritt 4, AP5)

Pruefschicht zwischen Agent und Ausfuehrung. Alle Regeln aus spec.guardrails, spec-getrieben (Katalog, Rollen,
Schema werden aus spec/spec.yaml gelesen, nicht im Code wiederholt).

Blockierende Regeln (Verstoss -> Ausgabe wird nicht ausgefuehrt, Fall geht an einen Menschen):
  schema_valid          JSON lesbar, Objekt, Pflichtfelder, Typen, Enum exception_type, actions nicht leer.
                        Ohne die Teile, die eigene Regeln haben (Aktions-ID, Rolle, Begruendung).
  action_in_catalog     jede action_id im Handlungskatalog
  target_role_exists    A5/A6 brauchen target_role; jede angegebene Rolle muss existieren
  rationale_present     Begruendung ist Text mit mindestens minLength Zeichen (ohne Leerraum am Rand)
  unknown_requires_A6   exception_type unknown -> Aktionsmenge genau {A6} (spec abstention.rule)
  case_id_match         Annahme G1 (Erweiterung): Ausgabe gehoert zum angefragten Fall
  autonomy_respected    Ausfuehrungsebene: keine Freigabe-Aktion ohne Freigabe (check_execution)

Hinweise (nicht blockierend, Annahme G2): type_mismatch (Typ weicht von der Erkennung ab, nicht unknown),
duplicate_action, role_on_non_role_action, extra_field, evidence_unknown_field (key_evidence nennt einen
Feldpfad attributes.*, derived.* oder detection.*, den es im Fallobjekt nicht gibt; Vorpruefung fuer K5).

Was die Guardrails NICHT pruefen koennen: ob die gewaehlte Aktion fachlich richtig ist (z. B. A3 statt A5 bei
einer indirekten Reklamation), ob die Begruendung stimmt oder nur plausibel klingt, ob key_evidence existiert.
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BLOCKING = ["schema_valid", "action_in_catalog", "target_role_exists", "rationale_present",
            "unknown_requires_A6", "case_id_match", "autonomy_respected"]
ROLE_ACTIONS = {"A5", "A6"}


def load_spec(path=ROOT / "spec" / "spec.yaml"):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


@dataclass
class GuardrailResult:
    passed: bool
    parsed: object = None                         # dict bei lesbarer Ausgabe, sonst None
    violations: list = field(default_factory=list)   # [{"rule": ..., "detail": ...}]
    warnings: list = field(default_factory=list)
    requires_approval: list = field(default_factory=list)   # Aktionen, die Freigabe brauchen

    def to_dict(self):
        return {"passed": self.passed, "violations": self.violations, "warnings": self.warnings,
                "requires_approval": self.requires_approval}


class Guardrails:
    def __init__(self, spec=None):
        self.spec = spec or load_spec()
        s = self.spec["agent_output_schema"]
        self.required = s["required"]
        self.props = s["properties"]
        self.catalog = self.spec["action_catalog"]
        self.roles = set(self.spec["process"]["roles"])
        self.types = set(self.props["exception_type"]["enum"])
        self.min_rationale = int(self.props["rationale"].get("minLength", 20))
        self.approval_actions = {a for a, v in self.catalog.items() if v["autonomy"] == "approval"}
        self.approval_types = {t for t, v in self.spec["exceptions"].items() if v.get("approval_required")}

    # -- Freigabepflicht (gilt auch fuer approval.py)
    def approval_needed(self, parsed, detected_type=None):
        acts = [a.get("action_id") for a in parsed.get("actions") or [] if isinstance(a, dict)]
        if parsed.get("exception_type") in self.approval_types or detected_type in self.approval_types:
            return acts                                   # E7: jede Aktion braucht Freigabe
        return [a for a in acts if a in self.approval_actions]

    def check(self, raw, case_id, detected_type=None, case_obj=None):
        v, w = [], []

        def viol(rule, detail):
            v.append({"rule": rule, "detail": detail})

        # schema_valid: lesbar und Objekt
        try:
            parsed = json.loads(raw) if isinstance(raw, str) else raw
        except (json.JSONDecodeError, TypeError) as e:
            viol("schema_valid", f"json_parse: {str(e)[:80]}")
            return GuardrailResult(False, None, v, w, [])
        if not isinstance(parsed, dict):
            viol("schema_valid", "kein JSON-Objekt")
            return GuardrailResult(False, None, v, w, [])

        for k in self.required:
            if k not in parsed:
                viol("schema_valid", f"missing:{k}")
        for k in parsed:
            if k not in self.props:
                w.append({"rule": "extra_field", "detail": k})
        if "case_id" in parsed and not isinstance(parsed["case_id"], str):
            viol("schema_valid", "type:case_id")
        if "exception_type" in parsed and parsed["exception_type"] not in self.types:
            viol("schema_valid", f"enum:exception_type={parsed['exception_type']!r}")
        acts = parsed.get("actions")
        if "actions" in parsed:
            if not isinstance(acts, list) or len(acts) < 1:
                viol("schema_valid", "actions: Liste mit mindestens 1 Eintrag erwartet")
                acts = []
            elif not all(isinstance(a, dict) and "action_id" in a for a in acts):
                viol("schema_valid", "actions: Eintrag ohne action_id")
                acts = [a for a in acts if isinstance(a, dict)]
        else:
            acts = []
        if "key_evidence" in parsed and not (isinstance(parsed["key_evidence"], list)
                                              and all(isinstance(x, str) for x in parsed["key_evidence"])):
            viol("schema_valid", "type:key_evidence")

        # action_in_catalog
        for a in acts:
            if "action_id" in a and a["action_id"] not in self.catalog:
                viol("action_in_catalog", f"{a['action_id']!r}")

        # target_role_exists
        for a in acts:
            aid, role = a.get("action_id"), a.get("target_role")
            if aid in ROLE_ACTIONS and not role:
                viol("target_role_exists", f"{aid} ohne target_role")
            elif role is not None and role not in self.roles:
                viol("target_role_exists", f"{aid}: unbekannte Rolle {role!r}")
            if role and aid not in ROLE_ACTIONS:
                w.append({"rule": "role_on_non_role_action", "detail": f"{aid}/{role}"})

        # rationale_present
        rat = parsed.get("rationale")
        if not isinstance(rat, str) or len(rat.strip()) < self.min_rationale:
            viol("rationale_present", f"Begruendung fehlt oder kuerzer als {self.min_rationale} Zeichen")

        # unknown_requires_A6
        ids = [a.get("action_id") for a in acts]
        if parsed.get("exception_type") == "unknown" and set(ids) != {"A6"}:
            viol("unknown_requires_A6", f"unknown mit {ids}")

        # case_id_match (G1)
        if parsed.get("case_id") is not None and parsed.get("case_id") != case_id:
            viol("case_id_match", f"{parsed.get('case_id')!r} statt {case_id!r}")

        # Hinweise (G2)
        if len(ids) != len(set(ids)):
            w.append({"rule": "duplicate_action", "detail": ids})
        et = parsed.get("exception_type")
        if detected_type and et not in (detected_type, "unknown", None):
            w.append({"rule": "type_mismatch", "detail": f"{et} statt {detected_type}"})

        if case_obj is not None and isinstance(parsed.get("key_evidence"), list):
            for ev in parsed["key_evidence"]:
                m = re.match(r"^(attributes|derived|detection)\.([A-Za-z_]+)", str(ev).strip())
                if m and m.group(2) not in (case_obj.get(m.group(1)) or {}):
                    w.append({"rule": "evidence_unknown_field", "detail": str(ev)})

        req = self.approval_needed({"exception_type": et, "actions": acts}, detected_type)
        return GuardrailResult(not v, parsed, v, w, req)

    # -- autonomy_respected auf Ausfuehrungsebene
    def check_execution(self, executed, approval_decisions, parsed, detected_type=None):
        """executed: Liste ausgefuehrter Aktionen (dicts). approval_decisions: Liste aus approval.py.
        Verstoss, wenn eine freigabepflichtige Aktion ohne Entscheid 'approved' ausgefuehrt wurde."""
        need = set(self.approval_needed(parsed or {}, detected_type))
        approved = {d["action_id"] for d in approval_decisions if d.get("decision") == "approved"}
        bad = [a.get("action_id") for a in executed if a.get("action_id") in need and a.get("action_id") not in approved]
        return [{"rule": "autonomy_respected", "detail": f"ohne Freigabe ausgefuehrt: {bad}"}] if bad else []


def ollama_format_schema(spec):
    """JSON-Schema fuer constrained decoding, abgeleitet aus spec.agent_output_schema.

    Annahme G3: Feldreihenfolge key_evidence, rationale vor exception_type und actions. Beim erzwungenen
    Decoding erzeugt das Modell die Felder in Schema-Reihenfolge; so stehen Belege und Begruendung vor der
    Entscheidung. Inhaltlich identisch mit spec (gleiche Felder, Pflichtfelder, Enums). Zusaetzlich:
    type string bei Enums, additionalProperties false. Kein if/then (spec guardrails, unknown -> A6).
    """
    s = spec["agent_output_schema"]["properties"]
    item = s["actions"]["items"]
    order = ["case_id", "key_evidence", "rationale", "exception_type", "actions"]
    props = {
        "case_id": {"type": "string"},
        "key_evidence": {"type": "array", "items": {"type": "string"}},
        "rationale": {"type": "string", "minLength": s["rationale"]["minLength"]},
        "exception_type": {"type": "string", "enum": list(s["exception_type"]["enum"])},
        "actions": {"type": "array", "minItems": s["actions"]["minItems"], "items": {
            "type": "object",
            "properties": {
                "action_id": {"type": "string", "enum": list(item["properties"]["action_id"]["enum"])},
                "target_role": {"type": "string", "enum": list(item["properties"]["target_role"]["enum"])}},
            "required": list(item["required"]), "additionalProperties": False}},
    }
    assert set(order) == set(s), "Schema-Felder weichen von spec ab"
    return {"type": "object", "properties": {k: props[k] for k in order},
            "required": list(spec["agent_output_schema"]["required"]), "additionalProperties": False}
