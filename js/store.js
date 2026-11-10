// Fortschritt speichern (nur auf diesem Gerät) sowie Sichern/Laden als Datei.

const KEY = "learnino-v2";
const OLD_KEY = "learnino-v1";

// Lernkartei: nach wie vielen Tagen ein Inhalt in Kasten 1 bis 5 wiederkommt
export const BOX_DAYS = [0, 1, 2, 4, 7, 14];

function blank() {
  return { version: 2, profiles: {}, savedAt: null, settings: {} };
}

let state = load();

function load() {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) return { ...blank(), ...JSON.parse(raw) };
    // Umzug von Version 1: Profilbild, Name und Tagesserie bleiben, Lernstand startet neu
    const old = localStorage.getItem(OLD_KEY);
    if (old) {
      const o = JSON.parse(old);
      const s = blank();
      for (const [id, p] of Object.entries(o.profiles || {})) {
        s.profiles[id] = { name: p.name || "", avatar: p.avatar ? { base: p.avatar.base, color: p.avatar.color } : null, streak: p.streak };
      }
      return s;
    }
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
  const p = (state.profiles[id] = state.profiles[id] || {});
  p.name = p.name || "";
  p.cards = p.cards || {};
  p.lessons = p.lessons || {};
  p.off = p.off || {};
  p.on = p.on || {};
  p.redo = p.redo || {};
  p.streak = p.streak || { count: 0, last: null, jokerWeek: null };
  return p;
}

export function today() {
  const d = new Date();
  return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
}

function addDays(dateStr, n) {
  const d = new Date(dateStr + "T12:00:00");
  d.setDate(d.getDate() + n);
  return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
}

function daysBetween(a, b) {
  return Math.round((new Date(b + "T12:00:00") - new Date(a + "T12:00:00")) / 86400000);
}

// ---------- Lernkartei ----------
export function card(pid, id) {
  return profile(pid).cards[id] || null;
}

// Neuer Inhalt kommt in Kasten 1, morgen wieder dran
export function introduce(pid, id) {
  const p = profile(pid);
  if (!p.cards[id]) p.cards[id] = { box: 1, due: addDays(today(), BOX_DAYS[1]), last: today() };
}

// Richtig: einen Kasten weiter (höchstens einmal pro Tag). Falsch: zurück in Kasten 1.
// Wer mindestens zweimal falsch war, gilt als "Sorgenkind": Es bleibt höchstens in Kasten 2
// (kommt also spätestens alle 2 Tage), bis es dreimal hintereinander richtig war.
export function grade(pid, id, correct) {
  const p = profile(pid);
  const c = p.cards[id] || { box: 1, due: today(), last: null };
  const t = today();
  c.wrong = c.wrong || 0;
  c.run = c.run || 0;
  if (!correct) {
    c.box = 1;
    c.due = addDays(t, BOX_DAYS[1]);
    c.wrong++;
    c.run = 0;
  } else {
    c.run++;
    if (c.run >= 3) c.wrong = 0;
    if (c.due <= t && c.last !== t) {
      c.box = Math.min(isTrouble(c) ? 2 : 5, c.box + 1);
      c.due = addDays(t, BOX_DAYS[c.box]);
    }
  }
  c.last = t;
  p.cards[id] = c;
}

export function isTrouble(c) {
  return !!c && (c.wrong || 0) >= 2;
}

export function troubleCards(pid) {
  return Object.entries(profile(pid).cards)
    .filter(([, c]) => isTrouble(c))
    .sort((a, b) => b[1].wrong - a[1].wrong)
    .map(([id, c]) => ({ id, ...c }));
}

export function dueCards(pid) {
  const t = today();
  return Object.entries(profile(pid).cards)
    .filter(([, c]) => c.due <= t)
    .sort((a, b) => a[1].box - b[1].box || a[1].due.localeCompare(b[1].due))
    .map(([id]) => id);
}

// ---------- Lektionen ----------
export function lessonDone(pid, unitId, n) {
  return !!(profile(pid).lessons[unitId] || [])[n];
}

export function setLessonDone(pid, unitId, n) {
  const p = profile(pid);
  p.lessons[unitId] = p.lessons[unitId] || [];
  p.lessons[unitId][n] = true;
}

export function totalStars(pid) {
  return Object.values(profile(pid).lessons).reduce((n, l) => n + l.filter(Boolean).length, 0);
}

// ---------- Freischalten (Standard: an, außer der Inhalt ist für das Kind nicht vorgesehen) ----------
export function isEnabled(pid, id, byDefault = true) {
  const p = profile(pid);
  if (p.off[id]) return false;
  if (p.on[id]) return true;
  return byDefault;
}

export function setEnabled(pid, id, on) {
  const p = profile(pid);
  if (on) {
    delete p.off[id];
    p.on[id] = true;
  } else {
    p.off[id] = true;
    delete p.on[id];
  }
}

// ---------- Foto-Aufgaben, die Eltern mit "nochmal" zurückgegeben haben ----------
export function setRedo(pid, taskId, on) {
  const p = profile(pid);
  if (on) p.redo[taskId] = today();
  else delete p.redo[taskId];
}

export function redoTasks(pid) {
  return Object.keys(profile(pid).redo);
}

// ---------- Tagesserie (ein Joker pro Woche) ----------
function weekId(dateStr) {
  const d = new Date(dateStr + "T12:00:00");
  const jan1 = new Date(d.getFullYear(), 0, 1);
  return d.getFullYear() + "-" + Math.ceil(((d - jan1) / 86400000 + jan1.getDay() + 1) / 7);
}

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

// ---------- Sichern / Laden ----------
export function exportFile() {
  save();
  return new File([JSON.stringify(state, null, 1)], "learnino-fortschritt-" + today() + ".json", { type: "application/json" });
}

export function importData(text) {
  const parsed = JSON.parse(text);
  if (!parsed || typeof parsed !== "object" || !parsed.profiles) throw new Error("Keine Learnino-Datei");
  if ((parsed.version || 1) < 2) throw new Error("Alte Version");
  state = { ...blank(), ...parsed };
  save();
}

export function savedAt() {
  return state.savedAt;
}

export function resetAll() {
  state = blank();
  save();
}
