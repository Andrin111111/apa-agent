# Metriken: mock_strict

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
| E2 | 4 | 2 | 50.0 % | guardrail_blockiert: 2 |
| E3 | 4 | 4 | 100.0 % | - |
| E6 | 6 | 5 | 83.3 % | enthaltung: 1 |
| E6:complaint | 2 | 2 | 100.0 % | - |
| E6:irrelevant | 1 | 0 | 0.0 % | enthaltung: 1 |
| E6:payment_announced | 1 | 1 | 100.0 % | - |
| E6:payment_difficulty | 2 | 2 | 100.0 % | - |
| none_text | 3 | 2 | 66.7 % | guardrail_blockiert: 1 |

| Aggregat | n | korrekt | Anteil |
|---|---|---|---|
| deterministisch (E2, E3) | 8 | 6 | 75.0 % |
| Ermessen (E6) | 6 | 5 | 83.3 % |
| Happy Path mit Freitext | 3 | 2 | 66.7 % |
| bewertet gesamt | 17 | 13 | 76.5 % |

- Fehlalarme Agent (Happy Path mit Freitext, Aktion != A0): 1 von 3
- Enthaltungsquote: 1 von 17 (5.9 %)
- Typ-Uebereinstimmung der Ausgabe (ohne E7): 13 von 17

### Aktionen (Run 2)

| Gruppe | n | korrekt | Anteil | Fehlergruende |
|---|---|---|---|---|
| E2 | 4 | 3 | 75.0 % | guardrail_blockiert: 1 |
| E3 | 4 | 3 | 75.0 % | guardrail_blockiert: 1 |
| E6 | 6 | 4 | 66.7 % | guardrail_blockiert: 2 |
| E6:complaint | 2 | 2 | 100.0 % | - |
| E6:irrelevant | 1 | 0 | 0.0 % | guardrail_blockiert: 1 |
| E6:payment_announced | 1 | 1 | 100.0 % | - |
| E6:payment_difficulty | 2 | 1 | 50.0 % | guardrail_blockiert: 1 |
| none_text | 3 | 2 | 66.7 % | guardrail_blockiert: 1 |

| Aggregat | n | korrekt | Anteil |
|---|---|---|---|
| deterministisch (E2, E3) | 8 | 6 | 75.0 % |
| Ermessen (E6) | 6 | 4 | 66.7 % |
| Happy Path mit Freitext | 3 | 2 | 66.7 % |
| bewertet gesamt | 17 | 12 | 70.6 % |

- Fehlalarme Agent (Happy Path mit Freitext, Aktion != A0): 1 von 3
- Enthaltungsquote: 0 von 17 (0.0 %)
- Typ-Uebereinstimmung der Ausgabe (ohne E7): 12 von 17

### Aktionen (Run 3)

| Gruppe | n | korrekt | Anteil | Fehlergruende |
|---|---|---|---|---|
| E2 | 4 | 3 | 75.0 % | guardrail_blockiert: 1 |
| E3 | 4 | 4 | 100.0 % | - |
| E6 | 6 | 4 | 66.7 % | guardrail_blockiert: 2 |
| E6:complaint | 2 | 2 | 100.0 % | - |
| E6:irrelevant | 1 | 0 | 0.0 % | guardrail_blockiert: 1 |
| E6:payment_announced | 1 | 1 | 100.0 % | - |
| E6:payment_difficulty | 2 | 1 | 50.0 % | guardrail_blockiert: 1 |
| none_text | 3 | 3 | 100.0 % | - |

| Aggregat | n | korrekt | Anteil |
|---|---|---|---|
| deterministisch (E2, E3) | 8 | 7 | 87.5 % |
| Ermessen (E6) | 6 | 4 | 66.7 % |
| Happy Path mit Freitext | 3 | 3 | 100.0 % |
| bewertet gesamt | 17 | 14 | 82.4 % |

- Fehlalarme Agent (Happy Path mit Freitext, Aktion != A0): 0 von 3
- Enthaltungsquote: 0 von 17 (0.0 %)
- Typ-Uebereinstimmung der Ausgabe (ohne E7): 14 von 17

- Schema/Guardrail-Vorpruefung: 11 von 51 Ausgaben mit Fehlern {'missing:exception_type': 11, 'missing:actions': 11, 'missing:rationale': 11, 'missing:key_evidence': 11, 'enum:exception_type': 11, 'actions_empty': 11, 'rationale_short': 11}
- Doppelte Ausgaben (gleicher Fall, gleicher Run): 0
- Reproduzierbarkeit: 8 von 17 (47.1 %)
- E5 (nur informativ, concept_only): 0 von 0 korrekt

