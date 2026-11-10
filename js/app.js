import { PROFILES, TEST_PROFILE, PRAISE, PRAISE_EN, LESSONS, SPEAKERS } from "./data.js";
import { sayParts, sayEn, sayDe, chime, voiceInfo, setGerman } from "./speech.js";
import { play, promptAnd, stopAudio } from "./audio.js";
import { canRecord, record, playUrl } from "./recorder.js";
import { content, loadContent } from "./content.js";
import * as store from "./store.js";
import * as photos from "./photos.js";
import { pic } from "./pics.js";

const APP_VERSION = 16;
const app = document.getElementById("app");
const current = { profile: null, subject: null, screen: null };

// ---------- Hilfsfunktionen ----------
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const shuffle = (a) => {
  a = a.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
};
const pick = (a) => a[Math.floor(Math.random() * a.length)];
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
const prof = () => [...PROFILES, TEST_PROFILE].find((p) => p.id === current.profile);
const isTestUser = () => current.profile === TEST_PROFILE.id;
const item = (id) => content.items.get(id);
const unitById = (id) => content.units.get(id);

// Vorlesen der Aufgaben (Deutsch): "auto" = wird vorgelesen, "selbst" = erst selbst lesen,
// 🔊 wird nach ein paar Sekunden freigegeben, "aus" = keine deutsche Stimme.
const VOICE_DEFAULT = { entdecker: "auto" };
const VOICE_WAIT_MS = 6000;
function voiceMode(pid = current.profile) {
  if (!pid) return "aus";
  return store.profile(pid).voice || VOICE_DEFAULT[pid] || "aus";
}

function render(html) {
  stopAudio();
  setGerman(voiceMode() !== "aus");
  current.screen = {};
  app.innerHTML = html;
  window.scrollTo(0, 0);
  return current.screen;
}
const alive = (token) => current.screen === token;

function on(sel, ev, fn) {
  app.querySelectorAll(sel).forEach((el) => el.addEventListener(ev, fn));
}
const $ = (id) => document.getElementById(id);

// ---------- Profilauswahl ----------
function showProfiles() {
  current.profile = null;
  current.subject = null;
  render(`
    <div class="screen center">
      <h1 class="logo">Learnino</h1>
      <p class="sub">Wer lernt heute?</p>
      <div class="profiles">
        ${PROFILES.map((p) => `<button class="profile-card" data-id="${p.id}">
            <span class="pname">${esc(p.title)}</span>
            <span class="small">⭐ ${store.totalStars(p.id)}</span>
          </button>`).join("")}
      </div>
      <button class="link-btn" id="parents">🔒 Elternbereich</button>
    </div>`);
  on(".profile-card", "click", (e) => {
    current.profile = e.currentTarget.dataset.id;
    chime("pop");
    showHome();
  });
  $("parents").onclick = showParentGate;
}

// ---------- Freigeschaltete Inhalte ----------
const stageDefault = (pid, st) => pid === TEST_PROFILE.id || !st.kinder || st.kinder.includes(pid);

function stagesFor(pid, sub) {
  return sub.stages
    .filter((st) => store.isEnabled(pid, st.id, stageDefault(pid, st)))
    .map((st) => ({ ...st, units: st.units.filter((u) => store.isEnabled(pid, u.id)) }))
    .filter((st) => st.units.length);
}

function subjectsFor(pid) {
  return content.subjects.filter((s) => store.isEnabled(pid, s.id) && stagesFor(pid, s).length);
}

const isSchool = (u) => u.type === "schule";
const unitIds = (u) => (isSchool(u) ? u.singles.map((q) => q.id) : u.words.map((w) => w.id));
const lessonsOf = (u) => (isSchool(u) ? u.lessons : LESSONS);

function unitMastered(pid, unit) {
  const ids = unitIds(unit);
  return ids.length > 0 && ids.every((id) => (store.card(pid, id)?.box || 0) >= 3);
}

function homeHeader(p) {
  return `<header class="bar">
        <button class="icon-btn back-btn" id="back" aria-label="Zurück"><span class="back-arrow">←</span> Zurück</button>
        <span class="who">${p.test ? `<span class="test-badge">🧪 Test</span>` : esc(p.title)}</span>
        <span class="stat">🔥 ${store.streakCount(p.id)}</span>
        <span class="stat">⭐ ${store.totalStars(p.id)}</span>
      </header>`;
}

function showHome(subjectId = current.subject) {
  const p = prof();
  const subs = subjectsFor(p.id);
  let sub = subs.find((x) => x.id === subjectId) || (subs.length === 1 ? subs[0] : null);
  if (!sub) return showSubjects(subs);
  current.subject = sub.id;
  const many = subs.length > 1;
  render(`
    <div class="screen">
      ${homeHeader(p)}
      ${many ? `<h2 class="subject-title">${esc(sub.title)}</h2>` : ""}
      ${stagesFor(p.id, sub).map((st) => `
        <h3 class="stage-title">${esc(st.title)}</h3>
        <div class="topics">
          ${st.units.map((u) => {
            const nl = lessonsOf(u).length;
            const done = lessonsOf(u).filter((_, n) => store.lessonDone(p.id, u.id, n)).length;
            return `<button class="topic" data-id="${u.id}" style="--c:${u.color}">
              ${unitMastered(p.id, u) ? `<span class="badge">🏆</span>` : ""}
              <span class="tname">${esc(u.title_de)}</span>
              <span class="dots small-dots">${Array.from({ length: nl }, (_, n) => `<span class="dot ${n < done ? "on" : ""}"></span>`).join("")}</span>
            </button>`;
          }).join("")}
        </div>`).join("")}
      ${stagesFor(p.id, sub).some((st) => st.units.some((u) => u.words.length)) ? `<button class="wide-btn album-btn" id="album">📒 Mein Sticker-Album</button>` : ""}
    </div>`);
  $("back").onclick = () => (many ? showSubjects(subs) : showProfiles());
  if ($("album")) $("album").onclick = showAlbum;
  on(".topic[data-id]", "click", (e) => {
    chime("pop");
    showUnit(e.currentTarget.dataset.id);
  });
  if (voiceMode() === "auto") sayDe("Such dir ein Thema aus!");
}

function showSubjects(subs) {
  const p = prof();
  current.subject = null;
  render(`
    <div class="screen">
      ${homeHeader(p)}
      ${subs.length ? `<div class="topics">
        ${subs.map((x) => `<button class="topic subject" data-id="${x.id}" style="--c:${x.color}">
<span class="tname">${esc(x.title)}</span></button>`).join("")}
      </div>` : `<p class="sub center-text">Hier ist noch nichts freigeschaltet. Frag Mama oder Papa!</p>`}
    </div>`);
  $("back").onclick = showProfiles;
  on(".subject", "click", (e) => showHome(e.currentTarget.dataset.id));
  if (voiceMode() === "auto") sayDe(subs.length ? "Was willst du heute lernen?" : "Hier ist noch nichts freigeschaltet.");
}

// ---------- Einheit mit 5 Lektionen ----------
function showUnit(unitId) {
  const u = unitById(unitId);
  const pid = current.profile;
  const sub = content.subjects.find((x) => x.id === u.subject);
  const lessons = lessonsOf(u);
  const isOpen = (i) => isSchool(u) || isTestUser() || i === 0 || store.lessonDone(pid, u.id, i - 1);
  const cur = lessons.findIndex((_, i) => isOpen(i) && !store.lessonDone(pid, u.id, i));
  // Pfad schlängelt sich wie eine Treppe nach links und rechts
  const sway = [0, -70, -105, -70, 0, 70, 105, 70];
  render(`
    <div class="screen unit-screen">
      <header class="bar">
        <button class="icon-btn back-btn" id="back" aria-label="Zurück"><span class="back-arrow">←</span> Zurück</button>
        <span class="who"></span>
        ${unitMastered(pid, u) ? `<span class="stat">🏆</span>` : ""}
      </header>
      <div class="unit-card">
        <small>${esc(sub ? sub.title : "")}</small>
        <b>${esc(u.title_de)}</b>
      </div>
      <div class="path">
        ${lessons.map((l, i) => {
          const open = isOpen(i);
          const done = store.lessonDone(pid, u.id, i);
          const last = i === lessons.length - 1;
          const state = !open ? "locked" : i === cur ? "cur" : done ? "done" : "open";
          const sym = !open ? "🔒" : done ? "✓" : last ? "🏆" : "★";
          return `<div class="step" style="--x:${sway[i % sway.length]}px">
            ${state === "cur" ? `<span class="go-bubble">${done ? "NOCHMAL" : i === 0 ? "LOS GEHT'S" : "WEITER"}</span>` : ""}
            <button class="node ${state}" data-i="${i}" ${open ? "" : "disabled"} aria-label="${esc(l.title)}">
              <span class="node-pics">${sym}</span>
            </button>
            <span class="node-label">${esc(l.title)}</span>
          </div>`;
        }).join("")}
      </div>
    </div>`);
  $("back").onclick = () => showHome();
  on(".node:not(.locked)", "click", (e) => startLesson(u.id, +e.currentTarget.dataset.i));
}

// ---------- Lektionen zusammenstellen ----------
function reviewSteps(pid, subject) {
  // Jede Sitzung beginnt mit höchstens 5 fälligen Inhalten aus der Lernkartei (nur aus demselben Fach)
  const inSubject = (unitId) => unitById(unitId) && unitById(unitId).subject === subject && store.isEnabled(pid, unitId);
  const steps = store
    .dueCards(pid)
    .filter((id) => item(id) && inSubject(item(id).unit))
    .slice(0, 5)
    .map((id) => {
      const it = item(id);
      if (it.kind === "task") return { ...singleStep(it.q), review: true, unit: it.unit };
      return { kind: it.kind === "word" ? "listen" : "phrasePic", id, review: true, unit: it.unit };
    });
  // Foto-Aufgaben, bei denen die Eltern "nochmal" gesagt haben
  for (const tid of store.redoTasks(pid)) {
    const t = content.photoTasks.get(tid);
    if (t && inSubject(t.unit)) steps.push({ kind: "photo", t, review: true, unit: t.unit });
  }
  return steps;
}

function buildLesson(u, n) {
  if (isSchool(u)) return buildSchoolLesson(u, n);
  const words = u.words.map((w) => w.id);
  const phrases = u.phrases.map((p) => p.id);
  const steps = [];
  if (n === 0) {
    steps.push({ kind: "explore", ids: words, introduce: true });
    shuffle(words).forEach((id) => steps.push({ kind: "listen", id }));
  } else if (n === 1) {
    steps.push({ kind: "memory", ids: shuffle(words).slice(0, 4) });
    shuffle(words).slice(0, 4).forEach((id) => steps.push({ kind: "listen", id }));
    steps.push({ kind: "missing" }, { kind: "missing" });
  } else if (n === 2) {
    steps.push({ kind: "explore", ids: phrases, introduce: true, phrases: true });
    shuffle(phrases).forEach((id) => steps.push({ kind: "phrasePic", id }));
    phrases.forEach((id) => steps.push({ kind: item(id).action ? "action" : "repeat", id }));
  } else if (n === 3) {
    if (u.story.length) steps.push({ kind: "story" });
    u.questions.forEach((q) => steps.push({ kind: "question", q }));
  } else {
    if (u.rhyme?.lines?.length) steps.push({ kind: "rhyme" });
    const quiz = [
      ...shuffle(words).slice(0, 4).map((id) => ({ kind: "listen", id })),
      ...shuffle(phrases).slice(0, 2).map((id) => ({ kind: "phrasePic", id }))
    ];
    const act = u.phrases.find((p) => p.action);
    if (act) quiz.push({ kind: "action", id: act.id });
    steps.push(...shuffle(quiz));
  }
  return steps.map((s) => ({ unit: u.id, ...s }));
}

function startLesson(unitId, n) {
  const u = unitById(unitId);
  const school = isSchool(u);
  const isTest = school && !!u.lessons[n].test;
  const review = isTest ? [] : reviewSteps(current.profile, u.subject);
  const steps = [...review, ...buildLesson(u, n)];
  const lesson = { u, n, steps, pos: 0, reviewCount: review.length, school, isTest, right: 0, total: 0, missed: [] };
  nextStep(lesson);
}

function lessonFrame(lesson, inner) {
  const pct = Math.round((lesson.pos / lesson.steps.length) * 100);
  const step = lesson.steps[lesson.pos];
  return `
    <div class="screen lesson" style="--c:${unitById(step?.unit || lesson.u.id).color}">
      <header class="bar">
        <button class="icon-btn" id="quit" aria-label="Beenden">✖</button>
        <div class="progress"><span style="width:${pct}%"></span></div>
      </header>
      ${step?.review ? `<p class="review-tag">🔁 Wiederholung</p>` : step?.retry ? `<p class="review-tag">🔁 Nochmal, weil es vorhin nicht geklappt hat</p>` : ""}
      ${inner}
    </div>`;
}

function lessonRender(lesson, inner) {
  const token = render(lessonFrame(lesson, inner));
  $("quit").onclick = () => showUnit(lesson.u.id);
  return token;
}

const STEPS = {};
function nextStep(lesson) {
  if (lesson.pos >= lesson.steps.length) return finishLesson(lesson);
  const step = lesson.steps[lesson.pos];
  STEPS[step.kind](lesson, step);
}
function advance(lesson) {
  if (lesson.school && voiceMode() === "selbst" && current.screen && !current.screen.heard) lesson.selfRead = (lesson.selfRead || 0) + 1;
  lesson.pos++;
  nextStep(lesson);
}

function nextBtn(label = "Weiter ➜", disabled = false) {
  return `<button class="go-btn" id="next" ${disabled ? "disabled" : ""}>${label}</button>`;
}

// ---------- Übung: Entdecken (Bilder antippen und hören) ----------
STEPS.explore = (lesson, step) => {
  const pid = current.profile;
  const heard = new Set();
  lessonRender(lesson, `
    <p class="task">Tipp auf jedes Bild und hör gut zu!</p>
    <div class="explore">
      ${step.ids.map((id) => `<button class="choice exp" data-id="${id}"><span class="${step.phrases ? "mid-pic" : "huge-pic"}">${pic(item(id).image)}</span><span class="check">✓</span></button>`).join("")}
    </div>
    ${nextBtn("Weiter ➜", true)}`);
  on(".exp", "click", async (e) => {
    const el = e.currentTarget;
    const id = el.dataset.id;
    app.querySelectorAll(".exp").forEach((b) => b.classList.remove("sel"));
    el.classList.add("sel", "heard");
    heard.add(id);
    if (heard.size === step.ids.length) $("next").disabled = false;
    await play(item(id));
  });
  $("next").onclick = () => {
    if (step.introduce) step.ids.forEach((id) => store.introduce(pid, id));
    store.save();
    advance(lesson);
  };
  sayDe("Tipp auf jedes Bild und hör gut zu!");
};

// ---------- Gemeinsame Auswahl-Logik ----------
// Falsche Antwort: freundlicher Hinweis, Audio nochmal, neuer Versuch. Bewertet wird nur der erste Versuch.
function choose(lesson, step, { task, prompt = "", options, correctId, speak, grade = true, big = true }) {
  const token = lessonRender(lesson, `
    <p class="task">${task}</p>
    ${prompt}
    <div class="choices n${options.length}">
      ${options.map((o) => `<button class="choice" data-id="${o.id}"><span class="${big ? "huge-pic" : "mid-pic"}">${pic(o.image)}</span></button>`).join("")}
    </div>
    <div class="feedback" id="fb"></div>`);
  on(".again", "click", () => speak());
  let first = true;
  let locked = false;
  on(".choice", "click", async (e) => {
    if (locked) return;
    const el = e.currentTarget;
    if (el.dataset.id === correctId) {
      locked = true;
      el.classList.add("right");
      chime("good");
      $("fb").innerHTML = `<span class="ok">${pick(PRAISE)}</span>`;
      if (grade) store.grade(current.profile, correctId, first);
      store.save();
      await play(item(correctId) || { en: "" });
      await wait(350);
      if (alive(token)) advance(lesson);
    } else {
      first = false;
      el.classList.add("wrong");
      el.disabled = true;
      chime("bad");
      $("fb").innerHTML = `<span class="try">Fast! Hör nochmal genau hin.</span>`;
      await wait(400);
      if (alive(token)) speak();
    }
  });
  setTimeout(() => alive(token) && speak(), 250);
}

function wordDistractors(unitId, id, n) {
  const u = unitById(unitId);
  return shuffle(u.words.filter((w) => w.id !== id)).slice(0, n);
}

function phraseDistractors(unitId, id, n) {
  const own = unitById(unitId).phrases.filter((p) => p.id !== id && p.image !== item(id).image);
  const others = [...content.items.values()].filter((x) => x.kind === "phrase" && x.unit !== unitId && x.image !== item(id).image);
  const pool = [...shuffle(own), ...shuffle(others)];
  const out = [];
  for (const p of pool) if (out.length < n && !out.some((o) => o.image === p.image)) out.push(p);
  return out;
}

// ---------- Übung: Hören → Bild antippen ----------
STEPS.listen = (lesson, step) => {
  const it = item(step.id);
  const options = shuffle([it, ...wordDistractors(step.unit, step.id, 3)]);
  choose(lesson, step, {
    task: "Hör zu und tipp das richtige Bild!",
    prompt: `<div class="row"><button class="speaker big again" aria-label="Nochmal hören">🔊</button></div>`,
    options,
    correctId: it.id,
    speak: () => promptAnd("Wo ist", it)
  });
};

// ---------- Übung: Satz hören → Bild wählen ----------
STEPS.phrasePic = (lesson, step) => {
  const it = item(step.id);
  const options = shuffle([it, ...phraseDistractors(step.unit, step.id, 2)]);
  choose(lesson, step, {
    task: "Welches Bild passt zum Satz?",
    prompt: `<div class="row"><button class="speaker big again" aria-label="Nochmal hören">🔊</button></div>`,
    options,
    correctId: it.id,
    speak: () => play(it),
    big: false
  });
};

// ---------- Übung: Memory (Bild + Ton) ----------
STEPS.memory = (lesson, step) => {
  const pairs = step.ids.map(item);
  const cards = shuffle(pairs.flatMap((it) => [{ it, face: "pic" }, { it, face: "sound" }]));
  let open = [];
  let found = 0;
  const token = lessonRender(lesson, `
    <p class="task">Memory: Finde Bild und Ton, die zusammengehören!</p>
    <div class="memory">
      ${cards.map((c, i) => `<button class="mcard" data-i="${i}"><span class="back">?</span><span class="front">${c.face === "pic" ? pic(c.it.image) : "🔊"}</span></button>`).join("")}
    </div>
    <div class="feedback" id="fb"></div>`);
  sayDe("Finde Bild und Ton, die zusammengehören!");
  on(".mcard", "click", async (e) => {
    const el = e.currentTarget;
    const c = cards[+el.dataset.i];
    if (el.classList.contains("flip") || open.length === 2) return;
    el.classList.add("flip");
    play(c.it);
    open.push({ el, c });
    if (open.length < 2) return;
    const [a, b] = open;
    if (a.c.it.id === b.c.it.id) {
      await wait(600);
      chime("good");
      a.el.classList.add("done");
      b.el.classList.add("done");
      open = [];
      if (++found === pairs.length) {
        $("fb").innerHTML = `<span class="ok">${pick(PRAISE)}</span>`;
        chime("win");
        await wait(1200);
        if (alive(token)) advance(lesson);
      }
    } else {
      await wait(1400);
      a.el.classList.remove("flip");
      b.el.classList.remove("flip");
      open = [];
    }
  });
};

// ---------- Übung: Was fehlt? ----------
STEPS.missing = async (lesson, step) => {
  const u = unitById(step.unit);
  const set = shuffle(u.words).slice(0, 4);
  const gone = pick(set);
  const rest = set.filter((x) => x !== gone);
  const others = shuffle(u.words.filter((w) => !set.includes(w))).slice(0, 2);
  const token = lessonRender(lesson, `
    <p class="task">Was fehlt? Schau dir die Bilder gut an!</p>
    <div class="missing-row" id="row">${set.map((w) => `<span class="mpic">${pic(w.image)}</span>`).join("")}</div>
    <div id="area"></div>`);
  await sayDe("Schau dir die Bilder gut an!");
  for (const w of set) {
    if (!alive(token)) return;
    await play(w);
    await wait(250);
  }
  await wait(600);
  if (!alive(token)) return;
  $("row").classList.add("closed");
  await sayDe("Augen zu!");
  await wait(900);
  if (!alive(token)) return;
  $("row").classList.remove("closed");
  $("row").innerHTML = rest.map((w) => `<span class="mpic">${pic(w.image)}</span>`).join("") + `<span class="mpic gap">❓</span>`;
  const options = shuffle([gone, ...others]);
  $("area").innerHTML = `<p class="task">Was fehlt?</p><div class="choices n${options.length}">${options.map((o) => `<button class="choice" data-id="${o.id}"><span class="huge-pic">${pic(o.image)}</span></button>`).join("")}</div><div class="feedback" id="fb"></div>`;
  sayDe("Was fehlt?");
  let first = true;
  on(".choice", "click", async (e) => {
    const el = e.currentTarget;
    if (el.dataset.id === gone.id) {
      el.classList.add("right");
      chime("good");
      $("fb").innerHTML = `<span class="ok">${pick(PRAISE)}</span>`;
      store.grade(current.profile, gone.id, first);
      app.querySelector(".gap").innerHTML = pic(gone.image);
      await play(gone);
      await wait(400);
      if (alive(token)) advance(lesson);
    } else {
      first = false;
      el.classList.add("wrong");
      el.disabled = true;
      chime("bad");
      $("fb").innerHTML = `<span class="try">Fast! Versuch es nochmal.</span>`;
    }
  });
};

// ---------- Übung: Nachsprechen mit Selbstvergleich ----------
STEPS.repeat = (lesson, step) => {
  const it = item(step.id);
  const mic = canRecord();
  let myUrl = null;
  let busy = false;
  const token = lessonRender(lesson, `
    <p class="task">Hör zu und sprich nach!</p>
    <div class="learn-card"><span class="huge-pic">${pic(it.image)}</span></div>
    <div class="row compare">
      <div class="cmp"><button class="speaker big" id="orig" aria-label="Original">🔊</button><span class="small">Original</span></div>
      ${mic ? `<div class="cmp"><button class="rec" id="rec" aria-label="Aufnehmen">🎙️<span class="rec-ring"></span></button><span class="small" id="reclabel">Aufnehmen</span></div>
      <div class="cmp"><button class="speaker big me" id="mine" aria-label="Meine Aufnahme" disabled>👂</button><span class="small">Ich</span></div>` : ""}
    </div>
    <div class="feedback" id="fb"></div>
    ${nextBtn("Weiter ➜", mic)}`);
  $("orig").onclick = () => play(it);
  $("next").onclick = () => {
    if (myUrl) URL.revokeObjectURL(myUrl);
    advance(lesson);
  };
  if (mic) {
    let active = null;
    $("rec").onclick = async () => {
      if (active) return active.stop();
      stopAudio();
      const btn = $("rec");
      btn.classList.add("on");
      $("reclabel").textContent = "Sprich jetzt!";
      try {
        active = await record(3500, (f) => btn.style.setProperty("--p", f));
        const url = await active.result;
        active = null;
        if (!alive(token)) return URL.revokeObjectURL(url);
        if (myUrl) URL.revokeObjectURL(myUrl);
        myUrl = url;
        btn.classList.remove("on");
        $("reclabel").textContent = "Nochmal";
        $("mine").disabled = false;
        $("next").disabled = false;
        $("next").classList.add("pulse");
        // Original und eigene Aufnahme direkt nacheinander zum Vergleichen
        await play(it);
        await wait(300);
        if (alive(token)) await playUrl(myUrl);
        if (alive(token)) $("fb").innerHTML = `<span class="ok">Hörst du den Unterschied? Du kannst es nochmal versuchen.</span>`;
      } catch (e) {
        active = null;
        if (!alive(token)) return;
        btn.classList.remove("on");
        $("reclabel").textContent = "Aufnehmen";
        $("fb").innerHTML = `<span class="try">Das Mikrofon ist aus. Sprich einfach laut nach!</span>`;
        $("next").disabled = false;
      }
    };
    $("mine").onclick = () => myUrl && playUrl(myUrl);
  }
  (async () => {
    await sayDe("Hör zu und sprich nach!");
    if (alive(token)) await play(it);
    if (alive(token) && mic) await sayDe("Tipp auf das Mikrofon und sprich!");
  })();
};

// ---------- Übung: Bewegungsaufgabe ----------
STEPS.action = (lesson, step) => {
  const it = item(step.id);
  const token = lessonRender(lesson, `
    <p class="task">Hör zu und mach mit!</p>
    <div class="learn-card action-card"><span class="huge-pic">${pic(it.image)}</span></div>
    <div class="row"><button class="speaker big again" aria-label="Nochmal hören">🔊</button></div>
    ${nextBtn("Geschafft! 💪")}`);
  on(".again", "click", () => play(it));
  $("next").onclick = () => {
    chime("good");
    store.grade(current.profile, it.id, true);
    store.save();
    advance(lesson);
  };
  (async () => {
    await sayDe("Hör zu und mach mit!");
    if (alive(token)) await play(it);
  })();
};

// ---------- Mini-Geschichte ----------
STEPS.story = (lesson, step) => {
  const u = unitById(step.unit);
  let i = 0;
  const token = lessonRender(lesson, `
    <p class="task">Hör dir die Geschichte an!</p>
    <div class="story-card">
      <span class="speaker-pic" id="who"></span>
      <span class="huge-pic" id="scene"></span>
    </div>
    <div class="story-dots">${u.story.map((_, k) => `<span class="dot" data-k="${k}"></span>`).join("")}</div>
    <div class="row">
      <button class="speaker big" id="again" aria-label="Nochmal">🔁</button>
      <button class="go-btn" id="next" disabled>Weiter ➜</button>
    </div>`);
  const show = async () => {
    const line = u.story[i];
    const sp = SPEAKERS[line.speaker] || { pitch: 1.05, pic: "🗣️" };
    $("who").innerHTML = pic(sp.pic);
    $("who").hidden = line.image === sp.pic;
    $("scene").innerHTML = pic(line.image);
    app.querySelectorAll(".story-dots .dot").forEach((d) => d.classList.toggle("on", +d.dataset.k <= i));
    $("next").disabled = true;
    await play(line, { pitch: sp.pitch });
    if (alive(token)) $("next").disabled = false;
  };
  $("again").onclick = show;
  $("next").onclick = () => {
    if (++i >= u.story.length) return advance(lesson);
    show();
  };
  show();
};

// ---------- Verständnisfrage zur Geschichte ----------
STEPS.question = (lesson, step) => {
  const q = step.q;
  const options = shuffle(q.choices.map(item));
  choose(lesson, step, {
    task: "Was war in der Geschichte?",
    prompt: `<div class="row"><button class="speaker big again" aria-label="Frage nochmal">🔊</button></div>`,
    options,
    correctId: q.answer,
    speak: () => play(q),
    grade: false
  });
};

// ---------- Reim zum Mitmachen ----------
STEPS.rhyme = (lesson, step) => {
  const r = unitById(step.unit).rhyme;
  let running = false;
  const token = lessonRender(lesson, `
    <p class="task">Ein Reim! Hör zu, klatsch und sprich mit!</p>
    <div class="learn-card"><span class="huge-pic" id="rpic">${pic(r.lines[0].image)}</span></div>
    <div class="row"><button class="speaker big" id="again" aria-label="Nochmal">🔁</button><button class="speaker big" id="clap" aria-label="Klatschen">👏</button></div>
    ${nextBtn("Weiter ➜", true)}`);
  const run = async () => {
    if (running) return;
    running = true;
    for (const line of r.lines) {
      if (!alive(token)) return;
      $("rpic").innerHTML = pic(line.image);
      $("rpic").classList.remove("bounce");
      void $("rpic").offsetWidth;
      $("rpic").classList.add("bounce");
      await play(line, { pitch: 1.15 });
      await wait(250);
    }
    running = false;
    if (alive(token)) $("next").disabled = false;
  };
  $("again").onclick = run;
  $("clap").onclick = () => chime("pop");
  $("next").onclick = () => advance(lesson);
  (async () => {
    await sayDe("Hör zu und sprich mit!");
    if (alive(token)) run();
  })();
};

// ---------- Ende der Lektion ----------
function finishLesson(lesson) {
  if (lesson.school) return finishSchoolLesson(lesson);
  const pid = current.profile;
  const first = !store.lessonDone(pid, lesson.u.id, lesson.n);
  store.setLessonDone(pid, lesson.u.id, lesson.n);
  const streak = store.touchStreak(pid);
  store.save();
  const isLast = lesson.n === 4;
  render(`
    <div class="screen center result" style="--c:${lesson.u.color}">
      <h2>${pick(PRAISE)}</h2>
      <div class="result-stars"><span class="star on">★</span></div>
      <p class="sub">🔥 ${streak.count} ${streak.count === 1 ? "Tag" : "Tage"} in Folge</p>
      ${isLast && first ? `<p class="sub">Neuer Sticker für dein Album:</p><div class="stickers"><span class="sticker big-sticker">${pic(lesson.u.image)}</span></div>` : ""}
      ${lesson.n === 0 && first ? `<p class="sub">Neue Wörter im Album:</p><div class="stickers">${lesson.u.words.map((w) => `<span class="sticker">${pic(w.image)}</span>`).join("")}</div>` : ""}
      <button class="go-btn" id="next">Weiter ➜</button>
    </div>`);
  chime("win");
  setTimeout(() => sayEn(pick(PRAISE_EN)), 600);
  $("next").onclick = () => showUnit(lesson.u.id);
}

// ================= Schulfächer (Deutsch, Mathe, HSU …) =================
// Aufgabenarten: pairs (Paare finden), type (eintippen, optional vorher hat/ist wählen),
// choice (auswählen, z. B. "Stimmt das?"), sort (in Gruppen sortieren),
// syllables (Silben trennen), photo (im Heft schreiben + Foto als Nachweis).

const norm = (s) => String(s || "").normalize("NFC").replace(/\s+/g, " ").trim();
const singleStep = (q) => ({ kind: q.kind, q });

// Frage und richtige Antwort als Text (für Elternbereich und Ergebnis)
function describe(q) {
  if (q.kind === "type") return [q.prompt, [q.before, q.choose?.answer, q.answer].filter(Boolean).join(" ")];
  if (q.kind === "syllables") return [q.word, q.answer];
  return [q.prompt || q.say, q.answer];
}

function buildSchoolLesson(u, n) {
  const l = u.lessons[n];
  if (l.test) return shuffle(u.singles).slice(0, l.count || 12).map((q) => ({ ...singleStep(q), unit: u.id }));
  if (l.pick) return shuffle(u.singles.filter((q) => q.id.startsWith(l.pick))).slice(0, l.count || 10).map((q) => ({ ...singleStep(q), unit: u.id }));
  let steps = l.tasks.map((t) => (["pairs", "sort", "photo"].includes(t.kind) ? { kind: t.kind, t } : singleStep(t)));
  if (l.mix) steps = shuffle(steps);
  return steps.map((s) => ({ unit: u.id, ...s }));
}

// Ergebnis einer Einzelfrage: Lernkartei, Punkte, und bei Fehler am Ende der Lektion nochmal
function score(lesson, step, id, correct) {
  const pid = current.profile;
  if (step.retry) return;
  store.grade(pid, id, correct);
  store.save();
  if (!step.review) {
    lesson.total++;
    if (correct) lesson.right++;
  }
  if (!correct) {
    if (!lesson.missed.includes(id)) lesson.missed.push(id);
    if (!lesson.isTest) lesson.steps.push({ ...singleStep(item(id).q), unit: item(id).unit, retry: true });
  }
}

// Aufgabenzeile mit Vorlese-Knopf (je nach Einstellung des Profils)
function taskHead(text) {
  const m = voiceMode();
  if (m === "aus") return `<p class="task">${esc(text)}</p>`;
  return `${m === "selbst" ? `<p class="read-self">📖 Lies die Aufgabe selbst!</p>` : ""}
    <div class="task-row"><p class="task">${esc(text)}</p><button class="speaker again ${m === "selbst" ? "waiting" : ""}" aria-label="Vorlesen" ${m === "selbst" ? "disabled" : ""}>🔊</button></div>`;
}
function wireVoice(token, say) {
  const m = voiceMode();
  if (m === "aus") return;
  on(".again", "click", () => {
    token.heard = true;
    say();
  });
  if (m === "auto") setTimeout(() => alive(token) && say(), 250);
  else
    setTimeout(() => {
      if (alive(token)) app.querySelectorAll(".again").forEach((b) => {
        b.disabled = false;
        b.classList.remove("waiting");
      });
    }, VOICE_WAIT_MS);
}

function promptCard(text) {
  return `<div class="prompt-card"><span class="prompt-text">${esc(text)}</span></div>`;
}

// ---------- Übung: Eintippen ----------
STEPS.type = (lesson, step) => {
  const q = step.q;
  let first = true;
  let chosen = q.choose ? null : "";
  const token = lessonRender(lesson, `
    ${taskHead(q.task || "Schreib die Antwort!")}
    ${promptCard(q.prompt)}
    ${q.choose ? `<div class="choices text-choices" id="ch">${q.choose.options.map((o) => `<button class="choice" data-v="${esc(o)}"><span class="word">${esc(o)}</span></button>`).join("")}</div>` : ""}
    <div class="type-row" id="tr" ${q.choose ? "hidden" : ""}>
      <span class="before" id="before">${esc(q.before || "")}</span>
      <input id="ans" class="input type-input" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false" enterkeyhint="done">
    </div>
    <div class="feedback" id="fb"></div>
    <button class="go-btn" id="check" ${q.choose ? "hidden" : ""}>Prüfen ✓</button>
    <button class="go-btn" id="next" hidden>Weiter ➜</button>`);
  wireVoice(token, () => sayDe(q.say || q.task || q.prompt));
  const showInput = () => {
    $("before").textContent = [q.before, chosen].filter(Boolean).join(" ");
    $("tr").hidden = false;
    $("check").hidden = false;
    $("ans").focus();
  };
  on("#ch .choice", "click", (e) => {
    if (chosen) return;
    const el = e.currentTarget;
    if (el.dataset.v === q.choose.answer) {
      chosen = el.dataset.v;
      el.classList.add("right");
      chime("good");
      app.querySelectorAll("#ch .choice").forEach((b) => (b.disabled = true));
      $("fb").innerHTML = "";
      showInput();
    } else {
      first = false;
      el.classList.add("wrong");
      el.disabled = true;
      chime("bad");
      $("fb").innerHTML = `<span class="try">Hmm, probier das andere!</span>`;
    }
  });
  if (!q.choose) setTimeout(() => alive(token) && $("ans").focus(), 300);
  const check = async () => {
    const typed = norm($("ans").value);
    if (!typed) return;
    const full = norm([q.before, chosen, q.answer].filter(Boolean).join(" "));
    const ok = typed === norm(q.answer) || typed === full || (q.also || []).some((a) => norm(a) === typed);
    $("ans").disabled = true;
    $("check").hidden = true;
    if (ok) {
      $("ans").classList.add("right");
      chime("good");
      $("fb").innerHTML = `<span class="ok">${pick(PRAISE)}</span>`;
      score(lesson, step, q.id, first);
      await wait(900);
      if (alive(token)) advance(lesson);
    } else {
      $("ans").classList.add("wrong");
      chime("bad");
      $("fb").innerHTML = `<span class="try">Richtig ist:</span> <span class="solution">${esc(full)}</span>`;
      score(lesson, step, q.id, false);
      $("next").hidden = false;
    }
  };
  $("check").onclick = check;
  $("ans").addEventListener("keydown", (e) => e.key === "Enter" && check());
  $("next").onclick = () => advance(lesson);
};

// ---------- Übung: Auswählen (auch "Stimmt das?") ----------
STEPS.choice = (lesson, step) => {
  const q = step.q;
  let first = true;
  let locked = false;
  const opts = q.keepOrder ? q.options : shuffle(q.options);
  const token = lessonRender(lesson, `
    ${taskHead(q.task || "Was ist richtig?")}
    ${q.pic ? `<div class="prompt-card pic-card"><span class="huge-pic">${pic(q.pic)}</span>${q.showText ? `<span class="prompt-text">${esc(q.prompt)}</span>` : ""}</div>` : promptCard(q.prompt)}
    <div class="choices ${q.picOptions ? "pic-choices" : "text-choices"} ${q.bigOptions ? "big-options" : ""}">${opts.map((o) => `<button class="choice" data-v="${esc(o)}" aria-label="${esc(o)}">${q.picOptions ? `<span class="mid-pic">${pic(o)}</span>` : `<span class="word">${esc(o)}</span>`}</button>`).join("")}</div>
    <div class="feedback" id="fb"></div>
    <button class="go-btn" id="next" hidden>Weiter ➜</button>`);
  wireVoice(token, () => sayDe(q.say || q.task || q.prompt));
  on(".choices .choice", "click", async (e) => {
    if (locked) return;
    const el = e.currentTarget;
    if (el.dataset.v === q.answer) {
      locked = true;
      el.classList.add("right");
      chime("good");
      score(lesson, step, q.id, first);
      if (q.explain) {
        $("fb").innerHTML = `<span class="ok">${first ? pick(PRAISE) : "Genau."}</span><p class="explain">${esc(q.explain)}</p>`;
        $("next").hidden = false;
      } else {
        $("fb").innerHTML = `<span class="ok">${pick(PRAISE)}</span>`;
        await wait(800);
        if (alive(token)) advance(lesson);
      }
    } else {
      first = false;
      el.classList.add("wrong");
      el.disabled = true;
      chime("bad");
      $("fb").innerHTML = `<span class="try">Nicht ganz. Versuch es nochmal!</span>`;
    }
  });
  $("next").onclick = () => advance(lesson);
};

// ---------- Übung: Silben trennen ----------
STEPS.syllables = (lesson, step) => {
  const q = step.q;
  const letters = [...q.word];
  const cuts = new Set();
  const token = lessonRender(lesson, `
    ${taskHead("Wo trennst du das Wort?")}
    <p class="hint">Tipp zwischen die Buchstaben. Geht es nicht zu trennen? Dann gleich auf „Fertig“.</p>
    <div class="syl-wrap"><div class="syl" id="syl">${letters.map((ch, i) => `<span class="let">${esc(ch)}</span>${i < letters.length - 1 ? `<button class="gap" data-i="${i}" aria-label="Hier trennen"></button>` : ""}`).join("")}</div></div>
    
    <div class="feedback" id="fb"></div>
    <button class="go-btn" id="check">Fertig ✓</button>
    <button class="go-btn" id="next" hidden>Weiter ➜</button>`);
  wireVoice(token, () => sayDe("Wo trennst du das Wort " + q.word + "?"));
  on(".gap", "click", (e) => {
    const i = +e.currentTarget.dataset.i;
    if (cuts.has(i)) cuts.delete(i);
    else cuts.add(i);
    e.currentTarget.classList.toggle("cut", cuts.has(i));
    chime("pop");
  });
  $("check").onclick = async () => {
    const built = letters.map((ch, i) => ch + (cuts.has(i) ? "-" : "")).join("");
    app.querySelectorAll(".gap").forEach((b) => (b.disabled = true));
    $("check").hidden = true;
    if (built === q.answer) {
      chime("good");
      $("syl").classList.add("right");
      $("fb").innerHTML = `<span class="ok">${pick(PRAISE)}</span>`;
      score(lesson, step, q.id, true);
      await wait(900);
      if (alive(token)) advance(lesson);
    } else {
      chime("bad");
      $("fb").innerHTML = `<span class="try">Richtig ist:</span> <span class="solution">${esc(q.answer.includes("-") ? q.answer : q.answer + " (nicht trennbar)")}</span>`;
      score(lesson, step, q.id, false);
      $("next").hidden = false;
    }
  };
  $("next").onclick = () => advance(lesson);
};

// ---------- Übung: Paare finden ----------
STEPS.pairs = (lesson, step) => {
  const t = step.t;
  const wrong = new Set();
  let sel = null;
  let found = 0;
  const left = shuffle(t.pairs);
  const right = shuffle(t.pairs);
  const token = lessonRender(lesson, `
    ${taskHead(t.task || "Was gehört zusammen?")}
    <p class="hint">Tipp links ein Wort an und dann rechts das passende.</p>
    <div class="pairs">
      <div class="pcol">${left.map((p) => `<button class="pbtn" data-side="a" data-id="${p.id}">${esc(p.a)}</button>`).join("")}</div>
      <div class="pcol">${right.map((p) => `<button class="pbtn" data-side="b" data-id="${p.id}">${esc(p.b)}</button>`).join("")}</div>
    </div>
    <div class="feedback" id="fb"></div>`);
  wireVoice(token, () => sayDe(t.say || t.task || "Was gehört zusammen?"));
  on(".pbtn", "click", async (e) => {
    const el = e.currentTarget;
    if (el.classList.contains("done")) return;
    if (!sel || sel.dataset.side === el.dataset.side) {
      if (sel) sel.classList.remove("sel");
      sel = el;
      el.classList.add("sel");
      chime("pop");
      return;
    }
    const a = sel;
    sel = null;
    a.classList.remove("sel");
    const leftBtn = a.dataset.side === "a" ? a : el;
    if (a.dataset.id === el.dataset.id) {
      a.classList.add("done");
      el.classList.add("done");
      chime("good");
      if (++found === t.pairs.length) {
        t.pairs.forEach((p) => score(lesson, step, p.id, !wrong.has(p.id)));
        $("fb").innerHTML = `<span class="ok">${pick(PRAISE)}</span>`;
        chime("win");
        await wait(1000);
        if (alive(token)) advance(lesson);
      }
    } else {
      wrong.add(leftBtn.dataset.id);
      chime("bad");
      [a, el].forEach((b) => {
        b.classList.add("wrong");
        setTimeout(() => b.classList.remove("wrong"), 500);
      });
    }
  });
};

// ---------- Übung: Sortieren ----------
STEPS.sort = (lesson, step) => {
  const t = step.t;
  const order = shuffle(t.items);
  let i = 0;
  let first = true;
  const token = lessonRender(lesson, `
    ${taskHead(t.task || "Wohin gehört das Wort?")}
    <div class="prompt-card"><span class="prompt-text" id="cur"></span></div>
    <div class="bins">${t.groups.map((g) => `<button class="bin" data-g="${esc(g)}"><span class="bin-title">${esc(g)}</span><span class="bin-items"></span></button>`).join("")}</div>
    <div class="feedback" id="fb"></div>`);
  wireVoice(token, () => sayDe(t.say || t.task || "Wohin gehört das Wort?"));
  const show = () => ($("cur").textContent = order[i].text);
  show();
  on(".bin", "click", async (e) => {
    if (i >= order.length) return;
    const el = e.currentTarget;
    const it = order[i];
    if (el.dataset.g === it.group) {
      chime("good");
      score(lesson, step, it.id, first);
      el.querySelector(".bin-items").insertAdjacentHTML("beforeend", `<span>${esc(it.text)}</span>`);
      first = true;
      $("fb").innerHTML = "";
      if (++i < order.length) return show();
      $("fb").innerHTML = `<span class="ok">${pick(PRAISE)}</span>`;
      chime("win");
      await wait(1200);
      if (alive(token)) advance(lesson);
    } else {
      first = false;
      chime("bad");
      el.classList.add("wrong");
      setTimeout(() => el.classList.remove("wrong"), 500);
      $("fb").innerHTML = `<span class="try">Nicht ganz. Wo passt es besser?</span>`;
    }
  });
};

// ---------- Übung: Im Heft schreiben + Foto ----------
STEPS.photo = (lesson, step) => {
  const t = step.t;
  const pid = current.profile;
  const token = lessonRender(lesson, `
    ${taskHead("✍️ Schreib in dein Heft!")}
    <p class="photo-task">${esc(t.task)}</p>
    ${t.show ? `<div class="write-list">${t.show.map((w) => `<span>${esc(w)}</span>`).join("")}</div>` : ""}
    
    <label class="go-btn photo-btn" id="camlabel">📷 Fertig? Foto machen<input type="file" accept="image/*" capture="environment" id="cam" hidden></label>
    <div id="after"></div>`);
  wireVoice(token, () => sayDe(t.say || t.task));
  $("cam").onchange = async (e) => {
    const f = e.target.files[0];
    if (!f) return;
    $("camlabel").hidden = true;
    $("after").innerHTML = `<p class="hint">Foto wird gespeichert …</p>`;
    let ok = true;
    let url = "";
    try {
      const blob = await photos.shrink(f);
      url = URL.createObjectURL(blob);
      await photos.addPhoto({ pid, taskId: t.id, unitTitle: unitById(t.unit || step.unit)?.title_de || "", task: t.task, blob });
      store.setRedo(pid, t.id, false);
      store.save();
    } catch (err) {
      ok = false;
    }
    if (!alive(token)) return url && URL.revokeObjectURL(url);
    chime(ok ? "win" : "bad");
    $("after").innerHTML = `
      ${ok ? `<p class="feedback"><span class="ok">Foto gespeichert! 📸</span></p>${url ? `<img class="photo-preview" src="${url}" alt="Dein Foto">` : ""}` : `<p class="feedback"><span class="try">Das Foto konnte nicht gespeichert werden.</span></p>`}
      ${t.solution ? `<p class="task">Vergleiche mit der Lösung:</p><div class="write-list solution-list">${t.solution.map((w) => `<span>${esc(w)}</span>`).join("")}</div>` : ""}
      <div class="row">${nextBtn()}</div>`;
    $("next").onclick = () => {
      if (url) URL.revokeObjectURL(url);
      advance(lesson);
    };
  };
};

// ---------- Ende einer Schul-Lektion ----------
function finishSchoolLesson(lesson) {
  const pid = current.profile;
  store.setLessonDone(pid, lesson.u.id, lesson.n);
  const streak = store.touchStreak(pid);
  store.save();
  const missed = lesson.missed.map((id) => item(id)?.q).filter(Boolean);
  render(`
    <div class="screen center result" style="--c:${lesson.u.color}">
      <h2>${lesson.isTest ? "Test geschafft!" : pick(PRAISE)}</h2>
      <div class="result-stars"><span class="star on">★</span></div>
      ${lesson.total ? `<p class="score">${lesson.right} von ${lesson.total} gleich richtig</p>` : ""}
      ${lesson.selfRead ? `<p class="self-read">📖 ${lesson.selfRead} ${lesson.selfRead === 1 ? "Aufgabe" : "Aufgaben"} ganz allein gelesen. Toll!</p>` : ""}
      <p class="sub">🔥 ${streak.count} ${streak.count === 1 ? "Tag" : "Tage"} in Folge</p>
      ${missed.length ? `<p class="sub">${lesson.isTest ? "Das üben wir noch:" : "Das kommt in den nächsten Tagen nochmal dran:"}</p>
        <div class="missed">${missed.map((q) => {
          const [a, b] = describe(q);
          return `<div><span>${esc(a)}</span> → <b>${esc(b)}</b></div>`;
        }).join("")}</div>` : ""}
      <button class="go-btn" id="next">Weiter ➜</button>
    </div>`);
  chime("win");
  $("next").onclick = () => showUnit(lesson.u.id);
}

// ---------- Sticker-Album ----------
function showAlbum() {
  const pid = current.profile;
  const units = subjectsFor(pid).flatMap((s) => stagesFor(pid, s).flatMap((st) => st.units)).filter((u) => u.words.length);
  render(`
    <div class="screen">
      <header class="bar">
        <button class="icon-btn back-btn" id="back" aria-label="Zurück"><span class="back-arrow">←</span> Zurück</button>
        <span class="who">📒 Sticker-Album</span>
      </header>
      ${units.map((u) => {
        const has = store.lessonDone(pid, u.id, 0);
        return `<h3 class="album-title">${store.lessonDone(pid, u.id, 4) ? pic(u.image) : "⬜"} ${esc(u.title_de)}</h3>
          <div class="album">${u.words.map((w) => `<button class="sticker ${has ? "" : "empty"}" data-id="${w.id}" ${has ? "" : "disabled"}>${has ? pic(w.image) : "?"}</button>`).join("")}</div>`;
      }).join("")}
    </div>`);
  $("back").onclick = () => showHome();
  on(".sticker:not(.empty)", "click", (e) => play(item(e.currentTarget.dataset.id)));
}

// ---------- Elternbereich ----------
// Eltern-Code: wird beim ersten Öffnen festgelegt, liegt nur auf diesem Gerät (als Prüfsumme),
// ist nicht in der Sicherungsdatei und bleibt beim Zurücksetzen erhalten.
const PIN_KEY = "learnino-eltern-code";
const PIN_LOCK_KEY = "learnino-eltern-sperre";
async function pinHash(code) {
  const text = "learnino:" + code;
  try {
    const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
    return [...new Uint8Array(buf)].map((x) => x.toString(16).padStart(2, "0")).join("");
  } catch (e) {
    let h = 5381;
    for (const ch of text) h = ((h * 33) ^ ch.charCodeAt(0)) >>> 0;
    return "s" + h.toString(16);
  }
}
const lsGet = (k) => {
  try {
    return localStorage.getItem(k);
  } catch (e) {
    return null;
  }
};
const lsSet = (k, v) => {
  try {
    localStorage.setItem(k, v);
  } catch (e) {
    /* blockiert */
  }
};
const validPin = (c) => /^\d{4,8}$/.test(c);

function showParentGate(msg = "") {
  if (!lsGet(PIN_KEY)) return showPinSetup(showParents, "");
  render(`
    <div class="screen center">
      <h2>🔒 Elternbereich</h2>
      <p class="sub">Eltern-Code eingeben</p>
      <input id="ans" class="input pin-input" type="password" inputmode="numeric" pattern="[0-9]*" autocomplete="off" maxlength="8">
      <p class="small pin-msg" id="msg">${esc(msg)}</p>
      <button class="go-btn" id="ok">Öffnen</button>
      <button class="link-btn" id="back">Zurück</button>
    </div>`);
  $("back").onclick = showProfiles;
  const tryOpen = async () => {
    const lock = JSON.parse(lsGet(PIN_LOCK_KEY) || '{"n":0,"until":0}');
    if (Date.now() < lock.until) {
      $("msg").textContent = `Zu oft falsch. Bitte in ${Math.ceil((lock.until - Date.now()) / 1000)} Sekunden nochmal.`;
      $("ans").value = "";
      return;
    }
    if ((await pinHash($("ans").value.trim())) === lsGet(PIN_KEY)) {
      lsSet(PIN_LOCK_KEY, '{"n":0,"until":0}');
      return showParents();
    }
    lock.n++;
    if (lock.n >= 3) {
      lock.until = Date.now() + 60000;
      lock.n = 0;
    }
    lsSet(PIN_LOCK_KEY, JSON.stringify(lock));
    $("ans").value = "";
    $("msg").textContent = lock.until > Date.now() ? "Zu oft falsch. Eine Minute warten." : "Falscher Code.";
  };
  $("ok").onclick = tryOpen;
  // Wichtig: kein "return false" für andere Tasten, sonst erscheinen keine Ziffern
  $("ans").addEventListener("keydown", (e) => {
    if (e.key === "Enter") tryOpen();
  });
  $("ans").focus();
}

// Code festlegen (beim ersten Mal) oder ändern (im Elternbereich)
function showPinSetup(done, back) {
  render(`
    <div class="screen center">
      <h2>🔒 Eltern-Code festlegen</h2>
      <p class="sub">4 bis 8 Ziffern. Damit öffnest du später den Elternbereich. Schreib ihn dir auf: Ohne Code kommt man nicht mehr hinein.</p>
      <input id="p1" class="input pin-input" type="password" inputmode="numeric" pattern="[0-9]*" autocomplete="off" maxlength="8" placeholder="Code">
      <input id="p2" class="input pin-input" type="password" inputmode="numeric" pattern="[0-9]*" autocomplete="off" maxlength="8" placeholder="Nochmal">
      <p class="small pin-msg" id="msg"></p>
      <button class="go-btn" id="ok">Speichern</button>
      <button class="link-btn" id="back">Zurück</button>
    </div>`);
  $("back").onclick = back ? () => showParents() : showProfiles;
  $("ok").onclick = async () => {
    const a = $("p1").value.trim();
    if (!validPin(a)) return ($("msg").textContent = "Bitte 4 bis 8 Ziffern eingeben.");
    if (a !== $("p2").value.trim()) return ($("msg").textContent = "Die beiden Eingaben sind verschieden.");
    lsSet(PIN_KEY, await pinHash(a));
    done("✅ Eltern-Code gespeichert.");
  };
  $("p1").focus();
}

function boxCounts(pid, unit) {
  const n = [0, 0, 0, 0, 0, 0];
  for (const id of unitIds(unit)) n[store.card(pid, id)?.box || 0]++;
  return n;
}

function unitTable(u) {
  const box = (pid, id) => {
    const c = store.card(pid, id);
    return c ? "Kasten " + c.box + (store.isTrouble(c) ? " ⚠️" : "") : "–";
  };
  if (isSchool(u)) {
    return `<table class="words">
      <tr><th>Aufgabe</th><th>Lösung</th>${PROFILES.map((p) => `<th>${p.title}</th>`).join("")}</tr>
      ${u.singles.map((q) => {
        const [a, b] = describe(q);
        return `<tr><td>${esc(a)}</td><td>${esc(b)}</td>${PROFILES.map((p) => `<td>${box(p.id, q.id)}</td>`).join("")}</tr>`;
      }).join("")}
    </table>`;
  }
  return `<table class="words">
    <tr><th></th><th>Englisch</th><th>Deutsch</th>${PROFILES.map((p) => `<th>${p.title}</th>`).join("")}</tr>
    ${[...u.words, ...u.phrases].map((w) => `<tr><td>${pic(w.image)}</td><td><button class="link-btn inline-btn" data-say="${w.id}">${esc(w.en)} 🔊</button></td><td>${esc(w.de || "")}</td>${PROFILES.map((p) => `<td>${box(p.id, w.id)}</td>`).join("")}</tr>`).join("")}
  </table>`;
}

function troubleHtml() {
  const rows = PROFILES.map((p) => {
    const list = store.troubleCards(p.id).filter((c) => item(c.id));
    if (!list.length) return `<p class="small"><b>${p.title}:</b> nichts, prima!</p>`;
    return `<p class="small"><b>${p.title}:</b></p><table class="words">
      <tr><th>Aufgabe</th><th>Lösung</th><th>falsch</th></tr>
      ${list.map((c) => {
        const it = item(c.id);
        const [a, b] = it.kind === "task" ? describe(it.q) : [it.en, it.de || ""];
        return `<tr><td>${esc(a)}</td><td>${esc(b)}</td><td>${c.wrong}×</td></tr>`;
      }).join("")}
    </table>`;
  }).join("");
  return `<section>
    <h3>⚠️ Das klappt noch nicht</h3>
    <p class="small">Aufgaben, die mindestens zweimal falsch waren. Sie kommen öfter dran (spätestens alle 2 Tage), bis sie dreimal hintereinander richtig waren.</p>
    ${rows}
  </section>`;
}

async function fillPhotos() {
  const box = $("photos");
  if (!box) return;
  const list = await photos.allPhotos();
  if (!$("photos")) return;
  if (!list.length) {
    box.innerHTML = `<p class="small">Noch keine Fotos.</p>`;
    return;
  }
  const label = { neu: "🆕 neu", ok: "✅ passt", nochmal: "🔁 nochmal" };
  box.innerHTML = list.map((f) => {
    const p = PROFILES.find((x) => x.id === f.pid);
    const url = URL.createObjectURL(f.blob);
    return `<div class="photo-item" data-id="${f.id}">
      <a href="${url}" target="_blank"><img src="${url}" alt="Foto"></a>
      <div class="photo-info">
        <b>${esc(p ? p.title : f.pid)}</b> · ${new Date(f.date).toLocaleString("de-DE", { dateStyle: "short", timeStyle: "short" })} · <span class="pstatus">${label[f.status] || ""}</span><br>
        <span class="small">${esc(f.unitTitle)}: ${esc(f.task)}</span>
        <div class="row left">
          <button class="wide-btn mini" data-act="ok">✅ Passt</button>
          <button class="wide-btn mini" data-act="nochmal">🔁 Nochmal</button>
          <button class="wide-btn mini danger" data-act="del">🗑️</button>
        </div>
      </div>
    </div>`;
  }).join("");
  box.querySelectorAll("[data-act]").forEach((b) =>
    b.addEventListener("click", async (e) => {
      const el = e.currentTarget.closest(".photo-item");
      const f = list.find((x) => x.id === +el.dataset.id);
      const act = e.currentTarget.dataset.act;
      if (act === "del") {
        if (!confirm("Foto löschen?")) return;
        await photos.deletePhoto(f.id);
        el.remove();
        return;
      }
      await photos.setStatus(f.id, act);
      store.setRedo(f.pid, f.taskId, act === "nochmal");
      store.save();
      el.querySelector(".pstatus").textContent = label[act];
    })
  );
}

function showParents(msg = "") {
  const v = voiceInfo();
  const saved = store.savedAt();
  render(`
    <div class="screen parents">
      <header class="bar">
        <button class="icon-btn back-btn" id="back" aria-label="Zurück"><span class="back-arrow">←</span> Zurück</button>
        <span class="who">Elternbereich</span>
      </header>
      ${msg ? `<p class="notice">${msg}</p>` : ""}
      ${content.errors.length ? `<section class="errors"><h3>⚠️ Probleme mit den Inhalten</h3><ul>${content.errors.map((e) => `<li>${esc(e)}</li>`).join("")}</ul></section>` : ""}
      <section>
        <h3>Freigeschaltet</h3>
        <p class="small">Was soll das Kind sehen? Ausgeschaltetes verschwindet, der Fortschritt bleibt gespeichert.</p>
        <div class="unlock">
          ${PROFILES.map((p) => `<div class="unlock-col">
            <h4>${p.title}</h4>
            ${content.subjects.map((sub) => `
              <label class="field check subj"><input type="checkbox" class="en-box" data-p="${p.id}" data-id="${sub.id}" ${store.isEnabled(p.id, sub.id) ? "checked" : ""}> ${esc(sub.title)}</label>
              ${sub.stages.map((st) => `
                <div class="unlock-topics">
                  <label class="field check subj"><input type="checkbox" class="en-box" data-p="${p.id}" data-id="${st.id}" ${store.isEnabled(p.id, st.id, stageDefault(p.id, st)) ? "checked" : ""}> ${esc(st.title)}</label>
                  <div class="unlock-topics">
                    ${st.units.map((u) => `<label class="field check"><input type="checkbox" class="en-box" data-p="${p.id}" data-id="${u.id}" ${store.isEnabled(p.id, u.id) ? "checked" : ""}> ${esc(u.title_de)}</label>`).join("")}
                  </div>
                </div>`).join("")}`).join("")}
          </div>`).join("")}
        </div>
      </section>
      <section>
        <h3>Lernstand</h3>
        <p class="small">Lernkartei: Jede Aufgabe wandert bei richtiger Antwort einen Kasten weiter (1 → 5), bei falscher zurück in Kasten 1. Eine Einheit ist geschafft 🏆, wenn alles mindestens in Kasten 3 ist. Fällig heute: ${PROFILES.map((p) => `${p.title} ${store.dueCards(p.id).length}`).join(", ")}.</p>
        ${content.subjects.flatMap((s) => s.stages.flatMap((st) => st.units)).map((u) => `
          <details class="unit-details">
            <summary>${esc(u.title_de)} <span class="small">${PROFILES.map((p) => {
              const n = boxCounts(p.id, u);
              const sure = n[3] + n[4] + n[5];
              return `${p.title}: ${sure}/${unitIds(u).length} sicher${unitMastered(p.id, u) ? " 🏆" : ""}`;
            }).join(" · ")}</span></summary>
            ${unitTable(u)}
          </details>`).join("")}
      </section>
      ${troubleHtml()}
      <section>
        <h3>📷 Fotomappe</h3>
        <p class="small">Fotos von Heft-Aufgaben. „Nochmal“ gibt die Aufgabe zurück: Sie kommt beim nächsten Üben im Fach wieder. Die Fotos liegen nur auf diesem Gerät und sind nicht in der Sicherungsdatei.</p>
        <div id="photos"><p class="small">Lade Fotos …</p></div>
      </section>
      <section>
        <h3>Fortschritt sichern und laden</h3>
        <p class="small">„Sichern“ erstellt eine Datei. Leg sie in OneDrive ab. Auf dem anderen Gerät „Laden“ tippen und die Datei aus OneDrive wählen.</p>
        <div class="row">
          <button class="wide-btn" id="export">💾 Sichern</button>
          <label class="wide-btn file-btn">📂 Laden<input type="file" id="import" accept=".json,application/json" hidden></label>
        </div>
        ${saved ? `<p class="small">Zuletzt gespeichert: ${new Date(saved).toLocaleString("de-DE")}</p>` : ""}
      </section>
      <section>
        <h3>🔊 Aufgaben vorlesen</h3>
        <p class="small">Für Kinder, die noch nicht lesen können. <b>Vorlesen</b>: Jede Aufgabe wird automatisch vorgelesen. <b>Erst selbst lesen</b>: Das Kind soll die Aufgabe zuerst selbst lesen, der 🔊-Knopf geht erst nach ein paar Sekunden. Am Ende steht, wie viele Aufgaben es allein gelesen hat. <b>Aus</b>: keine deutsche Stimme. Englische Wörter werden immer vorgesprochen.</p>
        ${[...PROFILES, TEST_PROFILE].map((p) => `<div class="voice-row"><span>${esc(p.title)}</span><select class="input voice-sel" data-p="${p.id}">
          ${[["auto", "Vorlesen"], ["selbst", "Erst selbst lesen"], ["aus", "Aus"]].map(([v, l]) => `<option value="${v}" ${voiceMode(p.id) === v ? "selected" : ""}>${l}</option>`).join("")}
        </select></div>`).join("")}
      </section>
      <section>
        <h3>Stimme</h3>
        <p class="small">${v.supported ? (v.british ? `Britische Stimme gefunden: ${esc(v.name)}` : "Keine britische Stimme gefunden. Bitte in den Android-Einstellungen unter „Sprachausgabe“ (Google) die Sprache „Englisch (Vereinigtes Königreich)“ herunterladen, dann funktioniert sie auch offline.") : "Dieses Gerät unterstützt keine Sprachausgabe."} Liegt für einen Inhalt eine Aufnahme im Ordner audio/en, wird stattdessen die Aufnahme abgespielt.</p>
        <button class="wide-btn" id="test">🔊 Stimme testen</button>
      </section>
      <section>
        <h3>🧪 Testmodus</h3>
        <p class="small">Zum Ausprobieren ohne den Fortschritt der Kinder zu verändern. Der Testmodus sieht alle Fächer und Stufen und hat einen eigenen Lernstand. Fällig im Test: ${store.dueCards(TEST_PROFILE.id).length}.</p>
        <div class="row">
          <button class="wide-btn" id="testmode">🧪 Testmodus starten</button>
          <button class="wide-btn" id="testreset">Test-Fortschritt löschen</button>
        </div>
      </section>
      <section>
        <h3>🔒 Eltern-Code</h3>
        <p class="small">Der Code gilt nur auf diesem Gerät. Auf dem Handy legst du beim ersten Öffnen dort einen eigenen fest.</p>
        <button class="wide-btn" id="pinchange">Code ändern</button>
      </section>
      <section>
        <h3>Zurücksetzen</h3>
        <button class="wide-btn danger" id="reset">Gesamten Fortschritt löschen</button>
      </section>
      <p class="small center-text">Learnino Version ${APP_VERSION}</p>
    </div>`);
  $("back").onclick = showProfiles;
  fillPhotos();
  on(".voice-sel", "change", (e) => {
    store.profile(e.target.dataset.p).voice = e.target.value;
    store.save();
  });
  on(".en-box", "change", (e) => {
    store.setEnabled(e.target.dataset.p, e.target.dataset.id, e.target.checked);
    store.save();
  });
  on("[data-say]", "click", (e) => play(item(e.currentTarget.dataset.say)));
  $("test").onclick = () => sayParts([["en", "Hello! My name is Learnino. Let's learn English!"]]);
  $("export").onclick = async () => {
    const file = store.exportFile();
    if (navigator.canShare && navigator.canShare({ files: [file] })) {
      try {
        await navigator.share({ files: [file], title: "Learnino Fortschritt" });
        return;
      } catch (e) {
        if (e.name === "AbortError") return;
      }
    }
    const a = document.createElement("a");
    a.href = URL.createObjectURL(file);
    a.download = file.name;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  };
  $("import").onchange = async (e) => {
    const f = e.target.files[0];
    if (!f) return;
    try {
      store.importData(await f.text());
      showParents("✅ Fortschritt geladen.");
    } catch (err) {
      showParents("⚠️ Diese Datei konnte nicht geladen werden (vielleicht von einer alten App-Version).");
    }
  };
  $("pinchange").onclick = () => showPinSetup(showParents, true);
  $("testmode").onclick = () => {
    current.profile = TEST_PROFILE.id;
    current.subject = null;
    showHome();
  };
  $("testreset").onclick = () => {
    store.resetProfile(TEST_PROFILE.id);
    showParents("Test-Fortschritt gelöscht.");
  };
  $("reset").onclick = () => {
    if (confirm("Wirklich den gesamten Fortschritt beider Kinder löschen?")) {
      store.resetAll();
      showParents("Fortschritt gelöscht.");
    }
  };
}

// ---------- Start ----------
if ("serviceWorker" in navigator && location.protocol !== "file:") {
  const hadController = !!navigator.serviceWorker.controller;
  let reloaded = false;
  // Sobald ein Update installiert ist, einmal neu laden, damit es sofort sichtbar ist
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    if (hadController && !reloaded) {
      reloaded = true;
      location.reload();
    }
  });
  navigator.serviceWorker.register("sw.js", { updateViaCache: "none" }).then((reg) => reg.update()).catch(() => {});
}

app.innerHTML = `<div class="screen center"><h1 class="logo">Learnino</h1><p class="sub">Einen Moment…</p></div>`;
loadContent().then(showProfiles);
