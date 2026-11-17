# Macht aus einem Silben-Malbild ein Wortarten-Malbild.
# Aufruf: python3 werkzeug/malen/wortarten.py <name> <neuer-name>
#   liest werkzeug/malen/<neuer-name>-config.json = {"silben": {"la": "Adjektiv", ...}, "woerter": {"Adjektiv": ["braun", ...], ...}}
# Liest img/malen/<name>.png und <name>-map.png, löscht die Silben aus der Strichzeichnung und
# schreibt in jede Fläche ein Wort der passenden Wortart (lange Wörter in große Flächen).
# Schreibt img/malen/<neuer-name>.png, <neuer-name>-map.png (ohne Silben-Lücken) und werkzeug/malen/<neuer-name>.json
# (Fläche → Wortart, Fläche → Wort). Flächen ohne Platz für ein Wort bekommen "" (zählen nicht).
import json, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as nd

name, new = sys.argv[1], sys.argv[2]
cfg = json.load(open(f"werkzeug/malen/{new}-config.json"))
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
img = np.array(Image.open(f"img/malen/{name}.png").convert("L")).astype(int)
ids = np.array(Image.open(f"img/malen/{name}-map.png").convert("RGB"))[:, :, 0].astype(int)
reg = json.load(open(f"werkzeug/malen/{name}.json"))
H, W = img.shape

# 1) Silben finden (kleine dunkle Teile, wie in malbild.py) und weiß machen
dark = img < 140
dl, dn = nd.label(dark, structure=np.ones((3, 3)))
boxes = [(i, sl) for i, sl in enumerate(nd.find_objects(dl), 1)]
small = [(i, sl) for i, sl in boxes if sl[0].stop - sl[0].start < 60 and sl[1].stop - sl[1].start < 60 and (dl[sl] == i).sum() < 1500]
# Jede Silbe beginnt mit einem schmalen Strich (l, i …): von dort aus nach rechts die Buchstaben einsammeln
stems = [sl for i, sl in small if sl[1].stop - sl[1].start <= 10 and 25 <= sl[0].stop - sl[0].start <= 48]
erase = np.zeros_like(dark)
for i, sl in small:
    for st in stems:
        if st[1].start - 4 <= sl[1].start and sl[1].stop <= st[1].start + 52 and st[0].start - 18 <= sl[0].start and sl[0].stop <= st[0].stop + 14:
            erase[sl] |= dl[sl] == i
            break
erase = nd.binary_dilation(erase, iterations=4)
clean = np.where(erase, 255, img)
# helle Reste der Buchstaben (Kantenglättung) auch weg
halo = nd.binary_dilation(erase, iterations=4) & (clean > 170)
clean = np.where(halo, 255, clean)
# Pixel der gelöschten Buchstaben gehören jetzt zur umgebenden Fläche
ids2 = ids.copy()
near = nd.distance_transform_edt(ids2 == 0, return_distances=False, return_indices=True)
fill = erase & (ids2 == 0)
ids2[fill] = ids[tuple(n[fill] for n in near)]

# 2) Wörter verteilen
font_cache = {}
def font(s):
    if s not in font_cache: font_cache[s] = ImageFont.truetype(FONT, s)
    return font_cache[s]
def edt(m):
    # Bildrand zählt als Rand der Fläche
    return nd.distance_transform_edt(np.pad(m, 1))[1:-1, 1:-1]
def best_spot(rid, word):
    mask = ids2 == rid
    dist = edt(mask)
    for size in range(40, 29, -2):
        f = font(size)
        x0, y0, x1, y1 = f.getbbox(word)
        tw, th = x1 - x0 + 14, y1 - y0 + 10
        # Kandidaten: Punkte weit weg vom Rand
        ys, xs = np.where(dist >= th / 2)
        if not len(ys): continue
        order = np.argsort(-dist[ys, xs])[:400]
        for k in order:
            cy, cx = ys[k], xs[k]
            a, b = cy - th // 2, cx - tw // 2
            if a < 0 or b < 0 or a + th > H or b + tw > W: continue
            if mask[a:a + th, b:b + tw].all(): return size, cx, cy
    return None
cap = {}
for rid in reg:
    m = ids2 == int(rid)
    cap[rid] = edt(m).max() * np.sqrt(m.sum())
out = {}
words = {k: sorted(v, key=len, reverse=True) for k, v in cfg["woerter"].items()}
used = {k: 0 for k in words}
pil = Image.fromarray(clean.astype(np.uint8)).convert("L")
dr = ImageDraw.Draw(pil)
labels = {}
frei = {}  # Flächen ohne Platz: werden gleich ausgemalt
fest = cfg.get("fest", {})  # Fläche → feste Farbe (z. B. brauner Baumstamm), ohne Wort
for rid in sorted(reg, key=lambda r: -cap[r]):
    if rid in fest:
        out[rid] = ""
        frei[rid] = fest[rid]
        continue
    kind = cfg["silben"].get(reg[rid])
    if not kind: out[rid] = ""; continue
    pool = words[kind]
    placed = False
    for j in range(len(pool)):
        w = pool[(used[kind] + j) % len(pool)]
        if w in labels.values(): continue
        spot = best_spot(int(rid), w)
        if spot:
            size, cx, cy = spot
            dr.text((cx, cy), w, font=font(size), fill=20, anchor="mm")
            out[rid] = kind
            labels[rid] = w
            used[kind] += 1
            placed = True
            break
    if not placed:
        out[rid] = ""
        frei[rid] = kind
pil.save(f"img/malen/{new}.png", optimize=True)
# Flächenkarte: dort, wo vorher Silben standen, gehören die Pixel jetzt zur Fläche
mp = np.array(Image.open(f"img/malen/{name}-map.png").convert("RGB"))
mp[:, :, 0] = ids2
mp[:, :, 1] = ids2
mp[:, :, 2] = ids2
Image.fromarray(mp.astype(np.uint8)).save(f"img/malen/{new}-map.png", optimize=True)
json.dump({"regions": out, "words": labels, "prefill": frei}, open(f"werkzeug/malen/{new}.json", "w"), ensure_ascii=False, indent=1)
print(f"{sum(1 for v in out.values() if v)} von {len(out)} Flächen mit Wort", {k: sum(1 for v in out.values() if v == k) for k in words})
