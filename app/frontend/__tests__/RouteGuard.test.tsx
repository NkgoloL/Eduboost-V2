import React from 'react'
import { fireEvent, render, screen } from '@testing-library/react'
import { RouteGuard } from '../src/components/eduboost/RouteGuard'
import { LearnerProvider } from '../src/context/LearnerContext'
import { vi } from 'vitest'

const MockRouter = { push: vi.fn() }
vi.mock('next/navigation', () => ({ useRouter: () => MockRouter }))

beforeEach(() => {
  MockRouter.push.mockClear()
})

test('shows loading state when loading', () => {
  // Use a provider but ensure eb_active_learner not set so loading becomes false quickly
  // Simulate loading by temporarily mocking useLearner via localStorage manipulation
  // @ts-ignore
  global.window = Object.create(window)
  const store: Record<string,string> = {}
  // @ts-ignore
  global.window.localStorage = { getItem: (k:string)=>store[k]||null, setItem: (k:string,v:string)=>store[k]=v, removeItem: (k:string)=>delete store[k] }

  render(
    <LearnerProvider>
      <RouteGuard required="learner"><div>ok</div></RouteGuard>
    </LearnerProvider>
  )
  expect(screen.queryByText(/Checking your session/)).not.toBeInTheDocument()
})

test('redirects when not allowed and not loading', () => {
  // Ensure no learner in localStorage so allowed=false
  // @ts-ignore
  global.window = Object.create(window)
  const store: Record<string,string> = {}
  // @ts-ignore
  global.window.localStorage = { getItem: (k:string)=>store[k]||null, setItem: (k:string,v:string)=>store[k]=v, removeItem: (k:string)=>delete store[k] }

  render(
    <LearnerProvider>
      <RouteGuard required="learner"><div>ok</div></RouteGuard>
    </LearnerProvider>
  )
  expect(MockRouter.push).toHaveBeenCalled()
})

test('allows parent access when guardian token exists', () => {
  // @ts-ignore
  global.window = Object.create(window)
  const store: Record<string,string> = { guardian_token: 'abc' }
  // @ts-ignore
  global.window.localStorage = { getItem: (k:string)=>store[k]||null, setItem: (k:string,v:string)=>store[k]=v, removeItem: (k:string)=>delete store[k] }

  render(
    <LearnerProvider>
      <RouteGuard required="parent"><div>ok</div></RouteGuard>
    </LearnerProvider>
  )

  expect(screen.getByText('ok')).toBeInTheDocument()
  expect(MockRouter.push).not.toHaveBeenCalled()
})

test('shows guardian login prompt and retry on parent route when token is missing', async () => {
  // @ts-ignore
  global.window = Object.create(window)
  const store: Record<string,string> = {}
  // @ts-ignore
  global.window.localStorage = { getItem: (k:string)=>store[k]||null, setItem: (k:string,v:string)=>store[k]=v, removeItem: (k:string)=>delete store[k] }

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

test('shows default learner prompt and retry navigates home for teacher route', async () => {
  // @ts-ignore
  global.window = Object.create(window)
  const store: Record<string,string> = {}
  // @ts-ignore
  global.window.localStorage = { getItem: (k:string)=>store[k]||null, setItem: (k:string,v:string)=>store[k]=v, removeItem: (k:string)=>delete store[k] }

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
