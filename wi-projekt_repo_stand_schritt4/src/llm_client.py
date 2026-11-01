#!/usr/bin/env python3
"""
llm_client.py | WI-Projekt Thema 75 | v1.0 (Schritt 4, AP4)

Austauschbare LLM-Schnittstelle. Jeder Client liefert fuer (system, user, schema, context) eine LLMResponse
mit der Rohausgabe als Text. Parsen und Pruefen macht die Pipeline (guardrails.py), nicht der Client.

  OllamaClient  HTTP auf localhost (nur Standardbibliothek). JSON-Schema als 'format' (constrained decoding),
                Temperatur und Seed aus spec/CLI, Timeout, Modell-Digest aus /api/tags, Server-Version.
                Endpunkt chat (Standard) oder generate (Ausweichweg, siehe Ollama-Issue 14645).
  ReplayClient  spielt gespeicherte Rohantworten aus dem Audit-Log ab (pro Fall und Run).
  MockClient    deterministisch, ohne LLM, fuer Sandbox-Tests. Kann absichtlich fehlerhafte Ausgaben erzeugen.

Fehlerklassen:
  LLMTransportError  Verbindung, Timeout, HTTP-Fehler: keine Modellausgabe. Die Pipeline schreibt dann keine
                     Aktionszeile, der Fall wird beim Fortsetzen erneut versucht.

Pruefung der lokalen Installation (Jan, vor dem Rauchtest):
  python src/llm_client.py check --model qwen3.5:9b --think off
  -> Server-Version, Digest, Fallentest: wird das Schema auch gegen eine Prosa-Aufforderung erzwungen?
"""

import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from keyword_labeler import classify  # noqa: E402  (nur MockClient)

DEFAULT_URL = "http://localhost:11434"


class LLMTransportError(Exception):
    pass


@dataclass
class LLMResponse:
    raw: str                        # Rohausgabe (content), unveraendert
    model: str = ""
    model_digest: str = ""
    thinking: str = ""              # nur bei Denkmodellen mit think=on
    meta: dict = field(default_factory=dict)


# ---------------------------------------------------------------- Ollama

class OllamaClient:
    name = "ollama"

    def __init__(self, model, temperature=0.0, seed=42, base_url=DEFAULT_URL, timeout=300,
                 endpoint="chat", think=None, num_ctx=8192, num_predict=1024, keep_alive="30m"):
        if not model:
            raise ValueError("OllamaClient braucht --model (spec meta.llm.model ist noch TBD)")
        self.model = model
        self.temperature = float(temperature)
        self.seed = int(seed)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.endpoint = endpoint
        self.think = think              # None = Feld nicht senden, sonst True/False
        self.num_ctx = num_ctx
        self.num_predict = num_predict
        self.keep_alive = keep_alive
        self._digest = None
        self._version = None

    # -- HTTP
    def _request(self, path, payload=None, timeout=None):
        url = self.base_url + path
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="GET" if data is None else "POST",
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout or self.timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:500]
            raise LLMTransportError(f"HTTP {e.code} {path}: {body}") from e
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            raise LLMTransportError(f"{type(e).__name__} {path}: {e}") from e

    def server_version(self):
        if self._version is None:
            try:
                self._version = self._request("/api/version", timeout=10).get("version", "")
            except LLMTransportError:
                self._version = ""
        return self._version

    def model_digest(self):
        if self._digest is None:
            self._digest = ""
            try:
                tags = self._request("/api/tags", timeout=10)
                for m in tags.get("models", []):
                    if m.get("name") == self.model or m.get("model") == self.model:
                        self._digest = m.get("digest", "")
                        break
            except LLMTransportError:
                pass
        return self._digest

    def build_payload(self, system, user, schema, seed=None):
        options = {"temperature": self.temperature, "seed": self.seed if seed is None else int(seed),
                   "num_ctx": self.num_ctx, "num_predict": self.num_predict}
        if self.endpoint == "chat":
            p = {"model": self.model, "stream": False, "format": schema, "options": options,
                 "keep_alive": self.keep_alive,
                 "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        else:
            p = {"model": self.model, "stream": False, "format": schema, "options": options,
                 "keep_alive": self.keep_alive, "system": system, "prompt": user}
        if self.think is not None:
            p["think"] = bool(self.think)
        return p

    def complete(self, system, user, schema, context=None):
        context = context or {}
        payload = self.build_payload(system, user, schema, seed=context.get("seed"))
        t0 = time.monotonic()
        r = self._request("/api/chat" if self.endpoint == "chat" else "/api/generate", payload)
        if self.endpoint == "chat":
            msg = r.get("message") or {}
            raw, thinking = msg.get("content", ""), msg.get("thinking", "") or ""
        else:
            raw, thinking = r.get("response", ""), r.get("thinking", "") or ""
        meta = {k: r.get(k) for k in ("done_reason", "total_duration", "load_duration", "prompt_eval_count",
                                      "prompt_eval_duration", "eval_count", "eval_duration")}
        meta.update({"endpoint": self.endpoint, "server_version": self.server_version(),
                     "wall_ms": int(1000 * (time.monotonic() - t0)), "options": payload["options"],
                     "think": payload.get("think")})
        return LLMResponse(raw=raw, model=r.get("model", self.model), model_digest=self.model_digest(),
                           thinking=thinking, meta=meta)


# ---------------------------------------------------------------- Replay

class ReplayClient:
    """Spielt Rohausgaben aus dem Audit-Log ab. Schluessel: (case_id, run) des Quell-Labels."""
    name = "replay"

    def __init__(self, audit_path, source_label):
        self.source_label = source_label
        self.entries = {}
        with open(audit_path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                e = json.loads(line)
                if e.get("label") != source_label or e.get("raw_output") is None:
                    continue
                self.entries[(e["case_id"], e["run"])] = e      # letzter Eintrag gewinnt
        if not self.entries:
            raise ValueError(f"Keine Rohausgaben mit Label '{source_label}' in {audit_path}")
        any_e = next(iter(self.entries.values()))
        self.model = any_e.get("model", "")

    def complete(self, system, user, schema, context=None):
        context = context or {}
        key = (context.get("case_id"), context.get("run"))
        e = self.entries.get(key)
        if e is None:
            raise LLMTransportError(f"Replay: keine Rohausgabe fuer {key}")
        mismatch = [k for k in ("prompt_hash", "case_object_hash", "schema_hash")
                    if context.get(k) and e.get(k) and context[k] != e[k]]
        return LLMResponse(raw=e["raw_output"], model=e.get("model", ""), model_digest=e.get("model_digest", ""),
                           thinking=e.get("thinking", ""),
                           meta={"replay_of": e.get("run_id"), "replay_mismatch": mismatch})


# ---------------------------------------------------------------- Mock

MOCK_FAULTS = ["invalid_json", "action_not_in_catalog", "missing_target_role", "unknown_without_A6",
               "short_rationale", "schema_missing_field", "wrong_case_id"]
MOCK_E6 = {"complaint": [{"action_id": "A5", "target_role": "Kundendienst"}],
           "payment_announced": [{"action_id": "A0"}],
           "payment_difficulty": [{"action_id": "A6", "target_role": "Credit Management"}]}


def _h(*parts):
    return int(hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest(), 16)


class MockClient:
    """Deterministischer Platzhalter ohne LLM. Keine Ground Truth: entscheidet nur aus dem Fallobjekt.

    Verhalten (bewusst einfach, nur fuer Pipeline-Tests):
      E2 -> A6 Credit Management; E3 -> A4+A2 (bei einem Teil der Faelle in Run 2 nur A2, damit die
      Reproduzierbarkeit < 100 % sichtbar wird); E5 -> A6 Buchhaltung + A7; E7 -> A6 Credit Management;
      E6 -> Keyword-Klassifikator, ohne Treffer Enthaltung (unknown + A6 Buchhaltung); none -> A0.
    faults="mixed": etwa jede vierte Ausgabe enthaelt einen der Fehler aus MOCK_FAULTS (hash-basiert).
    """
    name = "mock"

    def __init__(self, faults="none", model="mock-1.0"):
        if faults not in ("none", "mixed"):
            raise ValueError("faults: none | mixed")
        self.faults = faults
        self.model = model

    @staticmethod
    def _case_from_user(user):
        start = user.index("{")
        end = user.rindex("}") + 1
        return json.loads(user[start:end])

    def decide(self, case, run):
        cid = case["case_id"]
        t = case["detection"]["detected_type"]
        if t == "E2":
            return "E2", [{"action_id": "A6", "target_role": "Credit Management"}], \
                "Kreditlimit ueberschritten (credit_headroom negativ), Eskalation an Credit Management.", \
                ["derived.credit_headroom", "attributes.credit_limit"]
        if t == "E3":
            acts = [{"action_id": "A4"}, {"action_id": "A2"}]
            if run == 2 and _h(cid, "e3") % 2 == 0:
                acts = [{"action_id": "A2"}]
            return "E3", acts, "Liefertermin knapp oder verpasst und nicht versendet, priorisieren und Kunde informieren.", \
                ["derived.days_to_promised_delivery", "history: Versenden fehlt"]
        if t == "E5":
            return "E5", [{"action_id": "A6", "target_role": "Buchhaltung"}, {"action_id": "A7"}], \
                "Rechnung vor Versand gestellt, Eskalation an Buchhaltung und Fall sperren.", ["history"]
        if t == "E7":
            return "E7", [{"action_id": "A6", "target_role": "Credit Management"}], \
                "Kreditueberschreitung und Lieferverzoegerung zugleich, Uebergabe an Mensch.", \
                ["derived.overshoot_ratio", "derived.days_to_promised_delivery"]
        if t == "E6":
            cat, _ = classify(case.get("free_text") or "")
            if cat in MOCK_E6:
                return "E6", MOCK_E6[cat], f"Rechnung ueberfaellig, Freitext als {cat} eingeordnet.", \
                    ["derived.days_overdue", "free_text"]
            return "unknown", [{"action_id": "A6", "target_role": "Buchhaltung"}], \
                "Freitext laesst sich nicht sicher einordnen, Uebergabe an einen Menschen.", ["free_text"]
        return "none", [{"action_id": "A0"}], "Nur Freitext ohne harten Trigger, keine Massnahme.", ["free_text"]

    def complete(self, system, user, schema, context=None):
        context = context or {}
        case = self._case_from_user(user)
        run = int(context.get("run", 1))
        etype, acts, why, ev = self.decide(case, run)
        out = {"case_id": case["case_id"], "key_evidence": ev, "rationale": why,
               "exception_type": etype, "actions": acts}
        fault = None
        if self.faults == "mixed":
            h = _h(case["case_id"], run, "fault1")   # Salt so gewaehlt, dass im Pilot alle Fehlerarten vorkommen
            if h % 4 == 0:
                fault = MOCK_FAULTS[(h // 4) % len(MOCK_FAULTS)]
        if fault == "invalid_json":
            raw = "Hier ist meine Antwort: " + json.dumps(out, ensure_ascii=True)[:-5]
        else:
            if fault == "action_not_in_catalog":
                out["actions"] = [{"action_id": "A9"}]
            elif fault == "missing_target_role":
                out["actions"] = [{"action_id": "A6"}]
            elif fault == "unknown_without_A6":
                out["exception_type"], out["actions"] = "unknown", [{"action_id": "A0"}]
            elif fault == "short_rationale":
                out["rationale"] = "ok"
            elif fault == "schema_missing_field":
                out.pop("key_evidence")
            elif fault == "wrong_case_id":
                out["case_id"] = "C9999"
            raw = json.dumps(out, ensure_ascii=True)
        return LLMResponse(raw=raw, model=self.model, model_digest="mock",
                           meta={"mock_fault": fault, "wall_ms": 0})


# ---------------------------------------------------------------- Pruefung der Installation

PROBE_SCHEMA = {"type": "object", "properties": {"wort": {"type": "string"}, "anzahl": {"type": "integer"}},
                "required": ["wort", "anzahl"], "additionalProperties": False}


def check(args):
    think = {"on": True, "off": False, "unset": None}[args.think]
    c = OllamaClient(args.model, base_url=args.url, endpoint=args.endpoint, think=think, timeout=args.timeout)
    print("Server-Version:", c.server_version() or "nicht erreichbar")
    print("Modell-Digest :", c.model_digest() or "nicht gefunden (ollama pull?)")
    # Fallentest: Prosa-Aufforderung, aber Schema mit anderen Feldern. Nur erzwungenes Decoding liefert JSON.
    r = c.complete("Antworte immer ausfuehrlich in Prosa mit Markdown-Ueberschriften, niemals als JSON.",
                   "Beschreibe die Farbe Blau fuer ein Kind.", PROBE_SCHEMA)
    ok = False
    try:
        obj = json.loads(r.raw)
        ok = isinstance(obj, dict) and set(obj) == {"wort", "anzahl"} and isinstance(obj["anzahl"], int)
    except json.JSONDecodeError:
        pass
    print("Rohausgabe    :", r.raw[:200].replace("\n", " "))
    print("Denktext      :", "ja" if r.thinking else "nein")
    print("Dauer         :", r.meta.get("wall_ms"), "ms")
    print("ERGEBNIS      :", "OK, Schema wird erzwungen" if ok else
          "FEHLER, Schema nicht erzwungen. Mit --endpoint generate oder --think unset erneut pruefen.")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("check")
    p.add_argument("--model", required=True)
    p.add_argument("--url", default=DEFAULT_URL)
    p.add_argument("--endpoint", choices=["chat", "generate"], default="chat")
    p.add_argument("--think", choices=["on", "off", "unset"], default="off")
    p.add_argument("--timeout", type=int, default=300)
    a = ap.parse_args()
    sys.exit(check(a))


if __name__ == "__main__":
    main()
