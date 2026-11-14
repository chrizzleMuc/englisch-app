# Erzeugt Deutsch 3. Klasse, Paket Rechtschreibung (Rest) und Grammatik:
#   inhalte/deutsch/k3-besondere-laute.json, k3-merkwoerter.json, k3-grossschreibung.json,
#   k3-fehler-finden.json, k3-artikel-pronomen.json, k3-verben.json, k3-nomen-endungen.json,
#   k3-adjektive.json
# Eigene Aufgaben (Gliederung grob nach LehrplanPLUS Bayern 3/4), nichts aus Büchern oder Apps kopiert.
# JSON nicht von Hand ändern, sondern hier und neu erzeugen: python3 werkzeug/gen_deutsch_k3b.py
import json, re, sys, os, unicodedata

OUT = sys.argv[1] if len(sys.argv) > 1 else "inhalte/deutsch"
ids = set()


def slug(s):
    s = s.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    s = unicodedata.normalize("NFKD", s)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:28]


def uid(i):
    i = i.rstrip("-")
    n, k = i, 2
    while n in ids:
        n = f"{i}-{k}"; k += 1
    ids.add(n)
    return n


def ch(p, task, prompt, options, answer, explain=None, keep=True, big=True):
    assert answer in options, (prompt, answer, options)
    t = {"kind": "choice", "id": uid(f"{p}-{slug(prompt)}"), "task": task, "prompt": prompt,
         "options": options, "answer": answer}
    if keep: t["keepOrder"] = True
    if big: t["bigOptions"] = True
    if explain: t["explain"] = explain
    return t


def ty(p, task, prompt, answer, before=None, also=None):
    t = {"kind": "type", "id": uid(f"{p}-{slug(prompt + ' ' + answer)}"), "task": task, "prompt": prompt, "answer": answer}
    if before: t["before"] = before
    if also: t["also"] = also
    return t


def sort(p, task, review, groups, items):
    return {"kind": "sort", "task": task, "review": review, "groups": groups,
            "items": [{"id": uid(f"{p}-{slug(t)}"), "text": t, "group": g} for t, g in items]}


def pairs(p, task, review, prs):
    return {"kind": "pairs", "task": task, "review": review,
            "pairs": [{"id": uid(f"{p}-{slug(a)}"), "a": a, "b": b} for a, b in prs]}


def photo(i, task):
    return {"kind": "photo", "id": uid(i), "task": task}


def lesson(title, icon, tasks=None, mix=False, **kw):
    l = {"title": title, "icon": icon}
    if mix: l["mix"] = True
    if tasks is not None: l["tasks"] = tasks
    l.update(kw)
    return l


def test(n=15):
    return lesson("Test", "🏆", test=True, count=n)


def unit(id_, title, image, color, lessons):
    return {"id": id_, "type": "schule", "title_de": title, "image": image, "color": color, "lessons": lessons}


def gap(word, part, mark="_"):
    """Ersetzt den ersten Treffer von part im Wort durch eine Lücke."""
    i = word.find(part)
    if i < 0:
        i = word.lower().find(part.lower())
    assert i >= 0, (word, part)
    return word[:i] + mark + word[i + len(part):]


units = {}

# ======================================================================
# PAKET 1: RECHTSCHREIBUNG
# ======================================================================

# ---------- Besondere Laute: sp, st, qu, v, x ----------
P = "d3-bl"
SPST = [("der Stern", "St", "Scht"), ("der Stein", "St", "Scht"), ("der Stuhl", "St", "Scht"),
        ("der Stift", "St", "Scht"), ("die Straße", "St", "Scht"), ("der Stiefel", "St", "Scht"),
        ("stark", "st", "scht"), ("stolpern", "st", "scht"),
        ("der Sport", "Sp", "Schp"), ("das Spiel", "Sp", "Schp"), ("die Spinne", "Sp", "Schp"),
        ("der Spiegel", "Sp", "Schp"), ("der Spaß", "Sp", "Schp"), ("springen", "sp", "schp"),
        ("spitz", "sp", "schp"), ("sparen", "sp", "schp")]
spst = []
for w, right, wrong in SPST:
    art, _, word = w.rpartition(" ")
    pre = (art + " ") if art else ""
    spst.append(ch(P + "-sp", "Wie schreibt man es richtig?", pre + gap(word, right, "…"),
                   [right, wrong], right,
                   f"{w}: Man spricht „{wrong}“, man schreibt „{right}“."))

QU = [("die Qualle", "Qu", "Kw"), ("der Quark", "Qu", "Kw"), ("die Quelle", "Qu", "Kw"),
      ("das Quadrat", "Qu", "Kw"), ("der Quatsch", "Qu", "Kw"), ("quaken", "qu", "kw"),
      ("quer", "qu", "kw"), ("bequem", "qu", "kw"), ("quietschen", "qu", "kw"),
      ("das Aquarium", "qu", "kw")]
qu = []
for w, right, wrong in QU:
    art, _, word = w.rpartition(" ")
    pre = (art + " ") if art else ""
    qu.append(ch(P + "-qu", "Wie schreibt man es richtig?", pre + gap(word, right, "…"),
                 [right, wrong], right, f"{w}: „kw“ schreibt man immer „qu“."))
qu_pairs = pairs(P + "-qp", "Was gehört zusammen?", "Wörter mit qu",
                 [("die Ente", "quakt"), ("die Tür", "quietscht"), ("die Qualle", "schwimmt im Meer"),
                  ("das Quadrat", "hat vier gleiche Seiten"), ("der Quark", "ist weiß und cremig")])

VF = [("der Vogel", "V"), ("der Vater", "V"), ("viel", "v"), ("vier", "v"), ("voll", "v"),
      ("vergessen", "v"), ("die Vorsicht", "V"), ("verstecken", "v"),
      ("der Fisch", "F"), ("die Feder", "F"), ("das Fenster", "F"), ("die Ferien", "F"),
      ("fertig", "f"), ("der Fuchs", "F"), ("fallen", "f"), ("für", "f")]
vf = []
for w, l in VF:
    art, _, word = w.rpartition(" ")
    pre = (art + " ") if art else ""
    opts = ["V", "F"] if l.isupper() else ["v", "f"]
    ex = "Wörter mit V muss man sich merken." if l in "Vv" else "Hier schreibt man ganz normal f."
    vf.append(ch(P + "-vf", "V oder F?", pre + "_" + word[1:], opts, l, f"{w} – {ex}"))
VW = [("die Vase", "V"), ("der Vulkan", "V"), ("das Klavier", "v"), ("der Pullover", "v"),
      ("die Vanille", "V"), ("das Video", "V"), ("die Wolke", "W"), ("der Wal", "W"),
      ("die Möwe", "w"), ("die Löwin", "w")]
vw = []
for w, l in VW:
    art, _, word = w.rpartition(" ")
    pre = (art + " ") if art else ""
    i = word.lower().index(l.lower())
    opts = ["V", "W"] if l.isupper() else ["v", "w"]
    ex = "Hier klingt das v wie w. Merkwort!" if l in "Vv" else "Hier schreibt man ganz normal w."
    vw.append(ch(P + "-vw", "V oder W?", pre + word[:i] + "_" + word[i + 1:], opts, l, f"{w} – {ex}"))

X = [("die Hexe", "x"), ("das Taxi", "x"), ("boxen", "x"), ("mixen", "x"), ("das Lexikon", "x"),
     ("der Fuchs", "chs"), ("der Dachs", "chs"), ("wachsen", "chs"), ("sechs", "chs"),
     ("der Ochse", "chs"), ("die Büchse", "chs"),
     ("der Keks", "ks"), ("links", "ks"), ("der Klecks", "cks")]
xl = []
for w, l in X:
    art, _, word = w.rpartition(" ")
    pre = (art + " ") if art else ""
    xl.append(ch(P + "-x", "Wie schreibt man den x-Laut?", pre + gap(word, l, "_"),
                 ["x", "chs", "ks", "cks"], l, f"{w} – das muss man sich merken."))
x_sort = sort(P + "-xs", "Sortiere nach der Schreibweise.", "x oder chs?", ["x", "chs"],
              [("die Hexe", "x"), ("das Taxi", "x"), ("mixen", "x"), ("der Boxer", "x"),
               ("der Fuchs", "chs"), ("wachsen", "chs"), ("sechs", "chs"), ("der Dachs", "chs")])

units["k3-besondere-laute"] = unit("d3-besondere-laute", "Besondere Laute: sp, st, qu, v, x", "🔤", "#7a52c7", [
    lesson("Sp und St", "🕷️", spst, mix=True),
    lesson("qu", "🪼", qu + [qu_pairs], mix=True),
    lesson("V oder F", "🐦", vf, mix=True),
    lesson("V oder W", "🌋", vw, mix=True),
    lesson("x, chs, ks", "🦊", xl + [x_sort], mix=True),
    lesson("Ins Heft", "✍️", [photo("d3-bl-foto",
        "Schreib je 3 Wörter mit Sp, St, qu und V in dein Heft und kreise die besondere Stelle ein.")]),
    test(),
])

# ---------- Merkwörter: langes i ohne ie ----------
P = "d3-mw"
LANG_I = [("das Kino", "i"), ("der Tiger", "i"), ("der Igel", "i"), ("der Biber", "i"),
          ("das Krokodil", "i"), ("die Maschine", "i"), ("das Benzin", "i"), ("der Kamin", "i"),
          ("die Musik", "i"), ("die Mandarine", "i"), ("die Medizin", "i"), ("die Fabrik", "i")]
IE = [("die Biene", "ie"), ("die Wiese", "ie"), ("der Spiegel", "ie"), ("die Ziege", "ie"),
      ("das Tier", "ie"), ("schief", "ie"), ("der Brief", "ie"), ("fliegen", "ie")]
IH = [("ihr", "ih"), ("ihm", "ih"), ("ihn", "ih"), ("ihnen", "ih")]


def i_task(w, l):
    art, _, word = w.rpartition(" ")
    pre = (art + " ") if art else ""
    return pre + gap(word, l, "_")


def io(w, opts, l):
    """Großbuchstaben-Optionen, wenn die Lücke am Wortanfang steht (Igel)."""
    if w.rpartition(" ")[2][0] == "I":
        return [o.capitalize() for o in opts], l.capitalize()
    return opts, l


langi = []
for w, l in LANG_I:
    o, a = io(w, ["i", "ie"], l)
    langi.append(ch(P + "-li", "i oder ie?", i_task(w, l), o, a, f"{w} – langes i ohne e. Merkwort!"))
mixi = []
for w, l in LANG_I[:2] + LANG_I[3:6] + IE + IH:
    ex = {"i": "Merkwort mit langem i ohne e.", "ie": "Meistens schreibt man langes i als ie.",
          "ih": "ihr, ihm, ihn, ihnen schreibt man mit ih."}[l]
    o, a = io(w, ["i", "ie", "ih"], l)
    mixi.append(ch(P + "-mx", "i, ie oder ih?", i_task(w, l), o, a, f"{w} – {ex}"))
i_sort = sort(P + "-so", "Sortiere die Wörter.", "i, ie oder ih?", ["i", "ie", "ih"],
              [("das Kino", "i"), ("der Tiger", "i"), ("das Krokodil", "i"), ("die Biene", "ie"),
               ("die Wiese", "ie"), ("fliegen", "ie"), ("ihr", "ih"), ("ihm", "ih")])
richtig = [ch(P + "-rg", "Welches Wort ist richtig geschrieben?", "", [a, b], a)
           for a, b in [("Kino", "Kieno"), ("Tiger", "Tieger"), ("Igel", "Iegel"), ("Biene", "Bine"),
                        ("Musik", "Musiek"), ("ihm", "iem"), ("Maschine", "Maschiene"), ("Wiese", "Wise")]]
for t in richtig:
    t.pop("prompt")
    t["keepOrder"] = False
    t["id"] = t["id"] + "-" + slug(t["answer"])
units["k3-merkwoerter"] = unit("d3-merkwoerter", "Merkwörter mit langem i", "🔑", "#c2588f", [
    lesson("Langes i ohne e", "🐅", langi, mix=True),
    lesson("i, ie oder ih", "🐝", mixi + [i_sort], mix=True),
    lesson("Richtig geschrieben?", "👀", richtig, mix=True),
    lesson("Ins Heft", "✍️", [photo("d3-mw-foto",
        "Schreib diese Merkwörter in dein Heft: Kino, Tiger, Igel, Krokodil, Maschine, Musik, ihr, ihm. Markiere das i.")]),
    test(),
])

# ---------- Großschreibung: Satzanfang und Zeitangaben ----------
P = "d3-gs"
SATZ = ["Am Morgen scheint die Sonne.", "Heute gehen wir ins Schwimmbad.", "Mein Bruder spielt Fußball.",
        "Gestern hat es geregnet.", "Wo ist mein Schuh?", "Komm schnell her!",
        "Leider ist der Kuchen alle.", "Nach der Schule esse ich Nudeln."]
satz = []
for s in SATZ:
    wrong = s[0].lower() + s[1:]
    satz.append(ch(P + "-sa", "Welcher Satz ist richtig geschrieben?", "", [s, wrong], s,
                   "Am Satzanfang schreibt man immer groß.", keep=False, big=False))
for t in satz:
    t.pop("prompt")
# Satzanfang nach Punkt
NACH = [("Wir spielen im Garten. _ann regnet es.", "D", "d"),
        ("Der Hund bellt. _ie Katze rennt weg.", "D", "d"),
        ("Ich habe Hunger. _st das Essen fertig?", "I", "i"),
        ("Pass auf! _ort kommt ein Auto.", "D", "d"),
        ("Wir gehen in den Zoo. _ort sehen wir Affen.", "D", "d"),
        ("Was machst du? _ch lese ein Buch.", "I", "i")]
nach = [ch(P + "-np", "Groß oder klein?", s, [g, k], g,
           "Nach einem Punkt, Ausrufezeichen oder Fragezeichen fängt ein neuer Satz an: groß!")
        for s, g, k in NACH]
# Zeitangaben
ZEIT = [("Wir treffen uns heute _bend.", "A", "a", "heute Abend – Abend ist hier ein Nomen."),
        ("_bends lese ich gern.", "A", "a", "Am Satzanfang immer groß."),
        ("Ich gehe _orgens zur Schule.", "m", "M", "morgens (mit s) schreibt man klein."),
        ("Am _ontag haben wir Sport.", "M", "m", "am Montag – nach „am“ kommt ein Nomen."),
        ("Wir schwimmen _ontags.", "m", "M", "montags (mit s) schreibt man klein."),
        ("Gestern _ittag gab es Suppe.", "M", "m", "gestern Mittag – Mittag ist ein Nomen."),
        ("In der _acht schlafe ich.", "N", "n", "in der Nacht – nach „der“ kommt ein Nomen."),
        ("Eulen jagen _achts.", "n", "N", "nachts (mit s) schreibt man klein."),
        ("Jeden _orgen esse ich Müsli.", "M", "m", "jeden Morgen – Morgen ist ein Nomen."),
        ("Am _achmittag spielen wir.", "N", "n", "am Nachmittag – nach „am“ kommt ein Nomen."),
        ("Ich gehe _ittwochs zum Turnen.", "m", "M", "mittwochs (mit s) schreibt man klein."),
        ("Morgen _rüh fahren wir los.", "f", "F", "morgen früh – früh schreibt man klein.")]
zeit = []
for s, r, w, ex in ZEIT:
    opts = sorted([r, w], key=lambda c: c.islower())
    zeit.append(ch(P + "-zt", "Groß oder klein?", s, opts, r, ex))
zeit_sort = sort(P + "-zs", "Groß oder klein?", "Zeitangaben", ["groß", "klein"],
                 [("am Abend", "groß"), ("heute Morgen", "groß"), ("am Sonntag", "groß"),
                  ("in der Nacht", "groß"), ("abends", "klein"), ("sonntags", "klein"),
                  ("nachts", "klein"), ("morgens", "klein")])
units["k3-grossschreibung"] = unit("d3-grossschreibung", "Großschreibung: Satzanfang und Zeitangaben", "👑", "#d18a1f", [
    lesson("Satzanfang", "🔠", satz, mix=True),
    lesson("Nach dem Punkt", "⏺️", nach, mix=True),
    lesson("Zeitangaben 1", "🕰️", zeit[:6], mix=True),
    lesson("Zeitangaben 2", "🕰️", zeit[6:], mix=True),
    lesson("Mit oder ohne s", "🌙", [zeit_sort]),
    lesson("Ins Heft", "✍️", [photo("d3-gs-foto",
        "Schreib 4 Sätze über deine Woche in dein Heft. Benutze: am Montag, abends, heute Morgen, sonntags.")]),
    test(),
])

# ---------- Fehler finden (Rechtschreibstrategien gemischt) ----------
P = "d3-ff"
FEHLER = [
    ("Der Hunt bellt laut.", "Hunt", "Hund", "Verlängern: die Hunde → Hund"),
    ("Im Walt wohnt ein Fuchs.", "Walt", "Wald", "Verlängern: die Wälder → Wald"),
    ("Das Kint spielt.", "Kint", "Kind", "Verlängern: die Kinder → Kind"),
    ("Der Zuk fährt schnell.", "Zuk", "Zug", "Verlängern: die Züge → Zug"),
    ("Mein Korp ist voll.", "Korp", "Korb", "Verlängern: die Körbe → Korb"),
    ("Die Keckse sind lecker.", "Keckse", "Kekse", "Keks schreibt man mit ks."),
    ("Wir schwimen im See.", "schwimen", "schwimmen", "Kurzer Selbstlaut: schwim-men → mm"),
    ("Die Kaze schläft.", "Kaze", "Katze", "Kurzer Selbstlaut: Kat-ze → tz"),
    ("Ich backe einen Kuchen mit Zuker.", "Zuker", "Zucker", "Kurzer Selbstlaut: Zu-cker → ck"),
    ("Die Beume sind grün.", "Beume", "Bäume", "Ableiten: der Baum → die Bäume"),
    ("Die Hende sind kalt.", "Hende", "Hände", "Ableiten: die Hand → die Hände"),
    ("Der Tieger brüllt.", "Tieger", "Tiger", "Tiger ist ein Merkwort mit i."),
    ("Wir fahren auf der Schtraße.", "Schtraße", "Straße", "Am Anfang schreibt man St, nicht Scht."),
    ("Die kwalle schwimmt.", "kwalle", "Qualle", "Qualle mit Qu – und groß, weil es ein Nomen ist."),
    ("am Abend lese ich.", "am", "Am", "Am Satzanfang schreibt man groß."),
    ("Wir spielen im garten.", "garten", "Garten", "Garten ist ein Nomen: groß!"),
    ("Der Vogel flikt hoch.", "flikt", "fliegt", "Verlängern: fliegen → fliegt"),
    ("Der Ball ist rund und bunnt.", "bunnt", "bunt", "Nach dem kurzen u hörst du schon zwei Mitlaute (n, t): nichts verdoppeln."),
]
finden, schreiben = [], []
for s, wrong, right, ex in FEHLER:
    words = [w.strip(".!?") for w in s.split()]
    cands = [w for w in words if len(w) > 2 and w != wrong][:2] + [wrong]
    cands = sorted(set(cands), key=words.index)
    finden.append(ch(P + "-fi", "Welches Wort ist falsch geschrieben?", s, cands, wrong,
                     f"Richtig: {right}. {ex}", big=False))
    schreiben.append(ty(P + "-sc", f"Schreib das falsche Wort richtig: „{wrong}“", s, right))
units["k3-fehler-finden"] = unit("d3-fehler-finden", "Fehler finden und berichtigen", "🔍", "#3f8f6f", [
    lesson("Fehler finden 1", "🔎", finden[:9], mix=True),
    lesson("Fehler finden 2", "🔎", finden[9:], mix=True),
    lesson("Richtig schreiben 1", "✏️", schreiben[:9]),
    lesson("Richtig schreiben 2", "✏️", schreiben[9:]),
    lesson("Ins Heft", "✍️", [photo("d3-ff-foto",
        "Nimm einen Text aus deinem Heft. Such 3 Fehler oder schwierige Wörter und schreib dazu, wie du es prüfst (verlängern, ableiten, Merkwort).")]),
    test(),
])

# ======================================================================
# PAKET 2: GRAMMATIK
# ======================================================================

# ---------- Artikel und Pronomen ----------
P = "d3-ap"
ART = [("Tisch", "der"), ("Sonne", "die"), ("Haus", "das"), ("Löffel", "der"), ("Gabel", "die"),
       ("Messer", "das"), ("Schrank", "der"), ("Brille", "die"), ("Fenster", "das"), ("Mond", "der"),
       ("Blume", "die"), ("Auto", "das")]
art = [ch(P + "-ar", "Welcher Artikel passt?", "___ " + w, ["der", "die", "das"], a, f"{a} {w}") for w, a in ART]
UNB = {"der": "ein", "die": "eine", "das": "ein"}
best = sort(P + "-bu", "Bestimmter oder unbestimmter Artikel?", "Bestimmt oder unbestimmt?",
            ["bestimmt (der, die, das)", "unbestimmt (ein, eine)"],
            [("der Hund", "bestimmt (der, die, das)"), ("die Katze", "bestimmt (der, die, das)"),
             ("das Pferd", "bestimmt (der, die, das)"), ("der Baum", "bestimmt (der, die, das)"),
             ("ein Apfel", "unbestimmt (ein, eine)"), ("eine Maus", "unbestimmt (ein, eine)"),
             ("ein Buch", "unbestimmt (ein, eine)"), ("eine Tasse", "unbestimmt (ein, eine)")])
unb = [ch(P + "-ub", "Welcher unbestimmte Artikel passt?", "___ " + w, ["ein", "eine"], UNB[a],
          f"{a} {w} → {UNB[a]} {w}") for w, a in ART[:8]]
PRON_ERK = [("Gestern hat sie einen Kuchen gebacken.", "sie", ["Gestern", "sie", "Kuchen"]),
            ("Wir gehen heute schwimmen.", "Wir", ["Wir", "gehen", "heute"]),
            ("Morgen besuchst du Oma.", "du", ["Morgen", "du", "Oma"]),
            ("Der Ball ist rot. Er rollt weg.", "Er", ["Ball", "rot", "Er"]),
            ("Das Baby lacht, weil es Hunger hat.", "es", ["Baby", "lacht", "es"]),
            ("Habt ihr den Hasen gesehen?", "ihr", ["Habt", "ihr", "Hasen"]),
            ("Ich male einen Drachen.", "Ich", ["Ich", "male", "Drachen"]),
            ("Die Kinder spielen, bis sie müde sind.", "sie", ["Kinder", "spielen", "sie"])]
pron_erk = [ch(P + "-pe", "Welches Wort ist ein Pronomen?", s, o, a,
               "Pronomen sind Fürwörter: ich, du, er, sie, es, wir, ihr, sie.", big=False) for s, a, o in PRON_ERK]
PRON = [("Lisa malt ein Bild. ___ malt ein Haus.", "Sie", ["Er", "Sie", "Es"], "Lisa → sie"),
        ("Der Hund bellt. ___ hat Hunger.", "Er", ["Er", "Sie", "Es"], "der Hund → er"),
        ("Das Pferd rennt. ___ ist schnell.", "Es", ["Er", "Sie", "Es"], "das Pferd → es"),
        ("Tom und ich spielen. ___ bauen eine Burg.", "Wir", ["Wir", "Ihr", "Sie"], "Tom und ich → wir"),
        ("Die Kinder lachen. ___ sind fröhlich.", "Sie", ["Wir", "Ihr", "Sie"], "die Kinder → sie"),
        ("Ben und Mia, kommt ___ mit?", "ihr", ["wir", "ihr", "sie"], "Wenn man mehrere anspricht: ihr"),
        ("Die Blume blüht. ___ ist gelb.", "Sie", ["Er", "Sie", "Es"], "die Blume → sie"),
        ("Opa liest. ___ trägt eine Brille.", "Er", ["Er", "Sie", "Es"], "Opa → er"),
        ("Das Auto ist neu. ___ glänzt.", "Es", ["Er", "Sie", "Es"], "das Auto → es"),
        ("Mama und Papa kochen. ___ machen Suppe.", "Sie", ["Wir", "Ihr", "Sie"], "Mama und Papa → sie")]
pron = [ch(P + "-pv", "Welches Pronomen passt?", s, o, a, ex) for s, a, o, ex in PRON]
pron_pairs = pairs(P + "-pp", "Ersetze durch ein Pronomen.", "Welches Pronomen passt?",
                   [("der Vater", "er"), ("die Lehrerin", "sie"), ("das Kind", "es"),
                    ("Mia und ich", "wir"), ("du und Ben", "ihr")])
units["k3-artikel-pronomen"] = unit("d3-artikel-pronomen", "Artikel und Pronomen", "👉", "#4a7bd0", [
    lesson("der, die, das", "📌", art, mix=True),
    lesson("ein oder eine", "1️⃣", [best] + unb, mix=False),
    lesson("Pronomen erkennen", "🔎", pron_erk, mix=True),
    lesson("Pronomen verwenden", "🔁", pron + [pron_pairs], mix=True),
    lesson("Ins Heft", "✍️", [photo("d3-ap-foto",
        "Schreib 3 Sätze über ein Tier. Benutze im zweiten und dritten Satz ein Pronomen statt dem Namen (er, sie, es).")]),
    test(),
])

# ---------- Verben: Gegenwart und Vergangenheit ----------
P = "d3-vb"
SCHWACH_G = [("malen", "du", "malst"), ("spielen", "er", "spielt"), ("lachen", "wir", "lachen"),
             ("kaufen", "ihr", "kauft"), ("hören", "ich", "höre"), ("bauen", "Mia", "baut"),
             ("suchen", "du", "suchst"), ("lernen", "ihr", "lernt"), ("wohnen", "er", "wohnt"),
             ("tanzen", "du", "tanzt"), ("rennen", "wir", "rennen"), ("singen", "es", "singt")]
sg = []
for inf, person, form in SCHWACH_G:
    sg.append(ty(P + "-sg", "Schreib die richtige Form.", f"{inf} – {person}", form, before=person))
sg_pairs = pairs(P + "-sp", "Was gehört zusammen?", "Verb in der Gegenwart",
                 [("ich", "male"), ("du", "malst"), ("er", "malt"), ("wir", "malen")])
STARK_G = [("essen", "er", "isst", "esst"), ("lesen", "sie", "liest", "lest"), ("geben", "du", "gibst", "gebst"),
           ("fahren", "er", "fährt", "fahrt"), ("laufen", "sie", "läuft", "lauft"), ("sehen", "du", "siehst", "sehst"),
           ("schlafen", "es", "schläft", "schlaft"), ("nehmen", "er", "nimmt", "nehmt"),
           ("helfen", "du", "hilfst", "helfst"), ("tragen", "sie", "trägt", "tragt"),
           ("fallen", "er", "fällt", "fallt"), ("sprechen", "du", "sprichst", "sprechst")]
stg = [ch(P + "-st", "Was ist richtig?", f"{inf} – {p} …", [f"{p} {r}", f"{p} {w}"], f"{p} {r}",
          f"Bei {inf} ändert sich der Selbstlaut: {p} {r}.", keep=False) for inf, p, r, w in STARK_G]
stg_type = [ty(P + "-sy", "Schreib die richtige Form.", f"{inf} – {p}", r, before=p)
            for inf, p, r, w in STARK_G[:8]]
SCHWACH_V = [("spielen", "ich spiele", "spielte"), ("lachen", "wir lachen", "lachten"), ("kaufen", "ich kaufe", "kaufte"),
             ("malen", "er malt", "malte"), ("hören", "du hörst", "hörtest"), ("wohnen", "sie wohnt", "wohnte"),
             ("bauen", "wir bauen", "bauten"), ("sagen", "er sagt", "sagte"), ("lernen", "ich lerne", "lernte"),
             ("tanzen", "sie tanzt", "tanzte"), ("machen", "ihr macht", "machtet"), ("holen", "ich hole", "holte")]
sv = []
for inf, now, past in SCHWACH_V:
    p = now.split()[0]
    sv.append(ty(P + "-sv", "Schreib in der Vergangenheit.", f"heute: {now}", past, before="gestern: " + p))
sv_sort = sort(P + "-ss", "Schwaches oder starkes Verb?", "Schwach oder stark?",
               ["schwach (-te)", "stark (neuer Selbstlaut)"],
               [("suchte", "schwach (-te)"), ("lachte", "schwach (-te)"), ("spielte", "schwach (-te)"),
                ("kaufte", "schwach (-te)"), ("hörte", "schwach (-te)"),
                ("rief", "stark (neuer Selbstlaut)"), ("ging", "stark (neuer Selbstlaut)"),
                ("fand", "stark (neuer Selbstlaut)"), ("schrieb", "stark (neuer Selbstlaut)"),
                ("sang", "stark (neuer Selbstlaut)")])
units["k3-verben"] = unit("d3-verben", "Verben: Gegenwart und Vergangenheit", "⚽", "#d0573f", [
    lesson("Gegenwart: schwache Verben", "🖍️", [sg_pairs] + sg),
    lesson("Gegenwart: starke Verben", "📖", stg, mix=True),
    lesson("Starke Verben schreiben", "✏️", stg_type),
    lesson("Vergangenheit mit -te", "⏪", sv),
    lesson("Schwach oder stark?", "⚖️", [sv_sort]),
    lesson("Ins Heft", "✍️", [photo("d3-vb-foto",
        "Schreib auf, was du gestern gemacht hast: 4 Sätze in der Vergangenheit (z. B. Ich spielte …, Ich ging …).")]),
    test(),
])

# ---------- Nomen-Endungen: -nis und gemischt ----------
P = "d3-ne"
NIS = [("geheim", "das Geheimnis"), ("erleben", "das Erlebnis"), ("ergeben", "das Ergebnis"),
       ("hindern", "das Hindernis"), ("finster", "die Finsternis"), ("wild", "die Wildnis"),
       ("erlauben", "die Erlaubnis"), ("verstehen", "das Verständnis"), ("zeugen", "das Zeugnis"),
       ("bedürfen", "das Bedürfnis")]
nis = [ty(P + "-ni", "Bilde ein Nomen mit -nis. Mit Artikel!", w, n) for w, n in NIS[:8]]
NISS = [("das Geheimnis", "die Geheimni_e"), ("das Erlebnis", "die Erlebni_e"), ("das Zeugnis", "die Zeugni_e"),
        ("das Ergebnis", "die Ergebni_e"), ("das Hindernis", "die Hinderni_e")]
niss = [ch(P + "-nm", "Mehrzahl: s oder ss?", f"{a} → {b}", ["s", "ss"], "ss",
           "In der Mehrzahl wird -nis zu -nisse.") for a, b in NISS]
niss += [ch(P + "-ne", "Einzahl: s oder ss?", w, ["s", "ss"], "s",
            "In der Einzahl schreibt man -nis mit einem s.")
         for w in ["das Ergebni_", "die Wildni_", "das Zeugni_", "das Hinderni_"]]
END = [("frei", "Frei", "heit"), ("wohnen", "Wohn", "ung"), ("freundlich", "Freundlich", "keit"),
       ("geheim", "Geheim", "nis"), ("krank", "Krank", "heit"), ("sauber", "Sauber", "keit"),
       ("hoffen", "Hoff", "nung"), ("finster", "Finster", "nis"), ("einsam", "Einsam", "keit"),
       ("dunkel", "Dunkel", "heit"), ("zeichnen", "Zeichn", "ung"), ("wild", "Wild", "nis"),
       ("ehrlich", "Ehrlich", "keit"), ("erleben", "Erleb", "nis")]
end = []
for w, stem, e in END:
    if e == "nung":
        stem, e = "Hoffn", "ung"
    end.append(ch(P + "-en", "Welche Endung passt?", f"{w} → die/das {stem}…", ["-ung", "-heit", "-keit", "-nis"],
                  "-" + e, f"{w} → {stem}{e}"))
end_sort = sort(P + "-es", "Sortiere nach der Endung.", "-ung, -heit, -keit oder -nis?",
                ["-ung", "-heit", "-keit", "-nis"],
                [("die Zeitung", "-ung"), ("die Rechnung", "-ung"), ("die Gesundheit", "-heit"),
                 ("die Schönheit", "-heit"), ("die Fröhlichkeit", "-keit"), ("die Müdigkeit", "-keit"),
                 ("das Ereignis", "-nis"), ("die Kenntnis", "-nis")])
units["k3-nomen-endungen"] = unit("d3-nomen-endungen", "Nomen mit -nis und gemischten Endungen", "🧩", "#8c5a2b", [
    lesson("-nis", "🔐", nis),
    lesson("-nis oder -nisse", "👥", niss, mix=True),
    lesson("Welche Endung?", "🔚", end + [end_sort], mix=True),
    lesson("Ins Heft", "✍️", [photo("d3-ne-foto",
        "Schreib je 2 Nomen mit -ung, -heit, -keit und -nis mit Artikel in dein Heft.")]),
    test(12),
])

# ---------- Adjektive ----------
P = "d3-ad"
ADJ_ERK = [("Der kleine Hund bellt.", "kleine", ["kleine", "Hund", "bellt"]),
           ("Die Suppe ist heiß.", "heiß", ["Suppe", "ist", "heiß"]),
           ("Ein bunter Vogel singt.", "bunter", ["bunter", "Vogel", "singt"]),
           ("Mein Bruder rennt schnell.", "schnell", ["Bruder", "rennt", "schnell"]),
           ("Die alte Burg steht am Berg.", "alte", ["alte", "Burg", "steht"]),
           ("Der Drache ist grün und gefährlich.", "gefährlich", ["Drache", "ist", "gefährlich"]),
           ("Wir essen süße Kirschen.", "süße", ["essen", "süße", "Kirschen"]),
           ("Das Wasser ist kalt.", "kalt", ["Wasser", "ist", "kalt"])]
adj_erk = [ch(P + "-er", "Welches Wort ist ein Adjektiv?", s, o, a,
              "Adjektive sagen, wie etwas ist.", big=False) for s, a, o in ADJ_ERK]
adj_sort = sort(P + "-ws", "Welche Wortart?", "Nomen, Verb oder Adjektiv?", ["Nomen", "Verb", "Adjektiv"],
                [("der Baum", "Nomen"), ("die Wolke", "Nomen"), ("laufen", "Verb"), ("lachen", "Verb"),
                 ("weich", "Adjektiv"), ("laut", "Adjektiv"), ("das Glück", "Nomen"), ("schwimmen", "Verb"),
                 ("lustig", "Adjektiv")])
gp1 = pairs(P + "-g1", "Finde das Gegenteil.", "Gegensatzpaare",
            [("groß", "klein"), ("heiß", "kalt"), ("laut", "leise"), ("schnell", "langsam"), ("hell", "dunkel")])
gp2 = pairs(P + "-g2", "Finde das Gegenteil.", "Gegensatzpaare",
            [("nass", "trocken"), ("dick", "dünn"), ("hart", "weich"), ("voll", "leer"), ("alt", "jung")])
GEGEN = [("schwer", "leicht", ["leicht", "dick", "laut"]), ("früh", "spät", ["spät", "schnell", "kurz"]),
         ("lang", "kurz", ["kurz", "klein", "dünn"]), ("fleißig", "faul", ["faul", "müde", "lustig"]),
         ("sauber", "schmutzig", ["schmutzig", "nass", "kalt"]), ("mutig", "ängstlich", ["ängstlich", "traurig", "leise"])]
gegen = [ch(P + "-gg", "Was ist das Gegenteil?", w, o, a, f"{w} ↔ {a}", keep=False) for w, a, o in GEGEN]
ANP = [("ein ___ Hund", "kleiner", ["kleiner", "kleine", "kleines"]),
       ("eine ___ Katze", "kleine", ["kleiner", "kleine", "kleines"]),
       ("ein ___ Pferd", "kleines", ["kleiner", "kleine", "kleines"]),
       ("der ___ Baum", "große", ["großer", "große", "großes"]),
       ("die ___ Burg", "alte", ["alter", "alte", "altes"]),
       ("ein ___ Zauberer", "alter", ["alter", "alte", "altes"]),
       ("ein ___ Haus", "rotes", ["roter", "rote", "rotes"]),
       ("eine ___ Blume", "gelbe", ["gelber", "gelbe", "gelbes"]),
       ("das ___ Wasser", "kalte", ["kalter", "kalte", "kaltes"]),
       ("ein ___ Ball", "bunter", ["bunter", "bunte", "buntes"])]
anp = [ch(P + "-an", "Welche Form passt?", s, o, a, s.replace("___", a)) for s, a, o in ANP]
IGLICH = [("die Lust", "lust", "ig"), ("der Freund", "freund", "lich"), ("der Hunger", "hungr", "ig"),
          ("die Gefahr", "gefähr", "lich"), ("die Sonne", "sonn", "ig"), ("der Schreck", "schreck", "lich"),
          ("der Mut", "mut", "ig"), ("die Freude", "fröh", "lich"), ("der Wind", "wind", "ig"),
          ("die Angst", "ängst", "lich"), ("der Durst", "durst", "ig"), ("die Ehre", "ehr", "lich")]
iglich = [ch(P + "-il", "-ig oder -lich?", f"{n} → {s}…", ["-ig", "-lich"], "-" + e,
             f"{s}{e}" + (f" (verlängern: {s}{e}e)" if e == "ig" else "")) for n, s, e in IGLICH]
IGICH = [("lustig", "lusti_", "g", "lustige"), ("billig", "billi_", "g", "billige"),
         ("eisig", "eisi_", "g", "eisige"), ("traurig", "trauri_", "g", "traurige"),
         ("fertig", "ferti_", "g", "fertige"), ("ich", "i_", "ch", None)]
igich = [ch(P + "-ic", "g oder ch? Verlängere!", p, ["g", "ch"], a,
            f"{w} – verlängern: {v}" if v else "ich – kein Adjektiv, Merkwort.")
         for w, p, a, v in IGICH[:5]]
ZUS = [("so schnell wie der Blitz", "blitzschnell"), ("so kalt wie Eis", "eiskalt"),
       ("so weiß wie Schnee", "schneeweiß"), ("so stark wie ein Bär", "bärenstark"),
       ("so leicht wie eine Feder", "federleicht"), ("so rund wie eine Kugel", "kugelrund"),
       ("so süß wie Zucker", "zuckersüß"), ("so glatt wie ein Spiegel", "spiegelglatt"),
       ("so blau wie der Himmel", "himmelblau"), ("so groß wie ein Riese", "riesengroß")]
zus = [ty(P + "-zs", "Bilde ein zusammengesetztes Adjektiv.", a, b) for a, b in ZUS]
ZUSF = [("hell + blau", "hellblau"), ("dunkel + rot", "dunkelrot"), ("nass + kalt", "nasskalt"),
        ("klatschen + nass", "klatschnass"), ("blitzen + blank", "blitzblank"), ("hell + grün", "hellgrün")]
zusf = [ty(P + "-zf", "Setz zusammen. Schreib klein!", a, b) for a, b in ZUSF]
STEIG = [("klein", "kleiner", "kleinsten"), ("schnell", "schneller", "schnellsten"),
         ("groß", "größer", "größten"), ("alt", "älter", "ältesten"), ("lang", "länger", "längsten"),
         ("warm", "wärmer", "wärmsten"), ("gut", "besser", "besten"), ("viel", "mehr", "meisten"),
         ("gern", "lieber", "liebsten"), ("hoch", "höher", "höchsten")]
steig = [ty(P + "-sg", "Steigere das Adjektiv.", f"{a} – {b} – am …", c, before="am") for a, b, c in STEIG]
VERGL = [("Der Elefant ist ___ als die Maus. (groß)", "größer", ["größer", "großer", "am größten"]),
         ("Die Schnecke ist ___ langsam ___ die Raupe. (gleich)", "so – wie", ["so – wie", "so – als"]),
         ("Ein Gepard ist ___ als ein Pferd. (schnell)", "schneller", ["schneller", "schnellster", "am schnellsten"]),
         ("Der Wal ist das ___ Tier im Meer. (groß)", "größte", ["größte", "größer", "großte"]),
         ("Mein Opa ist ___ als mein Papa. (alt)", "älter", ["älter", "alter", "am ältesten"]),
         ("Eis mag ich ___ als Spinat. (gern)", "lieber", ["lieber", "gerner", "am liebsten"])]
vergl = [ch(P + "-vg", "Was passt?", s, o, a,
            "Gleich: so … wie. Unterschied: …er als." if "gleich" in s else s.split(" (")[0].replace("___", a),
            keep=False, big=False) for s, a, o in VERGL]
for t in vergl:
    if t["answer"] == "so – wie":
        t["explain"] = "Die Schnecke ist so langsam wie die Raupe. Gleich: so … wie."
units["k3-adjektive"] = unit("d3-adjektive", "Adjektive", "🎨", "#2f9fb0", [
    lesson("Adjektive erkennen", "🔎", adj_erk + [adj_sort], mix=True),
    lesson("Gegensatzpaare", "↔️", [gp1, gp2] + gegen),
    lesson("Adjektive anpassen", "🏰", anp, mix=True),
    lesson("-ig und -lich", "🦋", iglich + igich, mix=True),
    lesson("Zusammengesetzte Adjektive", "⚡", zus[:6] + zusf[:3]),
    lesson("Noch mehr zusammensetzen", "⚡", zus[6:] + zusf[3:]),
    lesson("Steigern", "📈", steig),
    lesson("Vergleichen", "⚖️", vergl, mix=True),
    lesson("Ins Heft", "✍️", [photo("d3-ad-foto",
        "Beschreibe dein Lieblingstier mit mindestens 5 Adjektiven (z. B. Mein Hund ist klein, braun und frech.)")]),
    test(),
])

os.makedirs(OUT, exist_ok=True)
for name, u in units.items():
    with open(os.path.join(OUT, name + ".json"), "w", encoding="utf-8") as f:
        json.dump(u, f, ensure_ascii=False, indent=1)
        f.write("\n")
    n = sum(len(l.get("tasks", [])) for l in u["lessons"])
    print(name, len(u["lessons"]), "Lektionen,", n, "Aufgaben")
