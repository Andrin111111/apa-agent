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
| Minh Sang | 4:00 | 1:20 | 185 |

Unser Referenzprozess ist Order-to-Cash in acht Schritten: Auftrag erfassen, Kreditprüfung, bestätigen, kommissionieren, versenden, Rechnung stellen, Zahlungseingang, Abschluss. Dazu kommen drei zulässige Varianten: Auftrag ändern, Teillieferung und Zahlungserinnerung.

Die Daten sind ein synthetisches Event Log: 1000 Aufträge, 5905 Events, Fallstart zwischen Januar und Juni 2026. Jedes Event hat Aktivität, Zeitstempel, Ressource und Rolle. Zu jedem Auftrag kennen wir ausserdem Auftragswert, Kreditlimit, offene Posten, Zahlungshistorie und, falls vorhanden, eine Nachricht des Kunden. 70 Prozent sind normale Fälle, der Rest verteilt sich auf die fünf Ausnahmetypen. Warum synthetisch? Öffentliche Logs zeigen, was passiert ist, aber nicht, was die richtige Reaktion gewesen wäre. Diese Ground Truth brauchen wir für die Bewertung.

Jeder Fall wird zu einem Stichtag betrachtet. Die Zahlen unter den Schritten zeigen, wie viele Fälle den Schritt bis dahin erreicht haben. Alle 1000 starten, 442 sind abgeschlossen, die übrigen laufen noch. Deshalb zählen wir 35 Varianten, viele davon unfertige Abläufe. 31 Prozent der Fälle durchlaufen den kompletten Normalablauf ohne Abweichung.

Die orangen Marken zeigen, wo die Erkennung auf Ausnahmen prüft: Kreditlimit, Lieferverzug, Rechnung vor Versand und Zahlungsverzug.

**Überleitung:** Welche Ausnahmen das genau sind, zeigt die nächste Folie.

### Folie 7: Ausnahmefälle, feste Regel oder Ermessen

| Sprecher | Start | Dauer | Wörter |
|---|---|---|---|
| Minh Sang | 5:20 | 1:20 | 175 |

Wir unterscheiden zwei Arten von Ausnahmen. Bei deterministischen Fällen bestimmt eine feste Regel die Erkennung und die Reaktion. E2: Auftragswert plus offene Posten liegen über dem Kreditlimit. Dann geht der Fall an das Credit Management. E3: Der Liefertermin ist in weniger als zwei Tagen oder schon verpasst, und es wurde nicht versendet. Dann wird priorisiert, der Kunde informiert oder beides.

Bei Ermessensfällen reicht die Regel nicht. E6 ist ein Zahlungsverzug mit einer Nachricht des Kunden. Die Erkennung ist fest: Die Rechnung ist überfällig. Die richtige Reaktion hängt aber vom Text ab. Meldet der Kunde einen Mangel, wäre eine Mahnung falsch, der Fall gehört zum Kundendienst. Kündigt er die Zahlung an, warten wir ab. Hat er Zahlungsschwierigkeiten, geht der Fall an das Credit Management. Hat der Text keinen Bezug, folgt die Mahnung.

Im Pilot sind E2, E3 und E6. E5 und E7 sind im Log enthalten und folgen später. Wichtig: Ob ein Fall eine Ausnahme ist, prüfen feste Regeln. Das Sprachmodell entscheidet danach nur, was zu tun ist.

**Überleitung:** Wie weit kommt man hier mit festen Regeln?

### Folie 8: Baseline

| Sprecher | Start | Dauer | Wörter |
|---|---|---|---|
| Minh Sang | 6:40 | 1:20 | 168 |

Zuerst zur Datenqualität. Jeder Fall hat eine Ground Truth: die zulässigen Aktionen und die Zielrolle. Bewertet wird mit exaktem Mengenvergleich. 70 normale Fälle haben einen irrelevanten Freitext, damit wir Fehlalarme messen können. 35 Grenzfälle liegen knapp unter einer Schwelle. Wir haben die Regeln absichtlich leicht verfälscht, zum Beispiel grösser-gleich statt grösser. Jede Verfälschung führt zu 11 bis 23 falsch erkannten Fällen. Ein solcher Programmierfehler würde also auffallen.

Unsere Baseline ist eine feste Regel plus ein Keyword-Klassifikator für den Freitext. Bei E2 und E3 erreicht sie 120 von 120, bei den Fällen mit irrelevantem Text 70 von 70. Das ist erwartbar, weil Regel und Ground Truth aus derselben Spezifikation stammen. Bei E6 sind es nur 59 von 80, bei indirekt formulierten Texten 11 von 32.

Ein Beispiel, Fall C0244: «Von den 40 Kartons waren 12 durchnässt. Der Inhalt ist nicht mehr brauchbar.» Kein Schlüsselwort wie Reklamation, also mahnt die Regel. Richtig wäre der Kundendienst.

**Überleitung:** Hier muss der Agent zeigen, dass er mehr kann. Andrin erklärt, wie er aufgebaut ist.

*Sprecherwechsel, 0:10*

---

## 3. Agent (Andrin)

### Folie 9: Handlungskatalog und Autonomiestufen

| Sprecher | Start | Dauer | Wörter |
|---|---|---|---|
| Andrin | 8:10 | 1:00 | 141 |

Der Agent darf nur aus acht Aktionen wählen. Der Katalog ist abschliessend. A0 bis A4 führt er selbst aus: keine Massnahme, Information anfordern, Kunde informieren, nächsten Schritt empfehlen, priorisieren. Diese Aktionen sind nachträglich sichtbar. A5 bis A7 brauchen eine Freigabe: neu zuweisen, eskalieren, Fall sperren. Hier entscheidet ein Mensch vor der Ausführung. Alle Aktionen sind im Prototyp simuliert. Bei A5 und A6 nennt der Agent zusätzlich die Zielrolle, etwa Credit Management oder Kundendienst.

A0, keine Massnahme, ist Pflicht. Ohne diese Option müsste der Agent immer handeln. Wir könnten dann nicht prüfen, ob er unnötig eingreift.

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
| Jan | 10:50 | 4:00 | 438 |

Ablauf, Tasten und Notfallplan: `docs/demo_drehbuch.md` Abschnitte 0, 2 und 4. Rund 30 s der 4:00 sind Wartezeit (3 × ca. 7 s LLM) und Tasten. Zeiten in Klammern ab Beginn der Demo.

**(0:00 bis 0:20) Kopf**

Was Sie jetzt sehen, ist die Pipeline von der letzten Folie. Sie läuft hier auf dem Rechner, ohne Internet. Eingestellt ist alles wie in unserer Auswertung, also gleiches Modell, gleicher Prompt und Temperatur null. Ich zeige Ihnen drei Fälle: ein überschrittenes Kreditlimit, einen drohenden Lieferverzug und einen Zahlungsverzug.

**(0:20 bis 1:15) Fall 1, C0902, E2**

[Enter]
Der erste Fall ist C0902. Der Kunde hat ein Limit von 100'000 Franken, steht aber bei gut 132'000, 32 Prozent darüber, und zahlt schlecht. Gefunden hat das die Regel, nicht das Sprachmodell. Das Modell sieht nur diesen Fall, den Katalog und die Zuordnung. An diesem Fall haben wir den Prompt nicht angepasst.
[ca. 7 s, AGENT erscheint]
Der Agent eskaliert ans Credit Management. Die Regel würde dasselbe tun, und laut Ground Truth ist das richtig.
[auf die Begründung zeigen]
Schauen Sie kurz auf die Begründung: "automatische Weiterleitung". Das stimmt nicht, eine Eskalation braucht eine Freigabe, das System wartet auf mich. Die Begründung schreibt das Modell selbst, und niemand prüft sie. Die eigentliche Kontrolle ist die Freigabe.
[`j`, Enter]
Ich gebe frei, mein Name und die Uhrzeit landen im Audit-Log. Unten sehen Sie: bytegleich mit der Auswertung. Bei Temperatur null kommt hier also Zeichen für Zeichen dasselbe heraus. Das heisst aber nur reproduzierbar, nicht richtig.

**(1:15 bis 1:50) Fall 2, C0537, E3**

[Enter]
Der zweite Fall ist C0537. Der Liefertermin ist morgen, die Ware ist kommissioniert, aber noch nicht versendet.
[ca. 7 s]
Der Agent priorisiert den Auftrag und informiert den Kunden. Das darf er allein, darum kommt keine Freigabefrage. Die Aktionen laufen sofort, simuliert, und stehen danach im Log. Die Regel würde dasselbe tun, hier bringt der Agent also nichts, wie erwartet. Übrigens wählt das Modell bei Temperatur null hier immer beide Aktionen, egal wie knapp der Termin ist.

**(1:50 bis 3:10) Fall 3, C0244, E6**

[Enter]
Der dritte Fall ist C0244. Die Rechnung ist seit 39 Tagen überfällig, und der Kunde zahlt schlecht. Normalerweise würde man jetzt mahnen. Der Kunde schreibt aber, dass von 40 Kartons 12 durchnässt waren und der Inhalt unbrauchbar ist. Das Wort Reklamation kommt nicht vor.
[ca. 7 s]
Die Keyword-Regel findet kein Schlüsselwort, hält den Text für irrelevant und mahnt. Der Agent erkennt den Mangel und gibt den Fall an den Kundendienst. Laut Ground Truth ist das richtig. Allerdings stammen Texte, Definitionen und Labels vom selben Autor. Das Ergebnis ist also eine Obergrenze, dazu gleich mehr.
[`j`, Enter]
Auch diese Zuweisung gebe ich frei.

**(3:10 bis 3:40) Zusammenfassung**

Kurz zusammengefasst: Jede Entscheidung landet im Audit-Log, mit Input, Antwort des Modells, Prüfung und Freigabe. Das Sprachmodell wählt nur aus dem Katalog. Alles andere läuft nach festen Regeln. So kann man jeden Lauf später nachlesen und mit der Auswertung vergleichen.

**(3:40 bis 4:00) Zurück zu den Folien**

Drei ausgewählte Fälle sind eine Illustration, kein Beleg. Bei Kreditlimit und Lieferverzug war die Antwort ohnehin vorgegeben.

**Überleitung:** Wie gut das über alle 80 Fälle mit Zahlungsverzug funktioniert und wo der Agent danebenliegt, sehen Sie jetzt.

**Bei Fallback (Replay, Tab 3), Ansage:** Ich zeige Ihnen stattdessen die Aufzeichnung desselben Laufs. Bei Temperatur null ist sie Zeichen für Zeichen identisch.

**Reserve C0776 (nur bei Fragen, ca. 45 s, nicht im Zeitplan):** Hier kündigt der Kunde an, dass er zahlt. Richtig wäre also, abzuwarten. Das Modell versteht das aber als Bitte um Aufschub und erfindet eine Zahlungsvereinbarung. Die Guardrails lassen das durch, weil die Antwort formal korrekt ist. [`n`, Grund "Zahlung angekuendigt", Enter] Genau hier hilft die Freigabe: Ich lehne ab, und es wird nichts ausgeführt. Wäre die Aktion autonom, gäbe es diese Kontrolle nicht.

### Folie 12 (neu): Erste Ergebnisse

| Sprecher | Start | Dauer | Wörter |
|---|---|---|---|
| Jan | 14:50 | 2:20 | 313 |

Zuerst zu den klaren Fällen, also Kreditlimit, Lieferverzug und normale Fälle. Hier trifft der Agent 51 von 51, die Regel 17 von 17. Das klingt gut, ist aber kein Befund. Typ und passende Aktion stehen ja schon im Fallobjekt und im Prompt. Ausserdem haben wir den Prompt an drei Pilotfällen nachgeschärft.

Einen Mehrwert kann der Agent nur beim Zahlungsverzug zeigen. Darum lief er über alle 80 dieser Fälle. Schreibt der Kunde direkt, was los ist, sind beide gleich gut, 43 von 43. Deutet er es nur an, trifft der Agent 31 von 32, die Regel nur 11. Falsch lag der Agent nur einmal: Der Kunde kündigt die Zahlung an, und das Modell eskaliert trotzdem. Das fängt die Freigabe ab.

Diese Zahl müssen wir klar einschränken. Texte, Definitionen im Prompt und Labels stammen alle vom selben Autor, von Claude. Die Definitionen passen deshalb fast wörtlich auf die indirekten Texte. Und dass die Keyword-Regel dort scheitert, liegt an der Konstruktion: Indirekt heisst bei uns, ohne Schlüsselwort. 31 von 32 ist also eine Obergrenze. Wie der Agent mit fremden Texten umgeht, messen wir erst in der zweiten Iteration.

Zur Reproduzierbarkeit: Bei Temperatur null sind alle Antworten bytegleich, auch über Sitzungen hinweg, und es gab keinen Fehlalarm. Bei Temperatur 0,7 bleibt die Entscheidung meistens gleich. Ausnahmen sind der Lieferverzug, wo der Prompt die Wahl offenlässt, und ein Fehlalarm: Ein normaler Fall bekam eine Mahnungsempfehlung, autonom, ohne Freigabe.

Und die Begründungen? Die entscheidende Information nennen sie immer, 18 von 18. Sie erklären aber nicht immer zuverlässig, wie die Entscheidung zustande kam. Im Schnitt gab es 1,56 von 2 Punkten, 8 von 18 bekamen Abzug. Einmal spricht die Begründung sogar gegen die gewählte Aktion. Bewertet hat das auch Claude, nach festen Regeln, aber nicht unabhängig.

Die Guardrails haben in 182 Aufrufen kein einziges Mal blockiert. Beide Fehler waren eben formal korrekt.

**Überleitung:** Was heisst das für die Aussagekraft? Minh Sang.

*Sprecherwechsel, 0:10*

---

## 5. Einordnung und Plan (Minh Sang)

### Folie 13: Kritische Einordnung

| Sprecher | Start | Dauer | Wörter |
|---|---|---|---|
| Minh Sang | 17:20 | 1:20 | 310 |

Unsere Ergebnisse haben Grenzen. Wir zeigen Ihnen sechs davon und jeweils, was wir dagegen tun.

Das grösste Problem: Wir prüfen uns ein Stück weit selbst. Daten, Erkennung und richtige Antworten kommen aus derselben Spezifikation, und die Kundentexte samt Labels hat Claude geschrieben. Die 31 von 32 sind darum eher eine Obergrenze. Ehrlich messen können wir das erst mit fremden Texten. Das machen wir in der zweiten Iteration.

Dann die Begründungen. Die entscheidende Information nennt das Modell immer. Ob die Begründung aber wirklich erklärt, warum es so entschieden hat, ist eine andere Frage. 8 von 18 bekamen dafür Abzug. Wir nutzen sie deshalb nicht als Erklärung, und später sollen Menschen sie bewerten statt Claude.

Bei Kreditlimit und Lieferverzug bekommt der Agent die erkannte Ausnahme und die passende Aktion praktisch mitgeliefert. Dass er dort alles trifft, sagt also wenig. Einen echten Mehrwert messen wir deshalb nur beim Zahlungsverzug. Später testen wir auch einen Prompt ohne diese Vorgabe.

Das Modell hätte jederzeit sagen dürfen, dass es unsicher ist. Das hat es in 182 Aufrufen nie getan. Ob es Unsicherheit überhaupt merkt, wissen wir also nicht. Darum bleibt bei heiklen Aktionen ein Mensch in der Freigabe.

Die Guardrails haben nie blockiert, weil sie nur prüfen, ob die Antwort formal stimmt, und nicht, ob sie inhaltlich richtig ist. Den einen Fehler hat die Freigabe abgefangen, den anderen nicht, weil die Aktion autonom lief. Eine Prüfung, ob die Aktion zum erkannten Typ passt, hätte ihn verhindert. Die nehmen wir als Ausblick mit.

Und schliesslich ist die Stichprobe klein. Die 80 Fälle mit Zahlungsverzug beruhen auf nur 34 Textvorlagen. Pro Vorlage gerechnet ist der Agent bei 8 besser als die Regel und bei keiner schlechter. Die Richtung ist also klar, die Grösse des Vorteils noch nicht. Bis Januar folgt die volle Auswertung mit fünf Läufen pro Fall.

**Überleitung:** Wie es konkret weitergeht, sehen Sie auf der nächsten Folie.

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
| 6 | O2C, Event Log | Minh Sang | 4:00 | 1:20 | 185 | 5:20 |
| 7 | Ausnahmefälle | Minh Sang | 5:20 | 1:20 | 175 | 6:40 |
| 8 | Baseline | Minh Sang | 6:40 | 1:20 | 168 | 8:00 |
| | Sprecherwechsel | | 8:00 | 0:10 | | 8:10 |
| 9 | Handlungskatalog | Andrin | 8:10 | 1:00 | 141 | 9:10 |
| 10 | Architektur | Andrin | 9:10 | 1:30 | 195 | 10:40 |
| | Sprecherwechsel | | 10:40 | 0:10 | | 10:50 |
| 11 | Live-Demo | Jan | 10:50 | 4:00 | 438 | 14:50 |
| 12 | Ergebnisse (neu) | Jan | 14:50 | 2:20 | 313 | 17:10 |
| | Sprecherwechsel | | 17:10 | 0:10 | | 17:20 |
| 13 | Kritische Einordnung | Minh Sang | 17:20 | 1:20 | 310 | 18:40 |
| 14 | Plan bis Januar | Minh Sang | 18:40 | 1:10 | 148 | 19:50 |
| 15 | Quellen | | | 0:00 | | |
| 16 | Dank | Minh Sang | 19:50 | 0:10 | 17 | 20:00 |
| | **Summe** | | | **20:00** | **2579** | |

| Person | Folien | Minuten |
|---|---|---|
| Andrin | 1 bis 5, 9, 10 | 6:20 |
| Minh Sang | 6 bis 8, 13, 14, 16 | 6:40 |
| Jan | 11, 12 | 6:20 |
| Sprecherwechsel | 4 × 0:10 | 0:40 |
| **Summe** | | **20:00** |

Rechnung bei 130 Wörtern pro Minute: 2579 Wörter = 19:50, dazu 0:30 Wartezeit in der Demo und 0:40 Sprecherwechsel = 21:00. [TODO: rund 1:00 zu lang, seit Folie 13 ausführlicher ist. Ausgleich offen, siehe Kürzungen.] Wer schneller als 130 spricht, wird früher fertig. Die Sprechzeit der Demo ist nicht gemessen (`out/step6_report.md` Abschnitt 5). Erst der Probevortrag mit Stoppuhr zeigt, ob 20:00 hält.

## 7. Kürzungen (je etwa 30 s), falls die Zeit nicht reicht

| # | Wo | Was streichen | Gewinn |
|---|---|---|---|
| 1 | Folie 3 (Andrin) | Absatz "Heute gibt es dafür zwei Werkzeuge ..." auf einen Satz kürzen: "Process Mining zeigt Abweichungen im Nachhinein, feste Regeln scheitern an Freitext." | ca. 0:30 |
| 2 | Folie 6 (Minh Sang) | Absatz zum Stichtag und zu den Zahlen unter den Schritten (442, 35 Varianten, 31 Prozent Normalablauf) weglassen. Steht auf der Folie | ca. 0:30 |
| 3 | Folie 11 (Jan) | Sprechtext bei Fall 2 auf "Autonom, keine Freigabe, die Regel macht dasselbe" kürzen und die Zusammenfassung (3:10 bis 3:40) streichen. Kürzungsstellen laut `out/step6_report.md` Abschnitt 7 | ca. 0:30 |
| 4 | Folie 13 (Minh Sang) | Kästchen "Begründung nicht treu" und "Leakage" (oben Mitte und oben rechts) nur zeigen, nicht sprechen (sie wiederholen Folie 12) | ca. 0:40 |

Nicht kürzen: die Einschränkung bei 31 von 32 (Folie 11 und 12, D-K5-5) und den Satz "Illustration, kein Beleg" am Ende der Demo.
