import { describe, expect, beforeEach, test, vi } from 'vitest'
import type { NextRequest } from 'next/server'
import { SESSION_COOKIE_NAME } from '../lib/auth/cookies'
import { POST as loginRoute } from '../app/api/auth/login/route'
import { POST as logoutRoute } from '../app/api/auth/logout/route'
import { POST as refreshRoute } from '../app/api/auth/refresh/route'
import { GET as sessionRoute } from '../app/api/auth/session/route'
import { POST as backendPost } from '../app/api/backend/[...path]/route'
import * as ServerClient from '../lib/api/server-client'
vi.mock('../lib/auth/session.server', () => {
  return {
    getSessionToken: vi.fn(() => null),
    getSessionClaims: vi.fn(() => null),
    clearSessionToken: vi.fn(),
    requireSessionToken: vi.fn(() => 'session-token'),
  }
})
import * as SessionServer from '../lib/auth/session.server'
import { middleware } from '../../middleware'

const backendFetchSpy = vi.spyOn(ServerClient, 'backendFetch')
const forwardSetCookiesSpy = vi.spyOn(ServerClient, 'forwardSetCookies')
const getSessionTokenSpy = vi.spyOn(SessionServer, 'getSessionToken')
const getSessionClaimsSpy = vi.spyOn(SessionServer, 'getSessionClaims')

const jsonResponse = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body ?? {}), { status, headers: { 'Content-Type': 'application/json' } })

const createRequest = (
  path: string,
  options: {
    method?: string
    body?: unknown
    cookies?: Record<string, string>
    headers?: Record<string, string>
    search?: string
  } = {}
) => {
  const headers = new Headers(options.headers)
  if (options.cookies) {
    const serialized = Object.entries(options.cookies)
      .map(([key, value]) => `${key}=${value}`)
      .join('; ')
    headers.set('cookie', serialized)
  }
  const bodyString =
    options.body === undefined ? '' : typeof options.body === 'string' ? options.body : JSON.stringify(options.body)
  return {
    method: options.method ?? (bodyString ? 'POST' : 'GET'),
    headers,
    nextUrl: new URL(`https://eduboost.local${path}${options.search ?? ''}`),
    text: async () => bodyString,
  } as unknown as NextRequest
}

beforeEach(() => {
  backendFetchSpy.mockReset()
  forwardSetCookiesSpy.mockReset()
  forwardSetCookiesSpy.mockImplementation(() => {})
  getSessionTokenSpy.mockReset()
  getSessionClaimsSpy.mockReset()
  getSessionTokenSpy.mockReturnValue('session-token')
  getSessionClaimsSpy.mockReturnValue(null)
})

describe('auth proxy routes', () => {
  test('login sets httpOnly session cookie on success', async () => {
    backendFetchSpy.mockResolvedValue(jsonResponse({ access_token: 'abc123' }))

    const response = await loginRoute(createRequest('/api/auth/login', { body: { email: 'a', password: 'b' } }))
    const cookie = response.cookies.get(SESSION_COOKIE_NAME)

    expect(cookie?.value).toBe('abc123')
    expect(cookie?.httpOnly).toBe(true)
    expect(response.status).toBe(200)
  })

  test('login clears session cookie on backend failure', async () => {
    backendFetchSpy.mockResolvedValue(jsonResponse({ detail: 'invalid' }, 401))

    const response = await loginRoute(createRequest('/api/auth/login', { body: { email: 'a', password: 'b' } }))
    const cookie = response.cookies.get(SESSION_COOKIE_NAME)

    expect(cookie?.value).toBe('')
    expect(cookie?.maxAge).toBe(0)
    expect(response.status).toBe(401)
  })

  test('logout always clears the session cookie', async () => {
    backendFetchSpy.mockResolvedValue(jsonResponse({ success: true }))
    getSessionTokenSpy.mockReturnValue('existing')

    const response = await logoutRoute(createRequest('/api/auth/logout'))
    const cookie = response.cookies.get(SESSION_COOKIE_NAME)

    expect(cookie?.value).toBe('')
    expect(cookie?.maxAge).toBe(0)
  })

  test('session route reports unauthenticated when no cookie is present', async () => {
    getSessionTokenSpy.mockReturnValue(null)
    getSessionClaimsSpy.mockReturnValue(null)

    const response = await sessionRoute()
    const payload = await response.json()
    expect(payload).toEqual({ authenticated: false, claims: null })
  })

  test('refresh sets new session token when backend succeeds', async () => {
    backendFetchSpy.mockResolvedValue(jsonResponse({ access_token: 'new-token' }))
    getSessionTokenSpy.mockReturnValue('old-token')

    const response = await refreshRoute(createRequest('/api/auth/refresh'))
    const cookie = response.cookies.get(SESSION_COOKIE_NAME)

    expect(cookie?.value).toBe('new-token')
    expect(response.status).toBe(200)
  })

  test('refresh clears session when backend rejects token', async () => {
    backendFetchSpy.mockResolvedValue(jsonResponse({ detail: 'expired' }, 401))

    const response = await refreshRoute(createRequest('/api/auth/refresh'))
    const cookie = response.cookies.get(SESSION_COOKIE_NAME)

    expect(cookie?.value).toBe('')
    expect(cookie?.maxAge).toBe(0)
    expect(response.status).toBe(401)
  })
})

describe('backend proxy route', () => {
  test('forwards sanitized path, query, headers, and body', async () => {
    getSessionTokenSpy.mockReturnValue('session-token')
    backendFetchSpy.mockResolvedValue(jsonResponse({ ok: true }))

    const request = createRequest('/api/backend', {
      method: 'POST',
      body: { hello: 'world' },
      headers: { accept: 'application/json', 'x-request-id': 'abc' },
      cookies: { eduboost_session: 'session-token', extra: 'x' },
      search: '?foo=1',
    })

    const response = await backendPost(request, { params: Promise.resolve({ path: ['diagnostics', 'start'] }) })

    expect(response.status).toBe(200)
    expect(backendFetchSpy).toHaveBeenCalledTimes(1)
    const backendCall = backendFetchSpy.mock.calls[0]!
    const [pathArg, options] = backendCall
    expect(pathArg).toBe('/diagnostics/start?foo=1')
    const forwardedHeaders = options?.headers as Headers
    expect(forwardedHeaders.get('accept')).toBe('application/json')
    expect(forwardedHeaders.get('x-request-id')).toBe('abc')
    expect(options?.token).toBe('session-token')
    expect(options?.body).toContain('hello')
    expect(options?.cookieHeader).toContain('eduboost_session=session-token')
  })

  test('rejects unsafe path traversal attempts', async () => {
    backendFetchSpy.mockResolvedValue(jsonResponse({ ok: true }))

    const response = await backendPost(createRequest('/api/backend'), { params: Promise.resolve({ path: ['..', 'secrets'] }) })

    expect(response.status).toBe(400)
    expect(backendFetchSpy).not.toHaveBeenCalled()
    const payload = await response.json()
    expect(payload.error.message).toMatch(/Invalid request path/)
  })
})

describe('middleware', () => {
  const createMiddlewareRequest = (path: string, hasSession = false) => ({
    cookies: {
      get: (name: string) => (hasSession && name === SESSION_COOKIE_NAME ? { value: 'session-token' } : undefined),
    },
    nextUrl: new URL(`https://eduboost.local${path}`),
  }) as unknown as NextRequest

  test('redirects unauthenticated protected routes to login with redirect param', () => {
    const response = middleware(createMiddlewareRequest('/dashboard'))
    expect(response?.status).toBe(307)
    expect(response?.headers.get('Location')).toBe('https://eduboost.local/login?redirect=%2Fdashboard')
  })

  test('allows protected routes when session cookie exists', () => {
    const response = middleware(createMiddlewareRequest('/dashboard', true))
    expect(response?.headers.get('Location')).toBeNull()
  })
})

