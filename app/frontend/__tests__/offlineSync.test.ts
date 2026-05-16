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
})
