# Erzeugt inhalte/mathe/k1-*.json (Mathe 1. Klasse). Eigene Aufgaben, Gliederung nach LehrplanPLUS Jgst. 1.
import json, random, sys, os
OUT = sys.argv[1] if len(sys.argv) > 1 else "inhalte/mathe"
R = random.Random(1311)
M = "−"
ids = set()

def uid(i):
    assert i not in ids, i
    ids.add(i); return i

def nopts(ans, lo, hi, k=3):
    s = {ans}
    while len(s) < k:
        d = R.choice([-2, -1, 1, 2, 3, -3])
        v = ans + d
        if lo <= v <= hi: s.add(v)
    return [str(x) for x in s]

def ch(i, task, ans, options, **kw):
    t = {"kind": "choice", "id": uid(i), "task": task, "options": options, "answer": ans}
    t.update(kw); return t

def ty(i, task, prompt, ans, **kw):
    t = {"kind": "type", "id": uid(i), "task": task, "prompt": prompt, "answer": str(ans), "num": True}
    t.update(kw); return t

def photo(i, task):
    return {"kind": "photo", "id": uid(i), "task": task}

def lesson(title, icon, tasks=None, **kw):
    l = {"title": title, "icon": icon}
    if tasks is not None: l["tasks"] = tasks
    l.update(kw); return l

def test(n=12): return lesson("Test", "⭐", test=True, count=n)

def unit(uid_, title, image, color, lessons):
    return {"id": uid_, "type": "schule", "title_de": title, "image": image, "color": color, "lessons": lessons}

def sample_pairs(cond, n, rng):
    pool = [(a, b) for a in rng for b in rng if cond(a, b)]
    R.shuffle(pool); return pool[:n]

THINGS = ["🍎", "🍓", "⭐", "🐟", "🎈", "🐞" if False else "🍌", "🦆", "🐸", "🚗", "⚽"]

units = []
def grp(p):
    out = []
    for e in p:
        if out and out[-1][0] == e: out[-1][1] += 1
        else: out.append([e, 1])
    return out

# ---------------- 1. Zahlen bis 10 ----------------
L = []
t = []
for k, n in enumerate([3, 1, 5, 2, 4, 3, 5, 2, 4, 1]):
    e = THINGS[k % len(THINGS)]
    t.append(ch(f"m1-z10-zaehl5-{k}", "Wie viele sind es? Zähle!", str(n), nopts(n, 1, 6), vis=f"menge:{e}*{n}", prompt=f"{n} × {e}", bigOptions=True))
L.append(lesson("Zählen bis 5", "🖐️", t))
t = []
for k, n in enumerate([7, 6, 9, 8, 10, 6, 8, 7, 9, 10]):
    if k % 2:
        t.append(ch(f"m1-z10-zaehl10-{k}", "Wie viele Punkte sind es?", str(n), nopts(n, 4, 10), vis=f"feld:{n}", prompt=f"{n} Punkte", bigOptions=True))
    else:
        e = THINGS[(k + 3) % len(THINGS)]
        t.append(ch(f"m1-z10-zaehl10-{k}", "Wie viele sind es? Zähle!", str(n), nopts(n, 4, 10), vis=f"menge:{e}*{n}", prompt=f"{n} × {e}", bigOptions=True))
L.append(lesson("Zählen bis 10", "🔟", t))
t = []
for k, n in enumerate([4, 7, 9, 3, 6, 10, 8, 5]):
    o = nopts(n, 1, 10)
    t.append(ch(f"m1-z10-zeig-{k}", "Welches Feld zeigt die Zahl?", f"feld:{n}", [f"feld:{x}" for x in o], prompt=str(n), showText=True, visOptions=True))
L.append(lesson("Zahlen zeigen", "🔴", t))
t = []
for k, n in enumerate([3, 6, 8, 1, 5, 9, 4, 7, 2, 6]):
    if k % 2 == 0:
        t.append(ty(f"m1-z10-nach-{k}", "Welche Zahl kommt danach?", "", n + 1, vis=f"zug:{n},?"))
    else:
        t.append(ty(f"m1-z10-nach-{k}", "Welche Zahl kommt davor?", "", n - 1 if n > 1 else 0, vis=f"zug:?,{n}"))
L.append(lesson("Nachbarzahlen", "🚂", t))
t = []
seqs = [[1, 2, 3, 4], [3, 4, 5, 6], [5, 6, 7, 8], [7, 8, 9, 10], [10, 9, 8, 7], [6, 5, 4, 3], [2, 3, 4, 5], [9, 8, 7, 6], [4, 5, 6, 7], [8, 7, 6, 5]]
for k, s in enumerate(seqs):
    gap = 1 + k % 3
    ans = s[gap]
    v = [str(x) for x in s]; v[gap] = "?"
    t.append(ty(f"m1-z10-reihe-{k}", "Welche Zahl fehlt im Zug?", "", ans, vis="zug:" + ",".join(v)))
L.append(lesson("Reihenfolge", "🔢", t))
t = []
cases = [(5, 2), (6, 4), (7, 3), (4, 1), (8, 5), (9, 4), (6, 1), (7, 5), (8, 2), (9, 6), (5, 3), (10, 4)]
for k, (n, a) in enumerate(cases):
    if k % 2:
        t.append(ty(f"m1-z10-haus-{k}", "Zahlenhaus: Welche Zahl fehlt?", "", n - a, vis=f"haus:{n};{a},?"))
    else:
        t.append(ty(f"m1-z10-haus-{k}", "Zahlenhaus: Welche Zahl fehlt?", "", n - a, vis=f"haus:{n};?,{a}"))

L.append(lesson("Zahlen zerlegen", "🏠", t))
t = []
for k, a in enumerate([3, 7, 5, 1, 8, 4, 6, 2, 9, 0]):
    if k % 2 == 0:
        t.append(ty(f"m1-z10-partner-{k}", "Wie viele Punkte fehlen bis 10?", "", 10 - a, vis=f"feld:{a}"))
    else:
        t.append(ty(f"m1-z10-partner-{k}", "Partnerzahlen: Zusammen sind es 10.", f"{a} + ☐ = 10", 10 - a))
L.append(lesson("Partnerzahlen", "🤝", t))
t = []
for k, (a, b) in enumerate([(3, 5), (7, 4), (6, 6), (2, 9), (8, 1), (5, 5), (4, 7), (10, 6), (1, 2), (9, 9), (0, 3), (6, 8)]):
    ans = "<" if a < b else ">" if a > b else "="
    t.append(ch(f"m1-z10-vgl-{k}", "Was passt in die Lücke? Kleiner, größer oder gleich?", ans, ["<", ">", "="], prompt=f"{a} ☐ {b}", keepOrder=True, bigOptions=True))
for k, (a, b) in enumerate([(3, 5), (6, 4), (2, 7), (8, 5)]):
    e = THINGS[k]
    big = max(a, b)
    t.append(ch(f"m1-z10-mehr-{k}", "Wo sind mehr?", f"menge:{e}*{big}", [f"menge:{e}*{a}", f"menge:{e}*{b}"], visOptions=True, prompt=f"{a} oder {b}"))
L.append(lesson("Vergleichen", "⚖️", t, mix=True))
L.append(lesson("Ins Heft", "✏️", [photo("m1-z10-heft", "Schreib die Zahlen von 1 bis 10 in dein Heft. Jede Zahl eine ganze Reihe. Schön langsam!")]))
L.append(test(12))
units.append(("k1-zahlen10.json", unit("m1-zahlen10", "Zahlen bis 10", "🖐️", "#3b6fd8", L)))

# ---------------- 2. Rechnen bis 10 ----------------
L = []
def plus(prefix, pairs, withvis):
    out = []
    for k, (a, b) in enumerate(pairs):
        kw = {"vis": f"feld:{a}+{b}"} if withvis and k % 2 == 0 else {}
        out.append(ty(f"{prefix}{a}p{b}", "Rechne.", f"{a} + {b} =", a + b, **kw))
    return out
def minus(prefix, pairs, withvis=False):
    out = []
    for k, (a, b) in enumerate(pairs):
        out.append(ty(f"{prefix}{a}m{b}", "Rechne minus.", f"{a} {M} {b} =", a - b))
    return out
L.append(lesson("Plus bis 5", "➕", plus("m1-r10-", sample_pairs(lambda a, b: a + b <= 5, 10, range(1, 5)), True)))
L.append(lesson("Plus bis 10", "➕", plus("m1-r10-", sample_pairs(lambda a, b: 5 < a + b <= 10, 12, range(1, 10)), True)))
L.append(lesson("Minus bis 5", "➖", minus("m1-r10-", sample_pairs(lambda a, b: a <= 5 and b < a, 10, range(1, 6)))))
L.append(lesson("Minus bis 10", "➖", minus("m1-r10-", sample_pairs(lambda a, b: 5 < a <= 10 and b < a, 12, range(1, 11)))))
t = []
for k, (a, s) in enumerate([(3, 7), (5, 9), (2, 6), (4, 10), (6, 8), (1, 5), (7, 10), (2, 9), (5, 7), (3, 8)]):
    t.append(ty(f"m1-r10-erg-{k}", "Welche Zahl fehlt?", f"{a} + ☐ = {s}", s - a))
L.append(lesson("Ergänzen", "❓", t))
t = []
for k, (a, b) in enumerate([(3, 5), (2, 7), (6, 1), (4, 5), (1, 8)]):
    o = [f"{b} + {a}", f"{a} + {b + 1}", f"{b} {M} {a}" if b > a else f"{a} {M} {b}"]
    t.append(ch(f"m1-r10-tausch-{k}", "Welche Aufgabe ist die Tauschaufgabe?", f"{b} + {a}", o, prompt=f"{a} + {b}"))
for k, (a, b) in enumerate([(2, 6), (3, 4), (5, 2), (1, 7), (4, 4)]):
    t.append(ty(f"m1-r10-nachbar-{k}", "Nachbaraufgabe: Rechne geschickt.", f"{a} + {b} = {a + b}\n{a + 1} + {b} =", a + 1 + b))
L.append(lesson("Tausch- und Nachbaraufgaben", "🔁", t, mix=True))
t = []
for k, (a, b) in enumerate([(2, 5), (3, 4), (6, 3), (1, 8), (4, 5), (7, 2), (5, 5), (3, 6)]):
    t.append(ty(f"m1-r10-umkehr-{k}", "Umkehraufgabe: Rechne zurück.", f"{a} + {b} = {a + b}\n{a + b} {M} {b} =", a))
L.append(lesson("Umkehraufgaben", "↩️" if False else "🔁", t))
L.append(lesson("Plus und minus gemischt", "🔀" if False else "🔁", pick="m1-r10-", count=12))
t = []
for k, (a, b) in enumerate([(3, 4), (2, 5), (1, 6), (4, 4), (5, 3), (2, 2)]):
    t.append(ty(f"m1-r10-mauer-{k}", "Zahlenmauer: Rechne die beiden Steine unten zusammen.", "", a + b, vis=f"mauer:?;{a},{b}"))
for k, (a, b, c) in enumerate([(1, 2, 3), (2, 1, 2), (1, 3, 1), (2, 2, 3)]):
    t.append(ty(f"m1-r10-mauer3-{k}", "Zahlenmauer: Welche Zahl steht ganz oben?", "", a + 2 * b + c, vis=f"mauer:?;{a + b},{b + c};{a},{b},{c}"))
L.append(lesson("Zahlenmauern", "🧱", t))
L.append(test(12))
units.append(("k1-rechnen10.json", unit("m1-rechnen10", "Rechnen bis 10", "➕", "#2a9d8f", L)))

# ---------------- 3. Zahlen bis 20 ----------------
L = []
t = []
for k, n in enumerate([12, 15, 11, 18, 14, 20, 13, 17, 16, 19]):
    t.append(ch(f"m1-z20-zaehl-{k}", "Wie viele Punkte sind es? Ein Zehner und …", str(n), nopts(n, 10, 20), vis=f"zf:{n}", prompt=f"{n} Punkte", bigOptions=True))
L.append(lesson("Zählen bis 20", "🔴", t))
t = []
for k, n in enumerate([14, 11, 17, 19, 13, 16, 12, 18]):
    o = nopts(n, 10, 20)
    t.append(ch(f"m1-z20-zeig-{k}", "Welches Feld zeigt die Zahl?", f"zf:{n}", [f"zf:{x}" for x in o], prompt=str(n), showText=True, visOptions=True))
L.append(lesson("Zahlen zeigen", "🔟", t))
t = []
for k, n in enumerate([11, 15, 13, 18, 12, 16, 14, 19, 17, 10]):
    if k % 2 == 0:
        t.append(ty(f"m1-z20-nach-{k}", "Welche Zahl kommt danach?", "", n + 1, vis=f"zug:{n},?"))
    else:
        t.append(ty(f"m1-z20-nach-{k}", "Welche Zahl kommt davor?", "", n - 1, vis=f"zug:?,{n}"))
L.append(lesson("Nachbarzahlen", "🚂", t))
t = []
seqs = [[11, 12, 13, 14], [14, 15, 16, 17], [10, 12, 14, 16], [12, 14, 16, 18], [20, 19, 18, 17], [18, 16, 14, 12], [11, 13, 15, 17], [15, 14, 13, 12], [5, 10, 15, 20], [13, 15, 17, 19]]
for k, s in enumerate(seqs):
    gap = 3 if k % 2 == 0 else 2
    v = [str(x) for x in s]; ans = s[gap]; v[gap] = "?"
    t.append(ty(f"m1-z20-folge-{k}", "Wie geht es weiter? Welche Zahl fehlt?", "", ans, vis="zug:" + ",".join(v)))
L.append(lesson("Zahlenfolgen", "🔢", t))
t = []
for k, (a, b) in enumerate([(13, 17), (19, 12), (15, 15), (11, 14), (20, 16), (18, 8), (9, 19), (14, 13), (16, 16), (12, 21 - 1), (17, 7), (10, 11)]):
    ans = "<" if a < b else ">" if a > b else "="
    t.append(ch(f"m1-z20-vgl-{k}", "Was passt in die Lücke? Kleiner, größer oder gleich?", ans, ["<", ">", "="], prompt=f"{a} ☐ {b}", keepOrder=True, bigOptions=True))
L.append(lesson("Vergleichen", "⚖️", t))
t = []
for k, n in enumerate([2, 4, 5, 3, 6, 8, 7, 9]):
    kw = {"vis": f"zf:{n}+{n}"} if k % 2 == 0 else {}
    t.append(ty(f"m1-z20-dopp-{k}", "Verdopple die Zahl.", f"{n} + {n} =", 2 * n, **kw))
for k, n in enumerate([4, 10, 6, 16, 8, 20]):
    t.append(ch(f"m1-z20-halb-{k}", "Was ist die Hälfte?", str(n // 2), nopts(n // 2, 1, 12), prompt=f"Die Hälfte von {n}", showText=True, bigOptions=True))
L.append(lesson("Verdoppeln und Halbieren", "✖️", t))
t = []
for k, n in enumerate([4, 7, 10, 3, 12, 9, 6, 15, 8, 11]):
    t.append(ch(f"m1-z20-gerade-{k}", "Gerade oder ungerade? Bleibt ein Punkt allein, ist die Zahl ungerade.", "gerade" if n % 2 == 0 else "ungerade", ["gerade", "ungerade"], vis=f"feld:{n}" if n <= 10 else f"zf:{n}", prompt=f"{n}", showText=True, keepOrder=True))
L.append(lesson("Gerade und ungerade", "⚪", t))
L.append(lesson("Ins Heft", "✏️", [photo("m1-z20-heft", "Schreib die Zahlen von 11 bis 20 in dein Heft. Male zu jeder Zahl ein Zwanzigerfeld mit Punkten.")]))
L.append(test(12))
units.append(("k1-zahlen20.json", unit("m1-zahlen20", "Zahlen bis 20", "🔟", "#7b3fe4", L)))

# ---------------- 4. Rechnen bis 20 ----------------
L = []
t = []
for k, (a, b) in enumerate([(5, 3), (2, 4), (6, 2), (3, 3), (4, 5)]):
    t.append(ty(f"m1-r20-verw-p{k}", "Verwandte Aufgabe: Die kleine Aufgabe hilft.", f"{a} + {b} = {a + b}\n1{a} + {b} =", 10 + a + b))
for k, (a, b) in enumerate([(5, 3), (8, 4), (7, 2), (9, 6), (6, 5)]):
    t.append(ty(f"m1-r20-verw-m{k}", "Verwandte Aufgabe: Die kleine Aufgabe hilft.", f"{a} {M} {b} = {a - b}\n1{a} {M} {b} =", 10 + a - b))
L.append(lesson("Verwandte Aufgaben", "🔟", t))
L.append(lesson("Plus bis 20", "➕", [ty(f"m1-r20-{a}p{b}", "Rechne.", f"{a} + {b} =", a + b) for a, b in sample_pairs(lambda a, b: a >= 10 and (a % 10) + b < 10, 12, range(1, 20))]))
L.append(lesson("Minus bis 20", "➖", [ty(f"m1-r20-{a}m{b}", "Rechne minus.", f"{a} {M} {b} =", a - b) for a, b in sample_pairs(lambda a, b: a > 10 and b <= a % 10, 12, range(1, 20))]))
t = []
for k, (a, b) in enumerate(sample_pairs(lambda a, b: a < 10 and b < 10 and a + b > 10, 12, range(2, 10))):
    kw = {"vis": f"zf:{a}+{b}"} if k % 2 == 0 else {}
    t.append(ty(f"m1-r20-{a}p{b}", "Rechne. Fülle zuerst bis 10 auf.", f"{a} + {b} =", a + b, **kw))
L.append(lesson("Plus über die 10", "🚀", t))
t = []
for k, (a, b) in enumerate(sample_pairs(lambda a, b: 10 < a < 19 and b < 10 and b > a % 10, 12, range(2, 19))):
    t.append(ty(f"m1-r20-{a}m{b}", "Rechne. Geh zuerst bis 10 zurück.", f"{a} {M} {b} =", a - b, **({"vis": f"zf:{a}"} if k % 2 == 0 else {})))
L.append(lesson("Minus über die 10", "🛝", t))
L.append(lesson("Gemischt", "🔁", pick="m1-r20-", count=14))
t = []
for k, (a, b) in enumerate([(8, 5), (6, 7), (9, 9), (12, 5)]):
    t.append(ty(f"m1-r20-mauer-{k}", "Zahlenmauer: Rechne die beiden Steine unten zusammen.", "", a + b, vis=f"mauer:?;{a},{b}"))
for k, (a, b, c) in enumerate([(3, 4, 2), (5, 2, 4), (2, 5, 3), (4, 3, 6)]):
    t.append(ty(f"m1-r20-mauer3-{k}", "Zahlenmauer: Welche Zahl steht ganz oben?", "", a + 2 * b + c, vis=f"mauer:?;{a + b},{b + c};{a},{b},{c}"))
L.append(lesson("Zahlenmauern", "🧱", t))
stories = [
    ("Im Korb liegen 5 Äpfel. Mama legt 3 dazu. Wie viele Äpfel sind es jetzt?", "menge:🍎*5+🍎*3", 8),
    ("Auf dem Teich schwimmen 7 Enten. 2 fliegen weg. Wie viele bleiben?", "menge:🦆*7", 5),
    ("Nathan hat 9 Murmeln. Eleanor hat 4. Wie viele haben sie zusammen?", "", 13),
    ("Auf dem Tisch sind 12 Kekse. 4 werden gegessen. Wie viele sind noch da?", "menge:🍪*12", 8),
    ("Am Baum hängen 6 Birnen und 6 Äpfel. Wie viel Obst ist es zusammen?", "", 12),
    ("Im Bus sitzen 15 Kinder. 5 steigen aus. Wie viele sitzen noch im Bus?", "menge:🚌*1", 10),
    ("Eleanor hat 8 Sticker. Sie bekommt 7 dazu. Wie viele hat sie jetzt?", "menge:⭐*8+⭐*7", 15),
    ("Es gibt 14 Luftballons. 6 platzen. Wie viele sind noch ganz?", "menge:🎈*14", 8),
]
t = []
for k, (txt, p, ans) in enumerate(stories):
    t.append(ch(f"m1-r20-sach-{k}", txt, str(ans), nopts(ans, 0, 20), **({"vis": p} if p else {}), prompt=txt, bigOptions=True))
for x in t:
    if "pic" not in x: x["prompt"] = x["task"]
    else: x["prompt"] = x["task"]
L.append(lesson("Rechengeschichten", "💬", t))
L.append(lesson("Ins Heft", "✏️", [photo("m1-r20-heft", "Rechne diese Aufgaben in deinem Heft: 8 + 5, 9 + 4, 7 + 6, 14 − 6, 13 − 5, 15 − 7. Male bei einer Aufgabe ein Zwanzigerfeld dazu.")]))
L.append(test(14))
units.append(("k1-rechnen20.json", unit("m1-rechnen20", "Rechnen bis 20", "🚀", "#e5484d", L)))

# ---------------- 5. Geld und Uhr ----------------
L = []
NAME = {0.01: "1 Cent", 0.02: "2 Cent", 0.05: "5 Cent", 0.1: "10 Cent", 0.2: "20 Cent", 0.5: "50 Cent", 1: "1 Euro", 2: "2 Euro"}
t = []
for k, (v, others) in enumerate([(1, [2, 0.5]), (2, [1, 0.2]), (0.5, [0.2, 1]), (0.1, [0.01, 0.5]), (0.2, [0.02, 2]), (0.05, [0.5, 0.1]), (1, [0.1, 0.01]), (2, [0.2, 0.05])]):
    t.append(ch(f"m1-gr-muenze-{k}", f"Wo ist die {NAME[v]}-Münze?" if v < 1 else f"Wo ist die {NAME[v]}-Münze?", f"geld:{v}", [f"geld:{x}" for x in [v] + others], visOptions=True, prompt=NAME[v]))
L.append(lesson("Münzen erkennen", "🪙" if False else "💶", t))
t = []
for k, (v, others) in enumerate([(5, [10, 20]), (10, [5, 20]), (20, [10, 5]), (5, [20, 10]), (10, [20, 5]), (20, [5, 10])]):
    t.append(ch(f"m1-gr-schein-{k}", f"Wo ist der {v}-Euro-Schein?", f"geld:{v}", [f"geld:{x}" for x in [v] + others], visOptions=True, prompt=f"{v} Euro"))
L.append(lesson("Scheine erkennen", "💶", t))
t = []
for k, items in enumerate([[2, 1], [1, 1, 1], [2, 2, 1], [5, 2], [5, 1, 1], [10, 2], [10, 5], [5, 5, 2], [10, 5, 2, 1], [2, 2, 2, 2]]):
    s = sum(items)
    t.append(ty(f"m1-gr-zaehl-{k}", "Wie viel Euro sind das zusammen?", "", s, vis="geld:" + ",".join(str(x) for x in items)))
L.append(lesson("Geld zählen", "🧮", t))
t = []
shop = [("Ein Eis kostet 2 €. Du bezahlst mit 5 €. Wie viel Euro bekommst du zurück?", "🍦", 3),
        ("Ein Ball kostet 7 €. Ein Buch kostet 5 €. Wie viel kostet beides zusammen?", "⚽📖", 12),
        ("Du hast 10 €. Ein Spielzeug kostet 6 €. Wie viel Euro bleiben übrig?", "🧸", 4),
        ("Eine Brezel kostet 1 €. Du kaufst 3 Brezeln. Wie viel Euro kostet das?", "🥨🥨🥨", 3),
        ("Ein Buch kostet 8 €. Du hast 5 €. Wie viel Euro fehlen dir?", "📖", 3),
        ("Du hast 20 €. Du kaufst ein Spiel für 10 €. Wie viel Euro bleiben übrig?", "🎲", 10)]
for k, (txt, p, ans) in enumerate(shop):
    t.append(ch(f"m1-gr-kauf-{k}", txt, f"{ans} €", [f"{x} €" for x in nopts(ans, 0, 20)], vis="menge:" + "+".join(f"{e}*{c}" for e, c in grp(p)), prompt=txt, bigOptions=True))
L.append(lesson("Einkaufen", "🛒" if False else "💶", t))
t = []
for k, h in enumerate([3, 7, 12, 9, 1, 6, 10, 4, 8, 2]):
    o = set([h])
    while len(o) < 3: o.add(R.randint(1, 12))
    t.append(ch(f"m1-gr-uhr-{k}", "Wie spät ist es? Der kurze rote Zeiger zeigt die Stunde.", f"{h} Uhr", [f"{x} Uhr" for x in o], vis=f"uhr:{h}", bigOptions=False))
L.append(lesson("Die Uhr lesen", "⏰", t))
t = []
for k, h in enumerate([5, 11, 2, 8, 12, 6, 9, 3]):
    o = [h]
    while len(o) < 3:
        x = R.randint(1, 12)
        if x not in o: o.append(x)
    t.append(ch(f"m1-gr-uhrzeig-{k}", f"Wo ist es {h} Uhr?", f"uhr:{h}", [f"uhr:{x}" for x in o], visOptions=True, prompt=f"{h} Uhr"))
L.append(lesson("Uhrzeit finden", "⏰", t))
t = []
for k, h in enumerate([2, 7, 10, 4, 12, 9]):
    o = [f"halb {h % 12 + 1}", f"{h} Uhr", f"halb {h}"]
    t.append(ch(f"m1-gr-halb-{k}", "Wie spät ist es? Der lange blaue Zeiger zeigt nach unten: Es ist halb.", f"halb {h % 12 + 1}", o, vis=f"uhr:{h}:30"))
L.append(lesson("Halbe Stunden", "🕧" if False else "⏰", t))
L.append(test(12))
units.append(("k1-groessen.json", unit("m1-groessen", "Geld und Uhr", "⏰", "#f2a33a", L)))

# ---------------- 6. Formen, Lage, Muster, Daten ----------------
L = []
FN = {"kreis": "den Kreis", "dreieck": "das Dreieck", "quadrat": "das Quadrat", "rechteck": "das Rechteck"}
t = []
order = ["kreis", "dreieck", "quadrat", "rechteck", "dreieck", "kreis", "rechteck", "quadrat"]
for k, f in enumerate(order):
    others = [x for x in FN if x != f]; R.shuffle(others)
    t.append(ch(f"m1-geo-form-{k}", f"Tipp auf {FN[f]}.", f"form:{f}", [f"form:{x}" for x in [f] + others[:2]], visOptions=True, prompt=FN[f]))
L.append(lesson("Formen erkennen", "🔺" if False else "🟦", t))
t = []
for k in range(8):
    target = list(FN)[k % 4]
    seq = [R.choice(list(FN)) for _ in range(6)]
    n = seq.count(target)
    if n == 0: seq[R.randrange(6)] = target; n = 1
    pl = {"kreis": "Kreise", "dreieck": "Dreiecke", "quadrat": "Quadrate", "rechteck": "Rechtecke"}[target]
    t.append(ch(f"m1-geo-zaehl-{k}", f"Wie viele {pl} siehst du?", str(n), nopts(n, 0, 6), vis="formen:" + ",".join(seq), bigOptions=True))
L.append(lesson("Formen zählen", "🔢", t))
t = []
ANI = [("🐱", "Die Katze"), ("🐶", "Der Hund"), ("🐭", "Die Maus"), ("🐸", "Der Frosch"), ("🐰", "Der Hase")]
WORD = {"links": "links von der Kiste", "rechts": "rechts von der Kiste", "oben": "auf der Kiste", "unten": "unter der Kiste"}
k = 0
for (e, nm) in ANI:
    for w in R.sample(list(WORD), 2):
        others = [x for x in WORD if x != w]; R.shuffle(others)
        t.append(ch(f"m1-geo-lage-{k}", f"{nm} ist {WORD[w]}. Welches Bild passt?", f"lage:{e}:{w}:📦", [f"lage:{e}:{x}:📦" for x in [w] + others[:2]], visOptions=True, prompt=f"{nm} ist {WORD[w]}"))
        k += 1
L.append(lesson("Links, rechts, oben, unten", "📦", t))
t = []
pats = [("🔴🟦", 3), ("🍎🍌", 3), ("⭐⭐🌙", 2), ("🟨🟩🟩", 2), ("🐸🦆", 3), ("🔴🔴🟦", 2), ("🍓🍎🍌", 2), ("🟦🟨", 3), ("⚽🎈🎈", 2), ("🌙⭐", 3)]
for k, (unit_, rep) in enumerate(pats):
    from itertools import islice
    import unicodedata
    # Zeichen der Einheit
    chars = []
    s = unit_
    i = 0
    while i < len(s):
        chars.append(s[i]); i += 1
    seq = (chars * rep)[:len(chars) * rep - (k % len(chars))]
    nxt = chars[len(seq) % len(chars)]
    opts = list(dict.fromkeys(chars + [c for c in ["⭐", "🐸", "🍌", "🟦", "🟨"] if c not in chars]))[:3]
    if nxt not in opts: opts[0] = nxt
    t.append(ch(f"m1-geo-muster-{k}", "Was kommt als Nächstes?", nxt, opts, vis="reihe:" + "".join(seq) + "?", picOptions=True, prompt="".join(seq)))
L.append(lesson("Muster fortsetzen", "🧩", t))
t = []
for k, (s, yes) in enumerate([("herz", True), ("schief", False), ("haus", True), ("fahne", False), ("stern", True), ("welle", False), ("blatt", True), ("stiefel", False)]):
    t.append(ch(f"m1-geo-sym-{k}", "Ist die Figur symmetrisch? Passen beide Hälften genau aufeinander?", "✅" if yes else "❌", ["✅", "❌"], vis=f"sym:{s}", picOptions=True, keepOrder=True, prompt=s))
L.append(lesson("Symmetrie", "🦋", t))
t = []
charts = [("🍎=4,🍌=2,🍓=5", "🍓"), ("🐶=3,🐱=6,🐰=2", "🐱"), ("⚽=5,🎈=3,🚗=1", "⚽"), ("🍦=2,🍪=4,🍰=6", "🍰")]
for k, (c, top) in enumerate(charts):
    opts = [x.split("=")[0] for x in c.split(",")]
    t.append(ch(f"m1-geo-daten-max-{k}", "Wovon gibt es am meisten?", top, opts, vis=f"balken:{c}", picOptions=True, prompt=c))
for k, (c, nm, n) in enumerate([("🍎=4,🍌=2,🍓=5", "Bananen", 2), ("🐶=3,🐱=6,🐰=2", "Hunde", 3), ("🍦=2,🍪=4,🍰=6", "Kekse", 4)]):
    t.append(ch(f"m1-geo-daten-n-{k}", f"Wie viele {nm} sind es? Schau auf die Säule.", str(n), nopts(n, 0, 8), vis=f"balken:{c}", prompt=f"{c}: {nm}", bigOptions=True))
for k, n in enumerate([7, 4, 12]):
    t.append(ch(f"m1-geo-strich-{k}", "Strichliste: Wie viele Striche sind es? Fünf Striche sind ein Bündel.", str(n), nopts(n, 1, 15), vis=f"strich:{n}", bigOptions=True))
L.append(lesson("Daten und Strichlisten", "📊" if False else "🔢", t))
L.append(test(12))
units.append(("k1-formen.json", unit("m1-formen", "Formen, Muster und Daten", "🟦", "#c2417a", L)))

# ---------------- 7. Extra: Zehnerzahlen bis 100 ----------------
L = []
t = []
for k, n in enumerate([3, 5, 2, 7, 4, 9, 6, 8, 1, 10]):
    ans = n * 10
    if k % 2 == 0:
        t.append(ch(f"m1-zz-erk-{k}", "Wie viel ist das? Jedes Bild ist ein Zehner.", str(ans), [str(ans), str(n), str(ans + 10 if ans < 100 else ans - 10)], vis=f"menge:🔟*{n}", prompt=f"{n} Zehner", bigOptions=True))
    else:
        t.append(ty(f"m1-zz-erk-{k}", "Wie viel ist das?", f"{n} Zehner =", ans))
L.append(lesson("Zehnerzahlen erkennen", "🔟", t))
t = []
for k, (a, b) in enumerate([(30, 50), (80, 20), (40, 40), (10, 70), (90, 60), (50, 50), (20, 30), (100, 90)]):
    ans = "<" if a < b else ">" if a > b else "="
    t.append(ch(f"m1-zz-vgl-{k}", "Was passt in die Lücke? Kleiner, größer oder gleich?", ans, ["<", ">", "="], prompt=f"{a} ☐ {b}", keepOrder=True, bigOptions=True))
L.append(lesson("Zehnerzahlen vergleichen", "⚖️", t))
t = []
for k, s in enumerate([[10, 20, 30, 40], [30, 40, 50, 60], [60, 70, 80, 90], [100, 90, 80, 70], [50, 40, 30, 20], [20, 30, 40, 50], [70, 80, 90, 100], [90, 80, 70, 60]]):
    gap = 2 if k % 2 else 3
    v = [str(x) for x in s]; ans = s[gap]; v[gap] = "?"
    t.append(ty(f"m1-zz-folge-{k}", "Welche Zehnerzahl fehlt?", "", ans, vis="zug:" + ",".join(v)))
L.append(lesson("Zehnerfolge", "🚂", t))
L.append(lesson("Plus mit Zehnern", "➕", [ty(f"m1-zz-{a}p{b}", "Rechne. Denk an die kleine Aufgabe.", f"{a} + {b} =", a + b) for a, b in [(x * 10, y * 10) for x, y in sample_pairs(lambda a, b: a + b <= 10, 10, range(1, 9))]]))
L.append(lesson("Minus mit Zehnern", "➖", [ty(f"m1-zz-{a}m{b}", "Rechne. Denk an die kleine Aufgabe.", f"{a} {M} {b} =", a - b) for a, b in [(x * 10, y * 10) for x, y in sample_pairs(lambda a, b: b < a, 10, range(1, 11))]]))
L.append(test(10))
units.append(("k1-zehnerzahlen.json", unit("m1-zehnerzahlen", "Extra: Zehnerzahlen bis 100", "💯", "#5b3fa6", L)))

os.makedirs(OUT, exist_ok=True)
for fn, u in units:
    json.dump(u, open(os.path.join(OUT, fn), "w"), ensure_ascii=False, indent=1)
    n = sum(len(l.get("tasks", [])) for l in u["lessons"])
    print(fn, len(u["lessons"]), "Lektionen", n, "Aufgaben")
