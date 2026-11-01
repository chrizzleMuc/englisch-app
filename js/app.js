import { SUBJECTS, PROFILES, NUMBER_WORDS, PRAISE, PRAISE_EN, AVATAR } from "./data.js";
import { sayParts, sayEn, sayDe, stop, chime, voiceInfo } from "./speech.js";
import * as store from "./store.js";
import { micReady, listenOnce } from "./mic.js";

const app = document.getElementById("app");
let current = { profile: null, screen: null, subject: null };
let listening = null;

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
const topicById = (id) => SUBJECTS.flatMap((x) => x.topics).find((t) => t.id === id);
const prof = () => PROFILES.find((p) => p.id === current.profile);

function fill(text) {
  const p = prof();
  const data = store.profile(p.id);
  const name = (data.name || "").trim() || "Sam";
  const [ageEn, ageDe] = NUMBER_WORDS[p.age] || [String(p.age), String(p.age)];
  return text.replace("{name}", name).replace("{age}", ageEn).replace("{age_de}", ageDe);
}

function itemsOf(topic) {
  return topic.items.map((it) => ({ ...it, en: fill(it.en), de: fill(it.de), key: store.wordKey(topic.id, it.en) }));
}

function lessonsOf(topic) {
  const n = prof().perLesson;
  const items = itemsOf(topic);
  const out = [];
  for (let i = 0; i < items.length; i += n) out.push(items.slice(i, i + n));
  // Einen sehr kleinen Rest an die letzte Lektion hängen
  if (out.length > 1 && out[out.length - 1].length < 3) out[out.length - 2].push(...out.pop());
  return out;
}

function stars(n, max = 3) {
  let s = "";
  for (let i = 0; i < max; i++) s += `<span class="star ${i < n ? "on" : ""}">★</span>`;
  return s;
}

function render(html) {
  stop();
  if (listening) listening.cancel();
  listening = null;
  current.screen = null;
  app.innerHTML = html;
  app.scrollTop = 0;
  window.scrollTo(0, 0);
}

function on(sel, ev, fn) {
  app.querySelectorAll(sel).forEach((el) => el.addEventListener(ev, fn));
}

function speakerBtn(cls = "") {
  return `<button class="speaker ${cls}" aria-label="Anhören">🔊</button>`;
}

// ---------- Avatar ----------
function avatarOf(pid) {
  const p = PROFILES.find((x) => x.id === pid);
  const a = store.profile(pid).avatar;
  return a || { base: p.pic, color: pid === "pirat" ? "#74c0fc" : "#8ce99a" };
}

function avatarHtml(a, cls = "") {
  return `<span class="avatar ${cls}" style="--bg:${a.color}">
    <span class="av-base">${a.base}</span>
  </span>`;
}

function showAvatarEditor(first = false) {
  const pid = current.profile;
  const a = { ...avatarOf(pid) };
  const groups = [
    ["base", "Welches Tier bist du?"],
    ["color", "Hintergrundfarbe"]
  ];
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
          ${AVATAR[g].map(([v, en], i) => `<button class="av-opt ${a[g] === v ? "sel" : ""}" data-g="${g}" data-i="${i}" ${g === "color" ? `style="background:${v}"` : ""}>${g === "color" ? "" : v}</button>`).join("")}
        </div>`).join("")}
      <button class="go-btn" id="done">Fertig ✓</button>
    </div>`);
  const refresh = () => (app.querySelector(".av-preview").innerHTML = avatarHtml(a, "xl"));
  on(".av-opt", "click", (e) => {
    const { g, i } = e.currentTarget.dataset;
    const [v, en] = AVATAR[g][+i];
    a[g] = v;
    app.querySelectorAll(`.av-opt[data-g="${g}"]`).forEach((b) => b.classList.toggle("sel", b === e.currentTarget));
    refresh();
    chime("pop");
    if (en && v) sayEn(en);
  });
  document.getElementById("done").onclick = () => {
    store.profile(pid).avatar = { base: a.base, color: a.color };
    store.save();
    chime("win");
    showHome();
  };
  if (!first) document.getElementById("back").onclick = () => showHome();
  if (first && !prof().reads) sayDe("Welches Tier willst du sein? Such dir eins aus!");
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
        ${PROFILES.map((p) => {
          const d = store.profile(p.id);
          return `<button class="profile-card" data-id="${p.id}">
            ${avatarHtml(avatarOf(p.id), "lg")}
            <span class="pname">${esc(p.title)}</span>
            ${d.name ? `<span class="small">${esc(d.name)}</span>` : ""}
            <span class="small">⭐ ${store.totalStars(p.id)}</span>
          </button>`;
        }).join("")}
      </div>
      <button class="link-btn" id="parents">🔒 Elternbereich</button>
    </div>`);
  on(".profile-card", "click", (e) => {
    current.profile = e.currentTarget.dataset.id;
    chime("pop");
    if (store.profile(current.profile).avatar) showHome();
    else showAvatarEditor(true);
  });
  document.getElementById("parents").onclick = showParentGate;
}

// ---------- Startseite mit Themen ----------
function topicProgress(topic) {
  const ls = lessonsOf(topic);
  const done = ls.filter((_, i) => store.lessonStars(current.profile, topic.id, i) > 0).length;
  return { done, total: ls.length };
}

function topicsFor(pid, subject) {
  return subject.topics.filter((t) => !t.soon && store.isEnabled(pid, t.id));
}

function subjectsFor(pid) {
  return SUBJECTS.filter((sub) => store.isEnabled(pid, sub.id) && topicsFor(pid, sub).length);
}

function homeHeader(p, backId = "back") {
  return `<header class="bar">
        <button class="icon-btn" id="${backId}" aria-label="Zurück">⬅</button>
        <button class="who who-btn" id="me" aria-label="Bild ändern">${avatarHtml(avatarOf(p.id), "sm")} ${esc(p.title)} <span class="pencil">✏️</span></button>
        <span class="stat">🔥 ${store.streakCount(p.id)}</span>
        <span class="stat">⭐ ${store.totalStars(p.id)}</span>
      </header>`;
}

function showHome(subjectId = current.subject) {
  const p = prof();
  const subs = subjectsFor(p.id);
  let sub = subs.find((x) => x.id === subjectId);
  if (!sub && subs.length === 1) sub = subs[0];
  if (!sub) return showSubjects(subs);
  current.subject = sub.id;
  const many = subs.length > 1;
  render(`
    <div class="screen">
      ${homeHeader(p)}
      ${many ? `<h2 class="subject-title">${sub.pic} ${sub.title}</h2>` : ""}
      <div class="topics">
        ${topicsFor(p.id, sub).map((t) => {
          const pr = topicProgress(t);
          return `<button class="topic" data-id="${t.id}" style="--c:${t.color}">
            <span class="big-pic">${t.pic}</span>
            <span class="tname">${t.title}</span>
            <span class="meter"><span style="width:${(pr.done / pr.total) * 100}%"></span></span>
          </button>`;
        }).join("")}
      </div>
      <button class="wide-btn album-btn" id="album">📒 Mein Sticker-Album</button>
    </div>`);
  document.getElementById("back").onclick = () => {
    current.subject = null;
    many ? showSubjects(subs) : showProfiles();
  };
  document.getElementById("album").onclick = showAlbum;
  document.getElementById("me").onclick = () => showAvatarEditor(false);
  on(".topic[data-id]", "click", (e) => {
    chime("pop");
    showTopic(e.currentTarget.dataset.id);
  });
  if (!p.reads) sayDe("Such dir ein Thema aus!");
}

function showSubjects(subs) {
  const p = prof();
  current.subject = null;
  render(`
    <div class="screen">
      ${homeHeader(p)}
      ${subs.length ? `<div class="topics">
        ${subs.map((x) => `<button class="topic subject" data-id="${x.id}" style="--c:${x.color}">
          <span class="big-pic">${x.pic}</span><span class="tname">${x.title}</span></button>`).join("")}
      </div>` : `<p class="sub center-text">Hier ist noch nichts freigeschaltet. Frag Mama oder Papa!</p>`}
    </div>`);
  document.getElementById("back").onclick = showProfiles;
  document.getElementById("me").onclick = () => showAvatarEditor(false);
  on(".subject", "click", (e) => {
    chime("pop");
    showHome(e.currentTarget.dataset.id);
  });
  if (!p.reads) sayDe(subs.length ? "Was willst du heute lernen?" : "Hier ist noch nichts freigeschaltet.");
}

// ---------- Themenseite mit Lektionen ----------
function showTopic(topicId) {
  const t = topicById(topicId);
  const ls = lessonsOf(t);
  const firstDone = store.lessonStars(current.profile, t.id, 0) > 0;
  render(`
    <div class="screen">
      <header class="bar">
        <button class="icon-btn" id="back" aria-label="Zurück">⬅</button>
        <span class="who">${t.pic} ${t.title}</span>
      </header>
      <div class="path">
        ${ls.map((items, i) => {
          const s = store.lessonStars(current.profile, t.id, i);
          const open = i === 0 || store.lessonStars(current.profile, t.id, i - 1) > 0;
          return `<button class="node ${open ? "" : "locked"} ${i % 2 ? "right" : "left"}" data-i="${i}" ${open ? "" : "disabled"} style="--c:${t.color}">
            <span class="node-pics">${open ? items.slice(0, 3).map((x) => x.pic).join("") : "🔒"}</span>
            <span class="node-stars">${stars(s)}</span>
          </button>`;
        }).join("")}
      </div>
      <button class="wide-btn" id="memory" ${firstDone ? "" : "disabled"} style="--c:${t.color}">🃏 Memory spielen${firstDone ? "" : " (nach Lektion 1)"}</button>
    </div>`);
  document.getElementById("back").onclick = () => showHome();
  on(".node:not(.locked)", "click", (e) => startLesson(t.id, +e.currentTarget.dataset.i));
  document.getElementById("memory").onclick = () => firstDone && startMemory(t.id);
}

// ---------- Lektion ----------
function buildSteps(topic, idx) {
  const p = prof();
  const ls = lessonsOf(topic);
  const fresh = ls[idx];
  const earlier = ls.slice(0, idx).flat();
  const pd = store.profile(p.id);
  // Wiederholung: bis zu 2 frühere Wörter, schwierige zuerst
  const review = earlier
    .map((it) => ({ it, score: (pd.words[it.key]?.w || 0) - (pd.words[it.key]?.c || 0) * 0.3 + Math.random() }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 2)
    .map((x) => x.it);

  const steps = fresh.map((it) => ({ kind: "learn", item: it }));
  const pool = itemsOf(topic);
  let quiz = [];
  const quizKinds = topic.type === "phrases" ? (p.reads ? ["situation", "meaning"] : ["situation", "situation"]) : p.reads ? ["listen", "word"] : ["listen", "listen"];
  fresh.forEach((it) => quizKinds.forEach((k) => quiz.push({ kind: k, item: it })));
  review.forEach((it) => quiz.push({ kind: quizKinds[0], item: it }));
  quiz = shuffle(quiz);
  // Nicht zweimal hintereinander dasselbe Wort
  for (let i = 1; i < quiz.length; i++) {
    if (quiz[i].item.key === quiz[i - 1].item.key) {
      const j = quiz.findIndex((q, k) => k > i && q.item.key !== quiz[i].item.key);
      if (j > 0) [quiz[i], quiz[j]] = [quiz[j], quiz[i]];
    }
  }
  const known = [...earlier, ...fresh];
  return { steps: [...steps, ...quiz], pool, known };
}

function startLesson(topicId, idx) {
  const topic = topicById(topicId);
  const { steps, pool, known } = buildSteps(topic, idx);
  const lesson = { topic, idx, steps, pool, known, pos: 0, mistakes: 0, retried: new Set(), total: steps.length };
  nextStep(lesson);
}

function lessonFrame(lesson, inner) {
  const pct = Math.round((lesson.pos / lesson.steps.length) * 100);
  return `
    <div class="screen lesson" style="--c:${lesson.topic.color}">
      <header class="bar">
        <button class="icon-btn" id="quit" aria-label="Beenden">✖</button>
        <div class="progress"><span style="width:${pct}%"></span></div>
      </header>
      ${inner}
    </div>`;
}

function bindQuit(lesson) {
  document.getElementById("quit").onclick = () => showTopic(lesson.topic.id);
}

function nextStep(lesson) {
  if (lesson.pos >= lesson.steps.length) return finishLesson(lesson);
  const step = lesson.steps[lesson.pos];
  ({ learn: stepLearn, listen: stepListen, word: stepWord, situation: stepSituation, meaning: stepMeaning })[step.kind](lesson, step);
}

function advance(lesson) {
  lesson.pos++;
  nextStep(lesson);
}

function distractors(lesson, item, n) {
  // Bevorzugt bekannte Wörter, sonst andere aus dem Thema
  let pool = lesson.known.filter((x) => x.key !== item.key);
  if (pool.length < n) pool = pool.concat(lesson.pool.filter((x) => x.key !== item.key && !pool.some((p) => p.key === x.key)));
  return shuffle(pool).slice(0, n);
}

function answered(lesson, step, correct) {
  store.recordAnswer(current.profile, step.item.key, correct);
  if (!correct) {
    lesson.mistakes++;
    // Falsch beantwortete Aufgabe einmal am Ende wiederholen
    if (!lesson.retried.has(lesson.pos)) {
      lesson.retried.add(lesson.steps.length);
      lesson.steps.push({ ...step });
    }
  }
}

// 1) Kennenlernen (mit Nachsprechen)
const TIMES = ["", "einmal", "zweimal", "dreimal", "viermal", "fünfmal"];

function stepLearn(lesson, step) {
  const p = prof();
  const it = step.item;
  const need = store.settings().repeat || 0;
  render(lessonFrame(lesson, `
    <p class="task">Neu! Hör gut zu.</p>
    <div class="learn-card">
      <span class="huge-pic">${it.pic}</span>
      <span class="en ${p.reads ? "" : "faint"}">${esc(it.en)}</span>
      <span class="de">${esc(it.de)}</span>
    </div>
    <div class="row">
      ${speakerBtn("big")}
      <button class="speaker big" id="slow" aria-label="Langsam anhören">🐢</button>
    </div>
    ${need ? `<div class="repeat">
      <p class="repeat-task">Jetzt du! Sag es ${TIMES[need] || need + "-mal"} laut nach.</p>
      <div class="dots">${Array.from({ length: need }, () => `<span class="dot"></span>`).join("")}</div>
      <button class="mic" id="mic" aria-label="Zuhören">🎤<span class="ring"></span></button>
      <button class="wide-btn said" id="said" hidden>🗣️ Ich hab's gesagt</button>
    </div>` : ""}
    <button class="go-btn" id="next" ${need ? "disabled" : ""}>Weiter ➜</button>`));
  bindQuit(lesson);
  const nextBtn = document.getElementById("next");
  nextBtn.onclick = () => advance(lesson);
  document.getElementById("slow").onclick = () => replay({ slow: true });
  on(".speaker:not(#slow)", "click", () => replay());

  if (!need) {
    setTimeout(() => sayParts([["en", it.en], ["de", it.de], ["en", it.en]]), 250);
    return;
  }

  let count = 0;
  let useMic = false;
  let fallbackTimer = null;
  const micBtn = document.getElementById("mic");
  const saidBtn = document.getElementById("said");
  const dots = app.querySelectorAll(".dot");
  const token = (current.screen = {});
  const alive = () => current.screen === token;

  const stopListening = () => {
    if (listening) listening.cancel();
    listening = null;
    clearTimeout(fallbackTimer);
    micBtn.classList.remove("on", "hear");
    micBtn.style.setProperty("--lvl", 0);
  };

  const listen = () => {
    if (!alive() || count >= need) return;
    if (!useMic) {
      saidBtn.hidden = false;
      return;
    }
    micBtn.classList.add("on");
    // Wenn nach 8 Sekunden nichts gehört wurde, auch den Knopf anbieten
    fallbackTimer = setTimeout(() => alive() && (saidBtn.hidden = false), 8000);
    listening = listenOnce({
      onLevel: (l) => micBtn.style.setProperty("--lvl", l.toFixed(2)),
      onStart: () => micBtn.classList.add("hear"),
      onDone: () => {
        stopListening();
        counted();
      }
    });
  };

  const counted = async () => {
    if (!alive() || count >= need) return;
    dots[count].classList.add("on");
    count++;
    store.recordSpoken(current.profile, it.key);
    if (count >= need) {
      chime("good");
      saidBtn.hidden = true;
      micBtn.hidden = true;
      app.querySelector(".repeat-task").innerHTML = `<span class="ok">${pick(PRAISE)}</span>`;
      nextBtn.disabled = false;
      nextBtn.classList.add("pulse");
      await sayEn(pick(PRAISE_EN));
      return;
    }
    chime("pop");
    await wait(250);
    if (!alive()) return;
    await sayEn(it.en);
    await wait(200);
    listen();
  };

  async function replay(opts) {
    stopListening();
    await sayEn(it.en, opts);
    await wait(200);
    listen();
  }

  saidBtn.onclick = () => {
    stopListening();
    counted();
  };
  micBtn.onclick = () => replay();

  (async () => {
    useMic = store.settings().mic && (await micReady());
    if (!alive()) return;
    await wait(150);
    await sayParts([["en", it.en], ["de", it.de], ["en", it.en]]);
    if (!alive()) return;
    if (lesson.pos === 0 && !p.reads) await sayDe(`Jetzt du! Sag es ${TIMES[need] || need + " mal"} nach.`);
    if (!alive()) return;
    await wait(150);
    listen();
  })();
}

// Gemeinsame Logik für Auswahlaufgaben
function choiceStep(lesson, step, { task, prompt, options, optionHtml, speak, checkMode }) {
  render(lessonFrame(lesson, `
    <p class="task">${task}</p>
    ${prompt}
    <div class="choices n${options.length}">
      ${options.map((o, i) => `<button class="choice" data-i="${i}">${optionHtml(o)}</button>`).join("")}
    </div>
    ${checkMode ? `<button class="go-btn" id="check" disabled>Prüfen ✓</button>` : ""}
    <div class="feedback" id="fb"></div>`));
  bindQuit(lesson);
  on(".again", "click", () => speak());
  let locked = false;
  let selected = null;

  const judge = async (i, el) => {
    if (locked) return;
    const ok = options[i].key === step.item.key;
    const fb = document.getElementById("fb");
    if (ok) {
      locked = true;
      el.classList.add("right");
      chime("good");
      const praise = pick(PRAISE);
      fb.innerHTML = `<span class="ok">${praise}</span>`;
      answered(lesson, step, true);
      await sayParts([["en", step.item.en]]);
      await wait(400);
      advance(lesson);
    } else {
      el.classList.add("wrong");
      el.disabled = true;
      chime("bad");
      if (!el.dataset.counted) {
        el.dataset.counted = "1";
        if (!lesson._wrongHere) {
          lesson._wrongHere = true;
          answered(lesson, step, false);
        }
      }
      fb.innerHTML = `<span class="try">Fast! Versuch es nochmal.</span>`;
      if (checkMode) {
        selected = null;
        document.getElementById("check").disabled = true;
      }
    }
  };

  on(".choice", "click", (e) => {
    const el = e.currentTarget;
    const i = +el.dataset.i;
    if (checkMode) {
      app.querySelectorAll(".choice").forEach((c) => c.classList.remove("sel"));
      el.classList.add("sel");
      selected = i;
      document.getElementById("check").disabled = false;
      sayEn(options[i].en);
    } else judge(i, el);
  });
  if (checkMode) document.getElementById("check").onclick = () => selected !== null && judge(selected, app.querySelector(`.choice[data-i="${selected}"]`));
  lesson._wrongHere = false;
  setTimeout(speak, 250);
}

// 2) Hör zu und tipp das richtige Bild
function stepListen(lesson, step) {
  const n = prof().reads ? 4 : 3;
  const options = shuffle([step.item, ...distractors(lesson, step.item, n - 1)]);
  const speak = () => sayParts([["de", "Wo ist"], ["en", step.item.en]]);
  choiceStep(lesson, step, {
    task: "Hör zu und tipp das richtige Bild!",
    prompt: `<div class="row">${speakerBtn("big again")}</div>`,
    options,
    optionHtml: (o) => `<span class="huge-pic">${o.pic}</span>`,
    speak
  });
}

// 3) Wort zum Bild (nur Pirat)
function stepWord(lesson, step) {
  const options = shuffle([step.item, ...distractors(lesson, step.item, 3)]);
  choiceStep(lesson, step, {
    task: "Welches Wort passt zum Bild?",
    prompt: `<div class="prompt-pic">${step.item.pic}</div>`,
    options,
    optionHtml: (o) => `<span class="word">${esc(o.en)}</span>`,
    speak: () => {}
  });
}

// 4) Was sagst du? (Redewendungen)
function stepSituation(lesson, step) {
  const p = prof();
  const options = shuffle([step.item, ...distractors(lesson, step.item, 2)]);
  const situation = fill(lesson.topic.items.find((x) => store.wordKey(lesson.topic.id, x.en) === step.item.key).situation);
  const speak = () => sayDe(situation);
  choiceStep(lesson, step, {
    task: esc(situation),
    prompt: `<div class="row">${speakerBtn("big again")}</div><p class="hint">Tipp auf eine Karte zum Anhören. Dann auf „Prüfen“.</p>`,
    options,
    optionHtml: (o) => `<span class="mid-pic">${o.pic}</span><span class="word ${p.reads ? "" : "faint"}">${esc(o.en)}</span>`,
    speak,
    checkMode: true
  });
}

// 5) Was bedeutet das? (Redewendungen, nur Pirat)
function stepMeaning(lesson, step) {
  const others = distractors(lesson, step.item, 3);
  const options = shuffle([step.item, ...others]);
  choiceStep(lesson, step, {
    task: "Was bedeutet das?",
    prompt: `<div class="row">${speakerBtn("big again")}</div>`,
    options,
    optionHtml: (o) => `<span class="word">${esc(o.de)}</span>`,
    speak: () => sayEn(step.item.en)
  });
}

function finishLesson(lesson) {
  const s = lesson.mistakes <= 1 ? 3 : lesson.mistakes <= 3 ? 2 : 1;
  const pid = current.profile;
  const firstTime = store.lessonStars(pid, lesson.topic.id, lesson.idx) === 0;
  store.setLessonStars(pid, lesson.topic.id, lesson.idx, s);
  const streak = store.touchStreak(pid);
  store.save();
  const newOnes = lessonsOf(lesson.topic)[lesson.idx];
  render(`
    <div class="screen center result" style="--c:${lesson.topic.color}">
      <h2>${pick(PRAISE)}</h2>
      <div class="result-stars">${stars(s)}</div>
      <p class="sub">🔥 ${streak.count} ${streak.count === 1 ? "Tag" : "Tage"} in Folge</p>
      ${firstTime ? `<p class="sub">Neue Sticker für dein Album:</p><div class="stickers">${newOnes.map((x) => `<span class="sticker">${x.pic}</span>`).join("")}</div>` : ""}
      <button class="go-btn" id="next">Weiter ➜</button>
    </div>`);
  chime("win");
  setTimeout(() => sayEn(pick(PRAISE_EN)), 600);
  document.getElementById("next").onclick = () => showTopic(lesson.topic.id);
}

// ---------- Memory ----------
function startMemory(topicId) {
  const topic = topicById(topicId);
  const p = prof();
  const ls = lessonsOf(topic);
  const learned = ls.filter((_, i) => store.lessonStars(current.profile, topic.id, i) > 0).flat();
  const pairs = shuffle(learned).slice(0, p.reads ? 6 : 4);
  const cards = shuffle(pairs.flatMap((it) => [
    { key: it.key, it, face: "pic" },
    { key: it.key, it, face: p.reads ? "word" : "sound" }
  ]));
  let open = [];
  let found = 0;
  let tries = 0;
  render(`
    <div class="screen" style="--c:${topic.color}">
      <header class="bar">
        <button class="icon-btn" id="back" aria-label="Zurück">⬅</button>
        <span class="who">🃏 Memory</span>
      </header>
      <p class="task">${p.reads ? "Finde Bild und Wort, die zusammengehören." : "Finde Bild und Ton, die zusammengehören."}</p>
      <div class="memory n${cards.length}">
        ${cards.map((c, i) => `<button class="mcard" data-i="${i}"><span class="back">?</span><span class="front">${c.face === "pic" ? c.it.pic : c.face === "word" ? `<span class="word">${esc(c.it.en)}</span>` : "🔊"}</span></button>`).join("")}
      </div>
    </div>`);
  document.getElementById("back").onclick = () => showTopic(topic.id);
  on(".mcard", "click", async (e) => {
    const el = e.currentTarget;
    const c = cards[+el.dataset.i];
    if (el.classList.contains("flip") || open.length === 2) return;
    el.classList.add("flip");
    sayEn(c.it.en);
    open.push({ el, c });
    if (open.length === 2) {
      tries++;
      const [a, b] = open;
      if (a.c.key === b.c.key) {
        await wait(500);
        chime("good");
        a.el.classList.add("done");
        b.el.classList.add("done");
        open = [];
        found++;
        if (found === pairs.length) {
          await wait(600);
          chime("win");
          sayEn(pick(PRAISE_EN));
          app.querySelector(".task").innerHTML = `<span class="ok">Geschafft in ${tries} Zügen!</span> <button class="go-btn inline" id="again">Nochmal 🔄</button>`;
          document.getElementById("again").onclick = () => startMemory(topic.id);
          store.touchStreak(current.profile);
          store.save();
        }
      } else {
        await wait(1300);
        a.el.classList.remove("flip");
        b.el.classList.remove("flip");
        open = [];
      }
    }
  });
}

// ---------- Sticker-Album ----------
function showAlbum() {
  const pid = current.profile;
  render(`
    <div class="screen">
      <header class="bar">
        <button class="icon-btn" id="back" aria-label="Zurück">⬅</button>
        <span class="who">📒 Sticker-Album</span>
      </header>
      ${subjectsFor(current.profile).flatMap((sub) => topicsFor(current.profile, sub)).map((t) => {
        const ls = lessonsOf(t);
        return `<h3 class="album-title">${t.pic} ${t.title}</h3>
          <div class="album">${ls.map((items, i) => items.map((it) => {
            const has = store.lessonStars(pid, t.id, i) > 0;
            return `<button class="sticker ${has ? "" : "empty"}" data-en="${esc(it.en)}" ${has ? "" : "disabled"}>${has ? it.pic : "?"}</button>`;
          }).join("")).join("")}</div>`;
      }).join("")}
    </div>`);
  document.getElementById("back").onclick = () => showHome();
  on(".sticker:not(.empty)", "click", (e) => sayEn(e.currentTarget.dataset.en));
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
  document.getElementById("back").onclick = showProfiles;
  document.getElementById("ok").onclick = () => {
    if (+document.getElementById("ans").value === a * b) showParents();
    else document.getElementById("ans").value = "";
  };
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
      <section>
        <h3>Vornamen</h3>
        <p class="small">Wird nur für den Satz „My name is …“ benutzt und bleibt auf diesem Gerät.</p>
        ${PROFILES.map((p) => `<label class="field">${p.pic} ${p.title} <input class="input name" data-id="${p.id}" value="${esc(store.profile(p.id).name || "")}" placeholder="Vorname"></label>`).join("")}
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
        <h3>Freigeschaltet</h3>
        <p class="small">Was soll das Kind sehen? Ausgeschaltete Fächer und Themen verschwinden, der Fortschritt bleibt gespeichert.</p>
        <div class="unlock">
          ${PROFILES.map((p) => `<div class="unlock-col">
            <h4>${p.pic} ${p.title}</h4>
            ${SUBJECTS.map((sub) => `
              <label class="field check subj"><input type="checkbox" class="en-box" data-p="${p.id}" data-id="${sub.id}" ${store.isEnabled(p.id, sub.id) ? "checked" : ""}> ${sub.pic} ${sub.title}</label>
              <div class="unlock-topics">
                ${sub.topics.filter((t) => !t.soon).map((t) => `<label class="field check"><input type="checkbox" class="en-box" data-p="${p.id}" data-id="${t.id}" ${store.isEnabled(p.id, t.id) ? "checked" : ""}> ${t.pic} ${t.title}</label>`).join("")}
              </div>`).join("")}
          </div>`).join("")}
        </div>
      </section>
      <section>
        <h3>Nachsprechen</h3>
        <p class="small">Beim Kennenlernen müssen die Kinder jedes neue Wort so oft laut nachsprechen, bevor es weitergeht.</p>
        <label class="field">Wie oft?
          <select class="input" id="repeat">
            ${[[0, "Aus"], [1, "1-mal"], [2, "2-mal"], [3, "3-mal"], [5, "5-mal"]].map(([v, t]) => `<option value="${v}" ${store.settings().repeat === v ? "selected" : ""}>${t}</option>`).join("")}
          </select>
        </label>
        <label class="field check"><input type="checkbox" id="usemic" ${store.settings().mic ? "checked" : ""}> Mikrofon nutzen</label>
        <p class="small">Mit Mikrofon zählt die App automatisch, sobald ein Kind etwas sagt. Sie prüft dabei nur, <b>dass</b> gesprochen wird, nicht ob die Aussprache stimmt. Es wird nichts aufgenommen oder gespeichert. Ohne Mikrofon tippt das Kind nach jedem Mal auf „Ich hab's gesagt“.</p>
      </section>
      <section>
        <h3>Stimme</h3>
        <p class="small">${v.supported ? (v.british ? `Britische Stimme gefunden: ${esc(v.name)}` : "Keine britische Stimme gefunden. Bitte in den Android-Einstellungen unter „Sprachausgabe“ (Google) die Sprache „Englisch (Vereinigtes Königreich)“ herunterladen, dann funktioniert sie auch offline.") : "Dieses Gerät unterstützt keine Sprachausgabe."}</p>
        <button class="wide-btn" id="test">🔊 Stimme testen</button>
      </section>
      <section>
        <h3>Zurücksetzen</h3>
        <button class="wide-btn danger" id="reset">Gesamten Fortschritt löschen</button>
      </section>
      <p class="small center-text">Learnino Version ${APP_VERSION}</p>
    </div>`);
  document.getElementById("back").onclick = showProfiles;
  on(".name", "change", (e) => {
    store.profile(e.target.dataset.id).name = e.target.value.trim().slice(0, 20);
    store.save();
  });
  on(".en-box", "change", (e) => {
    store.setEnabled(e.target.dataset.p, e.target.dataset.id, e.target.checked);
    store.save();
  });
  document.getElementById("repeat").onchange = (e) => {
    store.settings().repeat = +e.target.value;
    store.save();
  };
  document.getElementById("usemic").onchange = (e) => {
    store.settings().mic = e.target.checked;
    store.save();
  };
  document.getElementById("test").onclick = () => sayParts([["en", "Hello! My name is Learnino. Let's learn English!"]]);
  document.getElementById("export").onclick = async () => {
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
  document.getElementById("import").onchange = async (e) => {
    const f = e.target.files[0];
    if (!f) return;
    try {
      store.importData(await f.text());
      showParents("✅ Fortschritt geladen.");
    } catch (err) {
      showParents("⚠️ Diese Datei konnte nicht geladen werden.");
    }
  };
  document.getElementById("reset").onclick = () => {
    if (confirm("Wirklich den gesamten Fortschritt beider Kinder löschen?")) {
      store.resetAll();
      showParents("Fortschritt gelöscht.");
    }
  };
}

// ---------- Start ----------
const APP_VERSION = 6;

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
showProfiles();
