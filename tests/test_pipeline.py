"""Pipeline mit MockClient: Guardrail-Treffer, Freigabe, Replay, Fortsetzen, Auswertung mit metrics.py."""
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import _util  # noqa: F401
import metrics
from run_agent import parse_args, run

APPROVAL_ACTIONS = {"A5", "A6", "A7"}


def quiet(*a, **k):
    pass


class TestPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name)
        cls.args = ["--out-dir", str(cls.out)]
        cls.stats = run(parse_args(["--cases", "pilot", "--k", "3", "--client", "mock", "--mock-faults", "mixed",
                                    "--label", "mock"] + cls.args), show=quiet)
        cls.audit = [json.loads(x) for x in (cls.out / "audit_log.jsonl").read_text().splitlines()]

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_counts(self):
        self.assertEqual(self.stats["completed_pairs"], 51)        # 17 geroutete Pilotfaelle x 3
        lines = (self.out / "agent_actions_mock.jsonl").read_text().splitlines()
        self.assertEqual(len(lines), 51)

    def test_mock_run_triggers_every_output_guardrail(self):
        hit = {v["rule"] for e in self.audit for v in e["guardrail"]["violations"]}
        self.assertEqual(hit, {"schema_valid", "action_in_catalog", "target_role_exists", "rationale_present",
                               "unknown_requires_A6", "case_id_match"})

    def test_batch_never_executes_approval_actions(self):
        for e in self.audit:
            ids = {a["action_id"] for a in e["executed_actions"]}
            self.assertFalse(ids & APPROVAL_ACTIONS, e["case_id"])
            if not e["guardrail"]["passed"]:
                self.assertEqual(e["executed_actions"], [])
                self.assertEqual(e["disposition"], "blocked_to_human")

    def test_audit_fields(self):
        need = {"ts", "run_id", "case_id", "run", "client", "model", "model_digest", "temperature", "seed",
                "prompt_version", "prompt_hash", "case_object_hash", "raw_output", "parsed_output", "guardrail",
                "approval", "executed_actions", "duration_ms", "disposition"}
        for e in self.audit:
            self.assertTrue(need <= set(e), need - set(e))

    def test_replay_reproduces_mock(self):
        run(parse_args(["--cases", "pilot", "--k", "3", "--client", "replay", "--replay-label", "mock",
                        "--label", "replay"] + self.args), show=quiet)
        a = (self.out / "agent_actions_mock.jsonl").read_text()
        b = (self.out / "agent_actions_replay.jsonl").read_text()
        self.assertEqual(a, b)

    def test_resume_skips_done_and_config_guard(self):
        s = run(parse_args(["--cases", "pilot", "--k", "3", "--client", "mock", "--mock-faults", "mixed",
                            "--label", "mock"] + self.args), show=quiet)
        self.assertEqual(s["calls"], 0)
        with self.assertRaises(SystemExit):
            run(parse_args(["--cases", "pilot", "--k", "3", "--client", "mock", "--label", "mock"] + self.args),
                show=quiet)

    def test_interactive_approval(self):
        answers = iter(["j"] * 200)
        run(parse_args(["--cases", "C0317,C0880", "--k", "1", "--client", "mock", "--approval", "interactive",
                        "--label", "inter"] + self.args), ask=lambda _: next(answers), show=quiet)
        entries = [json.loads(x) for x in (self.out / "audit_log.jsonl").read_text().splitlines()]
        entries = [e for e in entries if e["label"] == "inter"]
        self.assertEqual({e["disposition"] for e in entries}, {"executed"})
        self.assertEqual({a["action_id"] for e in entries for a in e["executed_actions"]}, {"A5", "A6"})

    def test_concept_types_skipped(self):
        s = run(parse_args(["--cases", "routed", "--k", "1", "--client", "mock", "--label", "routed"] + self.args),
                show=quiet)
        self.assertEqual(s["expected_pairs"], 370 - 40 - 60)       # ohne E5 und E7

    def test_metrics_reads_mock_output(self):
        with redirect_stdout(io.StringIO()):
            scopes = metrics.evaluate_file(self.out / "agent_actions_mock.jsonl", "mock",
                                           scopes_sel=("pilot", "covered"))
        pilot = scopes["Pilot (20)"]["actions"]
        self.assertEqual(pilot["runs"], [1, 2, 3])
        self.assertEqual(pilot["per_run"][0]["aggregate"]["bewertet gesamt"]["n"], 17)
        self.assertIsNotNone(pilot["reproducibility"])
        self.assertIn("json_parse", pilot["schema_errors"])

    def test_metrics_strict_guardrails(self):
        with redirect_stdout(io.StringIO()):
            raw = metrics.evaluate_file(self.out / "agent_actions_mock.jsonl", "m", scopes_sel=("pilot",))
            strict = metrics.evaluate_file(self.out / "agent_actions_mock.jsonl", "m", scopes_sel=("pilot",),
                                           strict_guardrails=True)
        ok = lambda s: sum(p["aggregate"]["bewertet gesamt"]["ok"] for p in s["Pilot (20)"]["actions"]["per_run"])
        self.assertLess(ok(strict), ok(raw))                     # blockierte, aber korrekte Ausgaben fallen weg


if __name__ == "__main__":
    unittest.main()
