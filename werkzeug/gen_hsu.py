# Erzeugt Heimat- und Sachunterricht (HSU):
#   inhalte/hsu/k1-*.json (1. Klasse, alles mit Bildern, Aufgaben werden vorgelesen)
#   inhalte/hsu/k3-*.json (3. Klasse, mit Text)
#   inhalte/wissen-hsu.json (Merkkarten 3. Klasse, erscheinen vor der Lektion und im Wissensheft)
# Gliederung nach den Lernbereichen des LehrplanPLUS Bayern (HSU 1/2 und 3/4).
# Eigene Aufgaben, nichts aus Büchern oder Apps kopiert.
# JSON nicht von Hand ändern, sondern hier und neu erzeugen: python3 werkzeug/gen_hsu.py
import json, re, sys, os, unicodedata

OUT = sys.argv[1] if len(sys.argv) > 1 else "inhalte"
ids = set()
RULES = []


def slug(s):
    s = s.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    s = unicodedata.normalize("NFKD", s)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:28] or "x"


def uid(i):
    i = i.rstrip("-")
    n, k = i, 2
    while n in ids:
        n = f"{i}-{k}"; k += 1
    ids.add(n)
    return n


# ---------- Bausteine 1. Klasse (Bilder) ----------
def bild(p, task, options, answer, pic=None, explain=None):
    """Tipp auf das richtige Bild. options = Emojis."""
    assert answer in options, (task, answer)
    t = {"kind": "choice", "id": uid(f"{p}-{slug(task)}"), "task": task, "prompt": task,
         "options": options, "answer": answer, "picOptions": True}
    if pic: t["pic"] = pic
    if explain: t["explain"] = explain
    return t


def stimmt(p, aussage, ja, pic=None):
    """Stimmt das? ✅ oder ❌ (Aussage wird vorgelesen)."""
    t = {"kind": "choice", "id": uid(f"{p}-{slug(aussage)}"), "task": f"Stimmt das? {aussage}", "prompt": aussage,
         "options": ["✅", "❌"], "answer": "✅" if ja else "❌", "picOptions": True, "keepOrder": True}
    if pic: t["pic"] = pic
    return t


def bildsort(p, task, groups, items):
    """Bilder in Gruppen sortieren. items = (Emoji, Name, Gruppe)."""
    return {"kind": "sort", "pics": True, "task": task, "groups": groups,
            "items": [{"id": uid(f"{p}-{slug(n)}"), "pic": e, "text": n, "group": g} for e, n, g in items]}


def bildreihe(p, task, tiles, explain=None):
    """Bilder in die richtige Reihenfolge bringen."""
    t = {"kind": "order", "pics": True, "id": uid(f"{p}-{slug(task + ' ' + tiles[0])}"), "task": task, "tiles": tiles}
    if explain: t["explain"] = explain
    return t


# ---------- Bausteine 3. Klasse (Text) ----------
def ch(p, task, prompt, options, answer, explain=None, keep=False):
    assert answer in options, (prompt, answer, options)
    t = {"kind": "choice", "id": uid(f"{p}-{slug(prompt)}"), "task": task, "prompt": prompt,
         "options": options, "answer": answer}
    if keep: t["keepOrder"] = True
    if explain: t["explain"] = explain
    return t


def wahr(p, aussage, ja, explain=None):
    return ch(p, "Richtig oder falsch?", aussage, ["richtig", "falsch"], "richtig" if ja else "falsch", explain, keep=True)


def sort(p, task, review, groups, items):
    return {"kind": "sort", "task": task, "review": review, "groups": groups,
            "items": [{"id": uid(f"{p}-{slug(t)}"), "text": t, "group": g} for t, g in items]}


def pairs(p, task, review, prs):
    return {"kind": "pairs", "task": task, "review": review,
            "pairs": [{"id": uid(f"{p}-{slug(a)}"), "a": a, "b": b} for a, b in prs]}


def reihe(p, task, tiles, explain=None):
    t = {"kind": "order", "id": uid(f"{p}-{slug(task + ' ' + tiles[0])}"), "task": task, "tiles": tiles}
    if explain: t["explain"] = explain
    return t


def ty(p, task, prompt, answer, also=None):
    t = {"kind": "type", "id": uid(f"{p}-{slug(prompt)}"), "task": task, "prompt": prompt, "answer": answer}
    if also: t["also"] = also
    return t


def lesson(title, icon, tasks, mix=True):
    l = {"title": title, "icon": icon, "tasks": tasks}
    if mix: l["mix"] = True
    return l


def test(n=12):
    return {"title": "Test", "icon": "⭐", "test": True, "count": n}


def unit(id_, title, image, color, lessons):
    return {"id": id_, "type": "schule", "title_de": title, "image": image, "color": color, "lessons": lessons}


def wissen(id_, icon, title, merke, beispiele=(), lektionen=(), trick=""):
    r = {"id": id_, "icon": icon, "title": title, "merke": list(merke), "beispiele": list(beispiele), "lektionen": list(lektionen)}
    if trick: r["trick"] = trick
    RULES.append(r)


# ---------- Bausteine mit eigenen Zeichnungen (img/zeichnungen, siehe gen_zeichnungen.py) ----------
def Z(name):
    return f"[[{name}]]"


def bildfrage(p, task, prompt, zeich, options, answer, explain=None, keep=False):
    """Zeichnung oben, Frage darunter, Text-Antworten."""
    t = ch(p, task, prompt + " " + zeich, options, answer, explain, keep)
    t["prompt"], t["pic"], t["showText"] = prompt, Z(zeich), True
    if task == prompt: t["task"] = "Schau dir das Bild genau an!"
    return t


def bildwahl(p, task, options, answer, explain=None):
    """Tipp auf die richtige Zeichnung. options/answer = Namen der Zeichnungen."""
    assert answer in options
    t = {"kind": "choice", "id": uid(f"{p}-{slug(task + ' ' + answer)}"), "task": task, "prompt": task,
         "options": [Z(o) for o in options], "answer": Z(answer), "picOptions": True}
    if explain: t["explain"] = explain
    return t


def schaubild(p, task, image, spots, w=300, h=200, extra=(), text=None, labels=False):
    """Schaubild beschriften: spots = (x, y, Begriff) in Bildkoordinaten.
    Mit text (Absätze, "__" = Lücke in spots-Reihenfolge) wird daraus ein Lückentext zum Bild;
    labels=True schreibt die Begriffe als Hilfe ins Bild (x=None: kein Etikett)."""
    t = {"kind": "label", "id": uid(f"{p}-{slug(task + ' ' + image)}"), "task": task, "image": image, "w": w, "h": h,
         "spots": [({"x": x, "y": y} if x is not None else {}) | {"answer": a} for x, y, a in spots]}
    if extra: t["extra"] = list(extra)
    if text: t["text"] = list(text)
    if labels: t["labels"] = True
    return t


UNITS = {}
JZ = ["🌷 Frühling", "☀️ Sommer", "🍂 Herbst", "⛄ Winter"]

# =====================================================================
# 1. KLASSE
# =====================================================================

# ---------- Jahreszeiten, Wetter und Feste ----------
p = "h1-jahr"
UNITS["hsu/k1-jahreszeiten.json"] = unit(p, "Jahreszeiten, Wetter und Feste", "🍂", "#d9822b", [
    lesson("Die vier Jahreszeiten", "🌷", [
        bildsort(p, "Wann ist das? Tipp auf die richtige Jahreszeit!", JZ, [
            ("⛄", "Schneemann", "⛄ Winter"), ("🌷", "Tulpe", "🌷 Frühling"), ("🍦", "Eis", "☀️ Sommer"),
            ("🌰", "Kastanie", "🍂 Herbst"), ("🛷", "Schlitten", "⛄ Winter"), ("🍓", "Erdbeere", "☀️ Sommer"),
        ]),
        bildsort(p, "Wann ist das? Tipp auf die richtige Jahreszeit!", JZ, [
            ("🐣", "Küken", "🌷 Frühling"), ("🍄", "Pilz", "🍂 Herbst"), ("🏖️", "Strand", "☀️ Sommer"),
            ("🧤", "Handschuhe", "⛄ Winter"), ("🌸", "Blüte", "🌷 Frühling"), ("🎃", "Kürbis", "🍂 Herbst"),
        ]),
    ], mix=False),
    lesson("Was kommt danach?", "🔁", [
        bildreihe(p, "Leg die Jahreszeiten der Reihe nach. Fang mit dem Frühling an!", ["🌷", "☀️", "🍂", "⛄"]),
        bild(p, "Was kommt nach dem Winter?", ["🌷", "☀️", "🍂"], "🌷"),
        bild(p, "Was kommt nach dem Sommer?", ["🌷", "🍂", "⛄"], "🍂"),
        bild(p, "Was kommt nach dem Herbst?", ["⛄", "☀️", "🌷"], "⛄"),
        bild(p, "Was kommt nach dem Frühling?", ["🍂", "☀️", "⛄"], "☀️"),
        bildreihe(p, "Leg die Jahreszeiten der Reihe nach. Fang mit dem Herbst an!", ["🍂", "⛄", "🌷", "☀️"]),
    ], mix=False),
    lesson("Das Wetter", "🌦️", [
        bild(p, "Tipp auf den Regen!", ["🌧️", "☀️", "❄️"], "🌧️"),
        bild(p, "Tipp auf den Schnee!", ["☀️", "❄️", "🌧️"], "❄️"),
        bild(p, "Tipp auf das Gewitter!", ["🌩️", "☁️", "☀️"], "🌩️"),
        bild(p, "Tipp auf den Wind!", ["🌬️", "❄️", "🌧️"], "🌬️"),
        bild(p, "Es regnet. Was nimmst du mit?", ["☂️", "🕶️", "🛷"], "☂️"),
        bild(p, "Es ist sehr heiß. Was ziehst du an?", ["🧢", "🧣", "🧤"], "🧢"),
        bild(p, "Es schneit. Was ziehst du an?", ["🧤", "🩳", "🩴"], "🧤"),
        stimmt(p, "Wenn die Sonne scheint, ist es warm.", True, "☀️"),
        stimmt(p, "Im Winter baden wir im See.", False, "⛄"),
    ]),
    lesson("Feste im Jahr", "🎄", [
        bild(p, "Was gehört zu Weihnachten?", ["🎄", "🐣", "🎃"], "🎄"),
        bild(p, "Was gehört zu Ostern?", ["🐰", "🎄", "🏮"], "🐰"),
        bild(p, "Was gehört zu Sankt Martin?", ["🏮", "🥚", "🎄"], "🏮"),
        bild(p, "Was gehört zum Geburtstag?", ["🎂", "🏮", "🐣"], "🎂"),
        bild(p, "Was gehört zu Fasching?", ["🎭", "🎄", "🐰"], "🎭"),
        bildsort(p, "Wann feiern wir das? Tipp auf die Jahreszeit!", JZ, [
            ("🎄", "Weihnachten", "⛄ Winter"), ("🐰", "Ostern", "🌷 Frühling"), ("🏮", "Sankt Martin", "🍂 Herbst"),
        ]),
    ]),
    test(10),
])

# ---------- Mein Körper und meine Sinne ----------
p = "h1-koerper"
SINNE = ["👀 sehen", "👂 hören", "👃 riechen", "👅 schmecken"]
UNITS["hsu/k1-koerper.json"] = unit(p, "Mein Körper und meine Sinne", "👀", "#e0567a", [
    lesson("Körperteile", "🖐️", [
        bild(p, "Tipp auf die Hand!", ["🖐️", "🦶", "👂"], "🖐️"),
        bild(p, "Tipp auf den Fuß!", ["👃", "🦶", "🦵"], "🦶"),
        bild(p, "Tipp auf das Ohr!", ["👄", "👀", "👂"], "👂"),
        bild(p, "Tipp auf die Nase!", ["👃", "🖐️", "👄"], "👃"),
        bild(p, "Tipp auf den Mund!", ["👂", "👄", "🦶"], "👄"),
        bild(p, "Tipp auf das Bein!", ["🦵", "🖐️", "👃"], "🦵"),
        bild(p, "Tipp auf die Augen!", ["👂", "👄", "👀"], "👀"),
        bild(p, "Tipp auf den Zahn!", ["🦷", "🦶", "👂"], "🦷"),
    ]),
    lesson("Die fünf Sinne", "👂", [
        bild(p, "Womit siehst du?", ["👀", "👂", "👃"], "👀"),
        bild(p, "Womit hörst du?", ["👃", "👂", "👅"], "👂"),
        bild(p, "Womit riechst du?", ["👃", "👀", "🖐️"], "👃"),
        bild(p, "Womit schmeckst du?", ["👂", "👅", "👀"], "👅"),
        bild(p, "Womit fühlst du, ob etwas weich ist?", ["🖐️", "👂", "👃"], "🖐️"),
        stimmt(p, "Mit den Ohren kannst du hören.", True, "👂"),
        stimmt(p, "Mit der Nase kannst du sehen.", False, "👃"),
        stimmt(p, "Mit der Zunge schmeckst du, ob etwas süß ist.", True, "👅"),
    ]),
    lesson("Was merkst du womit?", "🌈", [
        bildsort(p, "Womit merkst du das? Tipp auf den richtigen Sinn!", SINNE, [
            ("🌈", "Regenbogen", "👀 sehen"), ("🔔", "Glocke", "👂 hören"), ("🌹", "Rose", "👃 riechen"),
            ("🍋", "Zitrone", "👅 schmecken"), ("🥁", "Trommel", "👂 hören"), ("⭐", "Stern", "👀 sehen"),
            ("🍦", "Eis", "👅 schmecken"), ("🧄", "Knoblauch", "👃 riechen"),
        ]),
        bild(p, "Die Sonne ist sehr hell. Was schützt deine Augen?", ["🕶️", "🧤", "🧣"], "🕶️"),
        stimmt(p, "Man schaut nie direkt in die Sonne.", True, "☀️"),
    ], mix=False),
    test(10),
])

# ---------- Gesund essen und Zähne putzen ----------
p = "h1-essen"
UNITS["hsu/k1-essen.json"] = unit(p, "Gesund essen und Zähne putzen", "🍎", "#3fa34d", [
    lesson("Obst oder Gemüse?", "🥕", [
        bildsort(p, "Ist das Obst oder Gemüse?", ["🍎 Obst", "🥕 Gemüse"], [
            ("🍌", "Banane", "🍎 Obst"), ("🥦", "Brokkoli", "🥕 Gemüse"), ("🍐", "Birne", "🍎 Obst"),
            ("🥒", "Gurke", "🥕 Gemüse"), ("🍇", "Trauben", "🍎 Obst"), ("🌽", "Mais", "🥕 Gemüse"),
            ("🍒", "Kirschen", "🍎 Obst"), ("🫑", "Paprika", "🥕 Gemüse"), ("🍓", "Erdbeere", "🍎 Obst"),
            ("🧅", "Zwiebel", "🥕 Gemüse"),
        ]),
    ], mix=False),
    lesson("Jeden Tag oder nur ab und zu?", "🍬", [
        bildsort(p, "Isst du das jeden Tag oder nur ab und zu?", ["💪 jeden Tag", "🍬 nur ab und zu"], [
            ("🍎", "Apfel", "💪 jeden Tag"), ("💧", "Wasser", "💪 jeden Tag"), ("🍭", "Lutscher", "🍬 nur ab und zu"),
            ("🍟", "Pommes", "🍬 nur ab und zu"), ("🥦", "Brokkoli", "💪 jeden Tag"), ("🍫", "Schokolade", "🍬 nur ab und zu"),
            ("🍞", "Brot", "💪 jeden Tag"), ("🥤", "Limo", "🍬 nur ab und zu"), ("🥕", "Karotte", "💪 jeden Tag"),
            ("🍩", "Donut", "🍬 nur ab und zu"),
        ]),
    ], mix=False),
    lesson("Gesunde Pause", "🥪", [
        bild(p, "Du hast Durst. Was trinkst du am besten?", ["💧", "🥤", "☕"], "💧"),
        bild(p, "Was ist ein gesundes Pausenbrot?", ["🥪", "🍰", "🍭"], "🥪"),
        bild(p, "Was ist ein gesunder Snack für die Pause?", ["🥕", "🍬", "🍩"], "🥕"),
        bild(p, "Was ist gesund für die Pause?", ["🍏", "🍫", "🍟"], "🍏"),
        stimmt(p, "Obst und Gemüse machen dich stark und gesund.", True, "🍎"),
        stimmt(p, "Limo ist das beste Getränk gegen Durst.", False, "🥤"),
        stimmt(p, "Ein Frühstück am Morgen gibt dir Kraft für die Schule.", True, "🥣"),
    ]),
    lesson("Zähne putzen", "🪥", [
        bild(p, "Womit putzt du deine Zähne?", ["🪥", "🧹", "🍴"], "🪥"),
        stimmt(p, "Zähne putzt man morgens und abends.", True, "🪥"),
        stimmt(p, "Nach dem Zähneputzen am Abend isst man noch Süßes.", False, "🍬"),
        stimmt(p, "Viele Süßigkeiten sind gut für die Zähne.", False, "🍭"),
        stimmt(p, "Zähne putzen dauert ungefähr so lange wie zwei Lieder.", True, "🎵"),
        stimmt(p, "Die Zahnärztin schaut nach, ob deine Zähne gesund sind.", True, "🦷"),
        bild(p, "Was ist gut für deine Zähne?", ["🥕", "🍭", "🍬"], "🥕"),
    ]),
    test(10),
])

# ---------- Gefühle und Regeln ----------
p = "h1-gefuehle"
UNITS["hsu/k1-gefuehle.json"] = unit(p, "Gefühle und Regeln", "😊", "#e8a317", [
    lesson("Wie fühlt sich das Kind?", "😀", [
        bild(p, "Tipp auf das fröhliche Gesicht!", ["😀", "😢", "😠"], "😀"),
        bild(p, "Tipp auf das traurige Gesicht!", ["😠", "😢", "😀"], "😢"),
        bild(p, "Tipp auf das wütende Gesicht!", ["😴", "😀", "😠"], "😠"),
        bild(p, "Tipp auf das Gesicht, das Angst hat!", ["😱", "😀", "😴"], "😱"),
        bild(p, "Tipp auf das müde Gesicht!", ["😢", "😴", "😀"], "😴"),
        bild(p, "Tipp auf das überraschte Gesicht!", ["😮", "😠", "😴"], "😮"),
    ]),
    lesson("Wie fühlst du dich?", "💬", [
        bild(p, "Du bekommst ein Geschenk. Wie fühlst du dich?", ["😀", "😢", "😠"], "😀"),
        bild(p, "Dein Eis fällt auf den Boden. Wie fühlst du dich?", ["😀", "😢", "😴"], "😢"),
        bild(p, "Jemand nimmt dir einfach dein Spielzeug weg. Wie fühlst du dich?", ["😠", "😀", "😴"], "😠"),
        bild(p, "Es donnert ganz laut in der Nacht. Wie fühlst du dich vielleicht?", ["😱", "😀", "😴"], "😱"),
        bild(p, "Es ist spät am Abend. Wie fühlst du dich?", ["😴", "😠", "😮"], "😴"),
        stimmt(p, "Alle Gefühle sind in Ordnung. Man darf auch mal traurig sein.", True, "💝"),
    ]),
    lesson("Regeln in der Klasse", "🏫", [
        stimmt(p, "Wir hören zu, wenn jemand spricht.", True, "👂"),
        stimmt(p, "Wer etwas sagen will, zeigt auf.", True, "🙋"),
        stimmt(p, "Wir schubsen andere Kinder.", False, "😠"),
        stimmt(p, "Wir räumen unseren Platz auf.", True, "🧹"),
        stimmt(p, "Wir lachen andere Kinder aus.", False, "😂"),
        stimmt(p, "Im Klassenzimmer rennen wir herum.", False, "🏃"),
        stimmt(p, "Wenn jemand traurig ist, tröste ich.", True, "🤗"),
    ]),
    lesson("Streit lösen", "🤝", [
        bild(p, "Zwei Kinder haben gestritten. Was hilft?", ["🤝", "👊", "😠"], "🤝"),
        stimmt(p, "Nach einem Streit kann man sich die Hand geben und sich vertragen.", True, "🤝"),
        stimmt(p, "Wenn ich wütend bin, haue ich.", False, "👊"),
        stimmt(p, "Wenn ich wütend bin, atme ich tief durch.", True, "😮‍💨"),
        stimmt(p, "Wenn ich Hilfe brauche, frage ich die Lehrerin.", True, "🧑‍🏫"),
        stimmt(p, "Wenn ich etwas falsch gemacht habe, sage ich: Entschuldigung.", True, "🙏"),
    ]),
    test(10),
])

# ---------- Tiere ----------
p = "h1-tiere"
WO = ["🏠 Zuhause", "🚜 Bauernhof", "🌲 Wald"]
UNITS["hsu/k1-tiere.json"] = unit(p, "Tiere", "🦔", "#a0663a", [
    lesson("Wo lebt das Tier?", "🏠", [
        bildsort(p, "Wo lebt das Tier? Tipp auf das richtige Bild!", WO, [
            ("🐱", "Katze", "🏠 Zuhause"), ("🐄", "Kuh", "🚜 Bauernhof"), ("🦊", "Fuchs", "🌲 Wald"),
            ("🐹", "Hamster", "🏠 Zuhause"), ("🐷", "Schwein", "🚜 Bauernhof"), ("🦌", "Reh", "🌲 Wald"),
        ]),
        bildsort(p, "Wo lebt das Tier? Tipp auf das richtige Bild!", WO, [
            ("🐔", "Huhn", "🚜 Bauernhof"), ("🦉", "Eule", "🌲 Wald"), ("🐶", "Hund", "🏠 Zuhause"),
            ("🐑", "Schaf", "🚜 Bauernhof"), ("🐿️", "Eichhörnchen", "🌲 Wald"), ("🐟", "Goldfisch", "🏠 Zuhause"),
        ]),
    ], mix=False),
    lesson("Was gibt uns das Tier?", "🥛", [
        bild(p, "Was gibt uns die Kuh?", ["🥛", "🥚", "🍯"], "🥛"),
        bild(p, "Was gibt uns das Huhn?", ["🧶", "🥚", "🥛"], "🥚"),
        bild(p, "Was gibt uns das Schaf?", ["🍯", "🥛", "🧶"], "🧶"),
        bild(p, "Was macht die Biene?", ["🍯", "🥚", "🧶"], "🍯"),
        bild(p, "Welches Tierkind schlüpft aus dem Ei?", ["🐥", "🐶", "🐱"], "🐥"),
        stimmt(p, "Das Kalb ist das Kind von der Kuh.", True, "🐄"),
        stimmt(p, "Das Küken ist das Kind vom Schwein.", False, "🐷"),
    ]),
    lesson("Was frisst das Tier?", "🥕", [
        bild(p, "Was frisst der Hase gern?", ["🥕", "🍖", "🐟"], "🥕"),
        bild(p, "Was frisst das Eichhörnchen gern?", ["🌰", "🧀", "🍬"], "🌰"),
        bild(p, "Was frisst die Kuh?", ["🌿", "🍖", "🍰"], "🌿"),
        bild(p, "Was frisst die Amsel gern?", ["🐛", "🍕", "🧀"], "🐛"),
        bild(p, "Was kaut der Hund gern?", ["🦴", "🌻", "🍬"], "🦴"),
        stimmt(p, "Haustiere brauchen jeden Tag frisches Wasser.", True, "💧"),
    ]),
    lesson("Tiere im Winter", "🦔", [
        bild(p, "Welches Tier hält Winterschlaf?", ["🦔", "🐄", "🐶"], "🦔"),
        bild(p, "Wo schläft der Igel im Winter?", ["🍂", "🏊", "☀️"], "🍂"),
        stimmt(p, "Der Igel schläft im Winter in einem Laubhaufen.", True, "🦔"),
        stimmt(p, "Das Eichhörnchen sammelt im Herbst Nüsse.", True, "🐿️"),
        stimmt(p, "Viele Vögel fliegen im Herbst in warme Länder.", True, "🐦"),
        stimmt(p, "Der Igel frisst im Winter jeden Tag Äpfel.", False, "🍎"),
    ]),
    test(10),
])

# ---------- Pflanzen ----------
p = "h1-pflanzen"
UNITS["hsu/k1-pflanzen.json"] = unit(p, "Pflanzen", "🌷", "#d04a8c", [
    lesson("Was braucht die Pflanze?", "💧", [
        stimmt(p, "Pflanzen brauchen Wasser.", True, "💧"),
        stimmt(p, "Pflanzen brauchen Licht.", True, "☀️"),
        stimmt(p, "Pflanzen brauchen Schokolade.", False, "🍫"),
        stimmt(p, "Pflanzen brauchen Erde.", True, "🪴"),
        bild(p, "Die Blume ist ganz trocken. Was braucht sie?", ["💧", "🍫", "🧸"], "💧"),
        bild(p, "Was braucht eine Pflanze zum Wachsen?", ["☀️", "🎈", "🧦"], "☀️"),
    ]),
    lesson("Wie wächst das?", "🌱", [
        bildreihe(p, "Wie wächst die Sonnenblume? Leg die Bilder der Reihe nach!", ["🌱", "🌿", "🌻"]),
        bildreihe(p, "Wie wird aus der Blüte ein Apfel? Leg die Bilder der Reihe nach!", ["🌸", "🍏", "🍎"]),
        bildreihe(p, "Der Baum im Jahr: Leg die Bilder der Reihe nach!", ["🌸", "🌳", "🍂"]),
        bild(p, "Was wächst an einem Apfelbaum?", ["🍎", "🍌", "🥥"], "🍎"),
        bild(p, "Was wächst unter der Erde?", ["🥕", "🍎", "🍒"], "🥕"),
        bild(p, "Welche Blume blüht schon im Frühling?", ["🌷", "🌻", "🍂"], "🌷"),
    ], mix=False),
    lesson("Baum oder Blume?", "🌳", [
        bildsort(p, "Ist das ein Baum oder eine Blume?", ["🌳 Baum", "💐 Blume"], [
            ("🌲", "Tanne", "🌳 Baum"), ("🌻", "Sonnenblume", "💐 Blume"), ("🌷", "Tulpe", "💐 Blume"),
            ("🌴", "Palme", "🌳 Baum"), ("🌹", "Rose", "💐 Blume"), ("🌼", "Gänseblümchen", "💐 Blume"),
        ]),
        stimmt(p, "Die Wurzel ist unter der Erde.", True, "🌱"),
        stimmt(p, "Die Blätter sind meistens grün.", True, "🍃"),
        stimmt(p, "Die Wurzel ist oben an der Blüte.", False, "🌸"),
    ], mix=False),
    test(10),
])

# ---------- Mein Tag ----------
p = "h1-tag"
UNITS["hsu/k1-tag.json"] = unit(p, "Mein Tag", "⏰", "#5468d4", [
    lesson("Morgens, mittags, abends", "🌅", [
        bildsort(p, "Wann machst du das? Morgens, mittags oder abends?", ["🌅 morgens", "☀️ mittags", "🌙 abends"], [
            ("⏰", "Wecker klingelt", "🌅 morgens"), ("🥣", "Frühstück", "🌅 morgens"), ("🎒", "zur Schule gehen", "🌅 morgens"),
            ("🍝", "Mittagessen", "☀️ mittags"), ("🛏️", "ins Bett gehen", "🌙 abends"), ("📖", "Gute-Nacht-Geschichte", "🌙 abends"),
        ]),
    ], mix=False),
    lesson("Was kommt zuerst?", "🔁", [
        bildreihe(p, "Am Morgen: Leg die Bilder der Reihe nach!", ["⏰", "🥣", "🎒", "🏫"]),
        bildreihe(p, "Der ganze Tag: Leg die Bilder der Reihe nach!", ["🌅", "☀️", "🌇", "🌙"]),
        bildreihe(p, "Kuchen backen: Leg die Bilder der Reihe nach!", ["🥚", "🥣", "🎂"]),
        bild(p, "Was machst du, bevor du ins Bett gehst?", ["🪥", "🥣", "🎒"], "🪥"),
        bild(p, "Was kommt nach dem Abend?", ["🌙", "🌅", "☀️"], "🌙"),
    ], mix=False),
    lesson("Die Woche", "📅", [
        bild(p, "Wie viele Tage hat eine Woche?", ["7️⃣", "3️⃣", "5️⃣"], "7️⃣"),
        stimmt(p, "Eine Woche hat sieben Tage.", True, "7️⃣"),
        stimmt(p, "Am Wochenende ist meistens keine Schule.", True, "🏫"),
        stimmt(p, "Nach dem Abend kommt die Nacht.", True, "🌙"),
        stimmt(p, "Nach dem Abend kommt gleich der Mittag.", False, "☀️"),
    ]),
    lesson("Früher und heute", "👵", [
        bildsort(p, "War das früher oder ist das heute?", ["👵 früher", "🧒 heute"], [
            ("🕯️", "Kerze als Licht", "👵 früher"), ("💡", "Lampe", "🧒 heute"), ("🐴", "mit dem Pferd fahren", "👵 früher"),
            ("🚗", "Auto", "🧒 heute"), ("☎️", "altes Telefon", "👵 früher"), ("📱", "Handy", "🧒 heute"),
        ]),
    ], mix=False),
    test(10),
])

# ---------- Sicher unterwegs ----------
p = "h1-verkehr"
UNITS["hsu/k1-verkehr.json"] = unit(p, "Sicher unterwegs", "🚦", "#d6453d", [
    lesson("Die Ampel", "🚦", [
        bild(p, "Bei welcher Farbe darfst du an der Fußgänger-Ampel gehen?", ["🟢", "🔴", "🟡"], "🟢"),
        bild(p, "Bei welcher Farbe musst du stehen bleiben?", ["🟢", "🔴", "🔵"], "🔴"),
        bild(p, "Die Fußgänger-Ampel ist rot. Was machst du?", ["🧍", "🚶", "🏃"], "🧍"),
        stimmt(p, "Auch bei Grün schaue ich nach links und rechts.", True, "👀"),
        stimmt(p, "Bei Rot renne ich schnell über die Straße.", False, "🔴"),
        bild(p, "Welches Schild sagt: Stopp, anhalten!", ["🛑", "🚸", "🚲"], "🛑"),
        bild(p, "Welches Schild sagt: Achtung, Kinder!", ["🚸", "🛑", "⛔"], "🚸"),
    ]),
    lesson("Über die Straße", "🦓", [
        bild(p, "Wo gehst du sicher über die Straße?", ["🦓", "🌳", "🚗"], "🦓"),
        bildreihe(p, "Wie gehst du über die Straße? Leg die Bilder der Reihe nach!", ["🧍", "👀", "🚶"],
                  "Erst stehen bleiben, dann nach links und rechts schauen, dann gehen."),
        stimmt(p, "Am Zebrastreifen schaue ich erst nach links und rechts.", True, "🦓"),
        stimmt(p, "Zwischen parkenden Autos kann ich gut über die Straße gehen.", False, "🚗"),
        stimmt(p, "Ich spiele nicht auf der Straße.", True, "⚽"),
        stimmt(p, "Ich gehe auf dem Gehweg.", True, "🚶"),
    ]),
    lesson("Gut sichtbar", "🦺", [
        bild(p, "Es ist dunkel. Was hilft, damit Autofahrer dich sehen?", ["🦺", "🕶️", "🧢"], "🦺"),
        stimmt(p, "Helle Kleidung sieht man im Dunkeln besser.", True, "🌙"),
        stimmt(p, "Beim Fahrradfahren trage ich einen Helm.", True, "🚲"),
        stimmt(p, "Im Auto schnalle ich mich immer an.", True, "🚗"),
        stimmt(p, "Dunkle Kleidung sieht man im Dunkeln gut.", False, "🌙"),
    ]),
    test(10),
])

# ---------- Forschen ----------
p = "h1-forschen"
UNITS["hsu/k1-forschen.json"] = unit(p, "Forschen: Magnet und Wasser", "🧲", "#7a4fd6", [
    lesson("Was zieht der Magnet an?", "🧲", [
        bildsort(p, "Zieht der Magnet das an?", ["🧲 zieht er an", "❌ zieht er nicht an"], [
            ("📎", "Büroklammer", "🧲 zieht er an"), ("🪵", "Holz", "❌ zieht er nicht an"), ("🔩", "Schraube", "🧲 zieht er an"),
            ("🧸", "Teddy", "❌ zieht er nicht an"), ("🧷", "Sicherheitsnadel", "🧲 zieht er an"), ("✏️", "Bleistift", "❌ zieht er nicht an"),
            ("🪡", "Nadel", "🧲 zieht er an"), ("🍎", "Apfel", "❌ zieht er nicht an"),
        ]),
        stimmt(p, "Der Magnet zieht Dinge aus Eisen an.", True, "🧲"),
        stimmt(p, "Der Magnet zieht Holz an.", False, "🪵"),
    ], mix=False),
    lesson("Schwimmt oder sinkt?", "🦆", [
        bildsort(p, "Schwimmt das oder sinkt es?", ["🦆 schwimmt", "⚓ sinkt"], [
            ("🪵", "Holz", "🦆 schwimmt"), ("🪨", "Stein", "⚓ sinkt"), ("🍎", "Apfel", "🦆 schwimmt"),
            ("🔑", "Schlüssel", "⚓ sinkt"), ("🏐", "Ball", "🦆 schwimmt"), ("🔩", "Schraube", "⚓ sinkt"),
        ]),
        stimmt(p, "Ein Stein schwimmt auf dem Wasser.", False, "🪨"),
    ], mix=False),
    lesson("Wasser", "💧", [
        bild(p, "Was wird aus Wasser, wenn es sehr kalt ist?", ["🧊", "🔥", "🌈"], "🧊"),
        stimmt(p, "Wenn es sehr kalt ist, wird Wasser zu Eis.", True, "🧊"),
        stimmt(p, "Eis schmilzt in der warmen Sonne.", True, "☀️"),
        stimmt(p, "Salz verschwindet im Wasser, wenn man rührt.", True, "🧂"),
        stimmt(p, "Der Schneemann wird in der Sonne immer größer.", False, "⛄"),
    ]),
    test(10),
])

# =====================================================================
# 3. KLASSE
# =====================================================================

# ---------- Wasser ----------
p = "h3-wasser"
wissen("hsu-zustaende", "🧊", "Wasser hat drei Zustände", [
    "**fest**: Eis, Schnee, Hagel",
    "**flüssig**: Wasser, Regen, Tee",
    "**gasförmig**: **Wasserdampf**. Man kann ihn nicht sehen.",
    "Bei **0 °C** gefriert Wasser zu Eis. Bei **100 °C** kocht es.",
], ["Eis **schmilzt** → Wasser **gefriert** → Wasser **verdunstet**"], [f"{p}/Fest, flüssig, gasförmig"])
wissen("hsu-kreislauf", "🔁", "Der Wasserkreislauf", [
    "Die **Sonne** erwärmt das Wasser im Meer, in Seen und Flüssen.",
    "Das Wasser **verdunstet** und steigt als Wasserdampf nach oben.",
    "Oben ist es kalt: Es bilden sich winzige Tröpfchen, daraus werden **Wolken**.",
    "Werden die Tropfen schwer, fällt **Regen** oder Schnee.",
    "Das Wasser fließt über Bäche und **Flüsse** zurück ins Meer.",
], [], [f"{p}/Der Wasserkreislauf"])

UNITS["hsu/k3-wasser.json"] = unit(p, "Wasser", "💧", "#2f7fd1", [
    lesson("Fest, flüssig, gasförmig", "🧊", [
        sort(p, "Fest, flüssig oder gasförmig?", "Ist das fest, flüssig oder gasförmig?", ["fest", "flüssig", "gasförmig"], [
            ("Eiswürfel", "fest"), ("Regen", "flüssig"), ("Hagelkorn", "fest"), ("Wasserdampf", "gasförmig"),
            ("Apfelsaft", "flüssig"), ("Schneeflocke", "fest"), ("Wasser im See", "flüssig"), ("Eiszapfen", "fest"),
        ]),
        ch(p, "Wie heißt das?", "Eis wird zu Wasser. Das Eis …", ["schmilzt", "gefriert", "verdunstet"], "schmilzt", keep=True),
        ch(p, "Wie heißt das?", "Wasser wird zu Eis. Das Wasser …", ["schmilzt", "gefriert", "verdunstet"], "gefriert", keep=True),
        ch(p, "Wie heißt das?", "Wasser wird zu Wasserdampf. Das Wasser …", ["schmilzt", "gefriert", "verdunstet"], "verdunstet", keep=True),
        ch(p, "Was stimmt?", "Bei wie viel Grad gefriert Wasser?", ["0 °C", "10 °C", "100 °C"], "0 °C", keep=True),
        ch(p, "Was stimmt?", "Bei wie viel Grad kocht Wasser?", ["0 °C", "50 °C", "100 °C"], "100 °C", keep=True),
        wahr(p, "Eine nasse Pfütze trocknet in der Sonne, weil das Wasser verdunstet.", True),
        wahr(p, "Wasserdampf kann man gut sehen.", False, "Wasserdampf ist unsichtbar. Was man über dem Kochtopf sieht, sind schon wieder winzige Wassertröpfchen."),
    ], mix=False),
    lesson("Der Wasserkreislauf", "🔁", [
        reihe(p, "Bring den Wasserkreislauf in die richtige Reihenfolge!", [
            "Die Sonne erwärmt das Meer", "Wasser verdunstet", "Wolken entstehen", "Es regnet", "Flüsse fließen ins Meer"]),
        ch(p, "Was stimmt?", "Woraus bestehen Wolken?", ["aus winzigen Wassertröpfchen", "aus Rauch", "aus Watte"], "aus winzigen Wassertröpfchen"),
        ch(p, "Was stimmt?", "Was bringt das Wasser zum Verdunsten?", ["die Wärme der Sonne", "der Mond", "der Wind allein"], "die Wärme der Sonne"),
        ch(p, "Was stimmt?", "Wohin fließt das Wasser der Flüsse am Ende?", ["ins Meer", "in die Wolken", "in den Berg"], "ins Meer"),
        wahr(p, "Im Wasserkreislauf geht kein Wasser verloren.", True),
        wahr(p, "Regen entsteht, wenn die Tropfen in der Wolke zu schwer werden.", True),
        reihe(p, "Was passiert mit dem Schnee? Bring es in die richtige Reihenfolge!", [
            "Schnee liegt auf dem Berg", "Die Sonne scheint", "Der Schnee schmilzt", "Ein Bach fließt ins Tal"]),
    ], mix=False),
    lesson("Wasser im Alltag", "🚿", [
        sort(p, "Spart das Wasser?", "Spart das Wasser oder verschwendet es Wasser?", ["spart Wasser", "verschwendet Wasser"], [
            ("duschen statt baden", "spart Wasser"), ("Wasser laufen lassen beim Zähneputzen", "verschwendet Wasser"),
            ("Regenwasser zum Gießen sammeln", "spart Wasser"), ("tropfenden Wasserhahn nicht reparieren", "verschwendet Wasser"),
            ("Spülmaschine nur voll einschalten", "spart Wasser"), ("Spartaste an der Toilette drücken", "spart Wasser"),
        ]),
        reihe(p, "Wie kommt das Wasser zurück in den Fluss? Bring es in die richtige Reihenfolge!", [
            "Abwasser aus dem Haus", "Kanal", "Kläranlage", "sauberes Wasser in den Fluss"]),
        ch(p, "Was stimmt?", "Wo wird schmutziges Abwasser gereinigt?", ["in der Kläranlage", "im Wasserturm", "im Schwimmbad"], "in der Kläranlage"),
        ch(p, "Was stimmt?", "Woher kommt bei uns das meiste Trinkwasser?", ["aus dem Grundwasser", "aus dem Meer", "aus Pfützen"], "aus dem Grundwasser"),
        wahr(p, "Das Wasser aus dem Hahn wird regelmäßig geprüft.", True),
    ]),
    lesson("Wasser-Experimente", "🧪", [
        sort(p, "Löst es sich im Wasser auf?", "Löst sich das im Wasser auf?", ["löst sich auf", "löst sich nicht auf"], [
            ("Salz", "löst sich auf"), ("Zucker", "löst sich auf"), ("Sand", "löst sich nicht auf"),
            ("Kieselstein", "löst sich nicht auf"), ("Brausepulver", "löst sich auf"), ("Öl", "löst sich nicht auf"),
        ]),
        ch(p, "Was stimmt?", "Wie bekommst du Sand aus dem Wasser?", ["mit einem Filter", "durch Umrühren", "mit mehr Wasser"], "mit einem Filter"),
        ch(p, "Was stimmt?", "Du stellst ein Glas Wasser ins Gefrierfach. Was passiert?", ["Es wird zu Eis.", "Es verdunstet.", "Es kocht."], "Es wird zu Eis."),
        wahr(p, "Eis nimmt mehr Platz ein als Wasser. Darum kann eine volle Flasche im Gefrierfach platzen.", True),
        wahr(p, "Salzwasser kann man ohne Weiteres trinken.", False, "Salzwasser macht noch durstiger. Trinkwasser muss Süßwasser sein."),
    ]),
    test(12),
])

# ---------- Der Wald ----------
p = "h3-wald"
SCH = ["Wurzelschicht", "Moosschicht", "Krautschicht", "Strauchschicht", "Baumschicht"]
wissen("hsu-stockwerke", "🌲", "Die Stockwerke des Waldes", [
    "Der Wald ist aufgebaut wie ein Haus mit **Stockwerken**.",
    "Von unten nach oben: **Wurzelschicht**, **Moosschicht**, **Krautschicht**, **Strauchschicht**, **Baumschicht**.",
    "In jedem Stockwerk leben andere Pflanzen und Tiere.",
], ["Regenwurm → Wurzelschicht, Farn → Krautschicht, Specht → Baumschicht"], [f"{p}/Stockwerke des Waldes"])
wissen("hsu-nahrungskette", "🔗", "Die Nahrungskette", [
    "Am Anfang einer Nahrungskette stehen immer **Pflanzen**.",
    "**Pflanzenfresser** fressen Pflanzen, **Fleischfresser** fressen andere Tiere.",
    "**Allesfresser** fressen Pflanzen und Tiere, zum Beispiel das Wildschwein.",
], ["Blatt → Raupe → Meise → Sperber"], [f"{p}/Tiere im Wald"])
UNITS["hsu/k3-wald.json"] = unit(p, "Der Wald", "🌲", "#2e8b57", [
    lesson("Stockwerke des Waldes", "🏠", [
        reihe(p, "Ordne die Stockwerke des Waldes von unten nach oben!", SCH),
        sort(p, "In welchem Stockwerk findest du das?", "In welchem Stockwerk des Waldes findest du das?", SCH, [
            ("Regenwurm", "Wurzelschicht"), ("Moos", "Moosschicht"), ("Farn", "Krautschicht"), ("Haselnussstrauch", "Strauchschicht"),
            ("Fichte", "Baumschicht"), ("Pilz", "Moosschicht"), ("Walderdbeere", "Krautschicht"), ("Specht", "Baumschicht"),
            ("Holunder", "Strauchschicht"), ("Fuchsbau", "Wurzelschicht"),
        ]),
    ], mix=False),
    lesson("Bäume erkennen", "🌳", [
        sort(p, "Laubbaum oder Nadelbaum?", "Ist das ein Laubbaum oder ein Nadelbaum?", ["Laubbaum", "Nadelbaum"], [
            ("Eiche", "Laubbaum"), ("Fichte", "Nadelbaum"), ("Buche", "Laubbaum"), ("Kiefer", "Nadelbaum"),
            ("Ahorn", "Laubbaum"), ("Tanne", "Nadelbaum"), ("Birke", "Laubbaum"), ("Lärche", "Nadelbaum"),
        ]),
        pairs(p, "Welche Frucht gehört zu welchem Baum?", "Zu welchem Baum gehört diese Frucht?", [
            ("Eichel", "Eiche"), ("Buchecker", "Buche"), ("Kastanie", "Rosskastanie"), ("Propeller-Samen", "Ahorn"),
        ]),
        wahr(p, "Die Lärche ist ein Nadelbaum, der im Herbst seine Nadeln verliert.", True),
        ch(p, "Was stimmt?", "Woran erkennst du, wie alt ein gefällter Baum war?", ["an den Jahresringen", "an der Zahl der Äste", "an der Farbe der Rinde"], "an den Jahresringen"),
        ch(p, "Was stimmt?", "Bei welchem Baum hängen die Zapfen nach unten?", ["Fichte", "Tanne", "Eiche"], "Fichte",
           "Fichtenzapfen hängen nach unten, Tannenzapfen stehen aufrecht auf den Zweigen."),
    ], mix=False),
    lesson("Tiere im Wald", "🦌", [
        sort(p, "Was frisst das Tier?", "Ist das Tier ein Pflanzenfresser, Fleischfresser oder Allesfresser?", ["Pflanzenfresser", "Fleischfresser", "Allesfresser"], [
            ("Reh", "Pflanzenfresser"), ("Hirsch", "Pflanzenfresser"), ("Hase", "Pflanzenfresser"), ("Wildschwein", "Allesfresser"),
            ("Dachs", "Allesfresser"), ("Luchs", "Fleischfresser"), ("Habicht", "Fleischfresser"), ("Waldkauz", "Fleischfresser"),
        ]),
        reihe(p, "Bring die Nahrungskette in die richtige Reihenfolge!", ["Blatt", "Raupe", "Meise", "Sperber"]),
        reihe(p, "Bring die Nahrungskette in die richtige Reihenfolge!", ["Gras", "Maus", "Fuchs"]),
        ch(p, "Was stimmt?", "Welches Tier hält Winterschlaf?", ["Igel", "Reh", "Fuchs"], "Igel"),
        ch(p, "Was stimmt?", "Welches Tier hält Winterruhe? Es wacht im Winter ab und zu auf und frisst.", ["Eichhörnchen", "Igel", "Fledermaus"], "Eichhörnchen"),
        ch(p, "Was stimmt?", "Wie nennt man die Kinder vom Reh?", ["Kitz", "Frischling", "Welpe"], "Kitz"),
        ch(p, "Was stimmt?", "Wie nennt man die Kinder vom Wildschwein?", ["Frischlinge", "Kitze", "Fohlen"], "Frischlinge"),
    ], mix=False),
    lesson("Den Wald schützen", "🛡️", [
        wahr(p, "Im Wald darf man Müll liegen lassen, er verrottet ja.", False, "Plastik und Dosen verrotten erst nach sehr vielen Jahren. Tiere können sich daran verletzen."),
        wahr(p, "Bäume stellen Sauerstoff her, den wir zum Atmen brauchen.", True),
        wahr(p, "Im Wald soll man leise sein, um die Tiere nicht zu stören.", True),
        wahr(p, "Im Sommer darf man im Wald ein Lagerfeuer machen.", False, "Feuer im Wald ist verboten. Es kann schnell ein Waldbrand entstehen."),
        wahr(p, "Der Förster oder die Försterin kümmert sich um den Wald.", True),
        ch(p, "Was stimmt?", "Wozu ist der Wald wichtig?", ["Er liefert Holz und Sauerstoff.", "Er macht die Luft schmutzig.", "Er verbraucht das ganze Grundwasser."], "Er liefert Holz und Sauerstoff."),
    ]),
    test(12),
])

# ---------- Ernährung und Gesundheit ----------
p = "h3-ernaehrung"
wissen("hsu-pyramide", "🥦", "Die Ernährungspyramide", [
    "Unten steht, wovon du **viel** brauchst: **Getränke** wie Wasser, dann **Gemüse und Obst**.",
    "In der Mitte: **Brot, Nudeln, Kartoffeln**, darüber **Milch, Fleisch, Fisch und Eier**.",
    "Ganz oben steht, wovon du nur **wenig** brauchst: **Fett** und **Süßes**.",
    "Merke: **5 Portionen** Obst und Gemüse am Tag, und etwa **1 Liter** trinken.",
], [], [f"{p}/Die Ernährungspyramide"])
wissen("hsu-zaehne", "🦷", "Zähne putzen mit KAI", [
    "Putze **morgens und abends** etwa **2 bis 3 Minuten**.",
    "**K**auflächen, dann **A**ußenflächen, dann **I**nnenflächen.",
    "Zu viel Zucker und schlechtes Putzen machen **Karies**, also Löcher in den Zähnen.",
], [], [f"{p}/Zähne und Körperpflege"])
UNITS["hsu/k3-ernaehrung.json"] = unit(p, "Ernährung und Gesundheit", "🥗", "#3fa34d", [
    lesson("Die Ernährungspyramide", "🥦", [
        reihe(p, "Ordne die Ernährungspyramide: Wovon brauchst du am meisten? Fang unten an!", [
            "Wasser und Tee", "Gemüse und Obst", "Brot, Nudeln, Kartoffeln", "Milch, Fleisch, Fisch, Eier", "Öl und Butter", "Süßes und Knabberzeug"]),
        sort(p, "Wie viel davon?", "Wie viel solltest du davon essen oder trinken?", ["viel", "mäßig", "wenig"], [
            ("Wasser", "viel"), ("Gurke", "viel"), ("Apfel", "viel"), ("Vollkornbrot", "viel"), ("Käse", "mäßig"),
            ("Wurst", "mäßig"), ("Fisch", "mäßig"), ("Butter", "wenig"), ("Gummibärchen", "wenig"), ("Chips", "wenig"),
        ]),
    ], mix=False),
    lesson("Gesund essen und trinken", "🥪", [
        ch(p, "Was stimmt?", "Was trinkst du am besten bei Durst?", ["Wasser", "Cola", "Limonade"], "Wasser"),
        ch(p, "Was stimmt?", "Wie viele Portionen Obst und Gemüse sollst du am Tag essen?", ["5", "1", "10"], "5", keep=True),
        ch(p, "Was stimmt?", "Wie viel sollen Kinder in deinem Alter etwa am Tag trinken?", ["etwa 1 Liter", "etwa 1 Glas", "etwa 5 Liter"], "etwa 1 Liter"),
        ch(p, "Was stimmt?", "Welches Pausenbrot ist am gesündesten?", ["Vollkornbrot mit Käse und Gurke", "Weißbrot mit Schokocreme", "ein Schokoriegel"], "Vollkornbrot mit Käse und Gurke"),
        wahr(p, "Zucker steckt auch in Ketchup und Fruchtjoghurt.", True),
        wahr(p, "Vollkornbrot hält länger satt als Weißbrot.", True),
        wahr(p, "Ein Glas Saft zählt genauso viel wie ein Glas Wasser.", False, "Saft enthält viel Zucker. Gegen Durst ist Wasser am besten."),
    ]),
    lesson("Zähne und Körperpflege", "🪥", [
        ch(p, "Was stimmt?", "Wie oft am Tag putzt du mindestens die Zähne?", ["2-mal", "1-mal pro Woche", "nur wenn sie wehtun"], "2-mal"),
        ch(p, "Was stimmt?", "Wie lange solltest du die Zähne putzen?", ["2 bis 3 Minuten", "10 Sekunden", "eine halbe Stunde"], "2 bis 3 Minuten"),
        ch(p, "Was stimmt?", "Wofür steht KAI beim Zähneputzen?", ["Kauflächen, Außenflächen, Innenflächen", "Kopf, Arme, Innen", "Kamm, Apfel, Igel"], "Kauflächen, Außenflächen, Innenflächen"),
        ch(p, "Was stimmt?", "Was ist Karies?", ["Löcher in den Zähnen", "eine Zahnpasta", "ein Zahnarzt-Werkzeug"], "Löcher in den Zähnen"),
        wahr(p, "Händewaschen mit Seife schützt vor Krankheiten.", True),
        wahr(p, "Zum Händewaschen reichen 2 Sekunden.", False, "Wasche die Hände etwa 20 bis 30 Sekunden mit Seife."),
    ]),
    lesson("Bewegung und Schlaf", "🏃", [
        wahr(p, "Kinder sollten sich jeden Tag mindestens eine Stunde bewegen.", True),
        wahr(p, "Wer genug schläft, kann sich in der Schule besser konzentrieren.", True),
        wahr(p, "Kinder in deinem Alter brauchen etwa 10 Stunden Schlaf.", True),
        ch(p, "Was stimmt?", "Was passiert mit deinem Herz, wenn du rennst?", ["Es schlägt schneller.", "Es bleibt stehen.", "Es schlägt langsamer."], "Es schlägt schneller."),
        ch(p, "Was stimmt?", "Was hilft in einer Pause bei den Hausaufgaben?", ["sich kurz bewegen", "noch mehr am Handy spielen", "Süßigkeiten essen"], "sich kurz bewegen"),
    ]),
    test(12),
])

# ---------- Auge und Ohr ----------
p = "h3-sinne"
wissen("hsu-auge", "👁️", "So funktioniert das Auge", [
    "Licht fällt durch die **Pupille** ins Auge. Die **Iris** gibt dem Auge seine Farbe.",
    "Im Dunkeln wird die Pupille **größer**, im hellen Licht **kleiner**.",
    "Die **Linse** macht das Bild scharf. Auf der **Netzhaut** entsteht das Bild.",
    "Der **Sehnerv** leitet das Bild zum **Gehirn**.",
], [], [f"{p}/Das Auge"])
wissen("hsu-ohr", "👂", "So funktioniert das Ohr", [
    "Die **Ohrmuschel** fängt den Schall auf. Er läuft durch den **Gehörgang**.",
    "Das **Trommelfell** schwingt und gibt die Schwingung an die **Gehörknöchelchen** weiter: Hammer, Amboss, Steigbügel.",
    "In der **Schnecke** wird daraus ein Signal. Der **Hörnerv** bringt es zum Gehirn.",
], [], [f"{p}/Das Ohr"])
UNITS["hsu/k3-sinne.json"] = unit(p, "Auge und Ohr", "👂", "#c2417a", [
    lesson("Das Auge", "👁️", [
        pairs(p, "Was macht dieser Teil des Auges?", "Was macht dieser Teil des Auges?", [
            ("Pupille", "lässt Licht ins Auge"), ("Iris", "gibt dem Auge die Farbe"), ("Linse", "macht das Bild scharf"),
        ]),
        pairs(p, "Was macht dieser Teil des Auges?", "Was macht dieser Teil des Auges?", [
            ("Netzhaut", "hier entsteht das Bild"), ("Sehnerv", "leitet das Bild zum Gehirn"), ("Wimpern", "halten Staub ab"),
        ]),
        ch(p, "Was stimmt?", "Was passiert mit der Pupille im Dunkeln?", ["Sie wird größer.", "Sie wird kleiner.", "Sie bleibt gleich."], "Sie wird größer.", keep=True),
        ch(p, "Was stimmt?", "Was passiert mit der Pupille im hellen Licht?", ["Sie wird größer.", "Sie wird kleiner.", "Sie bleibt gleich."], "Sie wird kleiner.", keep=True),
        wahr(p, "Die Tränenflüssigkeit hält das Auge feucht und sauber.", True),
    ], mix=False),
    lesson("Das Ohr", "👂", [
        reihe(p, "Welchen Weg nimmt der Schall im Ohr? Bring ihn in die richtige Reihenfolge!", [
            "Ohrmuschel", "Gehörgang", "Trommelfell", "Gehörknöchelchen", "Schnecke", "Hörnerv"]),
        ch(p, "Was stimmt?", "Wie heißen die drei Gehörknöchelchen?", ["Hammer, Amboss, Steigbügel", "Hammer, Zange, Säge", "Löffel, Gabel, Messer"], "Hammer, Amboss, Steigbügel"),
        ch(p, "Was stimmt?", "Was beginnt zu schwingen, wenn Schall ankommt?", ["das Trommelfell", "die Ohrmuschel", "der Hörnerv"], "das Trommelfell"),
        wahr(p, "Im Innenohr sitzt auch der Gleichgewichtssinn.", True),
        wahr(p, "Mit dem Wattestäbchen tief im Ohr putzen ist gut.", False, "Damit schiebt man das Ohrenschmalz tiefer hinein und kann das Trommelfell verletzen."),
    ], mix=False),
    lesson("Augen und Ohren schützen", "🕶️", [
        sort(p, "Was schützt die Augen, was die Ohren?", "Schützt das die Augen oder die Ohren?", ["schützt die Augen", "schützt die Ohren"], [
            ("Sonnenbrille", "schützt die Augen"), ("Musik nicht zu laut hören", "schützt die Ohren"), ("Schutzbrille beim Werken", "schützt die Augen"),
            ("Gehörschutz bei Lärm", "schützt die Ohren"), ("bei gutem Licht lesen", "schützt die Augen"), ("Mütze bei kaltem Wind", "schützt die Ohren"),
        ]),
        wahr(p, "Sehr lauter Lärm kann das Gehör für immer schädigen.", True),
        wahr(p, "Man darf kurz direkt in die Sonne schauen.", False, "Das Sonnenlicht kann die Netzhaut schon in kurzer Zeit verletzen."),
    ], mix=False),
    lesson("Die fünf Sinne", "✋", [
        pairs(p, "Welches Sinnesorgan gehört zu welchem Sinn?", "Welcher Sinn gehört zu diesem Sinnesorgan?", [
            ("Auge", "sehen"), ("Ohr", "hören"), ("Nase", "riechen"), ("Zunge", "schmecken"), ("Haut", "fühlen"),
        ]),
        ch(p, "Was stimmt?", "Welchen Geschmack kann die Zunge erkennen?", ["sauer", "laut", "hell"], "sauer"),
        ch(p, "Was stimmt?", "Mit welcher Schrift lesen blinde Menschen mit den Fingern?", ["Brailleschrift", "Schreibschrift", "Druckschrift"], "Brailleschrift"),
        ch(p, "Was stimmt?", "Welcher Sinn warnt dich vor verdorbenem Essen?", ["Riechen", "Hören", "Sehen"], "Riechen"),
    ]),
    test(12),
])

# ---------- Fahrrad und Verkehr ----------
p = "h3-fahrrad"
wissen("hsu-fahrrad", "🚲", "Das verkehrssichere Fahrrad", [
    "**Zwei Bremsen**, die unabhängig voneinander funktionieren, und eine **Klingel**.",
    "Vorne ein **weißer Scheinwerfer** und ein weißer Rückstrahler.",
    "Hinten ein **rotes Rücklicht** und ein roter Rückstrahler.",
    "**Gelbe Rückstrahler** an den Pedalen und in den Speichen (oder weiße Streifen an den Reifen).",
], [], [f"{p}/Das verkehrssichere Fahrrad"])
wissen("hsu-radregeln", "🚦", "Regeln für Kinder auf dem Rad", [
    "Bis **8 Jahre** müssen Kinder auf dem **Gehweg** fahren, bis **10 Jahre** dürfen sie es.",
    "Wo keine Schilder und Ampeln sind, gilt **rechts vor links**.",
    "Vor dem Abbiegen: **umschauen**, **Handzeichen** geben, **einordnen**.",
    "Ein **Helm** ist keine Pflicht, schützt aber deinen Kopf.",
], [], [f"{p}/Regeln für Radfahrer"])
UNITS["hsu/k3-fahrrad.json"] = unit(p, "Fahrrad und Verkehr", "🚲", "#d6453d", [
    lesson("Das verkehrssichere Fahrrad", "🚲", [
        sort(p, "Muss das am Fahrrad sein?", "Muss das an einem verkehrssicheren Fahrrad sein?", ["muss dran sein", "braucht man nicht"], [
            ("Klingel", "muss dran sein"), ("zwei Bremsen", "muss dran sein"), ("weißes Licht vorne", "muss dran sein"),
            ("rotes Rücklicht", "muss dran sein"), ("Fahrradkorb", "braucht man nicht"), ("Gepäckträger", "braucht man nicht"),
            ("gelbe Pedal-Rückstrahler", "muss dran sein"), ("Fahrradständer", "braucht man nicht"),
        ]),
        pairs(p, "Welche Farbe hat das?", "Welche Farbe hat dieser Teil am Fahrrad?", [
            ("Scheinwerfer vorne", "weiß"), ("Rücklicht hinten", "rot"), ("Rückstrahler an den Pedalen", "gelb"),
        ]),
        ch(p, "Was stimmt?", "Wie viele Bremsen braucht ein Fahrrad?", ["2", "1", "keine"], "2", keep=True),
    ], mix=False),
    lesson("Verkehrszeichen", "🛑", [
        sort(p, "Wie sieht das Schild aus?", "Wie sieht dieses Verkehrszeichen aus?", ["Dreieck mit rotem Rand", "rund mit rotem Rand", "rund und blau"], [
            ("Achtung, Kinder!", "Dreieck mit rotem Rand"), ("Achtung, Baustelle!", "Dreieck mit rotem Rand"), ("Radweg", "rund und blau"),
            ("Gehweg", "rund und blau"), ("Fahrräder verboten", "rund mit rotem Rand"), ("Höchstens 30 km/h", "rund mit rotem Rand"),
        ]),
        ch(p, "Was bedeutet das Schild?", "Achteckiges rotes Schild mit dem Wort STOP", ["Anhalten und Vorfahrt lassen", "Hier ist ein Parkplatz", "Radweg"], "Anhalten und Vorfahrt lassen"),
        ch(p, "Was bedeutet das Schild?", "Rundes blaues Schild mit einem weißen Fahrrad", ["Radweg", "Fahrräder verboten", "Fahrradladen"], "Radweg"),
        ch(p, "Was bedeutet das Schild?", "Dreieck mit der Spitze nach unten, rot-weiß", ["Vorfahrt gewähren", "Vorfahrtstraße", "Einbahnstraße"], "Vorfahrt gewähren"),
        ch(p, "Was bedeutet das Schild?", "Gelbe Raute mit weißem Rand", ["Vorfahrtstraße", "Vorfahrt gewähren", "Baustelle"], "Vorfahrtstraße"),
        ch(p, "Was bedeutet das Schild?", "Rundes rotes Schild mit einem weißen Querbalken", ["Verbot der Einfahrt", "Radweg", "Parkplatz"], "Verbot der Einfahrt"),
        ch(p, "Was stimmt?", "Was sagen dreieckige Schilder mit rotem Rand?", ["Achtung, Gefahr!", "Hier ist etwas verboten.", "Das musst du tun."], "Achtung, Gefahr!"),
    ]),
    lesson("Regeln für Radfahrer", "🚦", [
        ch(p, "Was stimmt?", "Bis zu welchem Alter müssen Kinder mit dem Fahrrad auf dem Gehweg fahren?", ["bis 8 Jahre", "bis 5 Jahre", "bis 12 Jahre"], "bis 8 Jahre"),
        wahr(p, "Kinder bis 10 Jahre dürfen noch auf dem Gehweg fahren.", True),
        ch(p, "Was stimmt?", "An einer Kreuzung ohne Schilder und Ampel gilt …", ["rechts vor links", "links vor rechts", "wer schneller ist, darf zuerst"], "rechts vor links"),
        reihe(p, "Links abbiegen: Bring die Schritte in die richtige Reihenfolge!", [
            "nach hinten schauen", "linken Arm ausstrecken", "zur Mitte einordnen", "Gegenverkehr vorbeilassen", "abbiegen"]),
        wahr(p, "Freihändig fahren ist erlaubt, wenn gerade niemand kommt.", False, "Mindestens eine Hand muss immer am Lenker sein."),
        wahr(p, "Am Zebrastreifen steigst du ab und schiebst. Dann hast du Vorrang wie ein Fußgänger.", True),
        wahr(p, "Ein Helm ist keine Pflicht, schützt aber bei einem Sturz den Kopf.", True),
    ]),
    test(12),
])

# ---------- Karte und Himmelsrichtungen ----------
p = "h3-karte"
HR = ["Norden", "Osten", "Süden", "Westen"]
wissen("hsu-himmelsrichtungen", "🧭", "Die Himmelsrichtungen", [
    "Auf der Karte ist **Norden oben**, **Süden unten**, **Osten rechts** und **Westen links**.",
    "Merksatz im Uhrzeigersinn: **N**ie **O**hne **S**eife **W**aschen.",
    "Die Sonne geht im **Osten** auf, steht mittags im **Süden** und geht im **Westen** unter.",
    "Die **Kompassnadel** zeigt nach Norden.",
], [], [f"{p}/Himmelsrichtungen"])
wissen("hsu-karte", "🗺️", "Karten lesen", [
    "Die **Legende** erklärt, was die Zeichen und Farben auf der Karte bedeuten.",
    "Der **Maßstab** zeigt, wie stark verkleinert wurde: Bei **1 : 100** ist 1 cm auf der Karte 100 cm, also 1 m, in Wirklichkeit.",
    "Ein **Grundriss** ist eine Zeichnung **von oben**.",
], [], [f"{p}/Karten lesen"])
UNITS["hsu/k3-karte.json"] = unit(p, "Karte und Himmelsrichtungen", "🧭", "#2f7fd1", [
    lesson("Himmelsrichtungen", "🧭", [
        ch(p, "Was stimmt?", "Welche Himmelsrichtung ist auf der Karte oben?", HR, "Norden", keep=True),
        ch(p, "Was stimmt?", "Welche Himmelsrichtung ist auf der Karte rechts?", HR, "Osten", keep=True),
        ch(p, "Was stimmt?", "Welche Himmelsrichtung ist auf der Karte links?", HR, "Westen", keep=True),
        ch(p, "Was stimmt?", "Welche Himmelsrichtung ist auf der Karte unten?", HR, "Süden", keep=True),
        ch(p, "Was stimmt?", "Wo geht die Sonne auf?", HR, "Osten", keep=True),
        ch(p, "Was stimmt?", "Wo geht die Sonne unter?", HR, "Westen", keep=True),
        ch(p, "Was stimmt?", "Wo steht die Sonne bei uns mittags?", HR, "Süden", keep=True),
        reihe(p, "Ordne im Uhrzeigersinn und fang mit Norden an!", HR),
    ], mix=False),
    lesson("Zwischen den Richtungen", "↗️", [
        ch(p, "Was stimmt?", "Zwischen Norden und Osten liegt …", ["Nordosten", "Südwesten", "Nordwesten"], "Nordosten"),
        ch(p, "Was stimmt?", "Zwischen Süden und Westen liegt …", ["Südosten", "Südwesten", "Nordwesten"], "Südwesten"),
        ch(p, "Was stimmt?", "Zwischen Norden und Westen liegt …", ["Nordwesten", "Nordosten", "Südosten"], "Nordwesten"),
        ch(p, "Was stimmt?", "Was liegt genau gegenüber von Nordosten?", ["Südwesten", "Südosten", "Nordwesten"], "Südwesten"),
        ch(p, "Was stimmt?", "Du schaust nach Norden und drehst dich ganz um. Wohin schaust du jetzt?", HR, "Süden", keep=True),
        ch(p, "Was stimmt?", "Du schaust nach Norden. Welche Richtung ist rechts von dir?", HR, "Osten", keep=True),
        ch(p, "Was stimmt?", "Du schaust nach Süden. Welche Richtung ist rechts von dir?", HR, "Westen", keep=True),
    ]),
    lesson("Karten lesen", "🗺️", [
        ch(p, "Was stimmt?", "Wo steht, was die Zeichen auf der Karte bedeuten?", ["in der Legende", "im Maßstab", "auf dem Kompass"], "in der Legende"),
        ch(p, "Was stimmt?", "Was zeigt der Maßstab?", ["wie stark die Wirklichkeit verkleinert ist", "wo Norden ist", "wie das Wetter wird"], "wie stark die Wirklichkeit verkleinert ist"),
        ch(p, "Was stimmt?", "Maßstab 1 : 100. Wie lang ist 1 cm auf der Karte in Wirklichkeit?", ["100 cm, also 1 m", "1 cm", "100 km"], "100 cm, also 1 m"),
        ch(p, "Was stimmt?", "Welche Farbe hat Wasser meistens auf Karten?", ["blau", "rot", "gelb"], "blau"),
        ch(p, "Was stimmt?", "Welche Farbe hat Wald meistens auf Karten?", ["grün", "blau", "lila"], "grün"),
        ch(p, "Was stimmt?", "Was ist ein Grundriss?", ["eine Zeichnung von oben", "ein Foto von der Seite", "eine Zeichnung von unten"], "eine Zeichnung von oben"),
        wahr(p, "Ein Stadtplan zeigt mehr Einzelheiten als eine Deutschlandkarte.", True),
        wahr(p, "Die Kompassnadel zeigt immer nach Süden.", False, "Die Kompassnadel zeigt nach Norden."),
    ]),
    test(12),
])

# ---------- Bayern und unsere Gemeinde ----------
p = "h3-bayern"
wissen("hsu-bayern", "🦁", "Bayern", [
    "Die **Landeshauptstadt** von Bayern ist **München**.",
    "Bayern hat **7 Regierungsbezirke**: Oberbayern, Niederbayern, Oberpfalz, Oberfranken, Mittelfranken, Unterfranken und Schwaben.",
    "Der höchste Berg ist die **Zugspitze** (fast 3000 m), der größte See der **Chiemsee**.",
    "Große Flüsse: **Donau**, **Main**, **Isar**, **Inn** und **Lech**.",
], [], [f"{p}/Bayern auf der Karte"])
wissen("hsu-gemeinde", "🏛️", "Unsere Gemeinde", [
    "Der **Bürgermeister** oder die **Bürgermeisterin** leitet die Gemeinde und arbeitet im **Rathaus**.",
    "Der **Gemeinderat** entscheidet zusammen über wichtige Dinge.",
    "In Bayern werden Bürgermeister und Gemeinderat alle **6 Jahre** gewählt.",
    "Die Gemeinde kümmert sich zum Beispiel um **Spielplätze**, **Schulgebäude**, **Straßen** und die **Feuerwehr**.",
], [], [f"{p}/Unsere Gemeinde"])
UNITS["hsu/k3-bayern.json"] = unit(p, "Bayern und unsere Gemeinde", "🦁", "#3b6fd8", [
    lesson("Bayern auf der Karte", "🗺️", [
        pairs(p, "Welche Stadt ist die Hauptstadt des Regierungsbezirks?", "Wie heißt die Hauptstadt dieses Regierungsbezirks?", [
            ("Oberbayern", "München"), ("Niederbayern", "Landshut"), ("Oberpfalz", "Regensburg"), ("Schwaben", "Augsburg"),
        ]),
        pairs(p, "Welche Stadt ist die Hauptstadt des Regierungsbezirks?", "Wie heißt die Hauptstadt dieses Regierungsbezirks?", [
            ("Oberfranken", "Bayreuth"), ("Mittelfranken", "Ansbach"), ("Unterfranken", "Würzburg"),
        ]),
        ch(p, "Was stimmt?", "Wie heißt die Landeshauptstadt von Bayern?", ["München", "Nürnberg", "Augsburg"], "München"),
        ch(p, "Was stimmt?", "Wie viele Regierungsbezirke hat Bayern?", ["7", "3", "16"], "7"),
        ch(p, "Was stimmt?", "Welche Farben hat die bayerische Flagge?", ["weiß und blau", "schwarz, rot, gold", "rot und weiß"], "weiß und blau"),
        ch(p, "Was stimmt?", "Welches Land grenzt im Süden an Bayern?", ["Österreich", "Frankreich", "Polen"], "Österreich"),
        ch(p, "Was stimmt?", "Welches Land grenzt im Osten an Bayern?", ["Tschechien", "Italien", "Dänemark"], "Tschechien"),
    ], mix=False),
    lesson("Berge, Flüsse und Seen", "🏔️", [
        ch(p, "Was stimmt?", "Wie heißt der höchste Berg Deutschlands?", ["Zugspitze", "Watzmann", "Brocken"], "Zugspitze"),
        ch(p, "Was stimmt?", "Wie hoch ist die Zugspitze ungefähr?", ["fast 3000 m", "etwa 300 m", "etwa 8000 m"], "fast 3000 m"),
        ch(p, "Was stimmt?", "Welcher ist der größte See in Bayern?", ["Chiemsee", "Starnberger See", "Ammersee"], "Chiemsee"),
        ch(p, "Was stimmt?", "Welcher Fluss fließt durch München?", ["Isar", "Main", "Rhein"], "Isar"),
        ch(p, "Was stimmt?", "Welcher Fluss fließt durch Regensburg?", ["Donau", "Isar", "Elbe"], "Donau"),
        ch(p, "Was stimmt?", "Welcher Fluss fließt durch Würzburg?", ["Main", "Inn", "Donau"], "Main"),
        wahr(p, "Die Donau fließt bis ins Schwarze Meer.", True),
    ]),
    lesson("Unsere Gemeinde", "🏛️", [
        ch(p, "Was stimmt?", "Wer leitet die Gemeinde?", ["der Bürgermeister oder die Bürgermeisterin", "der Pfarrer", "die Schulleiterin"], "der Bürgermeister oder die Bürgermeisterin"),
        ch(p, "Was stimmt?", "Wo arbeitet der Bürgermeister?", ["im Rathaus", "im Landtag", "im Bundestag"], "im Rathaus"),
        ch(p, "Was stimmt?", "Wer wählt den Gemeinderat?", ["die erwachsenen Bürgerinnen und Bürger", "nur die Kinder", "der Bürgermeister allein"], "die erwachsenen Bürgerinnen und Bürger"),
        ch(p, "Was stimmt?", "Wie oft wird der Gemeinderat in Bayern gewählt?", ["alle 6 Jahre", "jedes Jahr", "alle 20 Jahre"], "alle 6 Jahre"),
        sort(p, "Ist das eine Aufgabe der Gemeinde?", "Ist das eine Aufgabe der Gemeinde?", ["Aufgabe der Gemeinde", "keine Aufgabe der Gemeinde"], [
            ("Spielplätze bauen", "Aufgabe der Gemeinde"), ("Schulgebäude pflegen", "Aufgabe der Gemeinde"), ("Gemeindestraßen reparieren", "Aufgabe der Gemeinde"),
            ("Freiwillige Feuerwehr ausrüsten", "Aufgabe der Gemeinde"), ("Hausaufgaben kontrollieren", "keine Aufgabe der Gemeinde"),
            ("dein Zimmer aufräumen", "keine Aufgabe der Gemeinde"),
        ]),
    ]),
    test(12),
])

# ---------- Früher und heute ----------
p = "h3-zeit"
wissen("hsu-zeit", "⏳", "Zeit messen und ordnen", [
    "1 **Jahrzehnt** = 10 Jahre, 1 **Jahrhundert** = 100 Jahre, 1 **Jahrtausend** = 1000 Jahre.",
    "Wir leben im **21. Jahrhundert** (ab dem Jahr 2001). Die Jahre 1901 bis 2000 waren das 20. Jahrhundert.",
    "Auf einer **Zeitleiste** steht das Ältere links, das Neuere rechts.",
    "Was wir über früher wissen, erfahren wir aus **Quellen**: alte Fotos, Briefe, Gegenstände, Erzählungen.",
], [], [f"{p}/Zeitbegriffe"])
UNITS["hsu/k3-zeit.json"] = unit(p, "Früher und heute", "⏳", "#a0663a", [
    lesson("Zeitbegriffe", "⏳", [
        ch(p, "Was stimmt?", "Wie viele Jahre hat ein Jahrzehnt?", ["10", "100", "1000"], "10", keep=True),
        ch(p, "Was stimmt?", "Wie viele Jahre hat ein Jahrhundert?", ["10", "100", "1000"], "100", keep=True),
        ch(p, "Was stimmt?", "Wie viele Jahre hat ein Jahrtausend?", ["10", "100", "1000"], "1000", keep=True),
        ch(p, "Was stimmt?", "In welchem Jahrhundert leben wir?", ["im 21. Jahrhundert", "im 20. Jahrhundert", "im 19. Jahrhundert"], "im 21. Jahrhundert"),
        ch(p, "Was stimmt?", "Zu welchem Jahrhundert gehört das Jahr 1990?", ["zum 20. Jahrhundert", "zum 19. Jahrhundert", "zum 21. Jahrhundert"], "zum 20. Jahrhundert"),
        ty(p, "Rechne!", "Wie viele Jahre sind 3 Jahrzehnte?", "30"),
        wahr(p, "Deine Großeltern gehören zu einer anderen Generation als du.", True),
    ], mix=False),
    lesson("Die Zeitleiste", "📏", [
        reihe(p, "Bring in die richtige Reihenfolge: von früher nach heute!", ["Steinzeit", "Römer", "Ritter und Burgen", "erste Autos", "Smartphone"]),
        reihe(p, "Licht im Haus: Ordne von früher nach heute!", ["Kerze", "Petroleumlampe", "Glühbirne", "LED-Lampe"]),
        reihe(p, "Nachrichten schicken: Ordne von früher nach heute!", ["Brief mit der Postkutsche", "Telefon mit Schnur", "Handy", "Videoanruf"]),
        ch(p, "Was stimmt?", "Was gab es in der Steinzeit noch nicht?", ["Werkzeuge aus Metall", "Feuer", "Faustkeile aus Stein"], "Werkzeuge aus Metall"),
        ch(p, "Was stimmt?", "Was gab es zuerst?", ["die Dampflok", "den ICE", "das Elektroauto von heute"], "die Dampflok"),
    ]),
    lesson("Früher und heute", "👵", [
        sort(p, "Früher oder heute?", "War das früher so oder ist das heute so?", ["früher", "heute"], [
            ("auf einer Schiefertafel schreiben", "früher"), ("mit dem Tablet lernen", "heute"), ("mit Kohle den Ofen heizen", "früher"),
            ("Heizung mit Thermostat", "heute"), ("in der Telefonzelle anrufen", "früher"), ("mit dem Handy anrufen", "heute"),
            ("Wäsche auf dem Waschbrett schrubben", "früher"), ("Waschmaschine", "heute"),
        ]),
        ch(p, "Was stimmt?", "Woher wissen wir, wie die Menschen früher gelebt haben?", ["aus alten Fotos, Briefen und Funden", "aus Zeichentrickfilmen", "aus der Wettervorhersage"], "aus alten Fotos, Briefen und Funden"),
        ch(p, "Was stimmt?", "Wie nennt man alte Fotos, Briefe und Gegenstände, aus denen wir etwas über früher lernen?", ["Quellen", "Rezepte", "Gutscheine"], "Quellen"),
        wahr(p, "Deine Großeltern können dir als Zeitzeugen von früher erzählen.", True),
    ], mix=False),
    test(12),
])

# ---------- Strom ----------
p = "h3-strom"
wissen("hsu-stromkreis", "💡", "Der Stromkreis", [
    "Ein einfacher Stromkreis braucht eine **Batterie**, **Kabel** und ein Gerät, zum Beispiel eine **Lampe**.",
    "Die Lampe leuchtet nur, wenn der Stromkreis **geschlossen** ist.",
    "Ein **Schalter** öffnet und schließt den Stromkreis.",
    "**Leiter** lassen Strom durch: Metalle wie Eisen, Kupfer, Alufolie. **Nichtleiter** nicht: Holz, Kunststoff, Glas, Gummi.",
], [], [f"{p}/Der Stromkreis"])
wissen("hsu-stromgefahr", "⚠️", "Strom kann gefährlich sein", [
    "Mit einer **4,5-Volt-Batterie** darfst du gefahrlos experimentieren.",
    "Strom aus der **Steckdose** (230 Volt) ist **lebensgefährlich**.",
    "Elektrische Geräte gehören **nie** in die Nähe von **Wasser**.",
], [], [f"{p}/Sicher mit Strom"])
UNITS["hsu/k3-strom.json"] = unit(p, "Strom", "⚡", "#e8a317", [
    lesson("Der Stromkreis", "💡", [
        ch(p, "Was stimmt?", "Wann leuchtet die Lampe?", ["wenn der Stromkreis geschlossen ist", "wenn der Stromkreis offen ist", "wenn die Batterie leer ist"], "wenn der Stromkreis geschlossen ist"),
        ch(p, "Was stimmt?", "Was braucht ein einfacher Stromkreis?", ["Batterie, Kabel und Lampe", "nur eine Lampe", "Wasser und Holz"], "Batterie, Kabel und Lampe"),
        ch(p, "Was stimmt?", "Was macht ein Schalter?", ["Er öffnet und schließt den Stromkreis.", "Er macht Strom.", "Er macht die Lampe heller."], "Er öffnet und schließt den Stromkreis."),
        wahr(p, "Wenn ein Kabel nicht richtig angeschlossen ist, leuchtet die Lampe nicht.", True),
        wahr(p, "Eine Lampe leuchtet auch mit nur einem Kabel zur Batterie.", False, "Der Strom braucht einen geschlossenen Kreis: hin zur Lampe und wieder zurück zur Batterie."),
    ]),
    lesson("Leiter und Nichtleiter", "🔌", [
        sort(p, "Leitet das Strom?", "Leitet das Strom?", ["leitet Strom", "leitet nicht"], [
            ("Eisennagel", "leitet Strom"), ("Holzstab", "leitet nicht"), ("Kupferdraht", "leitet Strom"), ("Plastiklöffel", "leitet nicht"),
            ("Alufolie", "leitet Strom"), ("Radiergummi", "leitet nicht"), ("Büroklammer", "leitet Strom"), ("Glas", "leitet nicht"),
        ]),
        wahr(p, "Kabel sind mit Kunststoff umhüllt, damit man keinen Schlag bekommt.", True),
        ch(p, "Was stimmt?", "Wie nennt man Stoffe, die Strom nicht durchlassen?", ["Nichtleiter", "Leiter", "Batterien"], "Nichtleiter"),
    ], mix=False),
    lesson("Sicher mit Strom", "⚠️", [
        wahr(p, "Mit einer 4,5-Volt-Batterie kannst du gefahrlos experimentieren.", True),
        wahr(p, "An der Steckdose darf man experimentieren.", False, "Strom aus der Steckdose ist lebensgefährlich."),
        wahr(p, "Elektrische Geräte gehören nicht in die Nähe der Badewanne.", True),
        wahr(p, "Kaputte Kabel fasst man nicht an.", True),
        ch(p, "Was stimmt?", "Wie viel Volt hat eine Steckdose?", ["230 Volt", "4,5 Volt", "1,5 Volt"], "230 Volt"),
        ch(p, "Was stimmt?", "Womit kann man umweltfreundlich Strom erzeugen?", ["mit Sonne, Wind und Wasser", "mit Plastikmüll", "mit Sand"], "mit Sonne, Wind und Wasser"),
        sort(p, "Spart das Strom?", "Spart das Strom oder verschwendet es Strom?", ["spart Strom", "verschwendet Strom"], [
            ("Licht ausmachen, wenn man rausgeht", "spart Strom"), ("Fernseher im Stand-by lassen", "verschwendet Strom"),
            ("Kühlschranktür lange offen lassen", "verschwendet Strom"), ("Ladegerät nach dem Laden ausstecken", "spart Strom"),
        ]),
    ]),
    test(12),
])

# ---------- Klassenrat und Kinderrechte ----------
p = "h3-zusammen"
wissen("hsu-kinderrechte", "⚖️", "Kinderrechte", [
    "Die Kinderrechte stehen in der **UN-Kinderrechtskonvention**. Sie gelten für **alle Kinder** auf der Welt.",
    "Zum Beispiel: Recht auf **Bildung**, auf **Spiel und Freizeit**, auf **Gesundheit**, auf eine **eigene Meinung** und auf **Schutz vor Gewalt**.",
], [], [f"{p}/Kinderrechte"])
wissen("hsu-klassenrat", "🗳️", "Der Klassenrat", [
    "Im Klassenrat besprecht ihr Probleme und Wünsche der Klasse.",
    "Ein Kind **leitet**, eines schreibt das **Protokoll**, eines achtet auf die **Zeit**.",
    "Entschieden wird durch **Abstimmung**: Die **Mehrheit** gewinnt.",
], [], [f"{p}/Klassenrat"])
UNITS["hsu/k3-zusammen.json"] = unit(p, "Klassenrat und Kinderrechte", "⚖️", "#7a4fd6", [
    lesson("Kinderrechte", "⚖️", [
        wahr(p, "Jedes Kind hat das Recht, zur Schule zu gehen.", True),
        wahr(p, "Kinder haben ein Recht auf Spiel und Freizeit.", True),
        wahr(p, "Die Kinderrechte gelten nur für Jungen.", False, "Die Kinderrechte gelten für alle Kinder, egal ob Mädchen oder Junge, egal woher sie kommen."),
        wahr(p, "Kinder dürfen ihre Meinung sagen.", True),
        wahr(p, "Niemand darf Kinder schlagen.", True),
        ch(p, "Was stimmt?", "Wo sind die Kinderrechte aufgeschrieben?", ["in der UN-Kinderrechtskonvention", "in der Schulordnung", "in der Straßenverkehrsordnung"], "in der UN-Kinderrechtskonvention"),
    ]),
    lesson("Klassenrat", "🗳️", [
        ch(p, "Was stimmt?", "Was macht das Kind, das Protokoll führt?", ["Es schreibt die Beschlüsse auf.", "Es passt auf die Zeit auf.", "Es bestimmt alles allein."], "Es schreibt die Beschlüsse auf."),
        ch(p, "Was stimmt?", "Was macht der Zeitwächter?", ["Er achtet darauf, dass die Zeit reicht.", "Er schreibt alles auf.", "Er entscheidet allein."], "Er achtet darauf, dass die Zeit reicht."),
        ch(p, "Was stimmt?", "Wie wird im Klassenrat entschieden?", ["durch Abstimmung, die Mehrheit gewinnt", "der Lauteste entscheidet", "die Lehrkraft entscheidet immer allein"], "durch Abstimmung, die Mehrheit gewinnt"),
        ch(p, "Was stimmt?", "22 Kinder stimmen ab: 13 sind dafür, 9 dagegen. Was gilt?", ["Der Vorschlag ist angenommen.", "Der Vorschlag ist abgelehnt.", "Man muss nicht darauf hören."], "Der Vorschlag ist angenommen."),
        wahr(p, "Im Klassenrat darf jedes Kind seine Meinung sagen.", True),
    ]),
    lesson("Streit fair lösen", "🤝", [
        reihe(p, "Streit schlichten: Bring die Schritte in die richtige Reihenfolge!", [
            "Beide beruhigen sich", "Jeder erzählt, was passiert ist", "Gemeinsam Lösungen suchen", "Eine Lösung vereinbaren"]),
        sort(p, "Fair oder unfair?", "Ist das beim Streiten fair oder unfair?", ["fair", "unfair"], [
            ("ausreden lassen", "fair"), ("auslachen", "unfair"), ("zuhören", "fair"), ("beleidigen", "unfair"),
            ("Ich-Botschaften sagen", "fair"), ("jemanden ausschließen", "unfair"),
        ]),
        ch(p, "Was stimmt?", "Was ist eine Ich-Botschaft?", ["Ich bin traurig, weil du mich ausgelacht hast.", "Du bist immer so gemein!", "Halt den Mund!"], "Ich bin traurig, weil du mich ausgelacht hast."),
    ]),
    test(12),
])

# =====================================================================
# 3. KLASSE, RUNDE 2: Pflanzen, Bäume, Giftpflanzen, Sonne/Erde/Mond
# (Themenwahl nach LehrplanPLUS HSU 3/4, Texte und Aufgaben selbst geschrieben)
# =====================================================================

# ---------- Wie eine Pflanze entsteht ----------
p = "h3-pflanze"
wissen("hsu-bluete", "🌸", "Die Teile einer Blütenpflanze", [
    "Eine Blütenpflanze hat **Wurzel**, **Stängel**, **Blätter** und **Blüte**.",
    "Die **Wurzel** hält die Pflanze fest und nimmt Wasser auf.",
    "Die bunten **Kronblätter** locken Insekten an. Die grünen **Kelchblätter** schützen die Knospe.",
    "In den **Staubblättern** steckt der Blütenstaub (Pollen). In der Mitte steht der **Stempel**.",
], ["Blüte → Frucht → Samen → neue Pflanze"], [f"{p}/Die Teile einer Pflanze", f"{p}/Blüte und Bestäubung"])
wissen("hsu-bestaeubung", "🐝", "Von der Blüte zur Frucht", [
    "Eine Biene sammelt Nektar. Dabei bleibt **Blütenstaub** an ihr hängen.",
    "In der nächsten Blüte streift sie den Blütenstaub am **Stempel** ab. Das heißt **Bestäubung**.",
    "Danach wächst aus dem unteren Teil des Stempels die **Frucht** mit den **Samen**.",
    "Gräser, Haselnuss und Birke werden vom **Wind** bestäubt.",
], [], [f"{p}/Blüte und Bestäubung"])
wissen("hsu-keimung", "🌱", "Vom Samen zur Pflanze", [
    "Zum Keimen braucht ein Samen **Wasser**, **Wärme** und **Luft**.",
    "Zuerst quillt der Samen auf. Dann wächst die **Wurzel** nach unten.",
    "Danach wächst der **Spross** mit den ersten Blättern nach oben zum Licht.",
    "Im Samen steckt ein **Nahrungsvorrat** für den Anfang.",
], ["Samen → quellen → Wurzel → Spross → Blätter → Blüte"], [f"{p}/Vom Samen zur Pflanze"])
wissen("hsu-verbreitung", "🌬️", "Wie Samen reisen", [
    "**Wind**: Löwenzahn hat Schirmchen, der Ahorn hat Propeller.",
    "**Tiere**: Kletten bleiben im Fell hängen. Vögel fressen Beeren. Eichhörnchen verstecken Nüsse und vergessen manche.",
    "**Wasser**: Manche Samen schwimmen, zum Beispiel die Kokosnuss.",
    "**Selbst**: Das Springkraut schleudert seine Samen weg.",
], [], [f"{p}/Wie Samen reisen"])

UNITS["hsu/k3-pflanze.json"] = unit(p, "Wie eine Pflanze entsteht", "🌱", "#5a9e3a", [
    lesson("Die Teile einer Pflanze", "🌷", [
        reihe(p, "Ordne die Teile der Pflanze von unten nach oben!", ["Wurzel", "Stängel", "Blätter", "Blüte"]),
        pairs(p, "Was macht dieser Teil der Pflanze?", "Was macht dieser Teil der Pflanze?", [
            ("Wurzel", "hält fest und nimmt Wasser auf"), ("Stängel", "trägt Blätter und Blüte"),
            ("Blätter", "machen mit Sonnenlicht Nahrung"), ("Blüte", "daraus wird die Frucht"),
        ]),
        pairs(p, "Welcher Teil der Blüte ist das?", "Was macht dieser Teil der Blüte?", [
            ("Kronblätter", "bunt, locken Insekten an"), ("Kelchblätter", "grün, schützen die Knospe"),
            ("Staubblätter", "tragen den Blütenstaub"), ("Stempel", "in der Mitte, wird zur Frucht"),
        ]),
        wahr(p, "Die Wurzel holt Wasser aus der Erde.", True),
        wahr(p, "Die Blätter brauchen Licht, damit die Pflanze wachsen kann.", True),
        ch(p, "Was stimmt?", "Wie heißt der Blütenstaub noch?", ["Pollen", "Nektar", "Honig"], "Pollen"),
        ch(p, "Was stimmt?", "Warum sind viele Blüten so bunt?", ["Sie locken Insekten an.", "Sie wärmen die Pflanze.", "Sie schützen vor Regen."], "Sie locken Insekten an."),
    ], mix=False),
    lesson("Blüte und Bestäubung", "🐝", [
        reihe(p, "Von der Blüte zur Frucht: Bring es in die richtige Reihenfolge!", [
            "Die Blüte geht auf", "Eine Biene bringt Blütenstaub", "Die Kronblätter fallen ab", "Die Frucht wächst", "Die Samen sind reif"]),
        ch(p, "Was stimmt?", "Was heißt Bestäubung?", ["Blütenstaub kommt auf den Stempel einer Blüte.", "Die Blüte wird gegossen.", "Die Blätter werden staubig."], "Blütenstaub kommt auf den Stempel einer Blüte."),
        ch(p, "Was stimmt?", "Was sucht die Biene in der Blüte?", ["süßen Nektar", "Wasser", "Samen"], "süßen Nektar"),
        sort(p, "Wer bestäubt die Blüte?", "Wird diese Pflanze vom Wind oder von Insekten bestäubt?", ["Wind", "Insekten"], [
            ("Gras", "Wind"), ("Haselnuss", "Wind"), ("Birke", "Wind"), ("Apfelbaum", "Insekten"),
            ("Kirschbaum", "Insekten"), ("Sonnenblume", "Insekten"), ("Roggen", "Wind"), ("Klee", "Insekten"),
        ]),
        wahr(p, "Blüten, die der Wind bestäubt, sind meistens klein und unauffällig.", True, "Sie müssen keine Insekten anlocken. Dafür machen sie sehr viel Blütenstaub."),
        wahr(p, "Ohne Bienen gäbe es viel weniger Äpfel und Kirschen.", True),
        wahr(p, "Heuschnupfen kommt oft vom Blütenstaub der Gräser und Bäume.", True),
    ], mix=False),
    lesson("Vom Samen zur Pflanze", "🌱", [
        reihe(p, "Wie wächst eine Bohne? Bring es in die richtige Reihenfolge!", [
            "Bohnensamen in die Erde legen", "Der Samen quillt auf", "Die Wurzel wächst", "Der Spross kommt aus der Erde", "Die ersten Blätter wachsen"]),
        sort(p, "Was braucht ein Samen zum Keimen?", "Braucht ein Samen das zum Keimen?", ["braucht er", "braucht er nicht"], [
            ("Wasser", "braucht er"), ("Wärme", "braucht er"), ("Luft", "braucht er"),
            ("Dünger", "braucht er nicht"), ("Musik", "braucht er nicht"), ("viel Platz im Topf", "braucht er nicht"),
        ]),
        ch(p, "Was stimmt?", "Was wächst beim Keimen zuerst?", ["die Wurzel", "die Blüte", "die Frucht"], "die Wurzel"),
        ch(p, "Was stimmt?", "Woher bekommt der Keimling am Anfang seine Nahrung?", ["aus dem Vorrat im Samen", "von der Sonne allein", "aus dem Regen"], "aus dem Vorrat im Samen"),
        ch(p, "Was stimmt?", "Du legst Kresse auf trockene Watte. Was passiert?", ["Sie keimt nicht.", "Sie keimt sehr schnell.", "Sie blüht sofort."], "Sie keimt nicht.", "Ohne Wasser kann kein Samen keimen."),
        wahr(p, "Eine Bohne kann auch im Dunkeln keimen.", True, "Zum Keimen reichen Wasser, Wärme und Luft. Zum Weiterwachsen braucht die junge Pflanze dann aber Licht."),
        wahr(p, "Ein Samen im Eisfach keimt besonders gut.", False, "Es ist zu kalt. Samen brauchen Wärme zum Keimen."),
    ], mix=False),
    lesson("Wie Samen reisen", "🌬️", [
        sort(p, "Wie reist der Samen?", "Wie wird dieser Samen verbreitet?", ["Wind", "Tiere", "Wasser", "schleudert selbst"], [
            ("Löwenzahn mit Schirmchen", "Wind"), ("Ahorn mit Propeller", "Wind"), ("Klette im Fell", "Tiere"),
            ("Eichel, vom Eichhörnchen versteckt", "Tiere"), ("Kirsche, von der Amsel gefressen", "Tiere"),
            ("Kokosnuss", "Wasser"), ("Springkraut", "schleudert selbst"), ("Birkensamen mit Flügeln", "Wind"),
        ]),
        ch(p, "Was stimmt?", "Warum ist es gut, wenn Samen weit weg reisen?", ["Die jungen Pflanzen haben mehr Platz und Licht.", "Die Samen werden größer.", "Die Mutterpflanze wird schneller alt."], "Die jungen Pflanzen haben mehr Platz und Licht."),
        ch(p, "Was stimmt?", "Wie hilft ein Eichhörnchen der Eiche?", ["Es vergisst manche versteckte Eicheln. Daraus wachsen neue Eichen.", "Es gießt die Eiche.", "Es frisst die Blätter."], "Es vergisst manche versteckte Eicheln. Daraus wachsen neue Eichen."),
        wahr(p, "Kletten haben kleine Haken, mit denen sie im Fell hängen bleiben.", True),
        wahr(p, "Vögel fressen Beeren. Die Kerne kommen mit dem Kot an einer anderen Stelle wieder heraus.", True),
    ]),
    lesson("Pflanzen ohne Samen", "🍄", [
        sort(p, "Samen oder Sporen?", "Vermehrt sich diese Pflanze mit Samen oder mit Sporen?", ["Samen", "Sporen"], [
            ("Moos", "Sporen"), ("Farn", "Sporen"), ("Pilz", "Sporen"), ("Sonnenblume", "Samen"),
            ("Apfelbaum", "Samen"), ("Bohne", "Samen"), ("Tulpe", "Samen"),
        ]),
        ch(p, "Was stimmt?", "Was sind Sporen?", ["winzig kleine Körnchen, aus denen neue Pflanzen oder Pilze wachsen", "große Nüsse", "bunte Blütenblätter"], "winzig kleine Körnchen, aus denen neue Pflanzen oder Pilze wachsen"),
        ch(p, "Was stimmt?", "Wo findest du beim Farn die Sporen?", ["auf der Unterseite der Blätter", "in einer bunten Blüte", "in einer Frucht"], "auf der Unterseite der Blätter"),
        ch(p, "Was stimmt?", "Wie vermehrt sich die Erdbeere noch, außer mit Samen?", ["mit Ausläufern", "mit Sporen", "gar nicht"], "mit Ausläufern",
           "Erdbeeren bilden lange Triebe am Boden. Wo sie die Erde berühren, wächst eine neue Pflanze."),
        ch(p, "Was stimmt?", "Woraus wächst eine neue Kartoffelpflanze?", ["aus einer Kartoffelknolle", "aus Sporen", "aus einem Zapfen"], "aus einer Kartoffelknolle"),
        wahr(p, "Moose und Farne haben keine Blüten.", True),
    ]),
    test(12),
])

# ---------- Der Apfel ----------
p = "h3-apfel"
wissen("hsu-apfel", "🍎", "Der Apfel von innen", [
    "Außen ist die **Schale**, darunter das saftige **Fruchtfleisch**.",
    "In der Mitte liegt das **Kerngehäuse** mit den **Kernen**. Die Kerne sind die **Samen**.",
    "Oben ist der **Stiel**, unten der vertrocknete **Blütenrest**.",
    "Schneidest du einen Apfel quer durch, siehst du einen **Stern** mit fünf Kammern.",
], [], [f"{p}/Der Apfel von innen"])
wissen("hsu-apfeljahr", "🌸", "Das Jahr des Apfelbaums", [
    "**Frühling**: Der Apfelbaum blüht weiß und rosa. Bienen bestäuben die Blüten.",
    "**Sommer**: Aus der Blüte wächst ein kleiner grüner Apfel. Er wird immer größer.",
    "**Herbst**: Die Äpfel sind reif und werden geerntet.",
    "**Winter**: Der Baum ist kahl und ruht. Die Knospen sind schon da.",
], [], [f"{p}/Vom Apfelbaum"])
wissen("hsu-veredeln", "✂️", "Warum man Apfelbäume veredelt", [
    "Pflanzt du einen Apfelkern, wächst ein Baum mit **anderen** Äpfeln. Sie schmecken oft sauer.",
    "Darum **veredelt** der Gärtner: Er setzt einen Zweig der gewünschten Sorte auf einen jungen Baum.",
    "Der Zweig wächst an. Dann trägt der Baum genau die Äpfel dieser **Sorte**.",
], [], [f"{p}/Apfelsorten"])

UNITS["hsu/k3-apfel.json"] = unit(p, "Der Apfel", "🍎", "#d6453d", [
    lesson("Vom Apfelbaum", "🌳", [
        reihe(p, "Wie wächst ein Apfel? Bring es in die richtige Reihenfolge!", [
            "Knospen im Frühling", "Weiße und rosa Blüten", "Bienen bestäuben die Blüten", "Ein kleiner grüner Apfel wächst", "Der Apfel ist reif"]),
        sort(p, "Wann ist das beim Apfelbaum?", "Wann passiert das beim Apfelbaum?", ["Frühling", "Sommer", "Herbst", "Winter"], [
            ("Der Baum blüht.", "Frühling"), ("Die Äpfel wachsen und werden größer.", "Sommer"),
            ("Die Äpfel werden geerntet.", "Herbst"), ("Der Baum ist kahl und ruht.", "Winter"),
            ("Die Blätter werden gelb und fallen ab.", "Herbst"), ("Bienen fliegen von Blüte zu Blüte.", "Frühling"),
        ]),
        ch(p, "Was stimmt?", "Der Apfelbaum ist ein …", ["Laubbaum", "Nadelbaum", "Strauch"], "Laubbaum", keep=True),
        ch(p, "Was stimmt?", "Woraus wächst der Apfel?", ["aus der bestäubten Blüte", "aus einem Blatt", "aus der Wurzel"], "aus der bestäubten Blüte"),
        wahr(p, "Ohne Bienen und andere Insekten gäbe es kaum Äpfel.", True),
        ch(p, "Was stimmt?", "Was ist eine Streuobstwiese?", ["eine Wiese mit hohen Obstbäumen, die verstreut stehen", "ein Supermarkt für Obst", "ein Feld mit Erdbeeren"], "eine Wiese mit hohen Obstbäumen, die verstreut stehen"),
        wahr(p, "Auf einer Streuobstwiese leben viele Tiere, zum Beispiel Igel, Vögel und Bienen.", True),
    ], mix=False),
    lesson("Der Apfel von innen", "🔪", [
        pairs(p, "Welcher Teil des Apfels ist das?", "Welcher Teil des Apfels ist das?", [
            ("Schale", "schützt den Apfel außen"), ("Fruchtfleisch", "saftig, das essen wir"),
            ("Kerngehäuse", "in der Mitte, hält die Kerne"), ("Kerne", "die Samen des Apfels"),
        ]),
        reihe(p, "Ordne die Teile des Apfels von außen nach innen!", ["Schale", "Fruchtfleisch", "Kerngehäuse", "Kerne"]),
        ch(p, "Was stimmt?", "Was sind die Apfelkerne?", ["die Samen", "die Blüten", "die Blätter"], "die Samen"),
        ch(p, "Was stimmt?", "Was ist das kleine braune Ding unten am Apfel?", ["der Rest der Blüte", "ein Wurm", "der Stiel"], "der Rest der Blüte"),
        ch(p, "Was stimmt?", "Du schneidest einen Apfel quer durch. Was siehst du in der Mitte?", ["einen Stern", "einen Kreis ohne Kerne", "ein Herz"], "einen Stern"),
        ch(p, "Was stimmt?", "Warum wird ein aufgeschnittener Apfel braun?", ["Die Luft verändert das Fruchtfleisch.", "Er ist faul.", "Das Messer färbt ab."], "Die Luft verändert das Fruchtfleisch.",
           "Mit ein paar Tropfen Zitronensaft bleibt er länger hell."),
        wahr(p, "Ein Apfel ist eine Frucht.", True),
    ], mix=False),
    lesson("Apfelsorten", "🍏", [
        ch(p, "Was stimmt?", "Wie viele Apfelsorten gibt es auf der Welt ungefähr?", ["viele Tausend", "zehn", "genau hundert"], "viele Tausend"),
        sort(p, "Apfelsorte oder nicht?", "Ist das eine Apfelsorte?", ["Apfelsorte", "keine Apfelsorte"], [
            ("Elstar", "Apfelsorte"), ("Boskop", "Apfelsorte"), ("Gala", "Apfelsorte"), ("Braeburn", "Apfelsorte"),
            ("Granny Smith", "Apfelsorte"), ("Williams Christ (Birne)", "keine Apfelsorte"), ("Conference (Birne)", "keine Apfelsorte"),
        ]),
        ch(p, "Was stimmt?", "Welcher Apfel ist grün und sauer?", ["Granny Smith", "Gala", "Pink Lady"], "Granny Smith"),
        ch(p, "Was stimmt?", "Der Boskop ist sauer und eignet sich gut zum …", ["Backen", "Einfrieren", "Pflanzen"], "Backen"),
        ch(p, "Was stimmt?", "Du pflanzt einen Kern von einem Gala-Apfel. Was wächst daraus?", ["ein Apfelbaum mit anderen Äpfeln", "ein Baum mit Gala-Äpfeln", "ein Birnbaum"], "ein Apfelbaum mit anderen Äpfeln",
           "Aus dem Kern wächst eine neue Mischung. Darum veredelt man Apfelbäume."),
        ch(p, "Was stimmt?", "Was macht der Gärtner beim Veredeln?", ["Er setzt einen Zweig der Sorte auf einen jungen Baum.", "Er malt die Äpfel an.", "Er gießt mit Zuckerwasser."], "Er setzt einen Zweig der Sorte auf einen jungen Baum."),
        wahr(p, "Äpfel bleiben an einem kühlen, dunklen Ort lange frisch.", True),
    ]),
    lesson("Was man aus Äpfeln macht", "🧃", [
        sort(p, "Aus Äpfeln oder nicht?", "Wird das aus Äpfeln gemacht?", ["aus Äpfeln", "nicht aus Äpfeln"], [
            ("Apfelmus", "aus Äpfeln"), ("Apfelsaft", "aus Äpfeln"), ("Apfelstrudel", "aus Äpfeln"), ("Apfelessig", "aus Äpfeln"),
            ("Apfelringe, getrocknet", "aus Äpfeln"), ("Pommes", "nicht aus Äpfeln"), ("Ketchup", "nicht aus Äpfeln"), ("Kakao", "nicht aus Äpfeln"),
        ]),
        reihe(p, "Wie entsteht Apfelsaft? Bring es in die richtige Reihenfolge!", [
            "Äpfel ernten", "Äpfel waschen", "Äpfel zerkleinern", "Saft auspressen", "Saft erhitzen und abfüllen"]),
        reihe(p, "Wie kochst du Apfelmus? Bring es in die richtige Reihenfolge!", [
            "Äpfel schälen", "Kerngehäuse entfernen", "Stücke mit etwas Wasser kochen", "Weich gekochte Äpfel zerdrücken"]),
        ch(p, "Was stimmt?", "Was ist eine Apfelschorle?", ["Apfelsaft mit Wasser gemischt", "ein Apfelkuchen", "eine Apfelsorte"], "Apfelsaft mit Wasser gemischt"),
        wahr(p, "Äpfel aus der Region haben einen kurzen Weg bis in den Laden.", True),
    ]),
    test(12),
])

# ---------- Der Baum ----------
p = "h3-baum"
wissen("hsu-baumteile", "🌳", "Die Teile des Baumes", [
    "Die **Wurzeln** halten den Baum fest und holen Wasser aus dem Boden.",
    "Der **Stamm** trägt die Krone. In ihm steigt das Wasser nach oben.",
    "Die **Rinde** schützt den Stamm wie eine Haut.",
    "Die **Krone** besteht aus **Ästen**, **Zweigen** und **Blättern**.",
], ["Wurzeln → Stamm → Äste → Zweige → Blätter"], [f"{p}/Die Teile des Baumes"])
wissen("hsu-jahresringe", "🪵", "Jahresringe", [
    "Ein Baum wird jedes Jahr ein Stück dicker.",
    "Dabei entsteht jedes Jahr ein **Jahresring**: ein heller und ein dunkler Streifen.",
    "Zählst du die Ringe eines gefällten Baumes, weißt du, wie **alt** er war.",
    "Breite Ringe bedeuten ein gutes Jahr mit viel Regen, schmale Ringe ein trockenes Jahr.",
], [], [f"{p}/Wie alt ist der Baum?"])

UNITS["hsu/k3-baum.json"] = unit(p, "Der Baum", "🌳", "#3f8a3a", [
    lesson("Was ist ein Baum?", "🌳", [
        ch(p, "Was stimmt?", "Was hat ein Baum, das ein Strauch nicht hat?", ["einen einzigen dicken Stamm", "Blätter", "Wurzeln"], "einen einzigen dicken Stamm",
           "Ein Strauch hat viele dünne Stämme, die schon unten am Boden auseinandergehen."),
        sort(p, "Baum oder Strauch?", "Ist das ein Baum oder ein Strauch?", ["Baum", "Strauch"], [
            ("Eiche", "Baum"), ("Haselnuss", "Strauch"), ("Buche", "Baum"), ("Holunder", "Strauch"),
            ("Fichte", "Baum"), ("Himbeere", "Strauch"), ("Linde", "Baum"), ("Johannisbeere", "Strauch"),
        ]),
        sort(p, "Laubbaum oder Nadelbaum?", "Ist das ein Laubbaum oder ein Nadelbaum?", ["Laubbaum", "Nadelbaum"], [
            ("hat breite, flache Blätter", "Laubbaum"), ("hat Nadeln", "Nadelbaum"), ("ist im Winter meistens kahl", "Laubbaum"),
            ("ist im Winter meistens grün", "Nadelbaum"), ("trägt oft Zapfen", "Nadelbaum"), ("Linde", "Laubbaum"), ("Kiefer", "Nadelbaum"),
        ]),
        wahr(p, "Ein Baum ist eine Pflanze.", True),
        wahr(p, "Bäume haben einen Stamm aus Holz.", True),
    ], mix=False),
    lesson("Die Teile des Baumes", "🪵", [
        reihe(p, "Ordne die Teile des Baumes von unten nach oben!", ["Wurzeln", "Stamm", "Äste", "Zweige", "Blätter"]),
        pairs(p, "Was macht dieser Teil des Baumes?", "Was macht dieser Teil des Baumes?", [
            ("Wurzeln", "halten fest und holen Wasser"), ("Stamm", "trägt die Krone"),
            ("Rinde", "schützt den Stamm"), ("Blätter", "machen Nahrung aus Sonnenlicht"),
        ]),
        ch(p, "Was stimmt?", "Wie nennt man alle Äste, Zweige und Blätter zusammen?", ["die Krone", "den Stamm", "die Rinde"], "die Krone"),
        ch(p, "Was stimmt?", "Wie kommt das Wasser in die Blätter?", ["Es steigt von den Wurzeln durch den Stamm nach oben.", "Der Regen tropft hinein.", "Die Blätter trinken aus Pfützen."], "Es steigt von den Wurzeln durch den Stamm nach oben."),
        wahr(p, "Die Wurzeln eines Baumes können so weit reichen wie seine Krone.", True),
        wahr(p, "Wenn man die Rinde rundherum abschält, wird der Baum krank und kann sterben.", True),
    ], mix=False),
    lesson("Wie alt ist der Baum?", "⏳", [
        ch(p, "Was stimmt?", "Ein gefällter Baum hat 25 Jahresringe. Wie alt war er?", ["25 Jahre", "50 Jahre", "5 Jahre"], "25 Jahre"),
        ch(p, "Was stimmt?", "Wie viele Jahresringe bekommt ein Baum in einem Jahr?", ["einen", "zwei", "zwölf"], "einen", keep=True),
        ch(p, "Was stimmt?", "Ein Jahresring ist sehr schmal. Was bedeutet das?", ["Das Jahr war trocken.", "Das Jahr war besonders nass.", "Der Baum wurde gefällt."], "Das Jahr war trocken."),
        ch(p, "Was stimmt?", "Welcher heimische Baum kann über 800 Jahre alt werden?", ["die Eiche", "die Birke", "der Apfelbaum"], "die Eiche"),
        ty(p, "Rechne!", "Eine Linde wurde 1990 gepflanzt. Wie viele Jahresringe hat sie im Jahr 2026?", "36"),
        wahr(p, "Bäume hören nie ganz auf zu wachsen. Der Stamm wird jedes Jahr ein bisschen dicker.", True),
    ]),
    lesson("Warum wir Bäume brauchen", "💚", [
        sort(p, "Was geben uns Bäume?", "Tun Bäume das?", ["Bäume tun das", "Bäume tun das nicht"], [
            ("Sauerstoff zum Atmen herstellen", "Bäume tun das"), ("Schatten spenden", "Bäume tun das"),
            ("Tieren ein Zuhause geben", "Bäume tun das"), ("den Boden mit ihren Wurzeln festhalten", "Bäume tun das"),
            ("Holz liefern", "Bäume tun das"), ("die Luft schmutziger machen", "Bäume tun das nicht"), ("Strom erzeugen", "Bäume tun das nicht"),
        ]),
        sort(p, "Aus Holz oder nicht?", "Ist das meistens aus Holz gemacht?", ["aus Holz", "nicht aus Holz"], [
            ("Papier", "aus Holz"), ("Bleistift", "aus Holz"), ("Tisch", "aus Holz"), ("Brennholz", "aus Holz"),
            ("Glasflasche", "nicht aus Holz"), ("Löffel aus Metall", "nicht aus Holz"),
        ]),
        ch(p, "Was stimmt?", "Was nehmen die Blätter aus der Luft auf?", ["Kohlendioxid", "Sauerstoff", "Rauch"], "Kohlendioxid",
           "Die Blätter nehmen Kohlendioxid auf und geben Sauerstoff ab. Den brauchen wir zum Atmen."),
        ch(p, "Was stimmt?", "Warum pflanzt man in den Bergen Bäume an steilen Hängen?", ["Die Wurzeln halten den Boden fest.", "Damit es dunkler wird.", "Damit die Wanderer sich verlaufen."], "Die Wurzeln halten den Boden fest."),
        wahr(p, "Unter einem großen Baum ist es im Sommer kühler.", True),
        wahr(p, "Für jeden gefällten Baum sollte ein neuer gepflanzt werden.", True),
    ]),
    test(12),
])

# ---------- Laubbäume ----------
p = "h3-laub"
LB = ["Buche", "Eiche", "Birke", "Ahorn", "Eberesche", "Kastanie", "Linde"]
wissen("hsu-laubbaeume1", "🍂", "Buche, Eiche, Birke", [
    "**Buche**: ovale Blätter mit glattem, welligem Rand. Glatte graue Rinde. Früchte: **Bucheckern** in stacheliger Hülle.",
    "**Eiche**: Blätter mit runden Buchten. Rinde mit tiefen Rillen. Früchte: **Eicheln** mit Hütchen.",
    "**Birke**: kleine dreieckige Blätter mit gezacktem Rand. **Weiße Rinde** mit schwarzen Flecken.",
], [], [f"{p}/Buche, Eiche, Birke"])
wissen("hsu-laubbaeume2", "🍁", "Ahorn, Eberesche, Kastanie, Linde", [
    "**Ahorn**: Blatt wie eine Hand mit spitzen Zipfeln. Früchte mit **Propellern**.",
    "**Eberesche** (Vogelbeere): Blatt aus vielen kleinen Fiederblättchen. **Orangerote Beeren**, die Vögel gern fressen.",
    "**Kastanie** (Rosskastanie): Blatt wie eine Hand mit 5 bis 7 Fingern. Glänzende braune **Kastanien** in stacheliger Schale.",
    "**Linde**: **herzförmige** Blätter. Die Blüten duften und man macht Tee daraus.",
], [], [f"{p}/Ahorn, Eberesche, Kastanie, Linde"])
wissen("hsu-laubjahr", "🍂", "Laubbäume im Jahreslauf", [
    "**Frühling**: Die Knospen öffnen sich, junge Blätter und Blüten wachsen.",
    "**Sommer**: Die Krone ist dicht und grün. Die Früchte wachsen.",
    "**Herbst**: Die Blätter werden gelb, rot und braun und fallen ab.",
    "**Winter**: Der Baum ist kahl. Die Knospen für das nächste Jahr sind schon da.",
    "Im Winter ist der Boden oft gefroren. Ohne Blätter verliert der Baum kaum Wasser.",
], [], [f"{p}/Laubbäume im Jahreslauf"])

UNITS["hsu/k3-laubbaeume.json"] = unit(p, "Laubbäume", "🍂", "#c8741e", [
    lesson("Buche, Eiche, Birke", "🌳", [
        pairs(p, "Welche Frucht gehört zu welchem Baum?", "Zu welchem Baum gehört diese Frucht?", [
            ("Eichel mit Hütchen", "Eiche"), ("Buchecker", "Buche"), ("kleine Samen mit Flügelchen", "Birke"),
        ]),
        pairs(p, "Welches Blatt gehört zu welchem Baum?", "Zu welchem Baum gehört dieses Blatt?", [
            ("Blatt mit runden Buchten", "Eiche"), ("ovales Blatt mit glattem Rand", "Buche"), ("kleines dreieckiges Blatt mit Zacken", "Birke"),
        ]),
        ch(p, "Welcher Baum ist das?", "Seine Rinde ist weiß mit schwarzen Flecken.", ["Birke", "Buche", "Eiche"], "Birke"),
        ch(p, "Welcher Baum ist das?", "Seine Rinde ist glatt und grau wie die Haut eines Elefanten.", ["Buche", "Eiche", "Birke"], "Buche"),
        ch(p, "Welcher Baum ist das?", "Seine Rinde hat tiefe Rillen. Er kann viele Hundert Jahre alt werden.", ["Eiche", "Birke", "Buche"], "Eiche"),
        ch(p, "Was stimmt?", "Welcher Laubbaum wächst in Deutschland am häufigsten?", ["die Buche", "die Linde", "die Kastanie"], "die Buche"),
        wahr(p, "Wildschweine und Eichhörnchen fressen gern Eicheln und Bucheckern.", True),
    ], mix=False),
    lesson("Ahorn, Eberesche, Kastanie, Linde", "🍁", [
        pairs(p, "Welche Frucht gehört zu welchem Baum?", "Zu welchem Baum gehört diese Frucht?", [
            ("Propeller-Früchte", "Ahorn"), ("orangerote Beeren", "Eberesche"), ("glänzende braune Kugel in stacheliger Schale", "Kastanie"),
        ]),
        pairs(p, "Welches Blatt gehört zu welchem Baum?", "Zu welchem Baum gehört dieses Blatt?", [
            ("Blatt wie eine Hand mit spitzen Zipfeln", "Ahorn"), ("Blatt aus vielen kleinen Fiederblättchen", "Eberesche"),
            ("Blatt mit 5 bis 7 langen Fingern", "Kastanie"), ("herzförmiges Blatt", "Linde"),
        ]),
        ch(p, "Was stimmt?", "Warum heißt die Eberesche auch Vogelbeere?", ["Vögel fressen ihre Beeren gern.", "Sie sieht aus wie ein Vogel.", "Vögel bauen nur dort Nester."], "Vögel fressen ihre Beeren gern."),
        ch(p, "Was stimmt?", "Welches Blatt ist auf der Flagge von Kanada?", ["ein Ahornblatt", "ein Eichenblatt", "ein Lindenblatt"], "ein Ahornblatt"),
        wahr(p, "Die Kastanien von der Rosskastanie kann man wie Maronen essen.", False, "Rosskastanien sind bitter und machen Bauchweh. Maronen kommen von einem anderen Baum, der Esskastanie."),
        wahr(p, "Aus Lindenblüten kann man Tee kochen.", True),
    ], mix=False),
    lesson("Bäume zuordnen", "🔎", [
        sort(p, "Zu welchem Baum gehört das?", "Zu welchem Baum gehört das?", ["Eiche", "Buche", "Ahorn", "Kastanie"], [
            ("Eichel", "Eiche"), ("Blatt mit runden Buchten", "Eiche"), ("Buchecker", "Buche"), ("glatte graue Rinde", "Buche"),
            ("Propeller", "Ahorn"), ("Blatt mit spitzen Zipfeln", "Ahorn"), ("stachelige grüne Fruchtschale", "Kastanie"), ("Blatt mit 5 bis 7 Fingern", "Kastanie"),
        ]),
        sort(p, "Zu welchem Baum gehört das?", "Zu welchem Baum gehört das?", ["Birke", "Eberesche", "Linde"], [
            ("weiße Rinde", "Birke"), ("kleines dreieckiges Blatt", "Birke"), ("orangerote Beeren", "Eberesche"),
            ("gefiedertes Blatt", "Eberesche"), ("herzförmiges Blatt", "Linde"), ("duftende Blüten für Tee", "Linde"),
        ]),
        ch(p, "Welcher Baum ist das?", "Du findest im Herbst eine kleine dreikantige Nuss in einer stacheligen Hülle.", LB[:4], "Buche"),
        ch(p, "Welcher Baum ist das?", "Du findest ein Blatt, das aussieht wie ein Herz.", ["Linde", "Ahorn", "Eiche", "Birke"], "Linde"),
    ], mix=False),
    lesson("Laubbäume im Jahreslauf", "🍂", [
        reihe(p, "Ein Jahr beim Laubbaum: Bring es in die richtige Reihenfolge!", [
            "Die Knospen öffnen sich", "Der Baum blüht", "Die Krone ist dicht und grün", "Die Blätter werden bunt", "Der Baum ist kahl"]),
        sort(p, "Wann ist das?", "In welcher Jahreszeit ist das beim Laubbaum?", ["Frühling", "Sommer", "Herbst", "Winter"], [
            ("Junge hellgrüne Blätter wachsen.", "Frühling"), ("Die Krone gibt viel Schatten.", "Sommer"),
            ("Die Blätter werden gelb und rot.", "Herbst"), ("Der Baum hat keine Blätter.", "Winter"),
            ("Kastanien fallen herunter.", "Herbst"), ("Die Knospen öffnen sich.", "Frühling"),
        ]),
        ch(p, "Was stimmt?", "Warum werfen Laubbäume im Herbst ihre Blätter ab?", ["Im Winter würden sie über die Blätter zu viel Wasser verlieren.", "Die Blätter sind zu schwer.", "Der Wind reißt alle ab."], "Im Winter würden sie über die Blätter zu viel Wasser verlieren.",
           "Im Winter ist der Boden oft gefroren. Dann kommen die Wurzeln nicht an Wasser."),
        ch(p, "Was stimmt?", "Wann sind die Knospen für das nächste Frühjahr schon da?", ["schon im Herbst und Winter", "erst im Sommer", "gar nicht"], "schon im Herbst und Winter"),
        wahr(p, "Laub, das am Boden liegt, wird mit der Zeit zu guter Erde.", True),
        wahr(p, "Im Laubhaufen überwintern gern Igel.", True),
    ]),
    test(12),
])

# ---------- Nadelbäume ----------
p = "h3-nadel"
wissen("hsu-nadelbaeume", "🌲", "Nadelbäume erkennen", [
    "**Fichte**: spitze Nadeln rund um den Zweig, sie **stechen**. Die Zapfen **hängen** nach unten.",
    "**Tanne**: weiche, flache Nadeln mit zwei **weißen Streifen** unten. Die Zapfen **stehen** aufrecht und zerfallen am Baum.",
    "**Kiefer**: lange Nadeln, immer **zu zweit**. Kleine runde Zapfen.",
    "**Lärche**: weiche Nadeln in **Büscheln**. Sie wird im Herbst gelb und **wirft die Nadeln ab**.",
    "**Eibe**: weiche Nadeln, **keine Zapfen**, rote Beeren. Fast alles an ihr ist **giftig**.",
], ["Die Fichte sticht, die Tanne nicht."], [f"{p}/Nadelbäume kennenlernen", f"{p}/Nadeln und Zapfen"],
    trick="Die Fichte sticht, die Tanne nicht.")
wissen("hsu-nadelwinter", "❄️", "Nadelbäume im Winter", [
    "Die meisten Nadelbäume sind **immergrün**. Sie behalten ihre Nadeln mehrere Jahre.",
    "Nadeln sind schmal und haben eine **Wachsschicht**. So verlieren sie im Winter kaum Wasser.",
    "Die Äste sind biegsam, darum rutscht der **Schnee** ab.",
    "Die Samen liegen **frei** zwischen den Schuppen der Zapfen. Darum heißen Nadelbäume auch **Nacktsamer**.",
], [], [f"{p}/Nadelbäume im Winter"])

UNITS["hsu/k3-nadelbaeume.json"] = unit(p, "Nadelbäume", "🌲", "#1f6b45", [
    lesson("Nadelbäume kennenlernen", "🌲", [
        ch(p, "Was stimmt?", "Welcher Baum wächst in Deutschland am häufigsten?", ["die Fichte", "die Eibe", "die Lärche"], "die Fichte"),
        ch(p, "Was stimmt?", "Welcher Nadelbaum verliert im Herbst seine Nadeln?", ["die Lärche", "die Fichte", "die Tanne"], "die Lärche"),
        ch(p, "Was stimmt?", "Welcher Nadelbaum hat keine Zapfen, sondern rote Beeren?", ["die Eibe", "die Kiefer", "die Fichte"], "die Eibe"),
        ch(p, "Was stimmt?", "Woraus macht man oft Weihnachtsbäume?", ["aus Tannen und Fichten", "aus Birken", "aus Eichen"], "aus Tannen und Fichten"),
        wahr(p, "Alle Nadelbäume bleiben im Winter grün.", False, "Die Lärche wird im Herbst gelb und wirft ihre Nadeln ab."),
        wahr(p, "Nadeln sind auch Blätter, nur ganz schmal.", True),
    ], mix=False),
    lesson("Nadeln und Zapfen", "🔎", [
        pairs(p, "Welche Nadeln gehören zu welchem Baum?", "Zu welchem Baum gehören diese Nadeln?", [
            ("spitz, stechen, rund um den Zweig", "Fichte"), ("weich, flach, zwei weiße Streifen", "Tanne"),
            ("lang, immer zu zweit", "Kiefer"), ("weich, in Büscheln", "Lärche"),
        ]),
        pairs(p, "Welcher Zapfen gehört zu welchem Baum?", "Zu welchem Baum gehört dieser Zapfen?", [
            ("lang, hängt nach unten", "Fichte"), ("steht aufrecht und zerfällt am Baum", "Tanne"),
            ("klein und rund", "Kiefer"), ("gar kein Zapfen, rote Beeren", "Eibe"),
        ]),
        ch(p, "Was stimmt?", "Du gehst barfuß über Nadeln und es piekst sehr. Welcher Baum steht über dir?", ["Fichte", "Tanne", "Lärche"], "Fichte",
           "Merksatz: Die Fichte sticht, die Tanne nicht."),
        ch(p, "Was stimmt?", "Warum findet man am Boden fast nie ganze Tannenzapfen?", ["Sie zerfallen schon oben am Baum.", "Die Eichhörnchen nehmen alle mit.", "Tannen haben keine Zapfen."], "Sie zerfallen schon oben am Baum.",
           "Die meisten Zapfen, die man im Wald findet, sind Fichtenzapfen."),
        ch(p, "Was stimmt?", "Was steckt zwischen den Schuppen eines Zapfens?", ["die Samen", "Wasser", "Honig"], "die Samen"),
        ch(p, "Was stimmt?", "Warum heißen Nadelbäume auch Nacktsamer?", ["Ihre Samen liegen frei am Zapfen und stecken in keiner Frucht.", "Sie haben keine Rinde.", "Sie wachsen nur im Sommer."], "Ihre Samen liegen frei am Zapfen und stecken in keiner Frucht.",
           "Beim Apfel ist es anders: Seine Samen stecken in der Frucht. Solche Pflanzen heißen Bedecktsamer."),
        wahr(p, "Bei trockenem Wetter öffnen sich die Zapfen, bei Regen schließen sie sich.", True),
    ], mix=False),
    lesson("Nadelbäume im Winter", "❄️", [
        ch(p, "Was stimmt?", "Warum können Nadelbäume im Winter ihre Nadeln behalten?", ["Die Nadeln sind schmal und haben eine Wachsschicht.", "Die Nadeln sind aus Holz.", "Nadelbäume brauchen kein Wasser."], "Die Nadeln sind schmal und haben eine Wachsschicht."),
        ch(p, "Was stimmt?", "Was heißt immergrün?", ["Der Baum ist das ganze Jahr grün.", "Der Baum blüht immer.", "Der Baum wächst nur im Winter."], "Der Baum ist das ganze Jahr grün."),
        ch(p, "Was stimmt?", "Wie lange bleibt eine Fichtennadel ungefähr am Baum?", ["mehrere Jahre", "einen Tag", "nur einen Sommer"], "mehrere Jahre"),
        wahr(p, "Ein Nadelbaum verliert nie eine einzige Nadel.", False, "Er verliert immer wieder ein paar alte Nadeln, aber nie alle auf einmal."),
        wahr(p, "Die biegsamen Äste lassen den schweren Schnee abrutschen.", True),
        wahr(p, "Im Winter fressen Eichhörnchen und Vögel die Samen aus den Zapfen.", True),
    ]),
    lesson("Laub oder Nadel?", "🍂", [
        sort(p, "Laubbaum oder Nadelbaum?", "Ist das ein Laubbaum oder ein Nadelbaum?", ["Laubbaum", "Nadelbaum"], [
            ("Fichte", "Nadelbaum"), ("Tanne", "Nadelbaum"), ("Kiefer", "Nadelbaum"), ("Lärche", "Nadelbaum"), ("Eibe", "Nadelbaum"),
            ("Buche", "Laubbaum"), ("Birke", "Laubbaum"), ("Eberesche", "Laubbaum"), ("Linde", "Laubbaum"),
        ]),
        sort(p, "Nacktsamer oder Bedecktsamer?", "Liegen die Samen frei oder stecken sie in einer Frucht?", ["frei am Zapfen", "in einer Frucht"], [
            ("Fichte", "frei am Zapfen"), ("Kiefer", "frei am Zapfen"), ("Tanne", "frei am Zapfen"),
            ("Apfelbaum", "in einer Frucht"), ("Kirschbaum", "in einer Frucht"), ("Tomate", "in einer Frucht"),
        ]),
        wahr(p, "Die Lärche ist ein Nadelbaum, sieht im Winter aber kahl aus wie ein Laubbaum.", True),
    ], mix=False),
    test(12),
])

# ---------- Heimische Giftpflanzen ----------
p = "h3-gift"
wissen("hsu-giftregeln", "⚠️", "Regeln bei Giftpflanzen", [
    "Iss **nichts**, was du nicht sicher kennst. Frag immer einen Erwachsenen.",
    "Steck keine Blätter, Beeren oder Blüten in den Mund.",
    "Wasch dir nach dem Spielen in der Natur die **Hände**.",
    "Im Notfall: sofort einen **Erwachsenen** holen. Er ruft den **Giftnotruf** an (in Bayern 089 19240) oder im schlimmen Fall die **112**.",
    "Nimm einen Rest der Pflanze mit. Dann weiß der Arzt, was es war.",
    "**Nicht** erbrechen und **keine Milch** trinken. Am besten einen Schluck Wasser oder Tee.",
], [], [f"{p}/Was sind Giftpflanzen?"])
wissen("hsu-giftpflanzen", "☠️", "Giftpflanzen erkennen", [
    "**Maiglöckchen**: kleine weiße Glöckchen, später rote Beeren. Blätter sehen aus wie Bärlauch.",
    "**Fingerhut**: hohe Blütenstände mit lila Glocken.",
    "**Eisenhut**: blaue Blüten wie ein Helm. Eine der giftigsten Pflanzen Europas.",
    "**Herbstzeitlose**: lila Blüte im Herbst auf Wiesen.",
    "**Tollkirsche**: schwarze, glänzende Beeren wie Kirschen.",
    "**Eibe**, **Goldregen** (gelbe Blütentrauben) und **Pfaffenhütchen** (rosa Früchte) sind giftige Bäume und Sträucher.",
], [], [f"{p}/Kleine Giftpflanzen", f"{p}/Giftige Sträucher und Bäume"])
wissen("hsu-giftgemuese", "🥔", "Vorsicht bei Gemüse", [
    "**Bohnen** nie roh essen. Erst durch Kochen werden sie bekömmlich.",
    "Bei **Kartoffeln** grüne Stellen und Keime wegschneiden.",
    "**Grüne Tomaten** nicht essen. Nur rote, reife Tomaten.",
    "Beim **Rhabarber** nur die Stiele essen, nie die Blätter.",
    "**Holunderbeeren** nur gekocht essen, zum Beispiel als Saft.",
], ["Bärlauch riecht nach **Knoblauch**. Maiglöckchen riechen nicht danach."], [f"{p}/Giftiges Gemüse"])

UNITS["hsu/k3-giftpflanzen.json"] = unit(p, "Heimische Giftpflanzen", "⚠️", "#7a3fb0", [
    lesson("Was sind Giftpflanzen?", "⚠️", [
        ch(p, "Was stimmt?", "Was ist eine Giftpflanze?", ["eine Pflanze, die krank macht, wenn man sie isst oder berührt", "jede Pflanze mit Stacheln", "eine Pflanze, die nur im Dunkeln wächst"], "eine Pflanze, die krank macht, wenn man sie isst oder berührt"),
        sort(p, "Richtig oder falsch?", "Ist das richtig oder falsch?", ["richtig", "falsch"], [
            ("Unbekannte Beeren nie essen", "richtig"), ("Nach dem Spielen im Garten die Hände waschen", "richtig"),
            ("Einen Erwachsenen fragen, ob man etwas essen darf", "richtig"), ("Schöne Blüten probieren", "falsch"),
            ("Beeren essen, weil Vögel sie auch fressen", "falsch"), ("Blätter kauen, um zu sehen, wie sie schmecken", "falsch"),
        ]),
        reihe(p, "Dein Freund hat giftige Beeren gegessen. Was tust du? Bring es in die richtige Reihenfolge!", [
            "Einen Erwachsenen holen", "Der Erwachsene ruft den Giftnotruf an", "Einen Rest der Pflanze mitnehmen", "Zum Arzt fahren"]),
        ch(p, "Was stimmt?", "Was soll man bei einer Vergiftung NICHT tun?", ["Milch trinken und erbrechen", "einen Erwachsenen holen", "den Giftnotruf anrufen"], "Milch trinken und erbrechen"),
        ty(p, "Weißt du die Nummer?", "Wie lautet die Notrufnummer für Rettungsdienst und Feuerwehr?", "112"),
        wahr(p, "Was Vögel fressen, ist für Menschen auch ungefährlich.", False, "Vögel vertragen viele Beeren, die für Menschen giftig sind."),
        wahr(p, "Manche Pflanzen schaden schon, wenn man sie nur berührt.", True, "Zum Beispiel der Riesen-Bärenklau. Sein Saft macht in der Sonne schlimme Blasen auf der Haut."),
    ], mix=False),
    lesson("Kleine Giftpflanzen", "🌸", [
        pairs(p, "Welche Giftpflanze ist das?", "Welche Giftpflanze ist das?", [
            ("kleine weiße Glöckchen im Mai", "Maiglöckchen"), ("hohe Blüte mit vielen lila Glocken", "Fingerhut"),
            ("blaue Blüten wie ein Helm", "Eisenhut"), ("lila Blüte im Herbst auf der Wiese", "Herbstzeitlose"),
        ]),
        ch(p, "Was stimmt?", "Woran erkennst du Bärlauch und kannst ihn vom Maiglöckchen unterscheiden?", ["Bärlauch riecht nach Knoblauch.", "Bärlauch ist größer.", "Bärlauch ist blau."], "Bärlauch riecht nach Knoblauch.",
           "Trotzdem: Bärlauch nur mit einem Erwachsenen sammeln. Die Blätter sehen fast gleich aus."),
        ch(p, "Was stimmt?", "Welche Pflanze gilt als eine der giftigsten in Europa?", ["Eisenhut", "Gänseblümchen", "Löwenzahn"], "Eisenhut"),
        ch(p, "Was stimmt?", "Welche Farbe haben die Beeren vom Maiglöckchen?", ["rot", "blau", "weiß"], "rot"),
        ch(p, "Was stimmt?", "Der Aronstab hat im Sommer leuchtend … Beeren.", ["rote", "blaue", "weiße"], "rote", keep=True),
        wahr(p, "Beim Maiglöckchen sind alle Teile giftig.", True),
        wahr(p, "Der Fingerhut ist ungiftig, weil man ihn in Gärten pflanzt.", False, "Auch in Gärten wachsen viele Giftpflanzen. Der Fingerhut ist sehr giftig."),
    ], mix=False),
    lesson("Giftige Sträucher und Bäume", "🌳", [
        pairs(p, "Welche Giftpflanze ist das?", "Welche Giftpflanze ist das?", [
            ("schwarze, glänzende Beeren wie Kirschen", "Tollkirsche"), ("Nadelbaum mit roten Beeren", "Eibe"),
            ("gelbe, hängende Blütentrauben", "Goldregen"), ("rosa Früchte wie kleine Mützen", "Pfaffenhütchen"),
        ]),
        ch(p, "Was stimmt?", "Warum ist die Tollkirsche so gefährlich?", ["Ihre Beeren sehen aus wie leckere Kirschen.", "Sie hat Stacheln.", "Sie wächst nur in der Wüste."], "Ihre Beeren sehen aus wie leckere Kirschen."),
        ch(p, "Was stimmt?", "Was ist beim Goldregen besonders gefährlich?", ["die Samen in den Schoten, sie sehen aus wie Bohnen", "der Schatten", "die Rinde, wenn man sie anschaut"], "die Samen in den Schoten, sie sehen aus wie Bohnen"),
        sort(p, "Giftig oder essbar?", "Ist diese Beere giftig oder essbar?", ["giftig", "essbar"], [
            ("Tollkirsche", "giftig"), ("Eibe", "giftig"), ("Maiglöckchen", "giftig"), ("Pfaffenhütchen", "giftig"),
            ("Walderdbeere", "essbar"), ("Himbeere", "essbar"), ("Heidelbeere", "essbar"),
        ]),
        wahr(p, "Die Eibe ist ein Nadelbaum, der giftig ist.", True),
        wahr(p, "Giftige Sträucher wachsen auch in Parks und Gärten.", True),
    ], mix=False),
    lesson("Giftiges Gemüse", "🥔", [
        sort(p, "Wie isst man das sicher?", "Darf man das so essen?", ["darf man essen", "nicht essen"], [
            ("gekochte grüne Bohnen", "darf man essen"), ("rohe grüne Bohnen", "nicht essen"),
            ("rote, reife Tomaten", "darf man essen"), ("grüne, unreife Tomaten", "nicht essen"),
            ("Kartoffeln ohne grüne Stellen", "darf man essen"), ("grüne Stellen an Kartoffeln", "nicht essen"),
            ("Rhabarberstiele, gekocht", "darf man essen"), ("Rhabarberblätter", "nicht essen"),
        ]),
        ch(p, "Was stimmt?", "Was machst du mit Keimen an einer Kartoffel?", ["großzügig wegschneiden", "mitessen", "anmalen"], "großzügig wegschneiden"),
        ch(p, "Was stimmt?", "Wie kann man Holunderbeeren essen?", ["nur gekocht, zum Beispiel als Saft", "roh vom Strauch", "gar nicht, nie"], "nur gekocht, zum Beispiel als Saft"),
        ch(p, "Was stimmt?", "Warum muss man Bohnen kochen?", ["Roh enthalten sie einen Giftstoff.", "Roh sind sie zu süß.", "Roh sind sie zu weich."], "Roh enthalten sie einen Giftstoff."),
        wahr(p, "Kartoffeln soll man dunkel lagern, damit sie nicht grün werden.", True),
        wahr(p, "Grüne Tomaten schmecken besonders gesund.", False, "Unreife Tomaten enthalten einen Giftstoff. Nur rote, reife Tomaten essen."),
    ]),
    test(12),
])

# ---------- Sonne, Erde und Mond ----------
p = "h3-himmel"
PL = ["Merkur", "Venus", "Erde", "Mars", "Jupiter", "Saturn", "Uranus", "Neptun"]
wissen("hsu-himmelskoerper", "⭐", "Himmelskörper", [
    "Ein **Stern** leuchtet selbst. Die **Sonne** ist ein Stern, der uns am nächsten ist.",
    "Ein **Planet** kreist um die Sonne und leuchtet nicht selbst. Die **Erde** ist ein Planet.",
    "Ein **Mond** kreist um einen Planeten. Unser Mond wird von der Sonne angestrahlt.",
    "Ein **Komet** ist ein Brocken aus Eis und Staub mit einem leuchtenden **Schweif**.",
    "Eine **Sternschnuppe** ist ein kleiner Stein, der in der Luft verglüht.",
], [], [f"{p}/Himmelskörper"])
wissen("hsu-planeten", "🪐", "Die acht Planeten", [
    "Von der Sonne aus: **Merkur, Venus, Erde, Mars, Jupiter, Saturn, Uranus, Neptun**.",
    "Der **Jupiter** ist der größte Planet, der **Merkur** der kleinste.",
    "Der **Mars** sieht rot aus. Der **Saturn** hat große Ringe.",
    "Die **Erde** ist der einzige Planet, auf dem wir Leben kennen.",
], ["Merksatz: **M**ein **V**ater **e**rklärt **m**ir **j**eden **S**onntag **u**nseren **N**achthimmel."], [f"{p}/Die Planeten ordnen"],
    trick="Mein Vater erklärt mir jeden Sonntag unseren Nachthimmel.")
wissen("hsu-tagjahr", "🌍", "Tag, Monat, Jahr", [
    "**Tag**: Die Erde dreht sich in **24 Stunden** einmal um sich selbst. Auf der Seite zur Sonne ist **Tag**, auf der anderen **Nacht**.",
    "**Monat**: Der Mond braucht ungefähr **einen Monat**, um die Erde einmal zu umkreisen.",
    "**Jahr**: Die Erde braucht **365 Tage**, um einmal um die Sonne zu kreisen. Im **Schaltjahr** sind es 366 Tage.",
    "Die Sonne geht im **Osten** auf und im **Westen** unter.",
], [], [f"{p}/Tag und Nacht", f"{p}/Jahr, Monat, Tag"])
wissen("hsu-jahreszeiten3", "🌷", "Warum es Jahreszeiten gibt", [
    "Die Erdachse ist **schief**. Darum ist unsere Hälfte der Erde mal mehr, mal weniger zur Sonne geneigt.",
    "**Sommer**: Die Sonne steht hoch, scheint lange und wärmt stark.",
    "**Winter**: Die Sonne steht tief, die Tage sind kurz und es ist kalt.",
    "Um den **21. Juni** ist der längste Tag, um den **21. Dezember** der kürzeste.",
    "In Australien ist es genau umgekehrt: Dort ist an Weihnachten **Sommer**.",
], [], [f"{p}/Warum es Jahreszeiten gibt"])
wissen("hsu-mondphasen", "🌙", "Die Mondphasen", [
    "Der Mond leuchtet nicht selbst. Wir sehen nur den Teil, den die **Sonne** anstrahlt.",
    "**Neumond**: Wir sehen den Mond gar nicht.",
    "**Zunehmender Mond**: Er wird jeden Abend ein bisschen größer.",
    "**Vollmond**: Wir sehen eine ganze runde Scheibe.",
    "**Abnehmender Mond**: Er wird wieder kleiner. Nach etwa **4 Wochen** ist wieder Neumond.",
], [], [f"{p}/Die Mondphasen"])

UNITS["hsu/k3-himmel.json"] = unit(p, "Sonne, Erde und Mond", "🌍", "#2b3f8f", [
    lesson("Himmelskörper", "⭐", [
        pairs(p, "Was ist das?", "Was ist das für ein Himmelskörper?", [
            ("Sonne", "ein Stern, der selbst leuchtet"), ("Erde", "ein Planet"), ("Mond", "kreist um die Erde"), ("Komet", "Eis und Staub mit Schweif"),
        ]),
        ch(p, "Was stimmt?", "Die Sonne ist ein …", ["Stern", "Planet", "Mond"], "Stern", keep=True),
        ch(p, "Was stimmt?", "Was ist eine Sternschnuppe wirklich?", ["ein kleiner Stein, der in der Luft verglüht", "ein Stern, der herunterfällt", "ein Flugzeug"], "ein kleiner Stein, der in der Luft verglüht"),
        ch(p, "Was stimmt?", "Warum sieht man tagsüber keine Sterne?", ["Die Sonne ist viel heller und überstrahlt sie.", "Die Sterne schlafen am Tag.", "Die Sterne sind nur nachts da."], "Die Sonne ist viel heller und überstrahlt sie."),
        ch(p, "Was stimmt?", "Mit welchem Gerät kann man weit entfernte Sterne besser sehen?", ["mit einem Fernrohr", "mit einer Lupe", "mit einem Mikroskop"], "mit einem Fernrohr"),
        ch(p, "Was stimmt?", "Welcher Stern zeigt nachts ungefähr nach Norden?", ["der Polarstern", "die Sonne", "der Abendstern"], "der Polarstern"),
        wahr(p, "Der Mond leuchtet selbst wie eine Lampe.", False, "Der Mond wird von der Sonne angestrahlt und wirft das Licht zurück."),
        wahr(p, "Im Jahr 1969 waren zum ersten Mal Menschen auf dem Mond.", True),
    ], mix=False),
    lesson("Die Planeten ordnen", "🪐", [
        reihe(p, "Ordne die Planeten von der Sonne aus!", PL[:4]),
        reihe(p, "Ordne die äußeren Planeten von der Sonne aus!", PL[4:]),
        reihe(p, "Ordne alle acht Planeten von der Sonne aus!", PL),
        ch(p, "Was stimmt?", "Welcher Planet ist der größte?", ["Jupiter", "Erde", "Merkur"], "Jupiter"),
        ch(p, "Was stimmt?", "Welcher Planet ist der Sonne am nächsten?", ["Merkur", "Neptun", "Mars"], "Merkur"),
        ch(p, "Was stimmt?", "Welcher Planet wird der rote Planet genannt?", ["Mars", "Venus", "Uranus"], "Mars"),
        ch(p, "Was stimmt?", "Welcher Planet hat besonders große, schöne Ringe?", ["Saturn", "Erde", "Merkur"], "Saturn"),
        ch(p, "Was stimmt?", "Der wievielte Planet von der Sonne aus ist die Erde?", ["der dritte", "der erste", "der achte"], "der dritte", keep=True),
        wahr(p, "Pluto zählt heute nicht mehr zu den Planeten. Er ist ein Zwergplanet.", True),
    ], mix=False),
    lesson("Tag und Nacht", "🌗", [
        ch(p, "Was stimmt?", "Warum gibt es Tag und Nacht?", ["Die Erde dreht sich um sich selbst.", "Die Sonne geht abends schlafen.", "Der Mond schiebt sich vor die Sonne."], "Die Erde dreht sich um sich selbst."),
        ch(p, "Was stimmt?", "Wie lange braucht die Erde für eine Drehung um sich selbst?", ["24 Stunden", "eine Woche", "ein Jahr"], "24 Stunden"),
        ch(p, "Was stimmt?", "Wo geht die Sonne auf?", ["im Osten", "im Westen", "im Norden"], "im Osten"),
        ch(p, "Was stimmt?", "Wo geht die Sonne unter?", ["im Westen", "im Osten", "im Süden"], "im Westen"),
        ch(p, "Was stimmt?", "Wo steht die Sonne bei uns mittags?", ["im Süden", "im Norden", "im Osten"], "im Süden"),
        wahr(p, "Wenn bei uns Nacht ist, ist auf der anderen Seite der Erde Tag.", True),
        wahr(p, "Eigentlich bewegt sich nicht die Sonne über den Himmel, sondern die Erde dreht sich.", True),
    ], mix=False),
    lesson("Jahr, Monat, Tag", "📅", [
        pairs(p, "Was passiert in dieser Zeit?", "Was passiert in dieser Zeit?", [
            ("ein Tag", "Die Erde dreht sich einmal um sich selbst."),
            ("ungefähr ein Monat", "Der Mond kreist einmal um die Erde."),
            ("ein Jahr", "Die Erde kreist einmal um die Sonne."),
        ]),
        ch(p, "Was stimmt?", "Wie viele Tage hat ein normales Jahr?", ["365", "100", "52"], "365"),
        ch(p, "Was stimmt?", "Wie viele Tage hat ein Schaltjahr?", ["366", "365", "360"], "366"),
        ch(p, "Was stimmt?", "Welchen Tag gibt es nur im Schaltjahr?", ["den 29. Februar", "den 31. April", "den 32. Dezember"], "den 29. Februar"),
        ty(p, "Weißt du es?", "Wie viele Monate hat ein Jahr?", "12"),
        ty(p, "Weißt du es?", "Wie viele Stunden hat ein Tag?", "24"),
        wahr(p, "Die Erde kreist um die Sonne, nicht die Sonne um die Erde.", True),
    ]),
    lesson("Warum es Jahreszeiten gibt", "🌷", [
        ch(p, "Was stimmt?", "Warum gibt es Jahreszeiten?", ["Die Erdachse ist schief.", "Die Sonne ist im Winter ausgeschaltet.", "Im Sommer ist die Erde viel näher an der Sonne."], "Die Erdachse ist schief.",
           "Im Sommer ist unsere Hälfte der Erde zur Sonne geneigt. Die Sonne steht höher und scheint länger."),
        sort(p, "Sommer oder Winter?", "Ist das bei uns im Sommer oder im Winter?", ["Sommer", "Winter"], [
            ("Die Sonne steht mittags hoch.", "Sommer"), ("Die Tage sind lang.", "Sommer"), ("Die Sonne steht tief.", "Winter"),
            ("Es wird früh dunkel.", "Winter"), ("Der längste Tag des Jahres", "Sommer"), ("Der kürzeste Tag des Jahres", "Winter"),
        ]),
        ch(p, "Was stimmt?", "Wann ist ungefähr der längste Tag des Jahres?", ["am 21. Juni", "am 21. Dezember", "am 1. Januar"], "am 21. Juni"),
        ch(p, "Was stimmt?", "Welche Jahreszeit ist in Australien, wenn bei uns Weihnachten ist?", ["Sommer", "Winter", "Herbst"], "Sommer"),
        reihe(p, "Bring die Jahreszeiten in die richtige Reihenfolge! Fang mit dem Frühling an.", ["Frühling", "Sommer", "Herbst", "Winter"]),
        wahr(p, "Am Frühlingsanfang sind Tag und Nacht ungefähr gleich lang.", True),
    ], mix=False),
    lesson("Die Mondphasen", "🌙", [
        reihe(p, "Bring die Mondphasen in die richtige Reihenfolge! Fang mit dem Neumond an.", [
            "Neumond", "zunehmender Mond", "Vollmond", "abnehmender Mond"]),
        ch(p, "Was stimmt?", "Warum sieht der Mond nicht immer gleich aus?", ["Die Sonne strahlt immer einen anderen Teil an, den wir sehen.", "Der Mond wird angeknabbert.", "Wolken schneiden ein Stück ab."], "Die Sonne strahlt immer einen anderen Teil an, den wir sehen."),
        ch(p, "Was stimmt?", "Wie lange dauert es von einem Vollmond bis zum nächsten?", ["ungefähr 4 Wochen", "einen Tag", "ein Jahr"], "ungefähr 4 Wochen"),
        ch(p, "Was stimmt?", "Was siehst du bei Neumond?", ["fast nichts vom Mond", "eine runde helle Scheibe", "einen halben Mond"], "fast nichts vom Mond"),
        wahr(p, "Der zunehmende Mond wird jeden Abend ein Stückchen größer.", True),
        wahr(p, "Der Mond ist manchmal auch am Tag zu sehen.", True),
    ]),
    test(12),
])

# =====================================================================
# 3. KLASSE, RUNDE 2b: Zeichnungen, Schaubilder, Auge vertieft, Erde
# =====================================================================
def add_lessons(path, *ls):
    u = UNITS[path]["lessons"]
    pos = len(u) - 1 if u and u[-1].get("test") else len(u)
    for l in ls:
        u.insert(pos, l); pos += 1


# ---------- Auge vertieft ----------
p = "h3-sinne"
AUGE_VORN = [(150, 22, "Augenbraue"), (150, 64, "Lid"), (98, 92, "Wimpern"), (178, 126, "Iris"), (150, 112, "Pupille")]
AUGE_INNEN = [(92, 100, "Hornhaut"), (110, 78, "Iris"), (124, 100, "Linse"), (165, 100, "Glaskörper"), (205, 58, "Netzhaut"), (255, 104, "Sehnerv"), (190, 14, "Augenhöhle")]
wissen("hsu-auge-aussen", "👁️", "Das Auge von außen", [
    "Die **Augenbraue** lenkt Schweiß und Regen vom Auge weg.",
    "Das **Lid** schließt sich beim Blinzeln. Es verteilt die Tränenflüssigkeit und schützt das Auge.",
    "Die **Wimpern** halten Staub und kleine Insekten ab.",
    "Die **Iris** ist der farbige Ring. In ihrer Mitte ist die schwarze **Pupille**, ein Loch, durch das Licht ins Auge fällt.",
], [], [f"{p}/Das Auge von außen"])
wissen("hsu-auge-innen", "🔎", "Das Auge von innen", [
    "Vorn ist die durchsichtige **Hornhaut**. Dahinter liegen **Iris** und **Pupille**.",
    "Die **Linse** bündelt das Licht. Sie macht das Bild scharf.",
    "Innen ist das Auge mit dem **Glaskörper** gefüllt, einer klaren, festen Masse wie Gelee.",
    "Hinten auf der **Netzhaut** entsteht das Bild. Es steht dort auf dem Kopf.",
    "Der **Sehnerv** bringt das Bild zum **Gehirn**. Das Gehirn dreht es richtig herum.",
    "Das Auge liegt geschützt in der knöchernen **Augenhöhle**.",
], ["Licht → Hornhaut → Pupille → Linse → Glaskörper → Netzhaut → Sehnerv → Gehirn"], [f"{p}/Das Auge von innen", f"{p}/So sehen wir"])
add_lessons("hsu/k3-sinne.json",
    lesson("Das Auge von außen", "👁️", [
        schaubild(p, "Beschrifte das Auge! Tipp eine Nummer an und dann den passenden Begriff.", "auge-vorn", AUGE_VORN),
        pairs(p, "Wie schützt dieser Teil das Auge?", "Wie schützt dieser Teil das Auge?", [
            ("Augenbraue", "lenkt Schweiß vom Auge weg"), ("Wimpern", "halten Staub ab"),
            ("Lid", "schließt sich beim Blinzeln"), ("Tränen", "spülen das Auge sauber"),
        ]),
        bildfrage(p, "Was ist das?", "Wie heißt der farbige Ring im Auge?", "auge-vorn", ["Iris", "Pupille", "Lid"], "Iris"),
        bildfrage(p, "Was ist das?", "Wie heißt das schwarze Loch in der Mitte?", "auge-vorn", ["Pupille", "Iris", "Linse"], "Pupille"),
        ch(p, "Was stimmt?", "Wie oft blinzelst du ungefähr in einer Minute?", ["etwa 10- bis 20-mal", "einmal", "1000-mal"], "etwa 10- bis 20-mal"),
        wahr(p, "Die Pupille ist in Wirklichkeit ein Loch.", True, "Sie sieht schwarz aus, weil es im Inneren des Auges dunkel ist."),
    ], mix=False),
    lesson("Das Auge von innen", "🔎", [
        schaubild(p, "Beschrifte das Auge von innen!", "auge-schnitt", AUGE_INNEN),
        pairs(p, "Was macht dieser Teil des Auges?", "Was macht dieser Teil des Auges?", [
            ("Hornhaut", "durchsichtige Schutzschicht vorn"), ("Glaskörper", "füllt das Auge wie klares Gelee"),
            ("Augenhöhle", "Knochen, die das Auge schützen"), ("Netzhaut", "hier entsteht das Bild"),
        ]),
        bildfrage(p, "Was ist das?", "Welcher Teil macht das Bild scharf?", "auge-schnitt", ["die Linse", "die Hornhaut", "der Sehnerv"], "die Linse"),
        bildfrage(p, "Was ist das?", "Welcher Teil bringt das Bild zum Gehirn?", "auge-schnitt", ["der Sehnerv", "die Netzhaut", "die Iris"], "der Sehnerv"),
        wahr(p, "Auf der Netzhaut steht das Bild auf dem Kopf.", True, "Das Gehirn dreht es wieder richtig herum."),
        wahr(p, "Der größte Teil des Augapfels liegt versteckt in der Augenhöhle.", True),
    ], mix=False),
    lesson("So sehen wir", "💡", [
        reihe(p, "Welchen Weg nimmt das Licht? Bring es in die richtige Reihenfolge!", [
            "Hornhaut", "Pupille", "Linse", "Glaskörper", "Netzhaut", "Sehnerv", "Gehirn"]),
        ch(p, "Was stimmt?", "Warum sehen wir in völliger Dunkelheit nichts?", ["Ohne Licht kommt kein Bild ins Auge.", "Die Augen schlafen.", "Die Linse ist zu."], "Ohne Licht kommt kein Bild ins Auge."),
        ch(p, "Was stimmt?", "Ein Kind sieht in der Ferne alles verschwommen, in der Nähe aber gut. Es ist …", ["kurzsichtig", "weitsichtig", "farbenblind"], "kurzsichtig"),
        ch(p, "Was stimmt?", "Was hilft, wenn man nicht mehr scharf sieht?", ["eine Brille", "eine Sonnenbrille", "Augentropfen mit Zucker"], "eine Brille"),
        ch(p, "Was stimmt?", "Warum haben wir zwei Augen?", ["Damit wir Entfernungen besser schätzen können.", "Damit eins schlafen kann.", "Weil eins zu klein ist."], "Damit wir Entfernungen besser schätzen können."),
        wahr(p, "Beim Lesen soll das Licht gut sein, damit die Augen nicht so schnell müde werden.", True),
    ], mix=False),
)

# ---------- Zeichnungen in den Pflanzen-Themen ----------
p = "h3-pflanze"
add_lessons("hsu/k3-pflanze.json",
    lesson("Pflanzen genau ansehen", "🔎", [
        schaubild(p, "Beschrifte die Pflanze!", "bluetenpflanze", [(122, 38, "Blüte"), (78, 110, "Blatt"), (100, 145, "Stängel"), (100, 180, "Wurzel")], 200, 200),
        bildreihe(p, "Wie wächst eine Bohne? Bring die Bilder in die richtige Reihenfolge!", [
            "[[bohne-1]] Samen", "[[bohne-2]] quillt", "[[bohne-3]] Wurzel", "[[bohne-4]] Spross", "[[bohne-5]] Blätter"]),
        bildfrage(p, "Was siehst du?", "Was wächst hier gerade aus dem Samen?", "bohne-3", ["die Wurzel", "die Blüte", "die Frucht"], "die Wurzel"),
        bildfrage(p, "Wie reist dieser Samen?", "Wie wird dieser Samen verbreitet?", "frucht-ahorn", ["mit dem Wind", "mit dem Wasser", "im Fell von Tieren"], "mit dem Wind"),
        bildfrage(p, "Wie reist dieser Samen?", "Wer verbreitet diese Beeren?", "frucht-vogelbeeren", ["Vögel", "der Wind", "das Wasser"], "Vögel"),
    ], mix=False),
)

wissen("hsu-samenpflanzen", "🌰", "Samen und Sporen", [
    "Die meisten Pflanzen vermehren sich mit **Samen**. Damit ein Samen entsteht, muss die Blüte erst **bestäubt** und **befruchtet** werden.",
    "Bei den Samenpflanzen gibt es zwei Gruppen: **Nacktsamer** und **Bedecktsamer**.",
    "**Nacktsamer**: Die Samen liegen frei, zum Beispiel zwischen den Schuppen eines Zapfens (Fichte, Kiefer, Tanne).",
    "**Bedecktsamer**: Die Samen sind von einer **Frucht** umhüllt (Apfel, Kirsche, Tomate, Bohne).",
    "Moose, Farne und Pilze bilden keine Samen, sondern winzige **Sporen**. Dafür braucht es keine Befruchtung.",
], [], [f"h3-pflanze/Nacktsamer und Bedecktsamer"])
add_lessons("hsu/k3-pflanze.json",
    lesson("Nacktsamer und Bedecktsamer", "🌰", [
        ch("h3-pflanze", "Fülle die Lücke!", "Die meisten Pflanzen vermehren sich über …", ["Samen", "Wurzeln", "Steine"], "Samen"),
        ch("h3-pflanze", "Fülle die Lücke!", "Damit Samen entstehen können, muss die Blüte erst … werden.", ["befruchtet", "gegossen", "gepflückt"], "befruchtet"),
        ch("h3-pflanze", "Fülle die Lücke!", "Unter den Samenpflanzen gibt es Bedecktsamer und …", ["Nacktsamer", "Sporensamer", "Wurzelsamer"], "Nacktsamer"),
        ch("h3-pflanze", "Fülle die Lücke!", "Moose und Farne bilden keine Samen, sondern …", ["Sporen", "Zapfen", "Früchte"], "Sporen"),
        sort("h3-pflanze", "Nacktsamer oder Bedecktsamer?", "Ist diese Pflanze ein Nacktsamer oder ein Bedecktsamer?", ["Nacktsamer", "Bedecktsamer"], [
            ("Fichte", "Nacktsamer"), ("Kiefer", "Nacktsamer"), ("Tanne", "Nacktsamer"), ("Lärche", "Nacktsamer"),
            ("Apfelbaum", "Bedecktsamer"), ("Kirschbaum", "Bedecktsamer"), ("Bohne", "Bedecktsamer"), ("Sonnenblume", "Bedecktsamer"),
        ]),
        bildfrage("h3-pflanze", "Schau dir das Bild genau an!", "Die Samen liegen frei zwischen den Schuppen. Ist die Fichte ein …", "zapfen-fichte", ["Nacktsamer", "Bedecktsamer"], "Nacktsamer", keep=True),
        bildfrage("h3-pflanze", "Schau dir das Bild genau an!", "Die Kerne stecken im Fruchtfleisch. Ist der Apfelbaum ein …", "apfel-laengs", ["Nacktsamer", "Bedecktsamer"], "Bedecktsamer", keep=True),
        wahr("h3-pflanze", "Sporen entstehen ohne Befruchtung.", True),
    ], mix=False),
)

p = "h3-apfel"
add_lessons("hsu/k3-apfel.json",
    lesson("Den Apfel beschriften", "🍎", [
        schaubild(p, "Beschrifte den aufgeschnittenen Apfel!", "apfel-laengs",
                  [(103, 26, "Stiel"), (27, 100, "Schale"), (58, 128, "Fruchtfleisch"), (90, 104, "Kerne"), (100, 130, "Kerngehäuse"), (100, 180, "Blütenrest")], 200, 200),
        schaubild(p, "Setze die richtigen Wörter ein! Das Bild hilft dir.", "apfel-laengs",
                  [(27, 100, "Schale"), (103, 26, "Stiel"), (100, 180, "Blütenrest"), (52, 140, "Fruchtfleisch"), (122, 132, "Kerngehäuse"), (90, 104, "Kerne")], 200, 200,
                  extra=["Wurzel"], labels=True, text=[
                      "Außen ist der Apfel von der __ umhüllt. Sie schützt ihn vor Schmutz und davor, dass er austrocknet.",
                      "Oben sitzt der __. Früher hat er die Blüte mit dem Zweig verbunden. Unten sieht man den __, die vertrockneten Reste der Blüte.",
                      "Das meiste vom Apfel ist saftiges __. In der Mitte liegt das __. Darin stecken die __, die Samen des Apfelbaums.",
                  ]),
        bildfrage(p, "Was siehst du?", "So sieht ein Apfel aus, wenn man ihn quer durchschneidet. Wie viele Kammern hat der Stern?", "apfel-quer", ["5", "3", "8"], "5"),
        schaubild(p, "Setze die richtigen Wörter ein!", "apfel-quer",
                  [(None, None, "quer"), (None, None, "Stern"), (None, None, "fünf"), (None, None, "Kerne")], 200, 200,
                  extra=["Kreis", "drei"], text=[
                      "Schneidet man einen Apfel __ durch, sieht das Kerngehäuse aus wie ein __. Er hat __ Zacken.",
                      "In jeder Kammer liegen die __. Aus ihnen kann ein neuer Apfelbaum wachsen.",
                  ]),
        bildfrage(p, "Was siehst du?", "Was sind die braunen Dinge in der Mitte?", "apfel-laengs", ["die Kerne, also die Samen", "Würmer", "Schokolade"], "die Kerne, also die Samen"),
    ], mix=False),
)

p = "h3-gift"
wissen("hsu-giftwas", "🛡️", "Warum sind Pflanzen giftig?", [
    "Pflanzen können nicht weglaufen. Mit **Giftstoffen** schützen sie sich vor Tieren, die sie fressen wollen.",
    "Manchmal ist die **ganze Pflanze** giftig, manchmal nur ein Teil, zum Beispiel die Beeren, die Samen oder die Blätter.",
    "Giftige Tiere warnen oft mit **Warnfarben**, wie die Wespe. Einer Giftpflanze sieht man ihr Gift **nicht** an.",
    "Auch Pflanzen, die man jeden Tag sieht, können giftig sein. Zum Beispiel **Efeu** an der Hauswand oder die **Eibe** in der Hecke.",
    "Es kommt auf die **Menge** und die Stärke des Giftes an. Manche Pflanzen machen nur Bauchweh, andere können **tödlich** sein.",
], [], [f"{p}/Warum sind Pflanzen giftig?"], trick="Was du nicht kennst, isst du nicht und fasst du möglichst nicht an.")
UNITS["hsu/k3-giftpflanzen.json"]["lessons"].insert(0, lesson("Warum sind Pflanzen giftig?", "🛡️", [
    ch(p, "Was stimmt?", "Warum bilden manche Pflanzen Gift?", ["um sich vor Tieren zu schützen, die sie fressen wollen", "damit sie schöner blühen", "damit sie schneller wachsen"], "um sich vor Tieren zu schützen, die sie fressen wollen"),
    wahr(p, "Jede Giftpflanze erkennt man an einer leuchtenden Warnfarbe.", False, "Viele Giftpflanzen sehen ganz harmlos aus. Manche sehen sogar essbaren Pflanzen zum Verwechseln ähnlich."),
    ch(p, "Was stimmt?", "Welche Teile einer Giftpflanze können giftig sein?", ["alle Teile oder nur einzelne, zum Beispiel Beeren oder Samen", "immer nur die Wurzel", "nur die Blüte"], "alle Teile oder nur einzelne, zum Beispiel Beeren oder Samen"),
    wahr(p, "Efeu wächst an vielen Häusern und ist trotzdem giftig.", True),
    ch(p, "Was stimmt?", "Wovon hängt ab, wie gefährlich eine Giftpflanze ist?", ["von der Stärke des Giftes und von der Menge", "von der Farbe der Blüte", "vom Wetter"], "von der Stärke des Giftes und von der Menge"),
    ch(p, "Was stimmt?", "Manche Giftpflanzen haben sehr starke Gifte. Sie können … sein.", ["tödlich", "gesund", "lecker"], "tödlich"),
    ch(p, "Was tust du?", "Du findest beim Spielen eine Pflanze, die du nicht kennst. Was tust du?", ["Ich esse sie nicht und fasse sie möglichst nicht an.", "Ich probiere ein kleines Stück.", "Ich pflücke sie und nehme sie mit nach Hause."], "Ich esse sie nicht und fasse sie möglichst nicht an."),
], mix=False))

p = "h3-laub"
LBZ = [("blatt-buche", "Buche"), ("blatt-eiche", "Eiche"), ("blatt-birke", "Birke"), ("blatt-ahorn", "Ahorn"),
       ("blatt-eberesche", "Eberesche"), ("blatt-kastanie", "Kastanie"), ("blatt-linde", "Linde")]
FRZ = [("frucht-eichel", "Eiche"), ("frucht-buchecker", "Buche"), ("frucht-ahorn", "Ahorn"), ("frucht-vogelbeeren", "Eberesche"), ("frucht-kastanie", "Kastanie")]
rnd = __import__("random").Random(36)
def drei(richtig, alle):
    andere = [x for x in alle if x != richtig]
    rnd.shuffle(andere)
    return [richtig] + andere[:2]
NAMEN = [n for _, n in LBZ]
add_lessons("hsu/k3-laubbaeume.json",
    lesson("Blätter erkennen", "🍃", [bildfrage(p, "Welcher Baum ist das?", "Von welchem Baum ist dieses Blatt?", z, drei(n, NAMEN), n) for z, n in LBZ] + [
        bildwahl(p, "Tipp auf das Blatt der Eiche!", ["blatt-eiche", "blatt-buche", "blatt-linde"], "blatt-eiche"),
        bildwahl(p, "Tipp auf das Blatt vom Ahorn!", ["blatt-ahorn", "blatt-kastanie", "blatt-birke"], "blatt-ahorn"),
        bildwahl(p, "Tipp auf das gefiederte Blatt der Eberesche!", ["blatt-eberesche", "blatt-buche", "blatt-kastanie"], "blatt-eberesche"),
    ]),
    lesson("Früchte erkennen", "🌰", [bildfrage(p, "Welcher Baum ist das?", "Von welchem Baum ist diese Frucht?", z, drei(n, NAMEN[:6]), n) for z, n in FRZ] + [
        bildwahl(p, "Tipp auf die Frucht der Buche!", ["frucht-buchecker", "frucht-eichel", "frucht-kastanie"], "frucht-buchecker"),
        bildwahl(p, "Was fliegt wie ein Propeller? Tipp es an!", ["frucht-ahorn", "frucht-eichel", "frucht-vogelbeeren"], "frucht-ahorn"),
    ]),
)

p = "h3-nadel"
NZ = [("zweig-fichte", "Fichte"), ("zweig-tanne", "Tanne"), ("zweig-kiefer", "Kiefer"), ("zweig-laerche", "Lärche"), ("zweig-eibe", "Eibe")]
NN = [n for _, n in NZ]
add_lessons("hsu/k3-nadelbaeume.json",
    lesson("Zweige und Zapfen erkennen", "🌲", [bildfrage(p, "Welcher Baum ist das?", "Von welchem Nadelbaum ist dieser Zweig?", z, drei(n, NN), n) for z, n in NZ] + [
        bildfrage(p, "Welcher Baum ist das?", "Dieser lange Zapfen hängt nach unten. Von welchem Baum ist er?", "zapfen-fichte", ["Fichte", "Tanne", "Kiefer"], "Fichte"),
        bildfrage(p, "Welcher Baum ist das?", "Dieser Zapfen steht aufrecht auf dem Zweig. Von welchem Baum ist er?", "zapfen-tanne", ["Tanne", "Fichte", "Kiefer"], "Tanne"),
        bildfrage(p, "Welcher Baum ist das?", "Dieser kleine, runde Zapfen ist von der …", "zapfen-kiefer", ["Kiefer", "Tanne", "Fichte"], "Kiefer", keep=True),
        bildwahl(p, "Welcher Nadelbaum ist giftig? Tipp ihn an!", ["zweig-eibe", "zweig-fichte", "zweig-laerche"], "zweig-eibe"),
    ]),
)

p = "h3-gift"
GZ = [("gift-maigloeckchen", "Maiglöckchen"), ("gift-fingerhut", "Fingerhut"), ("gift-eisenhut", "Eisenhut"), ("gift-herbstzeitlose", "Herbstzeitlose"),
      ("gift-tollkirsche", "Tollkirsche"), ("gift-goldregen", "Goldregen"), ("gift-pfaffenhuetchen", "Pfaffenhütchen"), ("gift-aronstab", "Aronstab")]
GN = [n for _, n in GZ]
add_lessons("hsu/k3-giftpflanzen.json",
    lesson("Giftpflanzen erkennen", "🔎", [bildfrage(p, "Welche Giftpflanze ist das?", "Welche Giftpflanze ist das?", z, drei(n, GN), n) for z, n in GZ] + [
        bildwahl(p, "Welche Pflanze kann man essen? Sie riecht nach Knoblauch.", ["baerlauch", "gift-maigloeckchen", "gift-herbstzeitlose"], "baerlauch",
                 "Das ist Bärlauch. Aber Vorsicht: Seine Blätter sehen fast aus wie die vom Maiglöckchen. Nur mit einem Erwachsenen sammeln!"),
        bildwahl(p, "Tipp auf die Tollkirsche!", ["gift-tollkirsche", "frucht-vogelbeeren", "gift-aronstab"], "gift-tollkirsche"),
    ]),
)

# ---------- Himmel mit Bildern ----------
p = "h3-himmel"
PZ = [("planet-erde", "Erde"), ("planet-mars", "Mars"), ("planet-jupiter", "Jupiter"), ("planet-saturn", "Saturn")]
add_lessons("hsu/k3-himmel.json",
    lesson("Planeten und Mond erkennen", "🔭", [
        *[bildfrage(p, "Welcher Planet ist das?", "Welcher Planet ist das?", z, drei(n, PL), n) for z, n in PZ],
        bildreihe(p, "Ordne die Planeten von der Sonne aus!", ["[[planet-merkur]] Merkur", "[[planet-venus]] Venus", "[[planet-erde]] Erde", "[[planet-mars]] Mars"]),
        bildreihe(p, "Bring die Mondphasen in die richtige Reihenfolge! Fang mit dem Neumond an.", [
            "[[mond-neumond]] Neumond", "[[mond-zunehmend]] zunehmend", "[[mond-vollmond]] Vollmond", "[[mond-abnehmend]] abnehmend"]),
        bildfrage(p, "Wie heißt das?", "Wie heißt diese Mondphase?", "mond-vollmond", ["Vollmond", "Neumond", "zunehmender Mond"], "Vollmond"),
        bildfrage(p, "Wie heißt das?", "Der Mond wird jeden Abend größer. Wie heißt diese Mondphase?", "mond-zunehmend", ["zunehmender Mond", "abnehmender Mond", "Vollmond"], "zunehmender Mond"),
        bildwahl(p, "Tipp auf den Stern!", ["himmel-sonne", "planet-erde", "mond-vollmond"], "himmel-sonne", "Die Sonne ist ein Stern. Sie leuchtet selbst."),
    ], mix=False),
)

# ---------- Die Erde: Kontinente und Ozeane ----------
p = "h3-erde"
KW, KH = 1000, 439
KONT = [(200, 125, "Nordamerika"), (335, 290, "Südamerika"), (560, 85, "Europa"), (575, 255, "Afrika"),
        (790, 110, "Asien"), (865, 315, "Australien"), (760, 418, "Antarktis")]
OZE = [(90, 270, "Pazifischer Ozean"), (410, 210, "Atlantischer Ozean"), (710, 320, "Indischer Ozean"), (515, 20, "Arktischer Ozean"), (300, 405, "Antarktischer Ozean")]
KZ = [("weltkarte-nordamerika", "Nordamerika"), ("weltkarte-suedamerika", "Südamerika"), ("weltkarte-europa", "Europa"), ("weltkarte-afrika", "Afrika"),
      ("weltkarte-asien", "Asien"), ("weltkarte-australien", "Australien"), ("weltkarte-antarktis", "Antarktis")]
KN = [n for _, n in KZ]
wissen("hsu-kontinente", "🌍", "Kontinente und Ozeane", [
    "Von oben sieht die Erde blau aus: Mehr als zwei Drittel sind **Wasser**.",
    "Die großen Landflächen heißen **Kontinente**. Es gibt **sieben**: Nordamerika, Südamerika, Europa, Afrika, Asien, Australien und die Antarktis.",
    "**Asien** ist der größte Kontinent, **Australien** der kleinste. Wir leben in **Europa**.",
    "Ein **Ozean** ist ein riesiges, tiefes Meer. Es gibt **fünf**: den **Pazifischen** (Pazifik, der größte), den **Atlantischen** (Atlantik), den **Indischen**, den **Arktischen** (im Norden) und den **Antarktischen Ozean** (im Süden).",
    "Ein **Globus** ist ein kleines Modell der Erde als Kugel. Eine **Weltkarte** ist flach und zeigt alles auf einmal.",
], [], [f"{p}/Globus und Weltkarte", f"{p}/Die sieben Kontinente", f"{p}/Die Ozeane"])
UNITS["hsu/k3-erde.json"] = unit(p, "Die Erde: Kontinente und Ozeane", "🌍", "#1f78b4", [
    lesson("Globus und Weltkarte", "🌐", [
        ch(p, "Was stimmt?", "Was ist ein Globus?", ["ein kleines Modell der Erde als Kugel", "eine flache Karte", "ein Fernrohr"], "ein kleines Modell der Erde als Kugel"),
        ch(p, "Was stimmt?", "Was ist der Vorteil einer Weltkarte?", ["Man sieht alle Kontinente auf einmal.", "Sie ist rund.", "Sie dreht sich von selbst."], "Man sieht alle Kontinente auf einmal."),
        ch(p, "Was stimmt?", "Was gibt es auf der Erde mehr?", ["Wasser", "Land", "beides gleich viel"], "Wasser", keep=True),
        sort(p, "Was zeigt die Farbe?", "Was zeigt diese Farbe auf dem Globus meistens?", ["Wasser", "Land", "Eis"], [
            ("blau", "Wasser"), ("grün", "Land"), ("braun", "Land"), ("weiß", "Eis"),
        ]),
        wahr(p, "Auf einer flachen Weltkarte sehen manche Länder größer aus, als sie sind.", True, "Grönland zum Beispiel sieht riesig aus. Auf dem Globus stimmen die Größen."),
        wahr(p, "Den Globus muss man drehen, um alle Kontinente zu sehen.", True),
    ], mix=False),
    lesson("Die sieben Kontinente", "🗺️", [
        bildfrage(p, "Weißt du es?", "Wie viele Kontinente gibt es?", "weltkarte", ["5", "6", "7"], "7", keep=True),
        ch(p, "Was stimmt?", "Wie nennt man die großen, zusammenhängenden Landflächen der Erde?", ["Kontinente", "Ozeane", "Inseln"], "Kontinente"),
        *[bildfrage(p, "Welcher Kontinent ist das?", "Welcher Kontinent ist farbig?", z, drei(n, KN), n) for z, n in KZ],
        ch(p, "Was stimmt?", "Welcher ist der größte Kontinent?", ["Asien", "Europa", "Australien"], "Asien"),
        ch(p, "Was stimmt?", "Welcher ist der kleinste Kontinent?", ["Australien", "Afrika", "Asien"], "Australien"),
        ch(p, "Was stimmt?", "Auf welchem Kontinent leben wir?", ["Europa", "Afrika", "Nordamerika"], "Europa"),
        ch(p, "Was stimmt?", "Welcher Kontinent ist fast ganz mit Eis bedeckt?", ["die Antarktis", "Afrika", "Südamerika"], "die Antarktis"),
    ]),
    lesson("Kontinente beschriften", "✏️", [
        schaubild(p, "Beschrifte die Kontinente!", "weltkarte", KONT, KW, KH),
        bildwahl(p, "Tipp auf die Karte, auf der Afrika farbig ist!", ["weltkarte-afrika", "weltkarte-suedamerika", "weltkarte-australien"], "weltkarte-afrika"),
        bildwahl(p, "Tipp auf die Karte, auf der Europa farbig ist!", ["weltkarte-europa", "weltkarte-asien", "weltkarte-nordamerika"], "weltkarte-europa"),
    ], mix=False),
    lesson("Die Ozeane", "🌊", [
        ch(p, "Was ist ein Ozean?", "Ein Ozean ist ein riesiges, tiefes Meer und bedeckt einen großen Teil der Erde mit …", ["Wasser", "Land", "Sand"], "Wasser", keep=True),
        bildfrage(p, "Weißt du es?", "Wie viele Ozeane gibt es?", "weltkarte", ["3", "5", "7"], "5", keep=True),
        schaubild(p, "Beschrifte die Ozeane!", "weltkarte", OZE, KW, KH),
        ch(p, "Was stimmt?", "Welcher ist der größte Ozean?", ["der Pazifische Ozean", "der Atlantische Ozean", "der Indische Ozean"], "der Pazifische Ozean"),
        ch(p, "Was stimmt?", "Welcher Ozean liegt rund um den Nordpol?", ["der Arktische Ozean", "der Antarktische Ozean", "der Indische Ozean"], "der Arktische Ozean"),
        ch(p, "Was stimmt?", "Welcher Ozean liegt zwischen Europa und Amerika?", ["der Atlantische Ozean", "der Pazifische Ozean", "der Indische Ozean"], "der Atlantische Ozean"),
        ch(p, "Was stimmt?", "Welche zwei Meere liegen im Norden von Deutschland?", ["Nordsee und Ostsee", "Mittelmeer und Rotes Meer", "Pazifik und Atlantik"], "Nordsee und Ostsee"),
        wahr(p, "Das Wasser im Meer ist salzig.", True),
    ], mix=False),
    lesson("Tiere der Kontinente", "🦘", [
        pairs(p, "Wo lebt das Tier in freier Natur?", "Auf welchem Kontinent lebt dieses Tier in freier Natur?", [
            ("Känguru", "Australien"), ("Kaiserpinguin", "Antarktis"), ("Löwe", "Afrika"), ("Großer Panda", "Asien"),
        ]),
        pairs(p, "Wo lebt das Tier in freier Natur?", "Auf welchem Kontinent lebt dieses Tier in freier Natur?", [
            ("Lama", "Südamerika"), ("Bison", "Nordamerika"), ("Rothirsch", "Europa"),
        ]),
        wahr(p, "Eisbären und Pinguine treffen sich nie in freier Natur.", True, "Eisbären leben im hohen Norden, Pinguine im Süden, vor allem in der Antarktis."),
    ]),
    test(12),
])


# ---------- Schreiben ----------
os.makedirs(f"{OUT}/hsu", exist_ok=True)
for path, u in UNITS.items():
    with open(f"{OUT}/{path}", "w", encoding="utf-8") as f:
        json.dump(u, f, ensure_ascii=False, indent=1)
with open(f"{OUT}/wissen-hsu.json", "w", encoding="utf-8") as f:
    json.dump({"regeln": RULES}, f, ensure_ascii=False, indent=1)
print(len(UNITS), "Einheiten,", len(ids), "Aufgaben-IDs,", len(RULES), "Merkkarten")
