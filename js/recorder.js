// Kurze Aufnahme zum Selbstvergleich. Die Aufnahme bleibt nur im Arbeitsspeicher
// und wird beim Verlassen der Übung verworfen, nie gespeichert oder verschickt.

let stream = null;

export function canRecord() {
  return !!(navigator.mediaDevices?.getUserMedia && window.MediaRecorder);
}

export async function record(maxMs = 4000, onTick) {
  if (!stream) stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const rec = new MediaRecorder(stream);
  const chunks = [];
  rec.ondataavailable = (e) => e.data.size && chunks.push(e.data);
  const done = new Promise((resolve) => (rec.onstop = () => resolve(new Blob(chunks, { type: rec.mimeType }))));
  rec.start();
  const t0 = Date.now();
  const timer = setInterval(() => onTick && onTick(Math.min(1, (Date.now() - t0) / maxMs)), 100);
  const stopper = setTimeout(() => rec.state !== "inactive" && rec.stop(), maxMs);
  const api = {
    stop: () => rec.state !== "inactive" && rec.stop(),
    result: done.then((blob) => {
      clearInterval(timer);
      clearTimeout(stopper);
      return URL.createObjectURL(blob);
    })
  };
  return api;
}

export function playUrl(url) {
  return new Promise((resolve) => {
    const a = new Audio(url);
    a.onended = resolve;
    a.onerror = resolve;
    a.play().catch(resolve);
  });
}
