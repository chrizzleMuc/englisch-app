// Online-Abgleich des Lernstands über Supabase (ohne Zusatz-Bibliothek, nur fetch).
// Ohne Internet läuft alles weiter lokal; beim nächsten Mal mit Internet wird abgeglichen.
// Zusammenführen statt Überschreiben, damit zwei Geräte am selben Tag nichts verlieren:
// pro Aufgabe gewinnt die zuletzt geübte, Lektionen werden vereinigt, Einstellungen nach Zeitstempel.
// Fotos bleiben auf dem Gerät.
import { SUPABASE_URL, SUPABASE_KEY } from "./cloud-config.js";
import * as store from "./store.js";

const SESSION_KEY = "learnino-cloud";
const TABLE = "learnino_state";
const listeners = new Set();
let session = readSession();
let status = { state: "idle", at: null, error: "" };
let timer = null;
let running = null;

export const configured = () => !!(SUPABASE_URL && SUPABASE_KEY);
export const loggedIn = () => !!(session && session.refresh_token);
export const email = () => session?.email || "";
export const getStatus = () => status;
export function onChange(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}
function setStatus(s) {
  status = { ...status, ...s };
  listeners.forEach((fn) => fn(status));
}

function readSession() {
  try {
    return JSON.parse(localStorage.getItem(SESSION_KEY) || "null");
  } catch (e) {
    return null;
  }
}
function writeSession(s) {
  session = s;
  try {
    if (s) localStorage.setItem(SESSION_KEY, JSON.stringify(s));
    else localStorage.removeItem(SESSION_KEY);
  } catch (e) {
    /* blockiert */
  }
}
function fromAuth(j, mail) {
  return {
    access_token: j.access_token,
    refresh_token: j.refresh_token,
    expires_at: Date.now() + (Number(j.expires_in) || 3600) * 1000,
    user_id: j.user?.id || session?.user_id,
    email: j.user?.email || mail || session?.email || ""
  };
}

async function api(path, opts = {}) {
  const res = await fetch(SUPABASE_URL.replace(/\/$/, "") + path, {
    ...opts,
    headers: { apikey: SUPABASE_KEY, "Content-Type": "application/json", ...(opts.headers || {}) }
  });
  const text = await res.text();
  let body = null;
  try {
    body = text ? JSON.parse(text) : null;
  } catch (e) {
    body = text;
  }
  if (!res.ok) {
    const msg = body?.msg || body?.message || body?.error_description || body?.error || res.status;
    const err = new Error(String(msg));
    err.status = res.status;
    throw err;
  }
  return body;
}

// ---------- Anmeldung ----------
const appUrl = () => location.origin + location.pathname;

export async function sendLink(mail) {
  await api(`/auth/v1/otp?redirect_to=${encodeURIComponent(appUrl())}`, {
    method: "POST",
    body: JSON.stringify({ email: mail, create_user: true })
  });
  writeSession({ ...(session || {}), email: mail, refresh_token: null });
}

// Falls die E-Mail einen Zahlencode enthält, kann man ihn direkt in der App eingeben
export async function verifyCode(mail, code) {
  const j = await api("/auth/v1/verify", { method: "POST", body: JSON.stringify({ type: "email", email: mail, token: code }) });
  writeSession(fromAuth(j, mail));
  return sync();
}

// Anmelde-Link aus der E-Mail: Die Zugangsdaten stehen hinter dem # in der Adresse
export function handleRedirect() {
  if (!location.hash.includes("access_token=") && !location.hash.includes("error")) return null;
  const h = new URLSearchParams(location.hash.slice(1));
  history.replaceState(null, "", location.pathname + location.search);
  if (h.get("error")) return { ok: false, message: h.get("error_description") || h.get("error") };
  let uid = null;
  let mail = session?.email || "";
  try {
    const payload = JSON.parse(atob(h.get("access_token").split(".")[1].replace(/-/g, "+").replace(/_/g, "/")));
    uid = payload.sub;
    mail = payload.email || mail;
  } catch (e) {
    /* egal, kommt beim Abgleich */
  }
  writeSession({
    access_token: h.get("access_token"),
    refresh_token: h.get("refresh_token"),
    expires_at: Date.now() + (Number(h.get("expires_in")) || 3600) * 1000,
    user_id: uid,
    email: mail
  });
  return { ok: true, message: "Angemeldet als " + mail };
}

export function logout() {
  const t = session?.access_token;
  writeSession(null);
  setStatus({ state: "idle", error: "" });
  if (t) api("/auth/v1/logout", { method: "POST", headers: { Authorization: "Bearer " + t } }).catch(() => {});
}

async function token() {
  if (!loggedIn()) throw new Error("Nicht angemeldet");
  if (session.access_token && Date.now() < session.expires_at - 60000) return session.access_token;
  try {
    const j = await api("/auth/v1/token?grant_type=refresh_token", { method: "POST", body: JSON.stringify({ refresh_token: session.refresh_token }) });
    writeSession(fromAuth(j));
  } catch (e) {
    // Abgelaufene oder ungültige Anmeldung: neu anmelden nötig (Netzfehler dagegen nicht)
    if (e.status === 400 || e.status === 401) writeSession({ email: session.email, refresh_token: null });
    throw e;
  }
  return session.access_token;
}

// ---------- Zusammenführen ----------
const num = (x) => Number(x) || 0;
function cardTime(c) {
  return num(c.at) || (c.last ? new Date(c.last + "T12:00:00").getTime() : 0);
}

function mergeProfile(a = {}, b = {}) {
  const resetAt = Math.max(num(a.resetAt), num(b.resetAt));
  const fresh = (p) => num(p.resetAt) === resetAt; // Stand nach dem letzten Zurücksetzen
  const prefs = num(b.prefsAt) > num(a.prefsAt) ? b : a;
  const out = { ...a, ...b };
  for (const k of ["name", "voice", "pass", "rewards", "on", "off", "redo", "prefsAt"]) if (prefs[k] !== undefined) out[k] = prefs[k];
  out.resetAt = resetAt || undefined;

  // Aufgaben: die zuletzt geübte Fassung gewinnt; vor dem Zurücksetzen Geübtes fällt weg
  const cards = {};
  for (const src of [a.cards || {}, b.cards || {}]) {
    for (const [id, c] of Object.entries(src)) {
      if (resetAt && cardTime(c) < resetAt) continue;
      if (!cards[id] || cardTime(c) > cardTime(cards[id])) cards[id] = c;
    }
  }
  out.cards = cards;

  // Lektionen: vereinigen (nur Stände nach dem letzten Zurücksetzen)
  const lessons = {};
  for (const src of [a, b].filter(fresh).map((p) => p.lessons || {})) {
    for (const [u, list] of Object.entries(src)) {
      lessons[u] = lessons[u] || [];
      (list || []).forEach((v, i) => v && (lessons[u][i] = true));
    }
  }
  out.lessons = lessons;

  // Diamanten: bestes Ergebnis pro Lektion, Tagesboni vereinigen (nur nach dem letzten Zurücksetzen)
  const best = {};
  const bonus = {};
  for (const src of [a, b].filter(fresh)) {
    for (const [u, m] of Object.entries(src.best || {})) {
      best[u] = best[u] || {};
      for (const [n, v] of Object.entries(m || {})) best[u][n] = Math.max(num(best[u][n]), num(v));
    }
    Object.assign(bonus, src.bonus || {});
  }
  const rewardsGot = {};
  for (const src of [a, b].filter(fresh)) Object.assign(rewardsGot, src.rewardsGot || {});
  out.rewardsGot = rewardsGot;
  out.best = best;
  out.bonus = bonus;

  // Durchgänge (Auswertung): vereinigen, doppelte weg, die neuesten 400
  const seen = new Map();
  for (const x of [...(a.log || []), ...(b.log || [])]) if (x && x.id && num(x.at) >= resetAt) seen.set(x.id, x);
  out.log = [...seen.values()].sort((x, y) => x.at - y.at).slice(-400);

  // Tagesserie: die mit dem späteren Tag
  const sa = fresh(a) ? a.streak : null;
  const sb = fresh(b) ? b.streak : null;
  out.streak = !sa ? sb : !sb ? sa : (sb.last || "") > (sa.last || "") || ((sb.last || "") === (sa.last || "") && num(sb.count) > num(sa.count)) ? sb : sa;
  if (!out.streak) delete out.streak;
  return out;
}

export function merge(local, remote) {
  if (!remote || !remote.profiles) return local;
  const ids = new Set([...Object.keys(local.profiles || {}), ...Object.keys(remote.profiles || {})]);
  const profiles = {};
  for (const id of ids) profiles[id] = mergeProfile(remote.profiles[id], local.profiles?.[id]);
  const newer = (remote.savedAt || "") > (local.savedAt || "") ? remote : local;
  return { ...local, profiles, settings: num(remote.settings?.at) > num(local.settings?.at) ? { ...(local.settings || {}), ...remote.settings } : { ...(remote.settings || {}), ...(local.settings || {}) }, savedAt: newer.savedAt };
}

// ---------- Abgleich ----------
export function sync() {
  if (!configured() || !loggedIn()) return Promise.resolve(false);
  if (running) return running;
  running = (async () => {
    setStatus({ state: "busy", error: "" });
    try {
      const t = await token();
      const auth = { Authorization: "Bearer " + t };
      const rows = await api(`/rest/v1/${TABLE}?select=data,updated_at`, { headers: auth });
      const before = JSON.stringify(store.getState().profiles);
      const merged = merge(store.getState(), rows?.[0]?.data);
      const changed = JSON.stringify(merged.profiles) !== before;
      store.replaceState(merged);
      await api(`/rest/v1/${TABLE}?on_conflict=user_id`, {
        method: "POST",
        headers: { ...auth, Prefer: "resolution=merge-duplicates,return=minimal" },
        body: JSON.stringify([{ user_id: session.user_id, data: merged, updated_at: new Date().toISOString() }])
      });
      setStatus({ state: "ok", at: new Date().toISOString(), changed });
      return true;
    } catch (e) {
      const offline = !navigator.onLine || e instanceof TypeError;
      setStatus({ state: offline ? "offline" : "error", error: offline ? "Kein Internet. Wird später abgeglichen." : e.message });
      return false;
    } finally {
      running = null;
    }
  })();
  return running;
}

// Nach dem Speichern kurz warten und dann abgleichen (mehrere Antworten = ein Abgleich)
export function schedule(ms = 4000) {
  if (!configured() || !loggedIn()) return;
  clearTimeout(timer);
  timer = setTimeout(sync, ms);
}

export function start() {
  if (!configured()) return;
  // Solange die App offen ist: jede Minute neuen Stand von anderen Geräten holen
  setInterval(() => {
    if (document.visibilityState === "visible" && loggedIn() && navigator.onLine) sync();
  }, 60000);
  store.setOnSave(() => schedule());
  window.addEventListener("online", () => schedule(500));
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden" && timer) {
      clearTimeout(timer);
      timer = null;
      sync();
    } else if (document.visibilityState === "visible") schedule(500);
  });
}
