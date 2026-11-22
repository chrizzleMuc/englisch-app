# Fotos für den Sachunterricht (Wikimedia Commons, freie Lizenzen) -> img/fotos/<name>.webp
# und Bildnachweis -> inhalte/fotos.json
# Aufruf: python3 werkzeug/gen_fotos.py <auswahl.json>
#   auswahl.json: {"<name>": {"file": "<lokales Vorschaubild>", "title": "File:…", "artist_txt": "…",
#                  "lic": "CC BY-SA 4.0", "licurl": "…", "page": "https://commons.wikimedia.org/…"}, …}
# <name> ist derselbe Name wie bei den Zeichnungen ([[name]] in den Aufgaben). Gibt es ein Foto,
# zeigt die App das Foto statt der Zeichnung (js/pics.js).
import json, os, sys, urllib.parse
from PIL import Image, ImageOps

OUT = "img/fotos"
os.makedirs(OUT, exist_ok=True)
credits = json.load(open("inhalte/fotos.json")) if os.path.exists("inhalte/fotos.json") else {}
for name, r in json.load(open(sys.argv[1])).items():
    im = ImageOps.exif_transpose(Image.open(r["file"])).convert("RGB")
    if im.width > 640:
        im = im.resize((640, round(im.height * 640 / im.width)), Image.LANCZOS)
    im.save(f"{OUT}/{name}.webp", "WEBP", quality=78, method=6)
    page = "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(r["title"].replace(" ", "_"))
    credits[name] = {"title": r["title"], "lic": r["lic"], "licurl": r.get("licurl", ""), "page": page,
                     "artist": r.get("artist_txt", ""), "label": r.get("label", name)}
json.dump(dict(sorted(credits.items())), open("inhalte/fotos.json", "w"), ensure_ascii=False, indent=1)
print(len(credits), "Fotos")
