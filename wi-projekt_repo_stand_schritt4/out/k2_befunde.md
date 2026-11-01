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
