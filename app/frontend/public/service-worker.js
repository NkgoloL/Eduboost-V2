const STATIC_CACHE = "eduboost-static-v1";
const RUNTIME_CACHE = "eduboost-runtime-v1";
const STATIC_ASSETS = [
  "/",
  "/login",
  "/dashboard",
  "/lesson",
  "/plan",
  "/diagnostic",
  "/parent-dashboard",
  "/parent-portal",
  "/manifest.json",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(STATIC_CACHE).then((cache) => cache.addAll(STATIC_ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => ![STATIC_CACHE, RUNTIME_CACHE].includes(key))
          .map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  if (event.request.method !== "GET") {
    return;
  }

  const isLessonOrDiagnosticApi =
    url.pathname.includes("/api/v2/lessons/") || url.pathname.includes("/api/v2/diagnostics/");

  if (STATIC_ASSETS.includes(url.pathname)) {
    event.respondWith(
      caches.match(event.request).then((cached) => cached || fetch(event.request))
    );
    return;
  }

  if (isLessonOrDiagnosticApi) {
    event.respondWith(
      caches.open(RUNTIME_CACHE).then(async (cache) => {
        try {
          const response = await fetch(event.request);
          cache.put(event.request, response.clone());
          return response;
        } catch (error) {
          const cached = await cache.match(event.request);
          if (cached) {
            return cached;
          }
          throw error;
        }
      })
    );
  }
});
