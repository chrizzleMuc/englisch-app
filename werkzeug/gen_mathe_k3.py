# Erzeugt neue Mathe-Einheiten für die 3. Klasse (inhalte/mathe/k3-*.json).
# Gliederung angelehnt an Christins Anton-Übersicht, abgeglichen mit LehrplanPLUS Bayern Jgst. 3.
# Alle Aufgaben sind selbst geschrieben. Ältere k3-Dateien (einmaleins, rechnen100, zahlen1000,
# rechnen1000, sachaufgaben, groessen) stammen nicht aus diesem Skript und bleiben unverändert.
# Aufruf: python3 werkzeug/gen_mathe_k3.py
import json, random, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else "inhalte/mathe"
R = random.Random(1311 + 3)
M = "−"
ids = set()


def uid(i):
    assert i not in ids, i
    ids.add(i)
    return i


def ch(i, task, ans, options, **kw):
    options = [str(o) for o in options]
    assert str(ans) in options, (i, ans, options)
    t = {"kind": "choice", "id": uid(i), "task": task, "options": options, "answer": str(ans)}
    t.update(kw)
    return t


def ty(i, task, prompt, ans, num=True, **kw):
    t = {"kind": "type", "id": uid(i), "task": task, "prompt": prompt, "answer": str(ans)}
    if num:
        t["num"] = True
    t.update(kw)
    return t


def col(i, nums, op, **kw):
    t = {"kind": "column", "id": uid(i), "nums": nums, "op": op}
    t.update(kw)
    return t


def chain(i, task, prompt, lines, **kw):
    t = {"kind": "chain", "id": uid(i), "task": task, "prompt": prompt, "lines": [[a, str(b)] for a, b in lines], "answer": str(lines[-1][1])}
    t.update(kw)
    return t


def photo(i, task, say, show):
    return {"kind": "photo", "id": uid(i), "task": task, "say": say, "show": show}


def lesson(title, icon, tasks=None, **kw):
    l = {"title": title, "icon": icon}
    if tasks is not None:
        l["tasks"] = tasks
    l.update(kw)
    return l


def test(n=14):
    return lesson("Test", "⭐", test=True, count=n)


def unit(u, title, image, color, lessons):
    return {"id": u, "type": "schule", "title_de": title, "image": image, "color": color, "lessons": lessons}


def near(ans, deltas, lo=0, hi=1000, k=3):
    s = [ans]
    for d in deltas:
        v = ans + d
        if lo <= v <= hi and v not in s:
            s.append(v)
        if len(s) == k:
            break
    R.shuffle(s)
    return s


# ---------- Zahlwörter ----------
EIN = ["", "eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun", "zehn", "elf", "zwölf",
       "dreizehn", "vierzehn", "fünfzehn", "sechzehn", "siebzehn", "achtzehn", "neunzehn"]
ZEHN = ["", "", "zwanzig", "dreißig", "vierzig", "fünfzig", "sechzig", "siebzig", "achtzig", "neunzig"]


def wort(n):
    if n == 0:
        return "null"
    h, r = divmod(n, 100)
    out = ""
    if h:
        out += ("ein" if h == 1 else EIN[h]) + "hundert"
    if r:
        if r < 20:
            out += "eins" if r == 1 else EIN[r]
        else:
            z, e = divmod(r, 10)
            out += (("ein" if e == 1 else EIN[e]) + "und" if e else "") + ZEHN[z]
    return out


assert wort(347) == "dreihundertsiebenundvierzig" and wort(101) == "einhunderteins" and wort(516) == "fünfhundertsechzehn"

units = {}

# ================= 1. Zahlen bis 1000 entdecken =================
L = []
t = []
for k, n in enumerate([247, 315, 162, 403, 530, 128, 361, 212, 450, 236]):
    t.append(ty(f"m3-zd-hze-{n}", "Wie viel ist das? Zähle Hunderter, Zehner und Einer.", "", n, vis=f"hze:{n}"))
L.append(lesson("Hunderter, Zehner, Einer", "🧱", t))

t = []
for n in [352, 418, 263, 507, 640, 135]:
    t.append(ty(f"m3-zd-stp-{n}", "Welche Zahl ist in der Stellentafel?", "", n, vis=f"stp:{n}"))
for n, place, name in [(638, 1, "Zehner"), (472, 0, "Hunderter"), (905, 2, "Einer"), (260, 1, "Zehner"), (781, 0, "Hunderter"), (349, 2, "Einer")]:
    d = str(n)[place]
    t.append(ty(f"m3-zd-stz-{n}", f"Wie viele {name} hat die Zahl?", f"{n}", d, vis=f"st:{n}"))
L.append(lesson("Stellentafel", "🔢", t, mix=True))

t = []
for a, b, q, step in [(0, 1000, 300, 100), (0, 1000, 750, 100), (0, 1000, 450, 100), (300, 400, 370, 10), (600, 700, 640, 10),
                      (200, 300, 285, 10), (800, 900, 815, 10), (500, 600, 555, 10), (0, 1000, 900, 100), (100, 200, 130, 10)]:
    deltas = [100, -100, 50, -50] if step == 100 else [10, -10, 5, -5]
    opts = near(q, deltas, a, b)
    t.append(ch(f"m3-zd-zs-{a}-{q}", "Welche Zahl zeigt der Pfeil?", q, opts, vis=f"strahl:{a}:{b}:{q}:{step}", prompt=f"Zahlenstrahl {a} bis {b}", bigOptions=True))
L.append(lesson("Zahlenstrahl", "📏", t))

t = []
for start, q in [(340, 362), (510, 533), (720, 744), (230, 251), (860, 874), (450, 482), (170, 193), (610, 622)]:
    t.append(ty(f"m3-zd-tt-{q}", "Welche Zahl gehört in das gelbe Feld? Tipp: nach rechts +1, nach unten +10.", "", q, vis=f"tafel:{start}:{q}"))
L.append(lesson("Tausendertafel", "🟨", t))

t = []
for n in [347, 512, 609, 870, 128]:
    t.append(ty(f"m3-zd-zw-{n}", "Schreib die Zahl mit Ziffern.", wort(n), n))
for n in [436, 703, 951, 260]:
    s = str(n)
    swap = int(s[0] + s[2] + s[1]) if s[1] != s[2] else n + 10
    wrong2 = n + 100 if n < 900 else n - 100
    t.append(ch(f"m3-zd-zwc-{n}", "Welches Zahlwort passt?", wort(n), [wort(n), wort(swap), wort(wrong2)], prompt=str(n), showText=True))
L.append(lesson("Zahlwörter", "✍️", t, mix=True))

t = []
riddles = [
    ("Ich habe 4 Hunderter, 0 Zehner und 9 Einer.", 409),
    ("Ich bin 10 größer als 395.", 405),
    ("Ich bin 100 kleiner als 830.", 730),
    ("Ich liege genau in der Mitte zwischen 400 und 500.", 450),
    ("Ich bin die größte Zahl mit den Ziffern 3, 8 und 1.", 831),
    ("Ich bin die kleinste dreistellige Zahl.", 100),
    ("Ich habe 7 Hunderter. Meine Zehner und Einer sind beide 5.", 755),
    ("Ich bin der Nachfolger von 699.", 700),
]
for k, (txt, ans) in enumerate(riddles):
    t.append(ty(f"m3-zd-raetsel-{k}", "Zahlenrätsel: Welche Zahl bin ich?", txt, ans))
L.append(lesson("Zahlenrätsel", "🧩", t))
L.append(lesson("Ins Heft", "📸", [photo("m3-zd-foto", "Zeichne im Heft eine Stellentafel (H, Z, E). Trag diese Zahlen mit Plättchen ein: 324, 150, 506.",
                                            "Zeichne eine Stellentafel ins Heft und trag die Zahlen mit Plättchen ein.", ["324", "150", "506"])]))
L.append(test(14))
units["k3-zahlen1000-entdecken"] = unit("m3-zahlen-entdecken", "Zahlen bis 1000 entdecken", "🧱", "#5b6cd6", L)

# ================= 2. Rechenwege bis 1000 =================
L = []
t = []
for a, b in [(300, 400), (500, 200), (100, 600), (700, 300), (200, 250)]:
    t.append(ty(f"m3-rw-hp-{a}-{b}", "Rechne mit Hundertern.", f"{a} + {b} =", a + b))
for a, b in [(900, 200), (700, 300), (1000, 400), (800, 500), (650, 300)]:
    t.append(ty(f"m3-rw-hm-{a}-{b}", "Rechne mit Hundertern.", f"{a} {M} {b} =", a - b))
L.append(lesson("Mit Hundertern", "💯", t, mix=True))

t = []
for a, b in [(160, 200), (170, 720), (340, 250), (480, 130), (560, 270), (290, 340)]:
    t.append(ty(f"m3-rw-hzp-{a}-{b}", "Rechne.", f"{a} + {b} =", a + b))
for a, b in [(300, 150), (700, 430), (850, 320), (640, 280), (510, 160), (920, 450)]:
    t.append(ty(f"m3-rw-hzm-{a}-{b}", "Rechne.", f"{a} {M} {b} =", a - b))
L.append(lesson("Hunderter und Zehner", "🔟", t, mix=True))


def steps_plus(a, b):
    h, z, e = b // 100 * 100, b // 10 % 10 * 10, b % 10
    out, cur = [], a
    for part in [h, z, e]:
        if part:
            out.append((f"{cur} + {part} =", cur + part))
            cur += part
    return out


def steps_minus(a, b):
    h, z, e = b // 100 * 100, b // 10 % 10 * 10, b % 10
    out, cur = [], a
    for part in [h, z, e]:
        if part:
            out.append((f"{cur} {M} {part} =", cur - part))
            cur -= part
    return out


t = []
for a, b in [(478, 245), (356, 127), (514, 268), (233, 449), (162, 375), (605, 287)]:
    t.append(chain(f"m3-rw-hsp-{a}-{b}", "Rechne in Schritten: erst die Hunderter, dann die Zehner, dann die Einer.", f"{a} + {b}", steps_plus(a, b)))
L.append(lesson("Plus in Schritten", "🪜", t))
t = []
for a, b in [(579, 348), (634, 215), (812, 456), (745, 382), (903, 264), (561, 129)]:
    t.append(chain(f"m3-rw-hsm-{a}-{b}", "Rechne in Schritten: erst die Hunderter, dann die Zehner, dann die Einer.", f"{a} {M} {b}", steps_minus(a, b)))
L.append(lesson("Minus in Schritten", "🪜", t))

t = []
# Rechenvorteil: fast ein Hunderter (oder Zehner) → erst den runden Wert, dann ausgleichen
for a, op, b, r in [(944, "-", 98, 100), (527, "+", 199, 200), (365, "+", 99, 100), (812, "-", 297, 300), (436, "+", 198, 200), (703, "-", 99, 100), (458, "+", 39, 40), (621, "-", 58, 60)]:
    d = r - b
    if op == "+":
        t.append(chain(f"m3-rw-vt-p-{a}-{b}", f"Rechne geschickt: {b} ist fast {r}.", f"{a} + {b}", [(f"{a} + {r} =", a + r), (f"{a + r} {M} {d} =", a + b)]))
    else:
        t.append(chain(f"m3-rw-vt-m-{a}-{b}", f"Rechne geschickt: {b} ist fast {r}.", f"{a} {M} {b}", [(f"{a} {M} {r} =", a - r), (f"{a - r} + {d} =", a - b)]))
L.append(lesson("Geschickt rechnen", "💡", t))

t = []
for a, b in [(580, 120), (345, 230), (760, 190), (415, 385)]:
    t.append(ty(f"m3-rw-uk-{a}-{b}", f"Prüfe {a} + {b} = {a + b} mit der Umkehraufgabe.", f"{a + b} {M} {b} =", a))
for a, op, b, shown in [(456, "+", 237, 683), (318, "+", 245, 563), (702, "+", 150, 852), (634, "-", 218, 426), (900, "-", 345, 565), (527, "-", 136, 391)]:
    real = a + b if op == "+" else a - b
    expr = f"{a} {'+' if op == '+' else M} {b} = {shown}"
    t.append(ch(f"m3-rw-pr-{a}-{b}", "Stimmt das? Prüfe mit der Umkehraufgabe.", "stimmt" if shown == real else "stimmt nicht", ["stimmt", "stimmt nicht"], prompt=expr, keepOrder=True,
                explain=f"Richtig ist {real}."))
L.append(lesson("Überprüfen", "🔍", t, mix=True))

t = []
t.append(ch("m3-rw-bg-summe", "Wie heißt das Ergebnis einer Plusaufgabe?", "Summe", ["Summe", "Differenz", "Produkt"], prompt="250 + 130 = 380"))
t.append(ch("m3-rw-bg-diff", "Wie heißt das Ergebnis einer Minusaufgabe?", "Differenz", ["Summe", "Differenz", "Produkt"], prompt="500 − 120 = 380"))
t.append(ch("m3-rw-bg-addieren", "Wie heißt das Rechnen mit plus?", "addieren", ["addieren", "subtrahieren", "multiplizieren"]))
t.append(ch("m3-rw-bg-subtrahieren", "Wie heißt das Rechnen mit minus?", "subtrahieren", ["addieren", "subtrahieren", "dividieren"]))
for a, b in [(250, 130), (400, 350), (612, 200)]:
    t.append(ty(f"m3-rw-bg-s-{a}-{b}", "Rechne.", f"Die Summe von {a} und {b} ist", a + b))
for a, b in [(500, 120), (870, 300), (640, 40)]:
    t.append(ty(f"m3-rw-bg-d-{a}-{b}", "Rechne.", f"Die Differenz von {a} und {b} ist", a - b))
L.append(lesson("Rechenbegriffe", "📖", t))
L.append(lesson("Ins Heft", "📸", [photo("m3-rw-foto", "Rechne im Heft in Schritten und schreib jeden Schritt auf: 367 + 245, 712 − 358, 586 + 99.",
                                            "Rechne im Heft in Schritten und schreib jeden Schritt auf.", ["367 + 245", "712 − 358", "586 + 99"])]))
L.append(test(14))
units["k3-rechenwege"] = unit("m3-rechenwege", "Rechenwege bis 1000", "🪜", "#d0632f", L)

# ================= 3. Schriftlich plus und minus =================
L = []
TASK_P = "Rechne schriftlich. Fang bei den Einern an!"
TASK_M = "Rechne schriftlich. Fang bei den Einern an! Reicht es nicht, entbündle."


def gen_add(n, carries, three=False):
    out = []
    while len(out) < n:
        nums = [R.randint(100, 600), R.randint(10 if three else 100, 400)]
        if three:
            nums.append(R.randint(10, 199))
        s = sum(nums)
        if s > 999:
            continue
        c, cnt = 0, 0
        for i in range(3):
            colsum = sum(x // 10 ** i % 10 for x in nums) + c
            c = colsum // 10
            cnt += c > 0
        if cnt == carries and nums not in out:
            out.append(nums)
    return out


def gen_sub(n, borrows, zero=False):
    out = []
    while len(out) < n:
        a = R.randint(300, 999)
        b = R.randint(100, a - 100)
        if zero and str(a)[1] != "0":
            continue
        if not zero and "0" in str(a)[1:]:
            continue
        if (a - b) < 100:
            continue
        cnt, bb, aa = 0, 0, a
        for i in range(3):
            if aa // 10 ** i % 10 - bb < b // 10 ** i % 10:
                cnt += 1
                bb = 1
            else:
                bb = 0
        if cnt == borrows and [a, b] not in out:
            out.append([a, b])
    return out


L.append(lesson("Plus ohne Übertrag", "➕", [col(f"m3-sr-p0-{a}-{b}", [a, b], "+", task=TASK_P) for a, b in gen_add(6, 0)]))
L.append(lesson("Plus mit Übertrag", "➕", [col(f"m3-sr-p1-{a}-{b}", [a, b], "+", task=TASK_P) for a, b in gen_add(8, 1)]))
L.append(lesson("Zwei Überträge", "➕", [col(f"m3-sr-p2-{a}-{b}", [a, b], "+", task=TASK_P) for a, b in gen_add(6, 2)] +
                [col(f"m3-sr-p3-{a}-{b}-{c}", [a, b, c], "+", task="Rechne schriftlich mit drei Zahlen.") for a, b, c in gen_add(3, 1, three=True)]))
L.append(lesson("Minus ohne Entbündeln", "➖", [col(f"m3-sr-m0-{a}-{b}", [a, b], "-", task=TASK_M) for a, b in gen_sub(6, 0)]))
L.append(lesson("Minus mit Entbündeln", "➖", [col(f"m3-sr-m1-{a}-{b}", [a, b], "-", task=TASK_M) for a, b in gen_sub(8, 1)]))
L.append(lesson("Zweimal entbündeln", "➖", [col(f"m3-sr-m2-{a}-{b}", [a, b], "-", task=TASK_M) for a, b in gen_sub(6, 2)] +
                [col(f"m3-sr-m0z-{a}-{b}", [a, b], "-", task="Profi-Aufgabe: Hier steht eine Null. Entbündle über die Null hinweg!") for a, b in gen_sub(3, 2, zero=True)]))

t = []
for a, b, shown in [(456, 278, 634), (382, 415, 797), (619, 247, 866), (735, 168, 803), (528, 293, 921), (247, 386, 533)]:
    real = a + b
    ra, rb = round(a, -2), round(b, -2)
    t.append(ch(f"m3-sr-ub-{a}-{b}", f"Kann das stimmen? Mach einen Überschlag: {ra} + {rb} = {ra + rb}.", "kann stimmen" if shown == real else "kann nicht stimmen",
                ["kann stimmen", "kann nicht stimmen"], prompt=f"{a} + {b} = {shown}", keepOrder=True, explain=f"Richtig ist {real}."))
L.append(lesson("Überschlag", "🤔", t))
L.append(lesson("Ins Heft", "📸", [photo("m3-sr-foto", "Rechne schriftlich im Heft, mit Überschlag: 465 + 278, 539 + 186, 724 − 359, 803 − 467.",
                                            "Rechne die Aufgaben schriftlich im Heft. Schreib zuerst den Überschlag.", ["465 + 278", "539 + 186", "724 − 359", "803 − 467"])]))
L.append(test(12))
units["k3-schriftlich"] = unit("m3-schriftlich", "Schriftlich plus und minus", "🧮", "#2f8f6b", L)

# ================= 4. Mal und geteilt mit großen Zahlen =================
L = []
t = []
for n in [34, 45, 120, 260, 175, 380]:
    t.append(ty(f"m3-mg-dop-{n}", "Verdopple.", f"Das Doppelte von {n} ist", 2 * n))
for n in [68, 90, 340, 500, 726, 150]:
    t.append(ty(f"m3-mg-hal-{n}", "Halbiere.", f"Die Hälfte von {n} ist", n // 2))
L.append(lesson("Verdoppeln und halbieren", "🪞", t, mix=True))

nums = [12, 37, 58, 81, 140, 263, 396, 405, 774, 919]
L.append(lesson("Gerade und ungerade", "⚖️", [{"kind": "sort", "task": "Ist die Zahl gerade oder ungerade? Schau auf die Einer!", "review": "Gerade oder ungerade?",
                                                 "groups": ["gerade", "ungerade"],
                                                 "items": [{"id": uid(f"m3-mg-gu-{n}"), "text": str(n), "group": "gerade" if n % 2 == 0 else "ungerade"} for n in nums]}]))
t = []
for a, b in [(7, 70), (9, 90), (8, 80), (6, 40), (30, 5), (4, 90), (50, 7), (3, 60), (80, 6), (9, 20)]:
    t.append(ty(f"m3-mg-mz-{a}-{b}", "Rechne. Denk an das kleine Einmaleins!", f"{a} · {b} =", a * b))
L.append(lesson("Mal mit Zehnerzahlen", "✖️", t))
t = []
for a, b in [(490, 70), (360, 60), (200, 50), (160, 80), (420, 7), (240, 6), (350, 5), (810, 90), (480, 8), (280, 40)]:
    t.append(ty(f"m3-mg-gz-{a}-{b}", "Rechne. Denk an das kleine Einmaleins!", f"{a} : {b} =", a // b))
L.append(lesson("Geteilt mit Zehnerzahlen", "➗", t))

t = []
for a, b in [(5, 13), (4, 17), (6, 14), (3, 26), (7, 15), (8, 12)]:
    z, e = b // 10 * 10, b % 10
    t.append(chain(f"m3-mg-hm-{a}-{b}", "Rechne in Schritten: erst mit den Zehnern, dann mit den Einern.", f"{a} · {b}",
                   [(f"{a} · {z} =", a * z), (f"{a} · {e} =", a * e), (f"{a * z} + {a * e} =", a * b)], vis=f"kreuz:{a}:{z},{e}"))
for a, b in [(4, 125), (3, 214), (2, 342)]:
    h, z, e = b // 100 * 100, b // 10 % 10 * 10, b % 10
    t.append(chain(f"m3-mg-hm3-{a}-{b}", "Rechne in Schritten: Hunderter, Zehner, Einer.", f"{a} · {b}",
                   [(f"{a} · {h} =", a * h), (f"{a} · {z} =", a * z), (f"{a} · {e} =", a * e), (f"{a * h} + {a * z} + {a * e} =", a * b)], vis=f"kreuz:{a}:{h},{z},{e}"))
L.append(lesson("Malkreuz", "✖️", t))

t = []
for a, b in [(126, 3), (84, 4), (96, 3), (175, 5), (148, 4), (192, 6)]:
    big = (a // b) // 10 * 10 * b
    rest = a - big
    t.append(chain(f"m3-mg-hg-{a}-{b}", "Rechne in Schritten: Teile die Zahl in zwei leichte Teile.", f"{a} : {b}",
                   [(f"{big} : {b} =", big // b), (f"{rest} : {b} =", rest // b), (f"{big // b} + {rest // b} =", a // b)]))
L.append(lesson("Geteilt in Schritten", "➗", t))

t = []
for a, b in [(47, 6), (38, 5), (59, 7), (26, 4), (71, 9), (45, 8)]:
    t.append(chain(f"m3-mg-rest-{a}-{b}", "Teile mit Rest.", f"{a} : {b}", [(f"{a} : {b} =", a // b), ("Rest", a % b)]))
L.append(lesson("Teilen mit Rest", "🍪", t))

t = []
for left, right in [("43 + 8", "45 + 6"), ("7 · 8", "60 − 5"), ("300 + 250", "600 − 40"), ("9 · 9", "80"), ("72 : 8", "3 · 3"), ("500 − 120", "400 − 30"), ("6 · 70", "400 + 30"), ("250 + 250", "5 · 100")]:
    lv, rv = eval(left.replace("·", "*").replace(":", "//").replace("−", "-")), eval(right.replace("·", "*").replace(":", "//").replace("−", "-"))
    rel = "<" if lv < rv else ">" if lv > rv else "="
    t.append(ch(f"m3-mg-gl-{left}-{right}".replace(" ", ""), "Größer, kleiner oder gleich? Rechne beide Seiten aus.", rel, ["<", "=", ">"], prompt=f"{left}  ?  {right}",
                keepOrder=True, bigOptions=True, explain=f"{left} = {lv} und {right} = {rv}."))
L.append(lesson("Gleich oder ungleich?", "⚖️", t))
t = []
for expr in ["7 + 5 · 3", "20 − 4 · 3", "6 · 4 + 8", "30 : 5 + 7", "50 − 36 : 4", "8 + 2 · 9", "9 · 3 − 7", "100 − 10 · 6", "4 · 5 + 3 · 6", "60 : 6 − 2 · 4"]:
    val = eval(expr.replace("·", "*").replace(":", "//").replace("−", "-"))
    t.append(ty(f"m3-ex-pvs-{expr}".replace(" ", ""), "Punkt vor Strich: Rechne zuerst mal und geteilt!", f"{expr} =", val))
L.append(lesson("Punkt vor Strich", "⚫", t))

t = []
stories = [
    ("Ein Bus hat 48 Sitzplätze. Wie viele Plätze haben 6 Busse?", 288),
    ("Im Zoo bekommen 4 Elefanten zusammen 360 kg Heu. Jeder gleich viel. Wie viel kg bekommt ein Elefant?", 90),
    ("Eine Packung hat 24 Stifte. Die Lehrerin kauft 5 Packungen. Wie viele Stifte sind das?", 120),
    ("140 Kinder fahren ins Schullandheim. In jedes Zimmer passen 7 Kinder. Wie viele Zimmer brauchen sie?", 20),
    ("Ein Briefträger trägt am Tag 125 Briefe aus. Wie viele Briefe sind es in 3 Tagen?", 375),
    ("96 Äpfel werden gerecht auf 8 Kisten verteilt. Wie viele Äpfel kommen in eine Kiste?", 12),
]
for k, (txt, ans) in enumerate(stories):
    t.append(ty(f"m3-mg-sach-{k}", "Lies genau und rechne. Schreib nur die Zahl.", txt, ans))
L.append(lesson("Sachaufgaben", "📮", t))
L.append(lesson("Ins Heft", "📸", [photo("m3-mg-foto", "Rechne im Heft mit dem Malkreuz: 6 · 23, 4 · 37, 3 · 125. Schreib zu 3 · 125 eine Rechengeschichte.",
                                            "Rechne im Heft mit dem Malkreuz.", ["6 · 23", "4 · 37", "3 · 125"])]))
L.append(test(14))
units["k3-mal-geteilt"] = unit("m3-mal-geteilt", "Mal und geteilt mit großen Zahlen", "✖️", "#3b6fd8", L)

# ================= 5. Längen und Gewichte =================
L = []
t = []
for km, m in [(1, 0), (2, 0), (3, 500), (1, 250), (4, 50)]:
    t.append(ty(f"m3-lg-km-{km}-{m}", "Wie viele Meter sind das? 1 km = 1000 m.", f"{km} km {m} m = _ m" if m else f"{km} km = _ m", km * 1000 + m))
for txt, ans in [("1 m = _ cm", 100), ("5 cm = _ mm", 50), ("4 m 7 cm = _ cm", 407)]:
    if ans:
        t.append(ty(f"m3-lg-um-{txt}".replace(" ", "").replace("_", "x").replace("=", "-"), "Rechne um.", txt, ans))
L.append(lesson("Kilometer und Meter", "🛣️", t))

t = []
for txt, ans, opts in [("Wie weit ist es mit dem Fahrrad zur Oma?", "km", ["mm", "cm", "m", "km"]), ("Wie lang ist ein Bleistift?", "cm", ["mm", "cm", "m", "km"]),
                       ("Wie dick ist eine Münze?", "mm", ["mm", "cm", "m", "km"]), ("Wie hoch ist ein Haus?", "m", ["mm", "cm", "m", "km"])]:
    t.append(ch(f"m3-lg-einh-{ans}", "Welche Einheit passt?", ans, opts, prompt=txt, keepOrder=True))
for a, b in [("1 km", "900 m"), ("3 m", "300 cm"), ("45 mm", "5 cm"), ("2 km", "2500 m")]:
    def val(s):
        n, u_ = s.split()
        return int(n) * {"mm": 1, "cm": 10, "m": 1000, "km": 1000000}[u_]
    rel = "<" if val(a) < val(b) else ">" if val(a) > val(b) else "="
    t.append(ch(f"m3-lg-vgl-{a}-{b}".replace(" ", ""), "Was ist länger?", rel, ["<", "=", ">"], prompt=f"{a}  ?  {b}", keepOrder=True, bigOptions=True))
L.append(lesson("Längen vergleichen", "📏", t, mix=True))

t = []
for txt, ans, opts in [("Wie schwer ist eine Tafel Schokolade?", "100 g", ["100 g", "100 kg", "1 g"]), ("Wie schwer ist ein Kind in der 3. Klasse?", "30 kg", ["30 g", "30 kg", "300 kg"]),
                       ("Wie schwer ist ein Apfel?", "200 g", ["2 g", "200 g", "20 kg"]), ("Wie schwer ist ein Auto?", "1000 kg", ["10 kg", "100 g", "1000 kg"]),
                       ("Wie schwer ist ein Brief?", "20 g", ["20 g", "2 kg", "200 kg"]), ("Wie schwer ist eine Packung Mehl?", "1 kg", ["1 g", "1 kg", "100 kg"])]:
    t.append(ch(f"m3-lg-gw-{txt[14:30]}".replace(" ", "-"), "Schätze: Was passt am besten?", ans, opts, prompt=txt))
for txt, ans in [("1 kg = _ g", 1000), ("3 kg = _ g", 3000), ("2 kg 500 g = _ g", 2500), ("1 kg 250 g = _ g", 1250), ("4000 g = _ kg", 4), ("Halbes Kilogramm = _ g", 500)]:
    t.append(ty(f"m3-lg-kgg-{txt}".replace(" ", "").replace("_", "x").replace("=", "-"), "Rechne um. 1 kg = 1000 g.", txt, ans))
L.append(lesson("Gewichte", "⚖️", t, mix=True))

t = []
stories = [
    ("Leni läuft zur Schule 800 m und wieder zurück. Wie viele Meter läuft sie insgesamt?", 1600),
    ("Ein Seil ist 5 m lang. Papa schneidet 1 m 20 cm ab. Wie viele Zentimeter sind übrig?", 380),
    ("Ein Rucksack wiegt 2 kg. Ben packt eine Trinkflasche mit 750 g dazu. Wie viel Gramm wiegt der Rucksack jetzt?", 2750),
    ("Mama kauft 3 Packungen Nudeln zu je 500 g. Wie viel Gramm sind das?", 1500),
    ("Der Wanderweg ist 6 km lang. Familie Huber hat schon 3500 m geschafft. Wie viele Meter fehlen noch?", 2500),
    ("Ein Brett ist 2 m lang. Es wird in 4 gleich lange Stücke gesägt. Wie viele Zentimeter ist ein Stück lang?", 50),
]
for k, (txt, ans) in enumerate(stories):
    t.append(ty(f"m3-lg-sach-{k}", "Lies genau und rechne. Schreib nur die Zahl.", txt, ans))
L.append(lesson("Sachaufgaben", "🗺️", t))
L.append(test(12))
units["k3-laengen-gewichte"] = unit("m3-laengen-gewichte", "Längen und Gewichte", "⚖️", "#4f772d", L)

# ================= 6. Uhrzeit und Zeitdauer =================
L = []
t = []
for h, m in [(3, 15), (7, 45), (10, 25), (1, 50), (8, 5), (11, 35), (5, 40), (2, 10)]:
    ans = f"{h}:{m:02d}"
    wrong = [f"{h}:{(m + 30) % 60:02d}", f"{(h % 12) + 1}:{m:02d}", f"{h}:{(m + 5) % 60:02d}"]
    opts = [ans] + [w for w in wrong if w != ans][:2]
    R.shuffle(opts)
    t.append(ch(f"m3-uz-lesen-{h}-{m}", "Wie spät ist es? Der lange blaue Zeiger zeigt die Minuten.", ans, opts, vis=f"uhr:{h}:{m}", bigOptions=True))
L.append(lesson("Uhr lesen", "🕒", t))

t = []
for h, nach in [(3, 15), (7, 19), (9, 21), (5, 17), (11, 23), (1, 13)]:
    t.append(ty(f"m3-uz-24-{h}", "Wie heißt die Uhrzeit am Nachmittag oder Abend?", f"{h} Uhr nachmittags = _ Uhr", nach))
for txt, ans in [("1 h = _ min", 60), ("1 min = _ s", 60), ("eine halbe Stunde = _ min", 30), ("eine Viertelstunde = _ min", 15), ("2 h = _ min", 120), ("1 Tag = _ h", 24)]:
    t.append(ty(f"m3-uz-um-{txt}".replace(" ", "").replace("_", "x").replace("=", "-"), "Wie viel ist das?", txt, ans))
L.append(lesson("Stunden und Minuten", "⏱️", t, mix=True))

t = []
for a, b in [("8:00", "8:45"), ("9:15", "10:00"), ("14:30", "15:10"), ("7:50", "8:20"), ("10:40", "11:25"), ("16:15", "17:45")]:
    ha, ma = map(int, a.split(":"))
    hb, mb = map(int, b.split(":"))
    t.append(ty(f"m3-uz-dauer-{a}-{b}", "Wie lange dauert es? Schreib die Minuten.", f"von {a} Uhr bis {b} Uhr = _ min", (hb * 60 + mb) - (ha * 60 + ma)))
for a, d in [("8:15", 30), ("11:40", 25), ("13:50", 45), ("17:35", 50)]:
    ha, ma = map(int, a.split(":"))
    e = ha * 60 + ma + d
    t.append(ty(f"m3-uz-ende-{a}-{d}", "Wann ist es zu Ende? Schreib die Uhrzeit mit Doppelpunkt, z. B. 9:05.", f"Beginn {a} Uhr, Dauer {d} min. Ende: _ Uhr", f"{e // 60}:{e % 60:02d}", num=False))
L.append(lesson("Zeitdauer", "⏳", t))

t = []
stories = [
    ("Der Film beginnt um 15:30 Uhr und dauert 90 Minuten. Um wie viel Uhr ist er zu Ende? (z. B. 9:05)", "17:00"),
    ("Der Zug fährt um 7:48 Uhr ab und kommt um 8:21 Uhr an. Wie viele Minuten dauert die Fahrt?", "33"),
    ("Die Pause beginnt um 9:35 Uhr und dauert 20 Minuten. Wann ist sie zu Ende? (z. B. 9:05)", "9:55"),
    ("Nathan übt jeden Tag 15 Minuten Flöte. Wie viele Minuten sind das in 4 Tagen?", "60"),
    ("Das Fußballtraining geht von 16:00 Uhr bis 17:30 Uhr. Wie viele Minuten sind das?", "90"),
]
for k, (txt, ans) in enumerate(stories):
    t.append(ty(f"m3-uz-sach-{k}", "Lies genau und rechne.", txt, ans, num=":" not in ans))
L.append(lesson("Sachaufgaben", "🚆", t))
L.append(test(12))
units["k3-uhrzeit"] = unit("m3-uhrzeit", "Uhrzeit und Zeitdauer", "⏰", "#8a4fd6", L)

# ================= 7. Rechnen mit Geld =================
L = []
t = []
for e, c in [(3, 50), (12, 5), (7, 99), (20, 40)]:
    t.append(ty(f"m3-gd-komma-{e}-{c}", "Schreib mit Komma.", f"{e} € {c} ct = _ €", f"{e},{c:02d}", num=False, also=[f"{e}.{c:02d}"]))
for txt, ans in [("4,20 € = _ ct", 420), ("0,75 € = _ ct", 75), ("10,05 € = _ ct", 1005), ("2,50 € = _ ct", 250)]:
    t.append(ty(f"m3-gd-ct-{txt}".replace(" ", "").replace("_", "x").replace("=", "-").replace(",", "k"), "Wie viele Cent sind das?", txt, ans))
L.append(lesson("Euro mit Komma", "💶", t, mix=True))

t = []
for coins in [[2, 1, 0.5, 0.2], [5, 2, 2, 0.1], [10, 5, 1, 0.5, 0.05], [1, 1, 0.5, 0.2, 0.2, 0.1], [20, 2, 0.5]]:
    tot = round(sum(coins) * 100)
    t.append(ty(f"m3-gd-sum-{tot}", "Wie viel Geld ist das? Schreib in Cent.", "", tot, vis="geld:" + ",".join(str(c) for c in coins)))
L.append(lesson("Geld zählen", "🪙", t))

t = []
for pay, cost in [(10, 6.40), (5, 3.75), (20, 12.90), (10, 2.35), (50, 34.00), (5, 1.15)]:
    back = round((pay - cost) * 100)
    t.append(ty(f"m3-gd-rueck-{pay}-{int(cost * 100)}", "Wie viel Rückgeld bekommst du? Schreib in Cent.", f"Du zahlst mit {pay} €. Es kostet " + f"{cost:.2f}".replace(".", ",") + " €.", back))
L.append(lesson("Rückgeld", "🧾", t))

t = []
stories = [
    ("Ein Heft kostet 1,20 €. Lea kauft 3 Hefte. Wie viel Cent zahlt sie?", 360),
    ("Ein Eis kostet 1,50 €. Wie viel Cent kosten 4 Eis?", 600),
    ("Tim hat 8 € gespart. Ein Buch kostet 12 €. Wie viele Euro fehlen ihm noch?", 4),
    ("4 Freunde teilen sich eine Pizza für 16 €. Wie viele Euro zahlt jeder?", 4),
    ("Oma kauft Brot für 3,40 € und Butter für 2,10 €. Wie viel Cent zahlt sie zusammen?", 550),
    ("Eine Kinokarte kostet 7,50 €. Wie viel Cent kosten 2 Karten?", 1500),
]
for k, (txt, ans) in enumerate(stories):
    t.append(ty(f"m3-gd-sach-{k}", "Lies genau und rechne. Schreib nur die Zahl.", txt, ans))
L.append(lesson("Einkaufen", "🛒", t))
L.append(test(12))
units["k3-geld"] = unit("m3-geld", "Rechnen mit Geld", "💶", "#c08a1e", L)

# ================= 8. Daten und Zufall =================
L = []
t = []
data = [("🍎=6,🍌=3,🍓=8,🍊=5", "Lieblingsobst der Klasse 3b"), ("⚽=7,🎨=4,🎵=5,📚=2", "Lieblings-AG"), ("🐶=9,🐱=6,🐰=3,🐟=2", "Haustiere in der Klasse")]
qs = []
NAMES = {"🍎": "Apfel", "🍌": "Banane", "🍓": "Erdbeere", "🍊": "Orange", "⚽": "Fußball", "🎨": "Malen", "🎵": "Musik", "📚": "Lesen", "🐶": "Hund", "🐱": "Katze", "🐰": "Hase", "🐟": "Fisch"}
for di, (vis_, title) in enumerate(data):
    items = [(p.split("=")[0], int(p.split("=")[1])) for p in vis_.split(",")]
    most = max(items, key=lambda x: x[1])
    least = min(items, key=lambda x: x[1])
    a, b = items[0], items[1]
    qs.append(ch(f"m3-dz-most-{di}", f"{title}: Was haben die meisten gewählt?", most[0], [x[0] for x in items], vis=f"balken:{vis_}", picOptions=True, keepOrder=True))
    qs.append(ty(f"m3-dz-diff-{di}", f"{title}: Wie viele Kinder mehr haben {NAMES[a[0]]} gewählt als {NAMES[b[0]]}?", "", a[1] - b[1], vis=f"balken:{vis_}") if a[1] > b[1] else
              ty(f"m3-dz-diff-{di}", f"{title}: Wie viele Kinder weniger haben {NAMES[a[0]]} gewählt als {NAMES[b[0]]}?", "", b[1] - a[1], vis=f"balken:{vis_}"))
    qs.append(ty(f"m3-dz-sum-{di}", f"{title}: Wie viele Kinder sind es zusammen?", "", sum(x[1] for x in items), vis=f"balken:{vis_}"))
L.append(lesson("Diagramme lesen", "📊", qs))

t = []
for n in [7, 12, 15, 9, 18, 23]:
    t.append(ty(f"m3-dz-strich-{n}", "Wie viele Striche sind es? Ein Bündel hat 5.", "", n, vis=f"strich:{n}"))
L.append(lesson("Strichlisten", "✏️", t))

t = []
for txt, vis_, ans in [("Du ziehst ohne hinzuschauen. Was ziehst du wahrscheinlicher?", "menge:🔴*7+⚪*2", "🔴"), ("Du ziehst ohne hinzuschauen. Was ziehst du wahrscheinlicher?", "menge:🔴*2+⚪*6", "⚪")]:
    t.append(ch(f"m3-dz-w-{vis_[6:12]}", txt, ans, ["🔴", "⚪"], vis=vis_, picOptions=True, keepOrder=True))
for txt, vis_, ans in [("Im Säckchen sind nur rote Kugeln. Du ziehst eine rote Kugel.", "menge:🔴*5", "sicher"),
                       ("Im Säckchen sind nur rote Kugeln. Du ziehst eine weiße Kugel.", "menge:🔴*5", "unmöglich"),
                       ("Im Säckchen sind rote und weiße Kugeln. Du ziehst eine weiße Kugel.", "menge:🔴*3+⚪*3", "möglich"),
                       ("Du drehst ein Glücksrad mit den Zahlen 1 bis 8. Du drehst eine 9.", "", "unmöglich")]:
    kw = {"vis": vis_} if vis_ else {"pic": "🎯"}
    t.append(ch(f"m3-dz-smu-{len(t)}", "Sicher, möglich oder unmöglich?", ans, ["sicher", "möglich", "unmöglich"], prompt=txt, showText=True, keepOrder=True, **kw))
L.append(lesson("Wahrscheinlichkeit", "🎲", t))

t = []
for txt, ans in [("Mia hat 3 T-Shirts und 2 Hosen. Wie viele verschiedene Kombinationen kann sie anziehen?", 6),
                 ("Es gibt 2 Eissorten und 3 Soßen. Jedes Eis bekommt eine Sorte und eine Soße. Wie viele Möglichkeiten gibt es?", 6),
                 ("4 Kinder geben sich zur Begrüßung je einmal die Hand. Wie oft werden Hände geschüttelt?", 6),
                 ("Bilde zweistellige Zahlen aus den Ziffern 1, 2 und 3. Jede Ziffer nur einmal pro Zahl. Wie viele Zahlen gibt es?", 6),
                 ("Ein Menü: 2 Vorspeisen, 2 Hauptgerichte, 2 Nachspeisen. Wie viele verschiedene Menüs gibt es?", 8)]:
    t.append(ty(f"m3-dz-komb-{len(t)}", "Knobelaufgabe: Probiere alle Möglichkeiten aus.", txt, ans))
L.append(lesson("Kombinieren", "🧩", t))
L.append(test(12))
units["k3-daten"] = unit("m3-daten", "Daten und Zufall", "📊", "#2a9d8f", L)
# ================= 9. Geometrie =================
L = []
SOL = {"wuerfel": "Würfel", "quader": "Quader", "kugel": "Kugel", "zylinder": "Zylinder", "kegel": "Kegel", "pyramide": "Pyramide"}
t = []
for k in ["wuerfel", "quader", "kugel", "zylinder", "kegel", "pyramide"]:
    others = [v for kk, v in SOL.items() if kk != k]
    R.shuffle(others)
    t.append(ch(f"m3-geo-k-{k}", "Wie heißt der Körper?", SOL[k], [SOL[k]] + others[:2], vis=f"koerper:{k}"))
t.append(ch("m3-geo-k-name-zyl", "Welcher Körper ist ein Zylinder?", "koerper:zylinder", ["koerper:zylinder", "koerper:kegel", "koerper:quader"], prompt="Zylinder", showText=True, visOptions=True))
t.append(ch("m3-geo-k-name-pyr", "Welcher Körper ist eine Pyramide?", "koerper:pyramide", ["koerper:wuerfel", "koerper:pyramide", "koerper:kegel"], prompt="Pyramide", showText=True, visOptions=True))
L.append(lesson("Körper erkennen", "🧊", t))

t = []
for txt, ans, opts in [("Wie viele Ecken hat ein Würfel?", 8, [6, 8, 12]), ("Wie viele Kanten hat ein Würfel?", 12, [8, 10, 12]), ("Wie viele Flächen hat ein Würfel?", 6, [4, 6, 8]),
                       ("Wie viele Ecken hat ein Quader?", 8, [4, 8, 12]), ("Wie viele Ecken hat eine Kugel?", 0, [0, 1, 2]), ("Wie viele Flächen hat eine Pyramide mit quadratischer Grundfläche?", 5, [4, 5, 6])]:
    vis_ = "koerper:" + ("wuerfel" if "Würfel" in txt else "quader" if "Quader" in txt else "kugel" if "Kugel" in txt else "pyramide")
    t.append(ch(f"m3-geo-ekf-{len(t)}", txt, ans, opts, vis=vis_, keepOrder=True, bigOptions=True))
t.append(ch("m3-geo-roll", "Welcher Körper kann rollen?", "koerper:kugel", ["koerper:wuerfel", "koerper:kugel", "koerper:pyramide"], visOptions=True))
t.append(ch("m3-geo-quadrat", "Bei welchem Körper sind alle Flächen gleich große Quadrate?", "koerper:wuerfel", ["koerper:quader", "koerper:wuerfel", "koerper:zylinder"], visOptions=True))
L.append(lesson("Ecken, Kanten, Flächen", "📐", t))

NETS_OK = ["1,0;0,1;1,1;2,1;3,1;1,2", "0,0;0,1;1,1;2,1;3,1;3,2", "0,1;1,1;2,1;3,1;0,0;0,2", "0,0;1,0;1,1;2,1;2,2;3,2", "0,1;1,1;2,1;3,1;1,0;2,2"]
NETS_BAD = ["0,0;1,0;2,0;3,0;4,0;2,1", "0,0;1,0;0,1;1,1;2,1;3,1", "0,0;1,0;2,0;3,0;0,1;3,1", "0,0;1,0;2,0;0,1;1,1;2,1"]
t = []
for k, good in enumerate(NETS_OK):
    bad = [NETS_BAD[k % len(NETS_BAD)], NETS_BAD[(k + 1) % len(NETS_BAD)]]
    t.append(ch(f"m3-geo-netz-{k}", "Welches Netz kann man zu einem Würfel falten?", f"netz:{good}", [f"netz:{good}"] + [f"netz:{b}" for b in bad], visOptions=True))
L.append(lesson("Würfelnetze", "🗳️", t))

t = []
for k, (code, n) in enumerate([("2,1;1,1", 5), ("1,1,1;1,0,0", 4), ("3,2,1", 6), ("2,2;2,2", 8), ("2,3;1,1", 7), ("3,1,1;1,1,0", 7)]):
    t.append(ty(f"m3-geo-bau-{k}", "Wie viele Würfel sind es? Denk auch an die versteckten Würfel!", "", n, vis=f"bau:{code}"))
L.append(lesson("Bauen mit Würfeln", "🧱", t))

t = []
for k, (code, ans) in enumerate([("parallel", "parallel"), ("senkrecht", "senkrecht"), ("schief", "weder noch"), ("parallel2", "parallel"), ("senkrecht", "senkrecht"), ("schief", "weder noch")]):
    t.append(ch(f"m3-geo-lin-{k}", "Wie liegen die zwei Linien zueinander?", ans, ["parallel", "senkrecht", "weder noch"], vis=f"linien:{code}", keepOrder=True))
for txt, ans in [("Eine Gerade hat keinen Anfang und kein Ende.", "stimmt"), ("Eine Strecke hat zwei Endpunkte.", "stimmt"), ("Parallele Linien treffen sich irgendwann.", "stimmt nicht"),
                 ("Senkrechte Linien bilden einen rechten Winkel.", "stimmt")]:
    t.append(ch(f"m3-geo-gs-{len(t)}", "Stimmt das?", ans, ["stimmt", "stimmt nicht"], prompt=txt, keepOrder=True))
L.append(lesson("Geraden und Strecken", "📏", t))

t = []
for k, (sym, ans) in enumerate([("herz", "ja"), ("schief", "nein"), ("stern", "ja"), ("fahne", "nein"), ("blatt", "ja"), ("stiefel", "nein")]):
    t.append(ch(f"m3-geo-sym-{k}", "Ist die rote Linie eine Spiegelachse?", ans, ["ja", "nein"], vis=f"sym:{sym}", keepOrder=True))
L.append(lesson("Achsensymmetrie", "🦋", t))
L.append(lesson("Ins Heft", "📸", [photo("m3-geo-foto", "Zeichne im Heft ein Würfelnetz auf Kästchenpapier (jede Fläche 2 × 2 Kästchen). Schneide es aus, falte es und mach ein Foto vom Würfel.",
                                            "Zeichne ein Würfelnetz, schneide es aus und falte einen Würfel.", [])]))
L.append(test(12))
units["k3-geometrie"] = unit("m3-geometrie", "Körper, Linien, Symmetrie", "🧊", "#d6457a", L)

# ================= 10. Extras (eher 4. Klasse; Punkt vor Strich ist bei Nathan schon dran, steht deshalb bei Mal und geteilt) =================
L = []
t = []
for a, b in [(12, 4), (15, 3), (13, 5), (16, 2), (11, 7), (14, 6), (17, 3), (18, 5), (19, 4), (12, 8)]:
    t.append(ty(f"m3-ex-g1x1-{a}-{b}", "Großes Einmaleins: Rechne. Tipp: 10 · … und dann den Rest.", f"{b} · {a} =", a * b))
L.append(lesson("Großes Einmaleins", "🚀", t))

t = []
for n, ans, opts in [(24, "4", ["4", "5", "7"]), (35, "7", ["3", "6", "7"]), (36, "9", ["5", "8", "9"]), (40, "8", ["3", "6", "8"]), (27, "3", ["2", "3", "5"]), (42, "6", ["4", "5", "6"])]:
    t.append(ch(f"m3-ex-teiler-{n}", "Welche Zahl ist ein Teiler? (Sie geht ohne Rest auf.)", ans, opts, prompt=str(n), keepOrder=True, bigOptions=True))
for n, ans, opts in [(6, "42", ["32", "42", "44"]), (7, "56", ["54", "56", "47"]), (8, "64", ["62", "64", "68"]), (9, "81", ["81", "82", "91"])]:
    t.append(ch(f"m3-ex-vielf-{n}", f"Welche Zahl ist ein Vielfaches von {n}?", ans, opts, keepOrder=True, bigOptions=True))
L.append(lesson("Vielfache und Teiler", "🔍", t))


t = []
for code, n in [("4x3", 12), ("5x2", 10), ("3x3", 9), ("6x2", 12), ("0,0;1,0;2,0;0,1;0,2", 5), ("0,0;1,0;1,1;2,1;2,2;3,2", 6), ("0,0;1,0;2,0;0,1;1,1;2,1;1,2", 7)]:
    t.append(ty(f"m3-ex-fl-{code}".replace(";", "_").replace(",", ""), "Wie viele Kästchen groß ist die Fläche?", "", n, vis=f"flaeche:{code}"))
for w, h in [(4, 5), (7, 3), (6, 6)]:
    t.append(ty(f"m3-ex-flr-{w}-{h}", "Ein Rechteck ist so viele Kästchen lang und breit. Wie viele Kästchen hat es? Tipp: Länge mal Breite.", f"{w} Kästchen lang, {h} Kästchen breit", w * h))
L.append(lesson("Flächeninhalt", "🟪", t))

t = []
for a, b, ans in [("0,5", 2, "1"), ("0,5", 4, "2"), ("1,5", 2, "3"), ("2,5", 4, "10"), ("0,5", 5, "2,5"), ("1,5", 3, "4,5")]:
    t.append(ty(f"m3-ex-komma-{a}-{b}", "Kommazahlen: 0,5 ist die Hälfte von 1. Rechne.", f"{b} · {a} =", ans, num=False, also=[ans.replace(",", ".")]))
L.append(lesson("Kommazahlen", "🔸", t))
L.append(test(12))
units["k3-extra"] = unit("m3-extra", "Für Profis: schon 4. Klasse", "🚀", "#7b3fe4", L)

for name, u in units.items():
    with open(f"{OUT}/{name}.json", "w", encoding="utf-8") as f:
        json.dump(u, f, ensure_ascii=False, indent=1)
    print(name, sum(len(l.get("tasks", [])) for l in u["lessons"]), "Aufgaben")
