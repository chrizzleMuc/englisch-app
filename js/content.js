// Lädt die Inhalte aus dem Ordner "inhalte" und prüft sie.
// Fehler werden gesammelt und im Elternbereich angezeigt, statt dass die App leer bleibt.

export const content = { subjects: [], items: new Map(), units: new Map(), errors: [] };

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
