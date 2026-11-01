// Erkennt über das Mikrofon, DASS ein Kind etwas sagt (Lautstärke), nicht WAS es sagt.
// Läuft komplett auf dem Gerät, es wird nichts aufgenommen oder gespeichert.

let stream = null;
let ctx = null;
let analyser = null;
let denied = false;

export async function micReady() {
  if (analyser) return true;
  if (denied || !navigator.mediaDevices?.getUserMedia) return false;
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true }
    });
    ctx = new (window.AudioContext || window.webkitAudioContext)();
    const src = ctx.createMediaStreamSource(stream);
    analyser = ctx.createAnalyser();
    analyser.fftSize = 1024;
    src.connect(analyser);
    return true;
  } catch (e) {
    denied = true;
    return false;
  }
}

function level(buf) {
  analyser.getFloatTimeDomainData(buf);
  let sum = 0;
  for (let i = 0; i < buf.length; i++) sum += buf[i] * buf[i];
  return Math.sqrt(sum / buf.length);
}

// Wartet, bis das Kind einmal etwas sagt und danach kurz still ist.
// onLevel(0..1) zeigt die Lautstärke an. Gibt ein Objekt mit cancel() zurück.
export function listenOnce({ onLevel, onStart, onDone }) {
  if (!analyser) return { cancel() {} };
  if (ctx.state === "suspended") ctx.resume();
  const buf = new Float32Array(analyser.fftSize);
  let floor = 0.01;
  let calib = [];
  let voiced = 0;
  let quiet = 0;
  let started = false;
  let last = performance.now();
  let raf;
  let stopped = false;

  const tick = (now) => {
    if (stopped) return;
    const dt = now - last;
    last = now;
    const l = level(buf);
    if (calib !== null) {
      // Die ersten 300 ms: Grundrauschen im Raum messen
      calib.push(l);
      if (calib.length > 18) {
        calib.sort((a, b) => a - b);
        floor = calib[Math.floor(calib.length / 2)] || 0.01;
        calib = null;
      }
    } else {
      const threshold = Math.max(0.02, floor * 3);
      onLevel && onLevel(Math.min(1, l / (threshold * 3)));
      if (l > threshold) {
        voiced += dt;
        quiet = 0;
        if (!started && voiced > 200) {
          started = true;
          onStart && onStart();
        }
      } else {
        quiet += dt;
        if (!started && quiet > 400) voiced = 0;
        if (started && quiet > 600) {
          stopped = true;
          onDone && onDone();
          return;
        }
      }
    }
    raf = requestAnimationFrame(tick);
  };
  raf = requestAnimationFrame(tick);
  return {
    cancel() {
      stopped = true;
      cancelAnimationFrame(raf);
    }
  };
}
