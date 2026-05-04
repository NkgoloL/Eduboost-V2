"use client";

import { useEffect } from "react";
import { flushOfflineLessonSync } from "../lib/api/offlineSync";

export function ServiceWorkerRegistration() {
  useEffect(() => {
    if ("serviceWorker" in navigator && process.env.NODE_ENV !== "test") {
      navigator.serviceWorker.register("/service-worker.js").catch(() => {});
    }

    const onOnline = () => {
      void flushOfflineLessonSync();
    };

    window.addEventListener("online", onOnline);
    void flushOfflineLessonSync();

    return () => {
      window.removeEventListener("online", onOnline);
    };
  }, []);

  return null;
}
