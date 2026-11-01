# Drehbuch Demo, Folie 6 (4 Minuten)

Stand 01.11.2026, Schritt 6 (K6 bestanden). Alle Befehle aus dem Repo-Root `wi-projekt_repo_stand_schritt4`.
Alle Befehle zum Kopieren stehen in Abschnitt 0. Werkzeug: `src/demo.py` (Wrapper um `src/run_agent.py`, Konfiguration wie in der Evaluation: `qwen3.5:9b-q4_K_M`, Prompt v1.2a, T = 0, Seed 42).

Demo-Fälle (entschieden an K6):

| # | Fall | Typ | Was er zeigt | Agent | Regel (Baseline) |
|---|---|---|---|---|---|
| 1 | C0902 | E2 Kreditlimit | Eskalation mit Freigabe, Ehrlichkeitspunkt Begründung | A6 an Credit Management, Freigabe | gleich |
| 2 | C0537 | E3 Lieferverzögerung | autonome Aktionen, keine Freigabe | A4 + A2, sofort ausgeführt | gleich |
| 3 | C0244 | E6 indirekte Reklamation | Ermessen: Text ohne Schlüsselwort | A5 an Kundendienst, Freigabe | A3 (Mahnung), falsch |
| Reserve | C0776 | E6 Zahlung angekündigt | echter Fehler aus der Evaluation, Freigabe fängt ihn ab | A6 statt A0 | A3, ebenfalls falsch |

Alle vier sind im Evaluationslauf (`pilot_t0` bzw. `e6_t0`) so entschieden worden und live bytegleich reproduziert (16 von 16 Live-Aufrufen in Schritt 6). Keiner ist ein Rauchtestfall (C0317, C0067, C0880 wurden bewusst nicht gewählt).

## 0. Befehle zum Kopieren

In der Terminal-App ausführen, nicht in Claude Code (die Demo braucht Tastatureingaben). Jeden Block einzeln kopieren, einfügen, Enter.
**Wichtig:** In jedem neuen Tab zuerst den `cd`-Befehl ausführen. Sonst kommt `can't open file ... src/demo.py`. Mit `pwd` prüfen: Die Ausgabe muss auf `wi-projekt_repo_stand_schritt4` enden.

### Tab 1: Ruhezustand verhindern (offen lassen bis zum Schluss, keine Ausgabe)

```
caffeinate -dis
```

Neuer Tab: Cmd+T.

### Tab 2: Vorabprüfung und Demo

```
cd /Users/jansamueltkac/00_WI_Bachelor/wi-projekt/apa-agent/wi-projekt_repo_stand_schritt4
```

Vorabprüfung (ca. 10 s, letzte Zeile muss `BEREIT` sein):

```
~/.venvs/apa-agent/bin/python src/demo.py --check
```

Demo live starten (wartet auf Enter, ruft das LLM erst dann auf):

```
~/.venvs/apa-agent/bin/python src/demo.py --client ollama --approver Jan --baseline --truth --clear
```

Neuer Tab: Cmd+T.

### Tab 3: Fallback ohne LLM (nur eintippen, erst im Notfall Enter)

```
cd /Users/jansamueltkac/00_WI_Bachelor/wi-projekt/apa-agent/wi-projekt_repo_stand_schritt4
```

```
~/.venvs/apa-agent/bin/python src/demo.py --client replay --approver Jan --baseline --truth --clear
```

Fallback ab einem bestimmten Fall (z. B. wenn Fall 1 schon gezeigt war):

```
~/.venvs/apa-agent/bin/python src/demo.py --client replay --cases C0537,C0244 --approver Jan --baseline --truth --clear
```

### Tasten während der Demo (live und Replay gleich)

| Unten im Terminal steht | Du tippst |
|---|---|
| `[Enter] Fall 1/3: C0902` | Enter |
| (ca. 7 s) `A6 an Credit Management freigeben? [j/n/Enter=offen]` | `j` und Enter |
| `[Enter] Fall 2/3: C0537` | Enter |
| (ca. 7 s, keine Freigabefrage) `[Enter] Fall 3/3: C0244` | Enter |
| (ca. 7 s) `A5 an Kundendienst freigeben? [j/n/Enter=offen]` | `j` und Enter |
| `ZUSAMMENFASSUNG` | fertig, nichts mehr tippen |

Hängt "lokales LLM entscheidet" länger als 15 s: Ctrl+C, dann in Tab 3 Enter.

### Reserve: echter Fehler C0776 (nur bei Fragen oder Zeitreserve)

Live (in Tab 2, nach der Demo):

```
~/.venvs/apa-agent/bin/python src/demo.py --client ollama --cases C0776 --approver Jan --baseline --truth --clear
```

Fallback ohne LLM:

```
~/.venvs/apa-agent/bin/python src/demo.py --client replay --cases C0776 --replay-label demo_reserve_c0776 --approver Jan --baseline --truth --clear
```

| Unten im Terminal steht | Du tippst |
|---|---|
| `[Enter] Fall 1/1: C0776` | Enter |
| `A6 an Credit Management freigeben? [j/n/Enter=offen]` | `n` und Enter |
| `Grund (optional):` | `Zahlung angekuendigt` und Enter |

### Nach der Demo: einen Lauf nachlesen (optional)

Das Label steht in der Zusammenfassung (z. B. `demo_live_20261101T190550`):

```
~/.venvs/apa-agent/bin/python src/audit_view.py --audit out/demo/audit_log_demo.jsonl --label demo_live_20261101T190550
```

## 1. Vorbereitung

| Wann | Was | Befehl / Handgriff |
|---|---|---|
| am Vortag | Probelauf (K6), Bildschirmaufzeichnung als Fallback 3 (Abschnitt 5) | |
| T minus 30 min | Netzteil anschliessen. Fokus "Nicht stören" einschalten. Andere grosse Programme schliessen. Ollama-App nicht beenden oder aktualisieren | |
| T minus 30 min | Terminal: Profil mit hohem Kontrast, Schrift SF Mono 20 pt (Probe an K6), Fenster mindestens 80 Spalten × 42 Zeilen, Vollbild auf dem Beamer | Terminal > Einstellungen > Profile > Text |
| T minus 30 min | Tab 1: Ruhezustand verhindern, bis zum Ende offen lassen | `caffeinate -dis` |
| T minus 15 min | Tab 2: Vorabprüfung und Aufwärmen (ca. 10 s). Erwartung: letzte Zeile `BEREIT`, Modell bleibt 90 min geladen | `~/.venvs/apa-agent/bin/python src/demo.py --check` |
| T minus 5 min | Tab 2: Demo starten. Sie wartet auf Enter und ruft das LLM erst dann auf | `~/.venvs/apa-agent/bin/python src/demo.py --client ollama --approver Jan --baseline --truth --clear` |
| T minus 5 min | Tab 3: Fallback eintippen, nicht starten | `~/.venvs/apa-agent/bin/python src/demo.py --client replay --approver Jan --baseline --truth --clear` |
| T minus 5 min | Tab 2 sichtbar lassen, zurück zu den Folien | |

`--check` meldet `FEHLT` bei: Ollama nicht erreichbar, anderes Modell oder anderer Digest, Prompt oder Schema geändert, Fallobjekt geändert, Modell nicht vollständig im GPU-Speicher, Aufzeichnung fehlt. Bei `FEHLT` im LLM-Teil direkt mit Tab 3 (Replay) präsentieren.

## 2. Ablauf

| Zeit | Bildschirm | Handlung | Sprechtext (Stichworte) |
|---|---|---|---|
| 0:00 bis 0:20 | Kopf: Modus LIVE, Modell, Prompt v1.2a, T=0, Seed 42, "Konfiguration wie Evaluation", Pipeline-Zeile | Cmd+Tab ins Terminal | Echte Pipeline von Folie 5, lokal und offline. Gleiche Konfiguration wie in der Auswertung. Drei Fälle: E2, E3, E6. |
| 0:20 bis 1:15 | Fall 1 C0902: FALL-Block (Limit CHF 100'000, Engagement CHF 132'431, +32,4 %, Zahlungshistorie schlecht) | Enter, ca. 7 s warten | Die Ausnahme erkennt die Regel, nicht das LLM. Das Modell bekommt nur dieses Fallobjekt, den Katalog und die Zuordnung. |
| | AGENT: A6 an Credit Management `[Freigabe noetig]`, Begründung, REGEL gleich, SOLL korrekt, GUARDRAILS bestanden | zeigen auf "automatische Weiterleitung" | **Grenze:** Die Begründung sagt "automatische Weiterleitung". Das stimmt nicht: A6 braucht eine Freigabe, das System hält an. Die Begründung ist Text des Modells und nicht geprüft. Sie nennt die richtige Information (Bewertung 1,56 von 2), ist aber keine verlässliche Erklärung. Kontrolle leistet die Freigabe. |
| | FREIGABE: `A6 an Credit Management freigeben? [j/n/Enter=offen]` | `j` Enter | Freigabe mit Name und Zeit im Audit-Log. |
| | ERGEBNIS executed (simuliert), REPRO bytegleich mit `pilot_t0` | Enter | Gleiche Ausgabe Zeichen für Zeichen wie im Evaluationslauf: T = 0 ist auf diesem Rechner reproduzierbar. |
| 1:15 bis 1:50 | Fall 2 C0537: Liefertermin morgen, nicht versendet, Kommissionieren. AGENT: A4 + A2 `[autonom]`, FREIGABE nicht nötig, ERGEBNIS executed | Enter, warten, Enter | Priorisieren und Kunde informieren sind autonom, laufen sofort und sind nachträglich sichtbar. Die Regel macht dasselbe: bei deterministischen Fällen kein Mehrwert, das war erwartet. |
| 1:50 bis 3:10 | Fall 3 C0244: 39 Tage überfällig, Zahlungshistorie schlecht, Freitext "12 von 40 Kartons durchnässt" | Enter, ca. 7 s warten | Klassisch wäre jetzt die Mahnung. Im Text steht kein Wort wie "Reklamation". |
| | REGEL: A3 Mahnung, "ANDERS als Agent", Keyword-Regel: "irrelevant". AGENT: A5 an Kundendienst. SOLL A5: Agent korrekt, Regel falsch | | Die Keyword-Regel findet kein Schlüsselwort und mahnt. Der Agent erkennt den Mangel: Reklamation vor Mahnung, Fall an den Kundendienst. **Einschränkung:** Texte, Kategoriedefinitionen und Labels stammen vom selben Autor, das Ergebnis ist eine Obergrenze (Folie 7). Guardrails prüfen nur die Form, nicht ob die Aktion fachlich stimmt. |
| | FREIGABE A5 | `j` Enter | |
| 3:10 bis 3:40 | ZUSAMMENFASSUNG: 3 Fälle, Aktionen, Freigabe, Disposition, Pfad Audit-Log | | Jede Entscheidung steht im Audit-Log: Input, Rohausgabe, Guardrails, Freigabe mit Name und Zeit. Das LLM wählt nur aus dem Katalog, Erkennung, Freigabe und Protokoll sind deterministisch. |
| 3:40 bis 4:00 | | zurück zu den Folien | Drei ausgewählte Fälle sind Illustration, kein Beleg. E2 und E3 sind durch die Zuordnung vorgegeben. Wie gut das über alle 80 E6-Fälle trägt und wo der Agent falsch liegt: Folie 7. |

Hinweise zum Sprechen:
- Nicht sagen "der Agent erkennt die Ausnahme" (die Regel erkennt) und nicht "die Aktion wird ausgeführt" ohne "simuliert".
- "Bytegleich" heisst reproduzierbar, nicht korrekt.
- Bei E3 optional (wenn gefragt): Bei T = 0 wählt das Modell bei E3 immer beide Aktionen, unabhängig von der Lage.
- Wird live versehentlich `n` oder Enter getippt: nicht korrigieren, sondern zeigen (abgelehnt bzw. offen, nichts ausgeführt). Das ist ebenfalls korrektes Verhalten.

## 3. Reserve: echter Fehler (C0776), ca. 45 s

Für Fragen wie "Was passiert, wenn das Modell falsch liegt?" oder wenn der Probelauf deutlich unter 3:30 bleibt. Der Fehler ist nicht inszeniert: Es ist der einzige Agentenfehler im E6-Zusatzlauf, bei T = 0 bytegleich reproduziert.

```
~/.venvs/apa-agent/bin/python src/demo.py --client ollama --cases C0776 --approver Jan --baseline --truth --clear
```

| Bildschirm | Handlung | Sprechtext |
|---|---|---|
| Freitext: Systemumstellung, Betrag im nächsten Lauf am 23.03. | Enter | Der Kunde kündigt die Zahlung an. Richtig wäre A0 (abwarten). |
| AGENT: A6 an Credit Management. Begründung: "konkrete Zahlungsvereinbarung". SOLL A0: Agent falsch, Regel falsch. GUARDRAILS bestanden | | Das Modell deutet die Ankündigung als Bitte um Aufschub und erfindet eine Vereinbarung. Die Guardrails lassen es durch, weil die Ausgabe formal korrekt ist. |
| FREIGABE A6 | `n`, Grund "Zahlung angekündigt", Enter | Hier greift die Freigabe: Der Mensch lehnt ab, nichts wird ausgeführt. Bei einer autonomen Aktion (A0 bis A4) gäbe es diese Kontrolle nicht. |

Fallback ohne LLM: `~/.venvs/apa-agent/bin/python src/demo.py --client replay --cases C0776 --replay-label demo_reserve_c0776 --approver Jan --baseline --truth --clear`.

## 4. Notfallplan

| Symptom | Massnahme | Ansage |
|---|---|---|
| "... lokales LLM entscheidet" steht länger als 15 s | Ctrl+C. Tab 3 (Replay) starten, bei Bedarf ab dem offenen Fall: `--cases C0537,C0244` | "Ich zeige die Aufzeichnung desselben Laufs. Bei T = 0 ist sie Zeichen für Zeichen identisch." |
| `Kein Ergebnis: ... Connection refused` | Ollama läuft nicht. Nicht neu starten (dauert), sofort Tab 3 | wie oben |
| `Kein Ergebnis: ... timed out` (nach 30 s) | Tab 3 | wie oben |
| REPRO meldet "weicht ab" | Weiterzeigen. Ursache meist neue Ollama-Version (`--check` zeigt sie) | "Andere Laufzeitumgebung, andere Ausgabe: Reproduzierbarkeit gilt nur für diese Umgebung." |
| Laptop oder Beamer-Anschluss fällt aus | Aufzeichnung (Abschnitt 5) auf einem anderen Gerät abspielen, sonst Screenshots auf der Folie | "Aufzeichnung vom Probelauf." |
| Schrift zu klein, Zeilen brechen um | Cmd+Plus bzw. Cmd+Minus. Fenster breiter als 80 Spalten | |
| Fallblock passt nicht auf den Bildschirm | Cmd+Minus, oder ohne `--truth` starten (eine Zeile weniger) | |
| Bildschirm wird dunkel | `caffeinate -dis` läuft nicht: neu starten, Netzteil prüfen | |
| Tippfehler im Befehl | Befehle sind vorab in Tab 2 und 3. Sonst Pfeil hoch (Shell-Historie) | |
| Modell kalt (erster Aufruf über 10 s) | `--check` ist länger als 90 min her: abwarten, beim nächsten Mal näher am Termin prüfen | |

Rangfolge der Fallbacks: 1 live, 2 Replay (gleicher Rechner, kein LLM, Start unter 1 s), 3 Bildschirmaufzeichnung, 4 Screenshots auf der Folie (Schritt 7). Ein Replay oder Video wird immer als Aufzeichnung angesagt. Der Kopf des Replays zeigt "Modus AUFZEICHNUNG".

## 5. Bildschirmaufzeichnung (Jan)

1. Terminal wie für den Vortrag einrichten (Schrift, Fenstergrösse, Vollbild). `~/.venvs/apa-agent/bin/python src/demo.py --check` ausführen.
2. Cmd+Shift+5, "Ausgewählten Bereich aufnehmen" (Terminal-Fenster). Unter "Optionen": Speicherort Schreibtisch, Mikrofon "Keines" (ohne Ton kann man live darüber sprechen), Timer 5 s. "Aufnehmen". Alternativ QuickTime Player > Ablage > Neue Bildschirmaufnahme (gleicher Dialog).
3. Im Terminal: `~/.venvs/apa-agent/bin/python src/demo.py --client ollama --approver Jan --baseline --truth --clear`. Zügig durchklicken: Enter, `j`, Enter, Enter, Enter, `j`, Enter. Ein Lauf dauert so etwa 1 min.
4. Stoppen: Stopp-Symbol in der Menüleiste oder Cmd+Ctrl+Esc.
5. Datei umbenennen in `demo_folie6_live_<TT-MM>.mov`, auf dem Präsentationsrechner und einem zweiten Gerät (USB-Stick oder Cloud) ablegen und einmal abspielen. Nicht ins Git (Grösse), Einbindung in die Folien in Schritt 7.
6. Optional ein zweites Video mit dem Reservefall C0776.

Textfassung der Bildschirmausgabe für Screenshots oder Folien: `out/demo/console_demo_live.txt` (Live-Lauf vom 01.11.2026, ohne Farben), Reservefall `out/demo/console_demo_reserve_c0776.txt`.

## 6. Dateien

| Datei | Inhalt |
|---|---|
| `src/demo.py` | Demo-Werkzeug (`--check`, `--client ollama/replay`, `--baseline`, `--truth`, `--clear`, `--verbose`, `--cases`) |
| `out/demo/audit_log_demo.jsonl` | Audit-Log der Demo, wird angehängt. `out/audit_log.jsonl` der Auswertung bleibt unverändert |
| `out/demo/agent_actions_demo_ref.jsonl` | Aufzeichnung `demo_ref` (Quelle des Replays), live erstellt am 01.11.2026 |
| `out/demo/agent_actions_demo_reserve_c0776.jsonl` | Aufzeichnung des Reservefalls |
| `out/demo/console_*.txt` | Textfassungen von `--check`, Live-Lauf, Reservefall |

Nachlesen eines Demo-Laufs: `~/.venvs/apa-agent/bin/python src/audit_view.py --audit out/demo/audit_log_demo.jsonl --label <label>` (Label steht in der Zusammenfassung).
