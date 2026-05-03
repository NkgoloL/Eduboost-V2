import { vi, afterEach } from 'vitest'

globalThis.fetch = vi.fn((input: any) => {
  const url = typeof input === 'string' ? input : input?.url
  if (url && url.includes('/api/v2/diagnostics/')) {
    return Promise.resolve({ ok: true, status: 200, json: async () => ({ session_id: 'sess-1', first_item: { item_id: 'ITEM_1', question_text: 'What is 2+2?', options: ['1','2','3','4'] } }) })
  }
  if (url && url.match(/\/api\/v2\/diagnostics\/session\/[\w-]+\/respond/)) {
    return Promise.resolve({ ok: true, status: 200, json: async () => ({ is_complete: false, session_state: { progress: 1 } }) })
  }
  return Promise.resolve({ ok: true, status: 200, json: async () => ({}) })
})

afterEach(() => {
  vi.clearAllMocks()
})
import '@testing-library/jest-dom'
