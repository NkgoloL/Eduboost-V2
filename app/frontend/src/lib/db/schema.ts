// Avoid importing Dexie TypeScript type directly to prevent module augmentation
// conflicts with node_modules/@types/dexie. Runtime duck-typing handles Dexie API.
const Dexie = require('dexie').default || require('dexie');

export interface CachedLessonShell {
  id: string;
  lessonId: string;
  subject: string;
  title: string;
  content: unknown; // structured lesson shell JSON
  cachedAt: string; // ISO
  lastAccessedAt: string; // ISO
  sizeBytes: number;
  schemaVersion: number; // 1
  learnerScope: 'synthetic' | 'local-demo';
}

export interface SystemMetadata {
  key: string;
  value: string;
  updatedAt: string;
}

export class EduBoostOfflineDB extends (Dexie as any) {
  // Use `any` for the runtime Dexie table shape to avoid fragile type mismatches
  // with upstream Dexie types in different versions.
  cachedLessons: any;
  metadata: any;

  constructor() {
    super('EduBoostOfflineDB');
    this.version(1).stores({
      cachedLessons: 'id, lessonId, subject, lastAccessedAt',
      metadata: 'key',
    });
  }
}

// Export a lazy proxy that instantiates the real Dexie DB only on first use.
function createLazyDb(): EduBoostOfflineDB {
  // Use a Proxy to defer construction until a property is accessed.
  let real: EduBoostOfflineDB | null = null;
  const ensure = () => {
    if (!real) real = new EduBoostOfflineDB();
    return real;
  };

  // Return a Proxy typed as EduBoostOfflineDB but lazily delegating.
  const proxy = new Proxy(
    {},
    {
      get(_, prop) {
        const r = ensure();
        return r[prop as keyof EduBoostOfflineDB];
      },
      set(_, prop, value) {
        const r = ensure();
        (r as unknown as Record<string, unknown>)[prop as string] = value;
        return true;
      },
    }
  ) as unknown as EduBoostOfflineDB;

  return proxy;
}

export const db = createLazyDb();
