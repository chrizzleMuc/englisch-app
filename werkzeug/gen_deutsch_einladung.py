# Erzeugt Deutsch 3. Klasse: inhalte/deutsch/k3-einladung.json (Eine Einladung schreiben)
# Aufbau nach Nathans Schulheft (7 Bausteine, Satzanfänge-Liste), Beispieltexte selbst geschrieben.
# Schwerpunkte: Satzanfänge sicher merken; bei Wann/Wo immer Datum UND Uhrzeit UND Ort.
# JSON nicht von Hand ändern, sondern hier und neu erzeugen: python3 werkzeug/gen_deutsch_einladung.py
import json, re, sys, unicodedata

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


def ch(p, task, prompt, options, answer, explain=None, keep=True, big=False, letter=False):
    assert answer in options, (prompt, answer, options)
    t = {"kind": "choice", "id": uid(f"{p}-{slug(prompt)}"), "task": task, "prompt": prompt,
         "options": options, "answer": answer}
    if keep: t["keepOrder"] = True
    if big: t["bigOptions"] = True
    if letter: t["letter"] = True
    if explain: t["explain"] = explain
    return t


def ty(p, task, prompt, answer, also=None, explain=None):
    t = {"kind": "type", "id": uid(f"{p}-{slug(prompt)}"), "task": task, "prompt": prompt, "answer": answer}
    if also: t["also"] = also
    if explain: t["explain"] = explain
    return t


def sort(p, task, review, groups, items):
    return {"kind": "sort", "task": task, "review": review, "groups": groups,
            "items": [{"id": uid(f"{p}-{slug(t)}"), "text": t, "group": g} for t, g in items]}


def pairs(p, task, review, prs):
    return {"kind": "pairs", "task": task, "review": review,
            "pairs": [{"id": uid(f"{p}-{slug(a)}"), "a": a, "b": b} for a, b in prs]}


def order(p, task, tiles):
    return {"kind": "order", "id": uid(f"{p}-{slug(task + tiles[0])}"), "task": task, "tiles": tiles}


def mark(p, task, text, colors, explain=None):
    t = {"kind": "mark", "id": uid(f"{p}-{slug(text)}"), "task": task, "text": text, "colors": colors}
    if explain: t["explain"] = explain
    return t


def lesson(title, icon, tasks=None, mix=False, **kw):
    l = {"title": title, "icon": icon}
    if mix: l["mix"] = True
    if tasks is not None: l["tasks"] = tasks
    l.update(kw)
    return l


# ----------------------------------------------------------------------
BAUSTEINE = ["Ort und Datum", "Anrede", "Anlass (Was?)", "Wann? Wo?", "Wichtige Infos", "Schlusssatz", "Gruß und Unterschrift"]

# ---------- 1. Bausteine ----------
P = "d3-ei-bs"
bs = [order(P, "Bring die Bausteine einer Einladung in die richtige Reihenfolge!", BAUSTEINE),
      order(P, "Bring die Teile dieser Einladung in die richtige Reihenfolge!", [
          "Augsburg, 3.5.27", "Liebe Emma,", "ich lade dich herzlich zu meiner Pyjama-Party ein.",
          "Wir treffen uns am Freitag, den 14. Mai, um 18 Uhr bei mir zu Hause.",
          "Bring bitte deinen Schlafsack mit!", "Ich freue mich schon riesig auf dich!", "Viele Grüße\nDeine Hanna"]),
      order(P, "Bring die Teile dieser Einladung in die richtige Reihenfolge!", [
          "Nürnberg, 20.6.27", "Lieber Max,", "bald ist es so weit, ich werde 10 Jahre alt!",
          "Die Feier findet am Samstag, den 3. Juli, um 14 Uhr im Kletterwald statt.",
          "Zieh bitte Turnschuhe an!", "Sag mir bitte Bescheid, ob du kommen kannst.", "Liebe Grüße\nDein Felix"])]
WELCH = [("München, 12.3.27", "Ort und Datum"), ("Lieber Jonas,", "Anrede"), ("Liebe Oma,", "Anrede"),
         ("ich lade dich zu meiner Geburtstagsfeier ein.", "Anlass (Was?)"),
         ("hiermit lade ich dich zu unserem Sommerfest ein.", "Anlass (Was?)"),
         ("Wir treffen uns am Sonntag, den 4. April, um 10 Uhr am Spielplatz.", "Wann? Wo?"),
         ("Die Feier beginnt am Freitag, den 9. Mai, um 15 Uhr im Garten.", "Wann? Wo?"),
         ("Bring bitte eine Taschenlampe mit!", "Wichtige Infos"),
         ("Wir werden zusammen Pizza backen.", "Wichtige Infos"),
         ("Ich freue mich schon auf dich!", "Schlusssatz"),
         ("Das wird ein großer Spaß!", "Schlusssatz"),
         ("Liebe Grüße\nDein Paul", "Gruß und Unterschrift"),
         ("Bamberg, 7.9.27", "Ort und Datum"), ("Liebe Kinder,", "Anrede"),
         ("bald ist es so weit, ich werde 10 Jahre alt!", "Anlass (Was?)"),
         ("Die Party findet am Freitag, den 2. Juli, um 16 Uhr im Kletterwald statt.", "Wann? Wo?"),
         ("Zieh bitte alte Kleidung an!", "Wichtige Infos"),
         ("Sag mir bitte Bescheid, ob du kommen kannst.", "Schlusssatz"),
         ("Viele Grüße\nEure Klasse 3c", "Gruß und Unterschrift")]
welch = [ch(P + "-w", "Welcher Baustein ist das?", s, BAUSTEINE, a) for s, a in WELCH]

# ---------- 2. Anrede ----------
P = "d3-ei-an"
AN = [ch(P, "Welche Anrede ist richtig?", "Du schreibst an Tim.", ["Lieber Tim,", "Lieber Tim", "Liebe Tim,"], "Lieber Tim,",
         "Bei Jungen und Männern: Lieber. Nach der Anrede kommt ein Komma."),
      ch(P, "Welche Anrede ist richtig?", "Du schreibst an Lea.", ["Liebe Lea", "Liebe Lea,", "Lieber Lea,"], "Liebe Lea,",
         "Bei Mädchen und Frauen: Liebe. Nach der Anrede kommt ein Komma."),
      ch(P, "Welche Anrede ist richtig?", "Du schreibst an deinen Opa.", ["Lieber Opa,", "Liebe Opa,", "Lieber Opa."], "Lieber Opa,",
         "Nach der Anrede kommt ein Komma, kein Punkt."),
      ch(P, "Welche Anrede ist richtig?", "Du schreibst an deine ganze Klasse.", ["Liebe Kinder,", "Lieber Kinder,", "Liebe Kinder!"], "Liebe Kinder,",
         "Bei mehreren Personen: Liebe. Nach der Anrede kommt ein Komma."),
      ch(P, "Wie geht es nach der Anrede weiter?", "Lieber Tim,\n_____ bist herzlich zu meiner Feier eingeladen.", ["du", "Du"], "du",
         "Nach dem Komma geht es klein weiter."),
      ch(P, "Wie geht es nach der Anrede weiter?", "Liebe Sara,\n_____ lade dich herzlich zu meinem Fest ein.", ["ich", "Ich"], "ich",
         "Nach dem Komma geht es klein weiter."),
      ch(P, "Wie geht es nach der Anrede weiter?", "Liebe Kinder,\n_____ laden euch zum Vorlesenachmittag ein.", ["wir", "Wir"], "wir",
         "Nach dem Komma geht es klein weiter."),
      ch(P, "Wie geht es nach der Anrede weiter?", "Lieber Ben,\n_____ ist es so weit, ich werde 9!", ["bald", "Bald"], "bald",
         "Nach dem Komma geht es klein weiter."),
      ch(P, "Was ist hier falsch?", "Lieber Paul\ndu bist herzlich eingeladen.", ["Das Komma fehlt.", "du muss groß sein.", "Alles richtig."], "Das Komma fehlt.",
         "Richtig: Lieber Paul, – nach der Anrede kommt ein Komma."),
      ch(P, "Was ist hier falsch?", "Liebe Mia,\nIch lade dich zu meiner Party ein.", ["Das Komma fehlt.", "Ich muss klein sein.", "Alles richtig."], "Ich muss klein sein.",
         "Nach dem Komma geht es klein weiter: ich lade dich …"),
      ch(P, "Was ist hier falsch?", "Lieber Noah,\nwir treffen uns im Park.", ["Das Komma fehlt.", "wir muss groß sein.", "Alles richtig."], "Alles richtig.",
         "Komma nach der Anrede und klein weiter. Super!"),
      ty(P, "Schreib die Anrede richtig ab (mit Komma)!", "Liebe Oma", "Liebe Oma,", explain="Nach der Anrede kommt ein Komma."),
      ty(P, "Schreib die Anrede richtig ab (mit Komma)!", "Lieber Luca", "Lieber Luca,", explain="Nach der Anrede kommt ein Komma.")]

# ---------- 3./4./5. Satzanfänge ----------
GR = ["Anfang", "Ort und Zeit", "Programm", "Schluss"]
SA = {
    "Anfang": ["Ich lade dich …", "Bald ist es so weit, …", "Hiermit lade ich dich …", "Ich möchte dich …", "Ich plane …", "Endlich ist es wieder so weit, …"],
    "Ort und Zeit": ["Die Feier findet … statt.", "Wir treffen uns …", "Komm bitte …", "Um … geht es los.", "Ab … Uhr erwarte ich dich.", "Bitte komm pünktlich …"],
    "Programm": ["Wir werden …", "Es gibt …", "Ich habe … vorbereitet.", "Wir spielen …", "Bring bitte … mit.", "Danach …", "Zusammen werden wir …", "Es wartet … auf dich."],
    "Schluss": ["Ich freue mich!", "Sag mir bitte Bescheid, …", "Ich hoffe, …", "Das wird ein großer Spaß!", "Schön, wenn du …", "Ich kann es kaum erwarten, dass …"],
}
P = "d3-ei-so"
def pick(idx):
    return [(SA[g][i], g) for g in GR for i in idx if i < len(SA[g])]
sorts = [sort(P, "Wohin gehört der Satzanfang?", "Satzanfänge für eine Einladung", GR, pick(r)) for r in ([0, 1], [2, 3], [4, 5])]
sorts.append(sort(P, "Wohin gehört der Satzanfang?", "Satzanfänge für eine Einladung", GR,
                  [(SA["Programm"][6], "Programm"), (SA["Programm"][7], "Programm"), (SA["Anfang"][0], "Anfang"), (SA["Schluss"][0], "Schluss"),
                   (SA["Ort und Zeit"][1], "Ort und Zeit"), (SA["Schluss"][1], "Schluss")]))
P = "d3-ei-wo"
wohin = []
for g in GR:
    for s in SA[g]:
        wohin.append(ch(P, "Wohin gehört dieser Satzanfang?", s, GR, g))

P = "d3-ei-lk"
# Lückentexte: richtigen Satzanfang wählen
LK = [("_____ dich herzlich zu meiner Geburtstagsfeier ein.", "Ich lade", ["Ich lade", "Wir treffen", "Ich freue"]),
      ("_____ so weit, ich werde 10 Jahre alt!", "Bald ist es", ["Bald ist es", "Danach ist es", "Es gibt"]),
      ("_____ ich dich zu unserem Klassenfest ein.", "Hiermit lade", ["Hiermit lade", "Ich hoffe", "Komm bitte"]),
      ("_____ wieder so weit: Unser Sommerfest steht vor der Tür!", "Endlich ist es", ["Endlich ist es", "Zusammen ist es", "Es wartet"]),
      ("_____ am Samstag, den 5. Juni, um 15 Uhr im Garten statt.", "Die Feier findet", ["Die Feier findet", "Ich plane", "Ich hoffe"]),
      ("_____ am Freitag um 16 Uhr vor dem Kino.", "Wir treffen uns", ["Wir treffen uns", "Wir spielen", "Ich freue mich"]),
      ("Um 14 Uhr _____", "geht es los.", ["geht es los.", "gibt es Kuchen.", "freue ich mich."]),
      ("_____ 15 Uhr erwarte ich dich.", "Ab", ["Ab", "Bis", "Danach"]),
      ("_____, sonst verpasst du den Anfang!", "Bitte komm pünktlich", ["Bitte komm pünktlich", "Ich hoffe", "Es gibt"]),
      ("_____ eine Schatzsuche im Wald machen.", "Wir werden", ["Wir werden", "Ich lade", "Sag mir"]),
      ("_____ Pizza und Schokokuchen.", "Es gibt", ["Es gibt", "Wir treffen", "Ich möchte"]),
      ("Ich habe ein tolles Spiel _____", "vorbereitet.", ["vorbereitet.", "erwartet.", "gefreut."]),
      ("_____ deine Badesachen mit.", "Bring bitte", ["Bring bitte", "Komm bitte", "Ich hoffe"]),
      ("_____ gibt es noch eine Überraschung.", "Danach", ["Danach", "Hiermit", "Bald"]),
      ("Eine große Torte _____", "wartet auf dich.", ["wartet auf dich.", "findet statt.", "geht es los."]),
      ("_____ schon riesig auf dich!", "Ich freue mich", ["Ich freue mich", "Wir treffen uns", "Es gibt"]),
      ("_____, ob du kommen kannst.", "Sag mir bitte Bescheid", ["Sag mir bitte Bescheid", "Bring bitte", "Bitte komm pünktlich"]),
      ("_____, du hast Zeit.", "Ich hoffe", ["Ich hoffe", "Ich plane", "Es gibt"]),
      ("_____ kommen kannst!", "Schön, wenn du", ["Schön, wenn du", "Wir werden", "Ich lade"]),
      ("_____, dass wir zusammen feiern!", "Ich kann es kaum erwarten", ["Ich kann es kaum erwarten", "Ich habe vorbereitet", "Komm bitte"])]
luecke = [ch(P, "Welcher Satzanfang passt?", s, o, a, s.replace("_____", a), keep=False) for s, a, o in LK]

P = "d3-ei-pa"
paare = [pairs(P, "Was gehört zusammen?", "Satzanfang und Ende", [
             ("Ich lade dich", "herzlich zu meinem Fest ein."), ("Wir treffen uns", "um 15 Uhr im Park."),
             ("Bring bitte", "deine Badehose mit."), ("Sag mir bitte Bescheid,", "ob du kommen kannst.")]),
         pairs(P, "Was gehört zusammen?", "Satzanfang und Ende", [
             ("Bald ist es so weit,", "ich werde 9 Jahre alt!"), ("Die Feier findet", "im Garten statt."),
             ("Ich habe eine Schatzsuche", "vorbereitet."), ("Ich kann es kaum erwarten,", "dass du kommst!")]),
         pairs(P, "Was gehört zusammen?", "Satzanfang und Ende", [
             ("Ab 16 Uhr", "erwarte ich dich."), ("Es wartet", "eine Überraschung auf dich."),
             ("Schön, wenn du", "Zeit hast!"), ("Um 14 Uhr", "geht es los.")])]

P = "d3-ei-sw"
SW = [("Ich _____ dich herzlich zu meiner Party ein.", "lade"), ("Bald ist es so _____, ich werde 10!", "weit"),
      ("_____ lade ich dich zu meinem Fest ein.", "Hiermit"), ("Wir _____ uns am Samstag um 15 Uhr.", "treffen"),
      ("Die Feier _____ im Schwimmbad statt.", "findet"), ("Um 14 Uhr geht es _____.", "los"),
      ("Bitte komm _____!", "pünktlich"), ("Ich habe eine Schatzsuche _____.", "vorbereitet"),
      ("Bring bitte deinen Schlafsack _____.", "mit"), ("Sag mir bitte _____, ob du kommen kannst.", "Bescheid"),
      ("Ich kann es kaum _____, dass du kommst!", "erwarten"), ("Das wird ein großer _____!", "Spaß"),
      ("Ich _____ mich schon auf dich!", "freue"), ("Es _____ eine Überraschung auf dich.", "wartet")]
selbst = [ty(P, "Welches Wort fehlt? Schreib es auf!", s, a, also=(["soweit"] if a == "weit" else None),
             explain=s.replace("_____", a)) for s, a in SW]

# ---------- 6. Wann? Wo? ----------
P = "d3-ei-ww"
FARBEN = [{"key": "Datum", "label": "Datum", "color": "#7a4fd6"},
          {"key": "Uhrzeit", "label": "Uhrzeit", "color": "#e07a2e"},
          {"key": "Ort", "label": "Ort", "color": "#0f9d76"}]
MK = ["Wir treffen uns [am Samstag, den 12. Dezember,|Datum] [um 15 Uhr|Uhrzeit] [im Schwimmbad|Ort].",
      "Die Feier findet [am Freitag, den 7. Mai,|Datum] [um 16 Uhr|Uhrzeit] [im Garten|Ort] statt.",
      "Komm bitte [am Sonntag, den 2. März,|Datum] [um 10 Uhr|Uhrzeit] [zum Spielplatz|Ort].",
      "[Am Mittwoch, den 9. Juni,|Datum] geht es [um 14 Uhr|Uhrzeit] [vor der Schule|Ort] los.",
      "Ich erwarte dich [am Samstag, den 20. April,|Datum] [ab 15 Uhr|Uhrzeit] [bei mir zu Hause|Ort].",
      "Wir feiern [am Freitag, den 5. März,|Datum] [um 14 Uhr|Uhrzeit] [im Klassenzimmer der 3c|Ort]."]
marks = [mark(P + "-mk", "Male an: Datum lila, Uhrzeit orange, Ort grün!", t, FARBEN,
              "Bei Wann? und Wo? brauchst du immer alle drei: Datum, Uhrzeit und Ort.") for t in MK]
OPT = ["Datum", "Uhrzeit", "Ort", "Nichts fehlt"]
WF = [("Wir treffen uns am Samstag, den 12. Mai, im Park.", "Uhrzeit"),
      ("Die Feier beginnt um 15 Uhr im Garten.", "Datum"),
      ("Wir treffen uns am Freitag, den 3. Juli, um 14 Uhr.", "Ort"),
      ("Komm bitte am Sonntag, den 8. März, zum Kino.", "Uhrzeit"),
      ("Die Party findet am Samstag, den 6. Juni, um 16 Uhr im Schwimmbad statt.", "Nichts fehlt"),
      ("Am Mittwoch, den 4. Mai, geht es vor der Schule los.", "Uhrzeit"),
      ("Wir feiern um 18 Uhr bei mir zu Hause.", "Datum"),
      ("Ab 15 Uhr erwarte ich dich am Samstag, den 9. April, im Kletterwald.", "Nichts fehlt"),
      ("Die Feier findet am Freitag, den 20. Mai, in der Turnhalle statt.", "Uhrzeit"),
      ("Wir treffen uns am Sonntag, den 1. Juni, um 11 Uhr.", "Ort"),
      ("Komm bitte am Samstag, den 14. März, in den Zoo.", "Uhrzeit"),
      ("Um 10 Uhr geht es am Spielplatz los.", "Datum")]
EXPL = {"Uhrzeit": "Hier fehlt die Uhrzeit! Sonst weiß dein Gast nicht, wann er kommen soll. Zum Beispiel: um 15 Uhr.",
        "Datum": "Hier fehlt das Datum! Sonst weiß dein Gast nicht, an welchem Tag. Zum Beispiel: am Samstag, den 12. Mai.",
        "Ort": "Hier fehlt der Ort! Sonst weiß dein Gast nicht, wohin er kommen soll. Zum Beispiel: im Park.",
        "Nichts fehlt": "Super! Datum, Uhrzeit und Ort sind alle da."}
wasfehlt = [ch(P + "-wf", "Was fehlt bei Wann? Wo?", s, OPT, a, EXPL[a], big=True) for s, a in WF]
drei = [ch(P + "-3", "Was gehört zu Wann? Wo? in jede Einladung?", "Wann? Wo?",
           ["Datum, Uhrzeit und Ort", "nur das Datum", "Datum und Ort"], "Datum, Uhrzeit und Ort",
           "Immer alle drei: Datum + Uhrzeit + Ort!"),
        ch(P + "-3", "Welcher Satz ist vollständig?", "Wann? Wo?",
           ["Wir treffen uns am Samstag, den 5. Mai, um 15 Uhr im Park.", "Wir treffen uns am Samstag, den 5. Mai, im Park.",
            "Wir treffen uns um 15 Uhr im Park."], "Wir treffen uns am Samstag, den 5. Mai, um 15 Uhr im Park.",
           "Nur dieser Satz hat Datum, Uhrzeit und Ort.", keep=False),
        ch(P + "-3", "Welcher Satz ist vollständig?", "Wo? Wann?",
           ["Die Feier findet um 16 Uhr im Garten statt.", "Die Feier findet am Freitag, den 2. Juli, um 16 Uhr im Garten statt.",
            "Die Feier findet am Freitag, den 2. Juli, statt."], "Die Feier findet am Freitag, den 2. Juli, um 16 Uhr im Garten statt.",
           "Nur dieser Satz hat Datum, Uhrzeit und Ort.", keep=False),
        ch(P + "-3", "Welches ist eine Uhrzeit?", "Wann genau?", ["um 15 Uhr", "am Samstag", "im Garten"], "um 15 Uhr", keep=False),
        ch(P + "-3", "Welches ist ein Ort?", "Wo genau?", ["um 15 Uhr", "am Samstag", "im Schwimmbad"], "im Schwimmbad", keep=False),
        ch(P + "-3", "Welches ist ein Datum?", "Welcher Tag?", ["um 10 Uhr", "am Sonntag, den 4. Mai", "im Kino"], "am Sonntag, den 4. Mai", keep=False)]
P = "d3-ei-er"
ERG = [("Wir treffen uns am Samstag, den 12. Mai, _____ im Park.", ["um 15 Uhr", "am Abend", "in der Halle"], "um 15 Uhr"),
       ("Die Feier findet _____ um 14 Uhr im Garten statt.", ["am Freitag, den 9. Juli,", "um 17 Uhr", "im Haus"], "am Freitag, den 9. Juli,"),
       ("Komm bitte am Sonntag, den 3. März, um 11 Uhr _____", ["zum Spielplatz.", "um 12 Uhr.", "am Montag."], "zum Spielplatz."),
       ("Wir feiern am Samstag, den 5. Juni, _____ im Kletterwald.", ["um 13 Uhr", "am Sonntag", "im Wald"], "um 13 Uhr")]
ergaenzen = [ch(P, "Ergänze, was fehlt!", s, o, a, s.replace("_____", a).replace(",,", ","), keep=False) for s, o, a in ERG]

# ---------- 7. Fehler finden: ganze Einladung ----------
P = "d3-ei-ff"
def brief(teile):
    return "\n".join(teile)
ORT = "Regensburg, 2.5.27"; ANR = "Liebe Lina,"; AL = "ich lade dich herzlich zu meinem Geburtstag ein."
WW = "Wir treffen uns am Samstag, den 15. Mai, um 15 Uhr im Garten."
INF = "Bring bitte Gummistiefel mit!"; SCH = "Ich freue mich schon auf dich!"; GR_ = "Liebe Grüße\nDeine Sophie"
FF = [([ANR, AL, WW, INF, SCH, GR_], "Ort und Datum"),
      ([ORT, ANR, WW, INF, SCH, GR_], "Anlass (Was?)"),
      ([ORT, ANR, AL, WW, INF, SCH], "Gruß und Unterschrift"),
      ([ORT, ANR, AL, "Wir treffen uns am Samstag, den 15. Mai, im Garten.", INF, SCH, GR_], "Uhrzeit"),
      ([ORT, ANR, AL, "Wir treffen uns um 15 Uhr im Garten.", INF, SCH, GR_], "Datum"),
      ([ORT, ANR, AL, "Wir treffen uns am Samstag, den 15. Mai, um 15 Uhr.", INF, SCH, GR_], "Ort"),
      ([ORT, "Liebe Lina", AL, WW, INF, SCH, GR_], "Komma nach der Anrede"),
      ([ORT, ANR, AL, WW, INF, GR_], "Schlusssatz")]
FOPT = ["Ort und Datum", "Anlass (Was?)", "Datum", "Uhrzeit", "Ort", "Komma nach der Anrede", "Schlusssatz", "Gruß und Unterschrift"]
fehler = []
for teile, a in FF:
    opts = [a] + [o for o in FOPT if o != a]
    # 4 Antworten: richtige + 3 andere, Uhrzeit ist besonders wichtig und oft dabei
    others = [o for o in ["Uhrzeit", "Ort und Datum", "Schlusssatz", "Anlass (Was?)", "Ort", "Datum"] if o != a][:3]
    fehler.append(ch(P, "Fehler finden: Was fehlt in dieser Einladung?", brief(teile), [a] + others, a,
                     "Eine Einladung braucht alle Bausteine. Bei Wann? Wo? immer Datum, Uhrzeit und Ort!", keep=False, letter=True))

# ---------- 8. Auf Papier ----------
papier = [{"kind": "photo", "id": uid("d3-ei-papier-1"),
           "task": "Schreib eine Einladung zu deinem Geburtstag auf ein Blatt. Denk an alle Bausteine! Hak sie danach ab.",
           "show": ["Ort, Datum", "Anrede mit Komma", "Anlass", "Datum + Uhrzeit + Ort", "Wichtige Infos", "Schlusssatz", "Gruß + Name"]},
          {"kind": "photo", "id": uid("d3-ei-papier-2"),
           "task": "Lade deine Klasse zu einem Spielenachmittag ein. Nimm Satzanfänge aus der Liste! Vergiss die Uhrzeit nicht.",
           "show": ["Ich lade euch …", "Wir treffen uns …", "Wir spielen …", "Bringt bitte … mit.", "Ich freue mich …"]}]

unit = {"id": "d3-einladung", "type": "schule", "title_de": "Eine Einladung schreiben", "image": "💌", "color": "#d6457a",
        "lessons": [
            lesson("Die 7 Bausteine", "🧱", bs + welch[:7]),
            lesson("Welcher Baustein ist das?", "🔎", welch[7:], mix=True),
            lesson("Anrede mit Komma", "✉️", AN, mix=True),
            lesson("Satzanfänge sortieren", "🗂️", sorts),
            lesson("Wohin gehört der Satzanfang?", "🎯", wohin, mix=True),
            lesson("Satzanfänge im Lückentext", "🧩", luecke, mix=True),
            lesson("Satzanfänge zusammensetzen", "🔗", paare),
            lesson("Satzanfänge selbst schreiben", "✏️", selbst, mix=True),
            lesson("Wann? Wo? Datum + Uhrzeit + Ort", "⏰", drei + marks, mix=True),
            lesson("Was fehlt? Uhrzeit-Detektiv", "🕵️", wasfehlt + ergaenzen, mix=True),
            lesson("Fehler finden in der Einladung", "🔍", fehler, mix=True),
            lesson("Einladung auf Papier", "📷", papier),
            lesson("Probe-Test", "🏆", test=True, count=20),
        ]}
json.dump(unit, open(f"{OUT}/k3-einladung.json", "w"), ensure_ascii=False, indent=1)
print("ok", sum(len(l.get("tasks", [])) for l in unit["lessons"]), "Aufgaben")
