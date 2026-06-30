# FE-PR-011 — Read‑only Offline Lesson Shell Cache & Loadshedding UI

Status: Implemented and verified — DB + cache API + storage budget + tests complete.

Scope
- Implements a read‑only IndexedDB lesson shell cache (`cachedLessons`) and light UI surfaces to save/remove cached lesson shells and surface that cached lessons are read‑only when offline.
- Strictly forbids any offline write/replay/sync/audit queue code in this PR.

Files added (primary)
- `app/frontend/src/lib/db/schema.ts` — Dexie DB with `cachedLessons` and `metadata` tables only.
- `app/frontend/src/lib/db/cache-api.ts` — read-only cache API: `saveCachedLessonShell`, `getCachedLessonShell`, `listCachedLessonShells`, `deleteCachedLessonShell`, `cacheStatusSummary`.
- `app/frontend/src/lib/db/storage-budget.ts` — 500MB LRU eviction and helpers.
- `app/frontend/src/__tests__/db/cache-api.test.ts` — Vitest unit tests for cache API and storage budget.
- `app/frontend/src/__tests__/setup.ts` — Vitest setup for IndexedDB polyfill.

Non-goals / Boundaries
- No `progress`, `syncQueue`, `auditQueue`, `consentQueue` tables or APIs.
- No background sync, replay, conflict-resolution, or offline mutation logic.
- No audio/blob/media caching; lesson `content` is JSON-only structured shell.
- No live EskomSePush integration in this PR.

Verification checklist
- [x] `pnpm run type-check` (app/frontend) - ✅ Passes (May 30, 2026)
- [x] `pnpm run lint` (app/frontend) - ✅ Passes (May 30, 2026; fixed `any` type ESLint errors)
- [x] `pnpm test -- --run src/__tests__/db/cache-api.test.ts` - ✅ 4/4 tests pass (May 30, 2026)
- [x] `pnpm run build` (app/frontend) - ✅ (verified in Docker build for staging deploy)

Static grep guards (run from repo root)
```
grep -rnE "(auditQueue|progressQueue|syncQueue|backgroundSync|replayAuditQueue|queueOfflineAuditEvent|conflict-resolution|processSyncQueue)" app/frontend/src/ || true
```

Result: Matches found in guardrails only (FORBIDDEN_KEYS constant and test assertions), not in actual implementations. This is expected and correct.

Notes
- This change implements the minimal read-only cache layer required for FE-PR-011 and includes an LRU eviction policy capped at 500MB.
- UI wiring (buttons, banners) should call `saveCachedLessonShell` / `deleteCachedLessonShell` and respect offline state; that wiring will be done in a follow-up small PR to keep scope tight.
- Vitest unit tests for cache API and storage budget are included in this PR.

Next steps
- Add a small UI PR to surface Save/Remove actions and Offline banner messaging (non-destructive).
