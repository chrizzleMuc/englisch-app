# Ausmalbilder nach Silben

Christin liefert die Vorlage (Strichzeichnung im Rahmen, Silbe in jeder Fläche).

    pip install scipy
    python3 werkzeug/malen/malbild.py vorlage.png name werkzeug/malen

Das Skript findet den Rahmen, die Silben-Wörter (zwei Buchstaben aus m n l i a e o, oder sch + Vokal) und die Flächen, gibt kleinen
Flächen ohne Silbe die Silbe des Nachbarn und schreibt name.png, name-map.png (Rot-Wert = Flächennummer),
name.json (Nummer → Silbe) und name-debug.png zum Prüfen. Danach png und map nach img/malen/ kopieren,
das Bild in ../gen_ausmalen.py eintragen und das Skript laufen lassen. Neue Bilder auch in sw.js eintragen.

Wenn eine Fläche offen ist (zwei Silben in einer Fläche): Schnittlinien in name-cuts.json.
Wenn ein Kleinteil die falsche Farbe bekommt: name-force.json.
(Das Eichhörnchen wurde noch mit einer Vorversion gemacht, Ausschnitt 3 px anders.)
