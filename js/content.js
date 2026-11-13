// Lädt die Inhalte aus dem Ordner "inhalte" und prüft sie.
// Fehler werden gesammelt und im Elternbereich angezeigt, statt dass die App leer bleibt.

export const content = { subjects: [], items: new Map(), units: new Map(), photoTasks: new Map(), errors: [] };

// ---------- Schulfächer ----------
// Eine Schul-Einheit hat "type": "schule" und eine Liste "lessons" mit Aufgaben ("tasks").
// Jede bewertbare Aufgabe kommt als Einzelfrage in die Lernkartei (content.items, kind "task").

const KINDS = ["pairs", "type", "choice", "sort", "syllables", "photo", "paint"];

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
      if (t.kind === "choice" && !(t.options || []).includes(t.answer)) err(`${t.id}: Die Antwort steht nicht bei den Auswahlmöglichkeiten.`);
      // Ausmalbild: kommt in die Lernkartei (Wiederholung), aber nicht in Tests
      if (t.kind === "paint") {
        const keys = (t.colors || []).map((c) => c.key);
        if (!t.id || !(t.grid || []).length || !keys.length) err("Ein Ausmalbild braucht id, grid und colors.");
        for (const row of t.grid || []) for (const ch of row) if (!keys.includes(ch)) err(`${t.id}: Im Bild steht "${ch}", dafür gibt es keine Farbe.`);
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
  return content;
}
