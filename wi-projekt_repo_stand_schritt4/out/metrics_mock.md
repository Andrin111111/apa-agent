# Metriken: mock

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
| E2 | 4 | 3 | 75.0 % | rolle: 1 |
| E3 | 4 | 4 | 100.0 % | - |
| E6 | 6 | 5 | 83.3 % | enthaltung: 1 |
| E6:complaint | 2 | 2 | 100.0 % | - |
| E6:irrelevant | 1 | 0 | 0.0 % | enthaltung: 1 |
| E6:payment_announced | 1 | 1 | 100.0 % | - |
| E6:payment_difficulty | 2 | 2 | 100.0 % | - |
| none_text | 3 | 2 | 66.7 % | aktionsmenge: 1 |

| Aggregat | n | korrekt | Anteil |
|---|---|---|---|
| deterministisch (E2, E3) | 8 | 7 | 87.5 % |
| Ermessen (E6) | 6 | 5 | 83.3 % |
| Happy Path mit Freitext | 3 | 2 | 66.7 % |
| bewertet gesamt | 17 | 14 | 82.4 % |

- Fehlalarme Agent (Happy Path mit Freitext, Aktion != A0): 1 von 3
- Enthaltungsquote: 1 von 17 (5.9 %)
- Typ-Uebereinstimmung der Ausgabe (ohne E7): 15 von 17

### Aktionen (Run 2)

| Gruppe | n | korrekt | Anteil | Fehlergruende |
|---|---|---|---|---|
| E2 | 4 | 3 | 75.0 % | rolle: 1 |
| E3 | 4 | 4 | 100.0 % | - |
| E6 | 6 | 4 | 66.7 % | enthaltung: 2 |
| E6:complaint | 2 | 2 | 100.0 % | - |
| E6:irrelevant | 1 | 0 | 0.0 % | enthaltung: 1 |
| E6:payment_announced | 1 | 1 | 100.0 % | - |
| E6:payment_difficulty | 2 | 1 | 50.0 % | enthaltung: 1 |
| none_text | 3 | 2 | 66.7 % | aktionsmenge: 1 |

| Aggregat | n | korrekt | Anteil |
|---|---|---|---|
| deterministisch (E2, E3) | 8 | 7 | 87.5 % |
| Ermessen (E6) | 6 | 4 | 66.7 % |
| Happy Path mit Freitext | 3 | 2 | 66.7 % |
| bewertet gesamt | 17 | 13 | 76.5 % |

- Fehlalarme Agent (Happy Path mit Freitext, Aktion != A0): 1 von 3
- Enthaltungsquote: 2 von 17 (11.8 %)
- Typ-Uebereinstimmung der Ausgabe (ohne E7): 15 von 17

### Aktionen (Run 3)

| Gruppe | n | korrekt | Anteil | Fehlergruende |
|---|---|---|---|---|
| E2 | 4 | 4 | 100.0 % | - |
| E3 | 4 | 4 | 100.0 % | - |
| E6 | 6 | 4 | 66.7 % | enthaltung: 1, aktionsmenge: 1 |
| E6:complaint | 2 | 2 | 100.0 % | - |
| E6:irrelevant | 1 | 0 | 0.0 % | enthaltung: 1 |
| E6:payment_announced | 1 | 1 | 100.0 % | - |
| E6:payment_difficulty | 2 | 1 | 50.0 % | aktionsmenge: 1 |
| none_text | 3 | 3 | 100.0 % | - |

| Aggregat | n | korrekt | Anteil |
|---|---|---|---|
| deterministisch (E2, E3) | 8 | 8 | 100.0 % |
| Ermessen (E6) | 6 | 4 | 66.7 % |
| Happy Path mit Freitext | 3 | 3 | 100.0 % |
| bewertet gesamt | 17 | 15 | 88.2 % |

- Fehlalarme Agent (Happy Path mit Freitext, Aktion != A0): 0 von 3
- Enthaltungsquote: 1 von 17 (5.9 %)
- Typ-Uebereinstimmung der Ausgabe (ohne E7): 15 von 17

- Schema/Guardrail-Vorpruefung: 10 von 51 Ausgaben mit Fehlern {'target_role_missing': 2, 'json_parse': 2, 'rationale_short': 2, 'action_not_in_catalog': 1, 'unknown_requires_A6': 2, 'missing:key_evidence': 1}
- Doppelte Ausgaben (gleicher Fall, gleicher Run): 0
- Reproduzierbarkeit: 10 von 17 (58.8 %)
- E5 (nur informativ, concept_only): 0 von 0 korrekt

