import { ApiError, decodeJwtPayload, extractErrorMessage, fetchApi, getApiBaseUrl } from '../src/lib/api/client'
import { afterEach, vi } from 'vitest'

const originalFetch = globalThis.fetch

afterEach(() => {
  globalThis.fetch = originalFetch
  vi.clearAllMocks()
})

const okResponse = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body ?? {}), { status, headers: { 'Content-Type': 'application/json' } })

test('decodeJwtPayload returns payload for valid token', () => {
  const payload = Buffer.from(JSON.stringify({ foo: 'bar' })).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
  const token = `a.${payload}.c`
  const decoded = decodeJwtPayload<any>(token)
  expect(decoded).toEqual({ foo: 'bar' })
})

test('extractErrorMessage returns fallback for unknown', () => {
  expect(extractErrorMessage(undefined as any)).toBe('API request failed')
})

test('getApiBaseUrl returns a string', () => {
  expect(typeof getApiBaseUrl()).toBe('string')
})

test('extractErrorMessage returns string values unchanged and ApiError messages', () => {
  expect(extractErrorMessage('oops')).toBe('oops')
  expect(extractErrorMessage(new ApiError({ message: 'boom' } as any))).toBe('boom')
})

test('fetchApi routes relative endpoints through /api/backend', async () => {
  const fetchMock = vi.fn().mockResolvedValue(okResponse({ data: { ok: true } }))
  globalThis.fetch = fetchMock as any

  const result = await fetchApi<{ ok: boolean }>('/lessons')
  expect(result.ok).toBe(true)
  expect(fetchMock).toHaveBeenCalledTimes(1)
  expect(fetchMock.mock.calls[0][0]).toBe('/api/backend/lessons')
})

test('fetchApi returns null for 204 responses', async () => {
  globalThis.fetch = vi.fn().mockResolvedValue(new Response(null, { status: 204 })) as any
  const response = await fetchApi<null>('/diagnostics/progress')
  expect(response).toBeNull()
})

test('fetchApi retries once after 401 by calling /api/auth/refresh', async () => {
  const fetchMock = vi
    .fn()
    .mockResolvedValueOnce(new Response(JSON.stringify({ detail: 'Unauthorized' }), { status: 401 }))
    .mockResolvedValueOnce(okResponse({ data: { access_token: 'new' } }))
    .mockResolvedValueOnce(okResponse({ data: { ok: true } }))

  globalThis.fetch = fetchMock as any

  const response = await fetchApi<{ ok: boolean }>('/study-plan')
  expect(response.ok).toBe(true)
  expect(fetchMock).toHaveBeenCalledTimes(3)
  expect(fetchMock.mock.calls[1][0]).toBe('/api/auth/refresh')
})

test('fetchApi surfaces API errors via ApiError', async () => {
  const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
  globalThis.fetch = vi.fn().mockResolvedValue(okResponse({ detail: 'Forbidden' }, 403)) as any
  await expect(fetchApi('/restricted')).rejects.toThrow('Forbidden')
  errorSpy.mockRestore()
})
