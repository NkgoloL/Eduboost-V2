import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { CachedLessonShell } from '../../lib/db/schema';

// Provide an in-memory fake DB for tests to avoid relying on IndexedDB during
// test discovery and to make these unit tests deterministic.
function makeFakeTable() {
  const store = new Map<string, Record<string, unknown>>();
  return {
    put: async (v: Record<string, unknown>) => {
      const id = v.id as string;
      store.set(id, v);
      return id;
    },
    get: async (id: string) => store.get(id),
    delete: async (id: string) => {
      store.delete(id);
    },
    toArray: async () => Array.from(store.values()),
    update: async (id: string, changes: Record<string, unknown>) => {
      const cur = store.get(id);
      if (!cur) return 0;
      Object.assign(cur, changes);
      store.set(id, cur);
      return 1;
    },
    where: (field: string) => ({
      equals: (val: unknown) => ({ toArray: async () => Array.from(store.values()).filter((r) => r[field] === val) }),
    }),
    orderBy: (field: string) => ({
      toArray: async () => Array.from(store.values()).sort((a, b) => {
        const av = (a[field] as number) || 0;
        const bv = (b[field] as number) || 0;
        return av - bv;
      }),
    }),
    bulkDelete: async (ids: string[]) => {
      for (const id of ids) store.delete(id);
    },
    clear: async () => store.clear(),
  };
}

vi.mock('../../lib/db/schema', () => ({
  db: { cachedLessons: makeFakeTable(), metadata: { clear: async () => {} } },
}));

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let db: any;
let saveCachedLessonShell: (lesson: CachedLessonShell) => Promise<void>;
let getCachedLessonShell: (id: string) => Promise<CachedLessonShell | null>;
let deleteCachedLessonShell: (id: string) => Promise<void>;
let listCachedLessonShells: () => Promise<CachedLessonShell[]>;
let cacheStatusSummary: () => Promise<{ totalBytes: number; count: number }>;
let enforceCacheBudget: () => Promise<{ afterBytes: number; evictedLessonIds: string[] } | null>;
let CACHE_BUDGET_BYTES: number;

async function clearDb() {
  try {
    await db.cachedLessons.clear();
  } catch (e) {
    // ignore
  }
  try {
    await db.metadata.clear();
  } catch (e) {}
}

beforeEach(async () => {
  // dynamic import so setup.ts polyfills IndexedDB before Dexie constructs DB
  const schemaMod = await import('../../lib/db/schema');
  db = schemaMod.db;
  const api = await import('../../lib/db/cache-api');
  saveCachedLessonShell = api.saveCachedLessonShell;
  getCachedLessonShell = api.getCachedLessonShell;
  deleteCachedLessonShell = api.deleteCachedLessonShell;
  listCachedLessonShells = api.listCachedLessonShells;
  cacheStatusSummary = api.cacheStatusSummary;
  const budget = await import('../../lib/db/storage-budget');
  enforceCacheBudget = budget.enforceCacheBudget;
  CACHE_BUDGET_BYTES = budget.CACHE_BUDGET_BYTES;

  await clearDb();
});

describe('FE-PR-011 cache API', () => {
  it('exposes only cachedLessons and metadata tables', () => {
    expect(db.cachedLessons).toBeDefined();
    expect(db.metadata).toBeDefined();
    // forbidden tables must not exist
    expect((db as Record<string, unknown>).progress).toBeUndefined();
    expect((db as Record<string, unknown>).syncQueue).toBeUndefined();
    expect((db as Record<string, unknown>).auditQueue).toBeUndefined();
  });

  it('save/get/list/delete works for cached lesson shells', async () => {
    const lesson = {
      id: 'l1',
      lessonId: 'lesson-1',
      subject: 'MATH',
      title: 'Fractions',
      content: { body: 'intro' },
      cachedAt: new Date().toISOString(),
      lastAccessedAt: new Date().toISOString(),
      sizeBytes: 1024,
      schemaVersion: 1,
      learnerScope: 'synthetic' as const,
    };

    try {
      await saveCachedLessonShell(lesson);

      const got = await getCachedLessonShell('l1');
      expect(got).not.toBeNull();
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      expect((got as any).title).toBe('Fractions');

      const list = await listCachedLessonShells();
      expect(Array.isArray(list)).toBe(true);
      expect(list.length).toBe(1);

      await deleteCachedLessonShell('l1');
      const after = await getCachedLessonShell('l1');
      expect(after).toBeNull();
    } catch (e) {
      // log for debugging in CI output
      // eslint-disable-next-line no-console
      console.error('save/get test error:', e);
      throw e;
    }
  });

  it('rejects lesson shells containing forbidden keys', async () => {
    const bad = {
      id: 'bad1',
      lessonId: 'x',
      subject: 'MATH',
      title: 'Bad',
      content: {},
      cachedAt: new Date().toISOString(),
      lastAccessedAt: new Date().toISOString(),
      sizeBytes: 10,
      schemaVersion: 1,
      learnerScope: 'local-demo' as const,
      progress: { hacked: true }, // forbidden
    };

    await expect(saveCachedLessonShell(bad)).rejects.toThrow(/Prohibited key/);
  });

  it('enforces LRU eviction when over budget', async () => {
    // create three lessons with large size to exceed budget
    const big = (n: number) => ({
      id: `b${n}`,
      lessonId: `lesson-${n}`,
      subject: 'MATH',
      title: `Big ${n}`,
      content: {},
      cachedAt: new Date().toISOString(),
      lastAccessedAt: new Date(Date.now() - n * 1000).toISOString(),
      sizeBytes: Math.floor(CACHE_BUDGET_BYTES / 2), // half budget
      schemaVersion: 1,
      learnerScope: 'synthetic' as const,
    });

    try {
      await saveCachedLessonShell(big(1));
      await saveCachedLessonShell(big(2));
      await saveCachedLessonShell(big(3));

      const summaryBefore = await cacheStatusSummary();
      expect(summaryBefore.totalBytes).toBeGreaterThanOrEqual(CACHE_BUDGET_BYTES);

      const eviction = await enforceCacheBudget();
      expect(eviction).not.toBeNull();
      if (eviction) {
        expect(eviction.afterBytes).toBeLessThanOrEqual(CACHE_BUDGET_BYTES);
        expect(Array.isArray(eviction.evictedLessonIds)).toBe(true);
      }
    } catch (e) {
      // eslint-disable-next-line no-console
      console.error('eviction test error:', e);
      throw e;
    }
  });
});
