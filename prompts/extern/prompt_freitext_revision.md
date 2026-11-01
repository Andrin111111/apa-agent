# Auftrag: Freitext-Vorlagen überarbeiten

Du unterstützt ein Hochschulprojekt (Wirtschaftsinformatik). Wir erzeugen synthetische Kundennachrichten zu Aufträgen und Rechnungen eines Schweizer B2B-Lieferanten (Order-to-Cash). Ein KI-Agent soll diese Nachrichten später einer von vier Kategorien zuordnen. Alle Vorlagen stammen bisher von einem einzigen Sprachmodell. Damit sie nicht alle dieselben Formulierungsmuster tragen, sollst du einen Teil neu schreiben.

## Kategorien

| Kategorie | Bedeutung |
|---|---|
| complaint | Kunde meldet Mangel, Schaden, Falsch- oder Fehllieferung oder eine Funktionsstörung |
| payment_announced | Kunde kündigt eine Zahlung an oder bestätigt, dass sie ausgelöst bzw. terminiert ist |
| payment_difficulty | Kunde kann nicht oder nicht fristgerecht zahlen, bittet um Raten oder Aufschub, schildert finanzielle Engpässe |
| irrelevant | Kein Bezug zu Mangel oder Zahlung (z. B. Adresse, Kontakt, Ferien, Produktanfrage, Lob, Organisatorisches) |

## Aufgabe 1: Neu schreiben

Schreibe die mit **NEU** markierten Vorlagen neu. Regeln:

1. Gleiche Kategorie und gleicher Stil wie das Original. Stil `direkt`: Thema mit typischem Schlüsselwort. Stil `indirekt`: Thema klar erkennbar, aber ohne die typischen Schlüsselwörter der Kategorie (z. B. kein "Reklamation", "Mangel", "Zahlung", "Rate"). Stil `distraktor` (nur irrelevant): enthält Fachwörter aus dem Auftragsumfeld, hat aber keinen Bezug zu Mangel oder Zahlung.
2. Eindeutig genau eine Kategorie. Keine Mischformen (z. B. keine Reklamation mit Zahlungsankündigung).
3. Deutlich andere Formulierung und Situation als das Original, nicht nur Synonyme austauschen.
4. 1 bis 3 Sätze. Realistischer Geschäftston, Tonalität darf variieren (förmlich, knapp, genervt, freundlich).
5. Schweizer Schreibweise und **ASCII**: ae, oe, ue statt Umlauten, ss statt ß, keine Gedankenstriche, keine typografischen Anführungszeichen.
6. Platzhalter sind erlaubt, aber nicht nötig: {rechnungsnr}, {betrag}, {lieferdatum}, {datum} (kürzlich vergangen), {datum_zukunft}, {auftragsnr}. Bei `irrelevant` nur {datum_zukunft} und {auftragsnr}. Keine weiteren Platzhalter, keine anderen geschweiften Klammern.
7. Keine echten Firmen, Personen, Telefonnummern oder IBAN.

## Aufgabe 2: Kritisch prüfen

Prüfe alle 40 Vorlagen (auch die nicht markierten). Melde jede Vorlage, die mehrdeutig ist, zu einer anderen Kategorie passen könnte, unnatürlich klingt oder den Stil verfehlt. Wenn nichts auffällt, schreibe `keine`.

## Ausgabeformat (genau so, ohne weiteren Text)

```
NEU
id|neuer Text
complaint_02|...
```

```
BEFUNDE
id|Befund in einem Satz
payment_announced_05|...
```

## Vorlagen

### complaint

| id | Stil | Aktion | Text |
|---|---|---|---|
| complaint_01 | direkt | **NEU** | Die Lieferung vom {lieferdatum} ist unvollstaendig, es fehlen zwei Positionen. Wir reklamieren dies hiermit und bitten um Nachlieferung. |
| complaint_02 | direkt | prüfen | Wir beanstanden die Lieferung zu Rechnung {rechnungsnr}: Drei Paletten kamen mit gebrochenen Deckeln an. Bitte holen Sie die Ware ab und liefern Sie Ersatz. |
| complaint_03 | direkt | **NEU** | Reklamation: Die gelieferten Artikel entsprechen nicht der bestellten Ausfuehrung. |
| complaint_04 | direkt | prüfen | Mangelruege: Bei 6 von 20 Ventilen tritt nach kurzer Zeit Fluessigkeit aus. Wir erwarten Ihre Stellungnahme. |
| complaint_05 | indirekt | **NEU** | Von den 40 Kartons, die am {lieferdatum} bei uns eingetroffen sind, waren 12 durchnaesst. Der Inhalt ist nicht mehr brauchbar. |
| complaint_06 | indirekt | prüfen | Auf den Etiketten steht Artikel 2250, in den Kartons liegt aber Artikel 2205. Bei uns steht jetzt die Montage still. |
| complaint_07 | indirekt | **NEU** | Seit der Inbetriebnahme laeuft die Anlage nur mit Unterbrechungen. Ihr Techniker hat sich bis heute nicht gemeldet. |
| complaint_08 | indirekt | prüfen | Hallo zusammen, die Kabelrollen vom {lieferdatum} sind 50 statt 100 Meter lang. Koennen Sie das bitte anschauen? |
| complaint_09 | direkt | **NEU** | Wir sind mit der Qualitaet der letzten Lieferung unzufrieden. Die Oberflaechen sind zerkratzt und so nicht verkaufbar. |
| complaint_10 | indirekt | prüfen | Nach zwei Tagen im Einsatz ist bei beiden Steuergeraeten das Display ausgefallen. |

### payment_announced

| id | Stil | Aktion | Text |
|---|---|---|---|
| payment_announced_01 | direkt | **NEU** | Die Zahlung fuer Rechnung {rechnungsnr} ueber {betrag} wurde am {datum} ausgeloest. Sie sollte in den naechsten Tagen bei Ihnen eingehen. |
| payment_announced_02 | direkt | prüfen | Besten Dank fuer Ihre Geduld. Die Zahlung fuer {rechnungsnr} geht mit Valuta {datum_zukunft} an Sie raus. |
| payment_announced_03 | direkt | **NEU** | Zahlung erfolgt mit unserem naechsten Zahlungslauf am {datum_zukunft}. |
| payment_announced_04 | direkt | prüfen | Ueberweisung von {betrag} ist heute Morgen erfolgt, Referenz {rechnungsnr}. |
| payment_announced_05 | indirekt | **NEU** | Unsere Buchhaltung hat den Betrag gestern an Ihre Bank angewiesen. |
| payment_announced_06 | indirekt | prüfen | Wir hatten eine Systemumstellung im Kreditorenwesen. Der offene Betrag ist im naechsten Lauf am {datum_zukunft} enthalten und wird Ihnen dann gutgeschrieben. |
| payment_announced_07 | indirekt | **NEU** | Kurze Info: Der Betrag von {betrag} ist im E-Banking fuer den {datum_zukunft} terminiert. |
| payment_announced_08 | indirekt | prüfen | Kurze Rueckmeldung aus der Buchhaltung: Der Auftrag an die Bank ist am {datum} rausgegangen, der Betrag muesste bald bei Ihnen eingehen. |
| payment_announced_09 | direkt | **NEU** | Wir bestaetigen den Erhalt Ihrer Rechnung {rechnungsnr}. Die Zahlung ist veranlasst. |
| payment_announced_10 | direkt | prüfen | Wir werden die Rechnung {rechnungsnr} noch diese Woche bezahlen, die Freigabe durch die Geschaeftsleitung liegt vor. |

### payment_difficulty

| id | Stil | Aktion | Text |
|---|---|---|---|
| payment_difficulty_01 | direkt | **NEU** | Wir befinden uns derzeit in einem finanziellen Engpass und koennen die Rechnung {rechnungsnr} nicht fristgerecht begleichen. Waere eine Ratenzahlung moeglich? |
| payment_difficulty_02 | direkt | prüfen | Aufgrund eines Liquiditaetsengpasses koennen wir {betrag} nicht auf einmal ueberweisen. Waeren vier Monatsraten fuer Sie akzeptabel? |
| payment_difficulty_03 | direkt | **NEU** | Leider ist ein grosser Kunde von uns in Konkurs gegangen. Wir brauchen mehr Zeit, um die offene Rechnung zu bezahlen. |
| payment_difficulty_04 | direkt | prüfen | Koennen Sie die Faelligkeit der Rechnung {rechnungsnr} um zwei Monate verschieben? Wir haben momentan Zahlungsschwierigkeiten. |
| payment_difficulty_05 | indirekt | **NEU** | Unser Konto ist im Moment leider ausgereizt. Sobald die Gelder aus dem laufenden Projekt eingehen, melden wir uns wieder. |
| payment_difficulty_06 | indirekt | prüfen | Ein Grossprojekt von uns ist geplatzt, und die Bank prueft gerade unsere Kreditlinie. Bis das geklaert ist, sind uns die Haende gebunden. |
| payment_difficulty_07 | indirekt | **NEU** | Gibt es die Moeglichkeit, den Betrag ueber mehrere Monate verteilt abzuzahlen? |
| payment_difficulty_08 | indirekt | prüfen | Wir befinden uns in einem Nachlassverfahren. Saemtliche offenen Forderungen werden ueber den Sachwalter abgewickelt. |
| payment_difficulty_09 | direkt | **NEU** | Wegen Zahlungsausfaellen bei unseren eigenen Kunden koennen wir die Rechnung im Moment nicht bezahlen. Wir schlagen monatliche Teilzahlungen vor. |
| payment_difficulty_10 | indirekt | prüfen | Die Saisoneinnahmen sind dieses Jahr eingebrochen. Fuer {betrag} reicht es aktuell nicht. |

### irrelevant

| id | Stil | Aktion | Text |
|---|---|---|---|
| irrelevant_01 | direkt | **NEU** | Wir ziehen per {datum_zukunft} um. Neue Postadresse: Industriestrasse 14, 8400 Winterthur. |
| irrelevant_02 | direkt | prüfen | Bitte nehmen Sie zur Kenntnis, dass Herr Kaufmann per {datum_zukunft} pensioniert wird. Seine Aufgaben uebernimmt Frau Lutz. |
| irrelevant_03 | direkt | **NEU** | Unser Betrieb bleibt vom 22. Dezember bis 5. Januar geschlossen. |
| irrelevant_04 | direkt | prüfen | Haben Sie die Sicherheitsdatenblaetter zu Ihrem Reinigungsmittel auch auf Franzoesisch? |
| irrelevant_05 | direkt | **NEU** | Gibt es Artikel 4711 auch in einer Ausfuehrung aus Edelstahl? Wir planen eine Folgebestellung. |
| irrelevant_06 | direkt | prüfen | Unser Team freut sich auf den Besuch Ihres Aussendienstes am {datum_zukunft} in Aarau. |
| irrelevant_07 | direkt | **NEU** | Bezueglich Auftrag {auftragsnr}: Koennen Sie uns fuer unser Nachhaltigkeitsreporting die CO2-Angaben zu den Produkten senden? |
| irrelevant_08 | distraktor | prüfen | Die letzte Lieferung war wie immer tadellos, Kompliment an Ihr Lager-Team! |
| irrelevant_09 | distraktor | **NEU** | Bitte nutzen Sie fuer Anlieferungen bei uns ab sofort die Rampe 3 auf der Rueckseite des Gebaeudes. |
| irrelevant_10 | distraktor | prüfen | Fuer kuenftige Bestellungen benoetigen wir auf der Auftragsbestaetigung zusaetzlich unsere Projektnummer. Fuer Auftrag {auftragsnr} ist das nicht noetig. |
