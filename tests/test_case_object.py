"""Fallobjekt: keine Ground Truth, deterministischer Hash, konsistent mit der Erkennung."""
import unittest

import _util  # noqa: F401
from case_object import CaseStore, canonical_json, find_forbidden, object_hash

LEAK_STRINGS = ["tpl_", "complaint", "payment_announced", "payment_difficulty", "boundary_", "text_indirekt",
                "text_direkt", "text_distraktor", "overshoot_knapp", "promise_passed", "allowed_action_sets",
                "generator_tag", "expected_target_role"]


class TestCaseObject(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = CaseStore()
        cls.objs = {c: cls.store.get(c) for c in cls.store.ids()}

    def test_no_ground_truth_fields(self):
        for cid, (obj, det) in self.objs.items():
            self.assertEqual(find_forbidden(obj), [], cid)
            txt = canonical_json(obj)
            for s in LEAK_STRINGS:
                self.assertNotIn(s, txt, f"{cid}: {s}")

    def test_hash_deterministic(self):
        a, _ = self.store.get("C0880")
        b, _ = CaseStore().get("C0880")
        self.assertEqual(object_hash(a), object_hash(b))
        self.assertNotEqual(object_hash(a), object_hash(self.store.get("C0317")[0]))

    def test_consistent_with_detection(self):
        for cid, (obj, det) in self.objs.items():
            d = obj["derived"]
            self.assertEqual(d["credit_headroom"] < 0, "E2" in det["hard_triggers"], cid)
            self.assertEqual(obj["detection"]["detected_type"], det["detected_type"])
            self.assertEqual(obj["free_text"] is not None, det["soft_trigger"])
            if "E6" in det["hard_triggers"]:
                self.assertGreater(d["days_overdue"], 0, cid)
            if "E3" in det["hard_triggers"]:
                self.assertLess(d["days_to_promised_delivery"], 2, cid)

    def test_history_until_snapshot(self):
        for cid, (obj, _) in self.objs.items():
            for e in obj["history"]:
                self.assertLessEqual(e["timestamp"], obj["snapshot_time"][:16], cid)
            ts = [e["timestamp"] for e in obj["history"]]
            self.assertEqual(ts, sorted(ts))


if __name__ == "__main__":
    unittest.main()
