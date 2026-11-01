# Apromore-Export (AP7)

Erzeugt mit `python src/export_apromore.py`.
Zahlen dienen dem Abgleich: Apromore sollte nach dem Import dieselben Werte zeigen.

| Datei | Faelle | Events | Varianten |
|---|---|---|---|
| `apromore_events.csv` | 1000 | 5905 | 35 |
| `apromore_events_closed.csv` | 442 | 3674 | 7 |

Zeitraum: 2026-01-05 08:25:00 bis 2026-09-15 12:14:00.
Faelle mit gleichem Zeitstempel bei zwei Events: 0.

Aktivitaeten:

| Aktivitaet | Events |
|---|---|
| Auftrag erfassen | 1000 |
| Kreditpruefung | 912 |
| Auftrag bestaetigen | 781 |
| Kommissionieren | 706 |
| Versenden | 644 |
| Rechnung stellen | 612 |
| Zahlungseingang | 476 |
| Fall abschliessen | 442 |
| Auftrag aendern | 232 |
| Zahlungserinnerung | 68 |
| Teillieferung | 32 |

Top 10 Varianten, alle Faelle:

| # | Faelle | Anteil | Abfolge |
|---|---|---|---|
| 1 | 314 | 31.4% | Auftrag erfassen > Kreditpruefung > Auftrag bestaetigen > Kommissionieren > Versenden > Rechnung stellen > Zahlungseingang > Fall abschliessen |
| 2 | 100 | 10.0% | Auftrag erfassen > Kreditpruefung |
| 3 | 74 | 7.4% | Auftrag erfassen |
| 4 | 67 | 6.7% | Auftrag erfassen > Kreditpruefung > Auftrag bestaetigen > Kommissionieren > Versenden > Rechnung stellen |
| 5 | 60 | 6.0% | Auftrag erfassen > Kreditpruefung > Auftrag bestaetigen |
| 6 | 51 | 5.1% | Auftrag erfassen > Kreditpruefung > Auftrag bestaetigen > Kommissionieren |
| 7 | 31 | 3.1% | Auftrag erfassen > Kreditpruefung > Auftrag bestaetigen > Kommissionieren > Versenden > Rechnung stellen > Zahlungserinnerung |
| 8 | 30 | 3.0% | Auftrag erfassen > Kreditpruefung > Auftrag bestaetigen > Auftrag aendern > Auftrag aendern > Kommissionieren > Versenden > Rechnung stellen > Zahlungseingang > Fall abschliessen |
| 9 | 28 | 2.8% | Auftrag erfassen > Kreditpruefung > Auftrag bestaetigen > Kommissionieren > Versenden > Rechnung stellen > Zahlungserinnerung > Zahlungseingang > Fall abschliessen |
| 10 | 24 | 2.4% | Auftrag erfassen > Kreditpruefung > Auftrag bestaetigen > Kommissionieren > Teillieferung > Versenden > Rechnung stellen > Zahlungseingang > Fall abschliessen |

Top 10 Varianten, abgeschlossene Faelle:

| # | Faelle | Anteil | Abfolge |
|---|---|---|---|
| 1 | 314 | 71.0% | Auftrag erfassen > Kreditpruefung > Auftrag bestaetigen > Kommissionieren > Versenden > Rechnung stellen > Zahlungseingang > Fall abschliessen |
| 2 | 30 | 6.8% | Auftrag erfassen > Kreditpruefung > Auftrag bestaetigen > Auftrag aendern > Auftrag aendern > Kommissionieren > Versenden > Rechnung stellen > Zahlungseingang > Fall abschliessen |
| 3 | 28 | 6.3% | Auftrag erfassen > Kreditpruefung > Auftrag bestaetigen > Kommissionieren > Versenden > Rechnung stellen > Zahlungserinnerung > Zahlungseingang > Fall abschliessen |
| 4 | 24 | 5.4% | Auftrag erfassen > Kreditpruefung > Auftrag bestaetigen > Kommissionieren > Teillieferung > Versenden > Rechnung stellen > Zahlungseingang > Fall abschliessen |
| 5 | 24 | 5.4% | Auftrag erfassen > Kreditpruefung > Auftrag bestaetigen > Auftrag aendern > Kommissionieren > Versenden > Rechnung stellen > Zahlungseingang > Fall abschliessen |
| 6 | 21 | 4.8% | Auftrag erfassen > Kreditpruefung > Auftrag bestaetigen > Kommissionieren > Rechnung stellen > Versenden > Zahlungseingang > Fall abschliessen |
| 7 | 1 | 0.2% | Auftrag erfassen > Kreditpruefung > Auftrag bestaetigen > Auftrag aendern > Auftrag aendern > Kommissionieren > Rechnung stellen > Versenden > Zahlungseingang > Fall abschliessen |

Faelle pro Ausnahmetyp (alle / abgeschlossen):

| Typ | alle | abgeschlossen |
|---|---|---|
| E2 | 60 | 0 |
| E3 | 60 | 0 |
| E5 | 40 | 22 |
| E6 | 80 | 0 |
| E7 | 60 | 0 |
| none | 700 | 420 |
