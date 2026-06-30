import { db, CachedLessonShell } from './schema';

export const CACHE_BUDGET_BYTES = 500 * 1024 * 1024; // 500MB

export interface CacheEvictionResult {
  beforeBytes: number;
  afterBytes: number;
  evictedLessonIds: string[];
  budgetBytes: number;
}

export async function calculateCacheSize(): Promise<number> {
  const all = await (db as any).cachedLessons.toArray();
  return all.reduce((sum: number, record: CachedLessonShell) => sum + (record.sizeBytes || 0), 0);
}

export async function enforceCacheBudget(): Promise<CacheEvictionResult | null> {
  const all = await (db as any).cachedLessons.orderBy('lastAccessedAt').toArray();
  const total = all.reduce((sum: number, record: CachedLessonShell) => sum + (record.sizeBytes || 0), 0);
  if (total <= CACHE_BUDGET_BYTES) return { beforeBytes: total, afterBytes: total, evictedLessonIds: [], budgetBytes: CACHE_BUDGET_BYTES };

  let freed = 0;
  const toEvict: string[] = [];
  const target = total - CACHE_BUDGET_BYTES;

  for (const lesson of all) {
    if (freed >= target) break;
    toEvict.push(lesson.id);
    freed += lesson.sizeBytes || 0;
  }

  if (toEvict.length > 0) {
    await (db as any).cachedLessons.bulkDelete(toEvict);
  }

  const after = await calculateCacheSize();

  return {
    beforeBytes: total,
    afterBytes: after,
    evictedLessonIds: toEvict,
    budgetBytes: CACHE_BUDGET_BYTES,
  };
}
