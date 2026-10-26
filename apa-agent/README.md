# Agent-Gerüst: Agentic Process Automation

WI-Projekt HS 2026, Thema 75: KI-gestützte Erkennung und Bearbeitung von Ausnahmefällen in Geschäftsprozessen.

Der Agent bekommt eine **Ausnahmemeldung** zu einem Fall und holt sich über Tools Fallverlauf, Kontext und Prozesswissen. Dann wählt er **genau eine Massnahme** aus dem Handlungskatalog und begründet sie. Jede Entscheidung wird protokolliert und automatisch mit der erwarteten Massnahme verglichen.

> Die Daten im Ordner `daten/` sind **Testdaten**: 8 Fälle, angelehnt an das Procure-to-Pay-Beispiel aus Apromore. Später ersetzt ihr sie durch eure echten Ergebnisse.

## Schnellstart (Windows, VS Code)

Voraussetzung ist Python 3.10 oder neuer. Im VS-Code-Terminal (PowerShell) im Projektordner:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

`python main.py` läuft im **Regel-Modus** und braucht keinen API-Key. So seht ihr sofort, ob alles funktioniert.

- Wird `python` nicht gefunden, nehmt `py`.
- Blockiert PowerShell das `Activate.ps1`, einmal `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` ausführen.

**Mit Claude:** `.env.example` nach `.env` kopieren und euren API-Key aus der Claude Console eintragen. Dann:

```powershell
python main.py --modus claude                  # alle Testfälle
python main.py --modus claude --fall P2P-1007  # nur ein Fall
python evaluieren.py                           # letzten Lauf nochmals auswerten
```

## Ablauf

```
Erkennung (PM4Py)          Agent-Schleife (agent.py)                     Ergebnis
-----------------          -------------------------                     --------
daten/ausnahmen.json  -->  1. Meldung lesen                          -->  Massnahme (simuliert
                           2. Info-Tools: Fallverlauf, Fallkontext,        oder zur Freigabe)
                              Prozesswissen                          -->  protokolle/*.jsonl
                           3. genau eine Aktion wählen + begründen   -->  Auswertung (*.md)
                           Die Leitplanken prüfen jeden Aufruf.
```

## Dateien

| Datei | Inhalt | Wer liefert das später? |
|---|---|---|
| `daten/prozesswissen.json` | Soll-Ablauf, SLA, typische Dauern, Rollen, Geschäftsregeln | Analyse (Apromore) |
| `daten/ausnahmen.json` | Ausnahmemeldungen: die **Schnittstelle** zwischen Erkennung und Agent | Erkennung (PM4Py) |
| `daten/event_log.csv` | Event Log mit `case_id, activity, timestamp, resource, role` | echtes oder synthetisches Log |
| `daten/fallkontext.json` | Stammdaten pro Fall (Bestellwert, Lieferant, Rahmenvertrag usw.) | synthetische Daten |
| `daten/erwartete_massnahmen.json` | richtige Massnahme pro Testfall (Ground Truth) | Testszenarien |
| `config.py` | Modell, Leitplanken, **Handlungsspielraum** | Agent |
| `tools.py` | Info- und Aktions-Tools, Prüfung der Leitplanken | Agent |
| `llm.py` | Claude (echtes LLM) und Regel-Baseline (ohne KI) | Agent |
| `agent.py` | Agent-Schleife und Systemprompt | Agent |
| `protokoll.py`, `evaluieren.py` | Entscheidungsprotokoll und Auswertung | Agent |

## Schnittstelle: Ausnahmemeldung

So liefert die Erkennung ihre Meldungen, als Liste in `daten/ausnahmen.json`:

```json
{
  "meldung_id": "M-001",
  "case_id": "P2P-1001",
  "ausnahme_typ": "VERZOEGERUNG",
  "erkennungsregel": "Durchlaufzeit über SLA (28 Tage)",
  "beschreibung": "Fall seit 32 Tagen offen (SLA: 28 Tage). ...",
  "kennzahlen": {"tage_offen": 32.0, "sla_tage": 28},
  "erkannt_am": "2026-10-26T07:00:00"
}
```

- `ausnahme_typ` ist `VERZOEGERUNG`, `FEHLENDE_INFO`, `REWORK` oder `ABWEICHUNG`. Neue Typen ergänzt ihr in `config.py` unter `ERLAUBTE_MASSNAHMEN`.
- `kennzahlen` ist frei: alles, was die Erkennung berechnet hat. Der Agent sieht die ganze Meldung.

## Leitplanken

- **Handlungsspielraum:** Pro Ausnahmetyp sind nur bestimmte Massnahmen erlaubt (`ERLAUBTE_MASSNAHMEN` in `config.py`). Andere lehnt `tools.py` ab, und der Agent muss eine Alternative wählen.
- **Genau eine Massnahme pro Fall**, und nur im Fall aus der Meldung.
- **Begründung und ausschlaggebende Fakten** sind Pflichtfelder jeder Massnahme.
- **Human in the Loop:** Eskalationen werden nicht ausgeführt, sondern zur Freigabe vorgelegt (`FREIGABEPFLICHTIG`).
- **Feste Werte** für Rollen, Empfänger und Prioritäten, damit der Agent nichts erfindet.
- **Höchstens 6 Modell-Antworten pro Fall**, danach Abbruch.

## Zwei Modi als eingebauter Vergleich

`--modus regel` wählt pro Ausnahmetyp stur dieselbe Massnahme. Das entspricht den «starren Regeln» aus der Problemstellung. Mit den Testdaten trifft die Regel-Baseline 4 von 8 Fällen. Die anderen vier lassen sich nur mit Kontext richtig lösen, etwa ein Rahmenvertrag mit vereinbarter Lieferfrist (Fehlalarm) oder eine Erinnerung, die schon gesendet wurde. Der Vergleich Regel vs. Claude ist direkt ein Evaluationsergebnis für den Bericht.

## Protokoll und Auswertung

Jeder Lauf schreibt zwei Dateien in `protokolle/`:

- `lauf_<zeit>_<modus>.jsonl`: ein Fall pro Zeile mit allen Schritten (Tool-Aufrufe, Ergebnisse, Zusammenfassung des Denkprozesses, Begründung, Tokens)
- `lauf_<zeit>_<modus>.md`: lesbarer Bericht, z. B. für den Anhang oder die Präsentation

Gemessen werden **Korrektheit** (richtige Massnahme, wo vorgegeben inkl. Rolle oder Aktivität), **Nachvollziehbarkeit** (Begründung und Fakten vorhanden), **abgelehnte Aufrufe** (wie oft die Leitplanken eingreifen mussten) und **Aufwand** (Modell-Antworten, Tokens, Kosten).

## Kosten

Standardmodell ist `claude-sonnet-5-5` (2 USD pro Mio. Input-Tokens, 10 USD pro Mio. Output-Tokens). Günstiger ist `APA_MODELL=claude-haiku-5-5` in der `.env`. Nach jedem Lauf zeigt die Auswertung den Verbrauch.

## Nächste Schritte

1. `prozesswissen.json` mit den Ergebnissen der Apromore-Analyse füllen.
2. `ausnahmen.json` aus der PM4Py-Erkennung erzeugen (Format oben).
3. Mehr und schwierigere Testszenarien mit Ground Truth erstellen, vor allem Fälle, in denen mehrere Regeln zutreffen.
4. Varianten vergleichen: Regel-Baseline vs. Claude, verschiedene Modelle, Prompt mit und ohne Geschäftsregeln.
5. Aktionen später an echte Systeme anbinden (`Werkzeugkasten._aktion` in `tools.py`).
