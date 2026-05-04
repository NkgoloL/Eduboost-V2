import { LearnerService } from "./services";
import type { LessonPayload } from "./types";

const LESSON_SYNC_QUEUE_KEY = "eb_offline_lesson_sync_queue";
const LESSON_CACHE_PREFIX = "eb_cached_lesson:";

export interface OfflineLessonSyncEvent {
  lesson_id: string;
  event_type: "complete" | "feedback";
  completed_at?: string;
  score?: number;
}

function safeWindow() {
  return typeof window !== "undefined" ? window : null;
}

function readQueue(): OfflineLessonSyncEvent[] {
  const currentWindow = safeWindow();
  if (!currentWindow) {
    return [];
  }
  const raw = currentWindow.localStorage.getItem(LESSON_SYNC_QUEUE_KEY);
  if (!raw) {
    return [];
  }
  try {
    return JSON.parse(raw) as OfflineLessonSyncEvent[];
  } catch {
    return [];
  }
}

function writeQueue(queue: OfflineLessonSyncEvent[]) {
  const currentWindow = safeWindow();
  if (!currentWindow) {
    return;
  }
  currentWindow.localStorage.setItem(LESSON_SYNC_QUEUE_KEY, JSON.stringify(queue));
}

export function queueLessonSync(event: OfflineLessonSyncEvent) {
  const queue = readQueue();
  queue.push(event);
  writeQueue(queue);
}

export async function flushOfflineLessonSync() {
  const currentWindow = safeWindow();
  if (!currentWindow || !currentWindow.navigator.onLine) {
    return;
  }

  const queue = readQueue();
  if (queue.length === 0) {
    return;
  }

  const result = await LearnerService.syncLessonResponses(queue);
  if (result.processed >= queue.length) {
    writeQueue([]);
  } else if (result.processed > 0) {
    writeQueue(queue.slice(result.processed));
  }
}

function lessonCacheKey(learnerId: string, subject: string, topic: string) {
  return `${LESSON_CACHE_PREFIX}${learnerId}:${subject}:${topic}`;
}

export function cacheLessonSnapshot(learnerId: string, subject: string, topic: string, lesson: LessonPayload) {
  const currentWindow = safeWindow();
  if (!currentWindow) {
    return;
  }
  currentWindow.localStorage.setItem(lessonCacheKey(learnerId, subject, topic), JSON.stringify(lesson));
}

export function getCachedLessonSnapshot(learnerId: string, subject: string, topic: string): LessonPayload | null {
  const currentWindow = safeWindow();
  if (!currentWindow) {
    return null;
  }
  const raw = currentWindow.localStorage.getItem(lessonCacheKey(learnerId, subject, topic));
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as LessonPayload;
  } catch {
    return null;
  }
}
