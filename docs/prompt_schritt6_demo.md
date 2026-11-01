# Prompt: Schritt 6, Demo (WI-Projekt Thema 75)

Du arbeitest als ausführender Agent im WI-Projekt "Agentic Process Automation" (ZHAW, Thema 75). Ich (Jan) kontrolliere deine Ergebnisse an Kontrollpunkten. Deine Aufgabe in diesem Chat ist ausschliesslich Schritt 6 des Arbeitsplans (AP8, Teil Demo): eine Live-Demo des Agenten für Folie 6 der Zwischenpräsentation, mit Drehbuch und Fallback. Am Ende hältst du bei Kontrollpunkt K6 an und wartest auf meinen Probelauf.

## 1. Umgebung

- Claude Code auf Jans MacBook Pro M4 Pro (24 GB). Repo: `/Users/jansamueltkac/00_WI_Bachelor/wi-projekt/apa-agent/wi-projekt_repo_stand_schritt4`, Git-Root eine Ebene höher, Branch `jan/zwischenpraesentation`.
- Python: venv `~/.venvs/apa-agent` (pandas, numpy, PyYAML). Das System-Python hat diese Pakete nicht. Alle Befehle mit `~/.venvs/apa-agent/bin/python` aus dem Repo-Root.
- Ollama 0.40.13 läuft lokal. Modell **`qwen3.5:9b-q4_K_M`** (nicht `qwen3.5:9b`, das ist ein MLX-Build ohne Schema-Erzwingung, HTTP 501). Immer `--think off`. Rund 7 s pro Aufruf.
- Du kannst das lokale LLM selbst aufrufen. Interaktive Eingaben (Freigabe j/n) kannst du nicht selbst tippen. Teste die interaktiven Teile mit vorgegebenen Antworten (z. B. Parameter `ask` in `run_agent.run` oder Eingabe per Pipe) und lass den echten interaktiven Durchlauf Jan machen (K6).

## 2. Zuerst lesen

- `docs/WI-Projekt_Zwischenpraesentation_Kontext_und_Plan.md` (v0.6): Abschnitte 0, 6, 9, 10, 11, 12, 14, 16.
- `out/step5_report.md` (Ergebnisse, Fehler, K5, Entscheide D-K5-1 bis D-K5-5), `out/step4_report.md` Abschnitte 3, 6, 7.
- `src/run_agent.py`, `src/approval.py`, `src/audit_view.py`, `src/llm_client.py` (Clients `ollama`, `replay`, `mock`), `docs/ANLEITUNG_lokal.md`.
- Findest du ältere Versionen (Kontextdokument < v0.6, spec < v0.5.0) als massgebliche Dateien, stoppe und melde es.
- Zu Beginn prüfen: `python -m unittest discover -s tests` (37 OK) und `python src/llm_client.py check --model qwen3.5:9b-q4_K_M --think off` (`ERGEBNIS: OK, Schema wird erzwungen`).

## 3. Ausgangslage

- Pipeline fertig: Fallobjekt → LLM → Guardrails → Freigabe → Aktion (simuliert) → Audit-Log. `run_agent.py` kann `--approval interactive --approver <Name>` (pro Aktion j/n/Enter). `audit_view.py` zeigt Einträge lesbar.
- Ergebnisse Schritt 5: Pilot 51/51 (T = 0), E6 79/80 vs. Baseline 59/80, Mehrwert nur bei indirekten Texten (31/32 vs. 11/32), Obergrenze wegen gleichem Autor. T = 0 bytegleich reproduzierbar, auch über Sitzungen. Guardrails haben mit dem echten Modell nie blockiert. Begründungen nennen die richtige Information, sind aber nicht immer treu (K5 1,56 von 2).
- Folie 6 laut Abschnitt 11: "Demo: E2 (Eskalation mit Freigabe), E3 (autonome Priorisierung), E6 (Ermessen)", 4 Minuten, Fallback Aufzeichnung.

## 4. Auftrag und Artefakte

| Artefakt | Inhalt |
|---|---|
| `src/demo.py` | Dünner Wrapper um die bestehende Pipeline (keine zweite Logik). Zeigt pro Fall knapp und gut lesbar auf einem Beamer: Fallkern (Erkennung, Trigger, Freitext, 2 bis 3 Kennzahlen), Entscheid des Agenten (Typ, Aktionen, Begründung), Guardrail-Ergebnis, Freigabe (interaktiv bei A5 bis A7), Disposition. Optional pro Fall die Baseline-Entscheidung zum Vergleich. Modi: `--client ollama` (live) und `--client replay` (Fallback ohne LLM, spielt einen gespeicherten Lauf ab, Ausgabe identisch). Eigenes Label und eigenes Audit-Log (z. B. `out/audit_log_demo.jsonl`), damit `out/audit_log.jsonl` der Auswertung unverändert bleibt |
| Demo-Fälle | Vorschlag mit Begründung, Entscheid Jan. Ausgangspunkt: E2 C0317 oder C0902 (A6 an Credit Management, Freigabe live), E3 C0067 (A2+A4 autonom), E6 indirekte Reklamation, bei der die Baseline mahnt (A3) und der Agent an den Kundendienst gibt (A5), z. B. C0244 (durchnässte Kartons). Prüfe vorher im Audit-Log (`pilot_t0`, `e6_t0`), dass der Agent dort korrekt und stabil ist. Kein Fall, an dem der Prompt nachgeschärft wurde, als "Beleg" verkaufen (C0317, C0067, C0880 sind Rauchtestfälle, als Illustration aber zulässig: offen sagen) |
| Ehrlichkeit in der Demo | Mindestens ein Punkt zeigt eine Grenze: z. B. die Begründung als nicht verlässliche Erklärung (K5) oder dass Guardrails keine fachlich falsche Aktion abfangen. Kein Fehler wird künstlich als Live-Fehler des Modells inszeniert. Ein simulierter Fehler (Mock) ist nur zulässig, wenn er als simuliert angesagt wird. Vorschlag machen, Entscheid Jan |
| `docs/demo_drehbuch.md` | Drehbuch für 4 Minuten: Ablauf mit Zeiten, Befehle, was auf dem Bildschirm zu sehen ist, Sprechtext in Stichworten, Übergang zu Folie 7, Notfallplan (Ollama hängt → Replay, Terminal-Schriftgrösse, Netzteil, `caffeinate`, Modell vorab laden mit einem Aufwärmaufruf) |
| Fallback | Replay-Lauf der Demo-Fälle getestet und bytegleich. Anleitung für eine Bildschirmaufzeichnung durch Jan (macOS: Cmd+Shift+5 oder QuickTime), da du nicht selbst aufzeichnen kannst |
| `tests/` | Test für `demo.py` (Replay-Modus, vorgegebene Freigabe-Antworten, eigenes Audit-Log, `out/audit_log.jsonl` unverändert). Bestehende 37 Tests bleiben grün |
| `out/step6_report.md` | Ergebnis, Annahmen, getestete Befehle mit Laufzeit, offene Entscheide, nötige Nachführungen |

## 5. Vorgaben

- Keine fachlichen Änderungen an Pipeline, Prompt (v1.2), Guardrails, `spec.yaml` (v0.5.0) oder Kontextdokument (v0.6). Kleine, rückwärtskompatible Erweiterungen (z. B. Ausgabeformat für die Demo) sind erlaubt, wenn alle Tests grün bleiben und die Auswertungsdateien von Schritt 5 unverändert sind. Melde jede Änderung an bestehenden Dateien.
- Prompt-Version, Modell, Temperatur 0, Seed 42 wie in den Läufen. Die Demo zeigt das System, wie es evaluiert wurde.
- Lesbarkeit vor Vollständigkeit: wenige Zeilen pro Fall, keine JSON-Wände. Rohdaten nur auf Wunsch (`--verbose`).
- Typ-Aktions-Guardrail ist nur Ausblick (D-K5-3), nicht bauen.
- Technik: Python 3, Standardbibliothek plus pandas, numpy, PyYAML. Kein Cloud-LLM. Keine neuen Abhängigkeiten (z. B. keine Terminal-UI-Bibliothek).
- Nicht Teil dieses Auftrags: Folien (Schritt 7), Streamlit, E5/E7, neue Läufe für die Evaluation.

## 6. Arbeitsweise

- Du bist ausführender Agent. Entscheide trifft Jan. Fehlt etwas, triff eine begründete Annahme und kennzeichne sie als "Annahme". Höchstens eine Rückfrage, nur wenn sie blockiert.
- Kritisch bewerten statt validieren: Was kann live schiefgehen, was könnte das Publikum falsch verstehen?
- Stil: Deutsch (Schweizer Schreibweise, ss), knapp und strukturiert, keine Gedankenstriche. Umlaute in Markdown, ASCII in Code und Daten.
- Commit und Push nur auf meine Anweisung.

## 7. Abschluss (K6)

Schreibe einen Bericht von **höchstens einer Seite** im Chat, Details in `out/step6_report.md`:

1. Was ich entscheiden muss (Demo-Fälle, Grenze/Ehrlichkeitspunkt, Vergleich mit Baseline ja/nein), jeweils mit Empfehlung, "ok" muss reichen
2. Was ich prüfen muss (K6: Probelauf live mit den genauen Befehlen, einmal Replay-Fallback, Zeit stoppen, Lesbarkeit auf grossem Bildschirm)
3. Ergebnis in 3 bis 5 Zahlen (Tests, Laufzeit pro Fall live und Replay, Gesamtdauer)
4. Annahmen, Risiken und nötige Nachführungen (Kontextdokument, README) in Stichworten

Danach stoppst du und wartest auf meine K6-Freigabe. Starte nicht selbst mit Schritt 7.
