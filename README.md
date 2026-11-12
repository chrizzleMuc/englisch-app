# Learnino

Eine Englisch-Lern-App für Grundschulkinder: Hören und Sprechen mit Bildern und britischer Aussprache, ganz ohne Werbung, Konten oder Datenweitergabe. Sie läuft im Browser, lässt sich auf Android-Tablets und -Handys als App installieren und funktioniert danach offline.

## Aufbau

Fach → Stufe → Einheit → 5 Lektionen (Neue Wörter, Wörter üben, Sätze, Geschichte, Abschluss).
Jede Sitzung beginnt mit bis zu 5 fälligen Wiederholungen aus der Lernkartei (5 Kästen: 1, 2, 4, 7, 14 Tage).

## Inhalte ändern oder ergänzen

Alle Inhalte stehen im Ordner `inhalte/`:

- `inhalte/uebersicht.json` listet Fächer, Stufen und die Dateien der Einheiten.
- `inhalte/englisch/s1-....json` ist je eine Einheit mit Wörtern, Sätzen, Geschichte, Fragen und Reim.

Neue Einheit: eine vorhandene Datei kopieren, Inhalte und IDs ändern, Dateinamen in `uebersicht.json` eintragen. Fehler in den Dateien zeigt die App im Elternbereich an.

## Echte Aufnahmen

Für jede ID kann eine Aufnahme `audio/en/<ID>.mp3` abgelegt werden, z. B. `audio/en/s1-animals-horse.mp3`. Gibt es keine, spricht die Stimme des Geräts.

Damit die Stimme offline britisch spricht: Android-Einstellungen, Suche nach „Sprachausgabe“, bei Google-Sprachausgabe „Englisch (Vereinigtes Königreich)“ installieren.

## Nach Änderungen am Code

In `sw.js` die Zahl bei `VERSION` und in `js/app.js` `APP_VERSION` erhöhen, damit installierte Apps das Update laden.

## Lokal ansehen

```
python3 -m http.server 8000
```
Dann im Browser `http://localhost:8000` öffnen.

## Schulfächer (seit Version 8)

Schul-Einheiten liegen in `inhalte/<fach>/` und haben `"type": "schule"`. Jede Einheit hat Lektionen mit Aufgaben:

- `pairs` – Paare verbinden (z. B. wir singen – wir sangen)
- `type` – Antwort eintippen, optional vorher wählen (`choose`, z. B. hat/ist)
- `choice` – auswählen, auch „Stimmt das?“ mit `explain`
- `sort` – Wörter in Gruppen sortieren (z. B. Wortfamilien)
- `syllables` – Wort in Silben trennen (`answer` mit Bindestrichen)
- `photo` – im Heft schreiben, Foto als Nachweis (Fotomappe im Elternbereich)

Lektionen mit `"test": true` ziehen zufällige Aufgaben der ganzen Einheit, `"pick": "<id-anfang>"` übt eine Auswahl. Falsche Antworten kommen am Ende der Lektion nochmal und landen in der Lernkartei. Eine Stufe mit `"kinder": ["pirat"]` ist nur für diese Kinder voreingestellt, im Elternbereich änderbar.

## Version 23
- Bilder in Aufgaben deutlich größer (Fragebild und Bild-Antworten).
- Schlecht erkennbare Bilder entfernt: Esel, Leopard, Teddy (beim Klatschen jetzt „Bär“ mit einer Silbe). Wo sie nur falsche Antwort waren, ersetzt durch eindeutige Bilder.

## Version 22
- Online-Abgleich holt bei offener App jede Minute den Stand der anderen Geräte und zeigt ihn auf Start- und Fachseite gleich an.

## Version 19
- **Online-Speicherung** (Supabase, optional): Nach einmaliger Anmeldung per E-Mail gleicht sich der Lernstand automatisch zwischen Tablet und Handy ab. Ohne Internet läuft alles lokal weiter. Beide Geräte werden zusammengeführt statt überschrieben (pro Aufgabe gewinnt die zuletzt geübte). Fotos bleiben auf dem Gerät. Einrichtung: `docs/supabase.sql` im Supabase-SQL-Editor ausführen, dann Projekt-URL und Publishable-Key in `js/cloud-config.js` eintragen.
- Offline-Speicher (Service Worker) repariert: `sw.js` war seit Version 16 versehentlich leer, die App lief dadurch ohne Internet nicht mehr.

## Version 18
- Elternbereich übersichtlicher: Alle Abschnitte sind zugeklappt und lassen sich einzeln aufklappen, „Freigeschaltet“ nach Kind und Fach, „Lernstand“ nach Fach und Stufe. Offene Abschnitte bleiben offen, solange die App läuft.
- Häkchen-Beschriftungen im Elternbereich wieder lesbar (waren weiß auf hellem Grund).

## Version 17
- **Namen** im Elternbereich eintragen: Die Startseite zeigt den Namen groß und die Klasse klein darunter. Die Namen stehen nur auf dem Gerät und in der Sicherungsdatei, nicht im Programmcode.

## Version 16
- Fehler behoben: Im Eltern-Code-Feld erschienen auf dem Handy keine Ziffern.
- Zurück-Knopf oben links größer und gelb mit „Zurück“.

## Version 15
- **Eltern-Code** statt Rechenaufgabe: Beim ersten Öffnen des Elternbereichs legt man auf jedem Gerät einen Code (4–8 Ziffern) fest. Nach 3 Fehlversuchen eine Minute Sperre. Der Code liegt nur als Prüfsumme auf dem Gerät, ist nicht in der Sicherungsdatei und bleibt beim Zurücksetzen erhalten. Ändern im Elternbereich.

## Version 14
- **Aufgaben vorlesen** pro Kind (Elternbereich): „Vorlesen“ (Aufgabe wird automatisch vorgelesen, Standard für die 1. Klasse), „Erst selbst lesen“ (🔊 geht erst nach ein paar Sekunden, am Ende steht, wie viele Aufgaben das Kind allein gelesen hat) oder „Aus“ (Standard 3. Klasse). Englische Wörter werden immer vorgesprochen.
- **Leserichtung** (Deutsch 1. Klasse, neu): gleiche Silbe finden (am/ma), fehlende Silbe ergänzen, am/ma und im/mi im Satz, Wörter richtig herum lesen.
- Neu aus den Heft-Anweisungen: „Was passt nicht?“ (Anfangsbuchstaben), Silben lesen und „Welcher Satz passt zum Bild?“, Namen in zwei Farben schreiben (Heft).

## Version 12
- **Testmodus** (im Elternbereich): eigener Lernstand, sieht alle Fächer und Stufen, alle Lektionen offen. „Test-Fortschritt löschen“ setzt nur den Testmodus zurück.
- **Deutsch 1. Klasse** (Profil „1. Klasse“): Anfangsbuchstaben, Silben (hören, klatschen, erste Silbe), Wörter lesen und „ist oder sind“. Alles mit Bild und Vorlesen, Antworten als große Buchstaben oder Bilder.
- **Deutsch 3. Klasse**: neu Nomen, Verlängern (d/t, g/k, b/p), doppelte Mitlaute mit ck und tz, lange Selbstlaute (ie, h, aa/ee/oo, ß), Ableiten (ä/e, äu/eu).
- Auswahl-Aufgaben können jetzt ein Bild zeigen (`pic`), Bilder als Antworten haben (`picOptions`) und große Antwortknöpfe (`bigOptions`).
