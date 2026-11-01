# Schritt 5: Pilotläufe mit dem lokalen LLM (Bericht zu K5)

Stand 01.11.2026. Grundlage: Kontextdokument v0.5, `spec.yaml` v0.5.0 (beide unverändert), Prompt v1.2 Variante a, K4-Entscheide D-K4-1 bis D-K4-7.
Läufe und Auswertung hat Claude in Claude Code selbst ausgeführt (lokales Modell auf dem MacBook Pro M4 Pro).

## 1. Kurzfassung

| Befund | Wert | Einordnung |
|---|---|---|
| Pilot T = 0 (17 bewertete Fälle, k = 3) | 51/51 korrekt, roh = strikt | kein Befund: E2, E3, Happy Path sind vorgegeben, 3 Pilotfälle dienten dem Prompt-Tuning |
| E6-Zusatzlauf (80 Fälle, k = 1) | Agent 79/80 (98,8 %), Baseline 59/80 (73,8 %) | einziger Mehrwert-Befund, vollständig bei indirekten Texten |
| E6 indirekt (32) | Agent 31/32, Baseline 11/32 | Obergrenze: Prompt-Definitionen und Vorlagen vom selben Autor (Abschnitt 7.2) |
| E6 direkt (43) und Distraktor (5) | Agent und Baseline je 100 % | kein Unterschied |
| Reproduzierbarkeit T = 0 | 17/17 identisch, Rohtext bytegleich, auch über Sitzungen (9/9) | technischer Determinismus auf diesem Rechner bestätigt |
| Reproduzierbarkeit T = 0,7 (Seed 42, 43, 44) | Entscheidung identisch 12/17, Korrektheit 50/51 | Streuung dort, wo der Prompt Freiheit lässt (E3), plus 1 Fehlalarm |
| Guardrails | 0 von 182 Ausgaben blockiert | Guardrails im echten Lauf nie ausgelöst, beide Fehler passieren sie |
| Enthaltungen | 0 von 182 | Enthaltungsmechanismus im echten Lauf nicht beobachtet |
| Laufzeit | 182 Aufrufe in 20,7 min, Mittel 6,3 bis 7,1 s | Hochrechnung volle Evaluation unten |
| Nachvollziehbarkeit (K5, regelgeleitet durch Claude, nicht unabhängig) | Mittel 1,56 von 2 (18 Items): 10× 2, 8× 1, 0× 0 | Ausschlaggebende Information immer korrekt (18/18), aber 8 von 18 Begründungen mit falscher Aussage oder falschem Regelbezug |

## 2. Durchführung

| Punkt | Stand |
|---|---|
| Umgebung | venv ausserhalb des Repos (`~/.venvs/apa-agent`, Python 3.15.2, pandas 3.1.0, numpy 2.5.4, PyYAML 6.0.3). 37 Unit-Tests OK |
| Ollama | 0.40.13, Modell `qwen3.5:9b-q4_K_M`, Digest `56671c2ab938…`, 100 % GPU, Kontext 8192 |
| Schema-Check | `llm_client.py check --think off`: `ERGEBNIS: OK, Schema wird erzwungen` (`out/llm_check_step5.txt`) |
| Konfiguration | Prompt v1.2a (Hash `509c488c…`), Schema-Hash `9e9b629c…`, Denkmodus aus, Endpunkt chat, Freigabe batch |
| Läufe | `pilot_t0` 51/51 Paare, `e6_t0` 80/80, `pilot_t07` 51/51 (T = 0,7, `--seed-mode per_run`). Je mit `caffeinate -i`, nacheinander, ohne Abbruch |
| Fehler | Transportfehler 0, Parsefehler 0, `done_reason` immer `stop` (keine abgeschnittenen Ausgaben) |
| Konsolenausgaben | `out/console_<label>.log` |

Hinweis zur Durchführung: Ein erster Startversuch scheiterte am Argument-Parser (Shell-Variable in zsh nicht aufgeteilt), bevor ein Aufruf oder eine Datei entstand. Kein Einfluss auf die Daten.

## 3. Aktionskorrektheit nach Typ

Bewertung nach M1 bis M4 (`metrics.py`). Roh und strikt sind in allen Läufen identisch, weil kein Guardrail blockiert hat.

| Gruppe | n | Pilot T = 0 (3 Runs) | Pilot T = 0,7 (3 Runs) | Baseline Pilot | E6-Zusatzlauf | Baseline E6 |
|---|---|---|---|---|---|---|
| E2 | 4 | 12/12 | 12/12 | 4/4 | | |
| E3 | 4 | 12/12 | 12/12 | 4/4 | | |
| E6 | 6 (Pilot) / 80 | 18/18 | 18/18 | 6/6 | 79/80 (98,8 %) | 59/80 (73,8 %) |
| Happy Path mit Freitext | 3 | 9/9 | 8/9 | 3/3 | | |
| gesamt | 17 | 51/51 | 50/51 | 17/17 | 79/80 | 59/80 |

Pro Run: Pilot T = 0 je 17/17. Pilot T = 0,7: 17/17, 16/17, 17/17.

Typ-Übereinstimmung 182/182: Das Modell übernimmt `detected_type`. Das ist Abschreiben und kein Befund.

**E2, E3 und Happy Path sind durch Fallobjekt und Prompt vorgegeben.** `detected_type` steht im Fallobjekt, die Zuordnung Typ → Aktion im Prompt. 100 % dort zeigen Formatdisziplin, nicht Leistung. Zusätzlich sind C0317 (E2), C0067 (E3) und C0880 (E6) Rauchtestfälle, an denen Prompt v1.0 bis v1.2 nachgeschärft wurde (D-K4-7). Die Pilotzahlen sind damit kontaminiert und für die Mehrwertfrage nicht verwendbar. Agent und Baseline sind im Pilot gleich (17/17).

### E6 nach Kategorie (E6-Zusatzlauf)

| Kategorie | n | Agent | Baseline |
|---|---|---|---|
| Reklamation | 20 | 20 | 10 |
| Zahlung avisiert | 20 | 19 | 16 |
| Zahlungsschwierigkeiten | 20 | 20 | 13 |
| irrelevant | 20 | 20 | 20 |

## 4. E6 nach direkten und indirekten Texten

| Stil | n | Agent (roh = strikt) | Baseline | nur Agent korrekt | nur Baseline korrekt | beide falsch |
|---|---|---|---|---|---|---|
| direkt | 43 | 43 (100 %) | 43 (100 %) | 0 | 0 | 0 |
| indirekt | 32 | 31 (96,9 %) | 11 (34,4 %) | 20 | 0 | 1 |
| Distraktor | 5 | 5 (100 %) | 5 (100 %) | 0 | 0 | 0 |
| gesamt | 80 | 79 (98,8 %) | 59 (73,8 %) | 20 | 0 | 1 |

| Kategorie | Stil | n | Agent | Baseline |
|---|---|---|---|---|
| Reklamation | indirekt | 13 | 13 | 3 |
| Zahlung avisiert | indirekt | 7 | 6 | 3 |
| Zahlungsschwierigkeiten | indirekt | 12 | 12 | 5 |

**Statistik.** Auf Fallebene: exakter McNemar-Test 20 zu 0 diskordante Paare, p < 0,0001. Das überschätzt die Evidenz, weil 80 Fälle aus 34 Vorlagen stammen und Fälle derselben Vorlage fast identische Texte haben. Ehrlicher ist die Vorlage als Einheit: Agent besser bei 8 Vorlagen, schlechter bei 0, gleich bei 26, Vorzeichentest p = 0,0078. Agent pro Vorlage: 33 immer korrekt, 1 gemischt (`payment_announced_06`). Indirekte Vorlagen: 12, Agent immer korrekt bei 11, Baseline bei 4.

**Was der Unterschied misst.** "Indirekt" ist in den Vorlagen definiert als "ohne Schlüsselwort der Kategorie". Die Baseline ist ein Keyword-Klassifikator. Dass sie bei indirekten Texten scheitert, ist konstruktionsbedingt und kein empirischer Befund. Der Befund ist der andere Teil: Das 9B-Modell ordnet 31 von 32 schlüsselwortfreien Texten richtig ein. Zur Belastbarkeit siehe Abschnitt 7.2.

## 5. Reproduzierbarkeit

| Lauf | Fälle | Entscheidung identisch (Typ, Aktionen, Rollen) | Rohtext identisch | Korrekt in 3/3 Runs |
|---|---|---|---|---|
| Pilot T = 0, Seed 42 | 17 | 17/17 | 17/17 | 17/17 |
| Pilot T = 0,7, Seed 42/43/44 | 17 | 12/17 | 0/17 | 16/17 (1 Fall 2/3) |

Querprüfung über Sitzungen (gleiche Konfiguration): Rauchtest vs. `pilot_t0` Run 1 (3 Fälle) und `pilot_t0` Run 1 vs. `e6_t0` (6 E6-Pilotfälle). Entscheidung und Rohtext 9/9 bytegleich. Bei T = 0 ist das System auf diesem Rechner deterministisch. Das gilt für diese Hardware, diese Ollama-Version und sequentielle Aufrufe. Auf andere Umgebungen ist es nicht übertragbar.

Abweichungen bei T = 0,7:

| Fall | Typ | Run 1 | Run 2 | Run 3 | korrekt |
|---|---|---|---|---|---|
| C0067 | E3 | A4 (Rolle Vertrieb) | A2 | A4 | 3/3 |
| C0166 | E3 | A2+A4 (Rolle Lager/Logistik bei A4) | A4 | A2+A4 | 3/3 |
| C0642 | E3 | A2 | A2 | A2+A4 | 3/3 |
| C0447 | E6 irrelevant | A3 | A3 (Rolle Vertrieb) | A3 | 3/3 |
| C0412 | Happy Path, Betriebsferien | A0 | **A3** | A0 | 2/3 |

Dazu weicht C0537 (E3) zwischen T = 0 und T = 0,7 ab (A2+A4 vs. A4 in allen drei Runs), bei gleichem Seed 42 in Run 1.

Einordnung:
- Die E6-Entscheidungen sind unter Sampling stabil (6/6 Fälle, C0447 nur mit Rollen-Rauschen). Das spricht dafür, dass die E6-Einordnung nicht zufällig richtig ist.
- Bei E3 streut die Wahl, wo der Prompt sie freigibt ("Wähle nach Lage des Falls"). Bei T = 0 wählt das Modell in allen 4 E3-Fällen A2+A4, obwohl die Lage verschieden ist (Termin in 1 Tag bis 4 Tage verpasst). Die verlangte fallbezogene Wahl findet nicht statt. Bewertungsrelevant ist das nicht (D2), fachlich ist es ein Befund.
- Ohne Freiheitsgrad (E2, E6) gibt es bei T = 0,7 kaum Streuung. Reproduzierbarkeit hängt hier mehr am Prompt als an der Temperatur.

## 6. Enthaltungen, Guardrails, Laufzeit

| Lauf | Aufrufe | blockiert | Enthaltungen | Hinweise (nicht blockierend) | Dispositionen |
|---|---|---|---|---|---|
| pilot_t0 | 51 | 0 | 0 | 0 | executed 27, pending_approval 24 |
| pilot_t07 | 51 | 0 | 0 | `role_on_non_role_action` 3, `evidence_unknown_field` 1 | executed 27, pending_approval 24 |
| e6_t0 | 80 | 0 | 0 | 0 | executed 39, pending_approval 41 |

| Lauf | Mittel s | Median s | P95 s | Max s | Summe min | Tokens ein | Tokens aus (Mittel / Max) |
|---|---|---|---|---|---|---|---|
| pilot_t0 | 6,3 | 6,4 | 7,5 | 7,5 | 5,3 | 2041 | 165 / 187 |
| pilot_t07 | 6,9 | 6,8 | 8,4 | 9,3 | 5,9 | 2041 | 173 / 251 |
| e6_t0 | 7,1 | 7,1 | 8,0 | 8,4 | 9,5 | 2136 | 174 / 209 |

Hochrechnung volle Evaluation (370 geroutete Fälle, k = 5, 1850 Aufrufe): rund 3,5 Stunden bei 7 s. Machbar in einem Lauf über Nacht oder in Etappen (fortsetzbar).

Freigabe (batch): Alle A5 und A6 blieben `pending`, keine Freigabe-Aktion wurde ausgeführt.

## 7. Kritische Bewertung

### 7.1 Fehlerliste

| Lauf | Fall | Soll | Ausgabe | Guardrail | Disposition | Folge |
|---|---|---|---|---|---|---|
| e6_t0 | C0776 (E6, Zahlung avisiert, indirekt) | A0 | A6 Credit Management | bestanden | pending_approval | Mensch sieht den Fall, Fehler auf der sicheren Seite |
| pilot_t07 Run 2 | C0412 (Happy Path, Betriebsferien) | A0 | A3 (Mahnung empfehlen) | bestanden | executed | Fehlalarm erreicht ohne Freigabe die (simulierte) Ausführung |

Nicht als Fehler gewertet, aber zu benennen: 3 Ausgaben bei T = 0,7 mit `target_role` an A3 oder A4 (C0067, C0166, C0447). `metrics.py` prüft Rollen nur bei A5/A6, die Ausgaben zählen als korrekt. Die Reproduzierbarkeit zählt sie als abweichend.

Volle Liste: `out/step5_errors.csv`, `out/errors_<label>.csv`.

**C0776.** Text: "Wir hatten eine Systemumstellung im Kreditorenwesen. Der offene Betrag ist im nächsten Lauf am 23.03.2026 enthalten und wird Ihnen dann gutgeschrieben." Das Modell liest eine Verschiebung als Bitte um Aufschub. Die Begründung behauptet eine "konkrete Zahlungsvereinbarung", die es nicht gibt, und zitiert die Regel "Bitte um Aufschub", obwohl der Kunde nicht bittet. C0253 mit derselben Vorlage (anderes Datum, 11 statt 28 Tage überfällig) ist korrekt. Ob die Tage überfällig oder das Datum den Ausschlag gaben, lässt sich mit einem Fall nicht sagen. Fachlich ist die Grenze zwischen "Zahlung avisiert" und "Aufschub" bei dieser Vorlage nicht scharf. Das betrifft die Ground Truth (Labeling durch Claude, nicht unabhängig).

**C0412 Run 2.** Die Begründung zitiert eine Zuordnung "none → A3", die es im Prompt nicht gibt (verwechselt mit E6 irrelevant). Sie klingt plausibel und ist falsch. A3 ist autonom, der Fehler läuft ohne Mensch durch. Bei T = 0 tritt er nicht auf.

### 7.2 Belastbarkeit des E6-Befunds

- **Kontamination der Kategoriedefinitionen.** Claude hat Vorlagen, Prompt und Keyword-Liste geschrieben. Die Definitionen im Prompt treffen die indirekten Vorlagen sehr direkt:

| Prompt-Definition | Indirekte Vorlage |
|---|---|
| "fehlende oder falsche Teile" | complaint_06 (falscher Artikel im Karton), complaint_08 (50 statt 100 m) |
| "Schaden" | complaint_05 (Kartons durchnässt) |
| "Defekt, Fehlfunktion" | complaint_07 (Anlage läuft mit Unterbrechungen), complaint_10 (Display ausgefallen) |
| "Raten" | payment_difficulty_07 (über mehrere Monate verteilt abzahlen) |
| "meldet sie als veranlasst" | payment_announced_05 (an die Bank angewiesen), payment_announced_08 (Auftrag an die Bank) |

  Der Agent musste paraphrasierte Begriffe erkennen, nicht unbekannte Sachverhalte. Die 31/32 sind deshalb eine Obergrenze für diesen Textbestand. Wie das Modell auf fremde Texte reagiert, ist nicht gemessen.
- **Ground Truth vom selben Modell.** Labeler A ist Claude (nicht unabhängig). Beim einzigen Agentenfehler (C0776) ist die Ground Truth selbst diskutabel.
- **Kleine Stichprobe.** 32 indirekte Fälle aus 12 Vorlagen. Auf Vorlagenebene 8:0, p = 0,0078. Die Richtung ist klar, die Grösse des Effekts ist unsicher.
- **Der Pilot kann den Befund nicht stützen.** Die 6 Pilot-E6 sind für beide Verfahren 6/6 (Befund K3). Der Mehrwert stammt allein aus dem Zusatzlauf. Dieser diente nicht dem Tuning, enthält aber die 6 Pilot-E6, darunter C0880 (Rauchtest). Ohne C0880: 78/79. Am Ergebnis ändert das nichts.

### 7.3 Guardrails und Enthaltung

- 0 Blockaden in 182 Aufrufen. Unter erzwungenem Schema sind die Guardrails strukturell redundant (wie in `step4_report.md` erwartet). Ihre Wirksamkeit ist nur im Mock-Lauf mit Fehlerinjektion gezeigt, nicht mit dem echten Modell. "Guardrail-Wirksamkeit" lässt sich für die Zwischenpräsentation nur als "keine unzulässige Ausgabe aufgetreten" berichten, nicht als "abgefangen".
- Beide fachlichen Fehler passieren alle Guardrails. Die Absicherung gegen falsche Entscheidungen leistet bei C0776 die Freigabe (A6), bei C0412 nichts (A3 autonom).
- 0 Enthaltungen. Regel 4 ("im Zweifel an einen Menschen") wird nie über `unknown` umgesetzt. Bei C0776 wählt das Modell eine Kategorie mit A6, statt sich zu enthalten. Das ist für die Bewertung günstiger (Enthaltung zählt als falsch, M4), sagt aber nichts darüber, ob das Modell Unsicherheit erkennt.

### 7.4 Nachvollziehbarkeit (vor K5)

- Grobe automatische Prüfung: In keiner der 182 Begründungen steht eine Zahl oder ein Datum, das nicht im Fallobjekt vorkommt (Zahlenabgleich, keine inhaltliche Prüfung).
- Inhaltlich falsche Behauptungen gibt es trotzdem: C0776 (erfundene "Zahlungsvereinbarung"), C0412 Run 2 (erfundene Zuordnung), C0317 ("automatische Weiterleitung", obwohl A6 Freigabe braucht). C0880 (E6, richtig entschieden) begründet mit der Ermessensrichtlinie (Regel 3), die laut Prompt v1.2 nur bei E7 gilt. Das in v1.0 und v1.1 beobachtete Muster (Richtlinie statt Zuordnung) ist also in der Begründung noch da, wirkt sich hier aber nicht auf die Aktion aus.
- Systematisch über alle 182 Ausgaben (Textsuche): Die Ermessensrichtlinie wird in 15 von 32 Begründungen zu Reklamationen zitiert, "automatische" Weiterleitung steht in 7 von 24 E2-Begründungen.
- **Widerspruch zwischen Begründung und Aktion** (ausserhalb der Stichprobe): C0317 bei T = 0,7, Run 1. Die Begründung argumentiert mit Regel 1 (Kundenbeziehung hat Vorrang, "eine sofortige Eskalation wäre unverhältnismässig"), die Aktion ist A6 Eskalieren. Die Aktion ist korrekt, weil die Zuordnung sie vorgibt. Die Begründung trägt sie aber nicht, sie spricht dagegen. Das ist der deutlichste Beleg, dass die Begründung keine verlässliche Erklärung der Entscheidung ist. Die Begründungen klingen in allen Fällen gleich sicher, auch wenn die Entscheidung falsch ist. Das Schema stellt Belege und Begründung vor die Entscheidung (G3), erzwingt aber keine Treue.
- `key_evidence` verweist bei T = 0 immer auf existierende Felder. Bei T = 0,7 einmal nicht (`derived.detected_type`, richtig wäre `detection.detected_type`).

### 7.5 Kurz zur Hauptfrage

Für die Zwischenpräsentation vertretbar: Der Agent erreicht bei deterministischen Fällen dasselbe wie die Regel (erwartet, kein Mehrwert) und ist bei indirekt formulierten E6-Texten der Keyword-Regel klar überlegen, unter Bedingungen, die ihn begünstigen (Definitionen und Texte vom selben Autor). Nicht vertretbar wäre, die 98,8 % als Leistung auf realen Kundentexten darzustellen.

## 8. K5: Stichprobe der Begründungen

Vorbereitet in `out/k5_stichprobe.md` (lesbar) und `out/k5_stichprobe.csv` (Spalten `score_0_2`, `kommentar` zum Ausfüllen). Schlüssel mit Ground Truth und Korrektheit getrennt in `out/k5_key.csv`, damit blind bewertet werden kann.

| Punkt | Inhalt |
|---|---|
| Umfang | 18 Begründungen plus 2 Zusatzitems |
| Schichtung | 2 E2, 2 E3, 2 Happy Path mit Freitext (`pilot_t0` Run 1), 12 E6 (`e6_t0`, je Kategorie 3, davon bis zu 2 indirekt, jede Vorlage höchstens einmal) |
| Auswahl | Zufall mit Seed 42, unabhängig vom Ergebnis. Zufällig enthalten: C0317, C0067, C0880 (Rauchtestfälle) |
| Zusatzitems | K5-Z1 C0776, K5-Z2 C0412 Run 2 (die beiden Fehler, bewusst gewählt, nicht blind, nicht im Mittelwert) |
| Raster | 0 bis 2, Option A mit Klarstellungen (Entscheid Jan): falscher Regelbezug oder falsche Nebenaussage ergibt höchstens 1, 0 nur bei falscher oder fehlender ausschlaggebender Information |

### 8.1 Bewertung (an Claude delegiert, regelgeleitet)

Entscheid Jan: Die K5-Prüfung übernimmt Claude, möglichst neutral. Weil ein Urteil von Claude nicht neutral ist (Autor von Prompt, Texten und Labels, Schlüssel bekannt), wird jede Begründung in Einzelaussagen zerlegt und gegen Fallobjekt und Prompt geprüft. Die Punkte folgen mechanisch aus drei Prüfungen: I (ausschlaggebende Information korrekt), F (jede Sachaussage gedeckt, Überzeichnung zählt als falsch), R (angeführte Regel). Protokoll pro Item: `out/k5_pruefprotokoll.md`, Punkte: `out/k5_bewertung.csv`.

| Kennzahl (18 Items, ohne Zusatz) | Wert |
|---|---|
| Mittel | **1,56 von 2** |
| Verteilung | 2 Punkte: 10, 1 Punkt: 8, 0 Punkte: 0 |
| Information korrekt (I) | 18/18 |
| mindestens eine falsche Aussage (F) | 6/18 |
| Ermessensrichtlinie statt Zuordnung (R) | 2/18, dazu 1 Mischform |
| nach Typ | E2 1,0 (2), E3 2,0 (2), Happy Path 2,0 (2), E6 1,5 (12) |
| E6 nach Stil | direkt 1,83 (6), indirekt 1,17 (6) |
| Zusatzitems (Fehler) | C0776: 0 (Text falsch gedeutet, Vereinbarung erfunden). C0412 T 0,7: 1 (Information korrekt, Zuordnung erfunden) |

Falsche Aussagen: "automatische Weiterleitung" bei A6 (2× E2), "abgeschlossener Vorgang" bei angekündigter Zahlung, "bittet um Aufschub" und "explizit" bei indirekten Texten, "Lieferstopp" statt Montagestillstand.

**Abgleich Urteil vs. Protokoll:** 17 von 18 gleich. K5-06 im Urteil 2, im Protokoll 1. Das Urteil war milder, weil die Entscheidung bekannt richtig war. Massgeblich ist das Protokoll. Mit milder Lesart von Überzeichnungen läge das Mittel bei 1,61.

**Kernaussage Nachvollziehbarkeit:** Das Modell nennt die ausschlaggebende Information immer korrekt (18/18). Die Begründungen sind aber nicht durchgehend treu: Ein Drittel enthält eine falsche Nebenaussage, bei indirekten Texten die Hälfte und mehr (Paraphrase wird zur Behauptung). Dazu kommt der Widerspruch C0317 bei T = 0,7 (Begründung gegen die Aktion, Abschnitt 7.4). Die Begründung ist damit eine brauchbare Zusammenfassung, aber kein verlässlicher Beleg dafür, warum entschieden wurde.

**Grenzen:** nachprüfbar, nicht unabhängig (kein menschlicher Rater, keine Übereinstimmungsmessung). 18 Items, nur Tendenzen. Das Raster trennt folgenlose und folgenreiche falsche Regelbezüge nicht (für die Schlussabgabe: Treue als eigenes Kriterium, mindestens ein menschlicher Rater).

### 8.2 Status K5

K5 erledigt durch Delegation (Entscheid Jan 01.11.2026). Eine Prüfung durch Jan ist nicht nötig, aber jederzeit möglich (`out/k5_pruefprotokoll.md`, Grenzfälle K5-04, K5-06, K5-18).

## 9. Entscheide Jan (01.11.2026)

Vorgabe Jan: die Varianten mit wenig Zeitaufwand, damit eine Grundlage für die Präsentation entsteht.

| # | Frage | Entscheid | Folge |
|---|---|---|---|
| 1 | Raster K5 | A: eine Zahl 0 bis 2, falscher Regelbezug oder falsche Nebenaussage höchstens 1 | umgesetzt. Bewertung an Claude delegiert, regelgeleitet (8.1) |
| 2 | Rolle an A3/A4 | A: Hinweis bleibt, keine Regeländerung nach dem Lauf | Zahlen unverändert (pilot_t07 50/51), als Formatbefund berichtet |
| 3 | Typ-Aktions-Guardrail | A: nur Ausblick | kein Code. Argument für Folie 8: nicht zirkulär, hätte C0412 Run 2 blockiert, nicht aber C0776 |
| 4 | Test auf fremden Texten | A: erst in Iteration 2 | Kontamination (7.2) bleibt Limitation und muss auf der Folie stehen. Achtung: Iteration 2 nach `prompts/extern/` ändert die Vorlagen, danach alle Auswertungen neu rechnen. Ein separater Hold-out-Satz wäre weniger invasiv |
| 5 | Folie 7 | B: Aufteilung direkt/indirekt mit Einschränkung | Formulierung unten |

**Formulierung Folie 7 (Vorschlag):**
- Deterministische Fälle (E2, E3, Happy Path): Agent = Regel (51/51 bzw. 17/17). Erwartet, da durch Erkennung und Zuordnung vorgegeben.
- E6 direkt formuliert: Agent = Regel (43/43).
- E6 indirekt formuliert: Agent 31/32, Regel 11/32.
- Einschränkung: Texte, Kategoriedefinitionen und Labels vom selben Autor (Claude). Obergrenze, Prüfung mit fremden Texten in Iteration 2.
- Reproduzierbar bei T = 0 (bytegleich), bei T = 0,7 Entscheidung stabil ausser bei freier Wahl (E3) und 1 Fehlalarm.
- Begründungen nennen die ausschlaggebende Information immer (18/18), sind aber nicht immer treu (Mittel 1,56 von 2, 8 von 18 mit Abzug).

## 10. Nötige Nachführungen (nicht ausgeführt, erst auf Anweisung)

**Kontextdokument (v0.6):**
1. Abschnitt 10: Pilotergebnis und E6-Zusatzlauf (Tabellen aus 3 und 4), Reproduzierbarkeit (5), Einordnung (7).
2. Abschnitt 12/13: Schritt 5 erledigt bis auf K5-Bewertung, AP6 Pilotauswertung erledigt. Zeile "So geht es weiter" ersetzen.
3. Abschnitt 14: Annahmen Schritt 5 (venv ausserhalb des Repos, K5-Schichtung, Vorzeichentest auf Vorlagenebene, K5-Bewertung durch Claude nicht unabhängig), Entscheide aus Abschnitt 9 (1A, 2A, 3A, 4A, 5B).
4. Abschnitt 16: Risiken "Begründung nicht treu (Widerspruch C0317 T = 0,7)", "keine Enthaltung beobachtet", "autonome Fehlaktion A3 bei T > 0", Kontamination der Kategoriedefinitionen (konkretisiert).
5. Abschnitt 10 und 12: Raster K5 mit Klarstellungen, Ergebnis 1,56 von 2, K5 erledigt (an Claude delegiert).
5. Abschnitt 0 (Repo-Struktur): `src/step5_eval.py`, `out/step5_*`, `out/k5_*`.

**`spec.yaml`:** keine Parameteränderung nötig. Bei Entscheid 2 oder 3: `evaluation_rules` bzw. `guardrails`.

## 11. Neue Dateien (nichts Bestehendes geändert ausser `out/audit_log.jsonl`, angehängt)

| Datei | Inhalt |
|---|---|
| `src/step5_eval.py` | Zusatzauswertung (Stil, Vorlagen, Reproduzierbarkeit, Laufzeit, Fehlerliste, K5-Stichprobe). Nutzt `metrics.judge`, Bewertung identisch. Neu, nicht im Auftrag als Skript verlangt |
| `out/agent_actions_<label>.jsonl`, `out/agent_run_<label>.json` | Rohentscheidungen und Laufkonfiguration (`pilot_t0`, `e6_t0`, `pilot_t07`) |
| `out/metrics_<label>.md|json`, `out/errors_<label>.csv` | `metrics.py` roh und strikt (`_strict`) |
| `out/step5_tables.md`, `out/step5_errors.csv` | Tabellen und Fehlerliste aus `step5_eval.py` |
| `out/k5_stichprobe.md|csv`, `out/k5_key.csv` | K5-Stichprobe (blind) und Schlüssel |
| `out/k5_bewertung.csv`, `out/k5_pruefprotokoll.md` | Punkte (Protokoll und erstes Urteil) und Prüfprotokoll pro Item |
| `out/console_<label>.log`, `out/llm_check_step5.txt` | Konsolenausgaben, Schema-Check |

Reproduzieren der Auswertung (ohne LLM): `python src/metrics.py …` wie `docs/ANLEITUNG_lokal.md` Abschnitt 4, dann `python src/step5_eval.py`.
