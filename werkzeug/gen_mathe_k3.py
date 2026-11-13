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

for name, u in units.items():
    with open(f"{OUT}/{name}.json", "w", encoding="utf-8") as f:
        json.dump(u, f, ensure_ascii=False, indent=1)
    print(name, sum(len(l.get("tasks", [])) for l in u["lessons"]), "Aufgaben")
