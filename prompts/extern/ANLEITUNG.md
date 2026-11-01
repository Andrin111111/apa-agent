# Externe Modelle: Ablauf für Iteration 2 (optional)

In Iteration 1 (01.11.2026) hat Claude 20 Vorlagen überarbeitet und das E6-Labeling simuliert (Claude plus Keyword-Klassifikator).
Iteration 2 macht beides unabhängig. Regel: drei verschiedene Modelle, keines davon Claude und keines aus der Familie des Agentenmodells. Modellname und Datum notieren.

| # | Wer | Was | Ergebnis |
|---|---|---|---|
| 1 | Gruppe | `python src/extern_tasks.py revision-prompt`, dann `prompt_freitext_revision.md` vollständig in einen neuen Chat von **Modell X** einfügen. Markiert sind die 20 Vorlagen, die noch im Original von Claude sind | Antwort als `revision_<modell>.txt` speichern |
| 2 | Gruppe oder Claude | `python src/extern_tasks.py merge-revision --model "<X>" --file revision_<modell>.txt`, danach `generate_log.py`, `validate_log.py`, `extern_tasks.py labeling-prompt` | neue Daten, neuer `prompt_labeling.md` |
| 3 | Gruppe | `prompt_labeling.md` je in einen neuen Chat von **Modell Y** und **Modell Z** einfügen | `labels_<modell>.txt` (2 Dateien) |
| 4 | Gruppe oder Claude | `python src/extern_tasks.py eval-labeling --a labels_y.txt --model-a "<Y>" --b labels_z.txt --model-b "<Z>"` | `out/labeling_report.md` |

Nicht an die Modelle geben: `data/labeling/label_key.csv`, `data/ground_truth.csv`.
Achtung: Nach einer neuen Revision ändern sich die Texte. Pilot- und Labeling-Auswertungen danach neu rechnen.
