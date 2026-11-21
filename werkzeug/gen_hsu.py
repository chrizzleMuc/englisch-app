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


# ---------- Schreiben ----------
os.makedirs(f"{OUT}/hsu", exist_ok=True)
for path, u in UNITS.items():
    with open(f"{OUT}/{path}", "w", encoding="utf-8") as f:
        json.dump(u, f, ensure_ascii=False, indent=1)
with open(f"{OUT}/wissen-hsu.json", "w", encoding="utf-8") as f:
    json.dump({"regeln": RULES}, f, ensure_ascii=False, indent=1)
print(len(UNITS), "Einheiten,", len(ids), "Aufgaben-IDs,", len(RULES), "Merkkarten")
