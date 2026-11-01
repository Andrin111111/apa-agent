# Schritt 6: Demo für Folie 6 (Bericht zu K6)

Stand 01.11.2026. Grundlage: Kontextdokument v0.6.1, `spec.yaml` v0.5.0, Prompt v1.2a (alle unverändert), Ergebnisse Schritt 5.
Alles in Claude Code auf dem MacBook Pro M4 Pro ausgeführt (Ollama 0.40.13, `qwen3.5:9b-q4_K_M`, Digest `56671c2ab938`).

## 1. Kurzfassung

| Punkt | Ergebnis |
|---|---|
| Demo-Werkzeug | `src/demo.py`: Wrapper um `run_agent.run` (keine zweite Logik), Live und Replay, Vorabprüfung `--check` mit Aufwärmen |
| Demo-Fälle (Vorschlag) | C0902 (E2, A6 mit Freigabe), C0537 (E3, A4 + A2 autonom), C0244 (E6 indirekte Reklamation, Agent A5, Regel A3). Reserve C0776 (echter Fehler) |
| Ehrlichkeitspunkt (Vorschlag) | Begründung bei C0902 behauptet "automatische Weiterleitung", das System hält zur Freigabe an. Dazu dauerhaft auf dem Bildschirm: "Begründung: Text des Modells, nicht geprüft" und "Guardrails prüfen Form, nicht fachliche Richtigkeit" |
| Reproduzierbarkeit | 16 von 16 Live-Aufrufen in dieser Sitzung bytegleich mit den Evaluationsläufen `pilot_t0` / `e6_t0`. 20 von 20 Replay-Ausgaben bytegleich |
| Laufzeit | live 6,0 bis 11,2 s pro Fall (Mittel 7,5 s), nach `--check` 6,8 bis 7,9 s. Replay 0,8 s für alle drei Fälle. Technische Laufzeit der Demo 22 s, Rest ist Sprechzeit |
| Tests | 44 OK (37 bestehende + 7 neue in `tests/test_demo.py`) |
| Auswertungsdaten | `out/audit_log.jsonl` unverändert (SHA-256 `9e41524ef01d…` vor und nach allen Läufen), Demo schreibt nur nach `out/demo/` |
| Drehbuch | `docs/demo_drehbuch.md`: Ablauf 4:00 mit Zeiten, Befehlen, Bildschirm, Sprechtext, Reserve, Notfallplan, Anleitung Bildschirmaufzeichnung |

## 2. Artefakte und Änderungen

| Datei | Status | Inhalt |
|---|---|---|
| `src/demo.py` | neu | Anzeige pro Fall: Fallkern (Erkennung, Trigger, 2 bis 3 Kennzahlen, Freitext), Agent (Typ, Aktionen mit Autonomiestufe, Begründung), Regel (`--baseline`), Soll (`--truth`), Guardrails, Freigabe interaktiv, Ergebnis, Vergleich mit Evaluationslauf (REPRO). `--check`, `--clear`, `--verbose`, `--cases` |
| `tests/test_demo.py` | neu | 7 Tests: Replay mit Freigabe, Ablehnen und offen lassen, Ausgabe reproduzierbar, Label doppelt, Aufzeichnung fehlt, Soll-Zeile über `metrics.judge`, Formatierung. Prüft nach jedem Test, dass `out/audit_log.jsonl` unverändert ist |
| `docs/demo_drehbuch.md` | neu | Drehbuch, Notfallplan, Aufzeichnungsanleitung |
| `out/demo/` | neu | `audit_log_demo.jsonl` (alle Demo-Läufe, angehängt), Aufzeichnungen `demo_ref` und `demo_reserve_c0776`, Live-Lauf `demo_snapshot2`, Textfassungen `console_check.txt`, `console_demo_live.txt`, `console_demo_reserve_c0776.txt` |
| `src/run_agent.py` | **geändert** (+5/−1 Zeilen) | Optionaler Parameter `on_decision=None` in `run()`, aufgerufen nach den Guardrails und vor der Freigabe. Standard `None`: Verhalten unverändert, bestehende 37 Tests grün. Nötig, damit die Demo den Entscheid vor der Freigabefrage zeigen kann |

Nicht geändert: Prompt, Guardrails, Freigabe, Fallobjekt, LLM-Client, `spec.yaml`, Kontextdokument, README, alle Auswertungsdateien von Schritt 5.

## 3. Wahl der Demo-Fälle

Geprüft im Audit-Log (`pilot_t0` k = 3, `pilot_t07` k = 3, `e6_t0`) und live in dieser Sitzung.

| Fall | Warum | Stabilität | Gegen Alternativen |
|---|---|---|---|
| C0902 (E2) | Klare Überschreitung (+32,4 %), Zahlungshistorie schlecht, kein Rauchtestfall. Begründung enthält die falsche Nebenaussage "automatische Weiterleitung" (K5-17, Punkte 1): echte, nicht inszenierte Grenze | 6/6 korrekt (T = 0 und 0,7), live 5/5 bytegleich | C0317 ist Rauchtestfall (Prompt daran nachgeschärft). C0556, C0671 ohne falsche Nebenaussage |
| C0537 (E3) | Kurze Geschichte (Termin morgen, kommissioniert, nicht versendet), Begründung bezieht die Lage ein (K5-01, Punkte 2), kein Rauchtestfall | T = 0 3/3 identisch, T = 0,7 A4 statt A4 + A2 (ebenfalls korrekt), live 5/5 bytegleich | C0067 ist Rauchtestfall. C0642 Begründung ohne Bezug zur Lage |
| C0244 (E6) | Indirekte Reklamation (Kartons durchnässt), Baseline mahnt (A3), Agent A5 an Kundendienst. Kontrast verstärkt: 39 Tage überfällig, Zahlungshistorie schlecht | `e6_t0` korrekt, Vorlage `complaint_05` auch bei C0612 korrekt, live 5/5 bytegleich | C0298 Begründung mit "Lieferstopp" (falsch). C0353 gleichwertig (50 statt 100 m) |
| C0776 (Reserve) | Einziger Agentenfehler im E6-Zusatzlauf (A6 statt A0), Guardrails bestanden, Freigabe fängt ihn ab | live 1/1 bytegleich mit `e6_t0` | |

Einschränkung offen ansagen: C0244 gehört zu den Vorlagen, deren Text die Prompt-Definition fast wörtlich trifft ("Schaden", `step5_report.md` 7.2). C0902 und C0537 sind Pilotfälle, aber keine Rauchtestfälle.

## 4. Ehrlichkeit in der Demo (Vorschlag)

| Variante | Inhalt | Zeit | Empfehlung |
|---|---|---|---|
| A | C0902: Begründung "automatische Weiterleitung" gegen "Freigabe nötig" auf demselben Bildschirm. Dazu dauerhafte Bildschirmhinweise (Begründung nicht geprüft, Guardrails prüfen nur Form) und Einschränkung bei C0244 | 0 s zusätzlich | **ja** (Standard) |
| B | Reservefall C0776 live: echter Fehler, Guardrails lassen ihn durch, Mensch lehnt ab | ca. 45 s | als Reserve für Fragen oder wenn der Probelauf unter 3:30 bleibt |
| C | Mock mit Fehlerinjektion (als simuliert angesagt), damit ein Guardrail sichtbar blockiert | ca. 40 s | nein: nicht gebaut. Zeigt etwas, das mit dem echten Modell nie auftrat (0 von 182), und überzeichnet die Rolle der Guardrails |

## 5. Getestete Befehle und Laufzeiten

Alle aus dem Repo-Root mit `~/.venvs/apa-agent/bin/python`.

| Befehl | Ergebnis | Laufzeit |
|---|---|---|
| `python -m unittest discover -s tests` | vor Schritt 6: 37 OK; danach 44 OK | 2,1 s bzw. 5,4 s |
| `python src/llm_client.py check --model qwen3.5:9b-q4_K_M --think off` | `ERGEBNIS: OK, Schema wird erzwungen` | 3,7 s |
| `python src/demo.py --check` (Modell vorher entladen) | `BEREIT`, alle 8 Prüfungen OK | 12,1 s |
| `python src/demo.py --check` (Modell geladen) | `BEREIT` | 7,7 s |
| `printf 'j\nj\n' \| python src/demo.py --client ollama --label demo_ref --approver Claude --baseline --no-pause` | 3/3 executed, bytegleich mit Evaluation | 26,0 s (erster Aufruf 10,2 s, ohne Aufwärmen) |
| `printf 'j\nj\n' \| python src/demo.py --client ollama --label demo_snapshot2 --approver Jan --baseline --truth --no-pause` (nach `--check`) | 3/3 executed, bytegleich, LLM 7,0 / 6,8 / 7,0 s | 21,7 s |
| `printf 'j\nj\n' \| python src/demo.py --client replay ... --baseline --truth --no-pause` | identisch zum Live-Lauf bis auf Modus-Zeile, Zeitangaben und Label (`diff` geprüft) | 0,8 s |
| `printf 'n\nGrund\n\n' \| python src/demo.py --client replay ...` | rejected_by_human, executed, pending_approval | 0,8 s |
| `printf '\nj\n\n\nj\n' \| python src/demo.py --client replay --clear ...` (mit Pausen wie im Drehbuch) | Ablauf korrekt, Exit 0 | 0,8 s |
| `python src/demo.py --client ollama --cases C0776 ...` | A6 (Fehler wie in `e6_t0`), bytegleich | 8,0 s |
| `python src/demo.py --client ollama --url http://localhost:9` (Ollama aus) | `Kein Ergebnis: ... Connection refused`, Fallback-Befehl, Exit 2 | 0,5 s |
| Dummy-Server ohne Antwort, `--timeout 3` (Ollama hängt) | `Kein Ergebnis: TimeoutError`, Fallback-Befehl | 3,5 s |

Nicht getestet (nur Jan kann es): echte Tastatureingabe im Terminal, Ctrl+C während des LLM-Aufrufs (Code-Pfad: `run_agent` fängt `KeyboardInterrupt`, Demo meldet "abgebrochen" und den Fallback-Befehl), Farben und Lesbarkeit auf dem Beamer, Sprechzeit.

## 6. Annahmen

| # | Annahme | Begründung |
|---|---|---|
| D6-A1 | Demo-Dateien in `out/demo/` (Audit-Log `out/demo/audit_log_demo.jsonl`) statt `out/audit_log_demo.jsonl` | Alles zur Demo an einem Ort, `out/` der Auswertung bleibt unberührt |
| D6-A2 | Replay-Quelle ist eine eigene Live-Aufzeichnung (`demo_ref`), nicht direkt der Evaluationslauf | `ReplayClient` liest ein Label aus dem Log, in das geschrieben wird. Die Aufzeichnung ist mit `pilot_t0` / `e6_t0` bytegleich (geprüft, auch in `--check`) |
| D6-A3 | Ein `run()`-Aufruf pro Fall, pro Demo-Lauf ein Label mit Zeitstempel | Pause zwischen den Fällen. Fortsetzen-Logik von `run_agent` würde sonst bereits gezeigte Fälle überspringen |
| D6-A4 | Timeout 30 s pro LLM-Aufruf in der Demo (Pipeline 300 s) | Live ist ein langes Warten schlechter als der Wechsel auf das Replay |
| D6-A5 | `--truth` zeigt das Soll aus der Ground Truth, nur in der Anzeige, bewertet mit `metrics.judge` | Sonst sieht das Publikum bei C0244 nur "anders", nicht wer richtig liegt. Das Fallobjekt enthält die Ground Truth weiterhin nicht |
| D6-A6 | Reihenfolge E2, E3, E6 wie im Folientitel | Keine Folienänderung nötig |
| D6-A7 | `--check` wärmt mit einem echten Agentenaufruf an C0556 (Pilotfall, nicht in der Demo) auf, ohne Audit-Eintrag, und hält das Modell 90 min geladen | Ohne Aufwärmen dauert der erste Aufruf 10 bis 11 s statt 7 s. Ein Ladeaufruf ohne `num_ctx` 8192 erzwingt beim ersten Demo-Aufruf ein Neuladen (gemessen, behoben) |
| D6-A8 | Meine Testläufe bleiben im Demo-Audit-Log (Labels `demo_test_*`, `demo_snapshot*`), nur deren Aktions- und Konfigurationsdateien sind gelöscht | Audit-Log nur anhängen. Keine Auswertung liest dieses Log |
| D6-A9 | Der Ordner `apa-agent/apa-agent` (älterer Prototyp mit `agent.py`, `config.py`) ist kein massgebliches Dokument | Kein Kontextdokument und keine Spec darin, daher kein Stopp |

## 7. Kritische Bewertung: was live schiefgehen kann, was missverstanden werden kann

| Risiko | Einschätzung | Gegenmassnahme |
|---|---|---|
| Publikum hält die drei Fälle für Evidenz | hoch, weil alle drei "korrekt" zeigen | Sprechtext am Schluss ("Illustration, kein Beleg"), Reservefall C0776 bereit, Verweis auf Folie 7 |
| "Der Agent erkennt Ausnahmen" | mittel | Bildschirm: "E2 per Regel (deterministisch, ohne LLM)" |
| Begründung wird als Erklärung gelesen | hoch, Text klingt souverän | Kennzeichnung "nicht geprüft" plus Ehrlichkeitspunkt bei C0902 |
| "Guardrails schützen vor Fehlentscheiden" | mittel | Bildschirm: "prüft Form, nicht fachliche Richtigkeit". Reserve C0776 zeigt es konkret |
| "bytegleich" als Qualitätsbeleg gelesen | mittel | Sprechtext: reproduzierbar heisst nicht korrekt. Gilt nur für diese Umgebung |
| "ausgeführt" als echte Buchung gelesen | gering | Bildschirm: "(simuliert)" bei jeder Ausführung |
| Ollama-App aktualisiert sich vor dem Termin | mittel (macOS-App aktualisiert automatisch) | `--check` vergleicht Version und Digest. Bei neuer Version kann REPRO "weicht ab" zeigen, das ist ehrlich, aber zu erklären |
| Modell kalt oder entladen | gering nach `--check` (90 min) | `--check` höchstens 15 min vor Beginn |
| Beamer verändert Fenstergrösse, Zeilen brechen um | mittel | Ausgabe auf 78 Spalten begrenzt, Fallblock bis 39 Zeilen. Schrift an K6 testen |
| Farben schlecht lesbar am Beamer | unbekannt | `--no-color` ist vorhanden. An K6 testen |
| Replay wird nicht angesagt | gering | Kopfzeile "Modus AUFZEICHNUNG", Ansage im Drehbuch |
| Demo-Zeit wird überzogen | mittel: viele Sprechpunkte bei E2 und E6 | K6 mit Stoppuhr. Kürzbar: Sprechtext bei E3, Zusammenfassung |

## 8. Offene Entscheide (Jan, K6)

| # | Frage | Empfehlung |
|---|---|---|
| 1 | Demo-Fälle | C0902, C0537, C0244 (Abschnitt 3) |
| 2 | Grenze / Ehrlichkeitspunkt | Variante A, C0776 als Reserve (Abschnitt 4) |
| 3 | Vergleich mit Baseline | ja, mit Soll-Zeile: `--baseline --truth`. Zeigt "Regel gleich" bei E2/E3 (kein Mehrwert, ehrlich) und "Regel falsch" bei E6 |
| 4 | Aufzeichnung | durch Jan nach erfolgreichem Probelauf (Drehbuch Abschnitt 5) |
| 5 | Commit | `src/demo.py`, `src/run_agent.py`, `tests/test_demo.py`, `docs/demo_drehbuch.md`, `out/demo/`, dieser Bericht. Kein Video ins Git |

## 9. Nachführungen (nach K6 auf Anweisung Jan ausgeführt: Kontextdokument v0.7, README, `.gitignore`)

**Kontextdokument (v0.6.1 → v0.7):**
1. Abschnitt 0 (Repo-Struktur): `src/demo.py` ohne Stern, `docs/demo_drehbuch.md`, `out/demo/`, `out/step6_report.md`, Tests 44.
2. Abschnitt 9: Human-Approval interaktiv in der Demo umgesetzt, Hook `on_decision`.
3. Abschnitt 11, Folie 6: Fälle C0902, C0537, C0244, Quelle `out/demo/audit_log_demo.jsonl` statt `audit_log.jsonl`, Fallback Replay plus Aufzeichnung.
4. Abschnitt 12/13: Schritt 6 erledigt (nach K6), AP8 in Arbeit, "So geht es weiter" ersetzen.
5. Abschnitt 14: Annahmen D6-A1 bis D6-A9, Entscheide K6.
6. Abschnitt 16: Risiko "Demo scheitert live" mit konkreter Gegenmassnahme (Replay, `--check`), neu "Publikum hält Demo-Fälle für Evidenz", "Ollama-Update vor dem Termin".
7. Abschnitt 17: Änderungslog.

**README:** Befehle `demo.py --check`, live, replay; Testanzahl 44; Ordner `out/demo/`; Hinweis auf `docs/demo_drehbuch.md`.

**`ANLEITUNG_lokal.md`:** optional Abschnitt "Demo" mit Verweis auf das Drehbuch.

**`spec.yaml`:** keine Änderung nötig.

**Sonstiges:** `.gitignore` im Git-Root angelegt (`__pycache__/`, `*.py[cod]`, `.DS_Store`, `*.mov`). Videos bleiben damit ausserhalb des Repos.

**K6:** Probelauf live und Replay bei Jan bestanden (Labels `demo_live_20261101T190550` und `demo_replay_*` im Demo-Audit-Log, live 3/3 bytegleich, 6,7 bis 7,0 s pro Fall).
