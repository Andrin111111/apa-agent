"""OllamaClient gegen einen lokalen Fake-Server (Standardbibliothek): Payload, Antwort, Digest, Fehler."""
import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import _util  # noqa: F401
from guardrails import load_spec, ollama_format_schema
from llm_client import LLMTransportError, OllamaClient
from run_agent import parse_args, run

REQUESTS = []


class Fake(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, obj):
        b = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path == "/api/version":
            self._send({"version": "0.40.13"})
        elif self.path == "/api/tags":
            self._send({"models": [{"name": "fake:1b", "model": "fake:1b", "digest": "abc123"}]})

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        REQUESTS.append((self.path, body))
        user = body["messages"][1]["content"] if self.path == "/api/chat" else body["prompt"]
        case = json.loads(user[user.index("{"):user.rindex("}") + 1])
        out = json.dumps({"case_id": case["case_id"], "key_evidence": ["derived.credit_headroom"],
                          "rationale": "Kreditlimit ueberschritten, Eskalation an Credit Management.",
                          "exception_type": case["detection"]["detected_type"],
                          "actions": [{"action_id": "A6", "target_role": "Credit Management"}]})
        if self.path == "/api/chat":
            self._send({"model": "fake:1b", "message": {"role": "assistant", "content": out},
                        "done_reason": "stop", "eval_count": 42})
        else:
            self._send({"model": "fake:1b", "response": out, "done_reason": "stop"})


class TestOllamaClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = HTTPServer(("127.0.0.1", 0), Fake)
        cls.url = f"http://127.0.0.1:{cls.srv.server_port}"
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.schema = ollama_format_schema(load_spec())

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def test_payload_and_response(self):
        REQUESTS.clear()
        c = OllamaClient("fake:1b", temperature=0, seed=42, base_url=self.url, think=False)
        r = c.complete("SYS", 'Fallobjekt:\n{"case_id": "C0317", "detection": {"detected_type": "E2"}}',
                       self.schema, {"seed": 43})
        path, body = REQUESTS[-1]
        self.assertEqual(path, "/api/chat")
        self.assertEqual(body["format"], self.schema)
        self.assertEqual(body["options"]["temperature"], 0.0)
        self.assertEqual(body["options"]["seed"], 43)
        self.assertIs(body["think"], False)
        self.assertFalse(body["stream"])
        self.assertEqual(body["messages"][0], {"role": "system", "content": "SYS"})
        self.assertEqual(json.loads(r.raw)["case_id"], "C0317")
        self.assertEqual(r.model_digest, "abc123")
        self.assertEqual(r.meta["server_version"], "0.40.13")

    def test_generate_endpoint_and_think_unset(self):
        REQUESTS.clear()
        c = OllamaClient("fake:1b", base_url=self.url, endpoint="generate", think=None)
        c.complete("SYS", '{"case_id": "C0317", "detection": {"detected_type": "E2"}}', self.schema)
        path, body = REQUESTS[-1]
        self.assertEqual(path, "/api/generate")
        self.assertNotIn("think", body)
        self.assertEqual(body["system"], "SYS")

    def test_transport_error(self):
        c = OllamaClient("fake:1b", base_url="http://127.0.0.1:9", timeout=2)
        with self.assertRaises(LLMTransportError):
            c.complete("S", "{}", self.schema)

    def test_pipeline_with_fake_server(self):
        with tempfile.TemporaryDirectory() as d:
            s = run(parse_args(["--cases", "C0317,C0556", "--k", "2", "--client", "ollama", "--model", "fake:1b",
                                "--url", self.url, "--label", "fake", "--out-dir", d]), show=lambda *a, **k: None)
            self.assertEqual(s["completed_pairs"], 4)
            e = json.loads((Path(d) / "audit_log.jsonl").read_text().splitlines()[0])
            self.assertEqual(e["model_digest"], "abc123")
            self.assertTrue(e["guardrail"]["passed"])
            self.assertEqual(e["disposition"], "pending_approval")

    def test_transport_error_writes_no_action_line(self):
        with tempfile.TemporaryDirectory() as d:
            s = run(parse_args(["--cases", "C0317", "--client", "ollama", "--model", "fake:1b", "--timeout", "2",
                                "--url", "http://127.0.0.1:9", "--label", "down", "--out-dir", d]),
                    show=lambda *a, **k: None)
            self.assertEqual(s["transport_errors"], 1)
            self.assertEqual(s["completed_pairs"], 0)


if __name__ == "__main__":
    unittest.main()
