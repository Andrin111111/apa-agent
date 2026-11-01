# Schritt 4: Agent-Kern (Bericht zu K4)

Stand 01.11.2026. Grundlage: Kontextdokument v0.4, `spec.yaml` v0.4.0 (beide unverändert). Auftrag: `docs/prompt_schritt4_agent_kern.md`.
Lokales LLM laut Jan: Ollama 0.40.13 installiert, noch kein Modell geladen. Echte LLM-Läufe hat Claude nicht ausgeführt (Sandbox), getestet ist mit Mock-Client und einem Fake-Ollama-Server.

## 1. Ausgangslage

- Reproduziert: `generate_log.py` + `validate_log.py` 43/43, alle Daten bitgleich. `detect.py`, `baseline.py`, `metrics.py`: 249/270 und 17/17, alle Ausgabedateien bitgleich.
- Nach allen Änderungen erneut geprüft: Daten, `detections.csv`, `baseline_actions.jsonl`, `metrics_baseline.*`, `errors_baseline.csv` bitgleich.

## 2. Artefakte

| Datei | Inhalt |
|---|---|
| `src/case_object.py` | Fallobjekt aus `cases.csv`, `event_log.csv` und `detect.evaluate`. Hash über kanonisches JSON (sortierte Schlüssel). |
| `prompts/agent_prompt.md` | Systemprompt v1.0, Variante a (Standard) und b (ohne Zuordnungsblock, Ablation). ASCII. Kommentarzeilen werden nicht gesendet. |
| `src/llm_client.py` | `OllamaClient` (urllib, `format` = JSON-Schema, Temperatur, Seed, Timeout, Digest, Server-Version, Endpunkt chat oder generate, `think` steuerbar), `ReplayClient`, `MockClient`. Dazu `check`: Fallentest, ob das Schema erzwungen wird. |
| `src/guardrails.py` | Alle sechs Regeln aus `spec.guardrails` plus `case_id_match`, spec-getrieben. Ableitung des Ollama-Schemas aus spec. |
| `src/approval.py` | Freigabe batch (alles `pending`) und interaktiv (CLI). Simulierte Ausführung. |
| `src/run_agent.py` | Pipeline, fortsetzbar, abbrechbar. Fallauswahl `pilot`, `e6_full`, `routed`, ID-Liste. E5/E7 nur mit `--include-concept`. |
| `src/audit_view.py` | Lesbare Ansicht des Audit-Logs (K4, K5, Demo). Neu, nicht im Auftrag. |
| `tests/` | 37 Tests (`unittest`), Laufzeit ca. 7 s. |
| `docs/ANLEITUNG_lokal.md` | Setup, Check, Rauchtest, Befehle Schritt 5, Rückgabe in den Chat. |
| `out/audit_log.jsonl` | 102 Einträge: Mock-Lauf (`mock`, Pilot, k = 3, mit Fehlerinjektion) und dessen Replay (`mock_replay`). |
| `out/agent_actions_mock*.jsonl`, `out/agent_run_mock*.json`, `out/metrics_mock*.{md,json}` | Mock-Ausgaben und Auswertung (roh und strikt). |
| `out/metrics_baseline_e6.{md,json}` | Baseline auf allen 80 E6 als Vergleichswert für den E6-Zusatzlauf (59/80). |

## 3. Pipeline

Fallobjekt → `OllamaClient` (Systemprompt, Fallobjekt als JSON, Schema als `format`) → Guardrails → bei Verstoss blockiert, an Mensch → sonst Freigabe (A5 bis A7, bei E7 alles) → simulierte Ausführung → Audit-Log.

Pro Aufruf im Audit-Log: Zeitstempel, Lauf-ID, Label, Fall, Run, Client, Modell, Digest, Temperatur, Seed, Prompt-Version, Variante, Prompt-Hash, Schema-Hash, Fallobjekt-Hash, Fallobjekt selbst, Rohausgabe, Denktext (falls vorhanden), LLM-Metadaten (Tokens, Dauer, `done_reason`, Server-Version), geparste Ausgabe, Guardrail-Ergebnis, Freigabe, ausgeführte, offene und abgelehnte Aktionen, Disposition, Laufzeit.

Dispositionen: `executed`, `pending_approval`, `partially_executed_pending_approval`, `rejected_by_human`, `blocked_to_human`, `llm_error`.

## 4. Fallobjekt

Inhalt: Fallattribute, Freitext, Verlauf bis Stichtag (Aktivität, Zeitstempel, Rolle), Erkennung (`detected_type`, harte Trigger, weicher Trigger), abgeleitete Werte (Kreditausnutzung, Überschreitungsquote, Tage bis Liefertermin, Rechnungsdatum, Fälligkeit, Tage überfällig, Versand, Zahlung, Anzahl Änderungen und Erinnerungen, letzte Aktivität). Grösse ca. 1,5 KB, rund 500 Tokens.

Nie enthalten: Ground Truth, `generator_tag`, Vorlagen-ID, Kategorie, Stil, Personennamen. Test: Alle 1000 Fallobjekte sind frei von verbotenen Schlüsseln und Leak-Zeichenketten.

**Leakage-Wirkung (gewollt, aber zu benennen):** `detected_type` und harte Trigger stehen im Fallobjekt, und Variante a enthält die Zuordnung Typ → Aktion. Bei E2, E3 und Happy Path reduziert sich die Aufgabe damit auf Abschreiben. Ein Agent mit 100 % dort ist kein Befund. Die Typ-Übereinstimmung wird nahe 100 % liegen und ist nicht aussagekräftig. Der einzige Ort, an dem der Agent etwas leistet, das die Regel nicht kann, ist die Einordnung des E6-Freitexts.

## 5. Prompt

- Grösse: Variante a ca. 4,9 KB (rund 1300 Tokens), Variante b ca. 3,9 KB. Mit Fallobjekt rund 2000 Tokens Eingabe, Kontext 8192.
- Ermessensrichtlinie und Katalog wörtlich aus spec (Test). Zuordnung Typ/Kategorie → Aktion wie in spec und Baseline (Variante a).
- E6-Kategorien sind über Bedeutung definiert ("Mangel an Ware oder Lieferung ... auch ohne ausdrückliche Reklamation"), nicht über Schlüsselwörter.

**Schwächen des eigenen Prompts:**
- Kontamination: Claude hat Vorlagen, Keyword-Liste und Prompt geschrieben. Die Kategoriedefinitionen könnten unbewusst auf die indirekten Vorlagen zugeschnitten sein. Das begünstigt den Agenten gegenüber einem realen Einsatz.
- Regel 4 der Ermessensrichtlinie ("im Zweifel an Menschen") konkurriert mit der Zuordnung: Ein vorsichtiges Modell wird bei irrelevanten Texten eher eskalieren statt A3 zu wählen. Erwartbarer Fehlertyp: Enthaltung oder A6 statt A3.
- Die Rolle bei Enthaltung wählt das Modell frei. Fachlich unbestimmt, für die Bewertung ohne Folgen (`unknown` zählt als falsch).
- E3: Der Prompt lässt die Wahl zwischen A4, A2 und beiden offen. Alle sind korrekt (D2), also misst E3 nur Formatdisziplin.

## 6. Guardrails

| Regel | Blockiert | Kann unter erzwungenem Schema auftreten? |
|---|---|---|
| `schema_valid` | ja | nur wenn das Decoding versagt (Ollama-Issue 14645) oder die Ausgabe abgeschnitten wird |
| `action_in_catalog` | ja | nein (Enum im Schema), nur bei Decoding-Ausfall |
| `target_role_exists` | ja | ja: A5/A6 ohne Rolle ist schemakonform |
| `rationale_present` | ja | je nach Umsetzung von `minLength` in Ollama |
| `unknown_requires_A6` | ja | ja (kein if/then im Schema, laut spec) |
| `case_id_match` (G1) | ja | ja |
| `autonomy_respected` | Ausführungsebene | nur bei Programmfehler; geprüft nach jeder Ausführung |

Hinweise (nicht blockierend): `type_mismatch`, `duplicate_action`, `role_on_non_role_action`, `extra_field`, `evidence_unknown_field`.

**Was die Guardrails nicht abfangen:** eine schemakonforme, aber fachlich falsche Aktion. Der teuerste Fehler (A3 Mahnung statt A5 bei indirekter Reklamation, Verstoss gegen Regel 3) passiert alle Guardrails. Ein Policy-Guardrail dafür bräuchte wieder einen Textklassifikator, also die Baseline-Logik, und wäre zirkulär. Nicht umgesetzt. Ebenso nicht prüfbar: ob die Begründung die Entscheidung tatsächlich trägt. Das Schema stellt Belege und Begründung vor die Entscheidung (G3), erzwingt aber keine Treue der Begründung.

**Verhalten bei Verstoss (Empfehlung):** kein automatischer Neuversuch. Begründung: Ein Neuversuch mit Temperatur 0 und gleichem Seed liefert dieselbe Ausgabe. Ein Neuversuch mit Fehlerhinweis ändert den Prompt pro Fall und macht Läufe schwerer vergleichbar. Die Aktionsdatei enthält die Rohentscheidung. Folge: `metrics.py` bewertet standardmässig die Rohentscheidung, auch wenn ein Guardrail blockiert hat. Im Mock-Lauf betrifft das 3 von 11 blockierten Ausgaben (korrekte Aktion, aber z. B. zu kurze Begründung). Deshalb neu `--strict-guardrails`: blockierte Ausgaben zählen als falsch. Empfehlung: beide Zahlen berichten.

## 7. Freigabe

- Batch (alle Läufe in Schritt 5): A5 bis A7 bleiben `pending`, nichts wird automatisch freigegeben. In Schritt 5 wird also keine Freigabe geübt, nur die Weiche gemessen.
- Interaktiv (Demo, Schritt 6): pro Aktion j/n/offen, mit Name und Zeitstempel im Audit-Log.
- Annahme A1: Autonome Aktionen eines Falls laufen sofort, auch wenn eine andere Aktion desselben Falls auf Freigabe wartet. Bei E7 läuft nichts vorab.

## 8. Ergebnisse Mock-Lauf (Pilot, 17 geroutete Fälle, k = 3, Fehlerinjektion `mixed`)

| Kennzahl | Wert |
|---|---|
| Aufrufe | 51 (51/51 Paare) |
| Parsefehler | 2 |
| Blockiert | 11: `schema_valid` 3, `unknown_requires_A6` 2, `target_role_exists` 2, `rationale_present` 2, `action_in_catalog` 1, `case_id_match` 1 |
| Dispositionen | `executed` 21, `pending_approval` 19, `blocked_to_human` 11 |
| Freigabe-Aktionen ausgeführt | 0 (Test über alle Einträge) |
| Aktionskorrektheit pro Run (roh) | 14, 13, 15 von 17 |
| Aktionskorrektheit pro Run (strikt) | 13, 12, 14 von 17 |
| Reproduzierbarkeit | 10 von 17 Fällen (Mock variiert absichtlich) |
| Replay | Aktionsdatei bitgleich zum Mock-Lauf |

Die Mock-Zahlen messen nur die Pipeline, nicht einen Agenten. Der Mock entscheidet mit dem Keyword-Klassifikator und enthält sich ohne Treffer.

## 9. Tests (37, alle bestanden)

Fallobjekt (keine Ground Truth in 1000 Objekten, Hash deterministisch, konsistent mit Erkennung, Verlauf bis Stichtag), jeder Guardrail mindestens einmal ausgelöst, Hinweise nicht blockierend, Schema aus spec ohne if/then, Prompt (Richtlinie wörtlich, Katalog, Variante b, Hash, ASCII), Pipeline (Zählung, alle Ausgabe-Guardrails im Mock-Lauf, Batch führt keine Freigabe-Aktion aus, Audit-Felder, Replay bitgleich, Fortsetzen, Konfigurationsschutz, interaktive Freigabe, E5/E7 ausgeschlossen, `metrics.py` liest Mock-Ausgabe, strikte Auswertung), `OllamaClient` gegen Fake-Server (Payload mit Schema, Temperatur, Seed, `think`; Endpunkt generate; Digest; Transportfehler ohne Aktionszeile).

## 10. Modellvorschlag

Recherche 01.11.2026 (Websuche). Hardware: MacBook Pro M4 Pro, 24 GB. macOS gibt der GPU standardmässig nur einen Teil des Speichers frei (Annahme: rund 16 GB), Modelle über ca. 14 GB sind daher knapp.

| Modell | Download | Familie, Konflikt mit externen Labelern | Lizenz | Hinweise | Schätzung pro Aufruf | 182 Aufrufe |
|---|---|---|---|---|---|---|
| **qwen3.5:9b** (Empfehlung) | 6,6 GB | Alibaba Qwen. Lässt ChatGPT, Gemini, Mistral als Labeler frei | Apache 2.0 | Denkmodell, `--think off`. Bekannter Ollama-Fehler (Schema ignoriert bei `think=false`) laut Issue ab 0.31.2 behoben, Check vor dem Rauchtest | 8 bis 15 s | 25 bis 45 min |
| gemma4:12b | 7,7 GB | Google. Schliesst Gemini als Labeler aus | laut Quelle Apache 2.0, vor Einsatz prüfen | aktuelle Google-Generation, strukturierte Ausgabe | 10 bis 20 s | 30 bis 60 min |
| gpt-oss:20b | 13 GB | OpenAI. Schliesst ChatGPT als Labeler aus | Apache 2.0 | Reasoning nicht abschaltbar (`--think unset`), knapp im Speicher, mehr Ausgabetokens | 10 bis 25 s | 30 bis 75 min |

Nicht empfohlen: qwen3.5:27b und gemma4:31b (17 bis 19 GB), passen nicht sicher in den GPU-Anteil, ca. 14 Token/s.

Begründung Empfehlung: kleinstes Modell mit genug Reserve, schnell genug für 182 Aufrufe in unter einer Stunde, Apache 2.0, und die Familie blockiert keinen der naheliegenden externen Labeler. Erwartung: bei E6 indirekt schwächer als ein grosses Modell. Das ist ein Befund, kein Ausschlussgrund (Kontextdokument Abschnitt 9). Laufzeiten sind Schätzungen aus Benchmarks ähnlicher Hardware (rund 25 bis 40 Token/s für 9B Q4, rund 200 Ausgabetokens, Prompt-Präfix gecacht). Der Rauchtest misst den echten Wert.

## 11. Entscheide für Jan (K4)

| # | Frage | Empfehlung |
|---|---|---|
| 1 | Modell | qwen3.5:9b, Ersatz gemma4:12b, falls der Check scheitert |
| 2 | Prompt-Variante | a im Pilot, b als spätere Ablation (Schalter vorhanden) |
| 3 | Guardrail-Verstoss | kein Neuversuch, blockieren, an Mensch. Bewertung roh und strikt berichten |
| 4 | Denkmodus | aus (`--think off`). Begründung und Belege stehen im Schema vor der Entscheidung (G3) |
| 5 | Temperaturlauf | T = 0,7, Seed pro Run (42, 43, 44), Pilot k = 3 |
| 6 | Zusatz-Guardrail `case_id_match` | blockierend übernehmen |

## 12. Annahmen

| ID | Annahme |
|---|---|
| CO1 | Verlauf mit Uhrzeit (Minuten), weil E5 nach Zeitstempel prüft |
| CO2 | Ressource (Personenname) nicht im Fallobjekt |
| CO3 | Nicht definierte abgeleitete Werte sind null |
| CO4 | `days_to_promised_delivery` null nach Versand (sonst irreführend negative Werte bei E6) |
| G1 | Zusätzlicher blockierender Guardrail `case_id_match` |
| G2 | Hinweise nicht blockierend, nur im Audit-Log gezählt |
| G3 | Schema-Reihenfolge: `case_id`, `key_evidence`, `rationale`, `exception_type`, `actions`. Inhaltlich identisch mit spec. Ob Ollama die Reihenfolge einhält, zeigt der Rauchtest |
| A1 | Autonome Aktionen laufen trotz offener Freigabe anderer Aktionen desselben Falls (ausser E7) |
| R1 | Transportfehler erzeugen keine Aktionszeile, Fall wird beim Fortsetzen wiederholt. Unlesbare Modellausgabe wird als `_parse_error` geschrieben und zählt als falsch |
| R2 | Ein Label gehört zu genau einer Konfiguration (Modell, Temperatur, Seed-Modus, Prompt-Hash, Schema-Hash, Endpunkt, Denkmodus) |
| R3 | Reihenfolge Run für Run, nicht Fall für Fall |
| R4 | Kontext 8192, maximal 1024 Ausgabetokens, `keep_alive` 30 min |
| M5 | `metrics.py --scopes` (all, pilot, e6_full, covered). Standard unverändert |
| M6 | `metrics.py --strict-guardrails` (blockierte Ausgabe = falsch). Standard unverändert |

## 13. Limitationen und kritische Punkte

- Reproduzierbarkeit bei Temperatur 0 und festem Seed: Erwartet sind nahe 100 %. Gemessen wird nur technischer Nichtdeterminismus (Batching, Cache). Aussagekräftig ist erst der Lauf mit T = 0,7 und wechselndem Seed. Mit festem Seed wäre auch T = 0,7 vermutlich identisch.
- E2/E3/Happy Path sind durch Fallobjekt und Variante a vorgegeben (Abschnitt 4). Mehrwert nur bei E6 messbar, dort 80 Fälle aus 34 Vorlagen.
- Mehrere Guardrails sind unter erzwungenem Schema strukturell redundant. Sie schützen gegen Decoding-Ausfälle, nicht gegen falsche Entscheidungen.
- `key_evidence` wird nur als Hinweis gegen existierende Feldpfade geprüft. Freitextbelege ("history: Versenden fehlt") bleiben ungeprüft. Bewertungsraster (K5) bleibt manuell.
- Prompt, Vorlagen und Keyword-Liste vom selben Modell (Claude): Kontaminationsrisiko zugunsten des Agenten.
- Kein Test gegen ein echtes LLM im Chat. Risiko Ollama-Schema-Erzwingung bei Qwen 3.5 ist bekannt und wird vor dem Rauchtest geprüft (`llm_client.py check`).
- Laufzeitschätzungen sind nicht gemessen.

## 14. Geänderte bestehende Dateien

| Datei | Änderung | Wirkung auf Baseline |
|---|---|---|
| `src/metrics.py` | `--scopes`, `--strict-guardrails`, Grund `guardrail_blockiert` in `judge` (nur bei Feld `_blocked`) | keine, alle Baseline-Ausgaben bitgleich |
| `docs/prompt_schritt4_agent_kern.md` | durch ausgefüllte Fassung von Jan ersetzt (Ollama-Stand) | keine |
| `README.md` | Abschnitt Schritt 4 | keine |

`detect.py`, `baseline.py`, `spec.yaml` und Kontextdokument unverändert.

## 15. Nötige Nachführungen (nach K4, nicht ausgeführt)

**`spec.yaml` (v0.5.0):**
1. `meta.llm.model`: gewähltes Modell mit Tag, dazu `think`, `endpoint`, `num_ctx`, `num_predict`.
2. Neuer Abschnitt `agent`: Prompt-Pfad, Version, Variante a, Ablation b, Schema-Reihenfolge (G3).
3. `guardrails`: `case_id_match` ergänzen, Hinweise (G2) und Verhalten bei Verstoss (kein Neuversuch, blockiert, an Mensch).
4. `approval`: Regeln A5 bis A7 und E7, Modi batch und interaktiv, Annahme A1.
5. `pilot.extra_run`: Temperatur 0,7, `seed_mode: per_run`.
6. `evaluation_rules`: Rohbewertung als Standard, strikte Bewertung zusätzlich (M6), Umfänge (M5).

**Kontextdokument (v0.5):**
1. Abschnitt 9: Agent (Fallobjekt, Prompt-Varianten, Denkmodus aus, Schema-Reihenfolge), Guardrails mit `case_id_match`, Freigabe-Modi, Dispositionen.
2. Abschnitt 10: Hinweis zur Aussagekraft der Reproduzierbarkeit bei T = 0, roh vs. strikt.
3. Abschnitt 12/13: Schritt 4 erledigt (nach K4), AP4 und AP5 erledigt. Repo-Struktur: `audit_view.py`, `tests/`, `docs/ANLEITUNG_lokal.md`, `out/step4_report.md`.
4. Abschnitt 14: Entscheide K4 (Abschnitt 11 dieses Berichts), Annahmen CO1 bis CO4, G1 bis G3, A1, R1 bis R4, M5, M6.
5. Abschnitt 15: Modellwahl erledigt, offen: Labeler-Modelle für Iteration 2 nicht aus der Familie des Agentenmodells.
6. Abschnitt 16: Risiken Ollama-Schema-Erzwingung, Kontamination Prompt, Guardrails ohne semantische Prüfung.
