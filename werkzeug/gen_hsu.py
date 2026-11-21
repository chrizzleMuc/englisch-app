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


# ---------- Schreiben ----------
os.makedirs(f"{OUT}/hsu", exist_ok=True)
for path, u in UNITS.items():
    with open(f"{OUT}/{path}", "w", encoding="utf-8") as f:
        json.dump(u, f, ensure_ascii=False, indent=1)
with open(f"{OUT}/wissen-hsu.json", "w", encoding="utf-8") as f:
    json.dump({"regeln": RULES}, f, ensure_ascii=False, indent=1)
print(len(UNITS), "Einheiten,", len(ids), "Aufgaben-IDs,", len(RULES), "Merkkarten")
