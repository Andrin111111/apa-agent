# WI-Projekt HS 2026, Thema 75: Zwischenpräsentation, Kontext und Plan (lebendes Dokument)

| Feld | Wert |
|---|---|
| Version | 0.7.1 |
| Stand | 01.11.2026 |
| Phase | Vorbereitung Zwischenpräsentation. Schritte 1 bis 6 erledigt (K1 bis K6). Nächster Schritt: 7 (Folien) |
| Ziel | Vorbereitung abgeschlossen bis 01.11.2026 (Vorgabe Jan) |
| Betreuung | Michael Winter (Thema 75); Modulverantwortung Dr. Stefan Koruna (koru@zhaw.ch) |
| Ersetzt | `WI-Projekt_Projektkontext.md` v0.1 (inhaltlich vollständig übernommen und konsolidiert) |
| Begleitdatei | `spec.yaml` v0.5.0 (maschinenlesbare Parameter, Schemas, Katalog) |
| Quellen | `Projektausschreibung`, `WI-Projekt_Termine_und_Vorgaben.md`, `WI-Projekt_Onboarding_Protokoll_21-09-2026.md` |

---

## 0. Hinweise für Claude (Chat und Claude Code)

**Zweck:** Dieses Dokument ist die zentrale Arbeitsgrundlage, um die Zwischenpräsentation zu erstellen: Konzept, Entscheide, Plan, Artefakte und Status. Wer damit weiterarbeitet (anderer Chat im Projekt oder Claude Code), soll den aktuellen Stand ohne Rückfragen kennen.

**Lesereihenfolge:** Abschnitt 12 (Plan, Status, nächster Schritt) und 14 (Entscheidungen) zuerst, dann 5 bis 10 für Inhalte. Für Schritt 7 (Folien) gibt es noch keinen Prompt, Grundlage sind Abschnitt 11 und `docs/briefing_folien_geruest.md`. Ergebnisse: `out/step3_report.md` (Erkennung, Baseline), `out/step4_report.md` (Agent-Kern), `out/step5_report.md` (Pilotläufe, K5), `out/step6_report.md` (Demo, K6). Demo-Ablauf: `docs/demo_drehbuch.md`. Bedienung des Repos: `README.md`.

**Arbeitsmodus:**
- Claude arbeitet als ausführender Agent und liefert Artefakte. Jan kontrolliert an definierten Kontrollpunkten (K1 bis K7). Ohne Freigabe geht Claude nicht über einen Kontrollpunkt hinaus.
- Entscheide trifft nur Jan. Annahmen von Claude werden als "Annahme" gekennzeichnet und im Entscheidungslog geführt.
- Kritisch bewerten statt validieren: Widersprüche, Lücken und Risiken benennen.

**Grenzen:**
- Im Chat kann Claude die Läufe des lokalen LLM nicht selbst ausführen (Sandbox). Jan fährt sie lokal und liefert das Audit-Log zurück.
- In Claude Code kann Claude die Pipeline selbst ausführen, sofern das lokale Modell auf dem Rechner läuft.

**Konventionen:**
- Sprache Deutsch (Schweizer Schreibweise, ss statt ß), knappe und strukturierte Antworten, keine Gedankenstriche (Em-Dashes).
- Umlaute in Dokumenten, ASCII-Schreibweise (ae, oe, ue) in `spec.yaml`, Code und Daten.
- Parameter gelten laut `spec.yaml`, Begründungen laut diesem Dokument. Widerspruch melden und beide Dateien korrigieren.

**Pflege:** Bei jeder Änderung Version und Stand anpassen, Entscheide in Abschnitt 14, Änderungen in Abschnitt 17 und Status in Abschnitt 12/13 nachführen. Nicht entschiedene Vorschläge als "Entwurf", "Annahme" oder "offen" kennzeichnen.

**Repo-Struktur (Stand v0.7.1, * = noch nicht erstellt):** Der Git-Root ist der Projektordner (`apa-agent`). Bis 01.11.2026 lag alles im Unterordner `wi-projekt_repo_stand_schritt4`, ältere Prompts und Konsolen-Logs nennen noch diesen Pfad.
```
README.md  Bedienung und Status
docs/      dieses Dokument, Prompts Schritt 3, 4 und 6, ANLEITUNG_lokal.md, ANLEITUNG_apromore.md,
           demo_drehbuch.md, briefing_folien_geruest.md
tests/     44 Unit-Tests (python -m unittest discover -s tests)
spec/      spec.yaml
src/       generate_log.py, validate_log.py, make_k2.py, extern_tasks.py, keyword_labeler.py,
           detect.py, detect_checks.py, baseline.py, metrics.py, export_apromore.py
           case_object.py, llm_client.py, guardrails.py, approval.py, run_agent.py, audit_view.py,
           step5_eval.py, demo.py
prompts/   extern/ (Prompts für externe Modelle, Iteration 2), agent_prompt.md (v1.2)
data/      event_log.csv, cases.csv, ground_truth.csv, freitext_vorlagen.yaml,
           pilot_sample.csv, labeling_e6_blind.csv, labeling/ (label_items, label_key)
out/       generation_report.md, labeling_report.md, k2_befunde.md, step3_report.md,
           detections.csv, detect_checks.md, baseline_actions.jsonl, metrics_baseline.(md|json),
           errors_baseline.csv, step4_report.md, audit_log.jsonl,
           agent_actions_<label>.jsonl, agent_run_<label>.json, metrics_<label>.(md|json), errors_<label>.csv,
           step5_report.md, step5_tables.md, step5_errors.csv, k5_* (Stichprobe, Prüfprotokoll),
           console_<label>.log, apromore/ (Import für AP7), step6_report.md,
           demo/ (audit_log_demo.jsonl, Aufzeichnungen demo_ref und demo_reserve_c0776, console_*.txt)
slides/    *Zwischenpräsentation (.pptx), Grafiken
```
Labels der Läufe Schritt 5: `pilot_t0`, `e6_t0`, `pilot_t07` (dazu `smoke_v12`, `mock`, `mock_replay`).
Labels der Demo (nur in `out/demo/audit_log_demo.jsonl`): `demo_ref` (Quelle des Replays), `demo_reserve_c0776`, `demo_live_<Zeit>`, `demo_replay_<Zeit>`, Testläufe `demo_test_*` und `demo_snapshot*`.

---

## 1. Rahmenbedingungen

| Punkt | Stand |
|---|---|
| Thema | 75, Agentic Process Automation: KI-gestützte Erkennung und Bearbeitung von Ausnahmefällen in Geschäftsprozessen |
| Zwischenpräsentation | 20 % der Note. Vorgabe: bis SW 07. Genauer Termin nicht bestätigt. |
| Dauer | 20 Minuten (Vorgabe) |
| Schlussabgabe | Januar 2027, 80 % der Note. Genaues Datum zu klären. |
| Leistungsnachweis | Art (Artefakt, Bericht, Präsentation) schriftlich durch Dozierende. Liegt nicht vor. |
| Methodik | Wird von Dozierenden vorgegeben. Noch unbekannt. |
| Gruppe | 3 Personen: Jan plus zwei weitere (Namen offen). Peer Review am Schluss. |
| Aufwand | 6 ECTS pro Person. Modul ohne festen Stundenplan. |
| LLM | Kein API-Key erhalten. Es wird ein lokal betriebenes Modell verwendet. |
| Hardware | MacBook Pro M4 Pro, 24 GB RAM (Apple Silicon). Modellwahl in Schritt 4. |

**Aus dem On-Boarding (21.09.2026):**
- Prozesse laufen selten wie definiert. KI-Agent-Projekte scheitern oft an fehlendem Determinismus, daher muss er kontrolliert werden.
- Agent überwacht Logs, informiert über Abweichungen (Mindestfunktion). Ob er auch entscheiden kann, ist Teil der Untersuchung.
- Mensch als Supervisor vor Prozessschluss (Human-in-the-Loop).
- Abgrenzung: kein Multi-Agent-Framework, zuerst ein einzelner Agent.
- Tools: Apromore (Process Mining, Funktionsweise noch zu verifizieren), P.I.S. Python-Library (Eignung offen). Im Projekt: PM4Py für Erkennung, Apromore nur für Visualisierung.

## 2. Fragestellung

**Hauptfrage:** Kann ein einzelner KI-Agent im Order-to-Cash-Prozess Ausnahmefälle erkennen und darauf reagieren, und wo bringt er gegenüber festen Regeln einen Mehrwert?

**Teilfragen:**
1. Welche Ausnahmefälle lassen sich deterministisch (regelbasiert) lösen, welche erfordern Ermessen?
2. Inwiefern kann der Agent nur informieren, inwiefern darf er entscheiden (Autonomiestufen)?
3. Wie lässt sich das Agentenverhalten so absichern, dass es nachvollziehbar und reproduzierbar bleibt?

**Geplante Erweiterung:** Begrenzung und Verifikation des Handlungsspielraums (Guardrails) als eigener Untersuchungsaspekt.

## 3. Begriffe

| Begriff | Definition im Projekt |
|---|---|
| Fall | Ein Kundenauftrag (Case-ID = Auftragsnummer) |
| Stichtag (`snapshot_time`) | Zeitpunkt, zu dem ein Fall betrachtet und die Trigger ausgewertet werden |
| Deterministischer Fall | Ausnahme, deren Erkennung und Massnahme vollständig durch eine feste Regel bestimmt sind |
| Ermessensfall | Ausnahme, bei der Erkennung oder Massnahme Interpretation (z. B. Freitext) oder Abwägung widersprüchlicher Signale erfordert |
| Trigger | Deterministische Regel, die einen Fall zur Prüfung markiert |
| Fallobjekt | Strukturierte Zusammenfassung eines markierten Falls (Verlauf, Attribute, Freitext, Trigger), Input für den Agenten |
| Handlungskatalog | Abschliessende Liste erlaubter Aktionen des Agenten |
| Autonomiestufe | Legt fest, ob eine Aktion autonom oder nur mit menschlicher Freigabe ausgeführt wird |
| Guardrail | Prüfschicht zwischen Agent und Ausführung (Katalog, Autonomiestufe, Parameter) |
| Enthaltung | Agent kann den Fall nicht einordnen: `exception_type = unknown` und Aktion A6 |
| Zulässige Aktionsmenge | Menge(n) von Aktionen, die für einen Fall als korrekt gelten (Ground Truth) |
| Tagesbasis | Trigger vergleichen Kalenderdaten, die Uhrzeit des Stichtags wird ignoriert |
| Weicher Trigger | Eingegangener Freitext. Legt den Fall dem Agenten vor, ohne ihn als Ausnahme zu markieren |
| Datenabzug | 31.10.2026. Kein Stichtag liegt danach |
| Zielrolle | Erwartete Rolle bei A5/A6 (`expected_target_role` in der Ground Truth) |
| Ermessensrichtlinie | Vorgabe in natürlicher Sprache, an der sich der Agent bei Ermessensfällen orientiert |
| Baseline | Feste Regelzuordnung Ausnahmetyp → Aktion (E6: Keyword-Klassifikator), Vergleichswert für den Agenten |
| Mutantenprüfung | Absichtlich falsche Regelvarianten gegen die Ground Truth. Zeigt, ob die Daten Regelfehler aufdecken würden |

**Hinweis:** "Nicht-deterministisch" bezieht sich auf den Fall, nicht auf das System. Das System soll sich kontrolliert und reproduzierbar verhalten.

## 4. Prozessmodell Order-to-Cash

**Referenzablauf (Happy Path):** Auftrag erfassen → Kreditprüfung → Auftrag bestätigen → Kommissionieren → Versenden → Rechnung stellen → Zahlungseingang → Fall abschliessen

**Zulässige Varianten:** Auftrag ändern, Teillieferung, Zahlungserinnerung/Mahnung.

**Rollen:** Vertrieb, Credit Management, Lager/Logistik, Buchhaltung, Kundendienst.

**Abgrenzung:** O2C ist eigentlich objektzentriert (Positionen, Lieferungen, Rechnungen). Vereinfachung: ein Fall = ein Auftrag. Objektzentriertes Process Mining ist mögliche Erweiterung.

**Stichtag (D1):** Im Offline-Experiment wird jeder Fall zu einem Stichtag betrachtet. Im Betrieb liefe die Erkennung fortlaufend (täglich oder ereignisgesteuert). Die Erkennung ist als Funktion `evaluate(case, now)` gebaut, ein Tages-Loop wäre später ein dünner Wrapper. Nicht evaluiert wird dadurch, wie früh eine Ausnahme erkannt wird. Tägliche Ticks mit Zustandsverwaltung sind Ausblick und Limitation.

## 5. Ausnahmefälle

IDs bleiben stabil, auch wenn Fälle in den Backlog verschoben werden. Details und Parameter: `spec.yaml`.

### 5.1 Pilot (wird im Pilot gegen den Agenten evaluiert)

| ID | Ausnahmefall | Typ | Trigger | Zulässige Aktionen |
|---|---|---|---|---|
| E2 | Kreditlimit überschritten | deterministisch | Auftragswert + offene Posten > Kreditlimit | A6 (Credit Management) |
| E3 | Lieferverzögerung | deterministisch | Zugesagter Liefertermin in < 2 Tagen, nicht versendet | A4, A2 oder A4+A2 (jede Variante korrekt) |
| E6 | Zahlungsverzug mit Kundenkommunikation | Ermessen | Rechnung überfällig, kein Zahlungseingang (Freitext ist Kontext, nicht Trigger) | siehe unten |

**E6, Zuordnung nach Freitext-Inhalt:**

| Inhalt Freitext | Zulässige Aktionen |
|---|---|
| Reklamation / Mangel | A5 Neu zuweisen (Kundendienst) |
| Zahlung avisiert | A0 Keine Massnahme (Wiedervorlage) |
| Zahlungsschwierigkeiten / Ratenwunsch | A6 Eskalieren (Credit Management) |
| Irrelevant oder kein Bezug zur Zahlung | A3 Nächsten Schritt empfehlen (Mahnung) |

Entscheid: "Mahnung stoppen" ist keine eigene Katalogaktion, sondern durch A5 abgedeckt (Fall geht an den Kundendienst, damit läuft keine Mahnung mehr).

### 5.2 Nur Konzept (im Log erzeugt, im Pilot nicht evaluiert)

| ID | Ausnahmefall | Typ | Bemerkung |
|---|---|---|---|
| E5 | Rechnung vor Versand | deterministisch | Conformance Check, Reihenfolge nach Zeitstempel. Zulässig: A6 (Buchhaltung) + A7. Offen: 20 von 40 Fällen nur wenige Stunden Abstand am selben Tag |
| E7 | Zielkonflikt bei mehreren Signalen | Ermessen | Trigger: E2 und E3 gleichzeitig. Kontext: Kundensegment, Höhe der Überschreitung, Zahlungshistorie. Jede Aktion, die eine Lieferung blockiert oder freigibt, braucht Freigabe. Zulässige Mengen per Labeling. |

E5 und E7 werden vom Generator erzeugt (Entscheid), damit die Verteilung aus Abschnitt 8 gültig bleibt. Sie werden aus dem Pilot-Sample ausgeschlossen. Die Ground Truth von E7 bleibt bis zum Labeling leer. Vorrangregel für die Erkennung (Entscheid): Treffen E2 und E3 gleichzeitig zu, gilt der Fall als E7 und nicht zusätzlich als E2 oder E3. Implementierung von E5 und E7 im Agenten folgt nach der Zwischenpräsentation.

### 5.3 Backlog

| ID | Ausnahmefall | Typ | Bemerkung |
|---|---|---|---|
| E1 | Unvollständige Auftragsdaten | deterministisch | Trigger: erfasst, nach 24 h nicht bestätigt, Pflichtattribut fehlt |
| E4 | Wiederholte Auftragsänderung | deterministisch | Trigger: "Auftrag ändern" ≥ 3 |
| E8 | Unbekannte Abweichung | Ermessen | Z. B. Stornierung nach Versand; erwartet: einordnen oder an Mensch übergeben |
| E9 | Preisabweichung Rechnung vs. Auftrag | deterministisch | |

## 6. Handlungskatalog und Autonomiestufen

| ID | Aktion | Autonomie |
|---|---|---|
| A0 | Keine Massnahme / protokollieren | autonom |
| A1 | Information anfordern | autonom |
| A2 | Kunde informieren | autonom |
| A3 | Nächsten Schritt empfehlen | autonom (nur Empfehlung) |
| A4 | Priorisieren | autonom, nachträglich sichtbar |
| A5 | Neu zuweisen (Rolle) | Freigabe nötig |
| A6 | Eskalieren | Freigabe nötig |
| A7 | Fall sperren | Freigabe nötig |

A0 ist Pflicht, damit Fehlalarme messbar sind.

**Enthaltung (D4):** Kann der Agent den Fall nicht einordnen, gibt er `exception_type = unknown` und Aktion A6 aus (Eskalation läuft damit durch die Freigabe). Es gibt kein separates Feld `needs_human`, da es redundant zum Schema wäre. In der Auswertung zählt Enthaltung als nicht korrekt, wird aber als Enthaltungsquote separat ausgewiesen. Das setzt Regel 4 der Ermessensrichtlinie um.

**Approval vs. Enthaltung:** Approval betrifft eine gewählte Katalogaktion (A5 bis A7), die ein Mensch freigibt. Enthaltung bedeutet, dass der Agent gar keine fachliche Aktion wählt.

## 7. Ermessensrichtlinie

Wird dem Agenten als Text mitgegeben. Bewusst nicht als Entscheidungstabelle formuliert (D3: vage, keine Schwellenwerte).

1. Die Kundenbeziehung hat Vorrang, wenn eine Kreditüberschreitung geringfügig ist und der Kunde eine gute Zahlungshistorie hat.
2. Bei erheblicher Überschreitung oder wiederholten Zahlungsverzügen hat die Risikobegrenzung Vorrang.
3. Hinweise des Kunden auf Mängel oder Reklamationen haben Vorrang vor Mahnprozessen.
4. Im Zweifel wird an einen Menschen übergeben, statt autonom zu handeln.

**Designfrage (entschieden):** Je präziser die Richtlinie, desto eher wird E7 wieder deterministisch. Je vager, desto schwieriger die Ground Truth. Entscheid: vage lassen. Begründung: E7 ist im Pilot nur Konzept. Die Wahl wird in der Arbeit dokumentiert und kann in der Schlussphase überprüft werden.

## 8. Datenkonzept (synthetisches Event Log)

**Umfang:** 1000 Fälle, Seed 42, 5905 Events. Fallstart 05.01. bis 30.06.2026, Datenabzug 31.10.2026, Stichtag immer 18:00 (Tagesauswertung).

| Kategorie | Anteil (Richtwert) |
|---|---|
| Happy Path / zulässige Varianten | 70 % |
| E2 | 6 % |
| E3 | 6 % |
| E5 | 4 % |
| E6 | 8 % |
| E7 | 6 % |

**Fallattribute:** Auftragswert, Kundensegment (A/B/C), Kreditlimit, offene Posten, Zahlungshistorie, Zahlungsbedingungen, zugesagter Liefertermin, Freitext (optional), Stichtag.
**Eventattribute:** Aktivität, Zeitstempel, Ressource, Rolle.
**Ground Truth pro Fall:** `exception_type`, `free_text_category`, `allowed_action_sets` (Menge von Mengen), `expected_target_role`, `generator_tag`. Happy Path: `[["A0"]]`.
**E7 im Log:** E7-Fälle sind im Log enthalten, ihr Feld `allowed_action_sets` bleibt bis zum Doppellabeling leer. Sie werden in Pilot und Metriken zu E2/E3 nicht verwendet.
**Bewertung (D5):** exakter Mengenvergleich. Die gewählte Aktionsmenge muss einer erlaubten Menge exakt entsprechen.
**Formate:** CSV. XES nur bei Zeit.

**Rauschen:** 10 % der Happy-Path-Fälle (70) erhalten irrelevante Freitexte, um Fehlalarme zu testen. Gegen Leakage zusätzlich ca. 10 % in E2, E3, E5, E7 (Ground Truth unverändert).

**Varianten:** Happy Path 25 %. Gegen Leakage auch ca. 15 % "Auftrag aendern" in den E-Typen, E6 zusätzlich Teillieferung und ab 11 Tagen Verzug zu 50 % eine Zahlungserinnerung.

**Grenzfälle:** 35 Happy-Path-Fälle (5 %) knapp unter der Schwelle: Summe = Limit (13), Liefertermin = Stichtag + 2 (11), Stichtag = Fälligkeit (11). Die Mutantenprüfung (Schritt 3) bestätigt: Jeder Operatorfehler (`>=`, `<=`, Zeitpunkt statt Tag) würde 11 bis 23 Fehlklassifikationen erzeugen.

**Freitexte:** 40 Vorlagen (10 pro Kategorie, je mind. 3 indirekt bzw. Distraktor), von Claude erzeugt. 20 davon in einer zweiten Runde von Claude neu geschrieben (`source: claude-rev1`, Original in `original_claude`). Limitation: alle Texte stammen von einem Modell. Externe Revision ist für Iteration 2 vorbereitet (`prompts/extern/`).

**Labeling der Ermessensfälle:**
- E6 (Iteration 1, simuliert): 1 Beispiel pro Vorlage (40). Labeler A Claude (nicht unabhängig, 100 %), Labeler B Keyword-Klassifikator (78 %, Fehler nur bei indirekten Texten). Keine Vorlage mehrdeutig. Bericht: `out/labeling_report.md`.
- E6 (Iteration 2): zwei externe Modelle, keines aus der Familie des Agentenmodells.
- E7: Empfehlung mindestens eine menschliche Person, sonst zirkulär (LLM gegen LLM-Urteil). Offen.

## 9. Architektur und Technik

Event Log → Erkennung (Regeln + Conformance, PM4Py) → Fallobjekt → Agent (lokales LLM, strukturierte Ausgabe) → Guardrails → Human-Approval → Aktion (simuliert) → Audit-Log

| Komponente | Verhalten |
|---|---|
| Erkennung | deterministisch, `evaluate(case, events, now)` (`src/detect.py`), regel- und conformance-basiert. Fristen auf Tagesbasis, Reihenfolge (E5) nach Zeitstempel. Zusätzlich weicher Trigger: Fall mit Freitext geht an den Agenten. 370 Fälle geroutet |
| Agent | wählt nur Aktionen aus dem Katalog, Begründung und `key_evidence` als Pflichtfelder (im Schema vor der Entscheidung), JSON-Schema, Temperatur 0, fester Seed, Denkmodus aus. Fallobjekt (`src/case_object.py`) ohne Ground Truth. Prompt `prompts/agent_prompt.md` v1.2, Variante a (volle Zuordnung), Variante b (ohne Zuordnung) als spätere Ablation. Die Ermessensrichtlinie gilt nur bei E7, bei E2, E3, E5, E6 und none ist die Zuordnung bindend |
| Guardrails | Katalogzugehörigkeit, Autonomiestufe, Rolle existiert, Schema, Begründung vorhanden, `unknown` erfordert A6, `case_id_match` (blockierend). Bei Verstoss kein Neuversuch: Ausgabe blockiert, Fall geht an einen Menschen. Fachlich falsche, aber schemakonforme Aktionen fangen die Guardrails nicht ab |
| Human-Approval | Freigabe für A5 bis A7 und für E7 (`src/approval.py`). Modus batch (Schritt 5): nichts wird freigegeben, A5 bis A7 bleiben `pending`. Modus interaktiv (Demo, `src/demo.py`): j/n/offen mit Name und Zeitstempel. Dispositionen: `executed`, `pending_approval`, `partially_executed_pending_approval`, `rejected_by_human`, `blocked_to_human`, `llm_error` |
| Audit-Log | Input, Aktion, Begründung, Guardrail-Ergebnis, Freigabeentscheid, Zeitstempel (`audit_log.jsonl`) |
| Demo | `src/demo.py`: Wrapper um `run_agent.run` (einzige Änderung dort: optionaler Hook `on_decision`), ein Aufruf pro Fall, live oder Replay einer Aufzeichnung, eigenes Audit-Log `out/demo/audit_log_demo.jsonl`. Vorabprüfung `--check` (Version, Digest, Hashes, Schema, Aufwärmen). Anzeige optional mit Baseline (`--baseline`) und Soll (`--truth`, nur Anzeige). Drehbuch `docs/demo_drehbuch.md` |
| Baseline | `src/baseline.py`: Regelzuordnung Ausnahmetyp → Aktion, gleiche Fälle, Ausgabe im Agentenformat. E3: A4+A2. E6: Kategorie per Keyword-Klassifikator. E7: A6 Credit Management (nicht bewertet) |
| Metriken | `src/metrics.py`: wertet jede Aktionsdatei im Agentenformat aus (alle Fälle und Pilot, k Runs, Schema-Vorprüfung) |

**Technik:** Python, PM4Py, lokales LLM (Ollama, Modell `qwen3.5:9b-q4_K_M`, Denkmodus aus, Hardware: MacBook Pro M4 Pro, 24 GB RAM), austauschbarer LLM-Client (Ollama, Replay, Mock), Git-Repository. Streamlit nur bei Zeit. Apromore für Prozesslandkarte (manuell durch Gruppe).

**Modellhinweis:** Der Tag `qwen3.5:9b` lädt auf Apple Silicon einen MLX-Build (nvfp4, 7,6 GB), der strukturierte Ausgabe nicht unterstützt (HTTP 501 "structured output is unavailable", auch mit `--endpoint generate`). Der Build `qwen3.5:9b-q4_K_M` (6,6 GB) erzwingt das Schema (Check bestanden, Ollama 0.40.13). Alle Läufe verwenden den Q4_K_M-Tag.

**Erwartung zum lokalen Modell:** Ein kleines Modell wird bei E6 vermutlich schwächer sein. Das ist ein Befund, die Guardrails gewinnen dadurch an Gewicht. **Ergebnis Schritt 5:** nicht bestätigt. Das 9B-Modell löst 79 von 80 E6-Fällen, auch 31 von 32 indirekte Texte (Einschränkung Kontamination, Abschnitt 10). Die Guardrails haben in 182 Aufrufen nichts blockiert.

## 10. Evaluationskonzept

| Kriterium | Messung |
|---|---|
| Erkennungsgüte | Precision/Recall pro Ausnahmetyp gegen Ground Truth |
| Aktionskorrektheit | Anteil Fälle mit Aktionsmenge exakt in `allowed_action_sets`, bei A5/A6 zusätzlich Zielrolle = `expected_target_role` |
| Fehlalarme | Zwei Ebenen: Erkennung (Grenzfälle dürfen nicht auslösen) und Agent (Happy-Path-Fälle mit Freitext, Aktion ≠ A0) |
| Enthaltungsquote | Anteil Fälle mit `unknown` |
| Reproduzierbarkeit | k Durchläufe pro Fall, Anteil identischer Aktionen. Zusätzlich ein Lauf mit höherer Temperatur. |
| Guardrail-Wirksamkeit | Anzahl abgefangener unzulässiger Aktionen |
| Nachvollziehbarkeit | Bewertungsraster: nennt die Begründung die ausschlaggebende Information korrekt (0 bis 2) |
| Mehrwert | Vergleich Agent vs. Baseline, getrennt nach deterministischen Fällen und Ermessensfällen |

**Pilot (Zwischenpräsentation):** 20 Fälle (4 E2, 4 E3, 6 E6 über alle vier Kategorien, 6 Happy Path davon 3 mit irrelevantem Freitext), k = 3. 17 davon erreichen den Agenten (3 Happy Path ohne Freitext testen nur die Erkennung). **Zusatzlauf (Entscheid K3):** Agent auf allen 80 E6-Fällen, k = 1, weil die Baseline im Pilot alle 6 E6 löst und der Mehrwert dort nicht messbar ist. Volle Evaluation (1000 Fälle, k = 5, Doppellabeling) folgt bis Januar.

**Bewertungsregeln (Schritt 3, `spec.yaml` `evaluation_rules`):** bewertet werden E2, E3, E6 und Happy Path mit Freitext (E5 informativ, E7 nicht). Nenner end-to-end (fehlende Ausgabe = falsch). Aktionen als Menge, Rolle bei A5/A6 muss stimmen. `unknown` zählt als falsch. Fehlalarme der Erkennung sind nur auf allen Fällen messbar (keine Grenzfälle im Pilot).

**Baseline-Ergebnis (Schritt 3):**

| Gruppe | alle Fälle | Pilot |
|---|---|---|
| Erkennung (alle Typen) | 1000/1000, 0 von 35 Fehlalarmen | 20/20 |
| deterministisch (E2, E3) | 120/120 | 8/8 |
| Ermessen (E6) | 59/80 (73,8 %) | 6/6 |
| Happy Path mit Freitext | 70/70 | 3/3 |

E6-Fehler der Baseline nur bei indirekten Texten (21 von 32 falsch, direkt 0 von 43). Erkennung 100 % ist zirkulär (gleiche Spezifikation, gleiches Modell) und kein Erfolgsnachweis.

**Agentenlauf (K4):** Bewertet wird die Rohentscheidung des Agenten, auch wenn ein Guardrail sie blockiert hat. Zusätzlich wird strikt gerechnet (blockierte Ausgabe zählt als falsch). Beide Zahlen werden berichtet. Agentenläufe werden nur auf ihrem Umfang bewertet (Pilot bzw. E6-Zusatzlauf, nicht auf allen Fällen).

**Aussagekraft der Reproduzierbarkeit:** Bei Temperatur 0 und festem Seed ist nahezu 100 % zu erwarten und misst nur technischen Nichtdeterminismus (Batching, Cache). Aussagekräftig ist erst der Lauf mit T = 0,7 und Seed pro Run (42, 43, 44). E2, E3 und Happy Path sind durch Fallobjekt und Variante a vorgegeben, ein Agent mit 100 % dort ist kein Befund. Mehrwert ist nur bei E6 messbar.

**Vorrangregel:** E7-Fälle zählen bei der Erkennungsgüte als E7 (E7 vor E2/E3), damit Precision/Recall von E2 und E3 nicht verfälscht werden.

**Erwartung:** Bei E2 und E3 ist die Baseline mindestens gleich gut (bestätigt: 100 %). Der Mehrwert des Agenten ist bei E6 zu prüfen, insbesondere bei indirekten Texten (E7 später).

**Ergebnis Schritt 5 (Agent, `qwen3.5:9b-q4_K_M`, Prompt v1.2a, Details `out/step5_report.md`):**

| Gruppe | Agent Pilot T = 0 (k = 3) | Agent Pilot T = 0,7 (k = 3) | Baseline Pilot | Agent E6 alle (k = 1) | Baseline E6 alle |
|---|---|---|---|---|---|
| E2 | 12/12 | 12/12 | 4/4 | | |
| E3 | 12/12 | 12/12 | 4/4 | | |
| E6 | 18/18 | 18/18 | 6/6 | 79/80 (98,8 %) | 59/80 (73,8 %) |
| Happy Path mit Freitext | 9/9 | 8/9 | 3/3 | | |

| E6 nach Stil | n | Agent | Baseline |
|---|---|---|---|
| direkt | 43 | 43 | 43 |
| indirekt | 32 | 31 | 11 |
| Distraktor | 5 | 5 | 5 |

- Roh = strikt: 0 von 182 Ausgaben blockiert, 0 Parsefehler, 0 Enthaltungen. Typ-Übereinstimmung 182/182 (Abschreiben von `detected_type`).
- Statistik E6: auf Vorlagenebene Agent besser bei 8 von 34 Vorlagen, schlechter bei 0 (Vorzeichentest p = 0,0078). Fallebene überschätzt (80 Fälle aus 34 Vorlagen).
- Reproduzierbarkeit: T = 0 identisch 17/17, Rohtext bytegleich, auch über Sitzungen (9/9). T = 0,7: Entscheidung identisch 12/17, Streuung bei E3 (freie Wahl A2/A4) und 1 Fehlalarm (C0412: A3 statt A0, autonom ausgeführt). Bei T = 0 wählt das Modell bei E3 immer A2+A4, unabhängig von der Lage.
- Fehler: C0776 (E6 Zahlung avisiert, indirekt): A6 statt A0, geht in die Freigabe. C0412 (T = 0,7, Run 2): A3 statt A0. Beide passieren alle Guardrails.
- Laufzeit: 182 Aufrufe in 20,7 min (6,3 bis 7,1 s pro Aufruf). Hochrechnung volle Evaluation (370 Fälle, k = 5): rund 3,5 h.
- **Einordnung:** Pilot 100 % ist kein Befund (vorgegeben, Prompt an 3 Pilotfällen nachgeschärft). Mehrwert nur bei indirekten E6-Texten. Dort ist "indirekt" als "ohne Schlüsselwort" definiert, das Scheitern der Keyword-Baseline also konstruktionsbedingt. Die Kategoriedefinitionen im Prompt treffen die indirekten Vorlagen fast wörtlich (gleicher Autor), 31/32 ist eine Obergrenze. Test auf fremden Texten folgt in Iteration 2 (D-K5-4).

**Nachvollziehbarkeit (K5):** Stichprobe 18 Begründungen (geschichtet, Seed 42) plus 2 Fehler. Raster 0 bis 2 mit Klarstellungen (D-K5-1): 2 = ausschlaggebende Information korrekt, über die richtige Regel mit der Aktion verbunden, keine falschen Aussagen; 1 = Information korrekt, aber generisch, falscher Regelbezug oder falsche Nebenaussage; 0 = ausschlaggebende Information fehlt oder falsch. Bewertung an Claude delegiert, regelgeleitet (Prüfprotokoll Aussage für Aussage): Mittel 1,56 von 2, Information korrekt 18/18, falsche Aussage 6/18, Ermessensrichtlinie statt Zuordnung 2/18. Zusätzlich widerspricht bei C0317 (T = 0,7) die Begründung der Aktion. Kernaussage: Die Begründung nennt die richtige Information, ist aber kein verlässlicher Beleg dafür, warum entschieden wurde. Nicht unabhängig (Claude ist Autor von Prompt, Texten, Labels).

## 11. Zwischenpräsentation

**Termin:** offen, beim Dozenten bestätigen. **Dauer:** 20 Minuten (Vorgabe). Die Folienzeiten unten ergeben 15 Minuten und bleiben vorerst so (Entscheid Jan 01.11.2026). Ob die Zeit aufgeht, zeigt der Probevortrag (K7), danach Zeiten anpassen.

| Folie | Inhalt | Zeit | Quelle |
|---|---|---|---|
| 1 | Ausgangslage und Problem | 1,5 min | Abschnitt 1, 2 |
| 2 | Fragestellung und Teilfragen | 1 min | Abschnitt 2 |
| 3 | Referenzprozess und Ausnahmefälle (deterministisch vs. Ermessen) | 2 min | Abschnitt 4, 5, Prozessgrafik (PM4Py/Apromore) |
| 4 | Handlungskatalog und Autonomiestufen | 1 min | Abschnitt 6 |
| 5 | Architektur und Determinismus-Konzept | 2 min | Abschnitt 9, Architekturgrafik |
| 6 | Demo: E2 C0902 (Eskalation mit Freigabe), E3 C0537 (autonome Priorisierung), E6 C0244 (indirekte Reklamation, Ermessen). Reserve C0776 (echter Fehler, Freigabe fängt ihn ab) | 4 min | `src/demo.py`, `docs/demo_drehbuch.md`, `out/demo/`. Fallback: Replay, dann Aufzeichnung |
| 7 | Evaluationskonzept und Pilot-Zwischenstand | 2 min | Abschnitt 10, Formulierung `out/step5_report.md` Abschnitt 9 (D-K5-5) |
| 8 | Plan bis Januar, offene Fragen | 1,5 min | Abschnitt 12, 15 |

Summe Folienzeiten: 15 min, Rest 5 min (Puffer, Übergänge, Q&A je nach Vorgabe). Plus Titelfolie. Sprechnotizen und Q&A-Liste gehören zum Folienartefakt.

**Erwartete Fragen:**
- Zirkularität: eigene Ausnahmen, eigene Regeln, wie ist die Evaluation aussagekräftig?
- "Das kann ERP schon": warum Fokus auf Kombination mehrerer Signale und Freitext?
- Determinismus: wie bleibt es kontrolliert, wenn ein LLM entscheidet?
- Warum ein lokales, kleines Modell, und was bedeutet das für die Aussagekraft?
- Warum nur drei Ausnahmetypen im Pilot?
- Wie entsteht die Ground Truth bei Ermessensfällen?

## 12. Arbeitsplan Zwischenpräsentation und Status

**Vertikaler Schnitt:** E2, E3, E6 end-to-end. E5 und E7 als Konzept.

| # | Schritt | AP | Wer | Artefakte | Kontrollpunkt | Status |
|---|---|---|---|---|---|---|
| 0 | Klärung (Termin, Nachweis, Methodik, LLM, Rhythmus). Mit Annahmen weiterarbeiten. | - | Claude: Entwurf | Mail-Entwurf an Winter | - | entfällt (Entscheid Jan): Fragen werden nach der Zwischenpräsentation geklärt |
| 1 | Spezifikation einfrieren | AP1 | Claude | `spec.yaml` v0.2.3, dieses Dokument | K1: Entscheide D1 bis D5 getroffen, Spezifikation gegenlesen | erledigt (Freigabe Jan, Go für Schritt 2) |
| 2 | Log-Generator | AP2 | Claude | `generate_log.py`, `event_log.csv`, `cases.csv`, `ground_truth.csv`, `freitext_vorlagen.yaml` | K2: Stichprobe 10 Fälle pro Typ (bei E7 nur Plausibilität der Attribute, keine Ground Truth), Verteilung prüfen, Teil der Freitexte überarbeiten | erledigt. Stichprobe, Freitext-Revision und Labeling durch Claude (Entscheid Jan). K2 freigegeben |
| 3 | Erkennung und Baseline | AP3, AP6 | Claude | `detect.py`, `detect_checks.py`, `baseline.py`, `metrics.py`, `step3_report.md` | K3: Precision/Recall, 5 Fehlerfälle prüfen | erledigt (K3 freigegeben 01.11.2026) |
| 4 | Agent-Kern | AP4, AP5 | Claude | `case_object.py`, `agent_prompt.md`, `llm_client.py`, `guardrails.py`, `approval.py`, `run_agent.py`, `audit_log.jsonl`, Modellvorschlag | K4: Prompt, Guardrails und Modellwahl entscheiden, 3 Audit-Einträge prüfen | erledigt (Entscheide Jan 01.11.2026, Rauchtest 6/6 bestanden mit Prompt v1.2) |
| 5 | Pilotlauf (20 Fälle, k = 3) und E6-Zusatzlauf (80 Fälle, k = 1) | AP6 | Claude (Läufe und Auswertung in Claude Code) | `step5_eval.py`, `step5_report.md`, `k5_*` | K5: Begründungsraster stichprobenartig bewerten | erledigt (Läufe 182/182, K5 an Claude delegiert, Entscheide D-K5-1 bis D-K5-5) |
| 6 | Demo (E2, E3, E6) | AP8 | Claude | `demo.py`, `demo_drehbuch.md`, `out/demo/`, `step6_report.md`, Aufzeichnung (Jan) | K6: Probelauf bei Jan | erledigt (K6: Probelauf live und Replay bei Jan bestanden). Bildschirmaufzeichnung offen (Jan, wenn die Demo final ist) |
| 7 | Folien | AP8 | Claude | `.pptx`, Sprechnotizen, Q&A | K7: inhaltlich und Probevortrag | offen |
| 8 | Dieses Dokument nachführen (AP-Status, Logs) | - | Claude | aktualisierte Datei | kurz gegenlesen | laufend (v0.7 nach K6) |

**Reihenfolge:** 1 → 2 → 3 → 4 → 5 → 6. Folien-Gerüst und Grafiken nach K1 parallel, Finalisierung nach dem Pilot.

**Scope-Cut:**

| Muss | Kann | Verschieben |
|---|---|---|
| Schritte 0 bis 4, 6, 7, Mini-Pilot | E5, XES-Export, Streamlit | Implementierung E5 und E7, Doppellabeling, volle Evaluation mit k = 5 |

**Aufgaben der Gruppe (nur manuell):**

| Wann | Aufgabe | Ergebnis |
|---|---|---|
| Sofort | Apromore Academic Alliance Zugang beantragen, "Process Mining 101" durchgehen, Funktionsweise kurz verifizieren | Zugang, 3 Sätze Funktionsbeschreibung |
| Sofort | Ollama auf dem MacBook Pro M4 Pro (24 GB) installieren, Modell laden | Lauffähiges lokales LLM |
| Nach K2 | `event_log.csv` in Apromore importieren, Prozesslandkarte und Variantenansicht als Screenshot exportieren | Grafiken (AP7) |
| Iteration 2 (optional) | Externe Revision und externes Labeling nach `prompts/extern/ANLEITUNG.md`. Die Datei `labeling_e6_blind.csv` (15 Fälle) bleibt als Reserve für ein menschliches Labeling | Unabhängige Labels |
| Ab K7 | Folien lesen, Rollen und Redezeiten verteilen, Probevortrag | Sprechplan, Zeitcheck |

### So geht es weiter (Stand 01.11.2026, nach K6)

| # | Wer | Was | Dauer |
|---|---|---|---|
| 1 | Jan | Neuen Chat für Schritt 7 starten. Grundlage: Abschnitt 11, `docs/briefing_folien_geruest.md`, `out/step5_report.md` Abschnitt 9, `out/step6_report.md`. Ein Prompt für Schritt 7 fehlt noch | 5 min |
| 2 | Claude | Schritt 7: Folien, Sprechnotizen, Q&A (Folie 6 nach `docs/demo_drehbuch.md`, Folie 7 nach D-K5-5) | |
| 3 | Jan | Bildschirmaufzeichnung der Demo, sobald sie final ist (`docs/demo_drehbuch.md` Abschnitt 5) | 15 min |
| 4 | Jan, Gruppe | K7: Folien prüfen, Probevortrag mit Live-Demo und Stoppuhr | |
| parallel | Gruppe | Apromore-Import nach `docs/ANLEITUNG_apromore.md` (AP7), Screenshots für Folie 3. Folien-Gerüst nach `docs/briefing_folien_geruest.md`, falls noch offen | 45 bis 60 min |

## 13. Arbeitspakete (Übersicht)

| AP | Inhalt | Verantwortlich | Status |
|---|---|---|---|
| AP1 | Referenz-BPMN, Ausnahmetypen, Katalog, Richtlinie finalisieren | Jan + Claude | erledigt (Spezifikation v0.2.3) |
| AP2 | Log-Generator mit Labels und Freitext-Vorlagen | Claude, Review Jan | erledigt (K2) |
| AP3 | Erkennungsmodul (Trigger E2, E3, E6, Conformance) | Claude | erledigt (K3) |
| AP4 | Agent: Prompt, Tool-Schema, Fallobjekt-Format | Claude | erledigt (K4) |
| AP5 | Guardrails, Approval-Schritt, Audit-Log | Claude | erledigt (K4) |
| AP6 | Baseline und Kennzahlen, Pilotauswertung | Claude | erledigt (K5) |
| AP7 | Apromore-Visualisierung für Folien | Gruppenmitglieder 2 und 3 | in Arbeit (Export und Anleitung vorbereitet, Import durch Gruppe offen) |
| AP8 | Demo und Folien Zwischenpräsentation | Claude erstellt, Gruppe übt | in Arbeit (Demo erledigt, K6; Folien offen) |

Status-Werte: offen / in Arbeit / erledigt / zurückgestellt. Referenz-BPMN: wird als Prozessgrafik umgesetzt (PM4Py oder Diagramm).

## 14. Entscheidungslog

| Datum | Entscheid | Begründung | Status |
|---|---|---|---|
| 25.10.2026 | Prozess: Order-to-Cash | Vertraut aus früheren Studienmodulen | entschieden |
| 25.10.2026 | Fall = Auftrag (nicht objektzentriert) | Komplexität für Prototyp begrenzen | entschieden |
| 25.10.2026 | Synthetisches Log mit Ground Truth | Vorgabe Ausschreibung, messbare Evaluation | entschieden |
| 25.10.2026 | Prototyp v1: E2, E3, E5 deterministisch, E6, E7 Ermessen | Mehrwert des Agenten nur bei Ermessensfällen prüfbar | entschieden, für Pilot eingegrenzt (siehe unten) |
| 25.10.2026 | Erkennung deterministisch, LLM nur für Interpretation und Auswahl | Kontrolle des Determinismus (On-Boarding) | entschieden |
| 25.10.2026 | Einzelagent, kein Multi-Agent-Framework | Abgrenzung aus On-Boarding | entschieden |
| 31.10.2026 | Lokales LLM statt API | Kein API-Key erhalten | entschieden |
| 31.10.2026 | Pilot-Scope E2, E3, E6. E5 und E7 nur Konzept | Zeit bis zur Zwischenpräsentation | entschieden |
| 31.10.2026 | Apromore und Ollama-Setup durch die anderen zwei Gruppenmitglieder | Entlastung, manuelle Aufgaben | entschieden |
| 31.10.2026 | D1: ein Stichtag pro Fall, `evaluate(case, now)` zeitparametrisiert | Einfachheit, Ground Truth eindeutig, Tages-Loop später möglich | entschieden |
| 31.10.2026 | D2: E3 erlaubt A4, A2 oder A4+A2 | Lesart "jede Variante korrekt" | entschieden |
| 31.10.2026 | D3: Ermessensrichtlinie vage, keine Schwellenwerte | E7 im Pilot nur Konzept | entschieden |
| 31.10.2026 | D4: Kein Feld `needs_human`. Enthaltung = `unknown` + A6 | Redundanz vermeiden, Enthaltung messbar | entschieden |
| 31.10.2026 | D5: Aktionskorrektheit mit exaktem Mengenvergleich | Teilmenge wäre zu milde | entschieden |
| 31.10.2026 | Annahme: Präsentationsdauer 15 Minuten | Keine Vorgabe erhalten | ersetzt durch Vorgabe 20 Minuten (01.11.2026) |
| 01.11.2026 | Präsentationsdauer 20 Minuten. Folienzeiten bleiben vorerst bei 15 min, Prüfung im Probevortrag | Vorgabe; Verteilung erst nach Zeittest | entschieden |
| 31.10.2026 | "Mahnung stoppen" ist durch A5 abgedeckt, keine eigene Aktion | Nicht im Katalog, im Prototyp nur Simulation | entschieden |
| 31.10.2026 | Generator erzeugt alle fünf Typen inkl. E7, Pilot nur E2, E3, E6 | Verteilung aus Abschnitt 8 bleibt gültig | entschieden |
| 31.10.2026 | Vorrangregel E7 vor E2/E3 in der Erkennung. E7-Ground-Truth bleibt bis Labeling leer. | Verhindert verfälschte Metriken zu E2 und E3 | entschieden |
| 31.10.2026 | Mail an Winter wird nicht gesendet, offene Fragen nach der Zwischenpräsentation klären | Priorität auf Prototyp und Folien | entschieden |
| 31.10.2026 | Annahme: Freitexte durch Claude erzeugt, Jan überarbeitet einen Teil | Agent ist anderes Modell, Bias reduzieren | ersetzt durch Entscheid 01.11.2026 |
| 01.11.2026 | Trigger auf Tagesbasis (Datum des Stichtags, Uhrzeit ignoriert) | Bei Zeitpunktvergleich kippen 24 Fälle (Grenzfälle). Mutantenprüfung Schritt 3 ergibt 23 (E3, E6) | entschieden, präzisiert durch K3 (gilt für Fristen) |
| 01.11.2026 | Eingegangener Freitext ist weicher Trigger: Fall geht an den Agenten | Sonst sieht der Agent keine Rauschfälle, Fehlalarm-Messung wäre wertlos | entschieden |
| 01.11.2026 | Ground Truth enthält `expected_target_role`, Bewertung prüft Rolle bei A5/A6 | Sonst zählt eine falsche Rolle als korrekt. Umsetzung in Schritt 2 vorgezogen | entschieden |
| 01.11.2026 | Happy Path: zulässige Aktionsmenge `[["A0"]]` | Folgt aus der Fehlalarm-Metrik | entschieden |
| 01.11.2026 | Freitext-Revision (20 von 40) und E6-Labeling durch Claude statt extern. Externe Variante für Iteration 2 vorbereitet | Tempo bis zur Zwischenpräsentation | entschieden, Limitation |
| 01.11.2026 | Zweiter Labeler: Keyword-Klassifikator (kein fremdes LLM verfügbar) | Deterministisch, unabhängig vom Generator, zugleich Baseline-Kandidat für E6 | Annahme |
| 01.11.2026 | Generator: Stichtag 18:00, Beträge ganze CHF, Fallstart bis 30.06.2026, Datenabzug 31.10.2026, keine Feiertage | Eindeutige Grenzfälle, keine Daten "aus der Zukunft" | Annahme |
| 01.11.2026 | Varianten und irrelevanter Freitext auch in E-Typen, Zahlungserinnerung in E6 | Typ soll nicht aus Nebenmerkmalen erratbar sein | Annahme (Abweichung vom Schritt-2-Prompt) |
| 01.11.2026 | K2 freigegeben | Befunde zur Kenntnis genommen | entschieden |
| 01.11.2026 | K3 freigegeben | Erkennung, Baseline, Metriken abgenommen | entschieden |
| 01.11.2026 | D-K3-1: Pilot bleibt unverändert, zusätzlich Agent auf allen 80 E6-Fällen (k = 1) | Baseline löst im Pilot alle 6 E6, Mehrwert dort nicht messbar. Keine Auswahl nach Baseline-Fehlern (Selektionsverzerrung) | entschieden |
| 01.11.2026 | D-K3-2: Tagesbasis gilt für Fristen (E3, E6), Reihenfolge (E5) nach Zeitstempel | Wörtliche Tagesbasis verpasst 20 von 40 E5 | entschieden |
| 01.11.2026 | D-K3-3: Baseline E3 = A4+A2 (B1), Baseline E7 = A6 Credit Management (B2), Baseline enthält sich nie (B3) | Feste Regel kennt Grund der Verzögerung nicht; E7 ohne Abwägungslogik an Mensch | entschieden |
| 01.11.2026 | Bewertungsregeln M1 bis M4 (Umfang, Nenner end-to-end, Mengenvergleich mit Rolle, `unknown` falsch) | Konsistente Auswertung für Baseline und Agent | entschieden (K3) |
| 01.11.2026 | AN1: nur Events bis `now`. AN2: E2 ohne Stadiumsbedingung. AN3: Teillieferung ≠ Versenden. AN5: Mehrfachtrigger-Priorität E5 > E6 > E2 > E3. AN6: `evaluate(case, events, now)` | Spec-Lücken nicht still lösen; im Log ohne Wirkung | Annahme (K3 akzeptiert) |
| 01.11.2026 | D-K4-1: Modell `qwen3.5:9b`, lokal als Build `qwen3.5:9b-q4_K_M` | Der Standard-Tag lädt einen MLX-Build ohne Schema-Erzwingung (HTTP 501). Gleiches Modell, anderer Build. Familie Qwen lässt ChatGPT, Gemini, Mistral als Labeler frei | entschieden |
| 01.11.2026 | D-K4-2: Prompt-Variante a im Pilot, b als spätere Ablation | Vergleich mit Baseline misst nur Textverständnis | entschieden |
| 01.11.2026 | D-K4-3: Bei Guardrail-Verstoss kein Neuversuch, blockiert, an Mensch. Bewertung roh und strikt | Neuversuch bei T = 0 liefert dieselbe Ausgabe, mit Hinweis bräuchte es einen anderen Prompt pro Fall | entschieden |
| 01.11.2026 | D-K4-4: Denkmodus aus | Begründung und Belege stehen im Schema vor der Entscheidung (G3) | entschieden |
| 01.11.2026 | D-K4-5: Temperaturlauf T = 0,7 mit Seed pro Run (42, 43, 44) | Bei festem Seed wäre auch T = 0,7 identisch | entschieden |
| 01.11.2026 | D-K4-6: `case_id_match` als blockierender Guardrail | Verwechslungen abfangen | entschieden |
| 01.11.2026 | D-K4-7: Prompt v1.1 und v1.2: Ermessensrichtlinie gilt nur bei E7, bei E3 sind nur A4 und A2 zulässig | Rauchtest mit v1.0: C0317 (E2) A0 statt A6, C0067 (E3) A3 statt A4/A2. Mit v1.1 eskaliert das Modell bei C0067 zu A6, mit v1.2 stimmen alle drei Fälle in beiden Runs. Die Rauchtestfälle sind Pilotfälle: der Prompt wurde an ihnen nachgeschärft, Limitation | entschieden |
| 01.11.2026 | Annahmen K4: CO1 bis CO4 (Fallobjekt), G1 bis G3 (Guardrail `case_id_match`, nicht blockierende Hinweise, Schema-Reihenfolge), A1 (autonome Aktionen laufen sofort), R1 bis R4 (Läufe, ein Label pro Konfiguration), M5, M6 (Bewertung) | Details in `out/step4_report.md` | Annahme |
| 01.11.2026 | D-K5-1: Raster K5 als eine Zahl 0 bis 2, falscher Regelbezug oder falsche Nebenaussage höchstens 1 | Eine Zahl genügt für die Zwischenpräsentation, Klarstellungen machen die Bewertung reproduzierbar. Treue als eigenes Kriterium für die Schlussabgabe | entschieden |
| 01.11.2026 | D-K5-2: `target_role` an A3/A4 bleibt nicht blockierender Hinweis, zählt nicht als Fehler | Keine Regeländerung nach Sicht der Ergebnisse, ohne fachliche Wirkung | entschieden |
| 01.11.2026 | D-K5-3: Typ-Aktions-Guardrail (Aktionen gegen `detected_type`) nur als Ausblick | Zeit. Nicht zirkulär, hätte C0412 (T = 0,7) blockiert, C0776 nicht | entschieden |
| 01.11.2026 | D-K5-4: Test auf fremden Texten erst in Iteration 2 | Zeit. Kontamination bleibt Limitation und gehört auf die Folie | entschieden, Limitation |
| 01.11.2026 | D-K5-5: Folie 7 berichtet E6 getrennt nach direkt/indirekt mit Einschränkung (Obergrenze, gleicher Autor) | Gesamtzahl 98,8 % wäre ohne Einschränkung angreifbar | entschieden |
| 01.11.2026 | K5-Bewertung an Claude delegiert, regelgeleitet (Prüfprotokoll Aussage für Aussage) | Tempo bis zur Zwischenpräsentation | entschieden, Limitation (nicht unabhängig) |
| 01.11.2026 | Annahmen Schritt 5: S1 venv ausserhalb des Repos (Python 3.15). S2 K5-Stichprobe geschichtet nach Typ, Kategorie und Stil, eine Vorlage höchstens einmal, Fehler als Zusatzitems ausserhalb des Mittelwerts. S3 Vergleich Agent/Baseline zusätzlich auf Vorlagenebene (Vorzeichentest). S4 Läufe nacheinander, nicht parallel | Details in `out/step5_report.md` | Annahme |
| 01.11.2026 | K6: Demo-Fälle C0902 (E2), C0537 (E3), C0244 (E6), Reserve C0776. Ehrlichkeitspunkt: Begründung bei C0902 behauptet "automatische Weiterleitung", das System hält zur Freigabe an. Auf dem Bildschirm dauerhaft "Begründung nicht geprüft" und "Guardrails prüfen Form, nicht fachliche Richtigkeit". Vergleich mit Baseline und Soll (`--baseline --truth`). Kein simulierter Fehler (Mock) | Keine Rauchtestfälle. Fälle stabil, live 16/16 bytegleich mit der Evaluation. Grenze echt statt inszeniert | entschieden (Empfehlung Schritt 6, Probelauf von Jan freigegeben) |
| 01.11.2026 | Annahmen Schritt 6: D6-A1 Demo-Dateien in `out/demo/`. D6-A2 Replay aus eigener Live-Aufzeichnung `demo_ref` (bytegleich mit Evaluation). D6-A3 ein `run()`-Aufruf pro Fall, Label mit Zeitstempel. D6-A4 Timeout 30 s in der Demo. D6-A5 `--truth` zeigt Ground Truth nur in der Anzeige. D6-A6 Reihenfolge E2, E3, E6. D6-A7 `--check` wärmt an C0556 auf (ohne Audit-Eintrag), Modell 90 min geladen. D6-A8 Testläufe bleiben im Demo-Audit-Log. D6-A9 `apa-agent/apa-agent` ist ein älterer Prototyp, nicht massgeblich. Dazu: optionaler Hook `on_decision` in `run_agent.run` (Standard None) | Details in `out/step6_report.md` Abschnitt 2 und 6 | Annahme |
| 01.11.2026 | Repo vor dem Merge mit `main` umgebaut: Inhalt von `wi-projekt_repo_stand_schritt4` eine Ebene nach oben (Git-Root), früher Prototyp `apa-agent/` (agent.py, config.py, daten/) entfernt | Eine Struktur ohne Altlasten. Der Prototyp bleibt in der Git-Historie (`main`, Commit "Agent-Gerüst") | entschieden (Jan) |

## 15. Offene Punkte und Fragen an den Dozenten

- [ ] Fragen an Winter nach der Zwischenpräsentation klären (Entscheid Jan, Mail-Entwurf nicht gesendet): Termin, schriftlicher Leistungsnachweis, Methodik (z. B. Design Science Research), LLM lokal erlaubt und Key später, Meetingrhythmus und Sprints
- [x] Modellwahl für das lokale LLM: `qwen3.5:9b-q4_K_M` (D-K4-1)
- [x] Spezifikation gegengelesen (K1), Go für Schritt 2 erteilt
- [x] K2 freigegeben
- [x] K3 freigegeben (Erkennung, Baseline, Metriken)
- [ ] E7-Labeling: Methode festlegen (Empfehlung: mindestens eine menschliche Person)
- [x] Spec: E2 ohne Stadiumsbedingung, E3 bei Teillieferung als Annahme gelöst (AN2, AN3)
- [ ] E5 vor Umsetzung klären: Soll A7 nach Versand, Rechnung wenige Stunden vor Versand am selben Tag (`spec.yaml`, `detection.open_points`)
- [x] Schritt 4: Zuordnungswissen Variante a, Guardrail-Verstoss ohne Neuversuch (D-K4-2, D-K4-3)
- [x] K4: Entscheide getroffen, Rauchtest bestanden (Prompt v1.2)
- [x] Schritt 5: Läufe, Auswertung, K5 (D-K5-1 bis D-K5-5)
- [x] K6: Demo-Probelauf bei Jan bestanden (live und Replay)
- [ ] Bildschirmaufzeichnung der Demo (Jan), sobald die Demo final ist
- [ ] Labeler-Modelle für Iteration 2 dürfen nicht aus der Familie des Agentenmodells (Qwen) stammen
- [ ] Iteration 2: Agent auf fremden Texten testen (Hold-out). Achtung: Revision nach `prompts/extern/` ändert die Vorlagen, danach alle Auswertungen neu rechnen. Ein separater Hold-out-Satz wäre weniger invasiv
- [ ] Schlussabgabe: K5 mit mindestens einem menschlichen Rater, Treue als eigenes Kriterium
- [ ] Genaues Datum Schlussabgabe Januar 2027
- [ ] Namen der anderen zwei Gruppenmitglieder und Verteilung der Aufgaben ab K7
- [ ] Datenschutz: bei synthetischen Daten voraussichtlich unkritisch, bei Dozent bestätigen

## 16. Risiken und kritische Punkte

| Risiko | Gegenmassnahme |
|---|---|
| Zirkuläre Evaluation (eigene Ausnahmen, eigene Regeln) | Testszenarien durch Person ohne Kenntnis der Regeln. Rauschen und mehrdeutige Fälle. Als Limitation nennen. |
| Unscharfe Ground Truth bei Ermessensfällen | Zulässige Aktionsmengen, unabhängiges Doppellabeling |
| LLM trotz Temperatur 0 nicht deterministisch | Deterministische Hülle, fester Seed, Reproduzierbarkeit messen |
| Kleines lokales Modell schwach bei E6 | Als Befund ausweisen, Guardrails und Enthaltung betonen, Modellwahl nach Hardware |
| Laufzeit auf lokaler Hardware | Pilot auf 20 Fälle begrenzen, Läufe abbrechbar und fortsetzbar |
| Demo scheitert live (Ollama hängt, Modell kalt, Beamer) | `demo.py --check` vor dem Termin (Version, Digest, Hashes, Aufwärmen), Timeout 30 s, Replay ohne LLM (bytegleich, Start unter 1 s), Aufzeichnung, Notfallplan in `docs/demo_drehbuch.md` |
| Realitätsnähe (ERP automatisiert Kreditprüfung bereits) | Fokus auf Kombination mehrerer Signale und Freitext begründen |
| Zu viel Zeit in Apromore oder UI | Apromore nur manuell durch Gruppe, Demo minimal halten |
| Freitext-Bias (alle Texte von Claude, Labeling durch Claude nicht unabhängig) | Als Limitation nennen. Keyword-Labeler als unabhängige Prüfung, externe Revision und Labeling in Iteration 2 |
| Restleakage: Eventanzahl und letzte Aktivität verraten teils den Typ | Prozessbedingt, als Limitation nennen. Erkennung ist ohnehin deterministisch |
| Vorgaben (Methodik, Leistungsnachweis) ändern Struktur | Früh klären, Dokument entsprechend anpassen |
| Pilot bei E6 nicht repräsentativ (Baseline 6/6) | Zusatzlauf auf allen 80 E6 (D-K3-1) |
| Baseline zu stark (Keyword-Liste in Kenntnis der Vorlagen) | Als Limitation nennen; Vergleich wird eher konservativ |
| E6-Fälle teilen Vorlagen (80 Fälle aus 34 Vorlagen) | Auswertung zusätzlich pro Vorlage bzw. Stil, als Limitation nennen |
| Ollama erzwingt das Schema nicht (MLX-Build: HTTP 501) | `llm_client.py check` vor jedem Lauf, Tag `qwen3.5:9b-q4_K_M` verwenden |
| Kontamination: Prompt an Pilotfällen nachgeschärft (v1.0 bis v1.2) | Als Limitation nennen. Auswertung zusätzlich auf dem E6-Zusatzlauf (80 Fälle), der nicht zum Tuning diente |
| Guardrails ohne semantische Prüfung: schemakonforme, aber falsche Aktionen passieren | Roh und strikt berichten, Fehler nach Typ auswerten. Policy-Guardrail wäre zirkulär (Baseline-Logik) |
| Kleines Modell ignoriert Zuordnung und zitiert die Ermessensrichtlinie falsch (v1.0, v1.1 beobachtet) | Geltungsregel im Prompt, Befund berichten. Schritt 5: Aktionen korrekt, aber Richtlinie in 15 von 32 Begründungen zu Reklamationen zitiert |
| Begründung nicht treu: klingt sicher, auch wenn falsch, widerspricht teils der Aktion (C0317 bei T = 0,7) | Begründung nicht als Erklärung der Entscheidung verkaufen. K5-Befund berichten, Freigabe bleibt die Kontrolle |
| Keine Enthaltung beobachtet (0 von 182): Regel 4 wird nie über `unknown` umgesetzt | Als Befund nennen. Unsicherheitserkennung ist nicht gezeigt |
| Autonome Fehlaktion bei T > 0 (A3 statt A0 auf Happy Path, ohne Freigabe ausgeführt) | Produktiv T = 0. Typ-Aktions-Guardrail als Ausblick (D-K5-3) |
| Kontamination konkretisiert: Kategoriedefinitionen im Prompt treffen die indirekten Vorlagen fast wörtlich | E6-Ergebnis als Obergrenze berichten (D-K5-5), Hold-out in Iteration 2 (D-K5-4) |
| Publikum hält die drei Demo-Fälle für Evidenz (alle zeigen "korrekt") | Ansage "Illustration, kein Beleg", Reserve C0776 (echter Fehler), Verweis auf Folie 7 |
| Ollama-App aktualisiert sich vor dem Termin, Ausgabe nicht mehr bytegleich | `--check` vergleicht Version und Digest. Die REPRO-Zeile zeigt eine Abweichung offen an |

## 17. Änderungslog

| Version | Datum | Änderung |
|---|---|---|
| 0.1 | 25.10.2026 | Erstfassung (`WI-Projekt_Projektkontext.md`): Fragestellung, O2C-Modell, Ausnahmefälle E1 bis E9, Katalog, Richtlinie, Daten-, Architektur- und Evaluationskonzept |
| 0.2 | 31.10.2026 | Umbenennung und Konsolidierung zum Arbeitsdokument für die Zwischenpräsentation. Neu: Hinweise für Claude und Repo-Struktur (0), Rahmenbedingungen (1), Stichtag (4), Enthaltung (6), Pilot-Scope (5, 10), Arbeitsplan mit Kontrollpunkten und Status (12), Folienbudget (11). Lokales LLM statt API. Entscheide D1 bis D5. `spec.yaml` v0.2 angelegt. |
| 0.2.1 | 31.10.2026 | Entscheide ergänzt: E7 bleibt im Generator, "Mahnung stoppen" durch A5 abgedeckt. Neu als Annahme: Vorrangregel E7 vor E2/E3. `spec.yaml` v0.2.1 (Abschnitt `detection`). |
| 0.2.2 | 31.10.2026 | Vorrangregel E7 vor E2/E3 von Jan bestätigt, von Annahme zu Entscheid hochgestuft. Keine inhaltliche Änderung an Parametern. |
| 0.2.3 | 31.10.2026 | Hardware (MacBook Pro M4 Pro, 24 GB RAM) ergänzt. Mail an Winter entfällt, Fragen nach der Zwischenpräsentation. K1 erledigt, Schritt 2 (Log-Generator) in separatem Chat gestartet. |
| 0.3 | 01.11.2026 | Schritt 2 erledigt (K2 offen). Entscheide 01.11.2026 (Tagesbasis, weicher Trigger, Zielrolle, A0 für Happy Path, Revision und Labeling durch Claude). Datenkonzept, Begriffe, Evaluation, Repo-Struktur, Risiken und offene Punkte nachgeführt. Neu: Abschnitt 12 "So geht es weiter". `spec.yaml` v0.3.0. |
| 0.4 | 01.11.2026 | K2 und K3 freigegeben, Schritt 3 erledigt. Entscheide D-K3-1 bis D-K3-3, Bewertungsregeln M1 bis M4, Annahmen AN1 bis AN6. Baseline-Ergebnisse (10), E6-Zusatzlauf, E6-Trigger in 5.1 an spec angeglichen, E5 Zeitstempel. Neu: Prompt Schritt 4, Begriffe Baseline und Mutantenprüfung, Risiken. `spec.yaml` v0.4.0. |
| 0.5 | 01.11.2026 | Schritt 4 erledigt, K4-Entscheide D-K4-1 bis D-K4-7 getroffen. Modell `qwen3.5:9b-q4_K_M` (MLX-Build ohne Schema-Erzwingung ausgeschlossen), Prompt v1.2, Guardrail `case_id_match`, Freigabe-Modi, Bewertung roh und strikt, Temperaturlauf T 0,7 mit Seed pro Run. Abschnitte 0, 9, 10, 12 bis 16 nachgeführt. `spec.yaml` v0.5.0. |
| 0.6 | 01.11.2026 | Schritt 5 erledigt (Läufe in Claude Code, 182/182), K5 an Claude delegiert und erledigt. Entscheide D-K5-1 bis D-K5-5, Annahmen S1 bis S4. Ergebnisse und Einordnung in Abschnitt 10, Erwartung in 9 beantwortet, Status 12/13 (AP6 erledigt, AP7 in Arbeit), offene Punkte 15, Risiken 16. Prompt Schritt 6 angelegt. `spec.yaml` unverändert (v0.5.0). |
| 0.6.1 | 01.11.2026 | Präsentationsdauer 20 Minuten (Vorgabe) statt Annahme 15 Minuten: Abschnitte 1, 11, 14, 15. Folienzeiten unverändert (15 min), Test im Probevortrag. |
| 0.7 | 01.11.2026 | Schritt 6 erledigt (Demo, K6). Neu: `src/demo.py`, `docs/demo_drehbuch.md`, `out/demo/`, `out/step6_report.md`, 44 Tests. Abschnitte 0 (Lesereihenfolge, Repo-Struktur), 9 (Komponente Demo), 11 (Folie 6 mit Fällen), 12/13 (Status, AP8 in Arbeit, So geht es weiter), 14 (K6, Annahmen D6-A1 bis D6-A9), 15, 16 nachgeführt. `spec.yaml` unverändert (v0.5.0). |
| 0.7.1 | 01.11.2026 | Repo-Umbau vor dem Merge: Unterordner `wi-projekt_repo_stand_schritt4` aufgelöst (alles im Git-Root), Prototyp `apa-agent/` entfernt. Abschnitte 0 und 14. Inhalte unverändert. |
