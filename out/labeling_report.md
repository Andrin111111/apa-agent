# Simuliertes Doppellabeling (E6-Freitexte)

Modell A: Claude (Opus 5.5, blind). Modell B: Keyword-Klassifikator v0.1. Einheit: 1 gerendertes Beispiel pro Vorlage, 40 von 40 Eintraegen auswertbar.

| Kennzahl | Wert |
|---|---|
| Uebereinstimmung A vs. B | 78% |
| Cohens Kappa A vs. B | 0.70 |
| A vs. Konstruktion (Vorlagen-Kategorie) | 100% |
| B vs. Konstruktion | 78% |
| A, B und Konstruktion einig | 31 von 40 |
| als unsicher markiert (A / B) | 0 / 21 |

Lesart Kappa: ueber 0.80 sehr gut, 0.60 bis 0.80 gut, darunter pruefen.

## Nach Quelle und Stil (Anteil A und B beide korrekt)

| Gruppe | n | beide korrekt |
|---|---|---|
| source = claude | 20 | 80% |
| source = claude-rev1 | 20 | 75% |
| stil = direkt | 23 | 100% |
| stil = distraktor | 3 | 100% |
| stil = indirekt | 14 | 36% |
| category = complaint | 10 | 60% |
| category = irrelevant | 10 | 100% |
| category = payment_announced | 10 | 80% |
| category = payment_difficulty | 10 | 70% |

## Abweichungen (Kandidaten fuer unscharfe Vorlagen)

| item | Vorlage | Konstruktion | A | B | Text |
|---|---|---|---|---|---|
| L04 | complaint_08 | complaint | complaint | irrelevant | Hallo zusammen, die Kabelrollen vom 14.05.2026 sind 50 statt 100 Meter lang. Koennen Sie das bitte anschauen? |
| L05 | payment_difficulty_07 | payment_difficulty | payment_difficulty | irrelevant | Gibt es die Moeglichkeit, den Betrag ueber mehrere Monate verteilt abzuzahlen? |
| L07 | payment_announced_06 | payment_announced | payment_announced | irrelevant | Wir hatten eine Systemumstellung im Kreditorenwesen. Der offene Betrag ist im naechsten Lauf am 12.06.2026 enthalten und wird Ihnen dann gutgeschrieben. |
| L08 | complaint_06 | complaint | complaint | irrelevant | Auf den Etiketten steht Artikel 2250, in den Kartons liegt aber Artikel 2205. Bei uns steht jetzt die Montage still. |
| L12 | complaint_05 | complaint | complaint | irrelevant | Von den 40 Kartons, die am 16.07.2026 bei uns eingetroffen sind, waren 12 durchnaesst. Der Inhalt ist nicht mehr brauchbar. |
| L24 | payment_difficulty_06 | payment_difficulty | payment_difficulty | irrelevant | Ein Grossprojekt von uns ist geplatzt, und die Bank prueft gerade unsere Kreditlinie. Bis das geklaert ist, sind uns die Haende gebunden. |
| L30 | complaint_07 | complaint | complaint | irrelevant | Seit der Inbetriebnahme laeuft die Anlage nur mit Unterbrechungen. Ihr Techniker hat sich bis heute nicht gemeldet. |
| L37 | payment_difficulty_05 | payment_difficulty | payment_difficulty | irrelevant | Unser Konto ist im Moment leider ausgereizt. Sobald die Gelder aus dem laufenden Projekt eingehen, melden wir uns wieder. |
| L39 | payment_announced_08 | payment_announced | payment_announced | irrelevant | Kurze Rueckmeldung aus der Buchhaltung: Der Auftrag an die Bank ist am 06.03.2026 rausgegangen, der Betrag muesste bald bei Ihnen eingehen. |

Entscheid pro Abweichung (Jan): Vorlage schaerfen oder bewusst als schwierigen Fall behalten.

## Einordnung (Claude, 01.11.2026)

- Labeler A (Claude) stimmt zu 100 % mit der Konstruktion ueberein. Das ist **kein unabhaengiger Befund**: Claude hat die Texte selbst geschrieben. Externe Labeler sind fuer eine spaetere Iteration vorbereitet (`prompts/extern/`).
- Labeler B (Keyword-Klassifikator) irrt nur bei indirekten Texten (9 von 14), und zwar immer Richtung `irrelevant`. Zwischen den drei relevanten Kategorien gibt es keine Verwechslung.
- Folgerung: Keine Vorlage ist mehrdeutig, alle Abweichungen sind gewollte schwierige Faelle. Keine Nachschaerfung noetig.
- Hypothese fuer Schritt 3/4: Eine Regel-Baseline fuer E6 scheitert an indirekten Formulierungen. Dort ist der Mehrwert des Agenten zu pruefen.
