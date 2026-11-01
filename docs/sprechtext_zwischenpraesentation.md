# Sprechtext Zwischenpräsentation (20 Minuten)

Stand 01.11.2026, Schritt 7. Grundlage: korrigierte Folien nach `out/step7_folienpruefung.md` (Foliennummern dort, neue Folie 12 "Ergebnisse"), `docs/demo_drehbuch.md`, `out/step5_report.md` Abschnitt 9 (D-K5-5).

Annahmen: Sprechtempo mindestens 130 Wörter pro Minute. Die Wortzahl pro Folie ist so bemessen, dass sie bei 130 Wörtern pro Minute die Dauer füllt; wer schneller spricht, gewinnt Reserve. Wortzahl = Sprechtext plus Überleitung, ohne Regieanweisungen in eckigen Klammern. Sprecherverteilung ist ein Vorschlag (Entscheid Jan).

Regeln beim Sprechen: Nicht sagen "der Agent erkennt die Ausnahme" (die Regel erkennt). Ausgeführt heisst immer "simuliert". "Bytegleich" heisst reproduzierbar, nicht korrekt. Die 31 von 32 nie ohne Einschränkung nennen.

---

## 1. Einleitung (Andrin)

### Folie 1: Titel

| Sprecher | Start | Dauer | Wörter |
|---|---|---|---|
| Andrin | 0:00 | 0:20 | 40 |

Guten Tag. Wir sind Jan Tkac, Minh Sang Vu und ich, Andrin Rüedi. Unser Thema heisst Agentic Process Automation. Die Frage dahinter: Kann ein KI-Agent Ausnahmefälle im Order-to-Cash-Prozess erkennen und bearbeiten? Betreut werden wir von Michael Winter.

**Überleitung:** Kurz zum Ablauf.

### Folie 2: Agenda und Rollen

| Sprecher | Start | Dauer | Wörter |
|---|---|---|---|
| Andrin | 0:20 | 0:30 | 61 |

Der Vortrag hat fünf Teile. Ich beginne mit Ausgangslage, Fragestellung und Vorgehen. Minh Sang zeigt dann Prozess, Daten, Ausnahmefälle und die Regel-Baseline. Danach erkläre ich, wie der Agent aufgebaut ist. Jan zeigt ihn live und stellt die ersten Ergebnisse vor. Zum Schluss ordnet Minh Sang die Ergebnisse kritisch ein und zeigt den Plan bis Januar.

**Überleitung:** Zuerst: Warum ist das Thema relevant?

### Folie 3: Ausgangslage

| Sprecher | Start | Dauer | Wörter |
|---|---|---|---|
| Andrin | 0:50 | 1:20 | 172 |

Prozesse laufen selten so, wie sie modelliert sind. Im Order-to-Cash heisst das: Ein Kunde überschreitet sein Kreditlimit, eine Lieferung wird knapp, eine Rechnung bleibt offen.

Heute gibt es dafür zwei Werkzeuge. Process Mining macht Abweichungen im Event Log sichtbar, meist aber im Nachhinein, in Analysen und Dashboards. Feste Regeln in ERP oder RPA reagieren sofort und immer gleich. Sie sind aber starr. Schreibt ein Kunde eine Nachricht, oder widersprechen sich zwei Signale, landet der Fall beim Menschen. Ein Beispiel: Ein Kunde zahlt nicht, schreibt aber, dass die Ware beschädigt ankam. Eine Regel mahnt trotzdem.

Hier setzt Agentic Process Automation an. Ein Sprachmodell liest den Fall, interpretiert ihn und wählt eine Massnahme.

Das Kernproblem: Ein Sprachmodell entscheidet nicht deterministisch. Es kann sich irren und klingt dabei trotzdem sicher. Ein Agent im Prozess braucht deshalb einen festen Rahmen. Einen abschliessenden Katalog erlaubter Aktionen. Eine Freigabe durch einen Menschen vor kritischen Schritten. Und ein lückenloses Protokoll. Das deckt sich mit unserem On-Boarding: Der Agent muss kontrolliert werden, der Mensch bleibt Supervisor.

**Überleitung:** Daraus folgt unsere Fragestellung.

### Folie 4: Fragestellung und Abgrenzung

| Sprecher | Start | Dauer | Wörter |
|---|---|---|---|
| Andrin | 2:10 | 1:00 | 128 |

Unsere Hauptfrage: Kann ein einzelner KI-Agent im Order-to-Cash-Prozess Ausnahmefälle erkennen und darauf reagieren, und wo bringt er gegenüber festen Regeln einen Mehrwert?

Dazu drei Teilfragen. Erstens: Welche Fälle löst eine feste Regel, welche brauchen Ermessen? Zweitens: Wo darf der Agent nur informieren, wo darf er selbst entscheiden? Drittens: Wie bleibt sein Verhalten nachvollziehbar und reproduzierbar? Zu allen drei Teilfragen zeigen wir heute erste Antworten: in der Demo und in den Ergebnissen aus dem Pilotlauf.

Wir grenzen bewusst ein. Ein Fall ist ein Auftrag. Die Daten sind synthetisch, weil nur so zu jedem Fall die richtige Reaktion bekannt ist. Es gibt einen Agenten, kein Multi-Agent-System. Das Modell läuft lokal, alle Aktionen sind simuliert, kritische Aktionen gibt ein Mensch frei. Kein echtes ERP, keine echten Kundendaten.

**Überleitung:** So sind wir vorgegangen.

### Folie 5: Vorgehen

| Sprecher | Start | Dauer | Wörter |
|---|---|---|---|
| Andrin | 3:10 | 0:40 | 88 |

Wir arbeiten in sieben Schritten mit Kontrollpunkten. Jeder Schritt liefert ein prüfbares Artefakt: Code, Daten oder einen Bericht. Annahmen und Entscheide halten wir in einem Entscheidungslog fest. Alle Parameter stehen an einer Stelle, in einer Spezifikationsdatei. Spezifikation, Daten, Erkennung, Agent, Pilotlauf und Demo sind abgeschlossen. Die Folien sind der siebte Schritt. Methodisch lehnen wir uns an Design Science Research an: ein Artefakt bauen und gegen eine Ground Truth prüfen. Die Methodik-Vorgabe klären wir noch mit der Betreuung.

**Überleitung:** Minh Sang zeigt, auf welchem Prozess und welchen Daten wir arbeiten.

*Sprecherwechsel, 0:10*

---

## 2. Prozess, Ausnahmen, Baseline (Minh Sang)

### Folie 6: Order-to-Cash, Referenzprozess und Event Log

| Sprecher | Start | Dauer | Wörter |
|---|---|---|---|
| Minh Sang | 4:00 | 1:20 | 178 |

Unser Referenzprozess ist Order-to-Cash in acht Schritten: Auftrag erfassen, Kreditprüfung, bestätigen, kommissionieren, versenden, Rechnung stellen, Zahlungseingang, Abschluss. Dazu kommen drei zulässige Varianten: Auftrag ändern, Teillieferung und Zahlungserinnerung.

Die Daten sind ein synthetisches Event Log: 1000 Aufträge, 5905 Events, Fallstart zwischen Januar und Juni 2026. Jedes Event hat Aktivität, Zeitstempel, Ressource und Rolle. Zu jedem Auftrag kennen wir ausserdem Auftragswert, Kreditlimit, offene Posten, Zahlungshistorie und, falls vorhanden, eine Nachricht des Kunden. 70 Prozent sind normale Fälle, der Rest verteilt sich auf die fünf Ausnahmetypen. Warum synthetisch? Öffentliche Logs zeigen, was passiert ist, aber nicht, was die richtige Reaktion gewesen wäre. Diese Ground Truth brauchen wir für die Bewertung.

Jeder Fall wird zu einem Stichtag betrachtet. Die Zahlen unter den Schritten zeigen, wie viele Fälle den Schritt bis dahin erreicht haben. Alle 1000 starten, 442 sind abgeschlossen, die übrigen laufen noch. Insgesamt gibt es 35 Varianten, 31 Prozent der Fälle haben den vollständigen Ablauf.

Die orangen Marken zeigen, wo die Erkennung auf Ausnahmen prüft: Kreditlimit, Lieferverzug, Rechnung vor Versand und Zahlungsverzug.

**Überleitung:** Welche Ausnahmen das genau sind, zeigt die nächste Folie.

### Folie 7: Ausnahmefälle, feste Regel oder Ermessen

| Sprecher | Start | Dauer | Wörter |
|---|---|---|---|
| Minh Sang | 5:20 | 1:20 | 168 |

Wir unterscheiden zwei Arten von Ausnahmen. Bei deterministischen Fällen bestimmt eine feste Regel die Erkennung und die Reaktion. E2: Auftragswert plus offene Posten liegen über dem Kreditlimit. Dann geht der Fall an das Credit Management. E3: Der Liefertermin ist in weniger als zwei Tagen oder schon verpasst, und es wurde nicht versendet. Dann wird priorisiert, der Kunde informiert oder beides.

Bei Ermessensfällen reicht die Regel nicht. E6 ist ein Zahlungsverzug mit einer Nachricht des Kunden. Die Erkennung ist fest: Die Rechnung ist überfällig. Die richtige Reaktion hängt aber vom Text ab. Meldet der Kunde einen Mangel, wäre eine Mahnung falsch, der Fall gehört zum Kundendienst. Kündigt er die Zahlung an, warten wir ab. Hat er Zahlungsschwierigkeiten, geht der Fall an das Credit Management. Hat der Text keinen Bezug, folgt die Mahnung.

Im Pilot sind E2, E3 und E6. E5 und E7 sind im Log enthalten und folgen später. Wichtig: Das Sprachmodell erkennt keine Ausnahmen. Es interpretiert nur den markierten Fall.

**Überleitung:** Wie weit kommt man hier mit festen Regeln?

### Folie 8: Baseline

| Sprecher | Start | Dauer | Wörter |
|---|---|---|---|
| Minh Sang | 6:40 | 1:20 | 164 |

Zuerst zur Datenqualität. Jeder Fall hat eine Ground Truth: die zulässigen Aktionen und die Zielrolle. Bewertet wird mit exaktem Mengenvergleich. 70 normale Fälle haben einen irrelevanten Freitext, damit wir Fehlalarme messen können. 35 Grenzfälle liegen knapp unter einer Schwelle. Wir haben absichtlich falsche Regeln getestet, etwa grösser-gleich statt grösser. Jede solche Variante erzeugt 11 bis 23 Fehler. Die Daten decken Regelfehler also auf.

Unsere Baseline ist eine feste Regel plus ein Keyword-Klassifikator für den Freitext. Bei E2 und E3 erreicht sie 120 von 120, bei den Fällen mit irrelevantem Text 70 von 70. Das ist erwartbar, weil Regel und Ground Truth aus derselben Spezifikation stammen. Bei E6 sind es nur 59 von 80, bei indirekt formulierten Texten 11 von 32.

Ein Beispiel, Fall C0244: «Von den 40 Kartons waren 12 durchnässt. Der Inhalt ist nicht mehr brauchbar.» Kein Schlüsselwort wie Reklamation, also mahnt die Regel. Richtig wäre der Kundendienst.

**Überleitung:** Hier muss der Agent zeigen, dass er mehr kann. Andrin erklärt, wie er aufgebaut ist.

*Sprecherwechsel, 0:10*

---

## 3. Agent (Andrin)

### Folie 9: Handlungskatalog und Autonomiestufen

| Sprecher | Start | Dauer | Wörter |
|---|---|---|---|
| Andrin | 8:10 | 1:00 | 130 |

Der Agent darf nur aus acht Aktionen wählen. Der Katalog ist abschliessend. A0 bis A4 führt er selbst aus: keine Massnahme, Information anfordern, Kunde informieren, nächsten Schritt empfehlen, priorisieren. Diese Aktionen sind nachträglich sichtbar. A5 bis A7 brauchen eine Freigabe: neu zuweisen, eskalieren, Fall sperren. Hier entscheidet ein Mensch vor der Ausführung. Alle Aktionen sind im Prototyp simuliert. Bei A5 und A6 nennt der Agent zusätzlich die Zielrolle, etwa Credit Management oder Kundendienst.

A0 ist Pflicht. Ohne "keine Massnahme" könnten wir Fehlalarme nicht messen.

Kann der Agent einen Fall nicht einordnen, soll er sich enthalten: Typ unknown und Eskalation. Der Fall geht dann an einen Menschen. Ob das Modell diese Option nutzt, zeigen die Ergebnisse.

Autonomie ist also pro Aktion abgestuft, nicht alles oder nichts.

**Überleitung:** Wie ist das technisch umgesetzt?

### Folie 10: Architektur, deterministische Hülle um das LLM

| Sprecher | Start | Dauer | Wörter |
|---|---|---|---|
| Andrin | 9:10 | 1:30 | 195 |

Die Pipeline läuft von links nach rechts. Nur ein Baustein ist nicht deterministisch: das Sprachmodell, hier orange. Alles davor und danach ist Code mit festen Regeln.

Vier Kontrollbausteine. Erstens: Die Erkennung arbeitet ohne Sprachmodell, mit festen Regeln auf Tagesbasis. Das Modell sieht nur markierte Fälle, und zwar als Fallobjekt: Attribute, Verlauf bis zum Stichtag, abgeleitete Werte wie Tage überfällig und das Ergebnis der Erkennung. Die Ground Truth enthält es nicht. Pro Aufruf sind das rund 2000 Tokens Eingabe. Zweitens: Das Ausgabeformat ist erzwungen. Ollama gibt nur JSON nach unserem Schema aus. Belege und Begründung stehen vor der Entscheidung und sind Pflicht. Temperatur 0, fester Seed. Drittens: Sieben Guardrails prüfen jede Ausgabe vor der Ausführung, zum Beispiel Katalog, Autonomiestufe, Zielrolle und Fall-ID. Bei einem Verstoss wird blockiert und an einen Menschen übergeben, ohne Neuversuch. Viertens: Ein Audit-Log hält jede Entscheidung fest, mit Modell-Digest und Hashes von Prompt und Fallobjekt.

Das Modell ist Qwen 3.5 mit 9 Milliarden Parametern, quantisiert, lokal auf einem MacBook über Ollama. Keine Cloud.

Wichtig: Temperatur 0 allein garantiert keine gleichen Antworten. Deshalb messen wir die Reproduzierbarkeit. Und: Guardrails prüfen die Form, nicht ob eine Entscheidung fachlich stimmt.

**Überleitung:** Jan zeigt das jetzt live.

*Sprecherwechsel, 0:10 (Jan wechselt mit Cmd+Tab ins Terminal, Tab 2)*

---

## 4. Demo und Ergebnisse (Jan)

### Folie 11: Live-Demo

| Sprecher | Start | Dauer | Wörter |
|---|---|---|---|
| Jan | 10:50 | 4:00 | 401 |

Ablauf, Tasten und Notfallplan: `docs/demo_drehbuch.md` Abschnitte 0, 2 und 4. Rund 30 s der 4:00 sind Wartezeit (3 × ca. 7 s LLM) und Tasten. Zeiten in Klammern ab Beginn der Demo.

**(0:00 bis 0:20) Kopf**

Das ist die Pipeline von eben, lokal und offline. Die Konfiguration ist dieselbe wie in der Auswertung: gleiches Modell, gleicher Prompt, Temperatur 0, Seed 42. Ich zeige drei Fälle: E2, E3 und E6.

**(0:20 bis 1:15) Fall 1, C0902, E2**

[Enter]
Fall eins, C0902. Limit 100'000 Franken, Engagement 132'431, also 32 Prozent darüber. Die Zahlungshistorie ist schlecht. Die Ausnahme erkennt die Regel, nicht das Sprachmodell. Das Modell bekommt nur dieses Fallobjekt, den Katalog und die Zuordnung. An diesem Fall haben wir den Prompt nicht nachgeschärft.
[ca. 7 s, AGENT erscheint]
Der Agent eskaliert an das Credit Management. Die Regel macht dasselbe, und das ist laut Ground Truth korrekt.
[auf die Begründung zeigen]
Schauen Sie auf die Begründung: Da steht "automatische Weiterleitung". Das stimmt nicht. A6 braucht eine Freigabe, das System hält an. Die Begründung ist Text des Modells und nicht geprüft. Sie nennt die richtige Information, ist aber keine verlässliche Erklärung. Die Kontrolle leistet die Freigabe.
[`j`, Enter]
Ich gebe frei. Name und Zeit stehen im Audit-Log. Unten steht: bytegleich mit dem Evaluationslauf. Bei Temperatur 0 ist die Ausgabe auf diesem Rechner Zeichen für Zeichen gleich. Das heisst reproduzierbar, nicht korrekt.

**(1:15 bis 1:50) Fall 2, C0537, E3**

[Enter]
Fall zwei, C0537. Liefertermin morgen, kommissioniert, nicht versendet.
[ca. 7 s]
Der Agent priorisiert und informiert den Kunden. Beides ist autonom, es gibt keine Freigabefrage. Die Aktionen laufen sofort, simuliert, und sind nachträglich sichtbar. Die Regel macht dasselbe. Bei deterministischen Fällen gibt es keinen Mehrwert. Das war erwartet. Übrigens wählt das Modell bei E3 mit Temperatur 0 immer beide Aktionen, unabhängig davon, wie knapp der Termin ist.

**(1:50 bis 3:10) Fall 3, C0244, E6**

[Enter]
Fall drei, C0244. Rechnung 39 Tage überfällig, schlechte Zahlungshistorie. Der Kunde schreibt: 12 von 40 Kartons durchnässt, Inhalt unbrauchbar. Klassisch wäre jetzt die Mahnung. Im Text steht aber kein Wort wie Reklamation.
[ca. 7 s]
Die Keyword-Regel findet kein Schlüsselwort, stuft den Text als irrelevant ein und mahnt. Der Agent erkennt den Mangel und weist den Fall dem Kundendienst zu. Das ist laut Ground Truth richtig. Eine Einschränkung: Texte, Kategoriedefinitionen und Labels stammen vom selben Autor. Das Ergebnis ist eine Obergrenze, dazu gleich mehr. Und auch hier prüfen die Guardrails nur die Form.
[`j`, Enter]
Ich gebe die Zuweisung frei.

**(3:10 bis 3:40) Zusammenfassung**

Jede Entscheidung steht im Audit-Log: Input, Rohausgabe, Guardrails, Freigabe mit Name und Zeit. Das Sprachmodell wählt nur aus dem Katalog. Erkennung, Freigabe und Protokoll sind deterministisch. Jeder Lauf lässt sich später nachlesen und mit dem Evaluationslauf vergleichen.

**(3:40 bis 4:00) Zurück zu den Folien**

Drei ausgewählte Fälle sind eine Illustration, kein Beleg. E2 und E3 sind durch die Zuordnung vorgegeben.

**Überleitung:** Wie gut das über alle 80 E6-Fälle trägt und wo der Agent falsch liegt, zeige ich jetzt.

**Bei Fallback (Replay, Tab 3), Ansage:** Ich zeige die Aufzeichnung desselben Laufs. Bei Temperatur 0 ist sie Zeichen für Zeichen identisch.

**Reserve C0776 (nur bei Fragen, ca. 45 s, nicht im Zeitplan):** Hier kündigt der Kunde die Zahlung an. Richtig wäre abwarten. Das Modell deutet die Ankündigung als Bitte um Aufschub und erfindet eine Zahlungsvereinbarung. Die Guardrails lassen es durch, weil die Ausgabe formal korrekt ist. [`n`, Grund "Zahlung angekuendigt", Enter] Hier greift die Freigabe: Ich lehne ab, nichts wird ausgeführt. Bei einer autonomen Aktion gäbe es diese Kontrolle nicht.

### Folie 12 (neu): Erste Ergebnisse

| Sprecher | Start | Dauer | Wörter |
|---|---|---|---|
| Jan | 14:50 | 2:20 | 294 |

Zuerst die deterministischen Fälle, also E2, E3 und Happy Path. Der Agent trifft 51 von 51, die Regel 17 von 17. Das ist kein Befund. Typ und Zuordnung stehen im Fallobjekt und im Prompt. Und wir haben den Prompt an drei Pilotfällen nachgeschärft.

Ein Mehrwert ist nur bei E6 messbar. Dafür haben wir den Agenten auf alle 80 E6-Fälle angesetzt. Bei direkt formulierten Texten sind Agent und Regel gleich: 43 von 43. Bei indirekt formulierten Texten trifft der Agent 31 von 32, die Regel 11 von 32. Der einzige E6-Fehler: Ein Kunde kündigt die Zahlung an, das Modell eskaliert trotzdem an das Credit Management. Den fängt die Freigabe ab.

Diese Zahl hat eine klare Grenze. Texte, Kategoriedefinitionen im Prompt und Labels stammen vom selben Autor, von Claude. Die Definitionen treffen die indirekten Texte fast wörtlich. Dass die Keyword-Regel dort scheitert, ist zudem konstruktionsbedingt: Indirekt heisst bei uns ohne Schlüsselwort. 31 von 32 ist deshalb eine Obergrenze. Wie der Agent auf fremde Texte reagiert, haben wir noch nicht gemessen. Das folgt in der zweiten Iteration.

Zur Reproduzierbarkeit: Bei Temperatur 0 sind alle Ausgaben bytegleich, auch über Sitzungen, und es gab keinen Fehlalarm. Ein Aufruf dauert rund sieben Sekunden. Bei Temperatur 0,7 bleibt die Entscheidung stabil. Ausnahmen sind E3, wo der Prompt die Wahl freilässt, und ein Fehlalarm: Ein normaler Fall bekam eine Mahnungsempfehlung, autonom, ohne Freigabe.

Zu den Begründungen: Sie nennen die ausschlaggebende Information immer, 18 von 18. Sie sind aber nicht immer treu. Im Mittel 1,56 von 2 Punkten, 8 von 18 mit Abzug. Einmal spricht die Begründung sogar gegen die gewählte Aktion. Bewertet hat das ebenfalls Claude, regelgeleitet, aber nicht unabhängig.

Und die Guardrails haben in 182 Aufrufen nichts blockiert. Beide Fehler waren formal korrekt.

**Überleitung:** Was heisst das für die Aussagekraft? Minh Sang.

*Sprecherwechsel, 0:10*

---

## 5. Einordnung und Plan (Minh Sang)

### Folie 13: Kritische Einordnung

| Sprecher | Start | Dauer | Wörter |
|---|---|---|---|
| Minh Sang | 17:20 | 1:20 | 168 |

Wir kennen die Schwachstellen unserer Zahlen. Sechs Punkte.

Erstens Zirkularität: Daten, Erkennung und Ground Truth folgen derselben Spezifikation, Texte und Labels stammen von Claude. Deshalb werten wir 100 Prozent Erkennung nicht als Erfolg und berichten E6 als Obergrenze. Gegenmassnahme: ein Test mit fremden Texten.

Zweitens: Bei E2 und E3 bekommt der Agent den Typ vorgegeben. 100 Prozent dort sind kein Befund.

Drittens: Guardrails prüfen nur die Form. Den einen E6-Fehler fängt die Freigabe ab. Den Fehlalarm bei Temperatur 0,7 nicht, weil die Aktion autonom ist. Ein Guardrail, der Aktionen gegen den erkannten Typ prüft, hätte den Fehlalarm blockiert, den E6-Fehler nicht.

Viertens: Begründungen sind kein verlässlicher Beleg dafür, warum entschieden wurde.

Fünftens: Das Modell hat sich nie enthalten, 0 von 182. Ob es Unsicherheit erkennt, ist nicht gezeigt.

Sechstens: Die Stichprobe ist klein. Die 80 E6-Fälle stammen aus 34 Textvorlagen. Pro Vorlage gerechnet ist der Agent bei 8 besser und bei keiner schlechter. Die Richtung ist klar, die Grösse des Effekts nicht.

**Überleitung:** Was wir bis Januar daraus machen.

### Folie 14: Zwischenstand und Plan bis Januar 2027

| Sprecher | Start | Dauer | Wörter |
|---|---|---|---|
| Minh Sang | 18:40 | 1:10 | 148 |

Erreicht haben wir einen durchgängigen Prototyp. Spezifikation, Event Log mit 1000 Fällen und 43 bestandenen Prüfungen, Erkennung und Baseline. Dazu der Agent mit Guardrails, Freigabe und Audit-Log, 182 Aufrufe mit dem lokalen Modell, die Demo und 44 automatisierte Tests.

Bis Januar gehen wir die Grenzen von eben an. Wir setzen E5 und E7 um. E7, den Zielkonflikt, lassen wir von mindestens einer Person labeln. Wir testen den Agenten auf fremden Texten, gelabelt von Modellen ausserhalb der Qwen-Familie. Dieser Test prüft direkt die Obergrenze von heute. Die Begründungen bewertet mindestens eine Person. Dann folgt die volle Evaluation mit fünf Läufen pro Fall, rund dreieinhalb Stunden Rechenzeit. Als Ausblick prüfen wir einen Guardrail, der Aktionen gegen den erkannten Typ prüft. Im Januar folgen Bericht und Schlusspräsentation. [TODO: Monatszuordnung bestätigen]

An die Betreuung haben wir vier Fragen: die Methodik-Vorgabe, die Form des Leistungsnachweises, ob ein lokales Modell zulässig ist, und der Termin der Schlussabgabe.

**Überleitung:** keine (direkt Folie 16).

### Folie 15: Quellen

Nicht besprechen, nur beim Weiterklicken kurz sichtbar.

### Folie 16: Dank

| Sprecher | Start | Dauer | Wörter |
|---|---|---|---|
| Minh Sang | 19:50 | 0:10 | 17 |

Vielen Dank. Wir freuen uns auf Ihre Fragen und Ihre Rückmeldung. Für Rückfragen haben wir Zusatzfolien vorbereitet.

---

## 6. Zeittabelle

| Folie | Inhalt | Sprecher | Start | Dauer | Wörter | Ende |
|---|---|---|---|---|---|---|
| 1 | Titel | Andrin | 0:00 | 0:20 | 40 | 0:20 |
| 2 | Agenda | Andrin | 0:20 | 0:30 | 61 | 0:50 |
| 3 | Ausgangslage | Andrin | 0:50 | 1:20 | 172 | 2:10 |
| 4 | Fragestellung | Andrin | 2:10 | 1:00 | 128 | 3:10 |
| 5 | Vorgehen | Andrin | 3:10 | 0:40 | 88 | 3:50 |
| | Sprecherwechsel | | 3:50 | 0:10 | | 4:00 |
| 6 | O2C, Event Log | Minh Sang | 4:00 | 1:20 | 178 | 5:20 |
| 7 | Ausnahmefälle | Minh Sang | 5:20 | 1:20 | 168 | 6:40 |
| 8 | Baseline | Minh Sang | 6:40 | 1:20 | 164 | 8:00 |
| | Sprecherwechsel | | 8:00 | 0:10 | | 8:10 |
| 9 | Handlungskatalog | Andrin | 8:10 | 1:00 | 130 | 9:10 |
| 10 | Architektur | Andrin | 9:10 | 1:30 | 195 | 10:40 |
| | Sprecherwechsel | | 10:40 | 0:10 | | 10:50 |
| 11 | Live-Demo | Jan | 10:50 | 4:00 | 401 | 14:50 |
| 12 | Ergebnisse (neu) | Jan | 14:50 | 2:20 | 294 | 17:10 |
| | Sprecherwechsel | | 17:10 | 0:10 | | 17:20 |
| 13 | Kritische Einordnung | Minh Sang | 17:20 | 1:20 | 168 | 18:40 |
| 14 | Plan bis Januar | Minh Sang | 18:40 | 1:10 | 148 | 19:50 |
| 15 | Quellen | | | 0:00 | | |
| 16 | Dank | Minh Sang | 19:50 | 0:10 | 17 | 20:00 |
| | **Summe** | | | **20:00** | **2352** | |

| Person | Folien | Minuten |
|---|---|---|
| Andrin | 1 bis 5, 9, 10 | 6:20 |
| Minh Sang | 6 bis 8, 13, 14, 16 | 6:40 |
| Jan | 11, 12 | 6:20 |
| Sprecherwechsel | 4 × 0:10 | 0:40 |
| **Summe** | | **20:00** |

Rechnung bei 130 Wörtern pro Minute: 2352 Wörter = 18:06, dazu 0:30 Wartezeit in der Demo und 0:40 Sprecherwechsel = 19:16. Die restlichen rund 45 s liegen vor allem in der Demo (Tippen, Zeigen) und sind die einzige Reserve. Wer schneller als 130 spricht, wird früher fertig. Die Sprechzeit der Demo ist nicht gemessen (`out/step6_report.md` Abschnitt 5). Erst der Probevortrag mit Stoppuhr zeigt, ob 20:00 hält.

## 7. Kürzungen (je etwa 30 s), falls die Zeit nicht reicht

| # | Wo | Was streichen | Gewinn |
|---|---|---|---|
| 1 | Folie 3 (Andrin) | Absatz "Heute gibt es dafür zwei Werkzeuge ..." auf einen Satz kürzen: "Process Mining zeigt Abweichungen im Nachhinein, feste Regeln scheitern an Freitext." | ca. 0:30 |
| 2 | Folie 6 (Minh Sang) | Absatz zum Stichtag und zu den Zahlen unter den Schritten (442, 35 Varianten, 31 Prozent) weglassen. Steht auf der Folie | ca. 0:30 |
| 3 | Folie 11 (Jan) | Sprechtext bei Fall 2 auf "Autonom, keine Freigabe, die Regel macht dasselbe" kürzen und die Zusammenfassung (3:10 bis 3:40) streichen. Kürzungsstellen laut `out/step6_report.md` Abschnitt 7 | ca. 0:30 |
| 4 | Folie 13 (Minh Sang) | Punkte 2 und 4 nur zeigen, nicht sprechen (sie wiederholen Folie 12) | ca. 0:25 |

Nicht kürzen: die Einschränkung bei 31 von 32 (Folie 11 und 12, D-K5-5) und den Satz "Illustration, kein Beleg" am Ende der Demo.
