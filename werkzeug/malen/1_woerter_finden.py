import numpy as np, json
from PIL import Image
from scipy import ndimage as nd
src=Image.open('src.png').convert('L')
im=np.array(src).astype(int)[262:1028, 38:1454]   # Innenfläche des Rahmens
H,W=im.shape
dark=im<140
# dunkle Komponenten: großes Linien-Netz vs. Buchstaben
dl,dn=nd.label(dark,structure=np.ones((3,3)))
sizes=nd.sum(np.ones_like(dl),dl,range(1,dn+1))
objs=nd.find_objects(dl)
glyphs=[]
for i,(sl,sz) in enumerate(zip(objs,sizes)):
    h=sl[0].stop-sl[0].start; w=sl[1].stop-sl[1].start
    if sz<1500 and h<60 and w<60: glyphs.append((i+1,sl,sz))
print('glyph comps',len(glyphs))
# Buchstaben zu Wörtern gruppieren
cent=[((sl[0].start+sl[0].stop)/2,(sl[1].start+sl[1].stop)/2,sl,i) for i,sl,sz in glyphs]
words=[]
used=set()
for k,c in enumerate(cent):
    if k in used: continue
    grp=[k]; used.add(k); changed=True
    while changed:
        changed=False
        for j,d in enumerate(cent):
            if j in used: continue
            if any(abs(d[0]-cent[g][0])<30 and abs(d[1]-cent[g][1])<45 for g in grp):
                grp.append(j); used.add(j); changed=True
    words.append(grp)
res=[]
for g in words:
    y0=min(cent[k][2][0].start for k in g); y1=max(cent[k][2][0].stop for k in g)
    x0=min(cent[k][2][1].start for k in g); x1=max(cent[k][2][1].stop for k in g)
    # Spalten-Profil: Buchstaben trennen nach x-Überlappung
    parts=[]
    for k in sorted(g,key=lambda k:cent[k][2][1].start):
        sl=cent[k][2]
        if parts and sl[1].start < parts[-1][1]-2: parts[-1]=(min(parts[-1][0],sl[1].start),max(parts[-1][1],sl[1].stop))
        else: parts.append((sl[1].start,sl[1].stop))
    ws=[b-a for a,b in parts]
    res.append(dict(box=[int(x0),int(y0),int(x1),int(y1)],widths=ws))
for r in sorted(res,key=lambda r:(r['box'][1],r['box'][0])): print(r)
json.dump(res,open('words.json','w'))
