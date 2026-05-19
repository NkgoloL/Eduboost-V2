import { queueLessonSync, flushOfflineLessonSync, cacheLessonSnapshot, getCachedLessonSnapshot } from '../src/lib/api/offlineSync'
import { LearnerService } from '../src/lib/api/services'
import { vi } from 'vitest'

describe('offlineSync', () => {
  beforeEach(() => {
    // @ts-ignore
    global.window = Object.create(window)
    const store: Record<string,string> = {}
    // @ts-ignore
    global.window.localStorage = { getItem: (k:string)=>store[k]||null, setItem: (k:string,v:string)=>store[k]=v, removeItem: (k:string)=>delete store[k] }
    // @ts-ignore
    global.window.navigator = { onLine: true }
  })

  test('queue and flush with full processed clears queue', async () => {
    queueLessonSync({ learner_id: 'L1', responses: [] } as any)
    vi.spyOn(LearnerService, 'syncLessonResponses').mockResolvedValue({ processed: 1, queued: 0 })
    await flushOfflineLessonSync()
    expect(getCachedLessonSnapshot('L1','M','T')).toBeNull()
  })

  test('cache and get lesson snapshot', () => {
    cacheLessonSnapshot('L1','M','T',{ title: 'x'} as any)
    const s = getCachedLessonSnapshot('L1','M','T')
    expect(s).toBeTruthy()
    expect((s as any).title).toBe('x')
  })

  test('getCachedLessonSnapshot returns null for invalid JSON', () => {
    const store: Record<string,string> = {}
    cacheLessonSnapshot('L1','M','T',{ title: 'x'} as any)
    // @ts-ignore
    global.window.localStorage.setItem('eb_cached_lesson:L1:M:T', '{ invalid json')
    expect(getCachedLessonSnapshot('L1','M','T')).toBeNull()
  })

  test('flushOfflineLessonSync does nothing when offline', async () => {
    const store: Record<string,string> = {}
    // @ts-ignore
    global.window.localStorage = { getItem: (k:string)=>store[k]||null, setItem: (k:string,v:string)=>store[k]=v, removeItem: (k:string)=>delete store[k] }
    // @ts-ignore
    global.window.navigator = { onLine: false }

    await flushOfflineLessonSync()
    expect(store['eb_offline_lesson_sync_queue']).toBeUndefined()
  })

  test('flushOfflineLessonSync preserves queue on partial processing', async () => {
    const store: Record<string,string> = {}
    // @ts-ignore
    global.window.localStorage = { getItem: (k:string)=>store[k]||null, setItem: (k:string,v:string)=>store[k]=v, removeItem: (k:string)=>delete store[k] }
    // @ts-ignore
    global.window.navigator = { onLine: true }

    queueLessonSync({ learner_id: 'L1', responses: [] } as any)
    vi.spyOn(LearnerService, 'syncLessonResponses').mockResolvedValue({ processed: 0, queued: 1 })

    await flushOfflineLessonSync()

    expect(store['eb_offline_lesson_sync_queue']).toContain('L1')
  })
})
