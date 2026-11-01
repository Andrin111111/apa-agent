"""Jeder Guardrail wird mindestens einmal ausgeloest, gueltige Ausgaben passieren."""
import json
import unittest

import _util  # noqa: F401
from guardrails import BLOCKING, Guardrails, load_spec, ollama_format_schema

VALID = {"case_id": "C0317", "key_evidence": ["derived.credit_headroom"],
         "rationale": "Kreditlimit ueberschritten, daher Eskalation an Credit Management.",
         "exception_type": "E2", "actions": [{"action_id": "A6", "target_role": "Credit Management"}]}


def mod(**kw):
    d = json.loads(json.dumps(VALID))
    d.update(kw)
    return d


class TestGuardrails(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = Guardrails()

    def rules(self, out, case_id="C0317", det="E2"):
        r = self.g.check(json.dumps(out) if isinstance(out, dict) else out, case_id, det)
        return r, {v["rule"] for v in r.violations}

    def test_valid_passes(self):
        r, rules = self.rules(VALID)
        self.assertTrue(r.passed, r.violations)
        self.assertEqual(r.requires_approval, ["A6"])

    def test_schema_valid(self):
        self.assertIn("schema_valid", self.rules("kein json")[1])
        self.assertIn("schema_valid", self.rules("[1, 2]")[1])
        bad = mod()
        bad.pop("key_evidence")
        self.assertIn("schema_valid", self.rules(bad)[1])
        self.assertIn("schema_valid", self.rules(mod(exception_type="E9"))[1])
        self.assertIn("schema_valid", self.rules(mod(actions=[]))[1])

    def test_action_in_catalog(self):
        self.assertEqual({"action_in_catalog"}, self.rules(mod(actions=[{"action_id": "A9"}]))[1])

    def test_target_role_exists(self):
        self.assertEqual({"target_role_exists"}, self.rules(mod(actions=[{"action_id": "A6"}]))[1])
        self.assertEqual({"target_role_exists"},
                         self.rules(mod(actions=[{"action_id": "A5", "target_role": "Einkauf"}]))[1])

    def test_rationale_present(self):
        self.assertEqual({"rationale_present"}, self.rules(mod(rationale="zu kurz"))[1])
        self.assertEqual({"rationale_present"}, self.rules(mod(rationale="   " * 20))[1])

    def test_unknown_requires_A6(self):
        r = self.rules(mod(exception_type="unknown", actions=[{"action_id": "A0"}]))[1]
        self.assertEqual({"unknown_requires_A6"}, r)
        r = self.rules(mod(exception_type="unknown", actions=[{"action_id": "A6", "target_role": "Buchhaltung"},
                                                               {"action_id": "A2"}]))[1]
        self.assertEqual({"unknown_requires_A6"}, r)
        ok, _ = self.rules(mod(exception_type="unknown"))
        self.assertTrue(ok.passed)

    def test_case_id_match(self):
        self.assertEqual({"case_id_match"}, self.rules(mod(case_id="C9999"))[1])

    def test_autonomy_respected(self):
        executed = [{"action_id": "A6", "target_role": "Credit Management"}]
        v = self.g.check_execution(executed, [{"action_id": "A6", "decision": "pending"}], VALID, "E2")
        self.assertEqual([x["rule"] for x in v], ["autonomy_respected"])
        v = self.g.check_execution(executed, [{"action_id": "A6", "decision": "approved"}], VALID, "E2")
        self.assertEqual(v, [])

    def test_all_blocking_rules_covered(self):
        tested = {"schema_valid", "action_in_catalog", "target_role_exists", "rationale_present",
                  "unknown_requires_A6", "case_id_match", "autonomy_respected"}
        self.assertEqual(set(BLOCKING), tested)
        self.assertTrue(set(load_spec()["guardrails"]) <= set(BLOCKING))

    def test_warnings_not_blocking(self):
        r, rules = self.rules(mod(exception_type="E6"), det="E2")
        self.assertTrue(r.passed)
        self.assertIn("type_mismatch", {w["rule"] for w in r.warnings})

    def test_evidence_unknown_field_warning(self):
        obj = {"derived": {"credit_headroom": -5}, "attributes": {}, "detection": {}}
        r = self.g.check(json.dumps(mod(key_evidence=["derived.credit_headroom", "derived.erfunden"])),
                         "C0317", "E2", obj)
        self.assertTrue(r.passed)
        self.assertEqual([w["detail"] for w in r.warnings if w["rule"] == "evidence_unknown_field"],
                         ["derived.erfunden"])

    def test_e7_requires_approval_for_all(self):
        out = mod(exception_type="E7", actions=[{"action_id": "A2"}, {"action_id": "A4"}])
        r, _ = self.rules(out, det="E7")
        self.assertEqual(sorted(r.requires_approval), ["A2", "A4"])

    def test_format_schema_matches_spec(self):
        spec = load_spec()
        s = ollama_format_schema(spec)
        self.assertEqual(set(s["properties"]), set(spec["agent_output_schema"]["properties"]))
        self.assertEqual(s["required"], spec["agent_output_schema"]["required"])
        self.assertNotIn("if", json.dumps(s))
        self.assertEqual(list(s["properties"])[-1], "actions")


if __name__ == "__main__":
    unittest.main()
