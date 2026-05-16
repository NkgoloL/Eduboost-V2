import { decodeJwtPayload, extractErrorMessage, storeAccessToken, getStoredAccessToken, getApiBaseUrl } from '../src/lib/api/client'

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
