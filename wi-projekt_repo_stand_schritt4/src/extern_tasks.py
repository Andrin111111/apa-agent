#!/usr/bin/env python3
"""
extern_tasks.py | WI-Projekt Thema 75 | Schritt 2 (AP2) | v0.2

Aufgaben, die von externen Modellen (nicht Claude, nicht das Agentenmodell) erledigt werden:
Ueberarbeitung der Freitext-Vorlagen und simuliertes Doppellabeling.

Ablauf (aus dem Repo-Root):
  1. python src/extern_tasks.py revision-prompt
       -> prompts/extern/prompt_freitext_revision.md   (an Modell X geben)
  2. Antwort von Modell X als Textdatei speichern, dann:
     python src/extern_tasks.py merge-revision --model "<Modell X>" --file <antwort.txt>
       -> data/freitext_vorlagen.yaml aktualisiert (Original bleibt als original_claude erhalten)
     python src/generate_log.py && python src/validate_log.py
  3. python src/extern_tasks.py labeling-prompt
       -> prompts/extern/prompt_labeling.md   (an Modell Y und Modell Z, je in neuem Chat)
       -> data/labeling/label_key.csv          (Loesung, NICHT an die Modelle geben)
  4. Antworten speichern, dann:
     python src/extern_tasks.py eval-labeling --a <antwort_y.txt> --model-a "<Y>" --b <antwort_z.txt> --model-b "<Z>"
       -> out/labeling_report.md

Rueckgabeformat der Modelle: eine Zeile pro Eintrag, Felder mit "|" getrennt.
Codeblock-Zaeune und Kopfzeilen werden toleriert.
"""

import argparse
import re
import zlib
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT / "data" / "freitext_vorlagen.yaml"
SPEC = ROOT / "spec" / "spec.yaml"
CATS = ["complaint", "payment_announced", "payment_difficulty", "irrelevant"]
def to_revise(t):
    """Zur Revision markiert: noch unveraenderte Original-Vorlagen von Claude."""
    return t.get("source") == "claude" and not t.get("original_claude")
PH_ALL = {"rechnungsnr", "betrag", "lieferdatum", "datum", "datum_zukunft", "auftragsnr"}
PH_IRR = {"datum_zukunft", "auftragsnr"}
KEYWORDS = {                                              # fuer Stilpruefung "indirekt"
    "complaint": ["reklam", "mangel", "maengel", "beanstand", "beschwerde"],
    "payment_announced": ["zahlung", "bezahl", "ueberweis"],
    "payment_difficulty": ["rate", "liquidit", "zahlungsschwier", "aufschub", "engpass"],
}
TRANSLIT = {"\u00e4": "ae", "\u00f6": "oe", "\u00fc": "ue", "\u00c4": "Ae", "\u00d6": "Oe", "\u00dc": "Ue",
            "\u00df": "ss", "\u2014": ",", "\u2013": "-", "\u201e": '"', "\u201c": '"', "\u201d": '"',
            "\u2019": "'", "\u2018": "'", "\u00ab": '"', "\u00bb": '"', "\u2026": "..."}


def rng_for(name):
    seed = int(yaml.safe_load(SPEC.read_text(encoding="utf-8"))["meta"]["seed"])
    return np.random.default_rng(np.random.SeedSequence(entropy=seed, spawn_key=(zlib.crc32(name.encode()),)))


def load_tpl():
    raw = TPL.read_text(encoding="utf-8")
    return raw, yaml.safe_load(raw)["categories"]


def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_tpl(raw, cats):
    header = raw.split("\ncategories:")[0]
    out = [header, "", "categories:"]
    for cat in CATS:
        out.append(f"  {cat}:")
        for t in cats[cat]:
            out.append(f"    - id: {t['id']}")
            out.append(f"      text: {q(t['text'])}")
            out.append(f"      stil: {t['stil']}")
            out.append(f"      source: {q(t['source']) if ' ' in t['source'] else t['source']}")
            if t.get("original_claude"):
                out.append(f"      original_claude: {q(t['original_claude'])}")
            out.append(f"      reviewed_by_jan: {str(t['reviewed_by_jan']).lower()}")
        out.append("")
    TPL.write_text("\n".join(out), encoding="utf-8")


def parse_pipe(path, n_fields):
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("```") or "|" not in line:
            continue
        parts = [p.strip() for p in line.strip("|").split("|", n_fields - 1)]
        if len(parts) < n_fields or parts[0].lower() in ("id", "item_id"):
            continue
        rows.append(parts)
    return rows


def translit(s, warn, ref):
    out = re.sub(r"\s*[\u2014\u2013]\s*", ", ", s)
    for k, v in TRANSLIT.items():
        out = out.replace(k, v)
    if out != s:
        warn.append(f"{ref}: Umlaute/Sonderzeichen in ASCII umgewandelt")
    if not out.isascii():
        warn.append(f"{ref}: enthaelt weiterhin Nicht-ASCII-Zeichen")
    return out


# ---------------------------------------------------------------------------
def cmd_revision_prompt(_):
    _, cats = load_tpl()
    L = [
        "# Auftrag: Freitext-Vorlagen überarbeiten",
        "",
        "Du unterstützt ein Hochschulprojekt (Wirtschaftsinformatik). Wir erzeugen synthetische Kundennachrichten "
        "zu Aufträgen und Rechnungen eines Schweizer B2B-Lieferanten (Order-to-Cash). Ein KI-Agent soll diese "
        "Nachrichten später einer von vier Kategorien zuordnen. Alle Vorlagen stammen bisher von einem einzigen "
        "Sprachmodell. Damit sie nicht alle dieselben Formulierungsmuster tragen, sollst du einen Teil neu schreiben.",
        "",
        "## Kategorien",
        "",
        "| Kategorie | Bedeutung |",
        "|---|---|",
        "| complaint | Kunde meldet Mangel, Schaden, Falsch- oder Fehllieferung oder eine Funktionsstörung |",
        "| payment_announced | Kunde kündigt eine Zahlung an oder bestätigt, dass sie ausgelöst bzw. terminiert ist |",
        "| payment_difficulty | Kunde kann nicht oder nicht fristgerecht zahlen, bittet um Raten oder Aufschub, schildert finanzielle Engpässe |",
        "| irrelevant | Kein Bezug zu Mangel oder Zahlung (z. B. Adresse, Kontakt, Ferien, Produktanfrage, Lob, Organisatorisches) |",
        "",
        "## Aufgabe 1: Neu schreiben",
        "",
        "Schreibe die mit **NEU** markierten Vorlagen neu. Regeln:",
        "",
        "1. Gleiche Kategorie und gleicher Stil wie das Original. Stil `direkt`: Thema mit typischem Schlüsselwort. "
        "Stil `indirekt`: Thema klar erkennbar, aber ohne die typischen Schlüsselwörter der Kategorie "
        "(z. B. kein \"Reklamation\", \"Mangel\", \"Zahlung\", \"Rate\"). Stil `distraktor` (nur irrelevant): "
        "enthält Fachwörter aus dem Auftragsumfeld, hat aber keinen Bezug zu Mangel oder Zahlung.",
        "2. Eindeutig genau eine Kategorie. Keine Mischformen (z. B. keine Reklamation mit Zahlungsankündigung).",
        "3. Deutlich andere Formulierung und Situation als das Original, nicht nur Synonyme austauschen.",
        "4. 1 bis 3 Sätze. Realistischer Geschäftston, Tonalität darf variieren (förmlich, knapp, genervt, freundlich).",
        "5. Schweizer Schreibweise und **ASCII**: ae, oe, ue statt Umlauten, ss statt ß, keine Gedankenstriche, keine typografischen Anführungszeichen.",
        "6. Platzhalter sind erlaubt, aber nicht nötig: {rechnungsnr}, {betrag}, {lieferdatum}, {datum} (kürzlich vergangen), "
        "{datum_zukunft}, {auftragsnr}. Bei `irrelevant` nur {datum_zukunft} und {auftragsnr}. Keine weiteren Platzhalter, keine anderen geschweiften Klammern.",
        "7. Keine echten Firmen, Personen, Telefonnummern oder IBAN.",
        "",
        "## Aufgabe 2: Kritisch prüfen",
        "",
        "Prüfe alle 40 Vorlagen (auch die nicht markierten). Melde jede Vorlage, die mehrdeutig ist, zu einer anderen "
        "Kategorie passen könnte, unnatürlich klingt oder den Stil verfehlt. Wenn nichts auffällt, schreibe `keine`.",
        "",
        "## Ausgabeformat (genau so, ohne weiteren Text)",
        "",
        "```",
        "NEU",
        "id|neuer Text",
        "complaint_02|...",
        "```",
        "",
        "```",
        "BEFUNDE",
        "id|Befund in einem Satz",
        "payment_announced_05|...",
        "```",
        "",
        "## Vorlagen",
        "",
    ]
    for cat in CATS:
        L += [f"### {cat}", "", "| id | Stil | Aktion | Text |", "|---|---|---|---|"]
        for t in cats[cat]:
            act = "**NEU**" if to_revise(t) else "prüfen"
            L.append(f"| {t['id']} | {t['stil']} | {act} | {t['text']} |")
        L.append("")
    out = ROOT / "prompts" / "extern" / "prompt_freitext_revision.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"geschrieben: {out}")


def cmd_merge_revision(a):
    raw, cats = load_tpl()
    text = Path(a.file).read_text(encoding="utf-8")
    neu_part = text.split("BEFUNDE")[0]
    tmp = ROOT / "out" / "_neu.txt"
    tmp.parent.mkdir(exist_ok=True)
    tmp.write_text(neu_part, encoding="utf-8")
    rows = parse_pipe(tmp, 2)
    tmp.unlink()
    by_id = {t["id"]: (cat, t) for cat in CATS for t in cats[cat]}
    target = {i for i, (_, t) in by_id.items() if to_revise(t)}
    errors, warn, done = [], [], set()
    for tid, new in rows:
        if tid not in by_id:
            errors.append(f"{tid}: unbekannte ID")
            continue
        if tid not in target:
            warn.append(f"{tid}: war nicht zur Ueberarbeitung markiert, ignoriert")
            continue
        cat, t = by_id[tid]
        new = translit(new.strip().strip('"'), warn, tid)
        phs = set(re.findall(r"\{(\w+)\}", new))
        allowed = PH_IRR if cat == "irrelevant" else PH_ALL
        if not phs <= allowed:
            errors.append(f"{tid}: unzulaessige Platzhalter {sorted(phs - allowed)}")
        if re.sub(r"\{\w+\}", "", new).count("{") or re.sub(r"\{\w+\}", "", new).count("}"):
            errors.append(f"{tid}: ungueltige geschweifte Klammern")
        n_sent = len(re.findall(r"[.!?](\s|$)", new))
        if not 1 <= n_sent <= 3:
            warn.append(f"{tid}: {n_sent} Saetze (Soll 1 bis 3)")
        if t["stil"] == "indirekt" and cat in KEYWORDS:
            hits = [k for k in KEYWORDS[cat] if k in new.lower()]
            if hits:
                warn.append(f"{tid}: Stil indirekt, enthaelt aber {hits}")
        if new == t["text"]:
            warn.append(f"{tid}: unveraendert")
        if errors and errors[-1].startswith(tid):
            continue
        if not t.get("original_claude"):
            t["original_claude"] = t["text"]
        t["text"] = new
        t["source"] = a.model
        done.add(tid)
    missing = sorted(target - done)
    if missing:
        warn.append(f"nicht ueberarbeitet: {', '.join(missing)}")
    if errors:
        print("ABBRUCH, nichts geschrieben:")
        for e in errors:
            print("  FEHLER", e)
        for w in warn:
            print("  WARNUNG", w)
        raise SystemExit(1)
    write_tpl(raw, cats)
    befunde = parse_pipe_text(text.split("BEFUNDE")[1]) if "BEFUNDE" in text else []
    rep = ["# Revision der Freitext-Vorlagen", "", f"Modell: {a.model}. Ueberarbeitet: {len(done)} von {len(target)}.", "",
           "## Warnungen", ""] + [f"- {w}" for w in warn or ["keine"]] + ["", "## Befunde des Modells zu allen Vorlagen", ""]
    rep += [f"- {i}: {b}" for i, b in befunde] or ["- keine"]
    (ROOT / "out" / "revision_report.md").write_text("\n".join(rep) + "\n", encoding="utf-8")
    print(f"{len(done)} Vorlagen uebernommen, {len(warn)} Warnungen, {len(befunde)} Befunde -> out/revision_report.md")


def parse_pipe_text(s):
    out = []
    for line in s.splitlines():
        line = line.strip()
        if "|" in line and not line.startswith("```"):
            p = [x.strip() for x in line.strip("|").split("|", 1)]
            if len(p) == 2 and p[0].lower() != "id":
                out.append((p[0], p[1]))
    return out


def cmd_labeling_prompt(_):
    _, cats = load_tpl()
    rng = rng_for("labeling_items")
    items = []
    for cat in CATS:
        for t in cats[cat]:
            p = {"rechnungsnr": f"RE-26-{int(rng.integers(10000, 99999))}",
                 "betrag": "CHF " + f"{int(rng.integers(800, 40000)):,}".replace(",", "'") + ".00",
                 "lieferdatum": f"{int(rng.integers(1, 28)):02d}.0{int(rng.integers(3, 9))}.2026",
                 "datum": f"{int(rng.integers(1, 28)):02d}.0{int(rng.integers(3, 9))}.2026",
                 "datum_zukunft": f"{int(rng.integers(1, 28)):02d}.0{int(rng.integers(3, 9))}.2026",
                 "auftragsnr": f"C{int(rng.integers(1, 1000)):04d}"}
            items.append({"template_id": t["id"], "category": cat, "stil": t["stil"],
                          "source": t["source"], "text": t["text"].format_map(p)})
    perm = rng.permutation(len(items))
    items = [items[j] for j in perm]
    for k, it in enumerate(items, 1):
        it["item_id"] = f"L{k:02d}"
    key = pd.DataFrame(items)[["item_id", "template_id", "category", "stil", "source", "text"]]
    kp = ROOT / "data" / "labeling" / "label_key.csv"
    kp.parent.mkdir(parents=True, exist_ok=True)
    key.to_csv(kp, index=False, encoding="utf-8", lineterminator="\n")
    key[["item_id", "text"]].to_csv(kp.parent / "label_items.csv", index=False, encoding="utf-8", lineterminator="\n")
    L = [
        "# Auftrag: Kundennachrichten kategorisieren",
        "",
        "Du bist Sachbearbeiter:in im Debitorenmanagement eines Schweizer B2B-Lieferanten. Unten stehen 40 kurze "
        "Nachrichten von Geschäftskunden, die zu einem Auftrag eingegangen sind. Ordne jede Nachricht genau einer "
        "Kategorie zu. Beurteile jede Nachricht für sich, ohne Annahmen über die Verteilung der Kategorien.",
        "",
        "## Kategorien",
        "",
        "| Label | Wann |",
        "|---|---|",
        "| complaint | Kunde meldet Mangel, Schaden, Falsch- oder Fehllieferung oder eine Funktionsstörung |",
        "| payment_announced | Kunde kündigt eine Zahlung an oder bestätigt, dass sie ausgelöst bzw. terminiert ist |",
        "| payment_difficulty | Kunde kann nicht oder nicht fristgerecht zahlen, bittet um Raten oder Aufschub, schildert finanzielle Engpässe |",
        "| irrelevant | Kein Bezug zu Mangel oder Zahlung (z. B. Adresse, Kontakt, Ferien, Produktanfrage, Lob, Organisatorisches) |",
        "",
        "Wenn du unsicher bist, wähle trotzdem das passendste Label und setze `unsicher` auf `ja`.",
        "",
        "## Ausgabeformat (genau 40 Zeilen, ohne weiteren Text)",
        "",
        "```",
        "item_id|label|unsicher|begruendung",
        "L01|irrelevant|nein|Hinweis auf Adressaenderung",
        "```",
        "",
        "`begruendung`: höchstens 12 Wörter, ohne das Zeichen |.",
        "",
        "## Nachrichten",
        "",
        "```",
    ]
    L += [f"{it['item_id']}|{it['text']}" for it in items]
    L += ["```", ""]
    out = ROOT / "prompts" / "extern" / "prompt_labeling.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"geschrieben: {out} und {kp}")


def kappa(a, b, labels):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(l) / n) * (b.count(l) / n) for l in labels)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def read_labels(path, model):
    rows = parse_pipe(path, 4)
    df = pd.DataFrame(rows, columns=["item_id", "label", "unsicher", "begruendung"])
    df["label"] = df.label.str.strip().str.lower()
    df["unsicher"] = df.unsicher.str.strip().str.lower()
    df = df.drop_duplicates("item_id")
    bad = df[~df.label.isin(CATS)]
    if len(bad):
        print(f"WARNUNG {model}: {len(bad)} ungueltige Labels: {bad.label.unique().tolist()}")
    return df.set_index("item_id")


def cmd_eval_labeling(a):
    key = pd.read_csv(ROOT / "data" / "labeling" / "label_key.csv", dtype=str).set_index("item_id")
    A, B = read_labels(a.a, a.model_a), read_labels(a.b, a.model_b)
    ids = [i for i in key.index if i in A.index and i in B.index]
    miss = len(key) - len(ids)
    k = key.loc[ids]
    la, lb, lt = list(A.loc[ids, "label"]), list(B.loc[ids, "label"]), list(k.category)
    agree = sum(x == y for x, y in zip(la, lb)) / len(ids)
    acc_a = sum(x == y for x, y in zip(la, lt)) / len(ids)
    acc_b = sum(x == y for x, y in zip(lb, lt)) / len(ids)
    both = sum(x == y == z for x, y, z in zip(la, lb, lt))
    R = ["# Simuliertes Doppellabeling (E6-Freitexte)", "",
         f"Modell A: {a.model_a}. Modell B: {a.model_b}. Einheit: 1 gerendertes Beispiel pro Vorlage, "
         f"{len(ids)} von {len(key)} Eintraegen auswertbar" + (f" ({miss} fehlen)." if miss else "."), "",
         "| Kennzahl | Wert |", "|---|---|",
         f"| Uebereinstimmung A vs. B | {agree:.0%} |",
         f"| Cohens Kappa A vs. B | {kappa(la, lb, CATS):.2f} |",
         f"| A vs. Konstruktion (Vorlagen-Kategorie) | {acc_a:.0%} |",
         f"| B vs. Konstruktion | {acc_b:.0%} |",
         f"| A, B und Konstruktion einig | {both} von {len(ids)} |",
         f"| als unsicher markiert (A / B) | {(A.loc[ids, 'unsicher'] == 'ja').sum()} / {(B.loc[ids, 'unsicher'] == 'ja').sum()} |",
         "", "Lesart Kappa: ueber 0.80 sehr gut, 0.60 bis 0.80 gut, darunter pruefen.", "",
         "## Nach Quelle und Stil (Anteil A und B beide korrekt)", "", "| Gruppe | n | beide korrekt |", "|---|---|---|"]
    k = k.assign(a=la, b=lb)
    k["ok"] = (k.a == k.category) & (k.b == k.category)
    for col in ("source", "stil", "category"):
        for g, df in k.groupby(col):
            R.append(f"| {col} = {g} | {len(df)} | {df.ok.mean():.0%} |")
    R += ["", "## Abweichungen (Kandidaten fuer unscharfe Vorlagen)", "",
          "| item | Vorlage | Konstruktion | A | B | Text |", "|---|---|---|---|---|---|"]
    for i, r in k[~k.ok].iterrows():
        R.append(f"| {i} | {r.template_id} | {r.category} | {r.a} | {r.b} | {r.text} |")
    if k.ok.all():
        R.append("| - | - | - | - | - | keine |")
    R += ["", "Entscheid pro Abweichung (Jan): Vorlage schaerfen oder bewusst als schwierigen Fall behalten.", ""]
    out = ROOT / "out" / "labeling_report.md"
    out.write_text("\n".join(R), encoding="utf-8")
    print(f"Uebereinstimmung {agree:.0%}, Kappa {kappa(la, lb, CATS):.2f}, A {acc_a:.0%}, B {acc_b:.0%} -> {out}")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("revision-prompt")
    m = sp.add_parser("merge-revision")
    m.add_argument("--model", required=True)
    m.add_argument("--file", required=True)
    sp.add_parser("labeling-prompt")
    e = sp.add_parser("eval-labeling")
    e.add_argument("--a", required=True)
    e.add_argument("--model-a", required=True)
    e.add_argument("--b", required=True)
    e.add_argument("--model-b", required=True)
    a = ap.parse_args()
    {"revision-prompt": cmd_revision_prompt, "merge-revision": cmd_merge_revision,
     "labeling-prompt": cmd_labeling_prompt, "eval-labeling": cmd_eval_labeling}[a.cmd](a)


if __name__ == "__main__":
    main()
