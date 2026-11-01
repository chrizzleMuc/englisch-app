# Learnino

Eine Englisch-Lern-App für Kinder: Wörter und kurze Sätze mit Bildern und britischer Aussprache, ganz ohne Werbung. Sie läuft im Browser, lässt sich auf Android-Tablets und -Handys als App installieren und funktioniert danach offline.

## Was drin ist

- Zwei Profile: **Entdecker** (ohne Lesen, alles über Bild und Ton) und **Pirat** (mit Lesen)
- Themen: Hallo & Tschüss (Redewendungen), Tiere, Farben, Zahlen, Essen, Zuhause, Spielen
- Spiele: Kennenlernen, Hör zu und tipp, Was sagst du?, Wort zum Bild, Was bedeutet das?, Memory
- Sterne, Sticker-Album, Tagesserie mit einem Joker pro Woche
- Nachsprechen: jedes neue Wort mehrmals laut sagen (Mikrofon erkennt, dass gesprochen wird, oder Knopf)
- Avatar selbst gestalten: Figur, Hut, Ding in der Hand, Farbe
- Elternbereich: Vornamen, Nachsprechen einstellen, Fortschritt als Datei sichern/laden (z. B. über OneDrive), Stimme testen

## Inhalte ändern

Alle Themen und Wörter stehen in `js/data.js`. Nach jeder Änderung in `sw.js` die Zahl bei `VERSION` erhöhen, damit installierte Apps das Update laden.

## Aussprache

Die App nutzt die Sprachausgabe des Geräts. Damit sie offline britisch spricht: Android-Einstellungen, Suche nach „Sprachausgabe“, bei Google-Sprachausgabe die Sprache „Englisch (Vereinigtes Königreich)“ installieren.

## Lokal ansehen

```
python3 -m http.server 8000
```
Dann im Browser `http://localhost:8000` öffnen.
