# K2-Stichprobe (kompakt)

## Review durch Claude (01.11.2026)

**Ergebnis:** 60 von 60 Fällen konsistent, Validierung 43/43. Verlauf, Stichtag, Kennwerte und Soll-Aktion passen zu den Regeln. Einschränkung: Claude prüft hier Daten aus eigenem Code. Unabhängig ist nur die Validierung.

| # | Befund | Massnahme |
|---|---|---|
| 1 | 53 Stichtage lagen nach dem 31.10.2026 (Daten "aus der Zukunft") | behoben: Fallstart bis 30.06.2026, spätester Stichtag jetzt 21.09.2026 |
| 2 | E6-Fälle bis 96 Tage ohne jedes Event nach der Rechnung, unrealistisch und typverratend | behoben: ab 11 Tagen Verzug in 50 % eine Zahlungserinnerung (34 von 80) |
| 3 | `irrelevant_09` (Kostenstelle auf Dokumenten) kann bei überfälliger Rechnung als Grund für Nichtzahlung gelesen werden | behoben: durch Hinweis zur Anlieferungsrampe ersetzt |
| 4 | `payment_difficulty_08` nennt "Ausgaben über CHF 5'000", widerspricht kleinen Rechnungen | behoben: durch Revision ersetzt |
| 5 | E3: teils Bestätigung und Liefertermin am selben Tag | akzeptiert, plausibel als Eilauftrag |
| 6 | E2/E7: teils noch vor der Kreditprüfung | akzeptiert, Trigger ist attributbasiert ("drohend") |
| 7 | E5: Soll A6+A7 ("Fall sperren") auch nach Versand fragwürdig | offen, betrifft nicht den Pilot, bei Umsetzung E5 klären |
| 8 | Freitexte: 20 von 40 Vorlagen überarbeitet (`source: claude-rev1`, Original in `original_claude`) | erledigt, Limitation: weiterhin ein Modell |
| 9 | Labeling (40 Vorlagen): Claude 100 %, Keyword-Klassifikator 78 %, Fehler nur bei indirekten Texten | keine Vorlage mehrdeutig, siehe `out/labeling_report.md` |
| 10 | Ground Truth um `expected_target_role` ergänzt (Entscheid 01.11.2026) | erledigt |

**Für Jan:** Befunde zur Kenntnis nehmen, dann K2 freigeben. Die Tabellen unten sind nur Beleg.

## Legende

Verlauf: Aktivitaeten in Kurzform, Zahl in Klammern = Kalendertage seit dem vorherigen Event. ERF erfassen, KRED Kreditpruefung, BEST bestaetigen, AEND aendern, KOMM kommissionieren, TEIL Teillieferung, VERS versenden, RECH Rechnung, ERIN Zahlungserinnerung, ZAHL Zahlungseingang, ABS abschliessen.
Kennwerte: Seg = Segment, Q = (Auftragswert + offene Posten) / Kreditlimit, Hist = Zahlungshistorie, Ziel = Zahlungsziel, Lief = Liefertermin minus Stichtag (Tage), Verzug = Tage ueber Faelligkeit, Warte = Tage vom letzten Event bis Stichtag.

## none

| Fall | Verlauf | Kennwerte | Freitext | Soll |
|---|---|---|---|---|
| C0162 | ERF > KRED(1) > BEST(0) > KOMM(1) > VERS(0) > RECH(1) > ZAHL(21) > ABS(0) | Seg C, Q 0.89, Hist schlecht, Ziel 30, Warte 5 | - | A0 |
| C0226 | ERF > KRED(0) > BEST(0) > KOMM(3) > VERS(1) > RECH(0) > ZAHL(43) > ABS(0) | Seg B, Q 0.40, Hist schlecht, Ziel 45, Warte 20 | - | A0 |
| C0264 | ERF > KRED(0) > BEST(0) | Seg B, Q 0.65, Hist mittel, Ziel 60, Lief +10, Warte 4 | - | A0 |
| C0399 | ERF > KRED(0) > BEST(0) > KOMM(4) > VERS(0) > RECH(1) | Seg B, Q 0.61, Hist gut, Ziel 14, Verzug -9, Warte 5 | - | A0 |
| C0461 | ERF > KRED(0) > BEST(0) > KOMM(2) > VERS(4) > RECH(1) > ZAHL(23) | Seg C, Q 0.73, Hist gut, Ziel 30, Warte 0 | - | A0 |
| C0514 | ERF > KRED(0) > BEST(0) > KOMM(1) > VERS(3) | Seg B, Q 0.41, Hist mittel, Ziel 45, Warte 2 | - | A0 |
| C0624 | ERF > KRED(0) > BEST(1) > KOMM(1) > VERS(0) > RECH(0) > ZAHL(35) > ABS(3) | Seg A, Q 0.33, Hist schlecht, Ziel 45, Warte 20 | - | A0 |
| C0664 | ERF > AEND(1) > KRED(0) | Seg A, Q 0.52, Hist gut, Ziel 30, Lief +14, Warte 4 | - | A0 |
| C0687 | ERF > KRED(0) > BEST(0) > KOMM(2) > VERS(1) > RECH(0) > ZAHL(28) > ABS(1) | Seg A, Q 0.95, Hist gut, Ziel 30, Warte 12 | - | A0 |
| C0779 | ERF > KRED(0) > BEST(0) > KOMM(3) > VERS(1) > RECH(0) > ZAHL(59) | Seg B, Q 0.59, Hist schlecht, Ziel 60, Warte 1 | - | A0 |

## E2

| Fall | Verlauf | Kennwerte | Freitext | Soll |
|---|---|---|---|---|
| C0144 | ERF > KRED(0) | Seg B, Q 1.04, Hist gut, Ziel 14, Lief +6, Warte 4 | - | A6 |
| C0145 | ERF > KRED(0) | Seg B, Q 1.14, Hist gut, Ziel 45, Lief +3, Warte 4 | - | A6 |
| C0239 | ERF | Seg B, Q 1.57, Hist gut, Ziel 30, Lief +17, Warte 2 | Gibt es Artikel 4711 auch in einer Ausfuehrung aus Edelstahl? Wir planen eine Folgebestellung. | A6 (irrelevant) |
| C0504 | ERF > AEND(1) > KRED(0) | Seg C, Q 1.76, Hist schlecht, Ziel 30, Lief +6, Warte 0 | - | A6 |
| C0534 | ERF > KRED(0) | Seg B, Q 1.09, Hist mittel, Ziel 60, Lief +5, Warte 1 | - | A6 |
| C0671 | ERF | Seg B, Q 1.58, Hist gut, Ziel 30, Lief +14, Warte 5 | - | A6 |
| C0787 | ERF > KRED(0) | Seg B, Q 1.10, Hist schlecht, Ziel 30, Lief +4, Warte 1 | - | A6 |
| C0789 | ERF > AEND(1) > AEND(1) > KRED(0) | Seg C, Q 1.10, Hist mittel, Ziel 30, Lief +13, Warte 1 | - | A6 |
| C0860 | ERF | Seg B, Q 1.00, Hist gut, Ziel 45, Lief +14, Warte 4 | - | A6 |
| C0908 | ERF > AEND(1) > AEND(0) | Seg C, Q 1.01, Hist mittel, Ziel 60, Lief +4, Warte 2 | - | A6 |

## E3

| Fall | Verlauf | Kennwerte | Freitext | Soll |
|---|---|---|---|---|
| C0097 | ERF > KRED(0) > BEST(1) > KOMM(5) | Seg C, Q 0.36, Hist mittel, Ziel 14, Lief +0, Warte 1 | - | A4 / A2 / A4+A2 |
| C0198 | ERF > KRED(0) > BEST(3) | Seg B, Q 0.57, Hist schlecht, Ziel 30, Lief +0, Warte 0 | - | A4 / A2 / A4+A2 |
| C0449 | ERF > KRED(0) > BEST(1) | Seg C, Q 0.20, Hist gut, Ziel 30, Lief +1, Warte 2 | - | A4 / A2 / A4+A2 |
| C0455 | ERF > KRED(0) > BEST(1) | Seg C, Q 0.35, Hist mittel, Ziel 30, Lief +1, Warte 3 | - | A4 / A2 / A4+A2 |
| C0488 | ERF > KRED(0) | Seg A, Q 0.53, Hist mittel, Ziel 30, Lief +0, Warte 3 | - | A4 / A2 / A4+A2 |
| C0548 | ERF > KRED(0) > BEST(0) > KOMM(6) | Seg B, Q 0.48, Hist gut, Ziel 30, Lief +1, Warte 0 | - | A4 / A2 / A4+A2 |
| C0642 | ERF > KRED(0) > BEST(0) > AEND(1) > AEND(0) | Seg C, Q 0.45, Hist schlecht, Ziel 45, Lief -1, Warte 3 | - | A4 / A2 / A4+A2 |
| C0645 | ERF > KRED(1) > BEST(0) | Seg B, Q 0.66, Hist gut, Ziel 45, Lief -4, Warte 7 | - | A4 / A2 / A4+A2 |
| C0725 | ERF > KRED(0) > BEST(0) > KOMM(2) | Seg A, Q 0.77, Hist gut, Ziel 30, Lief -1, Warte 2 | - | A4 / A2 / A4+A2 |
| C0967 | ERF > KRED(0) > BEST(0) > KOMM(2) | Seg C, Q 0.76, Hist gut, Ziel 30, Lief +1, Warte 3 | - | A4 / A2 / A4+A2 |

## E5

| Fall | Verlauf | Kennwerte | Freitext | Soll |
|---|---|---|---|---|
| C0053 | ERF > KRED(0) > BEST(0) > KOMM(4) > RECH(0) > VERS(1) | Seg B, Q 0.59, Hist mittel, Ziel 30, Verzug -25, Warte 4 | - | A6+A7 |
| C0137 | ERF > KRED(1) > BEST(0) > KOMM(2) > RECH(0) > VERS(4) > ZAHL(22) > ABS(1) | Seg B, Q 0.32, Hist mittel, Ziel 30, Warte 0 | - | A6+A7 |
| C0181 | ERF > KRED(0) > BEST(0) > KOMM(1) > RECH(4) > VERS(0) | Seg B, Q 0.64, Hist gut, Ziel 60, Verzug -56, Warte 4 | - | A6+A7 |
| C0320 | ERF > KRED(0) > BEST(0) > KOMM(2) > RECH(0) > VERS(1) | Seg B, Q 0.41, Hist gut, Ziel 14, Verzug -13, Warte 0 | - | A6+A7 |
| C0326 | ERF > KRED(0) > BEST(1) > KOMM(12) > RECH(1) > VERS(1) | Seg A, Q 0.51, Hist mittel, Ziel 30, Verzug -27, Warte 2 | - | A6+A7 |
| C0494 | ERF > KRED(0) > BEST(0) > KOMM(2) > RECH(1) > VERS(0) | Seg B, Q 0.36, Hist mittel, Ziel 30, Verzug -25, Warte 5 | Die letzte Lieferung war wie immer tadellos, Kompliment an Ihr Lager-Team! | A6+A7 (irrelevant) |
| C0609 | ERF > KRED(0) > BEST(0) > KOMM(7) > RECH(0) > VERS(0) > ZAHL(58) > ABS(4) | Seg B, Q 0.70, Hist gut, Ziel 60, Warte 3 | - | A6+A7 |
| C0768 | ERF > KRED(0) > BEST(0) > KOMM(2) > RECH(0) > VERS(1) | Seg B, Q 0.52, Hist gut, Ziel 45, Verzug -42, Warte 2 | Wir ziehen per 11.02.2026 um. Neue Postadresse: Industriestrasse 14, 8400 Winterthur. | A6+A7 (irrelevant) |
| C0805 | ERF > KRED(0) > BEST(1) > KOMM(5) > RECH(1) > VERS(0) | Seg B, Q 0.33, Hist gut, Ziel 60, Verzug -56, Warte 4 | - | A6+A7 |
| C0992 | ERF > KRED(1) > BEST(1) > KOMM(5) > RECH(1) > VERS(0) | Seg B, Q 0.90, Hist mittel, Ziel 30, Verzug -26, Warte 4 | - | A6+A7 |

## E6

| Fall | Verlauf | Kennwerte | Freitext | Soll |
|---|---|---|---|---|
| C0042 | ERF > KRED(0) > BEST(3) > KOMM(1) > VERS(1) > RECH(0) > ERIN(69) | Seg A, Q 0.41, Hist schlecht, Ziel 60, Verzug 40, Warte 31 | Bitte nehmen Sie zur Kenntnis, dass Herr Kaufmann per 23.05.2026 pensioniert wird. Seine Aufgaben uebernimmt Frau Lutz. | A3 (irrelevant) |
| C0120 | ERF > KRED(0) > BEST(3) > AEND(1) > AEND(0) > KOMM(1) > VERS(1) > RECH(1) > ERIN(40) | Seg A, Q 0.31, Hist mittel, Ziel 30, Verzug 23, Warte 13 | Wir befinden uns derzeit in einem finanziellen Engpass und koennen die Rechnung RE-26-18167 nicht fristgerecht begleichen. Waere eine Ratenzahlung moeglich? | A6 (payment_difficulty) |
| C0161 | ERF > KRED(3) > BEST(0) > AEND(1) > AEND(0) > KOMM(9) > VERS(0) > RECH(4) | Seg C, Q 0.74, Hist gut, Ziel 30, Verzug 19, Warte 49 | Leider ist ein grosser Kunde von uns in Konkurs gegangen. Wir brauchen mehr Zeit, um die offene Rechnung zu bezahlen. | A6 (payment_difficulty) |
| C0253 | ERF > KRED(1) > BEST(0) > KOMM(4) > VERS(1) > RECH(0) | Seg B, Q 0.53, Hist mittel, Ziel 14, Verzug 11, Warte 25 | Wir hatten eine Systemumstellung im Kreditorenwesen. Der offene Betrag ist im naechsten Lauf am 23.06.2026 enthalten und wird Ihnen dann gutgeschrieben. | A0 (payment_announced) |
| C0496 | ERF > KRED(0) > BEST(1) > KOMM(6) > VERS(0) > RECH(0) | Seg C, Q 0.25, Hist gut, Ziel 45, Verzug 18, Warte 63 | Unser Konto ist im Moment leider ausgereizt. Sobald die Gelder aus dem laufenden Projekt eingehen, melden wir uns wieder. | A6 (payment_difficulty) |
| C0515 | ERF > KRED(1) > BEST(0) > KOMM(7) > TEIL(0) > VERS(4) > RECH(1) | Seg B, Q 0.62, Hist mittel, Ziel 60, Verzug 36, Warte 96 | Haben Sie die Sicherheitsdatenblaetter zu Ihrem Reinigungsmittel auch auf Franzoesisch? | A3 (irrelevant) |
| C0590 | ERF > KRED(0) > BEST(1) > KOMM(0) > VERS(1) > RECH(0) > ERIN(34) | Seg C, Q 0.52, Hist gut, Ziel 30, Verzug 14, Warte 10 | Koennen Sie die Faelligkeit der Rechnung RE-26-13217 um zwei Monate verschieben? Wir haben momentan Zahlungsschwierigkeiten. | A6 (payment_difficulty) |
| C0610 | ERF > KRED(0) > BEST(1) > KOMM(4) > VERS(0) > RECH(0) | Seg B, Q 0.66, Hist mittel, Ziel 45, Verzug 34, Warte 79 | Hallo zusammen, die Kabelrollen vom 04.06.2026 sind 50 statt 100 Meter lang. Koennen Sie das bitte anschauen? | A5 (complaint) |
| C0794 | ERF > KRED(0) > BEST(0) > KOMM(2) > VERS(0) > RECH(3) > ERIN(21) | Seg B, Q 0.42, Hist gut, Ziel 14, Verzug 40, Warte 33 | Mangelruege: Bei 6 von 20 Ventilen tritt nach kurzer Zeit Fluessigkeit aus. Wir erwarten Ihre Stellungnahme. | A5 (complaint) |
| C0880 | ERF > KRED(0) > BEST(3) > KOMM(2) > VERS(0) > RECH(1) | Seg B, Q 0.41, Hist gut, Ziel 30, Verzug 25, Warte 55 | Nach zwei Tagen im Einsatz ist bei beiden Steuergeraeten das Display ausgefallen. | A5 (complaint) |

## E7

| Fall | Verlauf | Kennwerte | Freitext | Soll |
|---|---|---|---|---|
| C0163 | ERF > KRED(0) | Seg C, Q 1.01, Hist gut, Ziel 30, Lief +1, Warte 2 | - | (Labeling) |
| C0250 | ERF | Seg C, Q 1.15, Hist mittel, Ziel 14, Lief +0, Warte 3 | Die letzte Lieferung war wie immer tadellos, Kompliment an Ihr Lager-Team! | (Labeling) |
| C0268 | ERF > KRED(1) | Seg B, Q 1.00, Hist mittel, Ziel 30, Lief +1, Warte 1 | - | (Labeling) |
| C0380 | ERF | Seg B, Q 1.28, Hist mittel, Ziel 30, Lief +1, Warte 2 | - | (Labeling) |
| C0565 | ERF > KRED(0) | Seg B, Q 1.00, Hist mittel, Ziel 60, Lief -2, Warte 6 | - | (Labeling) |
| C0663 | ERF > KRED(0) | Seg C, Q 1.00, Hist mittel, Ziel 60, Lief +1, Warte 2 | Unser Betrieb bleibt vom 22. Dezember bis 5. Januar geschlossen. | (Labeling) |
| C0667 | ERF | Seg A, Q 1.54, Hist mittel, Ziel 14, Lief -2, Warte 7 | - | (Labeling) |
| C0739 | ERF | Seg B, Q 1.11, Hist gut, Ziel 60, Lief -5, Warte 10 | - | (Labeling) |
| C0964 | ERF | Seg A, Q 1.01, Hist gut, Ziel 14, Lief +0, Warte 3 | - | (Labeling) |
| C0993 | ERF > AEND(3) > AEND(0) > KRED(0) | Seg A, Q 1.15, Hist gut, Ziel 45, Lief -2, Warte 3 | - | (Labeling) |
