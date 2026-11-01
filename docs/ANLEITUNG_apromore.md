# Anleitung: Event Log in Apromore importieren (AP7)

Stand 01.11.2026. Für die Gruppenmitglieder 2 und 3. Dauer ca. 45 bis 60 min.

## Zweck

Apromore dient im Projekt **nur der Visualisierung** für die Zwischenpräsentation (Folie 3 "Referenzprozess und Ausnahmefälle"). Die Erkennung und die Auswertung laufen über Python (PM4Py, `src/detect.py`, `src/metrics.py`) und hängen nicht von Apromore ab.

Ziele:
1. Prozesslandkarte des O2C-Prozesses (wie läuft der Prozess tatsächlich?)
2. Variantenansicht (wie stark weichen Fälle vom Happy Path ab?)
3. Plausibilitätsblick auf das synthetische Log (passen Häufigkeiten und Abfolgen zu einem O2C-Prozess?)

## 1. Voraussetzungen

| # | Was | Erwartung |
|---|---|---|
| 1 | Zugang Apromore (Academic Alliance) | Login funktioniert |
| 2 | Importdateien erzeugen (Jan oder wer Python hat): `python src/export_apromore.py` aus dem Repo-Root | Ordner `out/apromore/` mit drei Dateien |

Die Dateien in `out/apromore/`:

| Datei | Inhalt | Verwendung |
|---|---|---|
| `apromore_events.csv` | alle 1000 Fälle, 5905 Events | Ausnahmen zeigen, Filter nach Typ |
| `apromore_events_closed.csv` | 442 abgeschlossene Fälle, 3674 Events | saubere Prozesslandkarte für die Folie |
| `export_report.md` | Fälle, Events, Varianten, Top-10-Varianten | Abgleich nach dem Import |

Warum zwei Dateien: Das Log ist ein Snapshot. 558 Fälle laufen noch und enden mitten im Prozess. In der vollen Datei erscheinen sie als viele kurze "abgebrochene" Varianten, das wirkt auf einer Folie verwirrend.
Wichtig: In der Datei mit den abgeschlossenen Fällen kommen **keine** E2-, E3-, E6- und E7-Fälle vor (diese sind alle noch offen). Für Ansichten zu Ausnahmen immer `apromore_events.csv` verwenden.

## 2. Import

Für jede der beiden CSV-Dateien einzeln: im Portal hochladen (Upload / Import Log), danach erscheint die Spaltenzuordnung. Die Bezeichnungen können je nach Apromore-Version leicht abweichen.

| Spalte | Typ in Apromore |
|---|---|
| `case_id` | Case ID |
| `activity` | Activity |
| `timestamp` | End timestamp, Format `yyyy-MM-dd HH:mm:ss` |
| `resource` | Resource |
| `role` | Role (falls nicht angeboten: Event attribute) |
| `order_value`, `customer_segment`, `credit_limit`, `open_items`, `payment_history`, `payment_terms_days`, `promised_delivery_date`, `has_free_text`, `case_status`, `exception_type`, `exception_class` | Case attribute |

Hinweise:
- Es gibt nur einen Zeitstempel pro Event (kein Start). Apromore zeigt deshalb Warte- und Durchlaufzeiten zwischen Events, keine Bearbeitungszeiten. Auf der Folie nicht als "Bearbeitungsdauer" beschriften.
- Kein Fall hat zwei Events mit gleichem Zeitstempel, die Reihenfolge ist also eindeutig.
- Namen in Apromore: `O2C_alle` und `O2C_abgeschlossen`.

## 3. Abgleich nach dem Import

In der Log-Übersicht prüfen, ob die Zahlen mit `export_report.md` übereinstimmen:

| Log | Fälle | Events | Varianten |
|---|---|---|---|
| `O2C_alle` | 1000 | 5905 | 35 |
| `O2C_abgeschlossen` | 442 | 3674 | 7 |

Weichen die Zahlen ab, ist meist das Zeitformat oder eine Spaltenzuordnung falsch. Import wiederholen, nicht weiterarbeiten.

## 4. Ansichten und Screenshots

Im Process Discoverer öffnen. Screenshots als PNG speichern (Export-Funktion von Apromore oder Bildschirmfoto), Ablage in `out/apromore/screens/`.

| # | Log | Ansicht | Einstellungen | Dateiname |
|---|---|---|---|---|
| S1 | `O2C_abgeschlossen` | Prozesslandkarte, Häufigkeit | alle Aktivitäten und Kanten (Regler auf 100 %) | `s1_map_abgeschlossen.png` |
| S2 | `O2C_abgeschlossen` | Prozesslandkarte, Dauer (Median) | wie S1 | `s2_map_dauer.png` |
| S3 | `O2C_abgeschlossen` | Variantenansicht | 7 Varianten, Happy Path ist Variante 1 mit 71 % | `s3_varianten.png` |
| S4 | `O2C_alle` | Prozesslandkarte, Häufigkeit | Filter Case attribute `exception_class` = `deterministisch` | `s4_map_deterministisch.png` |
| S5 | `O2C_alle` | Prozesslandkarte, Häufigkeit | Filter `exception_class` = `ermessen` | `s5_map_ermessen.png` |
| S6 (optional) | `O2C_alle` | Prozesslandkarte | Filter `exception_type` = `E7` oder `customer_segment` = `A` | `s6_map_<filter>.png` |

Was die Bilder zeigen sollen:
- S1 und S3: Der Prozess folgt meist dem Referenzpfad, rund 29 % der abgeschlossenen Fälle weichen trotzdem ab (Auftrag ändern, Zahlungserinnerung, Teillieferung, Rechnung vor Versand).
- S4 und S5: Ausnahmefälle stecken in einem Prozessschritt fest oder laufen anders. Das ist die Stelle, an der der Agent ansetzt.

## 5. Rückmeldung

Im Gruppenchat oder an Jan:
1. Die Screenshots aus `out/apromore/screens/`
2. Ergebnis des Abgleichs (Abschnitt 3: stimmen die Zahlen?)
3. Drei Sätze zur Funktionsweise von Apromore (offener Punkt aus dem Kontextdokument, Abschnitt 1): Was macht das Tool, welche Ansichten wurden genutzt, was fiel auf?
4. Auffälligkeiten, die unplausibel wirken (z.B. seltsame Abfolgen oder Zeiten). Diese gehen als Befund in den Generator-Review.
