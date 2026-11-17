# Erzeugt inhalte/regeln.json (Regelkarten) und die Einheiten mit Regel-Quiz und Wortarten.
# Aufruf aus dem Repo-Ordner: python3 werkzeug/gen_regeln.py
# Regeltexte: **so** wird in der App gelb markiert.
# "lektionen": "<Einheit-id>/<Lektionstitel>" (Regelkarte vor dieser Lektion) oder nur "<Einheit-id>".
import json, re

R = []
def regel(id_, icon, title, kurz, merke, beispiele=(), trick="", lektionen=(), say=""):
    r = {"id": id_, "icon": icon, "title": title, "kurz": kurz, "merke": list(merke), "beispiele": list(beispiele), "lektionen": list(lektionen)}
    if trick: r["trick"] = trick
    if say: r["say"] = say
    R.append(r)

# ---------------- Deutsch 3. Klasse: Wortarten ----------------
regel("wortarten", "🔤", "Nomen, Verb oder Adjektiv?", "Wortarten erkennen", [
    "**Nomen** sind Namen für Menschen, Tiere, Dinge und Gefühle. Man schreibt sie **groß**.",
    "**Verben** sagen, was jemand **tut** oder was **passiert**. Man schreibt sie klein.",
    "**Adjektive** sagen, **wie** etwas ist. Man schreibt sie klein.",
], ["der **Hund** – er **rennt** – er ist **schnell**"],
    "Passt **der, die** oder **das** davor? → Nomen. Passt **ich** davor? → Verb. Passt **„Wie ist …?“**? → Adjektiv.",
    ["d3-wortarten/Nomen, Verb oder Adjektiv?", "d3-wortarten/Alle drei Wortarten"])
regel("nomen-gross", "🅰️", "Nomen schreibt man groß", "Nomen groß", [
    "Nomen sind Namen für **Menschen, Tiere, Pflanzen und Dinge**: Mama, Katze, Baum, Ball.",
    "Auch Dinge, die man **nicht anfassen** kann, sind Nomen: die **Freude**, der **Mut**, die **Angst**.",
    "Nomen schreibt man immer **groß**.",
], ["**der** Hund, **die** Wut, **das** Glück"],
    "Artikelprobe: Passt **der, die** oder **das** davor, ist es ein Nomen.",
    ["d3-nomen/Konkret oder abstrakt", "d3-nomen/Groß oder klein", "d3-wortarten/Nomen blau anmalen"])
regel("nomen-endungen", "🧩", "-ung, -heit, -keit, -nis machen Nomen", "Nomen-Endungen", [
    "Wörter mit den Endungen **-ung, -heit, -keit** und **-nis** sind immer **Nomen**.",
    "Deshalb schreibt man sie **groß**.",
    "**-nis** wird in der Mehrzahl zu **-nisse**.",
], ["wohnen → die Woh**nung**", "frei → die Frei**heit**", "ehrlich → die Ehrlich**keit**", "das Erleb**nis** → die Erleb**nisse**"],
    "", ["d3-nomen/-heit und -keit", "d3-nomen/-ung", "d3-nomen-endungen"])
regel("nomen-zusammen", "🔗", "Zusammengesetzte Nomen", "Nomen zusammensetzen", [
    "Aus zwei Wörtern kann ein **neues Nomen** werden.",
    "Das **letzte Wort** bestimmt den **Artikel**.",
    "Das neue Wort schreibt man **groß** und **zusammen**.",
], ["das Haus + **die Tür** → **die** Haustür", "die Schule + **der Hof** → **der** Schulhof"],
    "", ["d3-nomen/Zusammensetzen"])
regel("mehrzahl", "👥", "Einzahl und Mehrzahl", "Mehrzahl", [
    "Nomen gibt es in der **Einzahl** (eins) und in der **Mehrzahl** (viele).",
    "In der Mehrzahl heißt der Artikel immer **die**.",
    "Oft wird aus a, o, u ein **ä, ö, ü**.",
], ["der Baum → die B**ä**ume", "das Buch → die B**ü**cher"],
    "", ["d3-nomen/Mehrzahl 1", "d3-nomen/Mehrzahl 2"])
regel("verben", "🏃", "Verben sagen, was jemand tut", "Verben", [
    "**Verben** sagen, was jemand **tut** oder was **passiert**: rennen, lachen, regnen.",
    "Man schreibt sie **klein**.",
    "Die **Grundform** endet auf **-en** oder **-n**: spielen, wandern.",
    "Das Verb **verändert sich**, je nachdem wer etwas tut: ich spiel**e**, du spiel**st**, er spiel**t**.",
], ["ich **lache**, du **lachst**, sie **lacht**"],
    "ich-Probe: Passt **ich** davor, ist es ein Verb.",
    ["d3-verben/Gegenwart: schwache Verben", "d3-verben/Gegenwart: starke Verben", "d3-wortarten/Verben grün anmalen"])
regel("vergangenheit", "⏪", "Verben in der Vergangenheit", "Vergangenheit", [
    "Viele Verben bekommen in der Vergangenheit ein **-te**: ich spiel**te**.",
    "Starke Verben **ändern ihren Selbstlaut**: ich s**i**nge → ich s**a**ng.",
    "Starke Verben muss man sich **merken**.",
], ["ich lache → ich lach**te**", "ich gehe → ich **ging**", "ich laufe → ich **lief**"],
    "", ["d3-verben/Vergangenheit mit -te", "d3-verben/Schwach oder stark?", "d3-unregelmaessige-verben/Paare 1", "d3-unregelmaessige-verben/Paare 2"])
regel("hat-ist", "🚶", "hat oder ist?", "hat oder ist", [
    "Wenn man **sich bewegt** oder etwas **sich verändert**, nimmt man meistens **ist**.",
    "Sonst nimmt man **hat**.",
], ["ich **bin** gelaufen, sie **ist** eingeschlafen", "ich **habe** gemalt, er **hat** gelesen"],
    "", ["d3-unregelmaessige-verben/hat oder ist? 1", "d3-unregelmaessige-verben/hat oder ist? 2"])
regel("adjektive", "🎨", "Adjektive schreibt man klein", "Adjektive klein", [
    "**Adjektive** sagen, **wie** etwas ist: groß, rot, lustig, schnell.",
    "Man schreibt sie **klein**.",
    "**Aber:** Am **Satzanfang** schreibt man jedes Wort groß.",
], ["der **kleine** Hund", "Die Suppe ist **heiß**.", "**Heiß** ist die Suppe."],
    "Frag **„Wie ist …?“** – Wie ist der Hund? **klein**",
    ["d3-adjektive/Adjektive erkennen", "d3-adjektive/Gegensatzpaare", "d3-adjektive/Adjektive anpassen", "d3-wortarten/Adjektive rot anmalen"])
regel("adjektiv-endungen", "🔚", "Adjektive mit -ig und -lich", "-ig und -lich", [
    "Viele Adjektive enden auf **-ig** oder **-lich**.",
    "Am Wortende hört man -ig nicht genau. **Verlängere**: lustig → lusti**g**er. Dann hörst du das **g**.",
], ["lust**ig**, wind**ig**", "freund**lich**, gefähr**lich**"],
    "", ["d3-adjektive/-ig und -lich"])
regel("adjektive-zusammen", "🌳", "Zusammengesetzte Adjektive", "Adjektive zusammensetzen", [
    "Aus einem Nomen und einem Adjektiv wird ein **neues Adjektiv**.",
    "Das neue Wort ist ein Adjektiv, darum schreibt man es **klein**.",
], ["der Baum + hoch → **baumhoch**", "der Schnee + weiß → **schneeweiß**"],
    "", ["d3-adjektive/Zusammengesetzte Adjektive", "d3-adjektive/Noch mehr zusammensetzen"])
regel("steigern", "📈", "Adjektive steigern", "Steigern", [
    "Adjektive kann man **steigern**: groß – **größer** – **am größten**.",
    "Gleich viel: **so** groß **wie**. Unterschiedlich: größ**er als**.",
    "Merke: gut – **besser** – am **besten**, viel – **mehr** – am **meisten**.",
], ["Tom ist **so** alt **wie** Lea.", "Ein Hund ist größ**er als** eine Maus."],
    "", ["d3-adjektive/Steigern", "d3-adjektive/Vergleichen"])
regel("artikel", "📌", "Artikel: der, die, das, ein, eine", "Artikel", [
    "**der, die, das** sind **bestimmte** Artikel.",
    "**ein, eine** sind **unbestimmte** Artikel.",
    "Zu **der** und **das** gehört **ein**, zu **die** gehört **eine**.",
], ["der Hund → **ein** Hund", "die Katze → **eine** Katze"],
    "", ["d3-artikel-pronomen/der, die, das", "d3-artikel-pronomen/ein oder eine"])
regel("pronomen", "👉", "Pronomen ersetzen Nomen", "Pronomen", [
    "**Pronomen** stehen für ein Nomen: ich, du, er, sie, es, wir, ihr, sie.",
    "So muss man das Nomen nicht immer wiederholen.",
], ["**Die Katze** schläft. **Sie** ist müde."],
    "", ["d3-artikel-pronomen/Pronomen erkennen", "d3-artikel-pronomen/Pronomen verwenden"])

# ---------------- Deutsch 3. Klasse: Rechtschreibung ----------------
regel("verlaengern", "↔️", "Verlängern: d oder t, g oder k, b oder p?", "Verlängern", [
    "Am Wortende klingen d und t, g und k, b und p **gleich**.",
    "**Verlängere** das Wort: Mehrzahl, mit -er oder mit wir.",
    "Dann hörst du den richtigen Buchstaben.",
], ["der Hun**d** → die Hun**d**e", "der Zwer**g** → die Zwer**g**e", "gel**b** → gel**b**er"],
    "", ["d3-verlaengern"])
regel("doppelt", "✌️", "Doppelte Mitlaute, ck und tz", "Doppelte Mitlaute", [
    "Nach einem **kurzen** Selbstlaut folgen oft **zwei** Mitlaute: Ka**mm**, So**nn**e.",
    "Statt kk schreibt man **ck**, statt zz schreibt man **tz**.",
    "Hörst du schon zwei Mitlaute (Hu**nd**, ka**lt**), wird nichts verdoppelt.",
    "Nach l, n, r steht **nie** tz oder ck: Ker**z**e, Ban**k**.",
], ["der Ball, die Mütze, die Decke"],
    "Sprich das Wort langsam: Ist der Selbstlaut **kurz**?",
    ["d3-doppel"])
regel("ie", "📏", "Langes i: meistens ie", "Langes i = ie", [
    "Hörst du ein **langes i**, schreibst du meistens **ie**.",
    "Ein paar Wörter musst du dir merken: Tiger, Kino, Igel, ihr, ihm.",
], ["die Wiese, das Tier, spielen"],
    "", ["d3-lang/i oder ie", "d3-merkwoerter"])
regel("dehnungs-h", "🤫", "Das stumme h", "Dehnungs-h", [
    "Nach einem **langen** Selbstlaut steht manchmal ein **h**, das man nicht hört.",
    "Es steht oft vor **l, m, n** oder **r**.",
    "Diese Wörter muss man sich **merken**.",
], ["fa**hr**en, die Za**hl**, ne**hm**en, der So**hn**"],
    "", ["d3-lang/Mit h oder ohne"])
regel("ss-sz", "🐍", "ß oder ss?", "ß oder ss", [
    "Nach einem **langen** Selbstlaut oder au, ei, eu schreibt man **ß**: Fu**ß**, hei**ß**.",
    "Nach einem **kurzen** Selbstlaut schreibt man **ss**: Wa**ss**er, Ku**ss**.",
], ["die Straße – die Tasse", "groß – nass"],
    "", ["d3-lang/ß oder ss"])
regel("ableiten", "🌱", "ä oder e, äu oder eu?", "Ableiten", [
    "Gibt es ein **verwandtes Wort mit a**, schreibt man **ä**.",
    "Gibt es ein **verwandtes Wort mit au**, schreibt man **äu**.",
    "Sonst schreibt man e oder eu.",
], ["die B**ä**lle ← der B**a**ll", "die B**äu**me ← der B**au**m"],
    "", ["d3-ableiten"])
regel("trennen", "✂️", "Wörter trennen", "Trennen", [
    "Man trennt nach **Silben**: Ta-fel, Blu-me.",
    "**ch, ck, sch** bleiben zusammen: Sa-che, Zu-cker, Fla-sche.",
    "Ein **einzelner Buchstabe** wird nicht abgetrennt: Ofen, nicht O-fen.",
], ["Kat-ze, Fens-ter, Zu-cker"],
    "Klatsch die Silben mit!",
    ["d3-worttrennung"])
regel("sp-st", "🗣️", "Sp und St am Anfang", "Sp und St", [
    "Am Wortanfang spricht man **schp** und **scht**.",
    "Man schreibt aber **Sp** und **St**.",
], ["der **Sp**ort, der **St**ein, **sp**ringen"],
    "", ["d3-besondere-laute/Sp und St"])
regel("vorsilben", "🔑", "Vorsilben ver- und vor-", "ver- und vor-", [
    "Die Vorsilben **ver-** und **vor-** schreibt man immer mit **v**.",
    "Die Vorsilbe verändert die Bedeutung des Wortes.",
], ["**ver**laufen, **ver**gessen, **vor**lesen"],
    "", ["d3-vorsilben"])
regel("satzanfang", "🔠", "Satzanfang und Zeitangaben", "Satzanfang", [
    "Das **erste Wort** im Satz schreibt man **groß**.",
    "Nach einem **Punkt, Fragezeichen** oder **Ausrufezeichen** fängt ein neuer Satz an.",
    "Zeitangaben mit **am, der, heute** davor sind Nomen: **am Morgen, heute Abend**.",
    "Zeitangaben mit **-s** am Ende schreibt man klein: **morgens, abends**.",
], ["**Am** Montag spielen wir. Heute **A**bend lese ich.", "**m**ontags, **a**bends"],
    "", ["d3-grossschreibung"])
regel("satzzeichen", "❗", "Satzarten und Satzzeichen", "Satzzeichen", [
    "Am Ende eines **Aussagesatzes** steht ein **Punkt**.",
    "Am Ende einer **Frage** steht ein **Fragezeichen**.",
    "Nach einem **Ausruf** oder einer **Aufforderung** steht ein **Ausrufezeichen**.",
    "Bei einer **Aufzählung** steht ein **Komma**, aber nicht vor **und**.",
], ["Ich male. Malst du? Mal mit!", "Äpfel, Birnen**,** Kirschen und Pflaumen"],
    "", ["d3-satzarten"])
regel("satzglieder", "🧱", "Subjekt und Prädikat", "Subjekt und Prädikat", [
    "Das **Prädikat** ist das **Verb**. Es sagt, was jemand tut. Frage: **Was tut …?**",
    "Das **Subjekt** sagt, **wer** oder **was** etwas tut. Frage: **Wer oder was …?**",
    "Im Aussagesatz steht das Prädikat an **zweiter** Stelle.",
], ["**Der Hund** (Subjekt) **bellt** (Prädikat)."],
    "Umstellprobe: Teile, die zusammenbleiben, sind ein Satzglied.",
    ["d3-satzglieder"])
regel("woertliche-rede", "💬", "Wörtliche Rede", "Wörtliche Rede", [
    "Was jemand sagt, steht zwischen **Redezeichen**: „ … “",
    "Steht der Begleitsatz **vorne**, folgt ein **Doppelpunkt**: Tom sagt**:** „Hallo!“",
    "Steht der Begleitsatz **hinten**, folgt nach der Rede ein **Komma**: „Hallo“**,** sagt Tom.",
], ["Lea ruft: „Komm her!“", "„Ich komme“, sagt Max."],
    "", ["d3-woertliche-rede"])

# ---------------- Mathe 3. Klasse ----------------
regel("zahlwoerter", "✍️", "Zahlen als Wort schreiben", "Zahlwörter", [
    "Zahlen bis 1000 schreibt man als **ein Wort**, ohne Lücke.",
    "Zuerst kommen die **Hunderter**: **dreihundert**…",
    "Bei Zehnern und Einern kommt der **Einer zuerst**, dann **und**, dann der Zehner: sieben**und**vierzig.",
    "Zahlwörter schreibt man **klein**.",
], ["347 = **drei**hundert**sieben**und**vierzig**", "512 = fünfhundert**zwölf**", "609 = sechshundert**neun**"],
    "Aufpassen: ein**und**zwanzig (nicht eins), **sech**zig und **sieb**zig, drei**ß**ig mit ß.",
    ["m3-zahlen-entdecken/Zahlwörter"])
regel("stellenwerte", "🏛️", "Hunderter, Zehner, Einer", "Stellenwerte", [
    "Jede Ziffer hat einen **Platz**: **H**underter, **Z**ehner, **E**iner.",
    "10 Einer sind 1 Zehner. 10 Zehner sind 1 Hunderter. 10 Hunderter sind 1 Tausender.",
    "Ist eine Stelle leer, schreibt man eine **0**.",
], ["4 H, 0 Z, 7 E = **407**"],
    "", ["m3-zahlen-entdecken/Hunderter, Zehner, Einer", "m3-zahlen-entdecken/Stellentafel", "m3-zahlen1000/Stellenwerte"])
regel("runden", "🎯", "Runden", "Runden", [
    "Schau auf die Ziffer **rechts** von der Stelle, auf die du rundest.",
    "Bei **0, 1, 2, 3, 4** rundest du **ab**.",
    "Bei **5, 6, 7, 8, 9** rundest du **auf**.",
], ["347 ≈ 350 (auf Zehner)", "347 ≈ 300 (auf Hunderter)"],
    "", ["m3-zahlen1000/Runden"])
regel("schriftlich-plus", "➕", "Schriftlich plus rechnen", "Schriftlich plus", [
    "Schreibe die Zahlen **genau untereinander**: Einer unter Einer, Zehner unter Zehner.",
    "Fang **rechts bei den Einern** an.",
    "Sind es **10 oder mehr**, schreibst du den **Übertrag** klein in die nächste Spalte.",
], [],
    "Mach vorher einen **Überschlag**, dann merkst du Fehler.",
    ["m3-schriftlich/Plus ohne Übertrag", "m3-schriftlich/Plus mit Übertrag", "m3-schriftlich/Zwei Überträge"])
regel("schriftlich-minus", "➖", "Schriftlich minus rechnen", "Schriftlich minus", [
    "Schreibe die Zahlen **genau untereinander** und fang **rechts bei den Einern** an.",
    "Ist oben **zu wenig**, **entbündelst** du: Hol dir einen Zehner von links und mach daraus 10 Einer.",
    "Streich die Ziffer links durch und schreib die neue, kleinere Zahl darüber.",
], [],
    "", ["m3-schriftlich/Minus ohne Entbündeln", "m3-schriftlich/Minus mit Entbündeln", "m3-schriftlich/Zweimal entbündeln"])
regel("punkt-vor-strich", "⚡", "Punkt vor Strich", "Punkt vor Strich", [
    "**Mal** (·) und **geteilt** (:) rechnet man **zuerst**.",
    "Danach rechnet man **plus** und **minus**.",
    "Was in **Klammern** steht, rechnet man ganz zuerst.",
], ["3 + **4 · 2** = 3 + 8 = 11", "(3 + 4) · 2 = 7 · 2 = 14"],
    "", ["m3-mal-geteilt/Punkt vor Strich"])
regel("rest", "🍬", "Teilen mit Rest", "Teilen mit Rest", [
    "Manchmal geht eine Aufgabe **nicht genau auf**. Dann bleibt ein **Rest**.",
    "Der Rest ist immer **kleiner** als die Zahl, durch die du teilst.",
], ["17 : 5 = 3 Rest 2, denn 3 · 5 = 15 und 15 + 2 = 17"],
    "", ["m3-einmaleins/Teilen mit Rest", "m3-mal-geteilt/Teilen mit Rest"])
regel("einheiten", "📏", "Längen und Gewichte umrechnen", "Einheiten", [
    "1 km = **1000** m",
    "1 m = **100** cm, 1 cm = **10** mm",
    "1 kg = **1000** g",
], ["2 m 30 cm = 230 cm"],
    "", ["m3-laengen-gewichte/Kilometer und Meter", "m3-laengen-gewichte/Gewichte", "m3-groessen/Meter, cm und mm"])
regel("zeit", "⏰", "Stunden und Minuten", "Uhrzeit", [
    "1 Stunde hat **60** Minuten.",
    "Eine halbe Stunde sind **30** Minuten, eine Viertelstunde **15** Minuten.",
    "1 Minute hat **60** Sekunden, 1 Tag hat **24** Stunden.",
], [], "", ["m3-uhrzeit/Stunden und Minuten", "m3-uhrzeit/Zeitdauer"])
regel("geld", "💶", "Euro und Cent", "Euro und Cent", [
    "1 Euro = **100** Cent.",
    "Beim Komma stehen links die **Euro**, rechts die **Cent**.",
    "Rechts vom Komma stehen **immer zwei** Ziffern.",
], ["3,50 € = 3 € 50 ct", "3,05 € = 3 € 5 ct"],
    "", ["m3-geld/Euro mit Komma", "m3-groessen/Euro und Cent"])

# ---------------- Deutsch 1. Klasse (Eleanor: wird vorgelesen, darum sehr kurz) ----------------
regel("k1-silben", "👏", "Klatsch die Silben", "Silben", [
    "Sprich das Wort langsam und **klatsch** dabei.",
    "Jedes Klatschen ist **eine Silbe**.",
    "In jeder Silbe klingt ein **a, e, i, o** oder **u**.",
], ["Ma-ma 👏👏", "Ba-na-ne 👏👏👏"],
    "", ["d1-silben/Klatschen 1"])
regel("k1-leserichtung", "👉", "Wir lesen von links nach rechts", "Leserichtung", [
    "Wir lesen immer von **links** nach **rechts**.",
    "**am** und **ma** sind **nicht** gleich!",
], ["**a** → **m** = am", "**m** → **a** = ma"],
    "", ["d1-leserichtung/Gleiche Silbe finden", "d1-leserichtung/am oder ma? im oder mi?"])
regel("k1-ist-sind", "🍎", "ist oder sind?", "ist oder sind", [
    "Bei **einem** sagt man **ist**.",
    "Bei **vielen** sagt man **sind**.",
], ["Da **ist** ein Apfel. 🍎", "Da **sind** Äpfel. 🍎🍎🍎"],
    "", ["d1-lesen/ist oder sind"])
regel("k1-ein-eine", "🐶", "ein oder eine?", "ein oder eine", [
    "**der** Hund → **ein** Hund",
    "**das** Haus → **ein** Haus",
    "**die** Katze → **eine** Katze",
], [], "", ["d1-lesen2/ein oder eine?"])

# ---------------- Mathe 1. Klasse (Eleanor) ----------------
regel("k1-tausch", "🔄", "Tauschaufgaben", "Tauschaufgabe", [
    "Bei **plus** darf man die Zahlen **tauschen**.",
    "Das Ergebnis bleibt **gleich**.",
], ["3 + 5 = 8", "5 + 3 = 8"], "", ["m1-rechnen10/Tausch- und Nachbaraufgaben"])
regel("k1-umkehr", "↩️", "Umkehraufgaben", "Umkehraufgabe", [
    "**Minus** macht **plus** wieder rückgängig.",
], ["4 + 3 = 7", "7 − 3 = 4"], "", ["m1-rechnen10/Umkehraufgaben"])
regel("k1-nachbarn", "🏠", "Nachbarzahlen", "Nachbarzahlen", [
    "Der **linke** Nachbar ist **eins weniger**.",
    "Der **rechte** Nachbar ist **eins mehr**.",
], ["**4** – 5 – **6**"], "", ["m1-zahlen10/Nachbarzahlen", "m1-zahlen20/Nachbarzahlen"])
regel("k1-vergleichen", "🐊", "Größer oder kleiner?", "Vergleichen", [
    "Das **Krokodil** hat Hunger. Es frisst immer die **größere** Zahl.",
    "Der offene Mund zeigt zur größeren Zahl.",
], ["7 **>** 3", "2 **<** 9"], "", ["m1-zahlen10/Vergleichen", "m1-zahlen20/Vergleichen"])
regel("k1-zehner", "🔟", "Über die 10 rechnen", "Über die 10", [
    "Rechne **zuerst bis zur 10**.",
    "Dann rechnest du den **Rest** dazu.",
], ["8 + 5 = 8 + **2** + **3** = 13"], "", ["m1-rechnen20/Plus über die 10", "m1-rechnen20/Minus über die 10"])

# ================== Wortarten-Werkstatt (Deutsch 3. Klasse) ==================
FARBE = {"Nomen": "#3b6fd8", "Verb": "#1f9d5c", "Adjektiv": "#e5484d"}  # Schulfarben, hier ändern
COLORS = [{"key": k, "label": k, "color": c} for k, c in FARBE.items()]
def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")).strip("-")[:30]

SORT = {"Nomen": ["Hund", "Schule", "Freude", "Apfel", "Zahn", "Mut"],
        "Verb": ["rennen", "lacht", "schreiben", "schwimmt", "malen", "singt"],
        "Adjektiv": ["laut", "grün", "müde", "schnell", "weich", "lustig"]}
def mark(id_, text, keys, task, explain=""):
    cs = [c for c in COLORS if c["key"] in keys]
    t = {"kind": "mark", "id": id_, "task": task, "text": text, "colors": cs}
    if explain: t["explain"] = explain
    return t
ADJ = [
    "Der [kleine|Adjektiv] Hund bellt [laut|Adjektiv]. Er hat ein [weiches|Adjektiv] Fell.",
    "Im [dunklen|Adjektiv] Wald steht ein [alter|Adjektiv] Baum. Seine Blätter sind [gelb|Adjektiv] und [rot|Adjektiv].",
    "Lena trinkt [heißen|Adjektiv] Kakao. Danach ist sie [satt|Adjektiv] und [müde|Adjektiv].",
    "Die [bunten|Adjektiv] Fische schwimmen [schnell|Adjektiv] durch das [klare|Adjektiv] Wasser.",
]
NOM = [
    "Am Morgen packt [Tim|Nomen] seine [Tasche|Nomen]. Er nimmt ein [Heft|Nomen] und zwei [Stifte|Nomen] mit.",
    "Die [Katze|Nomen] jagt eine [Maus|Nomen] durch den [Garten|Nomen].",
    "Oma backt einen [Kuchen|Nomen] mit [Äpfeln|Nomen]. Die [Freude|Nomen] ist groß.",
]
VERB = [
    "Die Kinder [spielen|Verb] im Hof. Paul [wirft|Verb] den Ball und Mia [fängt|Verb] ihn.",
    "Am Abend [liest|Verb] Papa ein Buch vor. Ich [kuschle|Verb] mich ins Bett und [schlafe|Verb] ein.",
    "Der Vogel [baut|Verb] ein Nest. Bald [schlüpfen|Verb] die Küken.",
]
ALLE = [
    "Der [Hund|Nomen] [rennt|Verb] [schnell|Adjektiv] über die [Wiese|Nomen].",
    "Die [kleine|Adjektiv] [Katze|Nomen] [trinkt|Verb] [frische|Adjektiv] [Milch|Nomen].",
    "Im [Sommer|Nomen] [schwimmen|Verb] wir im [kalten|Adjektiv] [See|Nomen].",
    "Mein [Bruder|Nomen] [malt|Verb] ein [buntes|Adjektiv] [Bild|Nomen].",
    "Der [Mond|Nomen] [leuchtet|Verb] [hell|Adjektiv] am [Himmel|Nomen].",
    "Die [Kinder|Nomen] [lachen|Verb] [laut|Adjektiv] über den [lustigen|Adjektiv] [Witz|Nomen].",
]
PROBE = [  # Welche Probe hilft?
    ("Ist „Wolke“ ein Nomen?", "die Wolke", "der/die/das davor"),
    ("Ist „leise“ ein Adjektiv?", "Wie ist die Maus? leise", "Wie ist …?"),
    ("Ist „springen“ ein Verb?", "ich springe", "ich davor"),
    ("Ist „Glück“ ein Nomen?", "das Glück", "der/die/das davor"),
    ("Ist „kalt“ ein Adjektiv?", "Wie ist das Eis? kalt", "Wie ist …?"),
    ("Ist „kochen“ ein Verb?", "ich koche", "ich davor"),
]
mal = json.load(open("werkzeug/malen/pferd-wortarten.json"))
MAL_FARBE = FARBE  # gleiche Farben wie beim Textmarker, damit die Kinder nicht durcheinanderkommen
wortarten = {"id": "d3-wortarten", "type": "schule", "title_de": "Wortarten-Werkstatt", "image": "🔤", "color": "#e5484d", "lessons": [
    {"title": "Nomen, Verb oder Adjektiv?", "icon": "🗂️", "tasks": [
        {"kind": "sort", "id": "d3-wa-sort", "task": "Ist das ein Nomen, ein Verb oder ein Adjektiv?", "review": "Welche Wortart ist das?",
         "groups": list(FARBE), "items": [{"id": f"d3-wa-s-{slug(w)}", "text": w, "group": g} for g, ws in SORT.items() for w in ws]}]},
    {"title": "Adjektive rot anmalen", "icon": "🖍️", "tasks": [mark(f"d3-wa-adj-{i}", t, ["Adjektiv"], "Male alle Adjektive rot an!", "Adjektive sagen, wie etwas ist.") for i, t in enumerate(ADJ)]},
    {"title": "Nomen blau anmalen", "icon": "🖍️", "tasks": [mark(f"d3-wa-nom-{i}", t, ["Nomen"], "Male alle Nomen blau an!", "Nomen schreibt man groß. Der, die oder das passt davor.") for i, t in enumerate(NOM)]},
    {"title": "Verben grün anmalen", "icon": "🖍️", "tasks": [mark(f"d3-wa-verb-{i}", t, ["Verb"], "Male alle Verben grün an!", "Verben sagen, was jemand tut.") for i, t in enumerate(VERB)]},
    {"title": "Alle drei Wortarten", "icon": "🌈", "mix": True, "tasks": [mark(f"d3-wa-alle-{i}", t, list(FARBE), "Male Nomen blau, Verben grün und Adjektive rot an!") for i, t in enumerate(ALLE)]},
    {"title": "Ausmalbild Pferdeweide", "icon": "🐴", "tasks": [{
        "kind": "paint", "id": "d3-wa-mal-pferd", "task": "Lies jedes Wort. Nomen blau, Verben grün, Adjektive rot!",
        "prompt": "Ausmalbild Pferdeweide: Wortarten", "image": "img/malen/pferd-wortarten.png", "map": "img/malen/pferd-wortarten-map.png",
        "regions": mal["regions"], "prefill": mal["prefill"], "wordHint": True, "regel": "wortarten",
        "colors": [{"key": k, "label": k, "color": c} for k, c in MAL_FARBE.items()]}]},
    {"title": "Welche Probe hilft?", "icon": "🔍", "mix": True, "tasks": [
        {"kind": "choice", "id": f"d3-wa-probe-{i}", "task": "Welche Probe hilft?", "prompt": q, "options": ["der/die/das davor", "ich davor", "Wie ist …?"],
         "keepOrder": True, "answer": a, "explain": f"Probe: {ex}", "regel": "wortarten"} for i, (q, ex, a) in enumerate(PROBE)]},
    {"title": "Test", "icon": "🏆", "test": True, "count": 12},
]}

# ================== Regel-Detektiv: Welche Regel hilft? ==================
def detektiv(id_, title, color, fragen):
    tasks = []
    for i, (frage, antwort, falsch, explain) in enumerate(fragen):
        tasks.append({"kind": "choice", "id": f"{id_}-{i}", "task": "Welche Regel hilft?", "prompt": frage,
                      "options": [antwort] + falsch, "answer": antwort, "explain": explain})
    half = (len(tasks) + 1) // 2
    return {"id": id_, "type": "schule", "title_de": title, "image": "🕵️", "color": color, "lessons": [
        {"title": "Welche Regel hilft? 1", "icon": "🕵️", "mix": True, "tasks": tasks[:half]},
        {"title": "Welche Regel hilft? 2", "icon": "🕵️", "mix": True, "tasks": tasks[half:]},
        {"title": "Test", "icon": "🏆", "test": True, "count": 10}]}
K = {r["id"]: r["kurz"] for r in R}
D3 = [
    ("Hund oder Hunt?", K["verlaengern"], [K["doppelt"], K["ableiten"]], "Verlängern: die Hunde. Man hört d, also Hund."),
    ("Bäume oder Beume?", K["ableiten"], [K["verlaengern"], K["ie"]], "Ableiten: Baum hat au, also Bäume."),
    ("Mütze oder Müze?", K["doppelt"], [K["ss-sz"], K["vorsilben"]], "Kurzes ü: tz. Mütze."),
    ("Wiese oder Wise?", K["ie"], [K["dehnungs-h"], K["doppelt"]], "Langes i: meistens ie."),
    ("Straße oder Strasse?", K["ss-sz"], [K["doppelt"], K["sp-st"]], "Langes a: ß."),
    ("Die Freude oder die freude?", K["nomen-gross"], [K["adjektive"], K["satzanfang"]], "Artikelprobe: die Freude. Ein Nomen, also groß."),
    ("Der rote Ball oder der Rote Ball?", K["adjektive"], [K["nomen-gross"], K["artikel"]], "Wie ist der Ball? rot. Ein Adjektiv, also klein."),
    ("Die Heizung oder die heizung?", K["nomen-endungen"], [K["adjektive"], K["vorsilben"]], "-ung macht ein Nomen, also groß."),
    ("schneeweiß oder Schneeweiß?", K["adjektive-zusammen"], [K["nomen-gross"], K["nomen-zusammen"]], "Wie ist der Schnee? schneeweiß. Ein Adjektiv, also klein."),
    ("Am Abend oder am abend?", K["satzanfang"], [K["adjektive"], K["artikel"]], "am Abend: Zeitangabe mit am, also groß."),
    ("Schtein oder Stein?", K["sp-st"], [K["verlaengern"], K["trennen"]], "Man hört scht, schreibt aber St."),
    ("Sa-che oder Sac-he?", K["trennen"], [K["doppelt"], K["sp-st"]], "ch bleibt beim Trennen zusammen."),
    ("lustig oder lustich?", K["adjektiv-endungen"], [K["ie"], K["verlaengern"]], "Verlängern: lustiger. Man hört g."),
    ("Ich bin gelaufen oder ich habe gelaufen?", K["hat-ist"], [K["vergangenheit"], K["verben"]], "Bewegung: ist (bin)."),
    ("„Hallo“, sagt Tom. Wo steht das Komma?", K["woertliche-rede"], [K["satzzeichen"], K["satzglieder"]], "Begleitsatz hinten: Komma nach der Rede."),
    ("Wer bellt? Der Hund.", K["satzglieder"], [K["woertliche-rede"], K["pronomen"]], "Wer oder was? fragt nach dem Subjekt."),
]
M3 = [
    ("Wie schreibt man 47 als Wort?", K["zahlwoerter"], [K["stellenwerte"], K["runden"]], "Erst der Einer, dann und, dann der Zehner: siebenundvierzig."),
    ("3 + 4 · 2 = ?", K["punkt-vor-strich"], [K["schriftlich-plus"], K["rest"]], "Mal zuerst: 3 + 8 = 11."),
    ("347 auf Zehner runden", K["runden"], [K["stellenwerte"], K["zahlwoerter"]], "Rechts steht 7, also aufrunden: 350."),
    ("4 H, 0 Z, 7 E = ?", K["stellenwerte"], [K["runden"], K["einheiten"]], "Leere Stelle: 0. Also 407."),
    ("2 m 30 cm = ? cm", K["einheiten"], [K["geld"], K["zeit"]], "1 m = 100 cm, also 230 cm."),
    ("3,05 € = ? Cent", K["geld"], [K["einheiten"], K["stellenwerte"]], "1 € = 100 ct, also 305 ct."),
    ("17 : 5 = ?", K["rest"], [K["punkt-vor-strich"], K["schriftlich-minus"]], "3 · 5 = 15, Rest 2."),
    ("Wie viele Minuten sind eine halbe Stunde?", K["zeit"], [K["einheiten"], K["geld"]], "1 Stunde = 60 min, die Hälfte sind 30 min."),
    ("Bei 532 − 218 sind oben bei den Einern zu wenig.", K["schriftlich-minus"], [K["schriftlich-plus"], K["runden"]], "Entbündeln: einen Zehner holen."),
    ("Bei 458 + 37 sind es bei den Einern 15.", K["schriftlich-plus"], [K["schriftlich-minus"], K["rest"]], "5 hinschreiben, 1 als Übertrag."),
]
for r in R: r.pop("kurz")
json.dump({"regeln": R}, open("inhalte/regeln.json", "w"), ensure_ascii=False, indent=1)
json.dump(wortarten, open("inhalte/deutsch/k3-wortarten.json", "w"), ensure_ascii=False, indent=1)
json.dump(detektiv("d3-regel-detektiv", "Regel-Detektiv", "#c99a00", D3), open("inhalte/deutsch/k3-regel-detektiv.json", "w"), ensure_ascii=False, indent=1)
json.dump(detektiv("m3-regel-detektiv", "Regel-Detektiv", "#c99a00", M3), open("inhalte/mathe/k3-regel-detektiv.json", "w"), ensure_ascii=False, indent=1)
print(len(R), "Regeln")
