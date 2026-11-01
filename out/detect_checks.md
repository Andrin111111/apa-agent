# Sensitivitaet der Erkennung (Mutanten)

Falsche Regelvarianten gegen die Ground Truth. Fehler > 0 heisst: Die Daten entlarven den Mutanten.

| Variante | falsch erkannt | davon Grenzfaelle (boundary_*) | Beispiel-Faelle |
|---|---|---|---|
| Referenz (detect.py) | 0 | 0 |  |
| E2 >= statt > | 13 | 13 | C0036, C0060, C0129, C0192 |
| E3 <= 2 statt < 2 | 12 | 11 | C0140, C0178, C0344, C0345 |
| E6 <= statt < | 11 | 11 | C0105, C0106, C0142, C0527 |
| Zeitpunkt statt Tagesbasis (E3, E6) | 23 | 22 | C0105, C0106, C0140, C0142 |
| keine Vorrangregel E7 | 60 | 0 | C0007, C0031, C0061, C0072 |

- E5: Faelle mit Rechnung und Versand zum selben Zeitstempel: 0, am selben Tag: 205 (AN4 Zeitstempel statt Tag ist relevant)
