# K5: Stichprobe Begruendungen (Raster 0 bis 2)

Erzeugt von `src/step5_eval.py` (Seed 42). Bewertung durch Jan, blind: Ground Truth und Korrektheit stehen erst in `out/k5_key.csv`.
Bewertet wird die Begruendung (`rationale` und `key_evidence`), nicht die Aktion. Eintrag in `out/k5_stichprobe.csv`, Spalten `score_0_2` und `kommentar`.

## Raster (Entscheid Jan 01.11.2026: Option A, Anker mit Klarstellungen)

| Punkte | Anker |
|---|---|
| 2 | Nennt die ausschlaggebende Information korrekt und verbindet sie mit der gewaehlten Aktion ueber die richtige Regel (Zuordnung). Keine falschen oder erfundenen Fakten. |
| 1 | Ausschlaggebende Information korrekt, aber: nur teilweise oder generisch (z. B. nur "Typ laut Erkennung", Freitext nicht inhaltlich wiedergegeben), ODER falscher Regelbezug (z. B. Ermessensrichtlinie statt Zuordnung), ODER falsche Nebenaussage, die die Entscheidung nicht traegt. |
| 0 | Ausschlaggebende Information fehlt oder ist falsch (Freitext falsch gedeutet, falsche Zahlen, erfundene Fakten zum Kern), oder die Begruendung widerspricht der Aktion. |

Ausschlaggebend ist: E2 Kreditueberschreitung; E3 Liefertermin nah oder verpasst und nicht versendet; E6 Inhalt des Freitexts (Mangel, Zahlungsankuendigung, Zahlungsschwierigkeit, ohne Bezug); none: kein harter Trigger, Freitext ohne Ausnahme.

Zusammensetzung: 2 E2, 2 E3, 2 Happy Path mit Freitext (pilot_t0 Run 1), 12 E6 (e6_t0, je Kategorie 3, davon bis zu 2 indirekt, jede Vorlage hoechstens einmal). Auswahl unabhaengig vom Ergebnis.
Zusatzitems K5-Z*: 2 falsche Rohentscheidungen, bewusst gewaehlt (nicht blind, nicht im Mittelwert). Frage dort: Traegt die Begruendung die falsche Aktion, und ist sie dem Fall treu?

### K5-01 (C0537, pilot_t0, Run 1)

- Erkennung: E3 E3
- Freitext: -
- Fakten: Limit 25000, Exposure 8636, Headroom 16364; Liefertermin 2026-07-06 (in 1 T); Tage ueberfaellig None; Zahlungshistorie mittel; letzte Aktivitaet Kommissionieren
- Agent: Typ E3, Aktionen A2+A4
- Belege: derived.days_to_promised_delivery=1 | derived.shipped=false
- Begruendung: Der Fall ist als E3 (Lieferverzögerung) markiert, da der zugesagte Liefertermin in 1 Tag liegt und die Ware noch nicht versendet wurde. Gemäss den verbindlichen Zuordnungen für E3 sind nur A4 (Priorisieren), A2 (Kunde informieren) oder die Kombination davon zulässig. Da der Termin sehr knapp ist, wird der Kunde informiert und der Fall priorisiert.
- Punkte: __  Kommentar: 

### K5-02 (C0317, pilot_t0, Run 1)

- Erkennung: E2 E2
- Freitext: -
- Fakten: Limit 60000, Exposure 61788, Headroom -1788; Liefertermin 2026-02-02 (in 12 T); Tage ueberfaellig None; Zahlungshistorie gut; letzte Aktivitaet Kreditpruefung
- Agent: Typ E2, Aktionen A6/Credit Management
- Belege: derived.credit_exposure > derived.credit_limit | derived.credit_headroom: -1788 | detection.detected_type: E2
- Begruendung: Der Fall zeigt eine Überschreitung des Kreditlimits (Exposure 61.788 CHF vs. Limit 60.000 CHF), was den Ausnahmetyp E2 auslöst. Gemäß der verbindlichen Zuordnung für E2 ist die automatische Weiterleitung an das Credit Management erforderlich, um über die Freigabe oder Ablehnung des Auftrags zu entscheiden.
- Punkte: __  Kommentar: 

### K5-03 (C0028, e6_t0, Run 1)

- Erkennung: E6 E6
- Freitext: Kurze Rueckmeldung aus der Buchhaltung: Der Auftrag an die Bank ist am 08.05.2026 rausgegangen, der Betrag muesste bald bei Ihnen eingehen.
- Fakten: Limit 60000, Exposure 28969, Headroom 31031; Liefertermin 2026-02-19 (in None T); Tage ueberfaellig 24; Zahlungshistorie mittel; letzte Aktivitaet Zahlungserinnerung
- Agent: Typ E6, Aktionen A0
- Belege: derived.days_overdue=24 | free_text: "Der Auftrag an die Bank ist am 08.05.2026 rausgegangen, der Betrag muesste bald bei Ihnen eingehen."
- Begruendung: Der Fall ist als E6 (Zahlungsverzug) markiert, da die Rechnung überfällig ist und keine Zahlung eingegangen ist. Der Freitext des Kunden bestätigt jedoch ausdrücklich, dass die Zahlung veranlasst wurde und kurz vor dem Eingang steht. Gemäß der Zuordnung für E6 bei Meldung einer veranlassten Zahlung ist keine weitere Mahnung oder Eskalation nötig.
- Punkte: __  Kommentar: 

### K5-04 (C0327, e6_t0, Run 1)

- Erkennung: E6 E6
- Freitext: Unsere Buchhaltung hat den Betrag gestern an Ihre Bank angewiesen.
- Fakten: Limit 15000, Exposure 8050, Headroom 6950; Liefertermin 2026-04-17 (in None T); Tage ueberfaellig 20; Zahlungshistorie gut; letzte Aktivitaet Zahlungserinnerung
- Agent: Typ E6, Aktionen A0
- Belege: derived.days_overdue=20 | free_text='Unsere Buchhaltung hat den Betrag gestern an Ihre Bank angewiesen.'
- Begruendung: Der Fall ist als E6 (Zahlungsverzug) markiert, da die Rechnung überfällig ist. Der Freitext des Kunden bestätigt jedoch explizit, dass der Zahlungsbetrag bereits veranlasst wurde ('gestern an Ihre Bank angewiesen'). Gemäß den Zuordnungsregeln für E6 bei einer bestätigten Zahlung handelt es sich um einen abgeschlossenen Vorgang, der keine weitere Eskalation erfordert.
- Punkte: __  Kommentar: 

### K5-05 (C0945, e6_t0, Run 1)

- Erkennung: E6 E6
- Freitext: Die Zahlung fuer Rechnung RE-26-28840 ueber CHF 13'730.00 wurde am 06.08.2026 ausgeloest. Sie sollte in den naechsten Tagen bei Ihnen eingehen.
- Fakten: Limit 60000, Exposure 42438, Headroom 17562; Liefertermin 2026-06-01 (in None T); Tage ueberfaellig 14; Zahlungshistorie schlecht; letzte Aktivitaet Zahlungserinnerung
- Agent: Typ E6, Aktionen A0
- Belege: derived.days_overdue=14 | free_text: "Die Zahlung fuer Rechnung RE-26-28840 ueber CHF 13'730.00 wurde am 06.08.2026 ausgeloest. Sie sollte in den naechsten Tagen bei Ihnen eingehen."
- Begruendung: Der Fall ist als E6 (Zahlungsverzug) erkannt, da die Rechnung überfällig ist und keine Zahlung eingegangen ist. Der Freitext des Kunden bestätigt jedoch, dass die Zahlung bereits ausgelöst wurde. Gemäss der Zuordnung für E6 hat der Kunde die Zahlung als veranlasst gemeldet, was eine Wiedervorlage (A0) erfordert.
- Punkte: __  Kommentar: 

### K5-06 (C0179, e6_t0, Run 1)

- Erkennung: E6 E6
- Freitext: Ein Grossprojekt von uns ist geplatzt, und die Bank prueft gerade unsere Kreditlinie. Bis das geklaert ist, sind uns die Haende gebunden.
- Fakten: Limit 100000, Exposure 76214, Headroom 23786; Liefertermin 2026-06-30 (in None T); Tage ueberfaellig 35; Zahlungshistorie gut; letzte Aktivitaet Zahlungserinnerung
- Agent: Typ E6, Aktionen A6/Credit Management
- Belege: derived.days_overdue=35 | free_text: 'Ein Grossprojekt von uns ist geplatzt, und die Bank prueft gerade unsere Kreditlinie. Bis das geklaert ist, sind uns die Haende gebunden.'
- Begruendung: Der Fall zeigt einen Zahlungsverzug (Rechnung überfällig seit 35 Tagen) kombiniert mit einem Freitext des Kunden, der explizit Zahlungsschwierigkeiten und eine vorübergehende Zahlungsunfähigkeit aufgrund einer Bankprüfung anzeigt. Gemäß den Zuordnungsregeln für E6 ist bei Hinweis auf Zahlungsschwierigkeiten oder Bitte um Stundung die Eskalation an das Credit Management (A6) erforderlich.
- Punkte: __  Kommentar: 

### K5-07 (C0797, e6_t0, Run 1)

- Erkennung: E6 E6
- Freitext: Reklamation: Die gelieferten Artikel entsprechen nicht der bestellten Ausfuehrung.
- Fakten: Limit 100000, Exposure 69294, Headroom 30706; Liefertermin 2026-04-06 (in None T); Tage ueberfaellig 29; Zahlungshistorie schlecht; letzte Aktivitaet Rechnung stellen
- Agent: Typ E6, Aktionen A5/Kundendienst
- Belege: derived.days_overdue=29 | free_text: Reklamation: Die gelieferten Artikel entsprechen nicht der bestellten Ausfuehrung.
- Begruendung: Der Fall ist als E6 (Zahlungsverzug) markiert, da die Rechnung überfällig ist. Der Freitext des Kunden enthält jedoch eine explizite Reklamation wegen falscher Ausführung. Gemäss Ermessensrichtlinie haben Hinweise auf Mängel Vorrang vor Mahnprozessen. Daher wird der Fall an den Kundendienst zur Bearbeitung der Reklamation neu zugewiesen.
- Punkte: __  Kommentar: 

### K5-08 (C0982, e6_t0, Run 1)

- Erkennung: E6 E6
- Freitext: Wegen Zahlungsausfaellen bei unseren eigenen Kunden koennen wir die Rechnung im Moment nicht bezahlen. Wir schlagen monatliche Teilzahlungen vor.
- Fakten: Limit 100000, Exposure 49059, Headroom 50941; Liefertermin 2026-04-23 (in None T); Tage ueberfaellig 1; Zahlungshistorie gut; letzte Aktivitaet Rechnung stellen
- Agent: Typ E6, Aktionen A6/Credit Management
- Belege: derived.days_overdue=1 | free_text: 'Wegen Zahlungsausfaellen bei unseren eigenen Kunden koennen wir die Rechnung im Moment nicht bezahlen. Wir schlagen monatliche Teilzahlungen vor.'
- Begruendung: Der Fall ist als E6 (Zahlungsverzug) klassifiziert, da die Rechnung überfällig ist und der Kunde Zahlungsprobleme meldet. Der Freitext des Kunden bezieht sich explizit auf Zahlungsschwierigkeiten und bittet um Teilzahlungen, was laut Zuordnungsvorschrift eine Eskalation an das Credit Management erfordert.
- Punkte: __  Kommentar: 

### K5-09 (C0493, e6_t0, Run 1)

- Erkennung: E6 E6
- Freitext: Unser Team freut sich auf den Besuch Ihres Aussendienstes am 13.05.2026 in Aarau.
- Fakten: Limit 100000, Exposure 28306, Headroom 71694; Liefertermin 2026-02-17 (in None T); Tage ueberfaellig 33; Zahlungshistorie schlecht; letzte Aktivitaet Rechnung stellen
- Agent: Typ E6, Aktionen A3
- Belege: derived.days_overdue=33 | detection.detected_type=E6 | free_text='Unser Team freut sich auf den Besuch Ihres Aussendienstes am 13.05.2026 in Aarau.'
- Begruendung: Der Fall ist als E6 (Zahlungsverzug) markiert, da die Rechnung seit 33 Tagen überfällig ist und kein Zahlungseingang vorliegt. Der eingegangene Freitext des Kunden bezieht sich jedoch auf einen bevorstehenden Besuch und hat keinen Bezug zu Zahlungsschwierigkeiten, Reklamationen oder einer Kündigung. Gemäss der Zuordnung für E6 bei neutralem Kontext (kein Bezug zu Zahlung/Mangel) ist die nächste logische Aktion eine Empfehlung für den nächsten Schritt (Mahnung).
- Punkte: __  Kommentar: 

### K5-10 (C0955, pilot_t0, Run 1)

- Erkennung: none 
- Freitext: Bitte nehmen Sie zur Kenntnis, dass Herr Kaufmann per 14.07.2026 pensioniert wird. Seine Aufgaben uebernimmt Frau Lutz.
- Fakten: Limit 100000, Exposure 55253, Headroom 44747; Liefertermin 2026-07-08 (in 5 T); Tage ueberfaellig None; Zahlungshistorie mittel; letzte Aktivitaet Auftrag aendern
- Agent: Typ none, Aktionen A0
- Belege: detection.detected_type=none | free_text='Bitte nehmen Sie zur Kenntnis, dass Herr Kaufmann per 14.07.2026 pensioniert wird. Seine Aufgaben uebernimmt Frau Lutz.' | derived.days_overdue=null | derived.credit_headroom=44747
- Begruendung: Der Fall enthält keinen harten Trigger (keine Kreditüberschreitung, keine Lieferverzögerung, keine offene Rechnung). Der eingegangene Freitext betrifft eine interne Personaländerung beim Kunden und hat keinen Bezug zu Zahlungsmängeln oder Warendefekten. Gemäß der Zuordnung für 'none' ist keine Ausnahmebehandlung nötig.
- Punkte: __  Kommentar: 

### K5-11 (C0042, e6_t0, Run 1)

- Erkennung: E6 E6
- Freitext: Bitte nehmen Sie zur Kenntnis, dass Herr Kaufmann per 23.05.2026 pensioniert wird. Seine Aufgaben uebernimmt Frau Lutz.
- Fakten: Limit 200000, Exposure 81215, Headroom 118785; Liefertermin 2026-02-02 (in None T); Tage ueberfaellig 40; Zahlungshistorie schlecht; letzte Aktivitaet Zahlungserinnerung
- Agent: Typ E6, Aktionen A3
- Belege: derived.days_overdue=40 | free_text: 'Bitte nehmen Sie zur Kenntnis, dass Herr Kaufmann per 23.05.2026 pensioniert wird. Seine Aufgaben uebernimmt Frau Lutz.'
- Begruendung: Der Fall ist als E6 (Zahlungsverzug) markiert, da die Rechnung überfällig ist (40 Tage). Der eingegangene Freitext enthält jedoch keine Hinweise auf Zahlungsschwierigkeiten, Mahnungen oder Mängel, sondern lediglich eine interne Personalie des Kunden. Gemäss der Zuordnung für E6 bei neutralem Kontext ohne Bezug zu Zahlung/Mangel ist die nächste logische Aktion eine Empfehlung (A3), um den Prozess fortzusetzen (z.B. Mahnung vorbereiten).
- Punkte: __  Kommentar: 

### K5-12 (C0067, pilot_t0, Run 1)

- Erkennung: E3 E3
- Freitext: -
- Fakten: Limit 100000, Exposure 40663, Headroom 59337; Liefertermin 2026-03-30 (in -4 T); Tage ueberfaellig None; Zahlungshistorie mittel; letzte Aktivitaet Auftrag bestaetigen
- Agent: Typ E3, Aktionen A2+A4
- Belege: derived.days_to_promised_delivery: -4 | derived.shipped: false
- Begruendung: Der Fall ist als E3 (Lieferverzögerung) klassifiziert, da der zugesagte Liefertermin um 4 Tage verpasst wurde und die Ware noch nicht versendet wurde. Gemäss den verbindlichen Zuordnungen für E3 sind Aktionen wie A6 oder A7 ausgeschlossen; stattdessen muss entweder priorisiert (A4), der Kunde informiert werden (A2) oder beides kombiniert werden. Da ein Terminverzug vorliegt, ist eine Information des Kunden (A2) und eine Priorisierung des Falls (A4) die angemessene Reaktion.
- Punkte: __  Kommentar: 

### K5-13 (C0853, e6_t0, Run 1)

- Erkennung: E6 E6
- Freitext: Unser Konto ist im Moment leider ausgereizt. Sobald die Gelder aus dem laufenden Projekt eingehen, melden wir uns wieder.
- Fakten: Limit 400000, Exposure 283803, Headroom 116197; Liefertermin 2026-01-19 (in None T); Tage ueberfaellig 11; Zahlungshistorie schlecht; letzte Aktivitaet Zahlungserinnerung
- Agent: Typ E6, Aktionen A6/Credit Management
- Belege: derived.days_overdue=11 | free_text: "Unser Konto ist im Moment leider ausgereizt..." | detection.detected_type="E6"
- Begruendung: Der Kunde meldet explizit Zahlungsschwierigkeiten und bittet um Aufschub, da das Konto ausgereizt sei. Gemäss der Zuordnung für Ausnahmetyp E6 bei Hinweis auf Zahlungsschwierigkeiten ist eine Eskalation an das Credit Management erforderlich.
- Punkte: __  Kommentar: 

### K5-14 (C0303, pilot_t0, Run 1)

- Erkennung: none 
- Freitext: Wir ziehen per 27.02.2026 um. Neue Postadresse: Industriestrasse 14, 8400 Winterthur.
- Fakten: Limit 15000, Exposure 6283, Headroom 8717; Liefertermin 2026-02-02 (in None T); Tage ueberfaellig None; Zahlungshistorie mittel; letzte Aktivitaet Fall abschliessen
- Agent: Typ none, Aktionen A0
- Belege: detection.detected_type = none | free_text = 'Wir ziehen per 27.02.2026 um. Neue Postadresse: Industriestrasse 14, 8400 Winterthur.' | derived.days_overdue = null | payment_received = true
- Begruendung: Der Fall hat keinen harten Trigger (keine Kreditüberschreitung, keine Lieferverzögerung, kein Zahlungsverzug). Der eingegangene Freitext enthält eine reine Adressänderung ohne Bezug zu Zahlungsmängeln oder Warendefekten. Da der Kunde bereits bezahlt hat und keine Ausnahmebedingungen vorliegen, ist keine aktive Intervention nötig; der Fall wird lediglich protokolliert.
- Punkte: __  Kommentar: 

### K5-15 (C0880, e6_t0, Run 1)

- Erkennung: E6 E6
- Freitext: Nach zwei Tagen im Einsatz ist bei beiden Steuergeraeten das Display ausgefallen.
- Fakten: Limit 80000, Exposure 32839, Headroom 47161; Liefertermin 2026-06-18 (in None T); Tage ueberfaellig 25; Zahlungshistorie gut; letzte Aktivitaet Rechnung stellen
- Agent: Typ E6, Aktionen A5/Kundendienst
- Belege: derived.days_overdue=25 | free_text="Nach zwei Tagen im Einsatz ist bei beiden Steuergeraeten das Display ausgefallen."
- Begruendung: Der Fall zeigt einen Zahlungsverzug (Rechnung überfällig seit 25 Tagen), doch der Freitext des Kunden meldet einen konkreten Mangel an Ware (ausgefallenes Display). Gemäß der Ermessensrichtlinie haben Hinweise auf Mängel oder Reklamationen Vorrang vor Mahnprozessen. Daher ist eine Überweisung an den Kundendienst zur Bearbeitung des Mangels die richtige Maßnahme.
- Punkte: __  Kommentar: 

### K5-16 (C0695, e6_t0, Run 1)

- Erkennung: E6 E6
- Freitext: Haben Sie die Sicherheitsdatenblaetter zu Ihrem Reinigungsmittel auch auf Franzoesisch?
- Fakten: Limit 200000, Exposure 114930, Headroom 85070; Liefertermin 2026-05-22 (in None T); Tage ueberfaellig 14; Zahlungshistorie schlecht; letzte Aktivitaet Rechnung stellen
- Agent: Typ E6, Aktionen A3
- Belege: derived.days_overdue=14 | detection.detected_type=E6 | free_text='Haben Sie die Sicherheitsdatenblaetter zu Ihrem Reinigungsmittel auch auf Franzoesisch?'
- Begruendung: Der Fall ist als E6 (Zahlungsverzug) markiert, da die Rechnung überfällig ist (14 Tage). Der eingegangene Freitext bezieht sich jedoch ausschließlich auf eine Anfrage bezüglich Sicherheitsdatenblätter und hat keinen Bezug zu Zahlungsschwierigkeiten, Reklamationen oder einer Kundigung. Gemäss der Zuordnung für E6 bei neutralem Kontext ohne Mangelmeldung ist die nächste logische Massnahme eine Mahnung (A3).
- Punkte: __  Kommentar: 

### K5-17 (C0902, pilot_t0, Run 1)

- Erkennung: E2 E2
- Freitext: -
- Fakten: Limit 100000, Exposure 132431, Headroom -32431; Liefertermin 2026-03-13 (in 11 T); Tage ueberfaellig None; Zahlungshistorie schlecht; letzte Aktivitaet Kreditpruefung
- Agent: Typ E2, Aktionen A6/Credit Management
- Belege: derived.credit_exposure > derived.credit_limit | derived.credit_headroom: -32431 | detection.detected_type: E2
- Begruendung: Der Fall zeigt eine klare Überschreitung des Kreditlimits (Exposure 132.431 CHF vs. Limit 100.000 CHF), was den Ausnahmetyp E2 auslöst. Gemäss der verbindlichen Zuordnung für E2 ist die automatische Weiterleitung an das Credit Management erforderlich, um über eine eventuelle Freigabe oder Sperrung zu entscheiden.
- Punkte: __  Kommentar: 

### K5-18 (C0298, e6_t0, Run 1)

- Erkennung: E6 E6
- Freitext: Auf den Etiketten steht Artikel 2250, in den Kartons liegt aber Artikel 2205. Bei uns steht jetzt die Montage still.
- Fakten: Limit 80000, Exposure 44927, Headroom 35073; Liefertermin 2026-07-01 (in None T); Tage ueberfaellig 19; Zahlungshistorie mittel; letzte Aktivitaet Rechnung stellen
- Agent: Typ E6, Aktionen A5/Kundendienst
- Belege: free_text: "Auf den Etiketten steht Artikel 2250, in den Kartons liegt aber Artikel 2205. Bei uns steht jetzt die Montage still."
- Begruendung: Der Kunde meldet einen offensichtlichen Mangel an Ware (falsche Artikel im Karton), was zu einem Lieferstopp führt. Gemäss der Zuordnung für Ausnahmetyp E6 hat eine Meldung von Mängeln oder Reklamationen Vorrang vor Mahnprozessen. Daher ist die Überweisung an den Kundendienst zur Bearbeitung des Mangels erforderlich.
- Punkte: __  Kommentar: 

## Zusatzitems (falsche Entscheidungen, nicht im Mittelwert)

### K5-Z1 (C0776, e6_t0, Run 1)

- Erkennung: E6 E6
- Freitext: Wir hatten eine Systemumstellung im Kreditorenwesen. Der offene Betrag ist im naechsten Lauf am 23.03.2026 enthalten und wird Ihnen dann gutgeschrieben.
- Fakten: Limit 300000, Exposure 148411, Headroom 151589; Liefertermin 2026-01-26 (in None T); Tage ueberfaellig 28; Zahlungshistorie mittel; letzte Aktivitaet Rechnung stellen
- Agent: Typ E6, Aktionen A6/Credit Management
- Belege: derived.days_overdue=28 | free_text: 'Der offene Betrag ist im naechsten Lauf am 23.03.2026 enthalten und wird Ihnen dann gutgeschrieben.'
- Begruendung: Die Rechnung ist seit 28 Tagen faellig (E6), aber der Kunde hat in der Nachricht eine konkrete Zahlungsvereinbarung getroffen, die den Zahlungseingang verschiebt. Gemass der Zuordnung fuer E6 bei Hinweis auf Zahlungsschwierigkeiten oder Bitte um Aufschub ist A6 an Credit Management erforderlich.
- Punkte: __  Kommentar: 

### K5-Z2 (C0412, pilot_t07, Run 2)

- Erkennung: none 
- Freitext: Unser Betrieb bleibt vom 22. Dezember bis 5. Januar geschlossen.
- Fakten: Limit 15000, Exposure 12873, Headroom 2127; Liefertermin 2026-01-30 (in None T); Tage ueberfaellig None; Zahlungshistorie schlecht; letzte Aktivitaet Versenden
- Agent: Typ none, Aktionen A3
- Belege: free_text: "Unser Betrieb bleibt vom 22. Dezember bis 5. Januar geschlossen."
- Begruendung: Es liegt kein harter Trigger (Ausnahmetyp) vor, da keine Kreditüberschreitung, Lieferverzögerung, Rechnungsstellung vor Versand oder Zahlungsverzug vorliegt. Der Freitext betrifft eine reine Information über Betriebsferien, was nach der Zuordnung für 'none' mit A3 (nächster Schritt empfehlen) zu behandeln ist.
- Punkte: __  Kommentar: 
