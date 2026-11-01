# WI-Projekt Thema 75: Agentic Process Automation (Order-to-Cash)

Stand 01.11.2026. Schritte 1 bis 3 erledigt (K3 freigegeben). Schritt 4 (Agent-Kern) erstellt, wartet auf K4. Bericht: `out/step4_report.md`. Lokale Läufe: `docs/ANLEITUNG_lokal.md`.
Kontext, Entscheide und Plan: `docs/WI-Projekt_Zwischenpraesentation_Kontext_und_Plan.md` (v0.4). Parameter: `spec/spec.yaml` (v0.4.0).

## Struktur

| Ordner | Inhalt |
|---|---|
| `docs/` | Kontextdokument v0.4, Prompts für Schritt 3 und 4, `ANLEITUNG_lokal.md` |
| `spec/` | `spec.yaml` (Single Source of Truth für Parameter) |
| `src/` | Generator, Validierung, K2-Paket, Keyword-Labeler, Werkzeuge für externe Modelle, Erkennung, Baseline, Metriken, Agent (Fallobjekt, LLM-Client, Guardrails, Freigabe, Pipeline, Audit-Ansicht) |
| `tests/` | Tests Schritt 4 (`python -m unittest discover -s tests`) |
| `data/` | Event Log, Fallattribute, Ground Truth, Freitext-Vorlagen, Pilot, Labeling |
| `out/` | Berichte (Generierung, Labeling, K2-Befunde, Schritt 3), Erkennung, Baseline-Aktionen, Metriken |
| `prompts/` | `agent_prompt.md` (Systemprompt Agent); `extern/`: Prompts und Anleitung für externe Modelle (Iteration 2, optional) |

## Befehle (aus dem Repo-Root, Python 3 mit pandas, numpy, PyYAML)

| Zweck | Befehl |
|---|---|
| Daten erzeugen (deterministisch, Seed 42) | `python src/generate_log.py` |
| Daten prüfen, Bericht schreiben | `python src/validate_log.py` |
| K2-Paket erzeugen | `python src/make_k2.py` |
| Keyword-Labeler auf Labeling-Items | `python src/keyword_labeler.py --items data/labeling/label_items.csv --out out/labels_keyword.txt` |
| Erkennung (alle Fälle) | `python src/detect.py` |
| Sensitivität der Erkennung (Mutanten) | `python src/detect_checks.py` |
| Baseline | `python src/baseline.py` |
| Metriken für eine Aktionsdatei | `python src/metrics.py --actions out/baseline_actions.jsonl --label baseline` |
| Apromore-Import vorbereiten (AP7) | `python src/export_apromore.py` (Anleitung: `docs/ANLEITUNG_apromore.md`) |
| Externe Modelle (Iteration 2) | siehe `prompts/extern/ANLEITUNG.md` und `src/extern_tasks.py` |
| Tests Agent-Kern | `python -m unittest discover -s tests` |
| Ollama prüfen | `python src/llm_client.py check --model qwen3.5:9b --think off` |
| Agent mit Mock (Sandbox) | `python src/run_agent.py --cases pilot --k 3 --client mock --mock-faults mixed --label mock` |
| Agent lokal (Ollama) | `python src/run_agent.py --cases pilot --k 3 --client ollama --model <modell> --think off --label <label>` |
| Replay eines Laufs | `python src/run_agent.py --cases pilot --k 3 --client replay --replay-label <label> --label <neu>` |
| Audit-Log lesen | `python src/audit_view.py --label <label> [--case C0317] [--run 1]` |
| Metriken Agent | `python src/metrics.py --actions out/agent_actions_<label>.jsonl --label <label> --scopes pilot` (E6: `--scopes e6_full`, end-to-end: `--strict-guardrails`) |

Nach jeder Änderung an `data/freitext_vorlagen.yaml` oder `spec/spec.yaml`: Generator und Validierung neu laufen lassen.

## Daten in Kürze

1000 Fälle, 5905 Events. Happy Path 700, E2 60, E3 60, E5 40, E6 80 (je 20 pro Freitext-Kategorie), E7 60.
Pilot: 20 Fälle in `data/pilot_sample.csv` (17 erreichen den Agenten). Zusatzlauf E6: alle 80 E6-Fälle. Validierung: 43 von 43 Prüfungen bestanden.
Baseline (Schritt 3): E2/E3 120/120, E6 59/80, Happy Path mit Freitext 70/70, Pilot 17/17.
Trigger auf Tagesbasis. Stichtag immer 18:00. Kein Stichtag nach dem Datenabzug 31.10.2026.

## Konventionen

Deutsch, Schweizer Schreibweise (ss), keine Gedankenstriche. ASCII in Code, Daten und Spec, Umlaute nur in Markdown-Dokumenten.
Entscheide trifft Jan. Annahmen werden im Kontextdokument (Abschnitt 14) als "Annahme" geführt.
