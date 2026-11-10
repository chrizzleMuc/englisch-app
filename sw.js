// Offline-Speicher: Bei jeder Änderung an der App VERSION erhöhen.
const VERSION = "learnino-11";
const FILES = [
  "./",
  "index.html",
  "manifest.webmanifest",
  "css/style.css",
  "js/app.js",
  "js/data.js",
  "js/speech.js",
  "js/store.js",
  "js/audio.js",
  "js/recorder.js",
  "js/content.js",
  "js/photos.js",
  "js/pics.js",
  "img/emoji/1f319.webp",
  "img/emoji/1f31e.webp",
  "img/emoji/1f33b.webp",
  "img/emoji/1f34c.webp",
  "img/emoji/1f34e.webp",
  "img/emoji/1f353.webp",
  "img/emoji/1f37d.webp",
  "img/emoji/1f381.webp",
  "img/emoji/1f382.webp",
  "img/emoji/1f383.webp",
  "img/emoji/1f384.webp",
  "img/emoji/1f388.webp",
  "img/emoji/1f389.webp",
  "img/emoji/1f3a8.webp",
  "img/emoji/1f3e0.webp",
  "img/emoji/1f411.webp",
  "img/emoji/1f41f.webp",
  "img/emoji/1f426.webp",
  "img/emoji/1f42d.webp",
  "img/emoji/1f42e.webp",
  "img/emoji/1f430.webp",
  "img/emoji/1f431.webp",
  "img/emoji/1f434.webp",
  "img/emoji/1f436.webp",
  "img/emoji/1f437.webp",
  "img/emoji/1f440.webp",
  "img/emoji/1f442.webp",
  "img/emoji/1f443.webp",
  "img/emoji/1f444.webp",
  "img/emoji/1f448.webp",
  "img/emoji/1f449.webp",
  "img/emoji/1f44b.webp",
  "img/emoji/1f44f.webp",
  "img/emoji/1f450.webp",
  "img/emoji/1f466.webp",
  "img/emoji/1f467.webp",
  "img/emoji/1f47b.webp",
  "img/emoji/1f49d.webp",
  "img/emoji/1f4a5.webp",
  "img/emoji/1f4aa.webp",
  "img/emoji/1f4ac.webp",
  "img/emoji/1f501.webp",
  "img/emoji/1f51f.webp",
  "img/emoji/1f534.webp",
  "img/emoji/1f56f.webp",
  "img/emoji/1f590.webp",
  "img/emoji/1f600.webp",
  "img/emoji/1f602.webp",
  "img/emoji/1f60a.webp",
  "img/emoji/1f60b.webp",
  "img/emoji/1f60d.webp",
  "img/emoji/1f620.webp",
  "img/emoji/1f622.webp",
  "img/emoji/1f631.webp",
  "img/emoji/1f634.webp",
  "img/emoji/1f642.webp",
  "img/emoji/1f64c.webp",
  "img/emoji/1f64f.webp",
  "img/emoji/1f7e5.webp",
  "img/emoji/1f7e6.webp",
  "img/emoji/1f7e7.webp",
  "img/emoji/1f7e8.webp",
  "img/emoji/1f7e9.webp",
  "img/emoji/1f7ea.webp",
  "img/emoji/1f7eb.webp",
  "img/emoji/1f986.webp",
  "img/emoji/1f987.webp",
  "img/emoji/1f9b5.webp",
  "img/emoji/1f9b6.webp",
  "img/emoji/1f9d9-200d-2640.webp",
  "img/emoji/1fa77.webp",
  "img/emoji/1fad0.webp",
  "img/emoji/2705.webp",
  "img/emoji/274c.webp",
  "img/emoji/2753.webp",
  "img/emoji/2764.webp",
  "img/emoji/2b1b.webp",
  "img/emoji/2b1c.webp",
  "img/emoji/2b50.webp",
  "img/emoji/31-20e3.webp",
  "img/emoji/32-20e3.webp",
  "img/emoji/33-20e3.webp",
  "img/emoji/34-20e3.webp",
  "img/emoji/35-20e3.webp",
  "img/emoji/36-20e3.webp",
  "img/emoji/37-20e3.webp",
  "img/emoji/38-20e3.webp",
  "img/emoji/39-20e3.webp",
  "inhalte/uebersicht.json",
  "inhalte/deutsch/k3-vorsilben.json",
  "inhalte/deutsch/k3-unregelmaessige-verben.json",
  "inhalte/deutsch/k3-worttrennung.json",
  "inhalte/englisch/s1-animals.json",
  "inhalte/englisch/s1-body.json",
  "inhalte/englisch/s1-colours.json",
  "inhalte/englisch/s1-feelings.json",
  "inhalte/englisch/s1-festivals.json",
  "inhalte/englisch/s1-hello.json",
  "inhalte/englisch/s1-numbers.json",
  "icons/icon-192.png",
  "icons/icon-512.png",
  "icons/icon-maskable-512.png"
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(FILES.map((f) => new Request(f, { cache: "reload" })))).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k)))).then(() => self.clients.claim())
  );
});

// Erst aus dem Speicher, im Hintergrund aktualisieren
self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  e.respondWith(
    caches.match(e.request, { ignoreSearch: true }).then((hit) => {
      // Am Browser-Zwischenspeicher vorbei, damit Updates sofort ankommen
      const same = new URL(e.request.url).origin === location.origin;
      const net = fetch(same ? new Request(e.request.url, { cache: "no-cache" }) : e.request)
        .then((res) => {
          if (res.status === 200 && same) {
            const copy = res.clone();
            caches.open(VERSION).then((c) => c.put(e.request, copy));
          }
          return res;
        })
        .catch(() => hit);
      return hit || net;
    })
  );
});
