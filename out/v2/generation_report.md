# Generation Report v2 (erweiterter Prozess, Entwurf)

Spec: `spec_v2.yaml` v2.1.0, Seed 42. Faelle: 2000, Events: 16110, Aktivitaeten: 21.

**Ergebnis: 32 von 32 Pruefungen bestanden.**

Triggerlogik aus `src/detect_v2.py` (unabhaengig vom Generator).

## Pruefungen

| # | Pruefung | Ergebnis | Detail |
|---|---|---|---|
| 1 | event_log.csv Spalten | OK | case_id, activity, timestamp, resource, role |
| 2 | cases.csv Spalten = case_id + spec.case_attributes | OK | case_id, order_value, customer_segment, credit_limit, open_items, payment_history, payment_terms_days, promised_delivery_date, restock_date, invoice_amount, credit_note_amount, paid_amount, free_text, snapshot_time |
| 3 | ground_truth.csv Spalten | OK | case_id, exception_type, free_text_category, allowed_action_sets, expected_target_role, generator_tag |
| 4 | case_id eindeutig und identisch in allen Dateien | OK |  |
| 5 | Timestamp-Format YYYY-MM-DD HH:MM:SS | OK |  |
| 6 | event_log ohne leere Felder | OK |  |
| 7 | Daten rein ASCII | OK | alle ASCII |
| 8 | Anzahl pro Typ exakt | OK | none: 1630/1630; E2: 40/40; E3: 40/40; E5: 20/20; E6: 80/80; E7: 30/30; E8: 20/20; E9: 40/40; E10: 40/40; E11: 30/30; E12: 30/30 |
| 9 | Timestamps pro Fall streng monoton | OK | 0 Verstoesse |
| 10 | Keine Events nach dem Stichtag | OK | 0 Verstoesse |
| 11 | Events nur Mo bis Fr, 08:00 bis 17:00 | OK | 0 Faelle betroffen |
| 12 | Erstes Event = Auftrag erfassen | OK | 0 Verstoesse |
| 13 | Fallstart zwischen 2026-01-05 und 2026-06-30 | OK | 2026-01-05 bis 2026-06-30 |
| 14 | Kein Stichtag nach dem Datenabzug 2026-10-31 | OK | spaetester Stichtag 2026-10-11 |
| 15 | Rolle je Aktivitaet = spec.process.role_by_activity | OK | 0 Verstoesse |
| 16 | 3 bis 4 Ressourcen pro Rolle | OK | Buchhaltung: 3; Credit Management: 3; Kundendienst: 3; Lager/Logistik: 4; Vertrieb: 4 |
| 17 | Nur Aktivitaeten aus spec.process | OK | ok |
| 18 | Alle neuen Aktivitaeten kommen im Log vor | OK | alle 10 |
| 19 | Betraege > 0 genau dann, wenn das zugehoerige Event im Log steht | OK | 0 Verstoesse |
| 20 | restock_date gesetzt genau dann, wenn 'Ware nachbestellen' im Log steht | OK | 0 Verstoesse |
| 21 | Nach 'Auftrag stornieren' hoechstens 'Fall abschliessen' | OK | 0 Verstoesse |
| 22 | Trigger je Fall = Ground Truth (inkl. Ketten mit E6) | OK | 0 Abweichungen |
| 23 | Erkannter Typ nach Prioritaet = exception_type | OK | 0 Abweichungen |
| 24 | Kausale Ketten vorhanden (E8, E9, E11 jeweils mit E6) | OK | E11+E6: 12; E8+E6: 3; E9+E6: 7 |
| 25 | allowed_action_sets entsprechen spec_v2 | OK | 0 Abweichungen |
| 26 | expected_target_role entspricht spec_v2 | OK | 0 Abweichungen; (leer): 1840; Buchhaltung: 60; Credit Management: 60; Kundendienst: 20; Vertrieb: 20 |
| 27 | Freitext-Kategorie = Vorlagen-Kategorie (Regex-Abgleich) | OK | 0 Abweichungen |
| 28 | E6: 20 Faelle je Kategorie | OK | complaint: 20; irrelevant: 20; payment_announced: 20; payment_difficulty: 20 |
| 29 | Happy Path: alle 8 Varianten vorhanden | OK | aendern: 175; storno: 69; nachbestellung: 63; teillieferung: 48; erinnerung: 46; reklamation: 34; mahnung2: 29; rechnungskorrektur: 25 |
| 30 | Happy Path: Grenzfaelle fuer E2, E3, E6, E9, E10, E11, E12 | OK | e10: 12; e11: 11; e12: 11; e2: 12; e3: 12; e6: 12; e9: 12 |
| 31 | Info: Happy Path abgeschlossen | OK | 984 von 1630 (60.4%) |
| 32 | Wiederholbarkeit: weiterer Lauf byte-identisch (SHA-256) | OK | event_log.csv: fca0310ada44; cases.csv: f96bf87778e8; ground_truth.csv: 1a779dd573e7 |

## Typen

| Typ | n | Events Mittel | Freitext |
|---|---|---|---|
| none | 1630 | 8.4 | 10% |
| E2 | 40 | 1.8 | 12% |
| E3 | 40 | 4.3 | 20% |
| E5 | 20 | 8.5 | 10% |
| E6 | 80 | 7.7 | 100% |
| E7 | 30 | 1.8 | 10% |
| E8 | 20 | 7.5 | 10% |
| E9 | 40 | 8.1 | 5% |
| E10 | 40 | 9.8 | 18% |
| E11 | 30 | 9.0 | 10% |
| E12 | 30 | 5.3 | 10% |

## Letzte Aktivitaet zum Stichtag je Typ

| Letzte Aktivitaet | none | E2 | E3 | E5 | E6 | E7 | E8 | E9 | E10 | E11 | E12 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Auftrag aendern | 22 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| Auftrag bestaetigen | 61 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 30 |
| Auftrag erfassen | 38 | 13 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 |
| Auftrag stornieren | 33 | 0 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 |
| Fall abschliessen | 984 | 0 | 0 | 10 | 0 | 0 | 0 | 12 | 0 | 0 | 0 |
| Kommissionieren | 67 | 0 | 21 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Kreditpruefung | 61 | 27 | 6 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 |
| Mahnung Stufe 2 | 0 | 0 | 0 | 0 | 15 | 0 | 0 | 0 | 0 | 0 | 0 |
| Rechnung korrigieren | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Rechnung stellen | 74 | 0 | 0 | 0 | 49 | 0 | 0 | 28 | 0 | 0 | 0 |
| Retoure erfassen | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 30 | 0 |
| Verfuegbarkeitspruefung | 69 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Versenden | 61 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Ware nachbestellen | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Wareneingang Lager | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Zahlung zuordnen | 67 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 40 | 0 | 0 |
| Zahlungseingang | 71 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Zahlungserinnerung | 0 | 0 | 0 | 0 | 16 | 0 | 0 | 0 | 0 | 0 | 0 |
