# Erzeugt Deutsch 3. Klasse, Paket Sätze und Blitzlesen:
#   inhalte/deutsch/k3-satzarten.json, k3-satzglieder.json, k3-woertliche-rede.json, k3-blitzlesen.json
# Eigene Aufgaben (Gliederung grob nach LehrplanPLUS Bayern 3/4), nichts aus Büchern oder Apps kopiert.
# Neue Aufgabenarten: build (Satz aus Bausteinen bauen) und flash (Blitzlesen).
# JSON nicht von Hand ändern, sondern hier und neu erzeugen: python3 werkzeug/gen_deutsch_k3c.py
import itertools
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


def build(p, task, tiles, answers, end=".", show=None, explain=None, hint=None):
    t = {"kind": "build", "id": uid(f"{p}-{slug(' '.join(answers[0]))}"), "task": task, "tiles": tiles,
         "answers": answers, "end": end}
    if show: t["show"] = show
    if explain: t["explain"] = explain
    if hint: t["hint"] = hint
    return t


def flash(p, word, others, ms):
    return {"kind": "flash", "id": uid(f"{p}-{slug(word)}"), "task": "Blitzlesen: Was stand da?",
            "word": word, "ms": ms, "options": [word] + others, "answer": word}


def cap(s):
    return s[0].upper() + s[1:]


def sentence(blocks, end="."):
    return cap(" ".join(blocks)) + end


PRON = {"ich", "du", "er", "sie", "es", "wir", "ihr", "mir", "dir", "uns"}


def v2_orders(blocks, verb):
    """Alle Reihenfolgen mit dem Verb an 2. Stelle (Aussagesatz)."""
    rest = [b for i, b in enumerate(blocks) if i != verb]
    out = []
    for perm in itertools.permutations(rest):
        o = [perm[0], blocks[verb]] + list(perm[1:])
        # Pronomen (wir, mir …) stehen vorne oder direkt nach dem Verb, sonst klingt es falsch
        if all(i in (0, 2) for i, x in enumerate(o) if x in PRON):
            out.append(o)
    return out


units = {}

# ======================================================================
# SATZARTEN UND SATZZEICHEN
# ======================================================================
P = "d3-sa"
EXPL = {".": "Aussagesatz: Er erzählt etwas. Am Ende steht ein Punkt.",
        "?": "Fragesatz: Jemand will etwas wissen. Am Ende steht ein Fragezeichen.",
        "!": "Ausruf oder Aufforderung: Jemand ruft oder will, dass du etwas tust. Am Ende steht ein Ausrufezeichen."}
SZ = [("Wir gehen heute ins Kino", "."), ("Wann beginnt der Film", "?"), ("Pass auf, da kommt ein Auto", "!"),
      ("Mein Bruder spielt Fußball", "."), ("Hast du deine Hausaufgaben gemacht", "?"), ("Hurra, wir haben Ferien", "!"),
      ("Die Katze schläft auf dem Sofa", "."), ("Wo wohnt der Igel im Winter", "?"), ("Komm sofort her", "!"),
      ("Im Herbst fallen die Blätter", "."), ("Warum ist der Himmel blau", "?"), ("Au, das tut weh", "!"),
      ("Magst du Erdbeereis", "?"), ("Räum dein Zimmer auf", "!"), ("Der Bus fährt um acht Uhr", "."),
      ("Wie viele Beine hat eine Spinne", "?")]
sz = [ch(P + "-sz", "Welches Zeichen gehört ans Ende?", s + " _", [".", "?", "!"], e, f"{s}{e} {EXPL[e]}") for s, e in SZ]

ART = ["Aussagesatz", "Fragesatz", "Ausruf/Aufforderung"]
SORT1 = [("Der Hase hoppelt über die Wiese.", 0), ("Wer hat meinen Stift?", 1), ("Halt, stopp!", 2),
         ("Morgen besuchen wir Oma.", 0), ("Kannst du mir helfen?", 1), ("Mach bitte das Fenster zu!", 2)]
SORT2 = [("Ich habe einen Wackelzahn.", 0), ("Was gibt es zum Essen?", 1), ("Toll, ein Regenbogen!", 2),
         ("Der Wind ist heute kalt.", 0), ("Gehst du mit auf den Spielplatz?", 1), ("Sei bitte leise!", 2)]
sort1 = sort(P + "-so", "In welche Gruppe gehört der Satz?", "Welche Satzart ist das?", ART, [(s, ART[g]) for s, g in SORT1])
sort2 = sort(P + "-so", "In welche Gruppe gehört der Satz?", "Welche Satzart ist das?", ART, [(s, ART[g]) for s, g in SORT2])

WF = [("___ wohnst du?", "Wo", ["Wo", "Wer", "Wann"]), ("___ hat an der Tür geklingelt?", "Wer", ["Wer", "Wie", "Wo"]),
      ("___ fängt die Schule an?", "Wann", ["Wann", "Was", "Wer"]), ("___ isst du am liebsten?", "Was", ["Was", "Wo", "Wann"]),
      ("___ heißt deine Lehrerin?", "Wie", ["Wie", "Wer", "Wo"]), ("___ weint das Baby?", "Warum", ["Warum", "Was", "Wer"]),
      ("___ fährt der Zug hin?", "Wohin", ["Wohin", "Wann", "Wer"]), ("___ alt bist du?", "Wie", ["Wie", "Was", "Wo"])]
wf = [ch(P + "-wf", "Welches Fragewort passt?", s, o, a, s.replace("___", a)) for s, a, o in WF]

SG = [("Lena malt ein Bild es ist bunt", "Bild", ["malt", "Bild", "es"], "Lena malt ein Bild. Es ist bunt."),
      ("Der Hund bellt er will spielen", "bellt", ["Hund", "bellt", "er"], "Der Hund bellt. Er will spielen."),
      ("Wir backen Kekse sie schmecken lecker", "Kekse", ["backen", "Kekse", "sie"], "Wir backen Kekse. Sie schmecken lecker."),
      ("Tim hat Hunger er isst einen Apfel", "Hunger", ["hat", "Hunger", "er"], "Tim hat Hunger. Er isst einen Apfel."),
      ("Es regnet stark wir bleiben drinnen", "stark", ["regnet", "stark", "wir"], "Es regnet stark. Wir bleiben drinnen."),
      ("Oma kommt morgen wir freuen uns", "morgen", ["kommt", "morgen", "wir"], "Oma kommt morgen. Wir freuen uns."),
      ("Der Ball rollt weg die Katze rennt hinterher", "weg", ["rollt", "weg", "die"], "Der Ball rollt weg. Die Katze rennt hinterher."),
      ("Im Garten blühen Rosen sie duften gut", "Rosen", ["blühen", "Rosen", "sie"], "Im Garten blühen Rosen. Sie duften gut.")]
sg = [ch(P + "-sg", "Hier fehlt ein Punkt. Nach welchem Wort endet der erste Satz?", s, o, a,
         f"{e} Nach dem Punkt schreibt man groß.") for s, a, o, e in SG]

KO = [("Ich kaufe Äpfel Birnen und Bananen.", "nach Äpfel", ["nach Äpfel", "nach Birnen", "nach und"], "Ich kaufe Äpfel, Birnen und Bananen."),
      ("Lisa hat einen Hund eine Katze und zwei Hasen.", "nach Hund", ["nach Hund", "nach Katze", "nach zwei"], "Lisa hat einen Hund, eine Katze und zwei Hasen."),
      ("Im Mäppchen sind Stifte ein Lineal und ein Radiergummi.", "nach Stifte", ["nach Stifte", "nach Lineal", "nach Mäppchen"], "Im Mäppchen sind Stifte, ein Lineal und ein Radiergummi."),
      ("Der Ball ist rund bunt und weich.", "nach rund", ["nach rund", "nach bunt", "nach Ball"], "Der Ball ist rund, bunt und weich.")]
ko = [ch(P + "-ko", "Wo fehlt das Komma?", s, o, a, f"{e} Vor „und“ steht kein Komma.") for s, a, o, e in KO]
KZ = [("Im Zoo sehen wir Affen Löwen Zebras und Elefanten.", "2", "Im Zoo sehen wir Affen, Löwen, Zebras und Elefanten."),
      ("Zum Frühstück gibt es Brot Butter Honig Käse und Milch.", "3", "Zum Frühstück gibt es Brot, Butter, Honig, Käse und Milch."),
      ("Wir spielen Fangen und Verstecken.", "0", "Wir spielen Fangen und Verstecken. Bei nur zwei Dingen mit „und“ braucht man kein Komma.")]
kz = [ch(P + "-kz", "Wie viele Kommas fehlen?", s, ["0", "1", "2", "3"], a, e) for s, a, e in KZ]

# Sätze bauen: Aussagesätze (jede Reihenfolge mit dem Verb an 2. Stelle zählt) und Fragen
AUS = [(["der Igel", "schläft", "im Winter"], 1), (["meine Oma", "strickt", "einen Schal"], 1),
       (["die Kinder", "bauen", "im Sand", "eine Burg"], 1), (["am Abend", "liest", "Papa", "ein Buch"], 1)]
aus = [build(P + "-ab", "Bau einen Aussagesatz!", b, v2_orders(b, v), ".",
             hint="Das Verb steht im Aussagesatz an zweiter Stelle. Probier es nochmal!") for b, v in AUS]
FR = [(["kommst", "du", "morgen"], "Ja-Nein-Frage: Das Verb steht ganz vorne."),
      (["wo", "wohnt", "der Igel"], "W-Frage: Das Fragewort steht vorne, dann das Verb."),
      (["hast", "du", "einen Hund"], "Ja-Nein-Frage: Das Verb steht ganz vorne."),
      (["wann", "beginnt", "die Schule"], "W-Frage: Das Fragewort steht vorne, dann das Verb."),
      (["kann", "Tom", "schwimmen"], "Ja-Nein-Frage: Das Verb steht ganz vorne."),
      (["warum", "weint", "das Baby"], "W-Frage: Das Fragewort steht vorne, dann das Verb.")]
fr = [build(P + "-fb", "Bau eine Frage!", b, [b], "?", explain=e,
            hint="Bei einer Frage steht das Verb oder das Fragewort vorne. Probier es nochmal!") for b, e in FR]

units["k3-satzarten"] = unit("d3-satzarten", "Satzarten und Satzzeichen", "❓", "#7a4fd6", [
    lesson("Punkt, Frage- oder Ausrufezeichen?", "❗", sz[:8], mix=True),
    lesson("Noch mehr Satzzeichen", "❓", sz[8:], mix=True),
    lesson("Satzarten sortieren", "🗂️", [sort1, sort2]),
    lesson("Fragewörter", "🔍", wf, mix=True),
    lesson("Wo endet der Satz?", "🛑", sg, mix=True),
    lesson("Komma bei Aufzählungen", "✏️", ko + kz, mix=True),
    lesson("Sätze und Fragen bauen", "🧱", aus + fr, mix=True),
    test(),
])

# ======================================================================
# SUBJEKT, PRÄDIKAT, SATZGLIEDER
# ======================================================================
P = "d3-sg"
# Satzglieder in Kleinschreibung wie mitten im Satz, Index Subjekt, Index Prädikat
SATZ = [(["der kleine Hund", "bellt", "laut"], 0, 1), (["meine Schwester", "liest", "ein Buch"], 0, 1),
        (["im Sommer", "schwimmen", "wir", "im See"], 2, 1), (["der Bäcker", "backt", "frische Brötchen"], 0, 1),
        (["am Morgen", "kräht", "der Hahn"], 2, 1), (["die Kinder", "spielen", "im Garten"], 0, 1),
        (["Opa", "repariert", "das Fahrrad"], 0, 1), (["heute", "schreiben", "wir", "eine Probe"], 2, 1),
        (["der Fuchs", "schleicht", "durch den Wald"], 0, 1), (["nach der Schule", "isst", "Ben", "Nudeln"], 2, 1),
        (["die Sonne", "scheint", "hell"], 0, 1), (["im Herbst", "sammeln", "die Eichhörnchen", "Nüsse"], 2, 1),
        (["mein Freund", "schenkt", "mir", "einen Stift"], 0, 1), (["der Lehrer", "erklärt", "die Aufgabe"], 0, 1),
        (["leise", "schleicht", "die Katze", "zur Tür"], 2, 1), (["die Vögel", "bauen", "ein Nest"], 0, 1)]


def shown(blocks):
    return [cap(b) if i == 0 else b for i, b in enumerate(blocks)]


praed = [ch(P + "-pr", "Tippe das Prädikat an (Was tut jemand?).", sentence(b), shown(b), shown(b)[v],
            f"Das Prädikat ist das Verb: {b[v]}. Im Aussagesatz steht es an zweiter Stelle.", big=False)
         for b, s, v in SATZ]
subj = [ch(P + "-su", "Tippe das Subjekt an (Wer oder was?).", sentence(b), shown(b), shown(b)[s],
           f"Wer oder was {b[v]}? {cap(b[s])}. Das ist das Subjekt.", big=False)
        for b, s, v in SATZ]
umst = [build(P + "-um", "Stell den Satz um! Ein anderes Satzglied soll vorne stehen.", b,
              [o for o in v2_orders(b, v) if o[0] != b[0]], ".", show=sentence(b),
              hint="Nimm ein anderes Satzglied nach vorne. Das Verb bleibt an zweiter Stelle.")
        for b, s, v in SATZ[:10]]
zahl = [ch(P + "-za", "Wie viele Satzglieder hat der Satz? Tipp: Stell ihn in Gedanken um.", sentence(b),
           ["2", "3", "4", "5"], str(len(b)), " | ".join(shown(b)))
        for b, s, v in SATZ[4:14]]

units["k3-satzglieder"] = unit("d3-satzglieder", "Subjekt und Prädikat", "🧩", "#c0498f", [
    lesson("Das Prädikat finden", "🏃", praed[:8], mix=True),
    lesson("Noch mehr Prädikate", "🏃", praed[8:], mix=True),
    lesson("Das Subjekt finden", "🙋", subj[:8], mix=True),
    lesson("Noch mehr Subjekte", "🙋", subj[8:], mix=True),
    lesson("Sätze umstellen", "🔀", umst[:5]),
    lesson("Noch mehr umstellen", "🔀", umst[5:]),
    lesson("Satzglieder zählen", "🔢", zahl, mix=True),
    lesson("Ins Heft", "✍️", [photo("d3-sg-foto",
        "Schreib 4 Sätze über deinen Tag. Unterstreiche in jedem Satz das Prädikat (Verb) und das Subjekt (Wer oder was?).")]),
    test(),
])

# ======================================================================
# WÖRTLICHE REDE
# ======================================================================
P = "d3-wr"
# Begleitsatz vorne: (Begleitsatz ohne Doppelpunkt, Rede mit Satzzeichen)
VORNE = [("Mia ruft", "Ich habe gewonnen!"), ("Papa sagt", "Das Essen ist fertig."), ("Lukas fragt", "Kommst du mit?"),
         ("Die Lehrerin sagt", "Packt eure Hefte aus."), ("Oma fragt", "Wer möchte Kuchen?"), ("Ben flüstert", "Das Baby schläft."),
         ("Der Trainer ruft", "Lauf schneller!"), ("Lea sagt", "Ich mag Pferde.")]
# Begleitsatz hinten: (Rede mit Satzzeichen, Begleitsatz klein)
HINTEN = [("Ich habe Hunger.", "sagt Ben"), ("Wo ist mein Schuh?", "fragt Lea"), ("Hilfe!", "ruft der Junge"),
          ("Morgen regnet es.", "sagt Opa"), ("Hast du Zeit?", "fragt Mama"), ("Vorsicht, heiß!", "ruft der Koch")]


def vorne_ok(b, r):
    return f"{b}: „{r}“"


def hinten_ok(r, b):
    r2 = r[:-1] if r.endswith(".") else r
    return f"„{r2}“, {b}."


wer = []
for b, r in VORNE[:6]:
    wer.append(ch(P + "-wr", "Tippe an, was die Person genau sagt.", vorne_ok(b, r), [b + ":", f"„{r}“"], f"„{r}“",
                  "Was jemand genau sagt, steht in Redezeichen „ … “. Das ist die wörtliche Rede.", big=False))
for r, b in HINTEN[:4]:
    wer.append(ch(P + "-bs", "Tippe den Begleitsatz an. Er sagt, wer spricht.", hinten_ok(r, b),
                  [f"„{r[:-1] if r.endswith('.') else r}“,", b + "."], b + ".",
                  "Der Begleitsatz verrät, wer spricht. Er steht hier hinten.", big=False))

zeichen = []
for b, r in VORNE:
    zeichen.append(ch(P + "-dp", "Welches Zeichen fehlt?", f"{b} _ „{r}“", [":", ",", "."], ":",
                      "Steht der Begleitsatz vorne, kommt danach ein Doppelpunkt."))
ZA = [("Papa sagt", "Das Essen ist fertig."), ("Oma fragt", "Wer möchte Kuchen?"), ("Mia ruft", "Ich habe gewonnen!"),
      ("Lea sagt", "Ich mag Pferde.")]
for i, (b, r) in enumerate(ZA):
    if i % 2 == 0:
        zeichen.append(ch(P + "-an", "Welches Zeichen fehlt?", f"{b}: _{r}“", ["„", "“", ":"], "„",
                          "Am Anfang der wörtlichen Rede stehen die Redezeichen unten: „"))
    else:
        zeichen.append(ch(P + "-ab", "Welches Zeichen fehlt?", f"{b}: „{r}_", ["„", "“", ","], "“",
                          "Am Ende der wörtlichen Rede stehen die Redezeichen oben: “"))

richtig_v = []
for b, r in VORNE:
    ok = vorne_ok(b, r)
    wrong = [f"{b} „{r}“", f"{b}: „{r[:-1]}“{r[-1]}", f"{b}: {r}"]
    k = len(richtig_v) % 3
    opts = [ok, wrong[k], wrong[(k + 1) % 3]]
    richtig_v.append(ch(P + "-rv", "Welcher Satz ist richtig geschrieben?", f"{b} … {r}", opts, ok,
                        f"Richtig: {ok} – Doppelpunkt nach dem Begleitsatz, das Satzzeichen steht innerhalb der Redezeichen.",
                        keep=False, big=False))
richtig_h = []
for r, b in HINTEN:
    ok = hinten_ok(r, b)
    r2 = r[:-1] if r.endswith(".") else r
    if r.endswith("."):
        wrong = [f"„{r}“, {b}.", f"„{r2}“ {b}.", f"{r2}, {b}."]
    else:
        wrong = [f"„{r2}“ {b}.", f"„{r2}“. {cap(b)}.", f"{r2}, {b}."]
    k = len(richtig_h) % 3
    opts = [ok, wrong[k], wrong[(k + 1) % 3]]
    richtig_h.append(ch(P + "-rh", "Welcher Satz ist richtig geschrieben?", f"{r} … {b}", opts, ok,
                        f"Richtig: {ok} – Steht der Begleitsatz hinten, kommt nach den Redezeichen ein Komma. "
                        "Der Punkt der Rede fällt weg, Frage- und Ausrufezeichen bleiben.", keep=False, big=False))

SAG = [("Der Opa ___: „Wo ist meine Brille?“", "fragt", ["fragt", "ruft", "flüstert"]),
       ("Mama ___: „Psst, das Baby schläft.“", "flüstert", ["flüstert", "schreit", "fragt"]),
       ("„Feuer, Feuer!“, ___ der Mann.", "schreit", ["schreit", "flüstert", "fragt"]),
       ("Lisa ___: „Darf ich mitspielen?“", "fragt", ["fragt", "befiehlt", "lacht"]),
       ("Der Polizist ___: „Halt, stehen bleiben!“", "befiehlt", ["befiehlt", "flüstert", "fragt"]),
       ("„Ich verstehe das nicht“, ___ Tim.", "jammert", ["jammert", "jubelt", "befiehlt"]),
       ("„Tor! Wir haben gewonnen!“, ___ die Fans.", "jubeln", ["jubeln", "flüstern", "fragen"]),
       ("Der Lehrer ___: „Das Wort schreibt man mit ie.“", "erklärt", ["erklärt", "schreit", "jubelt"])]
sag = [ch(P + "-sa", "Welches Wort passt besser als „sagt“?", s, o, a, s.replace("___", a), keep=False)
       for s, a, o in SAG]
sag_pairs = pairs(P + "-sp", "Was passt zusammen?", "Wie spricht man, wenn …",
                  [("ganz leise", "flüstern"), ("sehr laut", "schreien"), ("man etwas wissen will", "fragen"),
                   ("man sich sehr freut", "jubeln"), ("man sich beklagt", "jammern")])

units["k3-woertliche-rede"] = unit("d3-woertliche-rede", "Wörtliche Rede", "💬", "#e07a2e", [
    lesson("Wer sagt was?", "🗣️", wer, mix=True),
    lesson("Redezeichen und Doppelpunkt", "✏️", zeichen, mix=True),
    lesson("Begleitsatz vorne", "⬅️", richtig_v, mix=True),
    lesson("Begleitsatz hinten", "➡️", richtig_h, mix=True),
    lesson("Statt „sagt“", "🎭", [sag_pairs] + sag, mix=False),
    lesson("Ins Heft", "✍️", [photo("d3-wr-foto",
        "Schreib ein kleines Gespräch zwischen dir und einem Freund: 4 Sätze mit wörtlicher Rede. Denk an Doppelpunkt und Redezeichen „ “.")]),
    test(),
])

# ======================================================================
# BLITZLESEN
# ======================================================================
P = "d3-bz"
KURZ = [("Haus", ["Maus", "Hals"]), ("Baum", ["Raum", "Bauch"]), ("Hund", ["Mund", "Hand"]), ("Tisch", ["Fisch", "Tasche"]),
        ("Wald", ["Wand", "Welt"]), ("Rose", ["Hose", "Dose"]), ("Nase", ["Hase", "Vase"]), ("Kanne", ["Tanne", "Wanne"]),
        ("Ziege", ["Wiege", "Fliege"]), ("Ball", ["Bild", "Fall"]), ("Stein", ["Stern", "Schein"]), ("Zahn", ["Zahl", "Zaun"])]
LANG = [("Schneemann", ["Schneeball", "Schneeflocke"]), ("Kinderwagen", ["Kindergarten", "Kinderzimmer"]),
        ("Sonnenblume", ["Sonnenbrille", "Sonnenschein"]), ("Regenbogen", ["Regenschirm", "Regentropfen"]),
        ("Feuerwehr", ["Feuerwerk", "Feuerstein"]), ("Briefmarke", ["Briefkasten", "Brieftaube"]),
        ("Bahnhof", ["Bauernhof", "Bahnsteig"]), ("Tierheim", ["Tierarzt", "Tiergarten"]),
        ("Turnschuh", ["Handschuh", "Turnhalle"]), ("Haustür", ["Hausnummer", "Hausaufgabe"])]
FAST = [("Biene", ["Birne", "Bienen"]), ("Stuhl", ["Stahl", "Stall"]), ("Wiese", ["Riese", "Wiesel"]),
        ("Leiter", ["Liter", "Leute"]), ("Nebel", ["Nabel", "Nadel"]), ("Feder", ["Fieber", "Felder"]),
        ("Bruder", ["Ruder", "Butter"]), ("Mantel", ["Mandel", "Marder"]), ("Kiste", ["Küste", "Kasse"]),
        ("Mond", ["Mund", "Mode"]), ("Ofen", ["offen", "Ufer"]), ("Schaf", ["Schal", "Schiff"])]
GRUPPE = [("der rote Ball", ["der rote Bus", "die rote Bank"]), ("ein kleiner Hund", ["ein kleiner Mund", "ein kluger Hund"]),
          ("im grünen Wald", ["im grünen Feld", "am grünen Wald"]), ("drei bunte Vögel", ["drei bunte Kugeln", "zwei bunte Vögel"]),
          ("auf dem Tisch", ["unter dem Tisch", "auf dem Teich"]), ("mit dem Fahrrad", ["mit dem Fußball", "auf dem Fahrrad"]),
          ("eine warme Jacke", ["eine warme Decke", "keine warme Jacke"]), ("hinter dem Haus", ["hinter der Maus", "neben dem Haus"])]
SATZ_B = [("Der Hund schläft im Korb.", ["Der Hund spielt im Korb.", "Der Hund schläft im Dorf."]),
          ("Lisa trinkt warmen Tee.", ["Lisa trinkt warme Milch.", "Lisa kocht warmen Tee."]),
          ("Wir fahren ans Meer.", ["Wir fahren aufs Meer.", "Wir laufen ans Meer."]),
          ("Die Katze fängt eine Maus.", ["Die Katze sieht eine Maus.", "Die Katze fängt eine Laus."]),
          ("Im Winter schneit es oft.", ["Im Winter regnet es oft.", "Im Sommer schneit es oft."]),
          ("Opa liest die Zeitung.", ["Oma liest die Zeitung.", "Opa liest die Zeitschrift."]),
          ("Der Zug kommt zu spät.", ["Der Zug kommt zu früh.", "Der Bus kommt zu spät."]),
          ("Mein Bruder baut eine Burg.", ["Mein Bruder malt eine Burg.", "Mein Vater baut eine Burg."])]
kurz = [flash(P + "-k", w, o, 900) for w, o in KURZ]
lang = [flash(P + "-l", w, o, 1100) for w, o in LANG]
fast = [flash(P + "-f", w, o, 700) for w, o in FAST]
grp = [flash(P + "-g", w, o, 1300) for w, o in GRUPPE]
satz = [flash(P + "-s", w, o, 1800) for w, o in SATZ_B]

units["k3-blitzlesen"] = unit("d3-blitzlesen", "Blitzlesen", "⚡", "#d9a400", [
    lesson("Kurze Wörter", "⚡", kurz, mix=True),
    lesson("Lange Wörter", "🚀", lang, mix=True),
    lesson("Fast gleich!", "👀", fast, mix=True),
    lesson("Wortgruppen", "🧺", grp, mix=True),
    lesson("Kurze Sätze", "📜", satz, mix=True),
    test(),
])

os.makedirs(OUT, exist_ok=True)
for name, u in units.items():
    with open(os.path.join(OUT, name + ".json"), "w", encoding="utf-8") as f:
        json.dump(u, f, ensure_ascii=False, indent=1)
        f.write("\n")
    n = sum(len(l.get("tasks", [])) for l in u["lessons"])
    print(name, len(u["lessons"]), "Lektionen,", n, "Aufgaben")
