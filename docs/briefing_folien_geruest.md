# Briefing: Folien-Gerüst Zwischenpräsentation (parallel zu Schritt 6)

| Feld | Wert |
|---|---|
| Stand | 01.11.2026 |
| Für | Gruppenmitglied, das das Folien-Gerüst baut, während Jan und Claude Schritt 6 (Demo) erledigen |
| Grundlage | `docs/WI-Projekt_Zwischenpraesentation_Kontext_und_Plan.md` v0.6.1, Abschnitt 11 (Folienplan) |
| Ablage | `slides/Zwischenpraesentation_geruest.pptx` (Ordner `slides/` neu anlegen) |
| Danach | Schritt 7 (Claude) finalisiert Inhalte, Sprechnotizen und Q&A auf diesem Gerüst. K7: Jan |

## 1. Auftrag

Grobe Folienstruktur umsetzen: Titel, Layout, Platzhalter für Grafiken, Kernaussagen als Stichworte. **Kein** Feinschliff an Formulierungen und keine Zahlen erfinden. Was noch nicht feststeht, als `[TODO: ...]` markieren.

Rahmen: 20 Minuten (Vorgabe), 8 Inhaltsfolien plus Titelfolie, Backup-Folien im Anhang erlaubt. Die Zeiten pro Folie (Summe 15 min) bleiben vorerst so, der Probevortrag zeigt, ob sie aufgehen.

Konventionen: Deutsch, Schweizer Schreibweise (ss statt ß), keine Gedankenstriche. Pro Folie eine Kernaussage als Titel (Aussagesatz, nicht nur Stichwort).

## 2. Was jetzt schon geht und was auf Schritt 6 wartet

| Folie | Jetzt umsetzbar? | Abhängigkeit |
|---|---|---|
| 0 Titel | ja | Namen der Gruppenmitglieder |
| 1 bis 5 | ja, inhaltlich stabil | Folie 3: Apromore-Screenshots (AP7, `docs/ANLEITUNG_apromore.md`), bis dahin Platzhalter |
| 6 Demo | nur Rahmen | Drehbuch, Screenshots und Aufzeichnung kommen aus Schritt 6 (`demo.py`) |
| 7 Evaluation | ja | Zahlen stehen fest (Schritt 5, Entscheid D-K5-5) |
| 8 Plan, offene Fragen | ja | |

## 3. Folien im Detail

### Folie 0: Titel
- Thema 75: Agentic Process Automation. KI-gestützte Erkennung und Bearbeitung von Ausnahmefällen in Geschäftsprozessen
- WI-Projekt HS 2026, ZHAW. Betreuung: Michael Winter
- Gruppe: `[TODO: Namen]`, Datum: `[TODO: Termin]`

### Folie 1: Ausgangslage und Problem (1,5 min) | Quelle: Kontext Abschnitt 1, 2
- Order-to-Cash: Ausnahmen (Kreditlimit, Verzug, Zahlungsverzug mit Kundenkommunikation) binden manuelle Arbeit
- Feste Regeln decken eindeutige Fälle ab, scheitern an Freitext und an Kombination mehrerer Signale
- Frage: Was kann ein KI-Agent zusätzlich, und wie bleibt er kontrolliert?
- Hinweis für Q&A ("Das kann ERP schon"): Fokus auf Freitext und kombinierte Signale

### Folie 2: Fragestellung (1 min) | Quelle: Abschnitt 2
- Hauptfrage: Kann ein einzelner KI-Agent im O2C-Prozess Ausnahmefälle erkennen und darauf reagieren, und wo bringt er gegenüber festen Regeln einen Mehrwert?
- Teilfragen: (1) deterministisch vs. Ermessen, (2) informieren vs. entscheiden (Autonomiestufen), (3) Absicherung: nachvollziehbar und reproduzierbar
- Erweiterung: Guardrails als eigener Untersuchungsaspekt

### Folie 3: Referenzprozess und Ausnahmefälle (2 min) | Quelle: Abschnitt 4, 5
- Grafik: Happy Path als Prozesskette: Auftrag erfassen, Kreditprüfung, Auftrag bestätigen, Kommissionieren, Versenden, Rechnung stellen, Zahlungseingang, Fall abschliessen. `[TODO: Apromore-Prozesslandkarte, sobald AP7 erledigt]`
- Tabelle Pilot:
  - E2 Kreditlimit überschritten, deterministisch, A6 Eskalation an Credit Management
  - E3 Lieferverzögerung, deterministisch, A4 Priorisieren und/oder A2 Kunde informieren
  - E6 Zahlungsverzug mit Kundenkommunikation, Ermessen (Freitext entscheidet)
- Nur Konzept: E5 Rechnung vor Versand, E7 Zielkonflikt (E2 und E3 gleichzeitig)
- Synthetisches Event Log: `[TODO: Anzahl Fälle aus out/generation_report.md]`

### Folie 4: Handlungskatalog und Autonomiestufen (1 min) | Quelle: Abschnitt 6, 7
- Katalog A0 bis A7, farblich trennen:
  - autonom: A0 Keine Massnahme, A1 Information anfordern, A2 Kunde informieren, A3 Nächsten Schritt empfehlen, A4 Priorisieren
  - Freigabe nötig: A5 Neu zuweisen, A6 Eskalieren, A7 Fall sperren
- Enthaltung: unbekannter Fall wird zu `unknown` + A6, läuft damit durch die Freigabe
- E6-Zuordnung als kleine Tabelle: Reklamation → A5, Zahlung avisiert → A0, Zahlungsschwierigkeiten → A6, irrelevant → A3

### Folie 5: Architektur und Determinismus-Konzept (2 min) | Quelle: Abschnitt 9
- Grafik (Pipeline, links nach rechts): Event Log → Erkennung (Regeln, PM4Py) → Fallobjekt → Agent (lokales LLM) → Guardrails → Human-Approval → Aktion (simuliert) → Audit-Log
- Deterministisch: Erkennung, Guardrails, Freigabe. Probabilistisch: nur die Agent-Entscheidung, eingeschränkt durch JSON-Schema, Katalog, Temperatur 0, fester Seed
- Technik: Python, Ollama, `qwen3.5:9b` (Q4_K_M), lokal auf MacBook Pro M4 Pro, kein Cloud-API
- Grafik am besten zweifarbig: deterministische Bausteine vs. LLM-Baustein

### Folie 6: Demo (4 min) | Quelle: Schritt 6
- Nur Rahmen anlegen: drei Fälle als Ablauf
  - E2: Eskalation, Freigabe durch Mensch (interaktiv j/n)
  - E3: autonome Priorisierung, ohne Freigabe ausgeführt
  - E6: Ermessensfall mit Freitext
- Platzhalter: `[TODO: Screenshots/Fall-IDs aus Schritt 6]`, Audit-Log-Ausschnitt, Hinweis auf Fallback-Aufzeichnung

### Folie 7: Evaluation und Pilot-Zwischenstand (2 min) | Quelle: `out/step5_report.md` Abschnitt 9
Formulierung ist von Jan entschieden (D-K5-5), bitte so übernehmen:
- Deterministische Fälle (E2, E3, Happy Path): Agent = Regel (51/51 bzw. 17/17). Erwartet, da durch Erkennung und Zuordnung vorgegeben
- E6 direkt formuliert: Agent = Regel (43/43)
- E6 indirekt formuliert: Agent 31/32, Regel 11/32
- Einschränkung: Texte, Kategoriedefinitionen und Labels vom selben Autor (Claude). Obergrenze, Prüfung mit fremden Texten in Iteration 2
- Reproduzierbar bei T = 0 (bytegleich), bei T = 0,7 Entscheidung stabil ausser bei freier Wahl (E3) und 1 Fehlalarm
- Begründungen nennen die ausschlaggebende Information immer (18/18), sind aber nicht immer treu (Mittel 1,56 von 2, 8 von 18 mit Abzug)
- Visualisierung: Balken direkt vs. indirekt, Agent vs. Regel. Einschränkung sichtbar auf der Folie, nicht nur im Vortrag

### Folie 8: Plan bis Januar und offene Fragen (1,5 min) | Quelle: Abschnitt 12, 15, 16
- Nächste Schritte: E5 und E7 implementieren, Test auf fremden Texten (Hold-out), menschliche Rater für Begründungen, Typ-Aktions-Guardrail als Ausblick, volle Evaluation (k = 5)
- Offene Fragen an Betreuung: Leistungsnachweis, Methodik (z. B. Design Science Research), Datum Schlussabgabe
- Limitationen kurz: synthetische Daten, Zirkularität, kleines Modell, keine Enthaltung beobachtet (0 von 182)

### Anhang (Backup für Q&A)
Je eine Folie anlegen, Inhalt folgt in Schritt 7:
- Zirkularität der Evaluation
- Warum lokales, kleines Modell
- Warum nur drei Ausnahmetypen im Pilot
- Ground Truth bei Ermessensfällen
- Ermessensrichtlinie (4 Regeln, Abschnitt 7)

## 4. Nicht tun
- Keine eigenen Zahlen berechnen oder runden. Alle Zahlen stammen aus `out/step5_report.md` und `out/generation_report.md`
- Keine Aussage wie "Der Agent ist besser als Regeln" ohne die Einschränkung (Kontamination, Obergrenze)
- Begründungen des Agenten nicht als Erklärung seiner Entscheidung darstellen (K5-Befund)
- Am Folienplan (Reihenfolge, Zeiten) nichts ändern, ohne Jan zu fragen

## 5. Übergabe
Gerüst in `slides/` ablegen (oder Link schicken, falls Google Slides/PowerPoint online) und kurz notieren, welche `[TODO]` offen sind. Grafiken (Prozess, Architektur) wenn möglich als separate Dateien (SVG/PNG) in `slides/grafiken/` ablegen, damit sie wiederverwendet werden können.
