import json, sys
COL = {"rot": "#e5484d", "gelb": "#f2c230", "gruen": "#3f9d4a", "hellgruen": "#9bd36a", "blau": "#5aa9f0", "braun": "#8d5a32", "orange": "#f28b30", "lila": "#8e5cd9", "grau": "#7d7f8c", "rosa": "#f28ab8"}
def P(id_, title, grid, colors, task=None):
    cs = [{"key": k, "label": lab, "color": COL[c]} for k, (lab, c) in colors.items()]
    return {"kind": "paint", "id": id_, "task": task or "Male aus! Tipp zuerst eine Farbe an, dann die Felder mit dieser Silbe.", "prompt": f"Ausmalbild {title}: " + ", ".join(c["label"] for c in cs), "grid": grid, "colors": cs}
pics = [
 P("k1-mal-pilz", "Pilz", ["..RRR..", ".RRRRR.", "RRRRRRR", "..SSS..", "..SSS..", "GGSSSGG", "GGGGGGG"],
   {"R": ("ma", "rot"), "S": ("mi", "braun"), "G": ("am", "gruen"), ".": ("im", "blau")}),
 P("k1-mal-baum", "Baum", ["..GGG..", ".GGGGG.", "GGGGGGG", ".GGGGG.", "...B...", "...B...", "LLLBLLL"],
   {"G": ("mo", "gruen"), "B": ("mu", "braun"), "L": ("om", "hellgruen"), ".": ("um", "blau")}),
 P("k1-mal-fisch", "Fisch", [".......", "..OO..O", ".OOOOOO", "OSOOOOO", ".OOOOOO", "..OO..O", "......."],
   {"O": ("la", "orange"), "S": ("al", "lila"), ".": ("le", "blau")}),
 P("k1-mal-haus", "Haus", ["...R...", "..RRR..", ".RRRRR.", ".WWWWW.", ".WBWBW.", ".WWBWW.", "GGGBGGG"],
   {"R": ("ro", "rot"), "W": ("re", "gelb"), "B": ("ri", "braun"), "G": ("ra", "gruen"), ".": ("or", "blau")}),
 P("k1-mal-blume", "Blume", ["...Y...", "..YOY..", "...Y...", "...S...", ".LLS...", "...SLL.", "GGGSGGG"],
   {"Y": ("so", "rosa"), "O": ("os", "gelb"), "S": ("sa", "gruen"), "L": ("as", "hellgruen"), "G": ("sa", "braun") if False else ("si", "braun"), ".": ("se", "blau")}),
 P("k1-mal-sonne", "Sonne", ["Y..Y..Y", ".YYYYY.", ".YOOOY.", "YYOOOYY", ".YOOOY.", ".YYYYY.", "Y..Y..Y"],
   {"Y": ("ti", "gelb"), "O": ("it", "orange"), ".": ("te", "blau")}),
]
u = {"id": "d1-ausmalen", "type": "schule", "title_de": "Ausmalbilder: Silben lesen", "image": "🎨", "color": "#8e5cd9",
     "lessons": [
       {"title": "Pilz: ma mi am im", "icon": "🎨", "tasks": [pics[0]]},
       {"title": "Baum: mo mu om um", "icon": "🌳", "tasks": [pics[1]]},
       {"title": "Fisch: la al le", "icon": "🐟", "tasks": [pics[2]]},
       {"title": "Haus: ro re ri ra or", "icon": "🏠", "tasks": [pics[3]]},
       {"title": "Blume: so os sa as si se", "icon": "🌷", "tasks": [pics[4]]},
       {"title": "Sonne: ti it te", "icon": "🌞", "tasks": [pics[5]]},
     ]}
json.dump(u, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
