# Prompt: Schritt 7, Folien prüfen und Sprechtext (WI-Projekt Thema 75)

Du arbeitest als ausführender Agent im WI-Projekt "Agentic Process Automation" (ZHAW, Thema 75). Deine Aufgabe: die vorhandenen Folien gegen den aktuellen Projektstand prüfen und einen Sprechtext für 20 Minuten schreiben. Danach stoppst du bei K7 und wartest auf mich (Jan).

## 1. Umgebung

- Repo: `/Users/jansamueltkac/00_WI_Bachelor/wi-projekt/apa-agent`, Branch `main`. Keinen neuen Branch anlegen.
- Folien: `slides/WI-Projekt_Thema75_Zwischenpraesentation.pptx` (provisorisch, von einem Kollegen). Nicht verändern.
- Python für Projektbefehle: `~/.venvs/apa-agent/bin/python`.

## 2. Grundlage

- `docs/WI-Projekt_Zwischenpraesentation_Kontext_und_Plan.md` (v0.7.1), vor allem Abschnitte 10 (Ergebnisse), 11 (Folienplan), 16 (Risiken).
- `out/step5_report.md` (Ergebnisse, Abschnitt 9: Formulierung der Ergebnisfolie nach D-K5-5), `out/step6_report.md`, `docs/demo_drehbuch.md` (Demo, 4 min).
- Bei Bedarf weitere Berichte in `out/` und der Code in `src/`.

## 3. Auftrag

**1. Folien prüfen: `out/step7_folienpruefung.md`**

Pro Folie: was falsch oder veraltet ist und der korrigierte Text. Jede Zahl gegen das Repo prüfen. Belege nur als Verweis auf unsere Dateien (z. B. `out/step5_report.md` Abschnitt 4, `src/demo.py`). Literaturquellen auf den Folien nicht prüfen.

Bekannte Punkte (selbst nachprüfen, nicht abschliessend):
- Folie 5 und 13: Status veraltet (K4/K5 offen, Spezifikation v0.4, 37 Tests). Stand: K1 bis K6 erledigt, `spec.yaml` v0.5.0, 44 Tests.
- Modell heisst überall `qwen3.5:9b-q4_K_M`, nicht `qwen3.5:9b`.
- Folie 11 (Demo): Fälle C0902, C0537, C0244 statt C0317/C0067, Werkzeug `src/demo.py`, Notizen nach `docs/demo_drehbuch.md`.
- Es fehlt eine Folie mit den Ergebnissen von Schritt 5 (nach D-K5-5).
- Folie 12: Grenzen an die Ergebnisse von Schritt 5 anpassen.
- Backup-Folien 19 bis 21: Stand Schritt 4 (Prompt v1.0, Mock-Beispiel).
- Sprecher: Agenda und Notizen widersprechen sich, teils "[Person 3]". Die Verteilung ist provisorisch. Mach einen einfachen Vorschlag mit ungefähr gleicher Redezeit für Jan, Andrin und Minh Sang. Die Demo macht Jan (geprobt, Modell auf seinem MacBook).

**2. Sprechtext: `docs/sprechtext_zwischenpraesentation.md`**

- Gesamtdauer 20:00 inklusive Demo. Rechne mit mindestens 130 Wörtern pro Minute.
- Pro Folie: Sprecher, Startzeit, Dauer, Wortzahl, ausformulierter Sprechtext (kurze, gesprochene Sätze), Überleitung.
- Der Text folgt den korrigierten Folien aus Teil 1. Für die Demo `docs/demo_drehbuch.md` ausformulieren.
- Am Schluss: Zeittabelle (Summe 20:00, Minuten pro Person) und 3 bis 4 Kürzungen von je etwa 30 s, falls die Zeit nicht reicht.

## 4. Vorgaben

- Nichts erfinden. Unbelegtes als "[TODO]" markieren.
- Ehrlich bleiben: Pilot 100 % ist kein Befund. E6 nur mit Einschränkung (Mehrwert nur bei indirekten Texten, Obergrenze wegen gleichem Autor). Demo-Fälle sind Illustration.
- Code, `spec.yaml`, Prompt und Kontextdokument nicht ändern. Nötige Nachführungen nur auflisten.
- Deutsch, Schweizer Schreibweise (ss), keine Gedankenstriche, knapp.
- Commit und Push nur auf meine Anweisung, ohne Co-Author- oder "Generated with Claude Code"-Zeilen.

## 5. Abschluss (K7)

Kurzer Bericht im Chat (höchstens eine halbe Seite): wichtigste Korrekturen, Sprecherverteilung mit Minuten pro Person, was ich entscheiden muss. Dann stoppen.
