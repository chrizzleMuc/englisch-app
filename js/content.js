// Lädt die Inhalte aus dem Ordner "inhalte" und prüft sie.
// Fehler werden gesammelt und im Elternbereich angezeigt, statt dass die App leer bleibt.
import { setFotos } from "./pics.js";

export const content = { subjects: [], items: new Map(), units: new Map(), photoTasks: new Map(), rules: new Map(), errors: [] };

// ---------- Schulfächer ----------
// Eine Schul-Einheit hat "type": "schule" und eine Liste "lessons" mit Aufgaben ("tasks").
// Jede bewertbare Aufgabe kommt als Einzelfrage in die Lernkartei (content.items, kind "task").

const KINDS = ["pairs", "type", "choice", "sort", "syllables", "photo", "paint", "column", "chain", "build", "flash", "mark", "gitter", "schlange", "order", "label"];

function sharedStart(a, b) {
  const wa = a.split(" ");
  const wb = b.split(" ");
  return wa.length > 1 && wb.length > 1 && wa[0] === wb[0] ? wa[0] : "";
}

// Macht aus einem Paar oder Sortier-Wort eine Einzelfrage (für Wiederholung und Test)
function singles(t) {
  if (t.kind === "pairs") {
    return t.pairs.map((p) => {
      const before = sharedStart(p.a, p.b);
      return { kind: "type", id: p.id, task: t.review || "Was gehört dazu?", prompt: p.a, before, answer: before ? p.b.slice(before.length + 1) : p.b };
    });
  }
  if (t.kind === "sort") {
    if (t.pics) return t.items.map((it) => ({ kind: "choice", id: it.id, task: t.review || t.task || "Wohin gehört das?", prompt: it.text, pic: it.pic, options: t.groups, answer: it.group, picText: true }));
    return t.items.map((it) => ({ kind: "choice", id: it.id, task: t.review || "Wohin gehört das Wort?", prompt: it.text, options: t.groups, answer: it.group }));
  }
  if (t.kind === "photo") return [];
  return [t];
}

function checkSchool(unit, path) {
  const err = (m) => content.errors.push(`${path}: ${m}`);
  unit.words = [];
  unit.phrases = [];
  unit.lessons = unit.lessons || [];
  unit.singles = [];
  if (!unit.lessons.length) err("Die Einheit hat keine Lektionen.");
  const add = (q) => {
    if (!q.id) return err(`Eine Aufgabe (${q.kind}) hat keine id.`);
    if (content.items.has(q.id)) err(`Die ID ${q.id} gibt es doppelt.`);
    content.items.set(q.id, { id: q.id, kind: "task", unit: unit.id, q });
    unit.singles.push(q);
  };
  for (const l of unit.lessons) {
    l.tasks = l.tasks || [];
    for (const t of l.tasks) {
      if (!KINDS.includes(t.kind)) {
        err(`Unbekannte Aufgabenart "${t.kind}".`);
        continue;
      }
      if (t.kind === "pairs" && !(t.pairs || []).length) err("Eine Paare-Aufgabe hat keine Paare.");
      if (t.kind === "sort" && (!(t.groups || []).length || !(t.items || []).length)) err("Eine Sortier-Aufgabe braucht groups und items.");
      if (t.kind === "sort") for (const it of t.items || []) if (!t.groups.includes(it.group)) err(`${it.id}: Gruppe "${it.group}" gibt es nicht.`);
      // Schriftlich rechnen: Aufgabe und Ergebnis als Text für Elternbereich und Auswertung
      if (t.kind === "column") {
        const nums = t.nums || [];
        if (nums.length < 2 || !["+", "-"].includes(t.op) || (t.op === "-" && (nums.length !== 2 || nums[0] < nums[1]))) err(`${t.id}: Schriftliche Aufgabe braucht nums und op (+ oder -).`);
        t.prompt = nums.join(t.op === "+" ? " + " : " − ");
        t.answer = String(t.op === "+" ? nums.reduce((a, b) => a + b, 0) : nums[0] - nums[1]);
      }
      // Satz bauen: Antworten sind Listen von Bausteinen (alle Bausteine, andere Reihenfolge)
      if (t.kind === "build") {
        const key = (a) => [...a].map((w) => w.toLowerCase()).sort().join("|");
        if (!(t.tiles || []).length || !(t.answers || []).length) err(`${t.id}: Satz bauen braucht tiles und answers.`);
        for (const a of t.answers || []) if (key(a) !== key(t.tiles || [])) err(`${t.id}: Eine Lösung passt nicht zu den Bausteinen.`);
        t.prompt = t.prompt || t.tiles.join(" / ");
        t.answer = (t.answers[0] || []).map((w, i) => (i ? w : w[0].toUpperCase() + w.slice(1))).join(" ").replace(/ ([,.!?:])/g, "$1") + (t.end || "");
      }
      // Reihenfolge: tiles stehen in der richtigen Reihenfolge, die App mischt sie
      if (t.kind === "order") {
        if ((t.tiles || []).length < 2) err(`${t.id}: Reihenfolge braucht mindestens 2 tiles.`);
        const plain = (x) => String(x).replace(/\[\[[^\]]+\]\]/g, "").replace(/^\P{L}+/u, "").trim() || x;
        t.prompt = t.prompt || t.task;
        t.answer = (t.tiles || []).map(plain).join(" → ");
      }
      // Schaubild beschriften: image (img/zeichnungen/<image>.svg), spots mit x, y, answer
      if (t.kind === "label") {
        if (!t.image || (t.spots || []).length < 2) err(`${t.id}: Schaubild braucht image und mindestens 2 spots.`);
        t.prompt = t.prompt || t.task;
        t.answer = (t.spots || []).map((s, k) => `${k + 1} ${s.answer}`).join(", ");
        // Lückentext zum Bild: text = Absätze, jede "__" ist die nächste Lücke (Reihenfolge wie spots)
        if (t.text) {
          const gaps = t.text.join(" ").split("__").length - 1;
          if (gaps !== t.spots.length) err(`${t.id}: Lückentext hat ${gaps} Lücken, aber ${t.spots.length} spots.`);
          let k = 0;
          t.answer = t.text.join(" ").replace(/__/g, () => t.spots[k++]?.answer || "?");
        }
      }
      if (t.kind === "flash") {
        if (!t.word || !(t.options || []).includes(t.answer)) err(`${t.id}: Blitzlesen braucht word und die Antwort bei options.`);
        t.prompt = t.prompt || t.word;
      }
      // Textmarker: Wörter im Text nach Wortart anmalen. text = Wörter, Wortart in eckigen Klammern: "Der [kleine|a] Hund"
      if (t.kind === "mark") {
        const keys = (t.colors || []).map((c) => c.key);
        t.tokens = [];
        for (const m of String(t.text || "").matchAll(/\[([^\]|]+)\|([^\]]+)\]([.,!?:;]*)|([^\s\[]+)/g)) {
          if (m[1]) {
            if (!keys.includes(m[2])) err(`${t.id}: "${m[2]}" hat keine Farbe.`);
            t.tokens.push({ w: m[1] + m[3], word: m[1], k: m[2] });
          } else t.tokens.push({ w: m[4], word: m[4].replace(/[.,!?:;]+$/, "") });
        }
        if (!t.tokens.some((x) => x.k)) err(`${t.id}: Im Text ist kein Wort markiert.`);
        t.prompt = t.prompt || t.tokens.map((x) => x.w).join(" ");
        t.answer = t.answer || t.tokens.filter((x) => x.k).map((x) => x.word).join(", ");
        if (content.items.has(t.id)) err(`Die ID ${t.id} gibt es doppelt.`);
        content.items.set(t.id, { id: t.id, kind: "task", unit: unit.id, q: t });
        continue;
      }
      if (t.kind === "chain" && !(t.lines || []).length) err(`${t.id}: Rechenweg ohne Schritte.`);
      if (t.kind === "choice" && !(t.options || []).includes(t.answer)) err(`${t.id}: Die Antwort steht nicht bei den Auswahlmöglichkeiten.`);
      // Ausmalbild: kommt in die Lernkartei (Wiederholung), aber nicht in Tests.
      // image = Strichzeichnung, map = gleiches Bild, Grauwert = Nummer der Fläche (0 = Linie), regions = Nummer → Silbe
      if (t.kind === "paint") {
        const keys = (t.colors || []).map((c) => c.key);
        if (!t.id || !t.image || !t.map || !t.regions || !keys.length) err("Ein Ausmalbild braucht id, image, map, regions und colors.");
        for (const [r, k] of Object.entries(t.regions || {})) if (k && !keys.includes(k)) err(`${t.id}: Fläche ${r} hat "${k}", dafür gibt es keine Farbe.`);
        if (content.items.has(t.id)) err(`Die ID ${t.id} gibt es doppelt.`);
        content.items.set(t.id, { id: t.id, kind: "task", unit: unit.id, q: t });
        continue;
      }
      if (t.kind === "photo") {
        if (!t.id) err("Eine Foto-Aufgabe hat keine id.");
        content.photoTasks.set(t.id, { ...t, unit: unit.id });
        continue;
      }
      for (const q of singles(t)) add(q);
    }
  }
  // Rätsel-Vorrat: Lektionen mit "pick" ziehen daraus zufällig (z. B. Rechengitter, Zahlenschlange)
  for (const t of unit.pool || []) {
    if (!KINDS.includes(t.kind)) {
      err(`Unbekannte Aufgabenart "${t.kind}".`);
      continue;
    }
    if (t.kind === "gitter") {
      if (!(t.grid || []).length) err(`${t.id}: Rechengitter ohne Raster.`);
      t.prompt = t.prompt || `Rechengitter (${t.grid.flat().filter((x) => String(x).startsWith("?")).length} Kästchen)`;
      t.answer = "";
    }
    if (t.kind === "schlange") {
      if (!(t.nodes || []).length || !(t.edges || []).length) err(`${t.id}: Zahlenschlange braucht nodes und edges.`);
      t.prompt = t.prompt || `Zahlenschlange ab ${t.nodes[0][2]}`;
      t.answer = "";
    }
    add(t);
  }
}

// Einzelrechnung aus einem Rätsel, die falsch war (kommt in die Lernkartei).
// Die ID enthält die Rechnung selbst, z. B. "rr:7·?=56", damit sie auch nach einem Neustart da ist.
export function puzzleItem(id) {
  if (!String(id).startsWith("rr:")) return null;
  if (content.items.has(id)) return content.items.get(id);
  const m = String(id).slice(3).match(/^(\?|\d+)([+\-·:])(\?|\d+)=(\?|\d+)$/);
  if (!m) return null;
  const [a, op, b, c] = [m[1], m[2], m[3], m[4]];
  const n = (x) => Number(x);
  const val = { "+": [n(c) - n(b), n(c) - n(a), n(a) + n(b)], "-": [n(b) + n(c), n(a) - n(c), n(a) - n(b)], "·": [n(c) / n(b), n(c) / n(a), n(a) * n(b)], ":": [n(b) * n(c), n(a) / n(c), n(a) / n(b)] }[op];
  const i = [a, b, c].indexOf("?");
  const shown = op === "-" ? "−" : op;
  const q = { kind: "type", id, num: true, task: "Rechne aus! (aus dem Rechenrätsel)", prompt: `${a === "?" ? "__" : a} ${shown} ${b === "?" ? "__" : b} = ${c === "?" ? "__" : c}`, answer: String(val[i]) };
  const it = { id, kind: "task", unit: "m3-raetsel", q };
  content.items.set(id, it);
  return it;
}

async function getJson(path) {
  const res = await fetch("inhalte/" + path);
  if (!res.ok) throw new Error(`Datei fehlt: inhalte/${path}`);
  try {
    return JSON.parse(await res.text());
  } catch (e) {
    throw new Error(`Datei kaputt (Tippfehler?): inhalte/${path}. ${e.message}`);
  }
}

function check(unit, path) {
  if (unit.type === "schule") return checkSchool(unit, path);
  const err = (m) => content.errors.push(`${path}: ${m}`);
  if (!unit.id) err("Es fehlt die „id“ der Einheit.");
  unit.words = unit.words || [];
  unit.phrases = unit.phrases || [];
  unit.story = unit.story || [];
  unit.questions = unit.questions || [];
  if (unit.words.length < 4) err("Eine Einheit braucht mindestens 4 Wörter.");
  for (const kind of ["words", "phrases"]) {
    for (const it of unit[kind]) {
      if (!it.id || !it.en || !it.image) err(`Ein Eintrag bei "${kind}" hat keine id, kein en oder kein image.`);
      if (content.items.has(it.id)) err(`Die ID ${it.id} gibt es doppelt.`);
      content.items.set(it.id, { ...it, unit: unit.id, kind: kind === "words" ? "word" : "phrase" });
    }
  }
  for (const q of unit.questions) {
    for (const c of [q.answer, ...(q.choices || [])]) {
      if (!unit.words.some((w) => w.id === c)) err(`Frage ${q.id}: Die Antwort ${c} ist kein Wort dieser Einheit.`);
    }
  }
}

// Regeln (inhalte/regeln.json): Regelkarte vor der Lektion, Regel-Knopf bei Fehlern, Regelheft.
// "lektionen": ["<Einheit-id>/<Lektionstitel>", …] oder "<Einheit-id>" für alle Lektionen der Einheit.
function attachRules(list) {
  for (const r of list || []) {
    if (!r.id || !r.title || !(r.merke || []).length) {
      content.errors.push(`regeln.json: Eine Regel braucht id, title und merke.`);
      continue;
    }
    content.rules.set(r.id, r);
    for (const ref of r.lektionen || []) {
      const [uid, title] = ref.split("/");
      const u = content.units.get(uid);
      const ls = u ? (title ? u.lessons.filter((l) => l.title === title) : u.lessons) : [];
      if (!ls.length) content.errors.push(`regeln.json: ${r.id}: Lektion "${ref}" gibt es nicht.`);
      for (const l of ls) {
        if (!l.regel) l.regel = r.id;
        for (const t of l.tasks || []) {
          if (!t.regel) t.regel = r.id;
          (t.items || []).forEach((it) => content.items.get(it.id) && !content.items.get(it.id).q.regel && (content.items.get(it.id).q.regel = r.id));
          (t.pairs || []).forEach((it) => content.items.get(it.id) && !content.items.get(it.id).q.regel && (content.items.get(it.id).q.regel = r.id));
        }
        if (u && !r.stage) r.stage = u.stageId;
        if (u && !r.unit) r.unit = u.id;
      }
    }
  }
}

export async function loadContent() {
  content.errors = [];
  let overview;
  try {
    overview = await getJson("uebersicht.json");
  } catch (e) {
    content.errors.push(e.message);
    return content;
  }
  for (const sub of overview.subjects || []) {
    const s = { ...sub, stages: [] };
    for (const st of sub.stages || []) {
      const stage = { ...st, units: [] };
      for (const path of st.units || []) {
        try {
          const unit = await getJson(path);
          check(unit, path);
          unit.subject = s.id;
          unit.stageId = stage.id;
          stage.units.push(unit);
          content.units.set(unit.id, unit);
        } catch (e) {
          content.errors.push(e.message);
        }
      }
      s.stages.push(stage);
    }
    content.subjects.push(s);
  }
  // Freie Fotos (Wikimedia Commons) mit Bildnachweis
  try {
    content.fotos = await getJson("fotos.json");
  } catch (e) {
    content.fotos = {};
  }
  setFotos(content.fotos);
  // regeln.json (Deutsch, Mathe) und wissen-hsu.json (Merkkarten Sachunterricht)
  for (const f of ["regeln.json", "wissen-hsu.json"]) {
    try {
      attachRules((await getJson(f)).regeln);
    } catch (e) {
      content.errors.push(e.message);
    }
  }
  return content;
}
