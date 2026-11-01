# Prompt: Schritt 4, Agent-Kern (WI-Projekt Thema 75)

Du arbeitest als ausführender Agent im WI-Projekt "Agentic Process Automation" (ZHAW, Thema 75). Ich (Jan) kontrolliere deine Ergebnisse an Kontrollpunkten. Deine Aufgabe in diesem Chat ist ausschliesslich Schritt 4 des Arbeitsplans (AP4, AP5): Agent-Kern mit Fallobjekt, Prompt, LLM-Client, Guardrails, Freigabe und Audit-Log. Am Ende hältst du bei Kontrollpunkt K4 an und wartest auf meine Freigabe.

**Stand lokales LLM (von Jan auszufüllen):** Ollama installiert: ja. Version: 0.40.13. Bereits geladene Modelle: keine.

## 1. Zuerst lesen

- Hochgeladenes Zip `wi-projekt_repo_stand_schritt3.zip` entpacken. Darin `README.md`, `docs/WI-Projekt_Zwischenpraesentation_Kontext_und_Plan.md` (v0.4), `spec/spec.yaml` (v0.4.0), `out/step3_report.md`.
- Relevant im Kontextdokument: Abschnitte 0, 3, 5, 6, 7, 9, 10, 12, 14, 15.
- Findest du ältere Versionen (Kontextdokument < v0.4, spec < v0.4.0) als massgebliche Dateien, stoppe und melde es. Die Entscheide in Abschnitt 14 sind verbindlich.
- Reproduzierbarkeit prüfen, alle Befehle aus dem Repo-Root:
  - `python src/generate_log.py && python src/validate_log.py` muss 43/43 ergeben.
  - `python src/detect.py && python src/baseline.py && python src/metrics.py --actions out/baseline_actions.jsonl --label baseline` muss 249/270 (alle Fälle) und 17/17 (Pilot) ergeben.

## 2. Ausgangslage

- Die Erkennung ist deterministisch und fertig (`src/detect.py`). Das LLM erkennt nicht, es interpretiert und wählt Aktionen (Entscheid 25.10.2026).
- `src/metrics.py` wertet jede Datei im Format `agent_output_schema` aus, inklusive optionalem Feld `run` (k Durchläufe). Der Agent muss genau dieses Format liefern, damit Agent und Baseline gleich bewertet werden.
- Die Baseline erreicht bei E2/E3 und Happy Path 100 %, bei E6 73,8 % (Fehler nur bei indirekten Texten). Der Mehrwert des Agenten ist bei E6 zu zeigen.
- Laufumfang für Schritt 5 (Entscheid D-K3-1): Pilot (17 geroutete von 20 Fällen, k = 3) und E6-Zusatzlauf (alle 80 E6, k = 1), dazu ein Lauf mit Temperatur > 0.
- Im Chat kannst du das lokale LLM nicht ausführen. Teste alles mit einem Mock-Client. Jan fährt die echten Läufe lokal.

## 3. Auftrag und Artefakte

| Artefakt | Inhalt |
|---|---|
| `src/case_object.py` | Fallobjekt aus `cases.csv`, `event_log.csv` und `detect.evaluate`: Fallattribute, Verlauf (Aktivität, Datum, Rolle), Freitext, harte Trigger, weicher Trigger, abgeleitete Werte (z. B. Rechnungsdatum, Fälligkeit, Tage überfällig, Tage bis Liefertermin, Überschreitungsquote). Nie Ground Truth, `generator_tag`, Vorlagen-IDs oder Kategorie. Deterministische Serialisierung (sortierte Schlüssel), damit ein Hash pro Fallobjekt reproduzierbar ist. |
| `prompts/agent_prompt.md` | Systemprompt: Rolle, Handlungskatalog mit Autonomiestufen, Ausnahmetypen, Ermessensrichtlinie (wörtlich aus spec), Enthaltungsregel, Ausgabeformat. Versioniert (Version im Kopf, Hash im Audit-Log). |
| `src/llm_client.py` | Austauschbare Schnittstelle mit drei Implementierungen: `OllamaClient` (HTTP auf localhost, nur Standardbibliothek, JSON-Schema als `format`, Temperatur und Seed aus spec, Timeout, Modell-Digest erfassen), `ReplayClient` (spielt gespeicherte Rohantworten pro Fall und Run ab), `MockClient` (deterministisch, für Sandbox-Tests, darf absichtlich fehlerhafte Ausgaben erzeugen). |
| `src/guardrails.py` | Alle Prüfungen aus `spec.guardrails`. Ergebnis pro Ausgabe: bestanden ja/nein, Liste der Verstösse. |
| `src/approval.py` | Freigabe für A5 bis A7 und für E7. Zwei Modi: interaktiv (CLI, für Demo) und Batch (`pending`, nichts wird ausgeführt, nichts automatisch freigegeben). |
| `src/run_agent.py` | Pipeline Fallobjekt → LLM → Guardrails → Freigabe → Aktion (simuliert) → Audit-Log. Parameter mindestens: Fallauswahl (`pilot`, `e6_full`, Liste von IDs), k, Client, Modell, Temperatur, Label. Fortsetzbar (fertige Fall/Run-Paare überspringen), abbrechbar. Schreibt `out/agent_actions_<label>.jsonl` (Schema-Format mit `run`) und hängt an `out/audit_log.jsonl` an. |
| `out/audit_log.jsonl` | Beispieleinträge aus dem Mock-Lauf. Felder mindestens: Zeitstempel, Lauf-ID, Fall, Run, Client, Modell und Digest, Temperatur, Seed, Prompt-Version und Hash, Fallobjekt-Hash, Rohausgabe, geparste Ausgabe, Guardrail-Ergebnis, Freigabe-Entscheid, ausgeführte (simulierte) Aktionen, Laufzeit. |
| `tests/` | Tests mit Standardbibliothek (`unittest`): jeder Guardrail mindestens einmal ausgelöst, Fallobjekt ohne Ground-Truth-Felder, Replay reproduziert Mock-Lauf, `metrics.py` verarbeitet Mock-Ausgabe. |
| `docs/ANLEITUNG_lokal.md` | Für Jan: Ollama-Setup, Modell laden, Rauchtest mit 3 Fällen (je ein E2, E3, E6 aus dem Pilot), Befehle für Schritt 5 (Pilot k = 3, E6-Zusatzlauf k = 1, Lauf mit Temperatur > 0), Auswertung mit `metrics.py`, was zurück in den Chat gehört. |
| `out/step4_report.md` | Ergebnisse, Annahmen, Modellvorschlag, nötige Nachführungen. |

## 4. Vorgaben

- **Determinismus:** Temperatur 0, Seed 42, JSON-Schema per constrained decoding (`spec.meta.llm`). Das Schema enthält kein if/then. Die Regel `unknown` → A6 prüft der Guardrail (spec).
- **Fallobjekt und Leakage:** Harte Trigger gehören zum Fallobjekt (Begriff in Abschnitt 3). Damit ist der Typ bei E2/E3 weitgehend vorgegeben. Das ist gewollt: Der Agent interpretiert, die Erkennung bleibt deterministisch. Benenne diese Wirkung im Bericht.
- **Zuordnungswissen im Prompt (Annahme, Entscheid Jan an K4):** Standard ist Variante a, der Prompt enthält die volle Zuordnung Typ/Freitext-Kategorie → zulässige Aktionen aus spec. Begründung: Die Baseline hat dieselbe Tabelle, der Vergleich misst dann nur das Textverständnis. Variante b (nur Katalog und Ermessensrichtlinie) als spätere Ablation vorbereiten (Schalter), nicht im Pilot.
- **Verhalten bei Guardrail-Verstoss (Annahme, Entscheid Jan an K4):** Empfehlung: kein automatischer Neuversuch in v1. Die Ausgabe wird blockiert, der Fall geht an einen Menschen, alles wird protokolliert. `agent_actions_<label>.jsonl` enthält die Rohausgabe des Agenten (für die Bewertung), Guardrail-Treffer werden separat gezählt. Begründe, falls du anders vorschlägst.
- **Umfang:** E2, E3, E6 und Fälle nur mit weichem Trigger. E5 und E7 sind Konzept: `run_agent.py` verarbeitet sie nur mit explizitem Schalter.
- **Modellvorschlag:** Recherchiere den aktuellen Stand (Websuche) und schlage 2 bis 3 lokale Modelle für MacBook Pro M4 Pro, 24 GB RAM, vor. Kriterien: Deutsch, zuverlässige strukturierte Ausgabe in Ollama, Laufzeit für ca. 220 Aufrufe (Pilot, E6-Zusatzlauf, Temperaturlauf), Lizenz. Bedingung aus Abschnitt 15: nicht aus der Familie späterer externer Labeler. Abschätzung der Laufzeit pro Fall angeben. Empfehlung mit Begründung, Entscheid trifft Jan.
- `spec.yaml` und Kontextdokument nicht ändern. Nötige Nachführungen am Ende auflisten (mindestens `meta.llm.model`, Prompt-Variante, Guardrail-Verhalten).
- Bestehende Dateien (`detect.py`, `baseline.py`, `metrics.py`) nicht fachlich ändern. Kleine Erweiterungen für die Agentenauswertung sind erlaubt, wenn die Baseline-Zahlen unverändert bleiben (249/270, 17/17). Melde jede Änderung.
- Technik: Python 3, Standardbibliothek plus pandas, numpy, PyYAML. HTTP über `urllib`. Kein Cloud-LLM.
- Nicht Teil dieses Auftrags: Pilotauswertung (Schritt 5), `demo.py` (Schritt 6), Folien, Implementierung von E5 und E7.

## 5. Arbeitsweise

- Du bist ausführender Agent. Entscheide trifft Jan. Fehlt etwas, triff eine begründete Annahme und kennzeichne sie als "Annahme". Höchstens eine Rückfrage, nur wenn sie blockiert.
- Kritisch bewerten statt validieren: Benenne Schwächen des eigenen Prompts und der Guardrails (z. B. was die Guardrails nicht abfangen können).
- Stil: Deutsch (Schweizer Schreibweise, ss), knapp und strukturiert, keine Gedankenstriche. ASCII in Code und Daten.

## 6. Abschluss (K4)

Stelle die Dateien bereit (inklusive aktualisiertem Repo als Zip `wi-projekt_repo_stand_schritt4.zip`) und schreibe einen Bericht von **höchstens einer Seite**:

1. Was ich entscheiden muss (Modell, Prompt-Variante, Guardrail-Verhalten, weitere), jeweils mit Empfehlung, "ok" muss reichen
2. Was ich prüfen muss (K4: Prompt und Guardrails lesen, 3 Audit-Einträge aus dem Mock-Lauf, Rauchtest mit 3 Fällen lokal nach `ANLEITUNG_lokal.md`)
3. Ergebnis in 3 bis 5 Zahlen (Tests, Mock-Lauf, Guardrail-Treffer)
4. Annahmen und Limitationen in Stichworten

Details gehören in `out/step4_report.md`, nicht in den Chat. Danach stoppst du und wartest auf meine K4-Freigabe. Starte nicht selbst mit Schritt 5.
