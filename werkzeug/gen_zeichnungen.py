# Erzeugt eigene Zeichnungen (SVG) für den Sachunterricht 3. Klasse:
#   img/zeichnungen/<name>.svg
# Blätter, Früchte, Nadelzweige, Zapfen, Apfel, Giftpflanzen, Planeten, Mondphasen.
# Alles selbst gezeichnet (Formeln und Pfade hier), nichts aus Büchern oder Apps.
# In den Aufgaben werden sie mit [[name]] eingebunden (siehe js/pics.js).
# Neu erzeugen: python3 werkzeug/gen_zeichnungen.py
import math, os, sys, random

OUT = sys.argv[1] if len(sys.argv) > 1 else "img/zeichnungen"
os.makedirs(OUT, exist_ok=True)
ALL = {}


def f(x):
    return f"{x:.1f}".rstrip("0").rstrip(".")


def smooth(pts, closed=True):
    """Catmull-Rom durch die Punkte -> glatter Bézier-Pfad."""
    n = len(pts)
    if n < 3:
        return "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts)
    d = f"M{f(pts[0][0])},{f(pts[0][1])}"
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if closed or i > 0 else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if closed or i + 2 < n else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{f(c1[0])},{f(c1[1])} {f(c2[0])},{f(c2[1])} {f(p2[0])},{f(p2[1])}"
    return d + (" Z" if closed else "")


def poly(pts):
    return "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts) + " Z"


def svg(name, body, defs="", vb="0 0 200 200"):
    ALL[name] = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">'
                 f'<defs>{defs}</defs>{body}</svg>')


def grad(id_, c1, c2, x2="0", y2="1"):
    return f'<linearGradient id="{id_}" x1="0" y1="0" x2="{x2}" y2="{y2}"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>'


def rgrad(id_, c1, c2, cx=".35", cy=".3", r=".75"):
    return f'<radialGradient id="{id_}" cx="{cx}" cy="{cy}" r="{r}"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></radialGradient>'


LEAF = grad("lg", "#8fd16a", "#3e8f3a")
LEAF_D = grad("lgd", "#5fae4e", "#24623a")
VEIN = "#2c6b2c"


def rot(pts, ang, cx, cy):
    a = math.radians(ang)
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def leaf_outline(width_fn, x0, y0, length, n=80, edge=None):
    """Blatt entlang der Mittelrippe von (x0,y0) nach oben. width_fn(t)->halbe Breite, edge(t,side)->Zusatz."""
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        w = width_fn(t)
        if edge: w = max(0, w + edge(t))
        y = y0 - t * length
        left.append((x0 - w, y))
        right.append((x0 + w, y))
    return right + left[::-1]


def veins(x0, y0, length, width_fn, k=6, t0=.1, t1=.85, slope=.5):
    d = f"M{f(x0)},{f(y0 + 2)} L{f(x0)},{f(y0 - length * .97)}"
    for i in range(k):
        t = t0 + (t1 - t0) * i / max(1, k - 1)
        y = y0 - t * length
        w = width_fn(t) * .8
        d += f" M{f(x0)},{f(y)} Q{f(x0 + w * .5)},{f(y - w * slope * .4)} {f(x0 + w)},{f(y - w * slope)}"
        d += f" M{f(x0)},{f(y)} Q{f(x0 - w * .5)},{f(y - w * slope * .4)} {f(x0 - w)},{f(y - w * slope)}"
    return f'<path d="{d}" fill="none" stroke="{VEIN}" stroke-width="2" stroke-linecap="round" opacity=".55"/>'


def stalk(x, y, l=22, c="#5b7a2a"):
    return f'<path d="M{f(x)},{f(y)} L{f(x)},{f(y + l)}" stroke="{c}" stroke-width="5" stroke-linecap="round"/>'


def leaf_svg(name, width_fn, edge=None, length=150, y0=172, k=6, slope=.5, angle=-18, fill="url(#lg)"):
    x0 = 100
    pts = leaf_outline(width_fn, x0, y0, length, edge=edge)
    outline = smooth(pts)
    body = stalk(x0, y0 - 2, 22) + f'<path d="{outline}" fill="{fill}" stroke="#2f6b2a" stroke-width="2.5" stroke-linejoin="round"/>'
    body += f'<g clip-path="url(#lc)">{veins(x0, y0, length, width_fn, k, slope=slope)}</g>'
    svg(name, f'<g transform="rotate({angle} 100 110)">{body}</g>', LEAF + f'<clipPath id="lc"><path d="{outline}"/></clipPath>')


def saw(n, amp, sharp=True):
    """gezackter Rand: n Zähne"""
    def e(t):
        ph = (t * n) % 1
        return amp * (ph if sharp else math.sin(ph * math.pi)) - amp * .5
    return e


# ---------------- Blätter ----------------
# Buche: oval, glatter leicht welliger Rand
leaf_svg("blatt-buche", lambda t: 52 * math.sin(math.pi * t) ** .85 * (1 - .15 * t), edge=lambda t: 2.2 * math.sin(t * 7 * math.pi * 2) * math.sin(math.pi * t), k=7, slope=.9)


# Eiche: breiter oben, runde Buchten, kurzer Stiel
def eiche_w(t):
    base = 50 * (math.sin(math.pi * min(1, t * 1.05)) ** .6) * (.55 + .5 * t) if t < .97 else 0
    lobe = .32 + .68 * abs(math.sin(t * math.pi * 4.6 + .4)) ** .7
    return base * lobe * (1 if t > .04 else t / .04)


leaf_svg("blatt-eiche", eiche_w, length=150, k=5, slope=.6)

# Birke: dreieckig/rautenförmig, gesägt, lange Spitze
leaf_svg("blatt-birke", lambda t: (55 * t / .3 if t < .3 else 55 * (1 - (t - .3) / .7) ** 1.25) * (1 if t > .02 else 0),
         edge=lambda t: (2.5 + 2.5 * ((t * 14) % 1)) * (1 if .05 < t < .95 else 0) - 2.5, length=140, y0=165, k=5, slope=.7)


# Linde: herzförmig mit Spitze, fein gesägt
def linde_svg():
    pts = []
    for i in range(121):
        a = i / 120 * 2 * math.pi
        # Herzkurve, oben spitz
        x = 16 * math.sin(a) ** 3
        y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        r = 1 + .025 * ((i * 1.0) % 3 - 1)
        pts.append((100 + x * 4.6 * r, 95 - y * 4.6 * r))
    # Herz umdrehen: Einbuchtung unten am Stiel, Spitze oben
    pts = [(x, 190 - y) for x, y in pts]
    body = stalk(100, 152, 30) + f'<path d="{smooth(pts)}" fill="url(#lg)" stroke="#2f6b2a" stroke-width="2.5"/>'
    d = "M100,150 L100,45"
    for t, s in [(.15, 1), (.35, 1), (.55, 1), (.75, 1)]:
        y = 150 - t * 105
        d += f" M100,{f(y)} Q{f(100 + 30)},{f(y - 12)} {f(100 + 58 * (1 - t * .6))},{f(y - 26)}"
        d += f" M100,{f(y)} Q{f(100 - 30)},{f(y - 12)} {f(100 - 58 * (1 - t * .6))},{f(y - 26)}"
    body += f'<path d="{d}" fill="none" stroke="{VEIN}" stroke-width="2" opacity=".55" stroke-linecap="round"/>'
    svg("blatt-linde", f'<g transform="rotate(-15 100 105)">{body}</g>', LEAF)


linde_svg()


# Ahorn: Hand mit 5 spitzen Zipfeln
def ahorn_svg():
    cx, cy = 100, 118
    lobes = [(-90, 78), (-35, 70), (-145, 70), (15, 48), (165, 48)]
    pts = []
    N = 360
    for i in range(N):
        ang = -180 + 360 * i / N
        r = 22
        for la, ll in lobes:
            dlt = (ang - la + 180) % 360 - 180
            r = max(r, ll * max(0, 1 - abs(dlt) / 24) ** 1.6 + 22)
            # kleine Nebenzacken
            for off in (-14, 14):
                dd = (ang - (la + off) + 180) % 360 - 180
                r = max(r, (ll * .62) * max(0, 1 - abs(dd) / 7) ** 1.2 + 22)
        if 60 < ang < 120: r = min(r, 18)
        pts.append((cx + r * math.cos(math.radians(ang)), cy + r * math.sin(math.radians(ang))))
    body = f'<path d="M100,135 L100,192" stroke="#8a5a2b" stroke-width="5" stroke-linecap="round"/>'
    body += f'<path d="{poly(pts)}" fill="url(#lg)" stroke="#2f6b2a" stroke-width="2.5" stroke-linejoin="round"/>'
    d = "".join(f"M{cx},{cy + 10} L{f(cx + ll * .95 * math.cos(math.radians(la)))},{f(cy + ll * .95 * math.sin(math.radians(la)))} " for la, ll in lobes)
    body += f'<path d="{d}" fill="none" stroke="{VEIN}" stroke-width="2" opacity=".55" stroke-linecap="round"/>'
    svg("blatt-ahorn", body, LEAF)


ahorn_svg()


def leaflet(x0, y0, length, width, ang, serr=True, fill="url(#lg)"):
    wf = lambda t: width * math.sin(math.pi * t) ** .7 * (1 - .2 * t)
    e = (lambda t: (1.2 + 1.6 * ((t * 12) % 1)) * (1 if .1 < t < .92 else 0) - 1.4) if serr else None
    pts = rot(leaf_outline(wf, x0, y0, length, n=60, edge=e), ang, x0, y0)
    mid = rot([(x0, y0), (x0, y0 - length * .95)], ang, x0, y0)
    return (f'<path d="{smooth(pts)}" fill="{fill}" stroke="#2f6b2a" stroke-width="2" stroke-linejoin="round"/>'
            f'<path d="M{f(mid[0][0])},{f(mid[0][1])} L{f(mid[1][0])},{f(mid[1][1])}" stroke="{VEIN}" stroke-width="1.6" opacity=".55"/>')


# Rosskastanie: 7 Finger von einem Punkt
def kastanie_blatt():
    cx, cy = 100, 128
    body = f'<path d="M{cx},{cy} L{cx},{cy + 66}" stroke="#5b7a2a" stroke-width="6" stroke-linecap="round"/>'
    for ang, l in [(-92, 46), (92, 46), (-60, 70), (60, 70), (-29, 88), (29, 88), (0, 98)]:
        body += leaflet(cx, cy, l, l * .22, ang)
    svg("blatt-kastanie", body, LEAF)


kastanie_blatt()


# Eberesche: gefiedert
def eberesche_blatt():
    body = '<path d="M100,190 L100,30" stroke="#6b7a2a" stroke-width="4" stroke-linecap="round"/>'
    for i in range(6):
        y = 168 - i * 23
        body += leaflet(100, y, 50, 11, 72) + leaflet(100, y, 50, 11, -72)
    body += leaflet(100, 34, 44, 11, 0)
    svg("blatt-eberesche", f'<g transform="rotate(-20 100 110)">{body}</g>', LEAF)


eberesche_blatt()


# ---------------- Früchte ----------------
def eichel():
    defs = rgrad("nut", "#d9a35a", "#8a5523") + grad("cup", "#b58b52", "#6e4e25")
    body = '<path d="M100,40 Q104,28 112,22" stroke="#6e4e25" stroke-width="5" fill="none" stroke-linecap="round"/>'
    body += '<ellipse cx="100" cy="120" rx="36" ry="56" fill="url(#nut)" stroke="#6b3f17" stroke-width="2.5"/>'
    body += '<path d="M100,178 l0,6" stroke="#6b3f17" stroke-width="4" stroke-linecap="round"/>'
    body += '<path d="M58,88 Q58,44 100,42 Q142,44 142,88 Q100,100 58,88 Z" fill="url(#cup)" stroke="#5a3d1a" stroke-width="2.5"/>'
    d = ""
    for r in range(3):
        for c in range(8):
            x = 66 + c * 10 + (5 if r % 2 else 0)
            y = 56 + r * 11
            if 60 < x < 140: d += f"M{x - 4},{y + 3} q4,-7 8,0 "
    body += f'<path d="{d}" fill="none" stroke="#5a3d1a" stroke-width="1.6" opacity=".7"/>'
    body += '<ellipse cx="86" cy="125" rx="8" ry="20" fill="#fff" opacity=".25"/>'
    svg("frucht-eichel", body, defs)


eichel()


def buchecker():
    defs = rgrad("bh", "#b07a3c", "#6e4520") + grad("bn", "#a8683a", "#5c3416")
    body = ""
    # geöffnete Hülle: 4 Klappen
    for ang in (-60, -20, 20, 60):
        pts = rot([(100, 150), (84, 100), (100, 60), (116, 100)], ang, 100, 150)
        body += f'<path d="{smooth(pts)}" fill="url(#bh)" stroke="#55361a" stroke-width="2"/>'
        for k in range(6):
            q = rot([(100 + random.uniform(-9, 9), 75 + k * 11)], ang, 100, 150)[0]
            body += f'<path d="M{f(q[0])},{f(q[1])} l{f(random.uniform(-6, 6))},{f(random.uniform(-7, -3))}" stroke="#55361a" stroke-width="1.6" stroke-linecap="round"/>'
    # zwei dreikantige Nüsse
    body += '<path d="M78,150 L92,92 L104,150 Z" fill="url(#bn)" stroke="#3e230d" stroke-width="2.5" stroke-linejoin="round"/>'
    body += '<path d="M98,150 L112,90 L124,150 Z" fill="url(#bn)" stroke="#3e230d" stroke-width="2.5" stroke-linejoin="round"/>'
    body += '<path d="M92,92 L91,150 M112,90 L111,150" stroke="#e0b07a" stroke-width="2" opacity=".6"/>'
    body += '<path d="M100,150 L100,182" stroke="#6e4520" stroke-width="5" stroke-linecap="round"/>'
    svg("frucht-buchecker", body, defs)


random.seed(4)
buchecker()


def ahorn_frucht():
    defs = grad("wing", "#e2d27a", "#a8964a")
    body = ""
    for s in (1, -1):
        body += (f'<path d="M100,125 Q{100 + s * 20},{118} {100 + s * 40},{95} Q{100 + s * 75},{58} {100 + s * 80},{40} '
                 f'Q{100 + s * 58},{48} {100 + s * 30},{78} Q{100 + s * 18},{95} 100,112 Z" fill="url(#wing)" stroke="#7d6a2a" stroke-width="2"/>')
        body += f'<path d="M{100 + s * 18},{110} Q{100 + s * 45},{80} {100 + s * 74},{46}" stroke="#7d6a2a" stroke-width="1.4" fill="none" opacity=".6"/>'
        body += f'<ellipse cx="{100 + s * 12}" cy="120" rx="13" ry="10" fill="#9b7a3a" stroke="#5e4618" stroke-width="2"/>'
    body += '<path d="M100,128 Q98,160 104,186" stroke="#7d6a2a" stroke-width="3.5" fill="none" stroke-linecap="round"/>'
    svg("frucht-ahorn", body, defs)


ahorn_frucht()


def vogelbeeren():
    defs = rgrad("vb", "#ffb15c", "#d8431c")
    random.seed(7)
    body = '<path d="M100,24 L100,60" stroke="#6b5a2a" stroke-width="4"/>'
    berries = []
    for i in range(26):
        a = random.uniform(0, 2 * math.pi); r = random.uniform(0, 1) ** .6 * 62
        berries.append((100 + r * math.cos(a), 112 + r * math.sin(a) * .75))
    for x, y in berries:
        body += f'<path d="M100,60 Q{f((x + 100) / 2)},{f(70)} {f(x)},{f(y)}" stroke="#6b5a2a" stroke-width="1.6" fill="none"/>'
    for x, y in sorted(berries, key=lambda b: b[1]):
        body += f'<circle cx="{f(x)}" cy="{f(y)}" r="11" fill="url(#vb)" stroke="#9b2a10" stroke-width="1.6"/><circle cx="{f(x)}" cy="{f(y + 8)}" r="2" fill="#5a1a08"/>'
    svg("frucht-vogelbeeren", body, defs)


vogelbeeren()


def kastanie_frucht():
    defs = grad("sh", "#9fd66a", "#4f8f2a") + rgrad("ka", "#b9622e", "#4a1d08")
    random.seed(2)
    body = '<path d="M30,150 Q40,95 85,92 Q90,140 70,170 Q45,178 30,150 Z" fill="url(#sh)" stroke="#3d6b1f" stroke-width="2.5"/>'
    body += '<path d="M38,148 Q48,108 80,104 Q82,140 66,160 Z" fill="#f4f0d8"/>'
    for i in range(14):
        a = random.uniform(-2.6, -.2)
        x, y = 58 + 34 * math.cos(a), 135 + 40 * math.sin(a)
        body += f'<path d="M{f(x)},{f(y)} l{f(10 * math.cos(a))},{f(10 * math.sin(a))}" stroke="#3d6b1f" stroke-width="2" stroke-linecap="round"/>'
    body += '<path d="M120,60 Q172,58 174,112 Q176,166 126,170 Q80,168 82,118 Q84,64 120,60 Z" fill="url(#ka)" stroke="#3a1606" stroke-width="2.5"/>'
    body += '<path d="M92,142 Q126,172 164,142 Q160,166 126,168 Q96,166 92,142 Z" fill="#d9c49a" opacity=".95"/>'
    body += '<ellipse cx="108" cy="90" rx="12" ry="7" fill="#fff" opacity=".35" transform="rotate(-30 108 90)"/>'
    svg("frucht-kastanie", body, defs)


kastanie_frucht()


# ---------------- Nadelzweige ----------------
def twig(body_needles, defs=""):
    return '<path d="M30,170 Q100,110 172,40" stroke="#7a5230" stroke-width="7" fill="none" stroke-linecap="round"/>' + body_needles


def along(n, t0=.05, t1=.97):
    for i in range(n):
        t = t0 + (t1 - t0) * i / (n - 1)
        # Punkt auf Q-Kurve
        x = (1 - t) ** 2 * 30 + 2 * (1 - t) * t * 100 + t * t * 172
        y = (1 - t) ** 2 * 170 + 2 * (1 - t) * t * 110 + t * t * 40
        dx = 2 * (1 - t) * (70) + 2 * t * (72)
        dy = 2 * (1 - t) * (-60) + 2 * t * (-70)
        ang = math.degrees(math.atan2(dy, dx))
        yield t, x, y, ang


def fichte_zweig():
    body = ""
    random.seed(1)
    for t, x, y, ang in along(34):
        for k in range(5):
            a = math.radians(ang + random.choice([-1, 1]) * random.uniform(35, 120))
            l = 16 + random.uniform(-2, 3)
            body += f'<path d="M{f(x)},{f(y)} l{f(l * math.cos(a))},{f(l * math.sin(a))}" stroke="{random.choice(["#2f6b3a", "#25593a", "#3c7d42"])}" stroke-width="3.2" stroke-linecap="round"/>'
    svg("zweig-fichte", twig(body))


def tanne_zweig():
    body = ""
    for t, x, y, ang in along(30):
        for s in (1, -1):
            a = math.radians(ang + s * 75)
            l = 22
            x2, y2 = x + l * math.cos(a), y + l * math.sin(a)
            body += f'<path d="M{f(x)},{f(y)} L{f(x2)},{f(y2)}" stroke="#2e6b3a" stroke-width="6" stroke-linecap="round"/>'
            body += f'<path d="M{f(x + 5 * math.cos(a))},{f(y + 5 * math.sin(a))} L{f(x2 - 2 * math.cos(a))},{f(y2 - 2 * math.sin(a))}" stroke="#cfe8d4" stroke-width="1.4" stroke-linecap="round" opacity=".9"/>'
    svg("zweig-tanne", twig(body))


def kiefer_zweig():
    body = ""
    random.seed(3)
    for t, x, y, ang in along(16, .05, .9):
        for s in (1, -1):
            a = math.radians(ang + s * random.uniform(25, 55))
            for dd in (-5, 5):
                b = a + math.radians(dd)
                body += f'<path d="M{f(x)},{f(y)} q{f(20 * math.cos(b) + 4)},{f(20 * math.sin(b))} {f(48 * math.cos(b))},{f(48 * math.sin(b))}" fill="none" stroke="#3d7a4a" stroke-width="3" stroke-linecap="round"/>'
    # Endbüschel
    for k in range(8):
        a = math.radians(-60 + k * 9)
        body += f'<path d="M172,40 l{f(44 * math.cos(a))},{f(44 * math.sin(a))}" stroke="#3d7a4a" stroke-width="3" stroke-linecap="round"/>'
    svg("zweig-kiefer", twig(body))


def laerche_zweig():
    body = ""
    for t, x, y, ang in along(7, .1, .95):
        body += f'<circle cx="{f(x)}" cy="{f(y)}" r="5" fill="#8a6a40"/>'
        for k in range(15):
            a = math.radians(ang - 90 + (k - 7) * 13)
            l = 24
            body += f'<path d="M{f(x)},{f(y)} l{f(l * math.cos(a))},{f(l * math.sin(a))}" stroke="#8cc45a" stroke-width="2.6" stroke-linecap="round"/>'
    svg("zweig-laerche", twig(body))


def eibe_zweig():
    defs = rgrad("ar", "#ff6b6b", "#c01818")
    body = ""
    for t, x, y, ang in along(26):
        for s in (1, -1):
            a = math.radians(ang + s * 80)
            body += f'<path d="M{f(x)},{f(y)} l{f(20 * math.cos(a))},{f(20 * math.sin(a))}" stroke="#1f4d2e" stroke-width="5.5" stroke-linecap="round"/>'
    for (x, y) in [(78, 150), (118, 118), (150, 88)]:
        body += f'<path d="M{x},{y - 18} l0,12" stroke="#1f4d2e" stroke-width="3"/><circle cx="{x}" cy="{y}" r="13" fill="url(#ar)" stroke="#8a0f0f" stroke-width="2"/><circle cx="{x}" cy="{y + 2}" r="5" fill="#3a2a1a"/>'
    svg("zweig-eibe", twig(body), defs)


fichte_zweig(); tanne_zweig(); kiefer_zweig(); laerche_zweig(); eibe_zweig()


# ---------------- Zapfen ----------------
def scales(cx, top, bottom, wmax, rows, color1, color2, shape="round"):
    out = ""
    for r in range(rows):
        t = r / (rows - 1)
        y = top + (bottom - top) * t
        w = wmax * (math.sin(math.pi * (.12 + .82 * t)) ** .7)
        n = 4 if w > wmax * .5 else 3
        for c in range(n):
            x = cx - w + (2 * w) * (c + .5 * (r % 2)) / n
            if abs(x - cx) > w * .95: continue
            col = color1 if (r + c) % 2 else color2
            if shape == "round":
                out += f'<path d="M{f(x - 10)},{f(y)} Q{f(x)},{f(y + 16)} {f(x + 10)},{f(y)} Z" fill="{col}" stroke="#4a2c12" stroke-width="1.6"/>'
            else:
                out += f'<path d="M{f(x)},{f(y - 9)} L{f(x + 10)},{f(y)} L{f(x)},{f(y + 9)} L{f(x - 10)},{f(y)} Z" fill="{col}" stroke="#4a2c12" stroke-width="1.6"/>'
    return out


def zapfen_fichte():
    body = '<path d="M60,14 Q100,24 140,12" stroke="#7a5230" stroke-width="7" fill="none" stroke-linecap="round"/><path d="M100,20 L100,34" stroke="#7a5230" stroke-width="6"/>'
    body += '<path d="M100,30 Q70,60 74,120 Q80,180 100,192 Q120,180 126,120 Q130,60 100,30 Z" fill="#9c6a35" stroke="#4a2c12" stroke-width="2.5"/>'
    body += scales(100, 44, 182, 26, 14, "#b07a40", "#8a5628")
    svg("zapfen-fichte", body)


def zapfen_tanne():
    body = '<path d="M20,175 Q100,160 182,176" stroke="#7a5230" stroke-width="8" fill="none" stroke-linecap="round"/>'
    for x in range(26, 180, 9):
        body += f'<path d="M{x},{170 if 50 < x < 150 else 173} l-6,18 M{x},{170} l6,18" stroke="#2e6b3a" stroke-width="4" stroke-linecap="round"/>'
    body += '<path d="M100,166 Q72,150 74,96 Q76,32 100,20 Q124,32 126,96 Q128,150 100,166 Z" fill="#8b6a52" stroke="#4a2c12" stroke-width="2.5"/>'
    body += scales(100, 34, 156, 24, 12, "#9d7c5c", "#7b5a40")
    svg("zapfen-tanne", body)


def zapfen_kiefer():
    body = '<path d="M100,30 L100,52" stroke="#7a5230" stroke-width="6" stroke-linecap="round"/>'
    body += '<path d="M100,50 Q56,70 60,120 Q66,170 100,176 Q134,170 140,120 Q144,70 100,50 Z" fill="#8e6236" stroke="#4a2c12" stroke-width="2.5"/>'
    body += scales(100, 66, 166, 34, 8, "#a67444", "#7d5228", shape="diamond")
    svg("zapfen-kiefer", body)


zapfen_fichte(); zapfen_tanne(); zapfen_kiefer()


# ---------------- Apfel ----------------
def apfel_laengs():
    defs = grad("ap", "#ff6a5e", "#c0261c", "1", "1")
    body = '<path d="M100,40 C70,20 26,32 24,88 C22,146 60,186 100,178 C140,186 178,146 176,88 C174,32 130,20 100,40 Z" fill="url(#ap)"/>'
    body += '<path d="M100,46 C72,30 33,40 32,90 C31,140 64,176 100,170 C136,176 169,140 168,90 C167,40 128,30 100,46 Z" fill="#fbf1c8"/>'
    # Kerngehäuse
    body += '<path d="M100,72 C78,82 74,112 86,134 C92,142 108,142 114,134 C126,112 122,82 100,72 Z" fill="#efe0a2" stroke="#d6c27a" stroke-width="2"/>'
    for s in (1, -1):
        body += f'<ellipse cx="{100 + s * 10}" cy="106" rx="6" ry="11" fill="#5a2e12" transform="rotate({s * 14} {100 + s * 10} 106)"/>'
    body += '<path d="M100,46 L100,72 M100,140 L100,166" stroke="#d6c27a" stroke-width="2"/>'
    body += '<path d="M100,44 Q98,22 108,10" stroke="#6b3f17" stroke-width="5" fill="none" stroke-linecap="round"/>'
    body += '<path d="M92,174 l4,8 l4,-6 l4,6 l4,-8" stroke="#5a3d1a" stroke-width="2.4" fill="none" stroke-linejoin="round"/>'
    body += '<path d="M108,22 Q140,4 156,22 Q130,34 108,22 Z" fill="#5fae4e" stroke="#2f6b2a" stroke-width="2"/>'
    svg("apfel-laengs", body, defs)


def apfel_quer():
    defs = grad("ap2", "#ff6a5e", "#c0261c", "1", "1")
    body = '<circle cx="100" cy="100" r="80" fill="url(#ap2)"/><circle cx="100" cy="100" r="73" fill="#fbf1c8"/>'
    star = []
    for i in range(10):
        a = math.radians(-90 + i * 36)
        r = 36 if i % 2 == 0 else 14
        star.append((100 + r * math.cos(a), 100 + r * math.sin(a)))
    body += f'<path d="{smooth(star)}" fill="#efe0a2" stroke="#d6c27a" stroke-width="2.5"/>'
    for i in range(5):
        a = math.radians(-90 + i * 72)
        x, y = 100 + 22 * math.cos(a), 100 + 22 * math.sin(a)
        body += f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="5" ry="9" fill="#5a2e12" transform="rotate({i * 72} {f(x)} {f(y)})"/>'
    svg("apfel-quer", body, defs)


apfel_laengs(); apfel_quer()


# ---------------- Pflanze und Keimung ----------------
def soil(y=150):
    return f'<rect x="0" y="{y}" width="200" height="{200 - y}" rx="10" fill="#9a6b4a"/><path d="M0,{y} H200" stroke="#7a4f32" stroke-width="3"/>'


def bohne(stage):
    defs = LEAF
    body = soil()
    seed = '<ellipse cx="100" cy="{y}" rx="{rx}" ry="{ry}" fill="#f1e2c0" stroke="#a08460" stroke-width="2"/>'
    if stage == 1:
        body += seed.format(y=172, rx=16, ry=10)
    if stage == 2:
        body += seed.format(y=170, rx=21, ry=14) + '<path d="M96,164 Q94,160 96,156" stroke="#a08460" stroke-width="2" fill="none"/>'
    if stage >= 3:
        body += seed.format(y=164, rx=20, ry=13) if stage == 3 else ""
        body += '<path d="M100,170 Q96,184 100,196 M100,180 l-10,10 M100,184 l9,8" stroke="#f3ead2" stroke-width="3" fill="none" stroke-linecap="round"/>'
    if stage == 4:
        body += '<path d="M100,170 Q100,140 100,118 Q100,100 112,96" stroke="#7cba4f" stroke-width="6" fill="none" stroke-linecap="round"/>'
        body += '<ellipse cx="88" cy="150" rx="12" ry="8" fill="#f1e2c0" stroke="#a08460" stroke-width="2"/>'
    if stage == 5:
        body += '<path d="M100,172 L100,70" stroke="#6aa944" stroke-width="7" stroke-linecap="round"/>'
        body += leaflet(100, 82, 56, 18, -55) + leaflet(100, 82, 56, 18, 55)
        body += leaflet(100, 70, 42, 14, 0)
    svg(f"bohne-{stage}", body, defs)


for s in range(1, 6): bohne(s)


def bluetenpflanze():
    defs = LEAF + grad("pet", "#ff8ab0", "#d0357a")
    body = soil(140)
    body += '<path d="M100,150 Q90,170 76,190 M100,150 Q104,175 98,196 M100,150 Q114,168 128,186 M90,172 l-12,4 M112,172 l10,6" stroke="#f3ead2" stroke-width="3" fill="none" stroke-linecap="round"/>'
    body += '<path d="M100,150 L100,64" stroke="#5c9e3a" stroke-width="7" stroke-linecap="round"/>'
    body += leaflet(100, 128, 54, 15, -50) + leaflet(100, 112, 50, 14, 52)
    for i in range(6):
        a = i * 60
        body += f'<ellipse cx="100" cy="36" rx="12" ry="24" fill="url(#pet)" stroke="#a02560" stroke-width="1.6" transform="rotate({a} 100 58)"/>'
    body += '<circle cx="100" cy="58" r="12" fill="#ffd24a" stroke="#c99a10" stroke-width="2"/>'
    svg("bluetenpflanze", body, defs)


bluetenpflanze()


# ---------------- Giftpflanzen ----------------
def maigloeckchen():
    defs = LEAF
    body = leaflet(92, 192, 165, 34, -10) + leaflet(108, 192, 150, 30, 12)
    body += '<path d="M100,192 Q92,120 120,46" stroke="#5c9e3a" stroke-width="4" fill="none" stroke-linecap="round"/>'
    for i, (x, y) in enumerate([(116, 58), (110, 76), (104, 94), (100, 112), (98, 130)]):
        body += f'<path d="M{x},{y} q14,2 18,10" stroke="#5c9e3a" stroke-width="2.4" fill="none"/>'
        cx, cy = x + 18, y + 16
        body += f'<path d="M{cx - 9},{cy + 6} Q{cx - 10},{cy - 8} {cx},{cy - 8} Q{cx + 10},{cy - 8} {cx + 9},{cy + 6} q-3,-3 -6,1 q-3,-4 -6,0 q-3,-4 -6,-1 Z" fill="#fff" stroke="#b9c7b0" stroke-width="1.6"/>'
    svg("gift-maigloeckchen", body, defs)


def baerlauch():
    defs = LEAF
    body = leaflet(90, 192, 160, 30, -14) + leaflet(110, 192, 150, 28, 16)
    body += '<path d="M100,192 L100,52" stroke="#6aa944" stroke-width="4"/>'
    for i in range(9):
        a = math.radians(-90 + (i - 4) * 20)
        x, y = 100 + 34 * math.cos(a), 56 + 34 * math.sin(a) + 26
        body += f'<path d="M100,56 L{f(x)},{f(y - 10)}" stroke="#6aa944" stroke-width="1.6"/>'
        for k in range(6):
            b = math.radians(k * 60)
            body += f'<ellipse cx="{f(x + 5 * math.cos(b))}" cy="{f(y - 10 + 5 * math.sin(b))}" rx="4" ry="2.2" fill="#fff" stroke="#c9d6c0" stroke-width=".8" transform="rotate({k * 60} {f(x + 5 * math.cos(b))} {f(y - 10 + 5 * math.sin(b))})"/>'
    svg("baerlauch", body, defs)


def fingerhut():
    defs = LEAF + grad("fh", "#d68ae6", "#8a2fa8")
    body = '<path d="M100,196 L100,20" stroke="#5c9e3a" stroke-width="5" stroke-linecap="round"/>'
    body += leaflet(100, 196, 70, 18, -60) + leaflet(100, 196, 70, 18, 60)
    for i in range(7):
        y = 38 + i * 19
        s = 1 if i % 2 else -1
        body += f'<path d="M100,{y} q{s * 10},0 {s * 16},8" stroke="#5c9e3a" stroke-width="2.4" fill="none"/>'
        x = 100 + s * 28
        body += f'<path d="M{x - 10},{y + 4} Q{x},{y - 2} {x + 10},{y + 4} L{x + 13},{y + 26} Q{x},{y + 31} {x - 13},{y + 26} Z" fill="url(#fh)" stroke="#6a1f84" stroke-width="1.8"/>'
        body += f'<circle cx="{x - 3}" cy="{y + 21}" r="1.6" fill="#3a0a4a"/><circle cx="{x + 3}" cy="{y + 18}" r="1.6" fill="#3a0a4a"/>'
    svg("gift-fingerhut", body, defs)


def eisenhut():
    defs = LEAF + grad("eh", "#7a8cff", "#2a2fa8")
    body = '<path d="M100,196 L100,18" stroke="#3f7a2a" stroke-width="5" stroke-linecap="round"/>'
    for ang in (-70, -35, 0, 35, 70):
        body += leaflet(100, 192, 42, 8, ang)
    for i in range(6):
        y = 30 + i * 22
        s = 1 if i % 2 else -1
        x = 100 + s * 20
        body += f'<path d="M100,{y + 8} L{x},{y + 8}" stroke="#3f7a2a" stroke-width="2.4"/>'
        body += f'<path d="M{x - 13},{y + 18} Q{x - 14},{y - 6} {x + 2},{y - 4} Q{x + 14},{y} {x + 13},{y + 18} Q{x},{y + 12} {x - 13},{y + 18} Z" fill="url(#eh)" stroke="#1c1f78" stroke-width="1.8"/>'
        body += f'<path d="M{x - 10},{y + 18} q4,8 10,0 q6,8 10,0" fill="url(#eh)" stroke="#1c1f78" stroke-width="1.5"/>'
    svg("gift-eisenhut", body, defs)


def herbstzeitlose():
    defs = grad("hz", "#e4c6f2", "#a26ad0")
    body = '<rect x="0" y="160" width="200" height="40" rx="10" fill="#8cc45a"/>'
    for x, h, a in [(78, 120, -8), (124, 100, 10)]:
        body += f'<g transform="rotate({a} {x} 175)"><path d="M{x},175 L{x},{175 - h + 40}" stroke="#f3ecf7" stroke-width="7" stroke-linecap="round"/>'
        for k, ang in enumerate((-22, 0, 22, -10, 10, 0)):
            body += f'<ellipse cx="{x}" cy="{175 - h + 16}" rx="10" ry="26" fill="url(#hz)" stroke="#7a3fa8" stroke-width="1.6" transform="rotate({ang} {x} {175 - h + 40})"/>'
        body += '</g>'
    svg("gift-herbstzeitlose", body, defs)


def tollkirsche():
    defs = LEAF + rgrad("tk", "#5a5a6a", "#0a0a12")
    body = leaflet(100, 120, 80, 26, -60) + leaflet(100, 120, 80, 26, 60) + leaflet(100, 120, 70, 22, 0)
    body += '<path d="M100,120 L100,140" stroke="#3f7a2a" stroke-width="4"/>'
    for k in range(5):
        a = math.radians(90 + (k - 2) * 40)
        body += f'<path d="M100,150 L{f(100 + 30 * math.cos(a))},{f(150 + 26 * math.sin(a) - 22)}" stroke="#3f7a2a" stroke-width="7" stroke-linecap="round"/>'
    body += '<circle cx="100" cy="160" r="26" fill="url(#tk)" stroke="#000" stroke-width="2"/><ellipse cx="91" cy="150" rx="7" ry="4" fill="#fff" opacity=".7"/>'
    svg("gift-tollkirsche", body, defs)


def goldregen():
    defs = grad("gr", "#fff07a", "#e0b000")
    body = '<path d="M10,26 Q100,10 190,30" stroke="#6e5530" stroke-width="7" fill="none" stroke-linecap="round"/>'
    for x0 in (50, 100, 150):
        body += f'<path d="M{x0},22 Q{x0 + 4},100 {x0 - 2},186" stroke="#7a8a3a" stroke-width="2.5" fill="none"/>'
        for i in range(10):
            y = 36 + i * 15
            s = 1 if i % 2 else -1
            r = 11 - i * .5
            body += f'<path d="M{x0 + s * 2},{y} q{s * r},{-r * .2} {s * r * 1.2},{r} q{-s * r * .8},{r * .6} {-s * r * 1.2},0 Z" fill="url(#gr)" stroke="#b08a00" stroke-width="1.2"/>'
    svg("gift-goldregen", body, defs)


def pfaffenhuetchen():
    defs = grad("ph", "#ff9ad0", "#d0408a")
    body = '<path d="M20,40 Q100,30 180,50" stroke="#5a7a3a" stroke-width="6" fill="none" stroke-linecap="round"/>'
    for x, y in [(60, 110), (124, 92), (150, 150)]:
        body += f'<path d="M{x},{y - 30} L{x},{y - 70 + (y - 92) * .1}" stroke="#5a7a3a" stroke-width="3"/>'
        for k in range(4):
            a = k * 90 + 45
            body += f'<ellipse cx="{x}" cy="{y - 14}" rx="12" ry="16" fill="url(#ph)" stroke="#9a1f5a" stroke-width="1.8" transform="rotate({a} {x} {y})"/>'
        body += f'<circle cx="{x}" cy="{y}" r="9" fill="#ff8a1a" stroke="#b05a00" stroke-width="1.6"/>'
    svg("gift-pfaffenhuetchen", body, defs)


def aronstab():
    defs = LEAF + rgrad("as", "#ff7a5a", "#c4200c")
    body = '<path d="M100,196 L100,50" stroke="#5c9e3a" stroke-width="7" stroke-linecap="round"/>'
    random.seed(9)
    for r in range(9):
        for c in range(3):
            y = 58 + r * 12
            x = 100 + (c - 1) * 13 + (6 if r % 2 else 0) - 3
            body += f'<circle cx="{x}" cy="{y}" r="8" fill="url(#as)" stroke="#8a1406" stroke-width="1.4"/>'
    svg("gift-aronstab", body, defs)


maigloeckchen(); baerlauch(); fingerhut(); eisenhut(); herbstzeitlose(); tollkirsche(); goldregen(); pfaffenhuetchen(); aronstab()


# ---------------- Sonne, Planeten, Mond ----------------
def planet(name, r, c1, c2, extra="", rings=False, bands=None):
    defs = rgrad("pg", c1, c2, ".38", ".32", ".8") + f'<clipPath id="pc"><circle cx="100" cy="100" r="{r}"/></clipPath>'
    body = ""
    if rings:
        body += f'<ellipse cx="100" cy="100" rx="{r * 1.9}" ry="{r * .5}" fill="none" stroke="#d9c08a" stroke-width="10" transform="rotate(-18 100 100)"/>'
        body += f'<ellipse cx="100" cy="100" rx="{r * 1.6}" ry="{r * .4}" fill="none" stroke="#b49a68" stroke-width="5" transform="rotate(-18 100 100)"/>'
    body += f'<circle cx="100" cy="100" r="{r}" fill="url(#pg)"/>'
    if bands:
        g = '<g clip-path="url(#pc)" opacity=".55">'
        for y, h, c in bands:
            g += f'<path d="M0,{100 + y * r} Q100,{100 + y * r + 6} 200,{100 + y * r} L200,{100 + y * r + h * r} Q100,{100 + y * r + h * r + 6} 0,{100 + y * r + h * r} Z" fill="{c}"/>'
        body += g + '</g>'
    body += f'<g clip-path="url(#pc)">{extra}</g>'
    if rings:
        body += f'<path d="M{100 - r * 1.9},{100} A{r * 1.9},{r * .5} 0 0 0 {100 + r * 1.9},100" fill="none" stroke="#d9c08a" stroke-width="10" transform="rotate(-18 100 100)"/>'
    body += f'<circle cx="100" cy="100" r="{r}" fill="none" stroke="#000" stroke-opacity=".25" stroke-width="2"/>'
    svg(name, body, defs)


def sonne():
    defs = rgrad("sg", "#fff6a0", "#ff9a1a", ".4", ".38", ".7")
    body = ""
    for i in range(16):
        a = math.radians(i * 22.5)
        l = 92 if i % 2 else 80
        body += f'<path d="M{f(100 + 58 * math.cos(a - .12))},{f(100 + 58 * math.sin(a - .12))} L{f(100 + l * math.cos(a))},{f(100 + l * math.sin(a))} L{f(100 + 58 * math.cos(a + .12))},{f(100 + 58 * math.sin(a + .12))} Z" fill="#ffc21a"/>'
    body += '<circle cx="100" cy="100" r="62" fill="url(#sg)" stroke="#e8861a" stroke-width="2"/>'
    svg("himmel-sonne", body, defs)


sonne()
planet("planet-merkur", 44, "#c9c2bb", "#6d655e", '<circle cx="80" cy="84" r="7" fill="#7a726b" opacity=".6"/><circle cx="116" cy="112" r="10" fill="#7a726b" opacity=".5"/><circle cx="96" cy="124" r="5" fill="#7a726b" opacity=".6"/>')
planet("planet-venus", 66, "#fff0c4", "#d49a3e", bands=[(-.5, .2, "#f7d48a"), (.1, .25, "#e8b860")])
planet("planet-erde", 68, "#6fc2ff", "#1a4fa0",
       '<path d="M52,70 Q70,48 96,56 Q110,70 96,86 Q80,92 82,112 Q72,128 60,110 Q44,92 52,70 Z" fill="#4caf50"/><path d="M118,104 Q140,92 156,108 Q160,134 140,150 Q120,146 122,126 Z" fill="#4caf50"/><path d="M60,40 Q100,30 140,40 L140,46 Q100,40 60,46 Z" fill="#fff" opacity=".8"/>')
planet("planet-mars", 52, "#ff9a6a", "#a8341a", '<circle cx="84" cy="90" r="9" fill="#8a2a12" opacity=".4"/><circle cx="118" cy="114" r="12" fill="#8a2a12" opacity=".35"/><path d="M78,54 Q100,48 122,54 L118,58 Q100,54 82,58 Z" fill="#fff" opacity=".8"/>')
planet("planet-jupiter", 86, "#f5dcb8", "#b07a48", '<ellipse cx="128" cy="122" rx="16" ry="9" fill="#c8502a" opacity=".85"/>',
       bands=[(-.75, .15, "#c89466"), (-.4, .2, "#a86a40"), (0, .12, "#d8aa7a"), (.25, .18, "#a86a40"), (.6, .12, "#c89466")])
planet("planet-saturn", 54, "#fbe6b0", "#c49a52", rings=True, bands=[(-.4, .15, "#d8b470"), (.15, .2, "#d8b470")])
planet("planet-uranus", 58, "#d4fbff", "#4fb8c8")
planet("planet-neptun", 58, "#7aa8ff", "#1a2fa0", '<ellipse cx="88" cy="94" rx="12" ry="6" fill="#0a1a6a" opacity=".5"/>', bands=[(-.2, .1, "#4a70e0")])


def mond(name, phase):
    """phase: 0 Neumond, 1 zunehmend (rechte Hälfte hell), 2 Vollmond, 3 abnehmend (linke Hälfte hell)"""
    defs = rgrad("mg", "#fffbe0", "#d8cf9a", ".4", ".35", ".8")
    body = '<rect width="200" height="200" rx="24" fill="#1b2350"/>'
    for x, y in [(30, 30), (170, 40), (40, 160), (160, 170), (150, 110), (24, 96)]:
        body += f'<circle cx="{x}" cy="{y}" r="2.2" fill="#fff" opacity=".8"/>'
    body += '<circle cx="100" cy="100" r="62" fill="#2a3266"/>'
    if phase == 2:
        body += '<circle cx="100" cy="100" r="62" fill="url(#mg)"/><circle cx="82" cy="84" r="10" fill="#c9bf86" opacity=".6"/><circle cx="118" cy="118" r="14" fill="#c9bf86" opacity=".5"/>'
    elif phase in (1, 3):
        s = 1 if phase == 1 else -1
        body += f'<path d="M100,38 A62,62 0 0 {1 if s > 0 else 0} 100,162 A28,62 0 0 {0 if s > 0 else 1} 100,38 Z" fill="url(#mg)"/>'
    body += '<circle cx="100" cy="100" r="62" fill="none" stroke="#fff" stroke-opacity=".18" stroke-width="2"/>'
    svg(name, body, defs)


mond("mond-neumond", 0); mond("mond-zunehmend", 1); mond("mond-vollmond", 2); mond("mond-abnehmend", 3)


# ---------------- Auge (Schaubilder zum Beschriften, 300 x 200) ----------------
def auge_vorn():
    defs = rgrad("ir", "#9fd4ff", "#1f5fa8", ".5", ".5", ".6") + grad("sk", "#f9dcc0", "#efc49e")
    b = '<rect width="300" height="200" rx="18" fill="url(#sk)"/>'
    # Augenbraue
    b += '<path d="M58,44 Q150,0 246,46 Q150,18 58,44 Z" fill="#6b4423" stroke="#5a3418" stroke-width="7" stroke-linejoin="round"/>'
    for i in range(26):
        t = i / 25
        x = (1 - t) ** 2 * 58 + 2 * (1 - t) * t * 150 + t * t * 246
        y = (1 - t) ** 2 * 44 + 2 * (1 - t) * t * 6 + t * t * 46
        b += f'<path d="M{f(x)},{f(y + 4)} l{f(6 + 4 * t)},{f(-7)}" stroke="#4a2c12" stroke-width="2.2" stroke-linecap="round"/>'
    # Oberlid (Hautfalte) deutlich als eigene Fläche
    b += '<path d="M64,120 Q150,-4 236,120 Q150,58 64,120 Z" fill="#e9a98a" stroke="#c98668" stroke-width="2.5"/>'
    E = "M70,120 Q150,58 230,120 Q150,172 70,120 Z"
    b += f'<path d="{E}" fill="#fff" stroke="#8a5a3a" stroke-width="3"/>'
    b += f'<clipPath id="ey"><path d="{E}"/></clipPath>'
    b += '<g clip-path="url(#ey)"><circle cx="150" cy="112" r="30" fill="url(#ir)" stroke="#153f70" stroke-width="2"/>'
    for k in range(18):
        a = math.radians(k * 20)
        b += f'<path d="M{f(150 + 14 * math.cos(a))},{f(112 + 14 * math.sin(a))} L{f(150 + 27 * math.cos(a))},{f(112 + 27 * math.sin(a))}" stroke="#2a6ab8" stroke-width="1.4" opacity=".6"/>'
    b += '<circle cx="150" cy="112" r="12" fill="#111"/><circle cx="143" cy="105" r="5" fill="#fff" opacity=".9"/></g>'
    for i in range(1, 16):
        t = i / 16
        x = (1 - t) ** 2 * 70 + 2 * (1 - t) * t * 150 + t * t * 230
        y = (1 - t) ** 2 * 120 + 2 * (1 - t) * t * 58 + t * t * 120
        dx = (t - .5) * 18
        b += f'<path d="M{f(x)},{f(y)} q{f(dx * .4)},-7 {f(dx)},-12" fill="none" stroke="#222" stroke-width="2.4" stroke-linecap="round"/>'
    for i in range(2, 13):
        t = i / 14
        x = (1 - t) ** 2 * 70 + 2 * (1 - t) * t * 150 + t * t * 230
        y = (1 - t) ** 2 * 120 + 2 * (1 - t) * t * 172 + t * t * 120
        b += f'<path d="M{f(x)},{f(y)} l{f((t - .5) * 10)},7" stroke="#333" stroke-width="1.8" stroke-linecap="round"/>'
    svg("auge-vorn", b, defs, "0 0 300 200")


def auge_schnitt():
    defs = rgrad("gk", "#ffffff", "#dfe8f2", ".45", ".5", ".7") + grad("bone", "#f3e3c4", "#d9c49a")
    b = '<rect width="300" height="200" rx="18" fill="#fbe9dc"/>'
    # Augenhöhle (Knochen)
    b += '<path d="M96,40 Q120,8 200,10 Q262,14 286,52 L286,24 Q240,-4 170,2 Q104,6 80,36 Z" fill="url(#bone)" stroke="#b49a68" stroke-width="2.5"/>'
    b += '<path d="M96,160 Q120,192 200,190 Q262,186 286,148 L286,176 Q240,204 170,198 Q104,194 80,164 Z" fill="url(#bone)" stroke="#b49a68" stroke-width="2.5"/>'
    # Sehnerv
    b += '<path d="M214,92 Q250,94 296,100 L296,122 Q250,116 214,112 Z" fill="#ffd84a" stroke="#c9a010" stroke-width="2"/>'
    # Augapfel mit Lederhaut
    b += '<circle cx="160" cy="100" r="64" fill="#fff" stroke="#9aa3ad" stroke-width="3"/>'
    b += '<circle cx="160" cy="100" r="59" fill="url(#gk)"/>'
    # Netzhaut (hinten innen)
    b += '<path d="M126,52 A58,58 0 1,1 126,148" fill="none" stroke="#e8785a" stroke-width="6"/>'
    # Hornhaut (vorn gewölbt)
    b += '<path d="M110,64 Q74,100 110,136" fill="#e6f4ff" fill-opacity=".7" stroke="#6aa8d8" stroke-width="3"/>'
    # Iris oben und unten, dazwischen die Pupille
    b += '<path d="M106,70 L114,68 L114,90 L106,90 Z" fill="#2a6ab8"/><path d="M106,110 L114,110 L114,132 L106,130 Z" fill="#2a6ab8"/>'
    # Linse
    b += '<ellipse cx="124" cy="100" rx="9" ry="22" fill="#fff6c0" stroke="#d6b84a" stroke-width="2.5"/>'
    # Lichtstrahlen
    b += '<path d="M20,88 L124,92 L216,108 M20,112 L124,108 L216,92" stroke="#ffb400" stroke-width="1.6" stroke-dasharray="5 4" fill="none" opacity=".8"/>'
    svg("auge-schnitt", b, defs, "0 0 300 200")


auge_vorn(); auge_schnitt()


for name, s in ALL.items():
    with open(f"{OUT}/{name}.svg", "w", encoding="utf-8") as fh:
        fh.write(s)
print(len(ALL), "Zeichnungen")
