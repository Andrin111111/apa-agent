# Anleitung: Agent lokal ausführen (Rauchtest K4 und Läufe Schritt 5)

Stand 01.11.2026, Schritt 4. Alle Befehle aus dem Repo-Root. Python 3 mit pandas, numpy, PyYAML (keine weiteren Pakete).
Modell in den Beispielen: `qwen3.5:9b-q4_K_M` (Empfehlung, Entscheid an K4). Bei anderem Modell überall `--model` und das Label anpassen.
Wichtig: Nicht `qwen3.5:9b` ziehen. Dieser Tag lädt auf dem Mac einen MLX-Build, der kein Schema erzwingt (HTTP 501). Immer `qwen3.5:9b-q4_K_M`.

## 1. Vorbereitung (einmalig, ca. 15 min)

| # | Befehl | Erwartung |
|---|---|---|
| 1 | `ollama --version` | ≥ 0.31.2 (gemeldet: 0.40.13). Ältere Versionen ignorieren bei Qwen 3.5 mit `think=false` das Schema (Ollama-Issue 14645). |
| 2 | `ollama pull qwen3.5:9b-q4_K_M` | Download ca. 6,6 GB |
| 3 | `python -m unittest discover -s tests` | `Ran 37 tests ... OK` |
| 4 | `python src/llm_client.py check --model qwen3.5:9b-q4_K_M --think off` | letzte Zeile `ERGEBNIS: OK, Schema wird erzwungen` |

Zu 4: Der Check verlangt vom Modell Prosa, gibt aber ein fremdes Schema vor. Nur wenn das Decoding das Schema erzwingt, kommt JSON zurück.
Bei `FEHLER`: erneut mit `--endpoint generate` prüfen. Ist das OK, alle folgenden Läufe mit `--endpoint generate` starten (für alle Läufe gleich, im Bericht notieren).

Während der Läufe: Netzteil anschliessen, andere grosse Programme schliessen. Ruhezustand verhindern mit `caffeinate -i` vor dem Befehl.

## 2. Rauchtest für K4 (6 Aufrufe, ca. 2 min)

Je ein Pilotfall E2 (C0317), E3 (C0067), E6 (C0880, indirekte Reklamation), k = 2:

```
caffeinate -i python src/run_agent.py --cases C0317,C0067,C0880 --k 2 --client ollama --model qwen3.5:9b-q4_K_M --think off --label smoke
python src/audit_view.py --label smoke
```

Prüfen:
- Schlusszeile: `6/6 Paare`, `Parsefehler 0`, `Transportfehler 0`. Blockierte Ausgaben notieren (kein Abbruchgrund, aber Befund).
- Run 1 und Run 2 pro Fall identisch (Temperatur 0, fester Seed)?
- C0317: A6 an Credit Management, Disposition `pending_approval`. C0067: A4 und/oder A2, `executed`. C0880: A5 an Kundendienst, `pending_approval`.
- Begründung verständlich und auf den Fall bezogen? `key_evidence` verweist auf existierende Felder?
- Reihenfolge der Felder in der Rohausgabe: `python src/audit_view.py --label smoke --n 1` zeigt geparst; roh: in `out/audit_log.jsonl` steht `key_evidence` und `rationale` vor `actions` (Annahme G3).
- Laufzeit pro Aufruf (letzte Spalte, ms). Hochrechnung Schritt 5: 182 Aufrufe.

## 3. Läufe Schritt 5 (erst nach K4-Freigabe)

| Lauf | Befehl | Aufrufe |
|---|---|---|
| Pilot, T = 0 | `caffeinate -i python src/run_agent.py --cases pilot --k 3 --client ollama --model qwen3.5:9b-q4_K_M --think off --label pilot_t0` | 51 |
| E6-Zusatzlauf, T = 0 | `caffeinate -i python src/run_agent.py --cases e6_full --k 1 --client ollama --model qwen3.5:9b-q4_K_M --think off --label e6_t0` | 80 |
| Pilot, T = 0,7 | `caffeinate -i python src/run_agent.py --cases pilot --k 3 --client ollama --model qwen3.5:9b-q4_K_M --think off --temperature 0.7 --seed-mode per_run --label pilot_t07` | 51 |

- `--seed-mode per_run` (Seed 42, 43, 44) ist beim Temperaturlauf nötig: Mit festem Seed wäre auch bei T > 0 jeder Run gleich, und der Lauf zeigte keine Streuung.
- Abbrechen mit Ctrl+C ist jederzeit möglich. Derselbe Befehl setzt fort und überspringt fertige Fall/Run-Paare.
- Ein Label gehört zu einer Konfiguration. Wer Modell, Temperatur oder Prompt ändert, braucht ein neues Label (das Skript bricht sonst ab).
- `out/audit_log.jsonl` enthält bereits Mock-Einträge (Labels `mock`, `mock_replay`). Nicht löschen, Auswertungen filtern nach Label.

## 4. Auswertung

```
python src/metrics.py --actions out/agent_actions_pilot_t0.jsonl  --label pilot_t0  --scopes pilot
python src/metrics.py --actions out/agent_actions_pilot_t07.jsonl --label pilot_t07 --scopes pilot
python src/metrics.py --actions out/agent_actions_e6_t0.jsonl     --label e6_t0     --scopes e6_full
python src/metrics.py --actions out/baseline_actions.jsonl        --label baseline_e6 --scopes e6_full   # Vergleich, bereits erzeugt
```

`--scopes all` ist für Agentenläufe nicht sinnvoll: Fälle ohne Ausgabe zählen dort als falsch (M2), der Agent läuft aber nur auf Pilot bzw. E6.

## 5. Was zurück in den Chat gehört

Ein Zip mit:
- `out/audit_log.jsonl`
- `out/agent_actions_<label>.jsonl` und `out/agent_run_<label>.json` aller Läufe
- `out/metrics_<label>.md|json` und `out/errors_<label>.csv`
- Konsolenausgabe von `llm_client.py check` (Version, Digest, Ergebnis) und die Schlusszeilen der Läufe

Für K4 genügen Rauchtest-Ausgabe und `audit_log.jsonl`.

## 6. Störungen

| Symptom | Ursache, Massnahme |
|---|---|
| `Transportfehler ... Connection refused` | Ollama läuft nicht: App starten oder `ollama serve` |
| viele `Parsefehler`, `schema_valid` | Schema nicht erzwungen: `check` wiederholen, ggf. `--endpoint generate` |
| `done_reason: length` im Audit-Log | Ausgabe abgeschnitten (num_predict 1024): melden |
| sehr langsam (> 60 s pro Aufruf) | Modell passt nicht in den GPU-Speicher: kleineres Modell oder andere Programme schliessen |
| `Label ... existiert mit anderer Konfiguration` | neues Label wählen |
