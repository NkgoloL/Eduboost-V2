import { vi, afterEach } from 'vitest'

vi.mock('server-only', () => ({}))

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

globalThis.fetch = vi.fn(async (input: RequestInfo | URL) => {
  const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
  if (url && url.includes('/api/v2/diagnostic/start')) {
    return jsonResponse({
      session_id: 'sess-1',
      first_item: {
        item_id: 'ITEM_1',
        question_text: 'What is 2+2?',
        options: ['1', '2', '3', '4'],
      },
    })
  }
  if (url && url.match(/\/api\/v2\/diagnostic\/session\/[\w-]+\/respond/)) {
    return jsonResponse({
      is_complete: false,
      session_state: { progress: 1 },
    })
  }
  return jsonResponse({})
})

const createStorage = () => {
  let store: Record<string, string> = {}
  return {
    get length() {
      return Object.keys(store).length
    },
    clear: () => {
      store = {}
    },
    getItem: (key: string) => (key in store ? store[key] : null),
    setItem: (key: string, value: string) => {
      store[key] = value
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    key: (index: number) => Object.keys(store)[index] ?? null,
  }
}

const localStorageMock = createStorage()
const sessionStorageMock = createStorage()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
  writable: true,
})

Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock,
  writable: true,
})

afterEach(() => {
  vi.clearAllMocks()
})
import '@testing-library/jest-dom'
