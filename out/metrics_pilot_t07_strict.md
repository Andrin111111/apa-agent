# Metriken: pilot_t07_strict

Erzeugt von `src/metrics.py`. Bewertungsregeln M1 bis M4 siehe Modulkopf.

## Umfang: Pilot (20)

### Erkennung

| Typ | n (GT) | TP | FP | FN | Precision | Recall |
|---|---|---|---|---|---|---|
| E2 | 4 | 4 | 0 | 0 | 100.0 % | 100.0 % |
| E3 | 4 | 4 | 0 | 0 | 100.0 % | 100.0 % |
| E6 | 6 | 6 | 0 | 0 | 100.0 % | 100.0 % |
| none | 6 | 6 | 0 | 0 | 100.0 % | 100.0 % |

- Fehlalarme Erkennung (Grenzfaelle): 0 von 0
- Routing: 17 Faelle an den Agenten, davon fehlend (muesste geroutet sein): 0 von 17

### Aktionen (Run 1)

| Gruppe | n | korrekt | Anteil | Fehlergruende |
|---|---|---|---|---|
| E2 | 4 | 4 | 100.0 % | - |
| E3 | 4 | 4 | 100.0 % | - |
| E6 | 6 | 6 | 100.0 % | - |
| E6:complaint | 2 | 2 | 100.0 % | - |
| E6:irrelevant | 1 | 1 | 100.0 % | - |
| E6:payment_announced | 1 | 1 | 100.0 % | - |
| E6:payment_difficulty | 2 | 2 | 100.0 % | - |
| none_text | 3 | 3 | 100.0 % | - |

| Aggregat | n | korrekt | Anteil |
|---|---|---|---|
| deterministisch (E2, E3) | 8 | 8 | 100.0 % |
| Ermessen (E6) | 6 | 6 | 100.0 % |
| Happy Path mit Freitext | 3 | 3 | 100.0 % |
| bewertet gesamt | 17 | 17 | 100.0 % |

- Fehlalarme Agent (Happy Path mit Freitext, Aktion != A0): 0 von 3
- Enthaltungsquote: 0 von 17 (0.0 %)
- Typ-Uebereinstimmung der Ausgabe (ohne E7): 17 von 17

### Aktionen (Run 2)

| Gruppe | n | korrekt | Anteil | Fehlergruende |
|---|---|---|---|---|
| E2 | 4 | 4 | 100.0 % | - |
| E3 | 4 | 4 | 100.0 % | - |
| E6 | 6 | 6 | 100.0 % | - |
| E6:complaint | 2 | 2 | 100.0 % | - |
| E6:irrelevant | 1 | 1 | 100.0 % | - |
| E6:payment_announced | 1 | 1 | 100.0 % | - |
| E6:payment_difficulty | 2 | 2 | 100.0 % | - |
| none_text | 3 | 2 | 66.7 % | aktionsmenge: 1 |

| Aggregat | n | korrekt | Anteil |
|---|---|---|---|
| deterministisch (E2, E3) | 8 | 8 | 100.0 % |
| Ermessen (E6) | 6 | 6 | 100.0 % |
| Happy Path mit Freitext | 3 | 2 | 66.7 % |
| bewertet gesamt | 17 | 16 | 94.1 % |

- Fehlalarme Agent (Happy Path mit Freitext, Aktion != A0): 1 von 3
- Enthaltungsquote: 0 von 17 (0.0 %)
- Typ-Uebereinstimmung der Ausgabe (ohne E7): 17 von 17

### Aktionen (Run 3)

| Gruppe | n | korrekt | Anteil | Fehlergruende |
|---|---|---|---|---|
| E2 | 4 | 4 | 100.0 % | - |
| E3 | 4 | 4 | 100.0 % | - |
| E6 | 6 | 6 | 100.0 % | - |
| E6:complaint | 2 | 2 | 100.0 % | - |
| E6:irrelevant | 1 | 1 | 100.0 % | - |
| E6:payment_announced | 1 | 1 | 100.0 % | - |
| E6:payment_difficulty | 2 | 2 | 100.0 % | - |
| none_text | 3 | 3 | 100.0 % | - |

| Aggregat | n | korrekt | Anteil |
|---|---|---|---|
| deterministisch (E2, E3) | 8 | 8 | 100.0 % |
| Ermessen (E6) | 6 | 6 | 100.0 % |
| Happy Path mit Freitext | 3 | 3 | 100.0 % |
| bewertet gesamt | 17 | 17 | 100.0 % |

- Fehlalarme Agent (Happy Path mit Freitext, Aktion != A0): 0 von 3
- Enthaltungsquote: 0 von 17 (0.0 %)
- Typ-Uebereinstimmung der Ausgabe (ohne E7): 17 von 17

- Schema/Guardrail-Vorpruefung: 0 von 51 Ausgaben mit Fehlern 
- Doppelte Ausgaben (gleicher Fall, gleicher Run): 0
- Reproduzierbarkeit: 12 von 17 (70.6 %)
- E5 (nur informativ, concept_only): 0 von 0 korrekt

