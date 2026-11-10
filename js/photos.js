// Fotos von Heft-Aufgaben: werden verkleinert und nur auf diesem Gerät gespeichert (IndexedDB).
// Sie sind NICHT in der Sicherungsdatei enthalten, weil die Datei sonst sehr groß würde.

const DB = "learnino-fotos";
const STORE = "fotos";
let dbPromise = null;

function db() {
  if (!dbPromise) {
    dbPromise = new Promise((resolve, reject) => {
      const req = indexedDB.open(DB, 1);
      req.onupgradeneeded = () => req.result.createObjectStore(STORE, { keyPath: "id", autoIncrement: true });
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }
  return dbPromise;
}

async function tx(mode, fn) {
  const d = await db();
  return new Promise((resolve, reject) => {
    const t = d.transaction(STORE, mode);
    const out = fn(t.objectStore(STORE));
    t.oncomplete = () => resolve(out && "result" in out ? out.result : undefined);
    t.onerror = () => reject(t.error);
  });
}

// Bild auf höchstens 1400 Pixel verkleinern, damit der Speicher nicht vollläuft
export async function shrink(file, max = 1400) {
  const url = URL.createObjectURL(file);
  try {
    const img = await new Promise((resolve, reject) => {
      const i = new Image();
      i.onload = () => resolve(i);
      i.onerror = reject;
      i.src = url;
    });
    const f = Math.min(1, max / Math.max(img.naturalWidth, img.naturalHeight));
    const c = document.createElement("canvas");
    c.width = Math.round(img.naturalWidth * f);
    c.height = Math.round(img.naturalHeight * f);
    c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
    return await new Promise((resolve) => c.toBlob((b) => resolve(b || file), "image/jpeg", 0.75));
  } catch (e) {
    return file;
  } finally {
    URL.revokeObjectURL(url);
  }
}

// entry: { pid, taskId, unitTitle, task, blob }
export function addPhoto(entry) {
  return tx("readwrite", (s) => s.add({ ...entry, date: new Date().toISOString(), status: "neu" }));
}

export async function allPhotos() {
  try {
    const list = await tx("readonly", (s) => s.getAll());
    return (list || []).sort((a, b) => b.date.localeCompare(a.date));
  } catch (e) {
    return [];
  }
}

export async function setStatus(id, status) {
  const d = await db();
  return new Promise((resolve, reject) => {
    const t = d.transaction(STORE, "readwrite");
    const s = t.objectStore(STORE);
    const g = s.get(id);
    g.onsuccess = () => {
      if (g.result) s.put({ ...g.result, status });
    };
    t.oncomplete = resolve;
    t.onerror = () => reject(t.error);
  });
}

export function deletePhoto(id) {
  return tx("readwrite", (s) => s.delete(id));
}
