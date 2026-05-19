import { ApiError, decodeJwtPayload, extractErrorMessage, fetchApi, getApiBaseUrl, getStoredAccessToken, storeAccessToken } from '../src/lib/api/client'
import { vi } from 'vitest'

const originalFetch = globalThis.fetch

function setLocalStorage(store: Record<string,string>) {
  // @ts-ignore
  global.window = Object.create(window)
  // @ts-ignore
  global.window.localStorage = {
    getItem: (k: string) => store[k] || null,
    setItem: (k: string, v: string) => {
      store[k] = v
    },
    removeItem: (k: string) => {
      delete store[k]
    },
  }
}

afterEach(() => {
  globalThis.fetch = originalFetch
})

test('decodeJwtPayload returns payload for valid token', () => {
  // header.{"foo":"bar"}.sig base64
  const payload = Buffer.from(JSON.stringify({ foo: 'bar' })).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
  const token = `a.${payload}.c`
  const decoded = decodeJwtPayload<any>(token)
  expect(decoded).toEqual({ foo: 'bar' })
})

test('extractErrorMessage returns fallback for unknown', () => {
  expect(extractErrorMessage(undefined as any)).toBe('API request failed')
})

test('store/get access token uses localStorage', () => {
  // @ts-ignore
  global.window = Object.create(window)
  const store: Record<string,string> = {}
  // @ts-ignore
  global.window.localStorage = { getItem: (k:string) => (store[k] ?? null), setItem: (k:string,v:string) => (store[k]=v), removeItem: (k:string)=>delete store[k] }
  storeAccessToken('tok')
  expect(getStoredAccessToken('/auth/login')).toBe('tok')
  storeAccessToken(null)
  expect(getStoredAccessToken('/auth/login')).toBeNull()
})

test('getApiBaseUrl returns a string', () => {
  expect(typeof getApiBaseUrl()).toBe('string')
})

test('getStoredAccessToken falls back to learner token for non-auth endpoints', () => {
  setLocalStorage({ learner_token: 'learner123' })
  expect(getStoredAccessToken('/lessons')).toBe('learner123')
})

test('extractErrorMessage returns string values unchanged and ApiError messages', () => {
  expect(extractErrorMessage('oops')).toBe('oops')
  expect(extractErrorMessage(new ApiError({ message: 'boom' } as any))).toBe('boom')
})

test('fetchApi returns envelope data and attaches Authorization headers', async () => {
  setLocalStorage({ guardian_token: 'tok' })

  const fetchMock = vi.fn().mockResolvedValue(
    new Response(JSON.stringify({ data: { ok: true } }), { status: 200 })
  )
  globalThis.fetch = fetchMock as any

  const response = await fetchApi<{ ok: boolean }>('/auth/sessions')
  expect(response.ok).toBe(true)
  expect(fetchMock).toHaveBeenCalledTimes(1)
  expect((fetchMock.mock.calls[0][1] as RequestInit).headers).toMatchObject({ Authorization: 'Bearer tok' })
})

test('fetchApi returns null for 204 No Content responses', async () => {
  setLocalStorage({ guardian_token: 'tok' })
  globalThis.fetch = vi.fn().mockResolvedValue(new Response(null, { status: 204 })) as any
  const response = await fetchApi<null>('/no-content')
  expect(response).toBeNull()
})

test('fetchApi retries after 401 and refreshes token successfully', async () => {
  setLocalStorage({ guardian_token: 'old-token' })

  const fetchMock = vi.fn()
    .mockResolvedValueOnce(new Response(JSON.stringify({ detail: 'Unauthorized' }), { status: 401 }))
    .mockResolvedValueOnce(new Response(JSON.stringify({ access_token: 'new-token' }), { status: 200 }))
    .mockResolvedValueOnce(new Response(JSON.stringify({ success: true }), { status: 200 }))

  globalThis.fetch = fetchMock as any

  const response = await fetchApi<{ success: boolean }>('/secure-endpoint')
  expect(response.success).toBe(true)
  expect(fetchMock).toHaveBeenCalledTimes(3)
  expect(fetchMock.mock.calls[1][0]).toContain('/auth/refresh')
})

test('fetchApi throws ApiError for failed response detail messages', async () => {
  setLocalStorage({ guardian_token: 'tok' })
  globalThis.fetch = vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: 'No access' }), { status: 403 })) as any
  const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

  await expect(fetchApi('/forbidden')).rejects.toThrow('No access')
  errorSpy.mockRestore()
})
