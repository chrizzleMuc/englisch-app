# Erzeugt die Rechenrätsel für die 3. Klasse (inhalte/mathe/k3-raetsel.json):
#  - Rechengitter: Rahmen aus Rechnungen (waagerecht und senkrecht), über Brücken verbunden.
#    Jede Rechnung ist "Zahl Rechenzeichen Zahl = Zahl". Zahlen bis 100, Mal/Geteilt im Einmaleins.
#    Jedes Rätsel ist eindeutig: Es lässt sich Schritt für Schritt lösen, immer mit einer Rechnung,
#    in der nur noch eine Zahl fehlt.
#  - Zahlenschlange: Startzahl, dann Kästchen mit Pfeilen und Rechenschritten (verzweigt).
# Alle Rätsel sind zufällig erzeugt (eigene Rätsel, nichts abgeschrieben).
# Aufruf: python3 werkzeug/gen_raetsel.py
import json, random, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "inhalte/mathe/k3-raetsel.json"
R = random.Random(2111)
OPS = ["+", "-", "·", ":"]


# ---------------- Rechengitter ----------------
# Ein Rahmen ist 5x5: oben, unten, links, rechts je eine Rechnung, Ecken gehören zu zwei Rechnungen.
# Rahmen liegen im Abstand 8; Brücken (3 Felder) verbinden die Mitte zweier Rahmen.
LAYOUTS = {
    "klein": [(0, 0), (1, 0)],                    # zwei Rahmen untereinander
    "mittel": [(0, 0), (1, 0), (1, 1)],           # L-Form
    "gross": [(0, 0), (0, 1), (1, 0), (1, 1)],    # vier Rahmen
}


def layout(frames):
    nums = set()
    eqs = []  # (a, b, c) Zellen; Rechenzeichen-Zelle liegt zwischen a und b
    for fr, fc in frames:
        r0, c0 = fr * 8, fc * 8
        for dr, dc in [(0, 0), (0, 2), (0, 4), (2, 0), (2, 4), (4, 0), (4, 2), (4, 4)]:
            nums.add((r0 + dr, c0 + dc))
        eqs += [
            ((r0, c0), (r0, c0 + 2), (r0, c0 + 4)),
            ((r0 + 4, c0), (r0 + 4, c0 + 2), (r0 + 4, c0 + 4)),
            ((r0, c0), (r0 + 2, c0), (r0 + 4, c0)),
            ((r0, c0 + 4), (r0 + 2, c0 + 4), (r0 + 4, c0 + 4)),
        ]
    fs = set(frames)
    for fr, fc in frames:
        r0, c0 = fr * 8, fc * 8
        if (fr, fc + 1) in fs:  # Brücke nach rechts
            a, b, c = (r0 + 2, c0 + 4), (r0 + 2, c0 + 6), (r0 + 2, c0 + 8)
            nums.add(b)
            eqs.append((a, b, c))
        if (fr + 1, fc) in fs:  # Brücke nach unten
            a, b, c = (r0 + 4, c0 + 2), (r0 + 6, c0 + 2), (r0 + 8, c0 + 2)
            nums.add(b)
            eqs.append((a, b, c))
    rows = max(r for r, _ in nums) + 1
    cols = max(c for _, c in nums) + 1
    return sorted(nums), eqs, rows, cols


def ok_eq(op, a, b, c):
    if min(a, b, c) < 1 or max(a, b, c) > 100:
        return False
    if op == "+":
        return a + b == c
    if op == "-":
        return a - b == c
    if op == "·":
        return 2 <= a <= 10 and 2 <= b <= 10 and a * b == c
    if op == ":":
        return 2 <= b <= 10 and 2 <= c <= 10 and b * c == a
    return False


def derive(op, a, b, c):
    """Fehlt genau eine Zahl (None), wird sie berechnet. Gibt (Index, Wert) oder None zurück."""
    miss = [i for i, x in enumerate((a, b, c)) if x is None]
    if len(miss) != 1:
        return None
    i = miss[0]
    if op == "+":
        v = c - b if i == 0 else c - a if i == 1 else a + b
    elif op == "-":
        v = b + c if i == 0 else a - c if i == 1 else a - b
    elif op == "·":
        if i == 2:
            v = a * b
        else:
            o = b if i == 0 else a
            if o == 0 or c % o:
                return (i, None)
            v = c // o
    else:  # :
        if i == 0:
            v = b * c
        elif i == 1:
            if c == 0 or a % c:
                return (i, None)
            v = a // c
        else:
            if b == 0 or a % b:
                return (i, None)
            v = a // b
    return (i, v)


def fill_grid(nums, eqs):
    """Zahlen und Rechenzeichen zufällig so wählen, dass alle Rechnungen stimmen.
    Sind in einer Rechnung zwei Zahlen bekannt, wird ein passendes Rechenzeichen gewählt
    und die dritte Zahl ausgerechnet; sonst bekommt ein freies Feld eine Zufallszahl."""
    for _ in range(3000):
        val, ops = {}, {}
        bad = False
        while not bad and (len(val) < len(nums) or len(ops) < len(eqs)):
            done_one = False
            for k, (a, b, c) in enumerate(eqs):
                if k in ops:
                    continue
                trip = [val.get(a), val.get(b), val.get(c)]
                kn = 3 - trip.count(None)
                if kn < 2:
                    continue
                choices = []
                for op in OPS:
                    if kn == 3:
                        if ok_eq(op, *trip):
                            choices.append((op, None, None))
                    else:
                        i, v = derive(op, *trip)
                        if v is None:
                            continue
                        t = list(trip)
                        t[i] = v
                        if ok_eq(op, *t):
                            choices.append((op, i, v))
                if not choices:
                    bad = True
                    break
                op, i, v = R.choices(choices, [{"+": 1, "-": 1, "·": 6, ":": 6}[x[0]] for x in choices])[0]
                ops[k] = op
                if i is not None:
                    val[(a, b, c)[i]] = v
                done_one = True
                break
            if bad or done_one:
                continue
            free = [c for c in nums if c not in val]
            if not free:
                bad = True
                break
            cell = R.choice(free)
            val[cell] = R.choice([R.randint(2, 10), R.randint(2, 10), R.randint(11, 60), R.randint(10, 99)])
        if not bad:
            return val, [ops[k] for k in range(len(eqs))]
    return None


def solvable(nums, eqs, ops, sol, givens):
    known = {c: sol[c] for c in givens}
    changed = True
    while changed:
        changed = False
        for k, (a, b, c) in enumerate(eqs):
            trip = [known.get(a), known.get(b), known.get(c)]
            d = derive(ops[k], *trip)
            if d and d[1] is not None:
                cell = (a, b, c)[d[0]]
                assert d[1] == sol[cell]
                known[cell] = d[1]
                changed = True
    return len(known) == len(nums)


def make_grid(size, extra):
    frames = LAYOUTS[size]
    nums, eqs, rows, cols = layout(frames)
    for _ in range(500):
        res = fill_grid(nums, eqs)
        if not res:
            continue
        sol, ops = res
        # Abwechslung: jedes Rechenzeichen mindestens einmal, keins mehr als ein Drittel
        if len(set(ops)) < 4 or max(ops.count(o) for o in OPS) > max(2, len(ops) // 3 + 1):
            continue
        # langweilige Zahlen vermeiden: nicht zu viele gleiche
        if max(list(sol.values()).count(v) for v in sol.values()) > 3:
            continue
        # Vorgaben: so lange aufdecken, bis lösbar, dann Überflüssige weglassen, dann ein paar Hilfen dazu
        cells = list(nums)
        R.shuffle(cells)
        givens = []
        for c in cells:
            givens.append(c)
            if solvable(nums, eqs, ops, sol, givens):
                break
        for c in list(givens):
            t = [g for g in givens if g != c]
            if solvable(nums, eqs, ops, sol, t):
                givens = t
        rest = [c for c in nums if c not in givens]
        R.shuffle(rest)
        givens += rest[:extra]
        # Raster als Liste von Zeilen: "" leer, Rechenzeichen, Zahl (vorgegeben) oder "?Zahl" (zu finden)
        g = [["" for _ in range(cols)] for _ in range(rows)]
        for k, (a, b, c) in enumerate(eqs):
            if a[0] == c[0]:
                g[a[0]][a[1] + 1] = ops[k]
                g[a[0]][a[1] + 3] = "="
            else:
                g[a[0] + 1][a[1]] = ops[k]
                g[a[0] + 3][a[1]] = "="
        for c in nums:
            g[c[0]][c[1]] = (str(sol[c]) if c in givens else "?" + str(sol[c]))
        return g, len(nums) - len(givens)
    raise RuntimeError("kein Gitter gefunden")


# ---------------- Zahlenschlange ----------------
def snake_ops(v, M, prev):
    c = []
    if M == 100:
        for n in range(2, 31):
            if v + n <= 100:
                c.append(("+", n))
            if v - n >= 1:
                c.append(("-", n))
        if v <= 10:
            c += [("·", k) for k in range(2, 11) if v * k <= 100 and v >= 2]
        c += [(":", k) for k in range(2, 11) if v % k == 0 and 2 <= v // k <= 10]
    else:
        adds = list(range(10, 100, 10)) + list(range(100, 500, 100)) + [R.randint(11, 59) for _ in range(6)] + [R.randint(101, 350) for _ in range(3)]
        for n in adds:
            if v + n <= 1000:
                c.append(("+", n))
            if v - n >= 1:
                c.append(("-", n))
        for k in range(2, 11):
            if v * k <= 1000 and (v <= 10 or (v % 10 == 0 and v <= 100) or (v <= 25 and k <= 5) or (v % 100 == 0)):
                c.append(("·", k))
            if v % k == 0 and v // k >= 2 and (
                v <= 100 or (v % 10 == 0 and (v // 10) % k == 0) or (v % 100 == 0 and (v // 100) % k == 0)
            ):
                c.append((":", k))
    # Abwechslung: anderes Rechenzeichen als zuletzt bevorzugen, Mal/Geteilt öfter anbieten
    by = {}
    for o, n in c:
        by.setdefault(o, []).append((o, n))
    keys = [o for o in by if o != prev] or list(by)
    w = {"+": 1, "-": 1, "·": 1.4, ":": 1.6}
    if not keys:
        return None
    o = R.choices(keys, [w[k] for k in keys])[0]
    return R.choices(by[o], [1 if (oo in "·:" and n == 2) else 2.5 if oo in "·:" else 1 for oo, n in by[o]])[0]


def apply(o, v, n):
    return {"+": v + n, "-": v - n, "·": v * n, ":": v // n}[o]


def make_snake(M, w, h, target):
    for _ in range(2000):
        pos = (R.randrange(h), 0) if R.random() < .5 else (0, R.randrange(w))
        start = R.randint(2, 12) if M == 100 else R.choice([R.randint(10, 60), R.randint(2, 9) * 10, R.randint(110, 300)])
        nodes = [[pos[0], pos[1], start]]
        at = {pos: 0}
        edges = []
        prevop = {0: None}
        last = 0
        tries = 0
        while len(nodes) < target and tries < 400:
            tries += 1
            src = last if R.random() < .72 else R.randrange(len(nodes))
            r, c, v = nodes[src]
            free = [(r + dr, c + dc) for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                    if 0 <= r + dr < h and 0 <= c + dc < w and (r + dr, c + dc) not in at]
            if not free:
                continue
            # nicht zu viele Abzweigungen an einem Kästchen
            if sum(1 for e in edges if e[0] == src) >= 2:
                continue
            p = R.choice(free)
            op = snake_ops(v, M, prevop[src])
            if not op:
                continue
            nv = apply(op[0], v, op[1])
            k = len(nodes)
            nodes.append([p[0], p[1], nv])
            at[p] = k
            edges.append([src, k, op[0], op[1]])
            prevop[k] = op[0]
            last = k
        if len(nodes) < target:
            continue
        opsused = {e[2] for e in edges}
        if len(opsused) < 4:
            continue
        # mindestens eine Abzweigung
        if not any(sum(1 for e in edges if e[0] == i) >= 2 for i in range(len(nodes))):
            continue
        # leere Zeilen und Spalten am Rand weglassen, Startzahl bleibt Knoten 0
        r0 = min(n[0] for n in nodes)
        c0 = min(n[1] for n in nodes)
        nodes = [[n[0] - r0, n[1] - c0, n[2]] for n in nodes]
        return nodes, edges
    raise RuntimeError("keine Schlange")


# ---------------- Einheit ----------------
def unit():
    pools = []
    lessons = []
    plan = [
        ("gk", "Rechengitter klein", "🧩", "klein", 10, 2, 2),
        ("gm", "Rechengitter mittel", "🧩", "mittel", 8, 2, 1),
        ("gg", "Rechengitter groß", "🧩", "gross", 6, 2, 1),
    ]
    for key, title, icon, size, count, extra, per in plan:
        for i in range(count):
            g, blanks = make_grid(size, extra)
            pools.append({"kind": "gitter", "id": f"m3-rr-{key}{i + 1}", "task": "Fülle die leeren Kästchen aus. Am Ende drückst du auf Prüfen.", "grid": g})
        lessons.append({"title": title, "icon": icon, "pick": f"m3-rr-{key}", "count": per})
    for key, title, M, w, h, n, count, per in [
        ("s1", "Zahlenschlange bis 100", 100, 4, 5, 12, 10, 2),
        ("s2", "Zahlenschlange bis 1000", 1000, 4, 5, 14, 10, 1),
    ]:
        for i in range(count):
            nodes, edges = make_snake(M, w, h, n)
            pools.append({"kind": "schlange", "id": f"m3-rr-{key}-{i + 1}", "task": "Folge den Pfeilen und rechne. Am Ende drückst du auf Prüfen.",
                          "w": max(x[1] for x in nodes) + 1, "h": max(x[0] for x in nodes) + 1, "nodes": nodes, "edges": edges})
        lessons.append({"title": title, "icon": "🐍", "pick": f"m3-rr-{key}", "count": per})
    return {"id": "m3-raetsel", "type": "schule", "title_de": "Rechenrätsel", "image": "🧩", "color": "#7b3fe4",
            "lessons": lessons, "pool": pools}


if __name__ == "__main__":
    u = unit()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(u, f, ensure_ascii=False, separators=(",", ":"))
    print(OUT, len(u["pool"]), "Rätsel")
