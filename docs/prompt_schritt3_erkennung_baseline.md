# Prompt: Schritt 3, Erkennung, Baseline, Metriken (WI-Projekt Thema 75)

Du arbeitest als ausführender Agent im WI-Projekt "Agentic Process Automation" (ZHAW, Thema 75). Ich (Jan) kontrolliere deine Ergebnisse an Kontrollpunkten. Deine Aufgabe in diesem Chat ist ausschliesslich Schritt 3 des Arbeitsplans (AP3, AP6): Erkennung, Baseline und Metriken. Am Ende hältst du bei Kontrollpunkt K3 an und wartest auf meine Freigabe.

## 1. Zuerst lesen

- Hochgeladenes Zip `wi-projekt_repo_stand_schritt2.zip` entpacken. Darin `README.md`, `docs/WI-Projekt_Zwischenpraesentation_Kontext_und_Plan.md` (v0.3) und `spec/spec.yaml` (v0.3.0).
- Relevant im Kontextdokument: Abschnitte 0, 3, 5, 6, 8, 9, 10, 12, 14.
- Findest du ältere Versionen (Kontextdokument < v0.3, spec < v0.3.0) als massgebliche Dateien, stoppe und melde es. Die Entscheide in Abschnitt 14 sind verbindlich.
- Prüfe zuerst, dass die Daten reproduzierbar sind: `python src/generate_log.py && python src/validate_log.py` muss 43/43 ergeben.

## 2. Auftrag und Artefakte

| Artefakt | Inhalt |
|---|---|
| `src/detect.py` | `evaluate(case, now)` gemäss `spec.yaml` (Abschnitte `detection`, `exceptions`). Harte Trigger E2, E3, E5, E6, Vorrang E7 vor E2/E3, Tagesbasis, `invoice_date` aus dem ersten Event "Rechnung stellen". Zusätzlich weicher Trigger `free_text_present`. Liest nur `event_log.csv` und `cases.csv`, nie die Ground Truth. |
| `out/detections.csv` | `case_id, detected_type, hard_triggers, soft_trigger, routed_to_agent` für alle 1000 Fälle |
| `src/baseline.py` | Regelzuordnung Ausnahmetyp → Aktion. E6: Kategorie per `src/keyword_labeler.py` (bestehend, nicht nachtunen), dann Zuordnung laut spec. Fälle nur mit weichem Trigger: A0. E7: nicht bewertet (Konzept). Ausgabe im Format von `agent_output_schema` (spec), damit der Agent in Schritt 4 dieselbe Auswertung nutzt. |
| `out/baseline_actions.jsonl` | eine Zeile pro an den Agenten gerouteten Fall |
| `src/metrics.py` | Auswertung für jede Aktionsdatei im Schema-Format: Precision/Recall pro Typ (Erkennung), Aktionskorrektheit mit exaktem Mengenvergleich (D5) plus Rollenprüfung (`role_check`), Fehlalarme auf zwei Ebenen (Erkennung: Grenzfälle; Agent: Happy Path mit Freitext, Aktion ≠ A0), Enthaltungsquote, getrennt nach deterministisch und Ermessen. Auswertung auf allen Fällen und auf `pilot_sample.csv`. |
| `out/step3_report.md` | Ergebnisse mit Zahlen |

## 3. Vorgaben

- Erkennung unabhängig vom Generator implementieren (kein Import aus `generate_log.py` oder `validate_log.py`).
- Erwartung: Erkennung nahe 100 %, weil Generator und Erkennung dieselben Regeln umsetzen. Abweichungen sind Implementierungsfehler oder Spec-Lücken. Benenne diese Zirkularität als Limitation, statt sie als Erfolg darzustellen.
- Baseline E3: wähle eine feste Variante aus den zulässigen Mengen und begründe sie.
- Offene Spec-Punkte (`detection.open_points`) nicht still lösen: Annahme treffen, kennzeichnen, im Bericht nennen.
- `spec.yaml` und Kontextdokument nicht ändern. Nötige Nachführungen am Ende auflisten.
- Technik: Python 3, Standardbibliothek plus pandas, numpy, PyYAML. Kein LLM in diesem Schritt.
- Nicht Teil dieses Auftrags: Agent, Prompt, Guardrails, Approval, Folien.

## 4. Arbeitsweise

- Du bist ausführender Agent. Entscheide trifft Jan. Fehlt etwas, triff eine begründete Annahme und kennzeichne sie als "Annahme". Höchstens eine Rückfrage, nur wenn sie blockiert.
- Kritisch bewerten statt validieren.
- Stil: Deutsch (Schweizer Schreibweise, ss), knapp und strukturiert, keine Gedankenstriche. ASCII in Code und Daten.

## 5. Abschluss (K3)

Stelle die Dateien bereit (inklusive aktualisiertem Repo als Zip) und schreibe einen Bericht von **höchstens einer Seite**:

1. Was ich entscheiden muss (mit deiner Empfehlung, "ok" muss reichen)
2. Was ich prüfen muss (K3: Precision/Recall-Tabelle, 5 Fehler- oder Grenzfälle)
3. Ergebnis in 3 bis 5 Zahlen
4. Annahmen und Limitationen in Stichworten

Details gehören in `out/step3_report.md`, nicht in den Chat. Danach stoppst du und wartest auf meine K3-Freigabe. Starte nicht selbst mit Schritt 4.
