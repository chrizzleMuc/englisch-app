import { PROFILES, PRAISE, PRAISE_EN, AVATAR, LESSONS, SPEAKERS } from "./data.js";
import { sayParts, sayEn, sayDe, chime, voiceInfo } from "./speech.js";
import { play, promptAnd, stopAudio } from "./audio.js";
import { canRecord, record, playUrl } from "./recorder.js";
import { content, loadContent } from "./content.js";
import * as store from "./store.js";
import * as photos from "./photos.js";

const APP_VERSION = 8;
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
const prof = () => PROFILES.find((p) => p.id === current.profile);
const item = (id) => content.items.get(id);
const unitById = (id) => content.units.get(id);

function render(html) {
  stopAudio();
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

// ---------- Avatar ----------
function avatarOf(pid) {
  const p = PROFILES.find((x) => x.id === pid);
  return store.profile(pid).avatar || { base: p.pic, color: pid === "pirat" ? "#74c0fc" : "#8ce99a" };
}

function avatarHtml(a, cls = "") {
  return `<span class="avatar ${cls}" style="--bg:${a.color}"><span class="av-base">${a.base}</span></span>`;
}

function showAvatarEditor(first = false) {
  const pid = current.profile;
  const a = { ...avatarOf(pid) };
  const groups = [["base", "Welches Tier bist du?"], ["color", "Hintergrundfarbe"]];
  render(`
    <div class="screen">
      <header class="bar">
        ${first ? "" : `<button class="icon-btn" id="back" aria-label="Zurück">⬅</button>`}
        <span class="who">${first ? "Wie willst du aussehen?" : "Mein Bild"}</span>
      </header>
      <div class="av-preview">${avatarHtml(a, "xl")}</div>
      ${groups.map(([g, label]) => `
        <h3 class="av-label">${label}</h3>
        <div class="av-row">
          ${AVATAR[g].map(([v], i) => `<button class="av-opt ${a[g] === v ? "sel" : ""}" data-g="${g}" data-i="${i}" ${g === "color" ? `style="background:${v}"` : ""}>${g === "color" ? "" : v}</button>`).join("")}
        </div>`).join("")}
      <button class="go-btn" id="done">Fertig ✓</button>
    </div>`);
  on(".av-opt", "click", (e) => {
    const { g, i } = e.currentTarget.dataset;
    const [v, en] = AVATAR[g][+i];
    a[g] = v;
    app.querySelectorAll(`.av-opt[data-g="${g}"]`).forEach((b) => b.classList.toggle("sel", b === e.currentTarget));
    app.querySelector(".av-preview").innerHTML = avatarHtml(a, "xl");
    chime("pop");
    sayEn(en);
  });
  $("done").onclick = () => {
    store.profile(pid).avatar = { base: a.base, color: a.color };
    store.save();
    chime("win");
    showHome();
  };
  if (!first) $("back").onclick = () => showHome();
  if (first) sayDe("Welches Tier willst du sein? Such dir eins aus!");
}

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
            ${avatarHtml(avatarOf(p.id), "lg")}
            <span class="pname">${esc(p.title)}</span>
            <span class="small">⭐ ${store.totalStars(p.id)}</span>
          </button>`).join("")}
      </div>
      <button class="link-btn" id="parents">🔒 Elternbereich</button>
    </div>`);
  on(".profile-card", "click", (e) => {
    current.profile = e.currentTarget.dataset.id;
    chime("pop");
    if (store.profile(current.profile).avatar) showHome();
    else showAvatarEditor(true);
  });
  $("parents").onclick = showParentGate;
}

// ---------- Freigeschaltete Inhalte ----------
const stageDefault = (pid, st) => !st.kinder || st.kinder.includes(pid);

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
        <button class="icon-btn" id="back" aria-label="Zurück">⬅</button>
        <button class="who who-btn" id="me" aria-label="Bild ändern">${avatarHtml(avatarOf(p.id), "sm")} ${esc(p.title)} <span class="pencil">✏️</span></button>
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
      ${many ? `<h2 class="subject-title">${sub.image} ${esc(sub.title)}</h2>` : ""}
      ${stagesFor(p.id, sub).map((st) => `
        <h3 class="stage-title">${esc(st.title)}</h3>
        <div class="topics">
          ${st.units.map((u) => {
            const nl = lessonsOf(u).length;
            const done = lessonsOf(u).filter((_, n) => store.lessonDone(p.id, u.id, n)).length;
            return `<button class="topic" data-id="${u.id}" style="--c:${u.color}">
              ${unitMastered(p.id, u) ? `<span class="badge">🏆</span>` : ""}
              <span class="big-pic">${u.image}</span>
              <span class="tname">${esc(u.title_de)}</span>
              <span class="dots small-dots">${Array.from({ length: nl }, (_, n) => `<span class="dot ${n < done ? "on" : ""}"></span>`).join("")}</span>
            </button>`;
          }).join("")}
        </div>`).join("")}
      ${stagesFor(p.id, sub).some((st) => st.units.some((u) => u.words.length)) ? `<button class="wide-btn album-btn" id="album">📒 Mein Sticker-Album</button>` : ""}
    </div>`);
  $("back").onclick = () => (many ? showSubjects(subs) : showProfiles());
  if ($("album")) $("album").onclick = showAlbum;
  $("me").onclick = () => showAvatarEditor(false);
  on(".topic[data-id]", "click", (e) => {
    chime("pop");
    showUnit(e.currentTarget.dataset.id);
  });
  sayDe("Such dir ein Thema aus!");
}

function showSubjects(subs) {
  const p = prof();
  current.subject = null;
  render(`
    <div class="screen">
      ${homeHeader(p)}
      ${subs.length ? `<div class="topics">
        ${subs.map((x) => `<button class="topic subject" data-id="${x.id}" style="--c:${x.color}">
          <span class="big-pic">${x.image}</span><span class="tname">${esc(x.title)}</span></button>`).join("")}
      </div>` : `<p class="sub center-text">Hier ist noch nichts freigeschaltet. Frag Mama oder Papa!</p>`}
    </div>`);
  $("back").onclick = showProfiles;
  $("me").onclick = () => showAvatarEditor(false);
  on(".subject", "click", (e) => showHome(e.currentTarget.dataset.id));
  sayDe(subs.length ? "Was willst du heute lernen?" : "Hier ist noch nichts freigeschaltet.");
}

// ---------- Einheit mit 5 Lektionen ----------
function showUnit(unitId) {
  const u = unitById(unitId);
  const pid = current.profile;
  render(`
    <div class="screen">
      <header class="bar">
        <button class="icon-btn" id="back" aria-label="Zurück">⬅</button>
        <span class="who">${u.image} ${esc(u.title_de)}</span>
        ${unitMastered(pid, u) ? `<span class="stat">🏆</span>` : ""}
      </header>
      <div class="path">
        ${lessonsOf(u).map((l, i) => {
          const open = isSchool(u) || i === 0 || store.lessonDone(pid, u.id, i - 1);
          const done = store.lessonDone(pid, u.id, i);
          return `<button class="node ${open ? "" : "locked"} ${i % 2 ? "right" : "left"}" data-i="${i}" ${open ? "" : "disabled"} style="--c:${u.color}">
            <span class="node-pics">${open ? l.icon : "🔒"}</span>
            <span class="node-label">${l.title}</span>
            <span class="node-stars">${done ? `<span class="star on">★</span>` : `<span class="star">★</span>`}</span>
          </button>`;
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
      ${step.ids.map((id) => `<button class="choice exp" data-id="${id}"><span class="${step.phrases ? "mid-pic" : "huge-pic"}">${item(id).image}</span><span class="check">✓</span></button>`).join("")}
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
      ${options.map((o) => `<button class="choice" data-id="${o.id}"><span class="${big ? "huge-pic" : "mid-pic"}">${o.image}</span></button>`).join("")}
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
      ${cards.map((c, i) => `<button class="mcard" data-i="${i}"><span class="back">?</span><span class="front">${c.face === "pic" ? c.it.image : "🔊"}</span></button>`).join("")}
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
    <div class="missing-row" id="row">${set.map((w) => `<span class="mpic">${w.image}</span>`).join("")}</div>
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
  $("row").innerHTML = rest.map((w) => `<span class="mpic">${w.image}</span>`).join("") + `<span class="mpic gap">❓</span>`;
  const options = shuffle([gone, ...others]);
  $("area").innerHTML = `<p class="task">Was fehlt?</p><div class="choices n${options.length}">${options.map((o) => `<button class="choice" data-id="${o.id}"><span class="huge-pic">${o.image}</span></button>`).join("")}</div><div class="feedback" id="fb"></div>`;
  sayDe("Was fehlt?");
  let first = true;
  on(".choice", "click", async (e) => {
    const el = e.currentTarget;
    if (el.dataset.id === gone.id) {
      el.classList.add("right");
      chime("good");
      $("fb").innerHTML = `<span class="ok">${pick(PRAISE)}</span>`;
      store.grade(current.profile, gone.id, first);
      app.querySelector(".gap").textContent = gone.image;
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
    <div class="learn-card"><span class="huge-pic">${it.image}</span></div>
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
    <div class="learn-card action-card"><span class="huge-pic">${it.image}</span></div>
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
    $("who").textContent = sp.pic;
    $("who").hidden = line.image === sp.pic;
    $("scene").textContent = line.image;
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
    <div class="learn-card"><span class="huge-pic" id="rpic">${r.lines[0].image}</span></div>
    <div class="row"><button class="speaker big" id="again" aria-label="Nochmal">🔁</button><button class="speaker big" id="clap" aria-label="Klatschen">👏</button></div>
    ${nextBtn("Weiter ➜", true)}`);
  const run = async () => {
    if (running) return;
    running = true;
    for (const line of r.lines) {
      if (!alive(token)) return;
      $("rpic").textContent = line.image;
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
      ${isLast && first ? `<p class="sub">Neuer Sticker für dein Album:</p><div class="stickers"><span class="sticker big-sticker">${lesson.u.image}</span></div>` : ""}
      ${lesson.n === 0 && first ? `<p class="sub">Neue Wörter im Album:</p><div class="stickers">${lesson.u.words.map((w) => `<span class="sticker">${w.image}</span>`).join("")}</div>` : ""}
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
  return [q.prompt, q.answer];
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

function promptCard(text) {
  return `<div class="prompt-card"><span class="prompt-text">${esc(text)}</span><button class="speaker again" aria-label="Vorlesen">🔊</button></div>`;
}

// ---------- Übung: Eintippen ----------
STEPS.type = (lesson, step) => {
  const q = step.q;
  let first = true;
  let chosen = q.choose ? null : "";
  const token = lessonRender(lesson, `
    <p class="task">${esc(q.task || "Schreib die Antwort!")}</p>
    ${promptCard(q.prompt)}
    ${q.choose ? `<div class="choices text-choices" id="ch">${q.choose.options.map((o) => `<button class="choice" data-v="${esc(o)}"><span class="word">${esc(o)}</span></button>`).join("")}</div>` : ""}
    <div class="type-row" id="tr" ${q.choose ? "hidden" : ""}>
      <span class="before" id="before">${esc(q.before || "")}</span>
      <input id="ans" class="input type-input" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false" enterkeyhint="done">
    </div>
    <div class="feedback" id="fb"></div>
    <button class="go-btn" id="check" ${q.choose ? "hidden" : ""}>Prüfen ✓</button>
    <button class="go-btn" id="next" hidden>Weiter ➜</button>`);
  const say = () => sayDe(q.say || q.prompt);
  on(".again", "click", say);
  setTimeout(() => alive(token) && say(), 250);
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
    <p class="task">${esc(q.task || "Was ist richtig?")}</p>
    ${promptCard(q.prompt)}
    <div class="choices text-choices">${opts.map((o) => `<button class="choice" data-v="${esc(o)}"><span class="word">${esc(o)}</span></button>`).join("")}</div>
    <div class="feedback" id="fb"></div>
    <button class="go-btn" id="next" hidden>Weiter ➜</button>`);
  const say = () => sayDe(q.say || q.prompt);
  on(".again", "click", say);
  setTimeout(() => alive(token) && say(), 250);
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
    <p class="task">Wo trennst du das Wort?</p>
    <p class="hint">Tipp zwischen die Buchstaben. Geht es nicht zu trennen? Dann gleich auf „Fertig“.</p>
    <div class="syl-wrap"><div class="syl" id="syl">${letters.map((ch, i) => `<span class="let">${esc(ch)}</span>${i < letters.length - 1 ? `<button class="gap" data-i="${i}" aria-label="Hier trennen"></button>` : ""}`).join("")}</div></div>
    <div class="row"><button class="speaker again" aria-label="Vorlesen">🔊</button></div>
    <div class="feedback" id="fb"></div>
    <button class="go-btn" id="check">Fertig ✓</button>
    <button class="go-btn" id="next" hidden>Weiter ➜</button>`);
  const say = () => sayDe(q.word);
  on(".again", "click", say);
  setTimeout(() => alive(token) && say(), 250);
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
    <p class="task">${esc(t.task || "Was gehört zusammen?")}</p>
    <p class="hint">Tipp links ein Wort an und dann rechts das passende.</p>
    <div class="pairs">
      <div class="pcol">${left.map((p) => `<button class="pbtn" data-side="a" data-id="${p.id}">${esc(p.a)}</button>`).join("")}</div>
      <div class="pcol">${right.map((p) => `<button class="pbtn" data-side="b" data-id="${p.id}">${esc(p.b)}</button>`).join("")}</div>
    </div>
    <div class="feedback" id="fb"></div>`);
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
    <p class="task">${esc(t.task || "Wohin gehört das Wort?")}</p>
    <div class="prompt-card"><span class="prompt-text" id="cur"></span></div>
    <div class="bins">${t.groups.map((g) => `<button class="bin" data-g="${esc(g)}"><span class="bin-title">${esc(g)}</span><span class="bin-items"></span></button>`).join("")}</div>
    <div class="feedback" id="fb"></div>`);
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
    <p class="task">✍️ Schreib in dein Heft!</p>
    <p class="photo-task">${esc(t.task)}</p>
    ${t.show ? `<div class="write-list">${t.show.map((w) => `<span>${esc(w)}</span>`).join("")}</div>` : ""}
    <div class="row"><button class="speaker again" aria-label="Vorlesen">🔊</button></div>
    <label class="go-btn photo-btn" id="camlabel">📷 Fertig? Foto machen<input type="file" accept="image/*" capture="environment" id="cam" hidden></label>
    <div id="after"></div>`);
  const say = () => sayDe(t.say || t.task);
  on(".again", "click", say);
  setTimeout(() => alive(token) && say(), 250);
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
        <button class="icon-btn" id="back" aria-label="Zurück">⬅</button>
        <span class="who">📒 Sticker-Album</span>
      </header>
      ${units.map((u) => {
        const has = store.lessonDone(pid, u.id, 0);
        return `<h3 class="album-title">${store.lessonDone(pid, u.id, 4) ? u.image : "⬜"} ${esc(u.title_de)}</h3>
          <div class="album">${u.words.map((w) => `<button class="sticker ${has ? "" : "empty"}" data-id="${w.id}" ${has ? "" : "disabled"}>${has ? w.image : "?"}</button>`).join("")}</div>`;
      }).join("")}
    </div>`);
  $("back").onclick = () => showHome();
  on(".sticker:not(.empty)", "click", (e) => play(item(e.currentTarget.dataset.id)));
}

// ---------- Elternbereich ----------
function showParentGate() {
  const a = 3 + Math.floor(Math.random() * 6);
  const b = 4 + Math.floor(Math.random() * 6);
  render(`
    <div class="screen center">
      <h2>🔒 Elternbereich</h2>
      <p class="sub">Wie viel ist ${a} × ${b}?</p>
      <input id="ans" class="input" inputmode="numeric" autocomplete="off">
      <button class="go-btn" id="ok">Öffnen</button>
      <button class="link-btn" id="back">Zurück</button>
    </div>`);
  $("back").onclick = showProfiles;
  $("ok").onclick = () => {
    if (+$("ans").value === a * b) showParents();
    else $("ans").value = "";
  };
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
    ${[...u.words, ...u.phrases].map((w) => `<tr><td>${w.image}</td><td><button class="link-btn inline-btn" data-say="${w.id}">${esc(w.en)} 🔊</button></td><td>${esc(w.de || "")}</td>${PROFILES.map((p) => `<td>${box(p.id, w.id)}</td>`).join("")}</tr>`).join("")}
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
        <button class="icon-btn" id="back" aria-label="Zurück">⬅</button>
        <span class="who">Elternbereich</span>
      </header>
      ${msg ? `<p class="notice">${msg}</p>` : ""}
      ${content.errors.length ? `<section class="errors"><h3>⚠️ Probleme mit den Inhalten</h3><ul>${content.errors.map((e) => `<li>${esc(e)}</li>`).join("")}</ul></section>` : ""}
      <section>
        <h3>Freigeschaltet</h3>
        <p class="small">Was soll das Kind sehen? Ausgeschaltetes verschwindet, der Fortschritt bleibt gespeichert.</p>
        <div class="unlock">
          ${PROFILES.map((p) => `<div class="unlock-col">
            <h4>${avatarHtml(avatarOf(p.id), "sm")} ${p.title}</h4>
            ${content.subjects.map((sub) => `
              <label class="field check subj"><input type="checkbox" class="en-box" data-p="${p.id}" data-id="${sub.id}" ${store.isEnabled(p.id, sub.id) ? "checked" : ""}> ${sub.image} ${esc(sub.title)}</label>
              ${sub.stages.map((st) => `
                <div class="unlock-topics">
                  <label class="field check subj"><input type="checkbox" class="en-box" data-p="${p.id}" data-id="${st.id}" ${store.isEnabled(p.id, st.id, stageDefault(p.id, st)) ? "checked" : ""}> ${esc(st.title)}</label>
                  <div class="unlock-topics">
                    ${st.units.map((u) => `<label class="field check"><input type="checkbox" class="en-box" data-p="${p.id}" data-id="${u.id}" ${store.isEnabled(p.id, u.id) ? "checked" : ""}> ${u.image} ${esc(u.title_de)}</label>`).join("")}
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
            <summary>${u.image} ${esc(u.title_de)} <span class="small">${PROFILES.map((p) => {
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
        <h3>Stimme</h3>
        <p class="small">${v.supported ? (v.british ? `Britische Stimme gefunden: ${esc(v.name)}` : "Keine britische Stimme gefunden. Bitte in den Android-Einstellungen unter „Sprachausgabe“ (Google) die Sprache „Englisch (Vereinigtes Königreich)“ herunterladen, dann funktioniert sie auch offline.") : "Dieses Gerät unterstützt keine Sprachausgabe."} Liegt für einen Inhalt eine Aufnahme im Ordner audio/en, wird stattdessen die Aufnahme abgespielt.</p>
        <button class="wide-btn" id="test">🔊 Stimme testen</button>
      </section>
      <section>
        <h3>Zurücksetzen</h3>
        <button class="wide-btn danger" id="reset">Gesamten Fortschritt löschen</button>
      </section>
      <p class="small center-text">Learnino Version ${APP_VERSION}</p>
    </div>`);
  $("back").onclick = showProfiles;
  fillPhotos();
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
