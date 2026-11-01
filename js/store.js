// Fortschritt speichern (auf dem Gerät) sowie Sichern/Laden als Datei.

const KEY = "learnino-v1";

function blank() {
  return { version: 1, profiles: {}, savedAt: null, settings: { repeat: 3, mic: true } };
}

let state = load();

function load() {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) return { ...blank(), ...JSON.parse(raw) };
  } catch (e) {
    /* leer starten */
  }
  return blank();
}

export function save() {
  state.savedAt = new Date().toISOString();
  try {
    localStorage.setItem(KEY, JSON.stringify(state));
  } catch (e) {
    /* Speicher voll oder blockiert */
  }
}

export function profile(id) {
  if (!state.profiles[id]) {
    state.profiles[id] = { name: "", stars: {}, words: {}, streak: { count: 0, last: null, jokerWeek: null } };
  }
  return state.profiles[id];
}

export function wordKey(topicId, en) {
  return topicId + ":" + en;
}

export function recordAnswer(pid, key, correct) {
  const p = profile(pid);
  const w = p.words[key] || { c: 0, w: 0, last: null };
  if (correct) w.c++;
  else w.w++;
  w.last = today();
  p.words[key] = w;
}

export function recordSpoken(pid, key) {
  const p = profile(pid);
  const w = p.words[key] || { c: 0, w: 0, last: null };
  w.s = (w.s || 0) + 1;
  p.words[key] = w;
}

export function lessonStars(pid, topicId, idx) {
  const t = profile(pid).stars[topicId] || {};
  return t[idx] || 0;
}

export function setLessonStars(pid, topicId, idx, stars) {
  const p = profile(pid);
  p.stars[topicId] = p.stars[topicId] || {};
  p.stars[topicId][idx] = Math.max(p.stars[topicId][idx] || 0, stars);
}

export function totalStars(pid) {
  const p = profile(pid);
  let n = 0;
  for (const t of Object.values(p.stars)) for (const s of Object.values(t)) n += s;
  return n;
}

function today() {
  const d = new Date();
  return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
}

function daysBetween(a, b) {
  return Math.round((new Date(b + "T12:00:00") - new Date(a + "T12:00:00")) / 86400000);
}

function weekId(dateStr) {
  const d = new Date(dateStr + "T12:00:00");
  const jan1 = new Date(d.getFullYear(), 0, 1);
  return d.getFullYear() + "-" + Math.ceil(((d - jan1) / 86400000 + jan1.getDay() + 1) / 7);
}

// Tagesserie: Ein verpasster Tag pro Woche wird mit einem Joker überbrückt.
export function touchStreak(pid) {
  const s = profile(pid).streak;
  const t = today();
  if (s.last === t) return s;
  if (!s.last) s.count = 1;
  else {
    const gap = daysBetween(s.last, t);
    if (gap === 1) s.count++;
    else if (gap === 2 && s.jokerWeek !== weekId(t)) {
      s.count++;
      s.jokerWeek = weekId(t);
    } else s.count = 1;
  }
  s.last = t;
  return s;
}

export function streakCount(pid) {
  const s = profile(pid).streak;
  if (!s.last) return 0;
  const gap = daysBetween(s.last, today());
  if (gap <= 1) return s.count;
  if (gap === 2 && s.jokerWeek !== weekId(today())) return s.count;
  return 0;
}

export function exportFile() {
  save();
  const data = JSON.stringify(state, null, 1);
  const name = "learnino-fortschritt-" + today() + ".json";
  return new File([data], name, { type: "application/json" });
}

export function importData(text) {
  const parsed = JSON.parse(text);
  if (!parsed || typeof parsed !== "object" || !parsed.profiles) throw new Error("Keine Learnino-Datei");
  state = { ...blank(), ...parsed };
  save();
}

export function settings() {
  state.settings = { repeat: 3, mic: true, ...(state.settings || {}) };
  return state.settings;
}

export function savedAt() {
  return state.savedAt;
}

export function resetAll() {
  state = blank();
  save();
}
