# Schritt 3: Erkennung, Baseline, Metriken (Bericht zu K3)

Stand 01.11.2026. Grundlage: Kontextdokument v0.3, `spec.yaml` v0.3.0 (beide unverändert).
Erzeugt aus: `src/detect.py`, `src/baseline.py`, `src/metrics.py`, `src/detect_checks.py`.
Detailzahlen: `out/metrics_baseline.md`, `out/detect_checks.md`, Fehlerliste `out/errors_baseline.csv`.

## 1. Ausgangslage

- Daten reproduziert: `generate_log.py` + `validate_log.py` ergeben 43/43, alle CSV-Dateien bitgleich zum gelieferten Stand.
- Erkennung ist unabhängig vom Generator geschrieben (kein Import aus `generate_log.py` oder `validate_log.py`) und liest nur `cases.csv` und `event_log.csv`.

## 2. Erkennung

| Typ | n | Precision | Recall |
|---|---|---|---|
| E2 | 60 | 100 % | 100 % |
| E3 | 60 | 100 % | 100 % |
| E5 | 40 | 100 % | 100 % |
| E6 | 80 | 100 % | 100 % |
| E7 | 60 | 100 % | 100 % |
| none | 700 | 100 % | 100 % |

- Fehlalarme auf Erkennungsebene: 0 von 35 Grenzfällen.
- Routing: 370 Fälle gehen an den Agenten (300 harte Trigger, 70 nur weicher Trigger). Kein Fall fehlt, der geroutet werden müsste.
- Pilot: 17 von 20 Fällen werden geroutet. Die 3 Happy-Path-Fälle ohne Freitext erreichen den Agenten nicht und testen nur die Erkennung.

**Einordnung (Zirkularität):** 100 % ist kein Erfolgsnachweis. Generator und Erkennung setzen dieselben Regeln aus derselben Spezifikation um, geschrieben vom selben Modell. Der Wert zeigt nur, dass zwei Implementierungen der Spezifikation übereinstimmen. Fehler in der Spezifikation selbst werden so nicht gefunden.

**Was die Daten tatsächlich prüfen (Mutanten, `out/detect_checks.md`):** Absichtlich falsche Regelvarianten werden von den Daten erkannt.

| Falsche Variante | falsch erkannt | davon Grenzfälle |
|---|---|---|
| E2 `>=` statt `>` | 13 | 13 |
| E3 `<= 2` statt `< 2` | 12 | 11 |
| E6 `<=` statt `<` | 11 | 11 |
| Zeitpunkt statt Tagesbasis (E3, E6) | 23 | 22 |
| ohne Vorrangregel E7 | 60 | 0 |

Die Grenzfälle erfüllen ihren Zweck: Jeder Operatorfehler würde sichtbar. Das Kontextdokument nennt für den Zeitpunktvergleich 24 kippende Fälle, die Mutantenprüfung ergibt 23 (vermutlich andere Definition der Variante, ohne Folgen).

**Befund E5 (Spec-Lücke):** 20 von 40 E5-Fällen haben Rechnung und Versand am selben Tag, die Rechnung einige Stunden früher. `detection.granularity: day` würde, wörtlich auf E5 angewendet, diese 20 Fälle verpassen. Umgesetzt ist Annahme AN4: Tagesbasis gilt für Fristen (E3, E6), die Reihenfolge bei E5 wird nach Zeitstempel geprüft. Fachlich kritisch: Eine Rechnung wenige Stunden vor dem Versand am selben Tag ist in der Praxis kaum ein relevanter Verstoss. E5 ist Konzept, betrifft den Pilot nicht, sollte aber vor der Umsetzung geklärt werden.

## 3. Baseline

| Typ | Regel |
|---|---|
| E2 | A6 Credit Management |
| E3 | A4 + A2 (Annahme B1) |
| E5 | A6 Buchhaltung + A7 (nur informativ) |
| E6 | Kategorie per `keyword_labeler.classify` (unverändert), dann Zuordnung laut spec |
| E7 | A6 Credit Management (Annahme B2, nicht bewertet) |
| nur weicher Trigger | A0 |

**Ergebnis Aktionskorrektheit (exakter Mengenvergleich, Rollenprüfung):**

| Gruppe | alle Fälle | Pilot |
|---|---|---|
| deterministisch (E2, E3) | 120/120 (100 %) | 8/8 |
| Ermessen (E6) | 59/80 (73,8 %) | 6/6 |
| Happy Path mit Freitext | 70/70 (100 %) | 3/3 |
| bewertet gesamt | 249/270 (92,2 %) | 17/17 |
| E5 (informativ) | 40/40 | - |

E6 nach Kategorie (alle Fälle): Reklamation 10/20, Zahlung avisiert 16/20, Zahlungsschwierigkeiten 13/20, irrelevant 20/20. Alle 21 Fehler entstehen, weil der Keyword-Klassifikator keinen Treffer findet und auf "irrelevant" (A3, Mahnung) fällt. Rollenfehler: 0. Enthaltungen: 0 (die Baseline enthält sich nie).

**E6 nach Textstil (Vorlagenfeld `stil`):**

| Stil | Fälle | Baseline falsch |
|---|---|---|
| direkt | 43 | 0 |
| distraktor | 5 | 0 |
| indirekt | 32 | 21 (66 %) |

Beispiel C0244 (Reklamation, indirekt): Text über durchnässte, unbrauchbare Kartons ohne Schlüsselwort. Baseline: irrelevant, A3 (Mahnung). Soll: A5 Kundendienst. Fachlich ist das der teuerste Fehlertyp, weil ein Kunde mit Mangel gemahnt wird (verletzt Regel 3 der Ermessensrichtlinie).

## 4. Kritischer Befund: Pilot kann den Mehrwert bei E6 nicht zeigen

Die Baseline löst im Pilot alle 6 E6-Fälle korrekt. Grund: Von den 6 zufällig gezogenen E6-Fällen sind 4 direkt formuliert, die 2 indirekten treffen zufällig Schlüsselwörter. Damit ist im Pilot jeder Agent bestenfalls gleich gut wie die Baseline, und die Hauptfrage (Mehrwert gegenüber festen Regeln) bleibt im Pilot unbeantwortbar. Auf allen 80 E6-Fällen liegt die Baseline bei 73,8 %, dort gibt es Raum für einen Unterschied.

Optionen:
1. **Empfehlung:** Pilot (20 Fälle, k = 3) unverändert lassen, in Schritt 5 den Agenten zusätzlich auf alle 80 E6-Fälle laufen lassen (k = 1, 80 lokale Aufrufe). Kein Eingriff in Daten, grössere Stichprobe (32 indirekte Texte).
2. Pilot nach dem a priori festgelegten Merkmal `stil` schichten (z. B. mind. 3 von 6 E6 indirekt) und neu ziehen. Erfordert Änderung an `spec.pilot` und Generator, ändert nur `pilot_sample.csv`.

Nicht empfohlen: Pilotfälle danach auswählen, wo die Baseline scheitert (Selektionsverzerrung zugunsten des Agenten).

Ergänzend: Die Grenzfälle liegen nicht im Pilot. Fehlalarme auf Erkennungsebene sind daher nur auf allen Fällen messbar. Da die Erkennung deterministisch ist, ist das unkritisch.

## 5. Metrikmodul für Schritt 4 und 5

`src/metrics.py --actions <datei> --label <name>` wertet jede Datei im Format `agent_output_schema` aus, auf allen Fällen und auf dem Pilot. Zusätzlich vorbereitet: optionales Feld `run` (k Durchläufe, Reproduzierbarkeit als Anteil Fälle mit identischem Typ, identischen Aktionen und Rollen über alle Runs), Schema- und Guardrail-Vorprüfung (Pflichtfelder, Enums, Rolle bei A5/A6, Begründung ≥ 20 Zeichen, `unknown` erfordert A6), Doppelte Ausgaben, Typ-Übereinstimmung. Das Bewertungsraster für Nachvollziehbarkeit (0 bis 2) ist manuell (K5) und nicht enthalten.

## 6. Annahmen

| ID | Annahme | Wirkung im Log |
|---|---|---|
| AN1 | Nur Events mit Zeitstempel ≤ `now` zählen | keine |
| AN2 | E2 ohne Stadiumsbedingung (open_point wörtlich umgesetzt) | kein Fall betroffen |
| AN3 | E3: Teillieferung zählt nicht als Versenden (open_point wörtlich) | kommt nicht vor |
| AN4 | E5: Reihenfolge nach Zeitstempel, nicht nach Tag | entscheidend für 20 von 40 E5 |
| AN5 | Mehrere harte Trigger ausser E2+E3: Priorität E5 > E6 > E2 > E3 | kommt nicht vor |
| AN6 | Signatur `evaluate(case, events, now)`: Events als eigener Parameter statt Teil von `case` | fachlich gleich, testbar ohne globale Daten |
| B1 | Baseline E3 = A4 + A2: umfassendste autonome Variante, Regel kennt den Grund der Verzögerung nicht; alle Varianten laut D2 korrekt, die Wahl ändert die Korrektheit nicht | keine |
| B2 | Baseline E7 = A6 Credit Management (Übergabe an Mensch) | nicht bewertet |
| B3 | Baseline enthält sich nie | Enthaltungsquote 0 |
| M1 | Bewertet: E2, E3, E6, Happy Path mit Freitext. E5 informativ, E7 nicht | |
| M2 | Nenner end-to-end: bewerteter Fall ohne Ausgabe zählt als falsch | |
| M3 | Aktionen als Menge (Reihenfolge egal), jede A5/A6 muss die erwartete Zielrolle haben | |
| M4 | `unknown` zählt als falsch, auch wenn A6 zulässig wäre (spec `abstention`) | |

## 7. Limitationen

- Zirkularität der Erkennung (Abschnitt 2). Aussagekräftig ist nur die Mutantenprüfung.
- Baseline bei E2, E3 und Happy Path trivial 100 %, weil Soll und Regel aus derselben Tabelle stammen. Der Vergleich Agent vs. Baseline ist nur bei E6 (später E7) informativ.
- Keyword-Klassifikator: Der Autor kannte die Vorlagen (Docstring), die Baseline ist daher eher zu stark als zu schwach.
- Pilot klein (17 bewertete Fälle) und bei E6 nicht repräsentativ (Abschnitt 4).
- E6-Texte stammen aus 34 von 40 Vorlagen, mehrere Fälle teilen sich eine Vorlage. Die 80 Fälle sind keine 80 unabhängigen Beobachtungen.
- E5 Tagesgleichheit (Abschnitt 2): Realitätsnähe fraglich.

## 8. Nötige Nachführungen (ausgeführt nach K3: Kontextdokument v0.4, `spec.yaml` v0.4.0)

**`spec.yaml`:**
1. `detection.granularity`: präzisieren, dass die Tagesbasis für Fristen (E3, E6) gilt und die Reihenfolge bei E5 nach Zeitstempel (AN4).
2. `detection.open_points`: AN2 und AN3 als Annahme oder Entscheid eintragen.
3. `detection`: Priorität bei Mehrfachtriggern ausser E2+E3 (AN5).
4. `snapshot.detection_interface`: Signatur mit Events (AN6) oder Hinweis, dass Events Teil des Falls sind.
5. Neuer Abschnitt `baseline` (B1 bis B3) und `evaluation_rules` (M1 bis M4).
6. `pilot`: je nach Entscheid zu Abschnitt 4 (Zusatzlauf E6 oder Schichtung nach `stil`).

**Kontextdokument:**
1. Abschnitt 5.1, Tabelle E6: Trigger lautet dort "Rechnung überfällig, Freitext am Fall". In `spec.yaml` ist Freitext nicht Teil des Triggers (nur Kontext). Im Log ohne Wirkung (alle E6 haben Freitext), Formulierung angleichen.
2. Abschnitt 10: Hinweis, dass Fehlalarme der Erkennung nur auf allen Fällen messbar sind (keine Grenzfälle im Pilot), und Pilot-Befund E6.
3. Abschnitt 12/13: Schritt 3 und AP3 erledigt (K3 offen), AP6 in Arbeit. Repo-Struktur: neu `detect_checks.py`, `out/detections.csv`, `out/baseline_actions.jsonl`, `out/metrics_baseline.*`, `out/errors_baseline.csv`, `out/detect_checks.md`, `out/step3_report.md`.
4. Abschnitt 14: Annahmen AN1 bis AN6, B1 bis B3, M1 bis M4 und die Entscheide aus K3.
5. Abschnitt 14: "24 Fälle kippen" bei Zeitpunktvergleich, Mutantenprüfung ergibt 23.
6. Abschnitt 16: Risiko "Pilot bei E6 nicht repräsentativ" und Limitation E5 Tagesgleichheit.

## 9. Befehle

```
python src/generate_log.py && python src/validate_log.py      # 43/43
python src/detect.py                                           # out/detections.csv
python src/detect_checks.py                                    # out/detect_checks.md
python src/baseline.py                                         # out/baseline_actions.jsonl
python src/metrics.py --actions out/baseline_actions.jsonl --label baseline
```
