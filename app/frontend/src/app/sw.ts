// @ts-nocheck

const PRECACHE_NAME = "serwist-precache-v1";
const publicRoutes = ["/", "/login", "/register", "/onboarding", "/auth/verify-email", "/auth/reset-password"];

const authRoutes = ["/dashboard", "/lesson", "/diagnostic", "/plan", "/badges", "/settings", "/parent-dashboard", "/parent"];

const isAuthRoute = (pathname) => {
  return authRoutes.some((route) => pathname.startsWith(route));
};

const isPublicRoute = (pathname) => {
  return publicRoutes.includes(pathname);
};

self.addEventListener("install", (event) => {
  const installWork = async () => {
    const precacheList = (self.__SW_MANIFEST || []).map((entry) => (typeof entry === "string" ? entry : entry.url));
    const cache = await caches.open(PRECACHE_NAME);
    await cache.addAll(precacheList.filter(Boolean));
    await self.skipWaiting();
  };

  event.waitUntil(installWork());
});

self.addEventListener("activate", (event) => {
  const activateWork = async () => {
    const cacheNames = await caches.keys();
    await Promise.all(
      cacheNames
        .filter((name) => ![PRECACHE_NAME, "static-assets", "public-pages"].includes(name))
        .map((name) => caches.delete(name))
    );
    await self.clients.claim();
  };

  event.waitUntil(activateWork());
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // API routes - NetworkOnly
  if (url.pathname.startsWith("/api/")) {
    event.respondWith(fetch(request));
    return;
  }

  // Authenticated routes - NetworkOnly
  if (request.mode === "navigate" && isAuthRoute(url.pathname)) {
    event.respondWith(fetch(request));
    return;
  }

  // Public routes - NetworkFirst with fallback
  if (request.mode === "navigate" && isPublicRoute(url.pathname)) {
    event.respondWith(
      (async () => {
        try {
          const networkResponse = await fetch(request);
          const cache = await caches.open("public-pages");
          cache.put(request, networkResponse.clone());
          return networkResponse;
        } catch {
          const cachedResponse = await caches.match(request);
          return cachedResponse || new Response("Offline", { status: 503 });
        }
      })()
    );
    return;
  }

  // Static assets - CacheFirst
  if (request.url.startsWith("http")) {
    event.respondWith(
      caches.open("static-assets").then((cache) => {
        return cache.match(request).then((cached) => {
          if (cached) return cached;
          return fetch(request).then((networkResponse) => {
            cache.put(request, networkResponse.clone());
            return networkResponse;
          });
        });
      })
    );
    return;
  }

  event.respondWith(fetch(request));
});
