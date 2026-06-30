import React from 'react'
import { fireEvent, render, screen } from '@testing-library/react'
import { RouteGuard } from '../src/components/eduboost/RouteGuard'
import { LearnerProvider } from '../src/context/LearnerContext'
import { vi } from 'vitest'

const MockRouter = { push: vi.fn() }
vi.mock('next/navigation', () => ({ useRouter: () => MockRouter }))

const mockSessionResponse = (authenticated: boolean) =>
  new Response(JSON.stringify({ authenticated }), { status: 200, headers: { 'Content-Type': 'application/json' } })

const originalFetch = global.fetch

beforeEach(() => {
  MockRouter.push.mockClear()
})

afterEach(() => {
  global.fetch = originalFetch
  vi.restoreAllMocks()
})

test('shows loading state while guardian session request is pending', () => {
  global.fetch = vi.fn(() => new Promise(() => {}) as any)

  render(
    <LearnerProvider>
      <RouteGuard required="parent"><div>ok</div></RouteGuard>
    </LearnerProvider>
  )

  expect(screen.getByText(/Checking your session/i)).toBeInTheDocument()
})

test('redirects learner routes when learner context is empty', () => {
  render(
    <LearnerProvider>
      <RouteGuard required="learner"><div>ok</div></RouteGuard>
    </LearnerProvider>
  )

  expect(MockRouter.push).toHaveBeenCalled()
})

test('allows parent route when session endpoint returns authenticated=true', async () => {
  global.fetch = vi.fn(async () => mockSessionResponse(true)) as any

  render(
    <LearnerProvider>
      <RouteGuard required="parent"><div>ok</div></RouteGuard>
    </LearnerProvider>
  )

  expect(await screen.findByText('ok')).toBeInTheDocument()
  expect(global.fetch).toHaveBeenCalledWith('/api/auth/session', expect.any(Object))
})

test('shows guardian prompt and retry navigates to login when session is missing', async () => {
  global.fetch = vi.fn(async () => mockSessionResponse(false)) as any

  render(
    <LearnerProvider>
      <RouteGuard required="parent"><div>ok</div></RouteGuard>
    </LearnerProvider>
  )

  expect(await screen.findByText(/Please log in as a guardian/i)).toBeInTheDocument()
  MockRouter.push.mockClear()
  fireEvent.click(screen.getByRole('button', { name: /Try Again/i }))
  expect(MockRouter.push).toHaveBeenCalledWith('/login')
})

test('teacher routes show default prompt and retry navigates home', async () => {
  global.fetch = vi.fn(async () => mockSessionResponse(false)) as any

  render(
    <LearnerProvider>
      <RouteGuard required="teacher"><div>ok</div></RouteGuard>
    </LearnerProvider>
  )

  expect(await screen.findByText(/Please choose a learner profile to continue/i)).toBeInTheDocument()
  MockRouter.push.mockClear()
  fireEvent.click(screen.getByRole('button', { name: /Try Again/i }))
  expect(MockRouter.push).toHaveBeenCalledWith('/')
})
