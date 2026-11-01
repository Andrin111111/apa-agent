"""Prompt: Ermessensrichtlinie woertlich, Katalog wie spec, Variante b ohne Zuordnung, Hash stabil."""
import unittest

import _util  # noqa: F401
from guardrails import load_spec
from run_agent import load_prompt


class TestPrompt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = load_spec()
        cls.a, cls.version, cls.hash_a = load_prompt("a")
        cls.b, _, cls.hash_b = load_prompt("b")

    def test_policy_verbatim(self):
        for i, line in enumerate(self.spec["judgement_policy"], 1):
            self.assertIn(f"{i}. {line}", self.a)
            self.assertIn(f"{i}. {line}", self.b)

    def test_catalog_and_roles(self):
        for aid, v in self.spec["action_catalog"].items():
            self.assertIn(f"- {aid} {v['name']} (", self.a)
        for role in self.spec["process"]["roles"]:
            self.assertIn(role, self.a)

    def test_variant_b_without_mapping(self):
        self.assertIn("Zuordnung Ausnahmetyp zu Aktionen", self.a)
        self.assertNotIn("Zuordnung Ausnahmetyp zu Aktionen", self.b)
        self.assertNotEqual(self.hash_a, self.hash_b)

    def test_no_comments_sent_and_ascii(self):
        self.assertNotIn("<!--", self.a)
        self.assertTrue(self.a.isascii())
        self.assertNotEqual(self.version, "?")

    def test_hash_stable(self):
        self.assertEqual(load_prompt("a")[2], self.hash_a)


if __name__ == "__main__":
    unittest.main()
