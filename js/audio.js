// Spielt einen Inhalt ab: zuerst eine echte Aufnahme aus audio/en/<ID>.mp3,
// wenn es keine gibt, spricht die Stimme des Tablets.

import { sayParts, stop as stopSpeech } from "./speech.js";

const missing = new Set();
let current = null;

export function stopAudio() {
  if (current) {
    current.pause();
    current = null;
  }
  stopSpeech();
}

function tryFile(id) {
  return new Promise((resolve) => {
    if (!id || missing.has(id)) return resolve(false);
    const a = new Audio(`audio/en/${id}.mp3`);
    let started = false;
    a.onplaying = () => (started = true);
    a.onended = () => resolve(true);
    a.onerror = () => {
      missing.add(id);
      resolve(started);
    };
    current = a;
    a.play().catch(() => {
      missing.add(id);
      resolve(false);
    });
  });
}

// item: { id, en }  opts: { slow, pitch }
export async function play(item, opts = {}) {
  stopAudio();
  if (!opts.slow && (await tryFile(item.id))) return;
  await sayParts([["en", item.en]], opts);
}

// Deutsche Anweisung, gefolgt von einem englischen Inhalt
export async function promptAnd(de, item, opts = {}) {
  stopAudio();
  await sayParts([["de", de]]);
  if (await tryFile(item.id)) return;
  await sayParts([["en", item.en]], { ...opts, keep: true });
}
