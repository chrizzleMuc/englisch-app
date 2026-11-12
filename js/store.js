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

// Wird nach jedem Speichern aufgerufen (Online-Abgleich hängt sich hier ein)
let onSave = null;
export function setOnSave(fn) {
  onSave = fn;
}

function writeLocal() {
  try {
    localStorage.setItem(KEY, JSON.stringify(state));
  } catch (e) {
    /* Speicher voll oder blockiert */
  }
}

export function save() {
  state.savedAt = new Date().toISOString();
  writeLocal();
  if (onSave) onSave();
}

// Für den Online-Abgleich: kompletter Stand lesen und (zusammengeführt) zurückschreiben
export function getState() {
  return state;
}
export function replaceState(next) {
  state = { ...blank(), ...next };
  writeLocal();
}

// Einstellungen eines Kindes (Name, Vorlesen, Freischalten) geändert: Zeitstempel fürs Zusammenführen
export function touchPrefs(pid) {
  profile(pid).prefsAt = Date.now();
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
  p.best = p.best || {};
  p.bonus = p.bonus || {};
  p.log = p.log || [];
  p.rewards = p.rewards || [];
  p.rewardsGot = p.rewardsGot || {};
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
  c.at = Date.now();
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

// ---------- Bestehen, Diamanten, Auswertung ----------
export const PASS_DEFAULT = 90;
export function passMark(pid) {
  return Number(profile(pid).pass) || PASS_DEFAULT;
}
export function setPassMark(pid, v) {
  const p = profile(pid);
  p.pass = Number(v);
  p.prefsAt = Date.now();
}

// Diamanten: pro Lektion zählt das beste Ergebnis (höchstens einmal), dazu Tagesboni.
// Gibt zurück, wie viele Diamanten neu dazukommen.
export function awardLesson(pid, unitId, n, diamonds) {
  const p = profile(pid);
  p.best[unitId] = p.best[unitId] || {};
  const before = Number(p.best[unitId][n]) || 0;
  if (diamonds > before) p.best[unitId][n] = diamonds;
  return Math.max(0, diamonds - before);
}
export function awardDailyBonus(pid) {
  const p = profile(pid);
  if (p.bonus[today()]) return 0;
  p.bonus[today()] = 1;
  return 1;
}
export function diamonds(pid) {
  const p = profile(pid);
  let n = Object.keys(p.bonus).length;
  for (const u of Object.values(p.best)) for (const v of Object.values(u)) n += Number(v) || 0;
  return n;
}

// ---------- Belohnungen (von Eltern festgelegt) ----------
export function addReward(pid, at, text) {
  const p = profile(pid);
  p.rewards.push({ id: Date.now().toString(36), at: Number(at), text: String(text).trim().slice(0, 120) });
  p.rewards.sort((a, b) => a.at - b.at);
  p.prefsAt = Date.now();
}
export function removeReward(pid, id) {
  const p = profile(pid);
  p.rewards = p.rewards.filter((r) => r.id !== id);
  p.prefsAt = Date.now();
}
// Neu erreichte Belohnungen (werden als erreicht markiert)
export function newRewards(pid) {
  const p = profile(pid);
  const d = diamonds(pid);
  const got = [];
  for (const r of p.rewards) {
    if (d >= r.at && !p.rewardsGot[r.id]) {
      p.rewardsGot[r.id] = Date.now();
      got.push(r);
    }
  }
  return got;
}

// ---------- Notenspiegel für Proben ----------
export const GRADE_DEFAULT = [95, 80, 65, 50, 25]; // ab so viel % gibt es Note 1, 2, 3, 4, 5; darunter 6
export function gradeScale() {
  const g = state.settings.grades;
  return Array.isArray(g) && g.length === 5 ? g.map(Number) : GRADE_DEFAULT;
}
export function setGradeScale(list) {
  state.settings.grades = list.map(Number);
  state.settings.at = Date.now();
}
export function gradeFor(pct) {
  const g = gradeScale();
  for (let i = 0; i < 5; i++) if (pct >= g[i]) return i + 1;
  return 6;
}

// Falsch angetippte Antwort merken (für die Auswertung im Elternbereich)
export function missPick(pid, id, picked) {
  const p = profile(pid);
  const c = p.cards[id] || (p.cards[id] = { box: 1, due: today(), last: null });
  c.miss = (c.miss || 0) + 1;
  if (picked !== undefined && picked !== null && String(picked).trim()) {
    const k = String(picked).trim().slice(0, 40);
    c.picks = c.picks || {};
    c.picks[k] = (c.picks[k] || 0) + 1;
  }
  c.at = Date.now();
}

// Ein Durchgang einer Lektion (Kind, Datum, Ergebnis, Fehlklicks, Dauer)
export function logAttempt(pid, entry) {
  const p = profile(pid);
  p.log.push({ id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6), at: Date.now(), ...entry });
  if (p.log.length > 400) p.log = p.log.slice(-400);
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
  p.prefsAt = Date.now();
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
  p.prefsAt = Date.now();
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

// Zurücksetzen merkt sich den Zeitpunkt, damit der Online-Abgleich den alten Stand nicht zurückholt
export function resetProfile(pid) {
  const keep = state.profiles[pid] || {};
  state.profiles[pid] = { name: keep.name, voice: keep.voice, pass: keep.pass, prefsAt: keep.prefsAt, resetAt: Date.now() };
  save();
}

export function resetAll() {
  const ids = Object.keys(state.profiles);
  const old = state.profiles;
  state = blank();
  for (const id of ids) state.profiles[id] = { name: old[id].name, voice: old[id].voice, pass: old[id].pass, prefsAt: old[id].prefsAt, resetAt: Date.now() };
  save();
}
