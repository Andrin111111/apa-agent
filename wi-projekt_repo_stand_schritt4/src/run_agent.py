#!/usr/bin/env python3
"""
run_agent.py | WI-Projekt Thema 75 | v1.0 (Schritt 4, AP4/AP5)

Pipeline: Fallobjekt -> LLM -> Guardrails -> Freigabe -> Aktion (simuliert) -> Audit-Log.

Ausgaben (pro Label):
  out/agent_actions_<label>.jsonl  eine Zeile pro (Fall, Run) im Format agent_output_schema plus 'run'.
                                   Enthaelt die geparste Rohausgabe des Agenten (auch wenn ein Guardrail
                                   blockiert hat), damit metrics.py die Entscheidung bewertet. Unlesbare
                                   Ausgabe: {"case_id", "run", "_parse_error": true}. Zusatzfelder mit '_'.
  out/agent_run_<label>.json       Konfiguration und Zusammenfassung des Laufs (fuer Fortsetzen und Bericht)
  out/audit_log.jsonl              ein Eintrag pro Aufruf, wird angehaengt (alle Labels)

Fortsetzbar: fertige (Fall, Run)-Paare werden uebersprungen. Abbrechbar mit Ctrl+C (fertige Zeilen bleiben).
Transportfehler (Ollama nicht erreichbar, Timeout) schreiben keine Aktionszeile: erneut starten setzt fort.
Ein Label gehoert zu genau einer Konfiguration (Modell, Temperatur, Prompt, ...). Abweichung -> Abbruch.

Guardrail-Verstoss (Annahme, Entscheid Jan an K4): kein automatischer Neuversuch. Ausgabe blockiert, Fall geht
an einen Menschen (Disposition blocked_to_human), nichts wird ausgefuehrt.

Beispiele (aus dem Repo-Root):
  python src/run_agent.py --cases pilot --k 3 --client mock --mock-faults mixed --label mock
  python src/run_agent.py --cases pilot --k 3 --client replay --replay-label mock --label mock_replay
  python src/run_agent.py --cases C0317,C0067,C0880 --k 2 --client ollama --model qwen3.5:9b --think off --label smoke
  python src/run_agent.py --cases pilot --k 3 --client ollama --model qwen3.5:9b --think off --label pilot_t0
  python src/run_agent.py --cases e6_full --k 1 --client ollama --model qwen3.5:9b --think off --label e6_t0
  python src/run_agent.py --cases pilot --k 3 --client ollama --model qwen3.5:9b --think off \\
         --temperature 0.7 --seed-mode per_run --label pilot_t07
"""

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import approval as approval_mod  # noqa: E402
from case_object import CaseStore, object_hash, render_json, sha256  # noqa: E402
from guardrails import Guardrails, load_spec, ollama_format_schema  # noqa: E402
from llm_client import LLMTransportError, MockClient, OllamaClient, ReplayClient  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = ROOT / "prompts" / "agent_prompt.md"
CONCEPT_TYPES = {"E5", "E7"}
CONFIG_KEYS = ["client", "model", "temperature", "seed", "seed_mode", "prompt_variant", "prompt_version",
               "prompt_hash", "schema_hash", "think", "endpoint", "mock_faults", "replay_label"]


# ---------------------------------------------------------------- Prompt

def load_prompt(variant="a", path=PROMPT_PATH):
    """Rueckgabe (Text wie gesendet, Version, sha256). Variante b entfernt den Zuordnungsblock."""
    src = Path(path).read_text(encoding="utf-8")
    m = re.search(r"version:\s*([0-9][0-9.]*)", src)
    version = m.group(1) if m else "?"
    if variant == "b":
        src = re.sub(r"<!-- MAPPING:BEGIN -->.*?<!-- MAPPING:END -->\n?", "", src, flags=re.S)
    elif variant != "a":
        raise ValueError("prompt_variant: a | b")
    lines = [ln for ln in src.splitlines() if not re.fullmatch(r"\s*<!--.*-->\s*", ln)]
    text = "\n".join(lines).strip() + "\n"
    return text, version, sha256(text)


def user_message(case_obj):
    return ("Fallobjekt:\n" + render_json(case_obj) +
            "\n\nBewerte den Fall und antworte mit genau einem JSON-Objekt gemaess Ausgabeformat.")


# ---------------------------------------------------------------- Fallauswahl

def select_cases(selection, store, include_concept=False, pilot_path=ROOT / "data" / "pilot_sample.csv"):
    """Rueckgabe (ausgewaehlte IDs, uebersprungene IDs mit Grund)."""
    det = {cid: store.get(cid)[1] for cid in store.ids()}
    routed = [c for c in store.ids() if det[c]["routed_to_agent"]]
    if selection == "pilot":
        ids = pd.read_csv(pilot_path).case_id.tolist()
    elif selection == "e6_full":
        ids = [c for c in store.ids() if det[c]["detected_type"] == "E6"]
    elif selection == "routed":
        ids = routed
    else:
        ids = [c.strip() for c in selection.split(",") if c.strip()]
    chosen, skipped = [], []
    for c in ids:
        if c not in det:
            skipped.append((c, "unbekannte case_id"))
        elif not det[c]["routed_to_agent"]:
            skipped.append((c, "nicht geroutet (kein Trigger)"))
        elif det[c]["detected_type"] in CONCEPT_TYPES and not include_concept:
            skipped.append((c, f"{det[c]['detected_type']} ist Konzept (--include-concept)"))
        else:
            chosen.append(c)
    return chosen, skipped


# ---------------------------------------------------------------- Hilfen

def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_done(actions_path):
    done = set()
    if actions_path.exists():
        for line in actions_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                done.add((r["case_id"], int(r.get("run", 1))))
    return done


def action_record(case_id, run, gr):
    if gr.parsed is None:
        return {"case_id": case_id, "run": run, "_parse_error": True,
                "_violations": [x["rule"] for x in gr.violations]}
    rec = {k: v for k, v in gr.parsed.items() if k not in ("case_id", "run")}
    rec = {"case_id": case_id, **rec, "run": run, "_guardrail_ok": gr.passed,
           "_violations": sorted({x["rule"] for x in gr.violations})}
    if gr.parsed.get("case_id") != case_id:
        rec["_output_case_id"] = gr.parsed.get("case_id")
    return rec


def make_client(a, spec, audit_path):
    temp = spec["meta"]["llm"]["temperature"] if a.temperature is None else a.temperature
    if a.client == "ollama":
        think = {"on": True, "off": False, "unset": None}[a.think]
        return OllamaClient(a.model, temperature=temp, seed=a.seed, base_url=a.url, timeout=a.timeout,
                            endpoint=a.endpoint, think=think, num_ctx=a.num_ctx), temp
    if a.client == "mock":
        return MockClient(faults=a.mock_faults), temp
    if a.client == "replay":
        if not a.replay_label:
            raise SystemExit("--client replay braucht --replay-label")
        return ReplayClient(audit_path, a.replay_label), temp
    raise SystemExit(f"unbekannter Client {a.client}")


# ---------------------------------------------------------------- Lauf

def run(a, ask=input, show=print):
    spec = load_spec()
    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    audit_path = Path(a.audit_log) if a.audit_log else out_dir / "audit_log.jsonl"
    actions_path = out_dir / f"agent_actions_{a.label}.jsonl"
    config_path = out_dir / f"agent_run_{a.label}.json"

    if a.seed is None:
        a.seed = int(spec["meta"]["llm"]["seed"])
    client, temperature = make_client(a, spec, audit_path)
    system, p_version, p_hash = load_prompt(a.prompt_variant)
    schema = ollama_format_schema(spec)
    schema_hash = sha256(json.dumps(schema, sort_keys=True))
    guard = Guardrails(spec)
    store = CaseStore()
    ids, skipped = select_cases(a.cases, store, a.include_concept)

    config = {"label": a.label, "client": client.name, "model": getattr(client, "model", ""),
              "temperature": temperature, "seed": a.seed, "seed_mode": a.seed_mode,
              "prompt_variant": a.prompt_variant, "prompt_version": p_version, "prompt_hash": p_hash,
              "schema_hash": schema_hash, "think": a.think if a.client == "ollama" else None,
              "endpoint": a.endpoint if a.client == "ollama" else None,
              "mock_faults": a.mock_faults if a.client == "mock" else None,
              "replay_label": a.replay_label if a.client == "replay" else None}
    if config_path.exists():
        old = json.loads(config_path.read_text(encoding="utf-8"))
        diff = [k for k in CONFIG_KEYS if old.get("config", {}).get(k) != config.get(k)]
        if diff and actions_path.exists():
            raise SystemExit(f"Label '{a.label}' existiert mit anderer Konfiguration ({diff}). Neues Label waehlen.")

    done = read_done(actions_path)
    todo = [(r, c) for r in range(1, a.k + 1) for c in ids if (c, r) not in done]   # Run-weise Reihenfolge
    run_id = f"{a.label}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    show(f"Lauf {run_id}: {len(ids)} Faelle x k={a.k}, offen {len(todo)}, bereits fertig {len(done)}, "
         f"uebersprungen {len(skipped)}")
    for c, why in skipped:
        show(f"  uebersprungen {c}: {why}")
    show(f"Client {client.name}, Modell {config['model']}, Temperatur {temperature}, Seed {a.seed} ({a.seed_mode}), "
         f"Prompt v{p_version} Variante {a.prompt_variant} {p_hash[:12]}")

    stats = {"calls": 0, "transport_errors": 0, "parse_errors": 0, "guardrail_blocked": 0,
             "violations": {}, "warnings": {}, "pending_approval": 0, "executed_actions": 0, "ms": []}
    interrupted = False
    try:
        with open(actions_path, "a", encoding="utf-8") as fa, open(audit_path, "a", encoding="utf-8") as fl:
            for run_k, cid in todo:
                obj, det = store.get(cid)
                o_hash = object_hash(obj)
                seed = a.seed if a.seed_mode == "fixed" else a.seed + run_k - 1
                ctx = {"case_id": cid, "run": run_k, "seed": seed, "prompt_hash": p_hash,
                       "case_object_hash": o_hash, "schema_hash": schema_hash}
                entry = {"ts": utc_now(), "run_id": run_id, "label": a.label, "case_id": cid, "run": run_k,
                         "client": client.name, "model": config["model"], "model_digest": "",
                         "temperature": temperature, "seed": seed, "prompt_version": p_version,
                         "prompt_variant": a.prompt_variant, "prompt_hash": p_hash, "schema_hash": schema_hash,
                         "case_object_hash": o_hash, "case_object": obj, "raw_output": None}
                t0 = time.monotonic()
                stats["calls"] += 1
                try:
                    resp = client.complete(system, user_message(obj), schema, ctx)
                except LLMTransportError as e:
                    stats["transport_errors"] += 1
                    entry.update({"error": str(e), "disposition": "llm_error",
                                  "duration_ms": int(1000 * (time.monotonic() - t0))})
                    fl.write(json.dumps(entry, ensure_ascii=True) + "\n")
                    fl.flush()
                    show(f"  [run {run_k}] {cid}: Transportfehler {e}")
                    if a.stop_on_error:
                        break
                    continue
                ms = int(1000 * (time.monotonic() - t0))
                gr = guard.check(resp.raw, cid, det["detected_type"], obj)
                entry.update({"model": resp.model or config["model"], "model_digest": resp.model_digest,
                              "raw_output": resp.raw, "thinking": resp.thinking, "llm_meta": resp.meta,
                              "parsed_output": gr.parsed, "guardrail": gr.to_dict()})
                for x in gr.violations:
                    stats["violations"][x["rule"]] = stats["violations"].get(x["rule"], 0) + 1
                for x in gr.warnings:
                    stats["warnings"][x["rule"]] = stats["warnings"].get(x["rule"], 0) + 1
                if gr.parsed is None:
                    stats["parse_errors"] += 1

                if not gr.passed:
                    stats["guardrail_blocked"] += 1
                    appr = {"required": False, "mode": a.approval, "status": "not_applicable", "decisions": []}
                    executed, pending, rejected = [], [], []
                    disposition = "blocked_to_human"
                else:
                    appr = approval_mod.request_approval(cid, gr.parsed, gr.requires_approval, a.approval,
                                                         a.approver, ask=ask, show=show)
                    executed, pending, rejected = approval_mod.execute(gr.parsed, gr.requires_approval,
                                                                       appr["decisions"])
                    bad = guard.check_execution(executed, appr["decisions"], gr.parsed, det["detected_type"])
                    if bad:                                   # darf nie eintreten (Programmfehler)
                        entry["guardrail"]["violations"] += bad
                        executed = []
                        disposition = "blocked_autonomy"
                    elif pending:
                        disposition = "partially_executed_pending_approval" if executed else "pending_approval"
                    elif rejected:
                        disposition = "rejected_by_human"
                    else:
                        disposition = "executed"
                    stats["pending_approval"] += int(bool(pending))
                    stats["executed_actions"] += len(executed)
                entry.update({"approval": appr, "executed_actions": executed, "pending_actions": pending,
                              "rejected_actions": rejected, "disposition": disposition, "duration_ms": ms})
                fl.write(json.dumps(entry, ensure_ascii=True) + "\n")
                fl.flush()
                fa.write(json.dumps(action_record(cid, run_k, gr), ensure_ascii=True) + "\n")
                fa.flush()
                stats["ms"].append(ms)
                acts = ";".join(f"{x.get('action_id')}{'/' + x['target_role'] if x.get('target_role') else ''}"
                                for x in (gr.parsed or {}).get("actions") or [] if isinstance(x, dict))
                show(f"  [run {run_k}] {cid} {det['detected_type']:>4} -> "
                     f"{(gr.parsed or {}).get('exception_type', '-')} {acts or '-'} | "
                     f"{'ok' if gr.passed else 'BLOCK ' + ','.join(x['rule'] for x in gr.violations)} | "
                     f"{disposition} | {ms} ms")
    except KeyboardInterrupt:
        interrupted = True
        show("\nAbgebrochen. Fertige Zeilen sind gespeichert, erneuter Aufruf mit gleichem Label setzt fort.")

    ms = stats.pop("ms")
    stats["mean_ms"] = int(sum(ms) / len(ms)) if ms else None
    stats["completed_pairs"] = len(read_done(actions_path))
    stats["expected_pairs"] = len(ids) * a.k
    config_path.write_text(json.dumps({"config": config, "cases": ids, "k": a.k, "last_run_id": run_id,
                                       "interrupted": interrupted, "summary_last_session": stats},
                                      indent=1, ensure_ascii=True), encoding="utf-8")
    show(f"Fertig: {stats['completed_pairs']}/{stats['expected_pairs']} Paare | Parsefehler {stats['parse_errors']} | "
         f"blockiert {stats['guardrail_blocked']} {stats['violations'] or ''} | offen zur Freigabe "
         f"{stats['pending_approval']} | Transportfehler {stats['transport_errors']} | mittel {stats['mean_ms']} ms")
    show(f"-> {actions_path}, {audit_path}")
    return stats


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description="Agent-Pipeline (Schritt 4)")
    ap.add_argument("--cases", default="pilot", help="pilot | e6_full | routed | Liste von IDs (C0001,C0002)")
    ap.add_argument("--k", type=int, default=1)
    ap.add_argument("--client", choices=["ollama", "mock", "replay"], default="mock")
    ap.add_argument("--model", default="")
    ap.add_argument("--temperature", type=float, default=None, help="Standard aus spec (0)")
    ap.add_argument("--seed", type=int, default=None, help="Standard aus spec (42)")
    ap.add_argument("--seed-mode", choices=["fixed", "per_run"], default="fixed",
                    help="per_run: Seed + Run - 1 (fuer Laeufe mit Temperatur > 0)")
    ap.add_argument("--label", required=True)
    ap.add_argument("--prompt-variant", choices=["a", "b"], default="a")
    ap.add_argument("--include-concept", action="store_true", help="E5 und E7 verarbeiten (Konzept)")
    ap.add_argument("--approval", choices=["batch", "interactive"], default="batch")
    ap.add_argument("--approver", default="")
    ap.add_argument("--mock-faults", choices=["none", "mixed"], default="none")
    ap.add_argument("--replay-label", default="")
    ap.add_argument("--url", default="http://localhost:11434")
    ap.add_argument("--endpoint", choices=["chat", "generate"], default="chat")
    ap.add_argument("--think", choices=["on", "off", "unset"], default="off")
    ap.add_argument("--num-ctx", type=int, default=8192)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--stop-on-error", action="store_true")
    ap.add_argument("--out-dir", default=str(ROOT / "out"))
    ap.add_argument("--audit-log", default="")
    return ap.parse_args(argv)


def main():
    run(parse_args())


if __name__ == "__main__":
    main()
