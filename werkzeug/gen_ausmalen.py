# Erzeugt inhalte/deutsch/k1-ausmalen.json. Die Bilder (Strichzeichnung + Flächenkarte) macht werkzeug/malen/malbild.py.
import json, sys
COL = {"braun": "#8d5a32", "dunkelgruen": "#2e7d32", "blau": "#5aa9f0", "hellgruen": "#9bd36a", "rot": "#e5484d", "gelb": "#f2c230", "orange": "#f28b30", "lila": "#8e5cd9", "rosa": "#f28ab8", "grau": "#9aa0ad", "gruen": "#4caf50"}
def bild(id_, name, title, colors):
    regions = json.load(open(f"werkzeug/malen/{name}.json"))
    cs = [{"key": k, "label": k, "color": COL[c]} for k, c in colors]
    return {"kind": "paint", "id": id_, "task": "Lies die Silben. Tipp eine Farbe an, dann die passenden Flächen.",
            "prompt": f"Ausmalbild {title}: " + ", ".join(k for k, _ in colors),
            "image": f"img/malen/{name}.png", "map": f"img/malen/{name}-map.png", "regions": regions, "colors": cs}
u = {"id": "d1-ausmalen", "type": "schule", "title_de": "Ausmalbilder: Silben lesen", "image": "🎨", "color": "#8e5cd9",
     "lessons": [
       {"title": "Eichhörnchen: im am mi ma", "icon": "🎨", "tasks": [bild("k1-mal-eichhoernchen", "eichhoernchen", "Eichhörnchen", [("im", "braun"), ("am", "dunkelgruen"), ("mi", "blau"), ("ma", "hellgruen")])]},
       {"title": "Pirateninsel: im am mi ma", "icon": "⛵", "tasks": [bild("k1-mal-piraten", "piraten", "Pirateninsel", [("im", "braun"), ("am", "dunkelgruen"), ("mi", "blau"), ("ma", "hellgruen")])]},
       {"title": "Pferdeweide: la le li lo", "icon": "🐴", "tasks": [bild("k1-mal-pferd", "pferd", "Pferdeweide", [("la", "braun"), ("le", "dunkelgruen"), ("li", "blau"), ("lo", "hellgruen")])]},
       {"title": "Im Zoo: na ne ni no", "icon": "🦁", "tasks": [bild("k1-mal-zoo", "zoo", "Im Zoo", [("na", "gelb"), ("ne", "grau"), ("ni", "blau"), ("no", "gruen")])]},
       {"title": "Unter Wasser: ma mi la li", "icon": "🐢", "tasks": [bild("k1-mal-wasser", "wasser", "Unter Wasser", [("ma", "orange"), ("mi", "blau"), ("la", "rot"), ("li", "gruen")])]},
       {"title": "Im Weltall: an na in ni", "icon": "🚀", "tasks": [bild("k1-mal-weltall", "weltall", "Im Weltall", [("an", "rot"), ("na", "gelb"), ("in", "blau"), ("ni", "grau")])]},
       {"title": "Im Wald: scha sche schi scho", "icon": "🐻", "tasks": [bild("k1-mal-wald", "wald", "Im Wald", [("scha", "braun"), ("sche", "dunkelgruen"), ("schi", "blau"), ("scho", "hellgruen")])]},
     ]}
json.dump(u, open(sys.argv[1] if len(sys.argv) > 1 else "inhalte/deutsch/k1-ausmalen.json", "w"), ensure_ascii=False, indent=1)
