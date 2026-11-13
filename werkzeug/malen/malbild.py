# Zerlegt eine Silben-Malbild-Vorlage in Flächen.  Aufruf: python3 malbild.py vorlage.png name [ordner]
# Schreibt <ordner>/<name>.png (Strichzeichnung), <name>-map.png (Rot = Flächennummer), <name>.json (Nummer → Silbe), <name>-debug.png
# Optional im Ordner: <name>-cuts.json  [[x0,y0,x1,y1],...] Schnittlinien, die offene Flächen schließen
#                     <name>-force.json [[x,y,zx,zy],...]   Fläche bei x,y bekommt die Silbe der Fläche bei zx,zy
import numpy as np, json, sys, os
from PIL import Image, ImageDraw
from scipy import ndimage as nd
src, name = sys.argv[1], sys.argv[2]
out = sys.argv[3] if len(sys.argv) > 3 else "."
full = np.array(Image.open(src).convert("L")).astype(int)
Hf, Wf = full.shape
dk = full < 128
rows = [y for y in range(Hf) if dk[y].sum() > Wf * 0.8]
y0 = max(r for r in rows if r < Hf / 2) + 3; y1 = min(r for r in rows if r > Hf / 2) - 3
cols = [x for x in range(Wf) if dk[y0:y1, x].sum() > (y1 - y0) * 0.9]
x0 = max(c for c in cols if c < Wf / 2) + 3; x1 = min(c for c in cols if c > Wf / 2) - 3
im = full[y0:y1, x0:x1]
H, W = im.shape
def opt(suffix):
    p = os.path.join(out, f"{name}-{suffix}.json")
    return json.load(open(p)) if os.path.exists(p) else []
cm = Image.new("L", (W, H), 0); dd = ImageDraw.Draw(cm)
for c in opt("cuts"): dd.line(c, fill=255, width=7)
cut = np.array(cm) > 0
im = np.where(cut, 0, im)
# 1) Wörter finden: kleine dunkle Teile = Buchstaben, nah beieinander = ein Wort
dark = im < 140
dl, dn = nd.label(dark, structure=np.ones((3, 3)))
sizes = nd.sum(np.ones_like(dl), dl, range(1, dn + 1))
cent = []
for i, (sl, sz) in enumerate(zip(nd.find_objects(dl), sizes)):
    h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
    if sz < 1500 and h < 60 and w < 60: cent.append(((sl[0].start + sl[0].stop) / 2, (sl[1].start + sl[1].stop) / 2, sl))
used = set(); words = []
for k in range(len(cent)):
    if k in used: continue
    grp = [k]; used.add(k); ch = True
    while ch:
        ch = False
        for j in range(len(cent)):
            if j not in used and any(abs(cent[j][0] - cent[g][0]) < 30 and abs(cent[j][1] - cent[g][1]) < 45 for g in grp):
                grp.append(j); used.add(j); ch = True
    sls = [cent[k][2] for k in grp]
    parts = []
    for sl in sorted(sls, key=lambda s: s[1].start):
        if parts and sl[1].start < parts[-1][1] - 2: parts[-1] = (min(parts[-1][0], sl[1].start), max(parts[-1][1], sl[1].stop))
        else: parts.append((sl[1].start, sl[1].stop))
    ws = [b - a for a, b in parts]
    box = [min(s[1].start for s in sls), min(s[0].start for s in sls), max(s[1].stop for s in sls), max(s[0].stop for s in sls)]
    lab_ = None
    if len(ws) == 2:
        a, b = ws
        lab_ = "im" if a < 12 else "mi" if b < 12 else ("am" if a < b else "ma")
    words.append((box, ws, lab_))
# 2) Flächen
line = (im < 170) | cut
lab, n = nd.label(~line)
fs = nd.sum(np.ones_like(lab), lab, range(n + 1))
owner = {}; problems = []
for box, ws, l in words:
    if l is None: problems.append(("unklar", box, ws)); continue
    bx0, by0, bx1, by1 = box
    ring = lab[max(0, by0 - 14):by1 + 14, max(0, bx0 - 14):bx1 + 14]
    vals, cnt = np.unique(ring[ring > 0], return_counts=True)
    vals = [v for v, c in sorted(zip(vals, cnt), key=lambda t: -t[1]) if fs[v] > 3000]
    if not vals: problems.append(("keine Fläche", box, l)); continue
    r = vals[0]
    if r in owner and owner[r] != l: problems.append(("zwei Silben in einer Fläche", box, owner[r], l))
    owner[r] = l
assign = {}
for fx, fy, tx, ty in opt("force"):
    r, t = lab[fy, fx], lab[ty, tx]
    if r and t and t in owner: assign[r] = t
for _ in range(4):
    for r in range(1, n + 1):
        if r in owner or r in assign: continue
        m = lab == r
        ring = nd.binary_dilation(m, iterations=10) & ~m
        vals, cnt = np.unique(lab[ring], return_counts=True)
        best = [(c, v) for v, c in zip(vals, cnt) if v > 0 and v != r and (v in owner or v in assign)]
        if best:
            v = max(best)[1]; assign[r] = v if v in owner else assign[v]
ids = sorted(owner); idx = {r: i + 1 for i, r in enumerate(ids)}
reg = np.zeros_like(lab)
for r in ids: reg[lab == r] = idx[r]
for r, v in assign.items(): reg[lab == r] = idx[v]
print(f"{len(words)} Wörter, {len(ids)} Flächen mit Silbe, {len(assign)} Kleinteile zugeordnet")
for p in problems: print("PROBLEM", p)
os.makedirs(out, exist_ok=True)
Image.fromarray(im.astype("uint8"), "L").quantize(16).save(f"{out}/{name}.png", optimize=True)
mp = np.zeros((H, W, 3), "uint8"); mp[..., 0] = reg
Image.fromarray(mp, "RGB").save(f"{out}/{name}-map.png", optimize=True)
json.dump({str(idx[r]): owner[r] for r in ids}, open(f"{out}/{name}.json", "w"))
COL = {"im": (141, 90, 50), "am": (46, 125, 50), "mi": (90, 169, 240), "ma": (155, 211, 106)}
dbg = np.stack([im] * 3, -1).astype(float)
for r in ids:
    m = reg == idx[r]; dbg[m] = np.array(COL[owner[r]]) * (im[m][:, None] / 255.0)
Image.fromarray(dbg.clip(0, 255).astype("uint8")).save(f"{out}/{name}-debug.png")
