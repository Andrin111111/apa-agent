# Schritt 5: Tabellen (erzeugt von `src/step5_eval.py`)

## 1 Aktionskorrektheit nach Typ (roh / strikt)

Pro Run: korrekt von n. Pilot: 3 Runs. E6-Zusatzlauf: 1 Run.

| Lauf | Gruppe | n | Run 1 roh | Run 2 roh | Run 3 roh | Summe roh | Summe strikt | Fehlergruende (roh) |
|---|---|---|---|---|---|---|---|---|
| pilot_t0 | E2 | 4 | 4/4 | 4/4 | 4/4 | 12/12 (100.0 %) | 12/12 (100.0 %) | - |
| pilot_t0 | E3 | 4 | 4/4 | 4/4 | 4/4 | 12/12 (100.0 %) | 12/12 (100.0 %) | - |
| pilot_t0 | E6 | 6 | 6/6 | 6/6 | 6/6 | 18/18 (100.0 %) | 18/18 (100.0 %) | - |
| pilot_t0 | Happy Path mit Freitext | 3 | 3/3 | 3/3 | 3/3 | 9/9 (100.0 %) | 9/9 (100.0 %) | - |
| pilot_t0 | gesamt | 17 | 17/17 | 17/17 | 17/17 | 51/51 (100.0 %) | 51/51 (100.0 %) | - |
| pilot_t07 | E2 | 4 | 4/4 | 4/4 | 4/4 | 12/12 (100.0 %) | 12/12 (100.0 %) | - |
| pilot_t07 | E3 | 4 | 4/4 | 4/4 | 4/4 | 12/12 (100.0 %) | 12/12 (100.0 %) | - |
| pilot_t07 | E6 | 6 | 6/6 | 6/6 | 6/6 | 18/18 (100.0 %) | 18/18 (100.0 %) | - |
| pilot_t07 | Happy Path mit Freitext | 3 | 3/3 | 2/3 | 3/3 | 8/9 (88.9 %) | 8/9 (88.9 %) | aktionsmenge: 1 |
| pilot_t07 | gesamt | 17 | 17/17 | 16/17 | 17/17 | 50/51 (98.0 %) | 50/51 (98.0 %) | aktionsmenge: 1 |
| e6_t0 | E6 | 80 | 79/80 |  |  | 79/80 (98.8 %) | 79/80 (98.8 %) | aktionsmenge: 1 |
| e6_t0 | gesamt | 80 | 79/80 |  |  | 79/80 (98.8 %) | 79/80 (98.8 %) | aktionsmenge: 1 |

### E6 nach Kategorie (roh, alle Runs zusammen)

| Lauf | Kategorie | korrekt | Anteil |
|---|---|---|---|
| pilot_t0 | complaint | 6/6 | 100.0 % |
| pilot_t0 | irrelevant | 3/3 | 100.0 % |
| pilot_t0 | payment_announced | 3/3 | 100.0 % |
| pilot_t0 | payment_difficulty | 6/6 | 100.0 % |
| pilot_t07 | complaint | 6/6 | 100.0 % |
| pilot_t07 | irrelevant | 3/3 | 100.0 % |
| pilot_t07 | payment_announced | 3/3 | 100.0 % |
| pilot_t07 | payment_difficulty | 6/6 | 100.0 % |
| e6_t0 | complaint | 20/20 | 100.0 % |
| e6_t0 | irrelevant | 20/20 | 100.0 % |
| e6_t0 | payment_announced | 19/20 | 95.0 % |
| e6_t0 | payment_difficulty | 20/20 | 100.0 % |

## 2 E6 nach Textstil: Agent (e6_t0) vs. Baseline (80 Faelle)

| Stil | n | Agent roh | Agent strikt | Baseline | nur Agent korrekt | nur Baseline korrekt | beide falsch |
|---|---|---|---|---|---|---|---|
| direkt | 43 | 43 (100.0 %) | 43 (100.0 %) | 43 (100.0 %) | 0 | 0 | 0 |
| indirekt | 32 | 31 (96.9 %) | 31 (96.9 %) | 11 (34.4 %) | 20 | 0 | 1 |
| distraktor | 5 | 5 (100.0 %) | 5 (100.0 %) | 5 (100.0 %) | 0 | 0 | 0 |
| gesamt | 80 | 79 (98.8 %) | 79 (98.8 %) | 59 (73.8 %) | 20 | 0 | 1 |

- Exakter McNemar-Test (roh, alle 80): diskordant 20 (nur Agent) vs. 0 (nur Baseline), p = 0.0000. Faelle teilen Vorlagen, die Unabhaengigkeitsannahme ist verletzt (siehe pro Vorlage).

- Nur indirekt: 20 vs. 0, p = 0.0000

### E6 nach Kategorie und Stil (roh)

| Kategorie | Stil | n | Agent | Baseline |
|---|---|---|---|---|
| complaint | direkt | 7 | 7 | 7 |
| complaint | indirekt | 13 | 13 | 3 |
| irrelevant | direkt | 15 | 15 | 15 |
| irrelevant | distraktor | 5 | 5 | 5 |
| payment_announced | direkt | 13 | 13 | 13 |
| payment_announced | indirekt | 7 | 6 | 3 |
| payment_difficulty | direkt | 8 | 8 | 8 |
| payment_difficulty | indirekt | 12 | 12 | 5 |

### Pro Vorlage (Cluster)

- Vorlagen: 34. Mittel der Vorlagen-Trefferquoten: Agent 98.5 %, Baseline 76.5 %.
- Agent pro Vorlage: immer korrekt 33, immer falsch 0, gemischt 1 (payment_announced_06).
- Indirekte Vorlagen: 12, davon Agent immer korrekt 11, Baseline immer korrekt 4.
- Vorzeichentest auf Vorlagenebene (Vorlage = Einheit): Agent besser 8, schlechter 0, gleich 26, p = 0.0078 (exakt, zweiseitig).

## 3 Reproduzierbarkeit

Identisch = gleicher Typ, gleiche Aktionsmenge, gleiche Rollen ueber alle Runs (wie metrics.py).

| Lauf | Faelle | identisch (Signatur) | identisch (Rohtext) | Korrektheit 3/3 | 2/3 | 1/3 | 0/3 |
|---|---|---|---|---|---|---|---|
| pilot_t0 | 17 | 17/17 | 17/17 | 17/17 | 0 | 0 | 0 |
| pilot_t07 | 17 | 12/17 | 0/17 | 16/17 | 1 | 0 | 0 |

Abweichende Faelle:

- pilot_t07 C0067 (E3/none): R1 A4/Vertrieb (E3) | R2 A2 (E3) | R3 A4 (E3)
- pilot_t07 C0166 (E3/none): R1 A2+A4/Lager/Logistik (E3) | R2 A4 (E3) | R3 A2+A4 (E3)
- pilot_t07 C0412 (none/irrelevant): R1 A0 (none) | R2 A3 (none) | R3 A0 (none)
- pilot_t07 C0447 (E6/irrelevant): R1 A3 (E6) | R2 A3/Vertrieb (E6) | R3 A3 (E6)
- pilot_t07 C0642 (E3/none): R1 A2 (E3) | R2 A2 (E3) | R3 A2+A4 (E3)

### Querpruefung ueber Sitzungen (gleiche Konfiguration, T = 0, Seed 42)

- 9 Paare (smoke_v12 vs. pilot_t0 Run 1: 3 Faelle; pilot_t0 Run 1 vs. e6_t0: 6 E6-Pilotfaelle): Signatur identisch 9/9, Rohtext identisch 9/9.

- pilot_t0 Run 1 vs. pilot_t07 Run 1 (beide Seed 42): Signatur verschieden in 4 von 17 Faellen (C0067, C0166, C0537, C0642).

## 4 Enthaltungen, Guardrails, Dispositionen, Laufzeit

| Lauf | Aufrufe | Transportfehler | Parsefehler | blockiert | Enthaltungen | Typ = Erkennung | Hinweise (nicht blockierend) | Dispositionen |
|---|---|---|---|---|---|---|---|---|
| smoke_v12 | 6 | 0 | 0 | 0 | 0 | 6/6 | - | executed: 2, pending_approval: 4 |
| pilot_t0 | 51 | 0 | 0 | 0 | 0 | 51/51 | - | executed: 27, pending_approval: 24 |
| pilot_t07 | 51 | 0 | 0 | 0 | 0 | 51/51 | role_on_non_role_action: 3, evidence_unknown_field: 1 | executed: 27, pending_approval: 24 |
| e6_t0 | 80 | 0 | 0 | 0 | 0 | 80/80 | - | executed: 39, pending_approval: 41 |

| Lauf | Aufrufe | Mittel s | Median s | P95 s | Max s | Summe min | Tokens ein (Mittel) | Tokens aus (Mittel / Max) | done_reason |
|---|---|---|---|---|---|---|---|---|---|
| smoke_v12 | 6 | 7.1 | 6.6 | 10.1 | 10.1 | 0.7 | 1984 | 174 / 187 | stop: 6 |
| pilot_t0 | 51 | 6.3 | 6.4 | 7.5 | 7.5 | 5.3 | 2041 | 165 / 187 | stop: 51 |
| pilot_t07 | 51 | 6.9 | 6.8 | 8.4 | 9.3 | 5.9 | 2041 | 173 / 251 | stop: 51 |
| e6_t0 | 80 | 7.1 | 7.1 | 8.0 | 8.4 | 9.5 | 2136 | 174 / 209 | stop: 80 |

## 5 Fehlerliste

2 Zeilen (roh oder strikt falsch) in `out/step5_errors.csv`.

| Lauf | Run | Fall | GT | Kategorie | Stil | Ausgabe Typ | Ausgabe Aktionen | Soll | Grund roh | Grund strikt |
|---|---|---|---|---|---|---|---|---|---|---|
| e6_t0 | 1 | C0776 | E6 | payment_announced | indirekt | E6 | A6/Credit Management | [["A0"]] | aktionsmenge | aktionsmenge |
| pilot_t07 | 2 | C0412 | none | irrelevant |  | none | A3 | [["A0"]] | aktionsmenge | aktionsmenge |

## 6 K5-Stichprobe: 18 plus 2 Zusatz Begruendungen in `out/k5_stichprobe.md|csv`, Schluessel `out/k5_key.csv`
