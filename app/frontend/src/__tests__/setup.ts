// Vitest setup: polyfill IndexedDB for Dexie in Node/jsdom tests
// Use fake-indexeddb to polyfill IndexedDB in the test environment.
// Be explicit so Dexie sees the API even if modules import early.
import 'fake-indexeddb/auto';
// fallback explicit assignments
const FDBFactory = require('fake-indexeddb/lib/FDBFactory');
const FDBKeyRange = require('fake-indexeddb/lib/FDBKeyRange');
(globalThis as Record<string, unknown>).indexedDB = (globalThis as Record<string, unknown>).indexedDB || new FDBFactory();
(globalThis as Record<string, unknown>).IDBKeyRange = (globalThis as Record<string, unknown>).IDBKeyRange || FDBKeyRange.IDBKeyRange || FDBKeyRange;

