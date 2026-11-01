# Metriken: baseline

Erzeugt von `src/metrics.py`. Bewertungsregeln M1 bis M4 siehe Modulkopf.

## Umfang: alle Faelle (1000)

### Erkennung

| Typ | n (GT) | TP | FP | FN | Precision | Recall |
|---|---|---|---|---|---|---|
| E2 | 60 | 60 | 0 | 0 | 100.0 % | 100.0 % |
| E3 | 60 | 60 | 0 | 0 | 100.0 % | 100.0 % |
| E5 | 40 | 40 | 0 | 0 | 100.0 % | 100.0 % |
| E6 | 80 | 80 | 0 | 0 | 100.0 % | 100.0 % |
| E7 | 60 | 60 | 0 | 0 | 100.0 % | 100.0 % |
| none | 700 | 700 | 0 | 0 | 100.0 % | 100.0 % |

- Fehlalarme Erkennung (Grenzfaelle): 0 von 35
- Routing: 370 Faelle an den Agenten, davon fehlend (muesste geroutet sein): 0 von 370

### Aktionen (Run 1)

| Gruppe | n | korrekt | Anteil | Fehlergruende |
|---|---|---|---|---|
| E2 | 60 | 60 | 100.0 % | - |
| E3 | 60 | 60 | 100.0 % | - |
| E5 | 40 | 40 | 100.0 % | - |
| E6 | 80 | 59 | 73.8 % | aktionsmenge: 21 |
| E6:complaint | 20 | 10 | 50.0 % | aktionsmenge: 10 |
| E6:irrelevant | 20 | 20 | 100.0 % | - |
| E6:payment_announced | 20 | 16 | 80.0 % | aktionsmenge: 4 |
| E6:payment_difficulty | 20 | 13 | 65.0 % | aktionsmenge: 7 |
| none_text | 70 | 70 | 100.0 % | - |

| Aggregat | n | korrekt | Anteil |
|---|---|---|---|
| deterministisch (E2, E3) | 120 | 120 | 100.0 % |
| Ermessen (E6) | 80 | 59 | 73.8 % |
| Happy Path mit Freitext | 70 | 70 | 100.0 % |
| bewertet gesamt | 270 | 249 | 92.2 % |

- Fehlalarme Agent (Happy Path mit Freitext, Aktion != A0): 0 von 70
- Enthaltungsquote: 0 von 370 (0.0 %)
- Typ-Uebereinstimmung der Ausgabe (ohne E7): 310 von 310

- Schema/Guardrail-Vorpruefung: 0 von 370 Ausgaben mit Fehlern 
- Doppelte Ausgaben (gleicher Fall, gleicher Run): 0
- Reproduzierbarkeit: nur 1 Run
- E5 (nur informativ, concept_only): 40 von 40 korrekt

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

- Schema/Guardrail-Vorpruefung: 0 von 17 Ausgaben mit Fehlern 
- Doppelte Ausgaben (gleicher Fall, gleicher Run): 0
- Reproduzierbarkeit: nur 1 Run
- E5 (nur informativ, concept_only): 0 von 0 korrekt

