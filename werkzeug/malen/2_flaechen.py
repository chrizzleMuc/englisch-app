import numpy as np, json
from PIL import Image
from scipy import ndimage as nd
src=Image.open('src.png').convert('L')
im=np.array(src).astype(int)[262:1028, 38:1454]
H,W=im.shape
line=im<170
from PIL import ImageDraw
CUTS=json.load(open('cuts.json'))
cm=Image.new('L',(W,H),0); dd=ImageDraw.Draw(cm)
for c in CUTS: dd.line(c,fill=255,width=7)
cut=np.array(cm)>0
line=line|cut
words=json.load(open('words.json'))
def cls(ws):
    if len(ws)!=2: return None
    a,b=ws
    if a<12: return 'im'
    if b<12: return 'mi'
    return 'am' if a<b else 'ma'
# Wort-Pixel (Buchstaben) als "nicht Linie" behandeln, damit Regionen nicht zerschnitten werden
txt=np.zeros_like(line)
for w in words:
    x0,y0,x1,y1=w['box']; txt[y0-3:y1+3,x0-3:x1+3]=True
area=(~line)|(txt & line & False)
lab,n=nd.label(~line)
sizes=nd.sum(np.ones_like(lab),lab,range(n+1))
labels={}
for w in words:
    c=cls(w['widths'])
    x0,y0,x1,y1=w['box']
    ring=lab[max(0,y0-14):y1+14, max(0,x0-14):x1+14]
    vals,cnt=np.unique(ring[ring>0],return_counts=True)
    vals=[v for v,c_ in sorted(zip(vals,cnt),key=lambda t:-t[1]) if sizes[v]>3000]
    rid=vals[0]
    if c is None: c='im'   # Kopf vom Eichhörnchen
    labels.setdefault(rid,set()).add(c)
    w['region']=int(rid); w['label']=c
bad={k:v for k,v in labels.items() if len(v)>1}
print('regions',n,'labeled',len(labels),'conflicts',bad)
# unbeschriftete Regionen dem Nachbarn mit der längsten Grenze zuordnen
owner={k:list(v)[0] for k,v in labels.items()}
assign={}
big=[r for r in range(1,n+1) if r not in owner]
for it in range(3):
  for r in big:
    if r in assign: continue
    m=lab==r
    ring=nd.binary_dilation(m,iterations=10)&~m
    vals,cnt=np.unique(lab[ring],return_counts=True)
    best=[(c,v) for v,c in zip(vals,cnt) if v>0 and v!=r and (v in owner or v in assign)]
    if best:
        v=max(best)[1]; assign[r]=v if v in owner else assign[v]
print('unlabeled',len(big),'assigned',len(assign))
# Flächen ohne Silbe gezielt einem Bereich geben (z. B. Eichel → Eichhörnchen)
for fx,fy,tx,ty in json.load(open('force.json')):
    r=lab[fy,fx]; t=lab[ty,tx]
    if r and t: assign[r]=t if t in owner else assign[t]
reg=np.zeros_like(lab)
ids=sorted(owner)
idx={r:i+1 for i,r in enumerate(ids)}
for r in ids: reg[lab==r]=idx[r]
for r,v in assign.items(): reg[lab==r]=idx[v]
# Kantenpixel (Antialias) dem nächsten Bereich geben, nur helle Grautöne
grey=(im>=170)&(reg==0)
json.dump([{'id':idx[r],'label':owner[r],'px':int((reg==idx[r]).sum())} for r in ids],open('regions.json','w'))
np.save('reg.npy',reg)
COL={'im':(141,90,50),'am':(46,125,50),'mi':(90,169,240),'ma':(155,211,106)}
out=np.stack([im,im,im],-1).astype(float); im=np.where(cut,0,im)
for r in ids:
    m=reg==idx[r]; c=np.array(COL[owner[r]])
    out[m]=c*(im[m][:,None]/255.0)
Image.fromarray(out.clip(0,255).astype('uint8')).save('debug.png')
print(sorted([(owner[r],int(sizes[r])) for r in ids],key=lambda t:t[1])[:5])
# Ausgabe für die App
import os
os.makedirs('out',exist_ok=True)
base=np.where(cut,0,np.array(src).astype(int)[262:1028, 38:1454])
Image.fromarray(base.astype('uint8'),'L').save('out/eichhoernchen.png',optimize=True)
Image.fromarray(reg.astype('uint8'),'L').save('out/eichhoernchen-map.png',optimize=True)
json.dump({str(idx[r]):owner[r] for r in ids},open('out/regions.json','w'))
