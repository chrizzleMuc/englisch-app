# Ausmalbilder nach Silben

Aus einer Vorlage (Strichzeichnung mit Silben in den Flächen) entstehen zwei Bilder:

1. `1_woerter_finden.py`: findet die Silben-Wörter (Buchstaben-Gruppen) im Bild → words.json
2. `2_flaechen.py`: zerlegt das Bild in Flächen, ordnet jeder Fläche ihre Silbe zu
   (kleine Flächen ohne Silbe gehören zum Nachbarn), schreibt die Strichzeichnung,
   die Flächenkarte (Rot-Wert = Flächennummer, 0 = Linie) und die Zuordnung.
   Offene Linien in der Vorlage werden mit Schnittlinien aus `<name>-cuts.json` geschlossen.
3. `../gen_ausmalen.py` baut daraus `inhalte/deutsch/k1-ausmalen.json`.

Die Skripte haben den Bildausschnitt (Rahmen) für die Eichhörnchen-Vorlage fest eingetragen;
für ein neues Bild Ausschnitt, Schnittlinien und Dateinamen anpassen und `debug.png` prüfen.
