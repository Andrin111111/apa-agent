# Generation Report (Schritt 2, Log-Generator)

Spec: `spec.yaml` v0.4.0, Seed 42. Faelle: 1000, Events: 5905.

**Ergebnis: 43 von 43 Pruefungen bestanden.**

Triggerlogik in `src/validate_log.py` unabhaengig vom Generator, Auswertung auf Tagesbasis.

## Pruefungen

| # | Pruefung | Ergebnis | Detail |
|---|---|---|---|
| 1 | event_log.csv Spalten | OK | case_id, activity, timestamp, resource, role |
| 2 | cases.csv Spalten = case_id + spec.case_attributes | OK | case_id, order_value, customer_segment, credit_limit, open_items, payment_history, payment_terms_days, promised_delivery_date, free_text, snapshot_time |
| 3 | cases.csv ohne typverratende Spalte | OK | keine |
| 4 | ground_truth.csv Spalten | OK | case_id, exception_type, free_text_category, allowed_action_sets, expected_target_role, generator_tag |
| 5 | case_id eindeutig (cases, ground_truth) | OK |  |
| 6 | case_id-Mengen identisch (cases, ground_truth, event_log) | OK |  |
| 7 | Timestamp-Format YYYY-MM-DD HH:MM:SS (event_log, snapshot_time) | OK |  |
| 8 | event_log ohne leere Felder | OK |  |
| 9 | Daten rein ASCII | OK | alle ASCII |
| 10 | Anzahl pro Typ exakt | OK | none: 700/700; E2: 60/60; E3: 60/60; E5: 40/40; E6: 80/80; E7: 60/60 |
| 11 | Timestamps pro Fall streng monoton | OK | 0 Verstoesse |
| 12 | Keine Events nach dem Stichtag | OK | 0 Verstoesse |
| 13 | Events nur Mo bis Fr, 08:00 bis 17:00 | OK | 0 Faelle betroffen |
| 14 | Erstes Event = Auftrag erfassen | OK | 0 Verstoesse |
| 15 | Fallstart zwischen 2026-01-05 und 2026-06-30 | OK | 2026-01-05 bis 2026-06-30 |
| 16 | Kein Stichtag nach dem Datenabzug 2026-10-31 | OK | spaetester Stichtag 2026-09-21 |
| 17 | Genau eine Rolle pro Aktivitaet | OK | Auftrag aendern: Vertrieb; Auftrag bestaetigen: Vertrieb; Auftrag erfassen: Vertrieb; Fall abschliessen: Buchhaltung; Kommissionieren: Lager/Logistik; Kreditpruefung: Credit Management; Rechnung stellen: Buchhaltung; Teillieferung: Lager/Logistik; Versenden: Lager/Logistik; Zahlungseingang: Buchhaltung; Zahlungserinnerung: Buchhaltung |
| 18 | 3 bis 4 Ressourcen pro Rolle | OK | Buchhaltung: 3; Credit Management: 3; Lager/Logistik: 4; Vertrieb: 4 |
| 19 | Nur Aktivitaeten aus spec.process | OK |  |
| 20 | Trigger je Fall entsprechen Ground Truth (unabhaengige Logik) | OK | 0 Abweichungen |
| 21 | expected_target_role korrekt (E2, E5, E6 complaint/difficulty, sonst leer) | OK | 0 Abweichungen; (leer): 860; Credit Management: 80; Buchhaltung: 40; Kundendienst: 20 |
| 22 | allowed_action_sets entsprechen spec (none = [[A0]], E7 leer) | OK | 0 Abweichungen |
| 23 | Freitext-Kategorie = Vorlagen-Kategorie (Regex-Abgleich) | OK | 0 falsch, 0 nicht eindeutig |
| 24 | E6: 20 Faelle je Kategorie | OK | complaint: 20; irrelevant: 20; payment_announced: 20; payment_difficulty: 20 |
| 25 | E6: jeder Fall hat Freitext | OK |  |
| 26 | Happy Path: Rauschen 10 % mit irrelevantem Freitext | OK | 70 von 700 |
| 27 | Info: irrelevanter Freitext in E2/E3/E5/E7 (Abweichung) | OK | 20 Faelle: E2: 5; E3: 6; E5: 2; E7: 7 |
| 28 | Vorlagen: ca. 10 je Kategorie, mind. 3 indirekt/Distraktor, Metadaten, ASCII | OK | complaint: 10 Vorlagen, 5 indirekt/Distraktor; payment_announced: 10 Vorlagen, 4 indirekt/Distraktor; payment_difficulty: 10 Vorlagen, 5 indirekt/Distraktor; irrelevant: 10 Vorlagen, 3 indirekt/Distraktor |
| 29 | Happy Path: ca. 60 % abgeschlossen | OK | 420 von 700 (60.0%) |
| 30 | Happy Path: ca. 25 % mit Variante | OK | 175 von 700 (25.0%) |
| 31 | Zahlungserinnerung nur mit Zahlungseingang vor Stichtag | OK | 0 Verstoesse |
| 32 | Info: E6 mit Zahlungserinnerung (ab 11 Tagen Verzug) | OK | 34 von 80 |
| 33 | Teillieferung nur zusammen mit Versenden (keine E3-Mehrdeutigkeit) | OK | 0 Verstoesse |
| 34 | Auftrag aendern hoechstens 2 mal (E4 nicht erzeugt) | OK | Maximum 2 |
| 35 | Happy Path: ca. 5 % Grenzfaelle knapp unter der Schwelle | OK | Summe = Limit: 13; Liefertermin = Stichtag + 2 Tage: 11; Stichtag = Faelligkeit: 11 |
| 36 | E3: negative Differenzen (Termin ueberschritten) vorhanden | OK | Delta min -5, max 1, negativ: 26 von 60 |
| 37 | E3: Fall steht in Kommissionieren oder davor | OK | Auftrag bestaetigen: 23; Kommissionieren: 23; Auftrag aendern: 7; Kreditpruefung: 7 |
| 38 | E6: ueberfaellig 1 bis 45 Tage | OK | min 1, max 45, Median 25 |
| 39 | E2: Ueberschreitung von knapp bis stark | OK | Quote min 1.0000, Median 1.108, max 1.779 |
| 40 | E7: Ueberschreitung von knapp bis stark | OK | Quote min 1.0000, Median 1.162, max 1.679 |
| 41 | pilot_sample.csv: 4 E2, 4 E3, 6 E6 (alle Kategorien), 6 HP (3 mit Freitext), kein E5/E7 | OK | {'E6': 6, 'none': 6, 'E3': 4, 'E2': 4}; E6: {'complaint': 2, 'irrelevant': 1, 'payment_announced': 1, 'payment_difficulty': 2}; HP mit Freitext: 3; E2/E3 mit Freitext: 0 |
| 42 | labeling_e6_blind.csv: 15 E6-Faelle, ohne Kategorie, Label leer | OK | Kategorien (nur im Bericht sichtbar): {'complaint': 3, 'irrelevant': 4, 'payment_announced': 4, 'payment_difficulty': 4} |
| 43 | Wiederholbarkeit: 2 weitere Laeufe byte-identisch (SHA-256) | OK | event_log.csv: 4555a8c191bd; cases.csv: 2dc11a7ec4e6; ground_truth.csv: 59e5eb237f59; pilot_sample.csv: 2ca8da9d2397; labeling_e6_blind.csv: a3bd3a179374 |

## Verteilungsvergleich der Kernattribute (Leakage-Pruefung)

Quote = (order_value + open_items) / credit_limit. Lieferfrist = promised_delivery_date minus Fallstart.

| Typ | n | Seg A | Seg B | Seg C | Hist gut | mittel | schlecht | Ziel (Tage) | Wert Median | Wert Mittel | Limit Median | Quote Median | Freitext | Events | Lieferfrist Median (Tage) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 700 | 20% | 47% | 33% | 48% | 35% | 17% | 35.7 | 7'098 | 12'001 | 80'000 | 0.59 | 10% | 6.6 | 8 |
| E2 | 60 | 22% | 48% | 30% | 42% | 37% | 22% | 33.5 | 5'904 | 11'764 | 80'000 | 1.11 | 8% | 2.0 | 12 |
| E3 | 60 | 17% | 47% | 37% | 42% | 45% | 13% | 35.3 | 7'118 | 12'437 | 80'000 | 0.57 | 10% | 3.5 | 4 |
| E5 | 40 | 12% | 62% | 25% | 52% | 40% | 8% | 37.4 | 6'343 | 10'627 | 80'000 | 0.55 | 5% | 7.2 | 10 |
| E6 | 80 | 24% | 59% | 18% | 55% | 28% | 18% | 37.1 | 9'078 | 14'178 | 80'000 | 0.54 | 100% | 6.7 | 8 |
| E7 | 60 | 20% | 48% | 32% | 50% | 37% | 13% | 36.1 | 8'070 | 12'760 | 100'000 | 1.16 | 12% | 1.7 | 3 |
| alle | 1000 | 20% | 49% | 31% | 48% | 35% | 17% | 35.7 | 7'203 | 12'178 | 80'000 | 0.62 | 17% | 5.9 | 8 |

Erwartete Unterschiede (durch Trigger bestimmt): Quote bei E2/E7 > 1; Freitext bei E6 100 %; Eventanzahl und Lieferfrist haengen vom Prozessstand zum Stichtag ab.

## Letzte Aktivitaet zum Stichtag je Typ

| Letzte Aktivitaet | E2 | E3 | E5 | E6 | E7 | none |
|---|---|---|---|---|---|---|
| Auftrag aendern | 2 | 7 | 0 | 0 | 2 | 18 |
| Auftrag bestaetigen | 0 | 23 | 0 | 0 | 0 | 37 |
| Auftrag erfassen | 17 | 0 | 0 | 0 | 23 | 34 |
| Fall abschliessen | 0 | 0 | 22 | 0 | 0 | 420 |
| Kommissionieren | 0 | 23 | 0 | 0 | 0 | 39 |
| Kreditpruefung | 41 | 7 | 0 | 0 | 35 | 48 |
| Rechnung stellen | 0 | 0 | 0 | 46 | 0 | 38 |
| Versenden | 0 | 0 | 18 | 0 | 0 | 32 |
| Zahlungseingang | 0 | 0 | 0 | 0 | 0 | 34 |
| Zahlungserinnerung | 0 | 0 | 0 | 34 | 0 | 0 |
