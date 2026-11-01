# Metriken: baseline_e6

Erzeugt von `src/metrics.py`. Bewertungsregeln M1 bis M4 siehe Modulkopf.

## Umfang: E6 alle (80)

### Erkennung

| Typ | n (GT) | TP | FP | FN | Precision | Recall |
|---|---|---|---|---|---|---|
| E6 | 80 | 80 | 0 | 0 | 100.0 % | 100.0 % |

- Fehlalarme Erkennung (Grenzfaelle): 0 von 0
- Routing: 80 Faelle an den Agenten, davon fehlend (muesste geroutet sein): 0 von 80

### Aktionen (Run 1)

| Gruppe | n | korrekt | Anteil | Fehlergruende |
|---|---|---|---|---|
| E2 | 0 | 0 | n/a | - |
| E3 | 0 | 0 | n/a | - |
| E6 | 80 | 59 | 73.8 % | aktionsmenge: 21 |
| E6:complaint | 20 | 10 | 50.0 % | aktionsmenge: 10 |
| E6:irrelevant | 20 | 20 | 100.0 % | - |
| E6:payment_announced | 20 | 16 | 80.0 % | aktionsmenge: 4 |
| E6:payment_difficulty | 20 | 13 | 65.0 % | aktionsmenge: 7 |
| none_text | 0 | 0 | n/a | - |

| Aggregat | n | korrekt | Anteil |
|---|---|---|---|
| deterministisch (E2, E3) | 0 | 0 | n/a |
| Ermessen (E6) | 80 | 59 | 73.8 % |
| Happy Path mit Freitext | 0 | 0 | n/a |
| bewertet gesamt | 80 | 59 | 73.8 % |

- Fehlalarme Agent (Happy Path mit Freitext, Aktion != A0): 0 von 0
- Enthaltungsquote: 0 von 80 (0.0 %)
- Typ-Uebereinstimmung der Ausgabe (ohne E7): 80 von 80

- Schema/Guardrail-Vorpruefung: 0 von 80 Ausgaben mit Fehlern 
- Doppelte Ausgaben (gleicher Fall, gleicher Run): 0
- Reproduzierbarkeit: nur 1 Run
- E5 (nur informativ, concept_only): 0 von 0 korrekt

