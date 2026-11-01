// Sprachausgabe über die eingebaute Stimme des Geräts (Web Speech API).
// Englisch wird mit britischer Stimme (en-GB) gesprochen, Anweisungen auf Deutsch (de-DE).

const synth = window.speechSynthesis;
let voices = [];

function loadVoices() {
  if (!synth) return;
  voices = synth.getVoices();
}
loadVoices();
if (synth && "onvoiceschanged" in synth) synth.onvoiceschanged = loadVoices;

function pickVoice(lang) {
  const want = lang.toLowerCase();
  const base = want.split("-")[0];
  const norm = (v) => v.lang.toLowerCase().replace("_", "-");
  const exact = voices.filter((v) => norm(v) === want);
  // Offline-Stimmen bevorzugen
  return (
    exact.find((v) => v.localService) ||
    exact[0] ||
    voices.find((v) => norm(v).startsWith(base) && v.localService) ||
    voices.find((v) => norm(v).startsWith(base)) ||
    null
  );
}

export function hasSpeech() {
  return !!synth;
}

export function voiceInfo() {
  loadVoices();
  const gb = pickVoice("en-GB");
  const anyEn = pickVoice("en");
  return {
    supported: !!synth,
    british: !!(gb && gb.lang.toLowerCase().replace("_", "-") === "en-gb"),
    name: gb ? gb.name : anyEn ? anyEn.name : null
  };
}

export function stop() {
  if (synth) synth.cancel();
}

function sayOne(text, lang, rate, pitch = 1.05) {
  return new Promise((resolve) => {
    if (!synth) return resolve();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = lang;
    const v = pickVoice(lang);
    if (v) u.voice = v;
    u.rate = rate;
    u.pitch = pitch;
    let done = false;
    const finish = () => {
      if (!done) {
        done = true;
        resolve();
      }
    };
    u.onend = finish;
    u.onerror = finish;
    // Sicherheitsnetz, falls ein Gerät "onend" nicht meldet
    setTimeout(finish, 1500 + text.length * 160);
    synth.speak(u);
  });
}

// Spricht mehrere Teile nacheinander, z. B. [["de","Wo ist"],["en","cat"]]
export async function sayParts(parts, { slow = false, pitch, keep = false } = {}) {
  if (!keep) stop();
  for (const [lang, text] of parts) {
    const isEn = lang === "en";
    await sayOne(text, isEn ? "en-GB" : "de-DE", isEn ? (slow ? 0.55 : 0.85) : 1.0, pitch);
  }
}

export function sayEn(text, opts) {
  return sayParts([["en", text]], opts);
}

export function sayDe(text) {
  return sayParts([["de", text]]);
}

// Kleine Klänge für richtig/falsch, ganz ohne Audiodateien
let ctx;
function tone(freq, start, dur, type = "sine", vol = 0.18) {
  ctx = ctx || new (window.AudioContext || window.webkitAudioContext)();
  const o = ctx.createOscillator();
  const g = ctx.createGain();
  o.type = type;
  o.frequency.value = freq;
  g.gain.setValueAtTime(vol, ctx.currentTime + start);
  g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + start + dur);
  o.connect(g).connect(ctx.destination);
  o.start(ctx.currentTime + start);
  o.stop(ctx.currentTime + start + dur);
}

export function chime(kind) {
  try {
    if (kind === "good") {
      tone(660, 0, 0.15);
      tone(880, 0.12, 0.25);
    } else if (kind === "bad") {
      tone(220, 0, 0.25, "triangle", 0.12);
    } else if (kind === "win") {
      [523, 659, 784, 1047].forEach((f, i) => tone(f, i * 0.12, 0.3));
    } else if (kind === "pop") {
      tone(520, 0, 0.08, "sine", 0.1);
    }
  } catch (e) {
    /* Klang ist nicht wichtig */
  }
}
