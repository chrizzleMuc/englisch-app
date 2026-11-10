// Offline-Speicher: Bei jeder Änderung an der App VERSION erhöhen.
const VERSION = "learnino-8";
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
