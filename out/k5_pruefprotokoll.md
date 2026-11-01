# K5: Prüfprotokoll Begründungen (Bewertung Claude, regelgeleitet)

Stand 01.11.2026. Entscheid Jan: Die K5-Prüfung ist an Claude delegiert, möglichst neutral.

## Vorgehen

Ein Urteil "nach Gefühl" ist bei Claude nicht neutral (Autor von Prompt, Texten und Labels, Schlüssel bekannt). Deshalb wird jede Begründung in Einzelaussagen zerlegt und jede Aussage gegen das Fallobjekt (`out/audit_log.jsonl`, Feld `case_object`) und den Prompt geprüft. Die Punkte folgen mechanisch aus drei Prüfungen:

| Prüfung | Frage | Werte |
|---|---|---|
| I | Ist die ausschlaggebende Information korrekt genannt? (E2 Überschreitung, E3 Termin und nicht versendet, E6 Inhalt des Freitexts, none kein Trigger und Text ohne Bezug) | ja / nein |
| F | Ist jede Sachaussage durch Fallobjekt oder Text gedeckt? Eine Aussage über den Freitext, die der Text nicht hergibt, zählt als falsch (auch Überzeichnung wie "explizit" bei indirektem Text) | alle gedeckt / Anzahl falsch |
| R | Welche Regel wird für die Aktion angeführt? | Zuordnung / Ermessensrichtlinie / erfunden / keine |

**Punkteregel:** I = nein → 0. I = ja und (F falsch oder R ≠ Zuordnung) → 1. Sonst 2. Fehlender Regelbezug (R = keine) zählt nicht als Abzug, wenn die Aktion aus der Information folgt.

## Protokoll

| Item | Fall | I | Falsche oder ungedeckte Aussagen (F) | R | Punkte |
|---|---|---|---|---|---|
| K5-01 | C0537 E3 | ja: Termin in 1 Tag, nicht versendet | keine | Zuordnung | 2 |
| K5-02 | C0317 E2 | ja: 61'788 vs. 60'000 | "automatische Weiterleitung": A6 braucht Freigabe | Zuordnung | 1 |
| K5-03 | C0028 E6 | ja: Bankauftrag erteilt, Eingang bald | keine | Zuordnung | 2 |
| K5-04 | C0327 E6 | ja: Betrag angewiesen | "abgeschlossener Vorgang": Zahlung nicht eingegangen, A0 ist Wiedervorlage | Zuordnung | 1 |
| K5-05 | C0945 E6 | ja: Zahlung ausgelöst | keine | Zuordnung | 2 |
| K5-06 | C0179 E6 | ja: Zahlungsschwierigkeit | "explizit" (Text ist indirekt); "Zahlungsunfähigkeit aufgrund einer Bankprüfung" (Ursache ist das geplatzte Projekt, die Bankprüfung läuft noch) | Zuordnung | 1 |
| K5-07 | C0797 E6 | ja: Reklamation falsche Ausführung | keine | Ermessensrichtlinie | 1 |
| K5-08 | C0982 E6 | ja: kann nicht zahlen, Teilzahlung | keine | Zuordnung | 2 |
| K5-09 | C0493 E6 | ja: Besuch, kein Bezug | keine ("keine Kündigung" überflüssig, nicht falsch) | Zuordnung | 2 |
| K5-10 | C0955 none | ja: kein Trigger, Personalie | keine (keine Rechnung im Verlauf: gedeckt) | Zuordnung | 2 |
| K5-11 | C0042 E6 | ja: Personalie, kein Bezug | keine | Zuordnung | 2 |
| K5-12 | C0067 E3 | ja: 4 Tage verpasst, nicht versendet | keine | Zuordnung | 2 |
| K5-13 | C0853 E6 | ja: Konto ausgereizt | "bittet um Aufschub": steht nicht im Text | Zuordnung | 1 |
| K5-14 | C0303 none | ja: kein Trigger, Adressänderung | keine (Zahlungseingang im Verlauf: gedeckt) | keine | 2 |
| K5-15 | C0880 E6 | ja: Display ausgefallen | keine | Ermessensrichtlinie | 1 |
| K5-16 | C0695 E6 | ja: Anfrage Datenblätter, kein Bezug | keine | Zuordnung | 2 |
| K5-17 | C0902 E2 | ja: 132'431 vs. 100'000 | "automatische Weiterleitung": A6 braucht Freigabe | Zuordnung | 1 |
| K5-18 | C0298 E6 | ja: falscher Artikel | "Lieferstopp" (Text: Montage steht still) | Regel 3 der Richtlinie als Zuordnung ausgegeben | 1 |
| K5-Z1 | C0776 E6 (Fehler) | nein: Ankündigung als Aufschub gedeutet | "konkrete Zahlungsvereinbarung"; "Bitte um Aufschub" | Zuordnung (falsch angewendet) | 0 |
| K5-Z2 | C0412 none T 0,7 (Fehler) | ja: kein Trigger, Betriebsferien | keine | erfunden: "none → A3" | 1 |

## Ergebnis (18 Items, ohne Zusatzitems)

| Kennzahl | Wert |
|---|---|
| Mittel | **1,56 von 2** |
| Verteilung | 2 Punkte: 10, 1 Punkt: 8, 0 Punkte: 0 |
| I (Information korrekt) | 18/18 |
| F (mindestens eine falsche Aussage) | 6/18 |
| R (Ermessensrichtlinie statt Zuordnung) | 2/18, dazu 1 Mischform (K5-18) |
| nach Typ | E2 1,0 (2), E3 2,0 (2), Happy Path 2,0 (2), E6 1,5 (12) |
| E6 nach Stil | direkt 1,83 (6), indirekt 1,17 (6) |

## Abgleich mit der ersten Bewertung (Urteil)

17 von 18 gleich. Abweichung: K5-06, im Urteil 2, im Protokoll 1. Richtung: Das Urteil war milder, weil die Entscheidung bekannt richtig war und die Überzeichnung den Sinn nicht ändert. Genau diese Verzerrung soll das Protokoll vermeiden. Massgeblich ist das Protokoll.

## Grenzen

- Claude bleibt Autor von Prompt, Texten und Labels. Das Protokoll macht die Bewertung nachprüfbar, nicht unabhängig. Kein menschlicher Rater, keine Übereinstimmungsmessung.
- Die Prüfung F ist streng: Überzeichnungen zählen als falsch. Eine mildere Lesart ergäbe für K5-06 2 Punkte (Mittel 1,61).
- Das Raster unterscheidet nicht zwischen folgenlosem und folgenreichem falschem Regelbezug (K5-07 und K5-Z2 je 1). Für die Schlussabgabe: Treue als eigenes Kriterium.
- 18 Items, pro Gruppe 2 bis 12. Nur Tendenzen.
