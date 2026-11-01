"""demo.py im Replay-Modus: vorgegebene Freigabe-Antworten, eigenes Audit-Log, Auswertungs-Log unveraendert.

Die Aufzeichnung 'demo_ref' wird im Test aus den echten Evaluationseintraegen (pilot_t0, e6_t0, Run 1) gebaut.
Kein LLM noetig.
"""
import hashlib
import json
import re
import tempfile
import unittest
from pathlib import Path

import _util  # noqa: F401
import demo

EVAL_AUDIT = _util.ROOT / "out" / "audit_log.jsonl"
CASES = ["C0902", "C0537", "C0244"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class TestDemo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name)
        cls.eval_sha = sha(EVAL_AUDIT)
        cls.eval = demo.eval_index(EVAL_AUDIT)
        with open(cls.dir / "audit_log_demo.jsonl", "w", encoding="utf-8") as f:
            for c in CASES:
                f.write(json.dumps({**cls.eval[c], "label": "demo_ref"}, ensure_ascii=True) + "\n")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def tearDown(self):
        self.assertEqual(sha(EVAL_AUDIT), self.eval_sha, "out/audit_log.jsonl wurde veraendert")

    def run_demo(self, label, answers, extra=()):
        out, it = [], iter(answers)
        argv = ["--client", "replay", "--demo-dir", str(self.dir), "--no-pause", "--no-color",
                "--approver", "Tester", "--label", label, "--baseline", *extra]
        code = demo.main(argv, ask=lambda _p: next(it), write=out.append)
        entries = [e for e in demo.read_jsonl(self.dir / "audit_log_demo.jsonl") if e["label"] == label]
        return code, "\n".join(out), entries

    def test_replay_with_approval(self):
        code, text, entries = self.run_demo("t_ok", ["j", "j"])
        self.assertEqual(code, 0)
        self.assertEqual([e["case_id"] for e in entries], CASES)
        self.assertEqual({e["disposition"] for e in entries}, {"executed"})
        self.assertEqual({e["client"] for e in entries}, {"replay"})
        executed = {e["case_id"]: sorted(a["action_id"] for a in e["executed_actions"]) for e in entries}
        self.assertEqual(executed, {"C0902": ["A6"], "C0537": ["A2", "A4"], "C0244": ["A5"]})
        by = {d["by"] for e in entries for d in e["approval"]["decisions"]}
        self.assertEqual(by, {"Tester"})
        for e in entries:                                     # Replay = Evaluation, bytegleich
            self.assertEqual(e["raw_output"], self.eval[e["case_id"]]["raw_output"])
        self.assertEqual(text.count("bytegleich mit Evaluationslauf"), 3)
        self.assertEqual(text.count("gleich wie Agent"), 2)
        self.assertEqual(text.count("ANDERS als Agent"), 1)   # C0244: Baseline A3 (Mahnung), Agent A5
        self.assertIn("AUFZEICHNUNG", text)
        self.assertTrue((self.dir / "agent_actions_t_ok.jsonl").exists())

    def test_reject_and_leave_open(self):
        code, text, entries = self.run_demo("t_mix", ["n", "Limit wird erhoeht", ""])
        self.assertEqual(code, 0)
        disp = {e["case_id"]: e["disposition"] for e in entries}
        self.assertEqual(disp, {"C0902": "rejected_by_human", "C0537": "executed", "C0244": "pending_approval"})
        rej = entries[0]["approval"]["decisions"][0]
        self.assertEqual((rej["decision"], rej["comment"]), ("rejected", "Limit wird erhoeht"))
        self.assertEqual(entries[0]["executed_actions"], [])
        self.assertEqual(entries[2]["executed_actions"], [])

    def test_output_reproducible(self):
        norm = lambda s: re.sub(r"\d\d:\d\d:\d\d", "HH:MM:SS", s.replace("t_r1", "L").replace("t_r2", "L"))
        _, a, _ = self.run_demo("t_r1", ["j", "j"])
        _, b, _ = self.run_demo("t_r2", ["j", "j"])
        self.assertEqual(norm(a), norm(b))

    def test_existing_label_refused(self):
        self.run_demo("t_dup", ["j", "j"])
        with self.assertRaises(SystemExit):
            self.run_demo("t_dup", ["j", "j"])

    def test_missing_recording(self):
        code, text, entries = self.run_demo("t_none", [], extra=("--replay-label", "gibt_es_nicht"))
        self.assertEqual(code, 2)
        self.assertIn("Keine Aufzeichnung", text)
        self.assertEqual(entries, [])

    def test_truth_line_uses_metrics_judge(self):
        _, text, _ = self.run_demo("t_truth", ["j", "j"], extra=("--truth",))
        self.assertEqual(text.count("Agent korrekt"), 3)
        self.assertEqual(text.count("Regel korrekt"), 2)
        self.assertEqual(text.count("Regel FALSCH"), 1)          # C0244

    def test_formatting(self):
        self.assertEqual(demo.chf(132431), "CHF 132'431")
        self.assertEqual(demo.pct(0.324), "32,4 %")
        self.assertEqual(demo.days_phrase(1), "morgen (in 1 Tag)")
        self.assertEqual(demo.days_phrase(-4), "seit 4 Tagen verpasst")
        self.assertEqual(demo.dmy("2026-03-02"), "02.03.2026")


if __name__ == "__main__":
    unittest.main()
