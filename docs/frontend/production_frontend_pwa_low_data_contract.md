# Production Frontend PWA Low-Data Contract

## Purpose

This contract defines PWA and low-data behavior for frontend production readiness.

## Required PWA and Low-Data Controls

- Add or verify service worker.
- Add or verify manifest.
- Cache app shell.
- Add offline-friendly lesson content.
- Add offline messaging.
- Add compressed assets.
- Add low-data mode.
- Add PWA installability test.
- Add offline E2E test.
- Add offline feedback queue.
- Add sync-on-reconnect behavior.

## Repository Evidence

- `app/frontend/src/components/ServiceWorkerRegistration.tsx`
- `app/frontend/src/lib/api/offlineSync.ts`
- `app/frontend/src/__tests__/OfflineSync.test.ts`
- `docs/frontend/accessibility_pwa_e2e_evidence.md`
- `docs/frontend/playwright_mocked_journey_specs.md`
