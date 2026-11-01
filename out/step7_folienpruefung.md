# Schritt 7: Prüfung der Folien gegen den Projektstand (Bericht zu K7)

Stand 01.11.2026. Geprüft: `slides/WI-Projekt_Thema75_Zwischenpraesentation.pptx` (21 Folien, nicht verändert), Folientext, Diagrammdaten und Sprechnotizen.
Grundlage: Kontextdokument v0.7.1, `spec/spec.yaml` v0.5.0, `out/step5_report.md`, `out/step6_report.md`, `docs/demo_drehbuch.md`, weitere Berichte in `out/`. Zahlen zum Event Log zusätzlich direkt aus `data/event_log.csv` und `data/cases.csv` nachgerechnet, Tests ausgeführt (44 OK).
Literaturquellen nicht geprüft (Auftrag). Aussagen über die Projektausschreibung sind im Repo nicht belegbar (Ausschreibung liegt nicht im Repo) und als `[TODO]` markiert.

## 1. Übersicht

| Folie (alt) | Inhalt | Befund | Neue Position |
|---|---|---|---|
| 1 | Titel | Datum, Zeitplan in den Notizen veraltet | 1 |
| 2 | Agenda, Rollen | Sprecher widersprechen den Notizen, Demo nicht bei Jan | 2 |
| 3 | Ausgangslage | ok (Literatur nicht geprüft) | 3 |
| 4 | Fragestellung | ok | 4 |
| 5 | Vorgehen | Status K4 bis K6 veraltet, Modellname, Notizen veraltet | 5 |
| 6 | O2C, Event Log | 1 Zahl uneinheitlich, Rollen im Log | 6 |
| 7 | Ausnahmefälle | ok | 7 |
| 8 | Baseline | ok, Überleitung anpassen | 8 |
| 9 | Handlungskatalog | 1 Aussage unbelegt, Enthaltung ergänzen | 9 |
| 10 | Architektur | Modellname, Guardrail-Liste unvollständig | 10 |
| 11 | Demo | Fälle, Werkzeug, Notizen veraltet | 11 |
| neu | Ergebnisse Schritt 5 | fehlt | **12** |
| 12 | Kritische Einordnung | Stand vor Schritt 5 | 13 |
| 13 | Zwischenstand, Plan | Stand vor K4 | 14 |
| 14 | Quellen | nur Notiz | 15 |
| 15 | Dank | Notiz anpassen | 16 |
| 16 bis 21 | Backup | 17 (Q&A), 19, 20, 21 veraltet; 18 ok | 17 bis 22 |

Durchgehend: Modell heisst `qwen3.5:9b-q4_K_M` (Folien 5, 10, 11, 19, 21). Der Tag `qwen3.5:9b` lädt auf Apple Silicon einen Build ohne Schema-Erzwingung (HTTP 501). Beleg: Kontextdokument Abschnitt 9 "Modellhinweis", D-K4-1.

## 2. Befunde pro Folie

### Folie 1: Titel

| Stelle | Ist | Korrektur | Beleg |
|---|---|---|---|
| Datum | 01.11.2026 | `[TODO: Termin der Zwischenpräsentation]`. Termin ist laut Kontext offen | Kontextdokument Abschnitt 1, 11 |
| Notizen | Zeit- und Sprechplan mit "[Person 3]", Demo bei Andrin, 19:30 plus Reserve | ersetzen durch die Zeittabelle in `docs/sprechtext_zwischenpraesentation.md` Abschnitt 6 | |
| Notizen | "bei Überzug zuerst Folie 7 und Folie 12 kürzen, nie die Demo" | ersetzen durch die Kürzungen im Sprechtext Abschnitt 7 | |

### Folie 2: Agenda und Rollen

| Stelle | Ist | Korrektur | Beleg |
|---|---|---|---|
| Agenda, "spricht" | 1 Andrin, 2 Minh Sang, 3 Jan, 4 Jan, 5 Minh Sang. Widerspricht den Notizen (Folie 1: Jan, [Person 3], Andrin) | Vorschlag (Abschnitt 3): 1 Ausgangslage, Fragestellung, Vorgehen: Andrin. 2 Prozess, Ausnahmefälle, Baseline: Minh Sang. 3 Agent: Katalog und Architektur: Andrin. 4 Live-Demo und Ergebnisse: Jan. 5 Kritische Einordnung und Plan: Minh Sang | Prompt Schritt 7 (Demo macht Jan) |
| Agenda | 5 Teile ohne Ergebnisse | Teil 4 "Live-Demo und Ergebnisse" (neue Folie 12) | `out/step5_report.md` Abschnitt 9 |
| Rollen | Andrin: "KI-Agent und lokales LLM (Ollama), Demo" | "Demo" zu Jan verschieben. Rollentexte insgesamt `[TODO: Jan bestätigen]`, im Repo nicht belegt | |
| Notizen | "Sprecher: Jan" | Sprecher: Andrin | |

### Folie 3: Ausgangslage

Keine Korrektur. Literatur nicht geprüft. Notizen: "Sprecher: Jan · 1:30" durch "Andrin · 1:20" ersetzen.

### Folie 4: Fragestellung und Abgrenzung

Inhalt stimmt mit Kontextdokument Abschnitt 2 überein. Notizen: Sprecher Andrin, 1:00.

### Folie 5: Vorgehen

| Stelle | Ist | Korrektur | Beleg |
|---|---|---|---|
| Schritt 4 | "gebaut, K4 offen" (in Arbeit) | "K4 erledigt" (Farbe erledigt) | Kontextdokument Abschnitt 12 |
| Schritt 5 | "K5 offen" | "K5 erledigt" | `out/step5_report.md` Abschnitt 8.2 |
| Schritt 6 | "K6 Probelauf" | "K6 erledigt" | `out/step6_report.md` Abschnitt 9 |
| Schritt 7 | "K7 heute" | "K7 in Arbeit" (Folien und Probevortrag) | Kontextdokument Abschnitt 12 |
| Arbeitsweise | "An jedem Kontrollpunkt entscheidet das Team" | Kontext: "Entscheide trifft nur Jan". Formulierung `[TODO: Jan]`, z. B. "An jedem Kontrollpunkt wird entschieden" | Kontextdokument Abschnitt 0 |
| Werkzeuge | "Ollama mit qwen3.5:9b (lokal)" | "Ollama mit qwen3.5:9b-q4_K_M (lokal)" | D-K4-1 |
| Notizen | "Agent-Kern mit Mock-Client getestet, Abnahme K4 steht an", "[Person 3]" | "Schritte 1 bis 6 abgeschlossen, K1 bis K6 freigegeben. Folien sind Schritt 7." Übergabe an Minh Sang | Kontextdokument Abschnitt 12 |

### Folie 6: Order-to-Cash, Referenzprozess und Event Log

Nachgerechnet aus `data/event_log.csv`: 1000, 912, 781, 706, 644, 612, 476, 442 Fälle pro Aktivität, 5905 Events, 35 Varianten, vollständiger Ablauf 31,4 %, Teillieferung 32 Fälle, Zahlungserinnerung 68 Fälle. Alles korrekt.

| Stelle | Ist | Korrektur | Beleg |
|---|---|---|---|
| "Auftrag ändern · 232" | 232 ist die Anzahl **Events**. Die anderen Zahlen sind Fälle. 232 Events verteilen sich auf **152 Fälle** | "Auftrag ändern · 152" (Fälle, einheitlich mit Teillieferung und Zahlungserinnerung) | `data/event_log.csv` (nachgerechnet) |
| "5 Rollen: Vertrieb, Credit Management, Lager, Buchhaltung, Kundendienst" | Im Event Log kommen 4 Rollen vor. Kundendienst ist nur Zielrolle des Agenten (A5) | "4 Rollen im Log (Vertrieb, Credit Management, Lager/Logistik, Buchhaltung), dazu Kundendienst als Zielrolle" | `out/generation_report.md` Prüfung 17, 21 |
| "Events mit Aktivität, Zeitstempel und Rolle" | Events haben auch eine Ressource | optional "und Ressource" | `out/generation_report.md` Prüfung 1 |
| Notizen | "[Person 3] · 1:45" | Minh Sang · 1:20 | |

### Folie 7: Ausnahmefälle

Inhalt stimmt mit `spec.yaml`, Prompt v1.2 (Abschnitt Ausnahmetypen) und Kontextdokument Abschnitt 5 überein (E3 "in < 2 Tagen oder verpasst", E5 A6 Buchhaltung + A7, E7 mit Freigabe).

| Stelle | Ist | Korrektur | Beleg |
|---|---|---|---|
| Notizen | "E7 braucht ein Labeling mit Personen" | "Empfehlung: Labeling mit mindestens einer Person (offen)" | Kontextdokument Abschnitt 8, 15 |
| Notizen | "[Person 3] · 1:45" | Minh Sang · 1:20 | |

### Folie 8: Baseline

Geprüft und korrekt: Diagramm 120/120, 70/70, 59/80 (73,75 %), 11/32 (34,4 %); 70 Rauschfälle, 35 Grenzfälle, Mutanten 11 bis 23 Fehler, 43 von 43 Datenprüfungen, Zitat C0244.
Belege: `out/step3_report.md`, `out/detect_checks.md`, `out/generation_report.md`, `data/cases.csv`.

| Stelle | Ist | Korrektur | Beleg |
|---|---|---|---|
| Notizen | Übergabe "Andrin zeigt, wie der Agent aufgebaut ist" | bleibt (Andrin spricht Folie 9 und 10) | |
| Notizen | "[Person 3] · 2:00" | Minh Sang · 1:20 | |

### Folie 9: Handlungskatalog und Autonomiestufen

Katalog und Autonomiestufen stimmen mit `spec.yaml` und Prompt v1.2 überein.

| Stelle | Ist | Korrektur | Beleg |
|---|---|---|---|
| Fusszeile | "deckt alle Massnahmen der Ausschreibung ab" | im Repo nicht belegbar, `[TODO: gegen Ausschreibung prüfen]` | |
| Enthaltung | nur Regel | in den Notizen ergänzen: "Im Pilot nie genutzt (0 von 182), siehe Ergebnisse" | `out/step5_report.md` Abschnitt 7.3 |
| Notizen | "Sprecher: Andrin · 1:15" | Andrin · 1:00 | |

### Folie 10: Architektur

| Stelle | Ist | Korrektur | Beleg |
|---|---|---|---|
| Baustein Agent | "qwen3.5:9b lokal" | "qwen3.5:9b-q4_K_M lokal" | D-K4-1 |
| Guardrails | "Katalog, Zielrolle, Schema, Begründung, Enthaltung, Fall-ID" (6 genannt, "7 Prüfregeln" im Baustein) | "Katalog, Autonomiestufe, Zielrolle, Schema, Begründung, Enthaltung, Fall-ID" (7) | `spec/spec.yaml` `guardrails` |
| Audit-Log | "Replay ist bitgleich" | "Replay ist bytegleich" (Begriff wie in Demo und Bericht) | `out/step6_report.md` Abschnitt 1 |
| Fusszeile | "Reproduzierbarkeit wird deshalb gemessen" | ergänzen: "Ergebnis: Folie 12" | |
| Notizen | ok, Sprecher Andrin 1:30. Übergabe "Jetzt live" an Jan | | |

### Folie 11: Live-Demo

Komplett nach `docs/demo_drehbuch.md` ersetzen.

| Stelle | Ist | Korrektur | Beleg |
|---|---|---|---|
| Fall 1 | C0317 (Rauchtestfall), Auftrag CHF 11'762 + offene Posten 50'026 | **C0902**, E2 Kreditlimit. Lage: Auftrag CHF 5'963 + offene Posten CHF 126'468 = CHF 132'431, Limit CHF 100'000 (+32,4 %), Zahlungshistorie schlecht. Erwartet: A6 an Credit Management. Wir zeigen: Freigabe live, Begründung behauptet "automatische Weiterleitung" | `data/cases.csv`, `out/demo/console_demo_live.txt` |
| Fall 2 | C0067 (Rauchtestfall) | **C0537**, E3 Lieferverzug. Lage: Liefertermin 06.07.2026, Stichtag 05.07.2026 (morgen), kommissioniert, nicht versendet. Erwartet: A4 und/oder A2. Wir zeigen: autonome Ausführung ohne Freigabe | `out/demo/console_demo_live.txt` |
| Fall 3 | C0244 | bleibt. Lage stimmt (39 Tage überfällig, 12 von 40 Kartons). "Wir zeigen": "Agent A5, Keyword-Regel A3 (Mahnung). Einschränkung: Obergrenze, Folie 12" | `out/demo/console_demo_live.txt` |
| Fusszeile | "Live mit qwen3.5:9b über Ollama: run_agent.py mit interaktiver Freigabe, Anzeige mit audit_view.py. Fallback: Aufzeichnung" | "Live mit qwen3.5:9b-q4_K_M über Ollama, Werkzeug `src/demo.py` (Konfiguration wie Evaluation, T = 0, Seed 42). Fallback 1: Replay derselben Aufzeichnung (bytegleich). Fallback 2: Bildschirmaufzeichnung `[TODO: Jan, noch offen]`. Drei Fälle sind Illustration, kein Beleg" | `docs/demo_drehbuch.md` Abschnitt 4, Kontextdokument Abschnitt 15 |
| Optional | | Reserve C0776 (echter Fehler) nicht auf der Folie, nur in den Notizen | `docs/demo_drehbuch.md` Abschnitt 3 |
| Notizen | PowerShell, `ollama pull qwen3.5:9b`, `run_agent.py --cases C0317,C0067,C0244`, Approver Andrin, Alternative C0880 | ersetzen: "Sprecher Jan, 4:00. Ablauf, Befehle und Notfallplan: `docs/demo_drehbuch.md` (Abschnitt 0 Befehle, 2 Ablauf, 4 Notfallplan). T minus 15 min `src/demo.py --check`, letzte Zeile BEREIT. Reserve C0776 nur bei Fragen". C0880 ist Rauchtestfall, nicht als Alternative nennen | `docs/demo_drehbuch.md`, `out/step6_report.md` Abschnitt 3 |

### Neue Folie 12: Ergebnisse Pilot und E6-Zusatzlauf (fehlt)

Formulierung nach D-K5-5 (`out/step5_report.md` Abschnitt 9), Zahlen aus Abschnitt 3 bis 8.

**Titel:** Erste Ergebnisse: Mehrwert nur bei indirekt formulierten Kundentexten, mit Einschränkung

**Inhalt:**
- Deterministische Fälle (E2, E3, Happy Path): Agent = Regel (51/51 bzw. 17/17). Erwartet, da durch Erkennung und Zuordnung vorgegeben.
- E6 direkt formuliert: Agent = Regel (43/43).
- E6 indirekt formuliert: Agent 31/32, Regel 11/32.
- Einschränkung: Texte, Kategoriedefinitionen und Labels vom selben Autor (Claude). Obergrenze, Prüfung mit fremden Texten in Iteration 2.
- Reproduzierbar bei T = 0 (bytegleich), bei T = 0,7 Entscheidung stabil ausser bei freier Wahl (E3) und 1 Fehlalarm.
- Begründungen nennen die ausschlaggebende Information immer (18/18), sind aber nicht immer treu (Mittel 1,56 von 2, 8 von 18 mit Abzug).

**Grafik:** Balken Agent vs. Regel nach Stil (direkt 43/43 vs. 43/43, indirekt 31/32 vs. 11/32, Distraktor 5/5 vs. 5/5). Einschränkung als Kasten auf der Folie, nicht nur im Vortrag (Briefing Folie 7).

**Fusszeile:** `qwen3.5:9b-q4_K_M`, Prompt v1.2a, 182 Aufrufe (Pilot 17 Fälle × 3 Runs bei T = 0 und T = 0,7, E6-Zusatzlauf 80 Fälle × 1). 0 Ausgaben blockiert, 0 Enthaltungen. Bewertung der Begründungen durch Claude, regelgeleitet, nicht unabhängig.

**Notizen:** Pilot 100 % ist kein Befund (Prompt an C0317, C0067, C0880 nachgeschärft). Auf Vorlagenebene Agent besser bei 8 von 34 Vorlagen, schlechter bei 0 (Vorzeichentest p = 0,0078). Fallebene überschätzt (80 Fälle aus 34 Vorlagen). Fehler: C0776 (A6 statt A0, Freigabe fängt ab), C0412 bei T = 0,7 (A3 statt A0, autonom, keine Kontrolle).

Belege: `out/step5_report.md` Abschnitte 1, 3, 4, 5, 7, 8.1, 9.

### Folie 13 (alt 12): Kritische Einordnung

Stand vor Schritt 5. Zwei Punkte sind überholt, vier Befunde fehlen.

| Kasten | Ist | Korrektur | Beleg |
|---|---|---|---|
| Zirkularität | Spezifikation, 100 % Erkennung | ergänzen: Prompt-Definitionen treffen die indirekten Texte fast wörtlich, Prompt an 3 Pilotfällen nachgeschärft. → E6 als Obergrenze berichten, Hold-out mit fremden Texten in Iteration 2 | `out/step5_report.md` 7.2, D-K5-4 |
| Freitext-Bias | ok | mit Zirkularität zusammenlegen (Platz für neue Punkte) | |
| Leakage | ok | bleibt | `out/step5_report.md` Abschnitt 3 |
| Kleines lokales Modell | "voraussichtlich schwächer" | **überholt**: nicht bestätigt (31/32 indirekt), aber Obergrenze. Ersetzen durch "**Begründung nicht treu**: Information immer korrekt (18/18), aber 8 von 18 mit Abzug, C0317 bei T = 0,7 Begründung gegen die Aktion. → Begründung nicht als Erklärung werten, menschliche Rater und Treue als Kriterium bis Januar" | `out/step5_report.md` 7.4, 8.1 |
| Guardrails prüfen nur die Form | Beispiel hypothetisch ("Mahnung statt Kundendienst") | echte Fälle: "0 von 182 Ausgaben blockiert. Beide Fehler passieren: C0776 (A6 statt A0) fängt die Freigabe ab, C0412 bei T = 0,7 (A3 statt A0, autonom) nicht. → Typ-Aktions-Guardrail als Ausblick" | `out/step5_report.md` 7.1, 7.3, D-K5-3 |
| Kleine Stichprobe | "Zusatzlauf auf allen 80 E6-Fällen" als Gegenmassnahme | Zusatzlauf ist erledigt. Neu: "80 E6-Fälle aus 34 Vorlagen, 32 indirekte aus 12 Vorlagen. → Auswertung pro Vorlage (8:0, p = 0,0078), volle Evaluation (k = 5) bis Januar" | `out/step5_report.md` 4, 7.2 |
| neu | | "**Keine Enthaltung**: 0 von 182. Ob das Modell Unsicherheit erkennt, ist nicht gezeigt. → als Befund berichten, Freigabe bleibt die Kontrolle" | `out/step5_report.md` 7.3 |
| Notizen | "[Person 3] · 1:15", Übergabe an Jan | Minh Sang · 1:20, kein Sprecherwechsel zu Folie 14 | |

### Folie 14 (alt 13): Zwischenstand und Plan

| Stelle | Ist | Korrektur | Beleg |
|---|---|---|---|
| Erreicht | "Spezifikation v0.4" | "Spezifikation v0.5.0" | `spec/spec.yaml` Zeile 16 |
| Erreicht | "37 automatisierte Tests, Pipeline mit Mock-Client end-to-end" | "44 automatisierte Tests" und "Pipeline end-to-end mit dem lokalen Modell: 182 Aufrufe (K4, K5)" | Testlauf 01.11.2026 (44 OK), `out/step5_report.md` 2 |
| Erreicht | "Offen: Rauchtest und Pilot mit qwen3.5:9b (K4, K5)" | streichen. Neu: "Demo live und Replay (K6)" | `out/step6_report.md` |
| November | K4, Pilot, Zusatzlauf, Temperaturlauf, K5 | alles erledigt. Neu: "Zwischenpräsentation, Fragen an die Betreuung" | Kontextdokument 12, 15 |
| Dezember | E5, E7, E7-Labeling, volle Evaluation (k = 5), Prozesswirkung, Apromore | ergänzen: Hold-out mit fremden Texten (externe Labeler, nicht Qwen-Familie), menschliche Rater für Begründungen, Typ-Aktions-Guardrail als Ausblick. Volle Evaluation: 370 Fälle, k = 5, rund 3,5 h. Monatszuordnung `[TODO: Jan bestätigen]`, im Kontext nur "bis Januar" | Kontextdokument 15, `out/step5_report.md` 6, 9 |
| Dezember | "Auswirkungen auf den Prozess (Freigabelast, vermiedene Fehlmahnungen)" | Herleitung aus der Ausschreibung `[TODO: prüfen]`. Freigabelast ist bereits messbar: pending_approval 24 von 51 (Pilot), 41 von 80 (E6) | `out/step5_report.md` 6 |
| Notizen | "Pilot und E6-Zusatzlauf liefern im November die erste echte Antwort" | "Erste Antwort liegt vor (Folie 12), bis Januar prüfen wir sie auf fremden Texten" | |
| Notizen | "Sprecher: Jan · 1:30" | Minh Sang · 1:10 | |

### Folie 15 (alt 14): Quellen

Nicht geprüft. Notiz: "Berichte (Schritte 1 bis 4)" durch "(Schritte 1 bis 6)" ersetzen.

### Folie 16 (alt 15): Dank

Notiz: Sprecher Minh Sang, 0:10 (bis 20:00). Backup-Liste um "Ergebnisse im Detail" ergänzen, falls Folie 18 bis 22 erweitert werden.

### Backup-Folien (alt 16 bis 21)

| Folie | Ist | Korrektur | Beleg |
|---|---|---|---|
| 17 Q&A | "Warum kleines lokales Modell? ... Schwächen bei E6 weisen wir als Befund aus" | "Schwäche bei E6 nicht beobachtet (31/32 indirekt), aber Obergrenze wegen gleichem Autor. Daten bleiben lokal, Modellstand fixiert (Digest)" | `out/step5_report.md` 7.2 |
| 17 Q&A | "Kappa 0,70" | stimmt, ergänzen: "(Claude vs. Keyword-Klassifikator, nicht unabhängig)" | `out/labeling_report.md` |
| 17 Q&A | "34 % bei indirekten Texten" | stimmt (11/32) | `out/step3_report.md` |
| 17 Q&A, neu | | "Sind 98,8 % nicht zu gut? Ja, für reale Texte: Obergrenze, gleicher Autor, Hold-out folgt." und "Was passiert, wenn das Modell falsch liegt? C0776: Guardrails lassen es durch, die Freigabe fängt es ab. Bei autonomen Aktionen (C0412) greift nichts" | `out/step5_report.md` 7 |
| 18 Prozesslandkarte | 35 Varianten, 31,4 / 10,0 / 7,4 / 6,7 / 6,0 % | stimmt (nachgerechnet) | `data/event_log.csv` |
| 19 Modellwahl | "qwen3.5:9b (Vorschlag)" | "qwen3.5:9b, Build Q4_K_M (entschieden, D-K4-1)". Grund ergänzen: Standard-Tag lädt MLX-Build ohne Schema-Erzwingung (HTTP 501) | Kontextdokument 9, 14 |
| 19 Modellwahl | "Laufzeit: 182 Aufrufe ... unter einer Stunde (Schätzung, Rauchtest misst)" | gemessen: "182 Aufrufe in 20,7 min, 6,3 bis 7,1 s pro Aufruf im Mittel" | `out/step5_report.md` 6 |
| 19 Modellwahl | "Strukturierte Ausgabe: wird vor dem Rauchtest geprüft" | "geprüft: Schema wird erzwungen (Ollama 0.40.13)" | `out/llm_check_step5.txt` |
| 19 Modellwahl | "Windows-PC mit RTX 3080 (10 GB VRAM)" | im Repo nicht belegt, alle Läufe auf dem MacBook. `[TODO: streichen oder belegen]` | `out/step4_report.md`, `out/step5_report.md` 2 |
| 19 Notizen | "Entscheid an K4. Laufzeiten sind Schätzungen" | "Entschieden an K4. Laufzeiten gemessen in Schritt 5" | |
| 20 Prompt | "Aufbau des Systemprompts (v1.0)" | "(v1.2, Variante a)". Ergänzen: "Geltungsregel: Ermessensrichtlinie nur bei E7, sonst ist die Zuordnung bindend. Bei E3 nur A4 und A2 zulässig" | `prompts/agent_prompt.md` Zeilen 48, 58, D-K4-7 |
| 20 Prompt | "Rund 1300 Tokens" | Wert gilt für v1.0. Für v1.2 gemessen nur mit Fallobjekt: "Eingabe 2041 bis 2136 Tokens im Mittel" | `out/step4_report.md` 46, `out/step5_report.md` 6 |
| 21 Audit-Eintrag | Mock-Beispiel C0880 (Rauchtestfall), Prompt v1.0, Modell "..." | echter Eintrag, z. B. C0244 aus `e6_t0`: `"model": "qwen3.5:9b-q4_K_M"`, `"model_digest": "56671c2ab938..."`, `"temperature": 0`, `"seed": 42`, `"prompt_version": "1.2"`, `"prompt_hash": "509c488c..."`, `"case_object_hash": "3d7b322d..."`, `exception_type` E6, `actions` A5 Kundendienst, `"guardrail": {"passed": true, "requires_approval": ["A5"]}`, `"approval": {"mode": "batch", "status": "pending"}`, `"disposition": "pending_approval"`. Fusszeile: "Echter Eintrag aus dem E6-Zusatzlauf (gekürzt)". Hinweis: `key_evidence` ist dort ein Textzitat, kein Feldpfad | `out/audit_log.jsonl` (Label `e6_t0`, C0244) |

## 3. Sprecherverteilung (Vorschlag)

Grundsatz: zusammenhängende Blöcke, 4 Sprecherwechsel (je 10 s eingeplant), Demo bei Jan, Rollen auf Folie 2 passen zum Inhalt (Andrin Agent, Jan Demo und Evaluation, Minh Sang Daten).

| Block | Folien | Sprecher | Dauer |
|---|---|---|---|
| Einleitung | 1 bis 5 | Andrin | 3:50 |
| Prozess, Ausnahmen, Baseline | 6 bis 8 | Minh Sang | 4:00 |
| Agent: Katalog, Architektur | 9, 10 | Andrin | 2:30 |
| Demo, Ergebnisse | 11, 12 | Jan | 6:20 |
| Einordnung, Plan, Dank | 13, 14, 16 | Minh Sang | 2:40 |
| Sprecherwechsel | 4 × 0:10 | | 0:40 |
| **Summe** | | Andrin 6:20, Minh Sang 6:40, Jan 6:20 | **20:00** |

Details und Text: `docs/sprechtext_zwischenpraesentation.md`.

## 4. Nötige Nachführungen (nicht ausgeführt, erst auf Anweisung)

**Folien (`.pptx`):** alle Korrekturen aus Abschnitt 2, neue Folie 12, Notizen pro Folie aus dem Sprechtext.

**Kontextdokument (v0.7.1):**
1. Abschnitt 0: "Für Schritt 7 gibt es noch keinen Prompt" ersetzen (`docs/prompt_schritt7_folien.md`). Repo-Struktur: Dateiname der Folien (`slides/WI-Projekt_Thema75_Zwischenpraesentation.pptx`), neu `out/step7_folienpruefung.md`, `docs/sprechtext_zwischenpraesentation.md`.
2. Abschnitt 1 und 15: Namen der Gruppe (Jan Tkac, Andrin Rüedi, Minh Sang Vu, laut Titelfolie) und Sprecherverteilung.
3. Abschnitt 11: Folienplan (8 Folien, 15 min) entspricht nicht dem Foliensatz (16 Hauptfolien plus Backup, 20:00). An die Struktur aus Abschnitt 3 anpassen, Entscheid "Folienzeiten bleiben bei 15 min" ersetzen.
4. Abschnitt 12/13: Schritt 7 Status, AP8.
5. Abschnitt 14: Entscheide K7 (Sprecher, Folienstruktur, Kürzungen).
6. Abschnitt 17: Änderungslog.

**`docs/demo_drehbuch.md`:** Foliennummern folgen dem Folienplan des Kontexts, nicht dem Foliensatz: "Folie 6" (Titel) → 11, "Pipeline von Folie 5" → 10, "Folie 7" (Abschnitt 2) → 12.

**`spec.yaml`, Code, Prompt:** keine Änderung nötig.
