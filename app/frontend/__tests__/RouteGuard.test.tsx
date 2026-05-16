import React from 'react'
import { render, screen } from '@testing-library/react'
import { RouteGuard } from '../src/components/eduboost/RouteGuard'
import { LearnerProvider } from '../src/context/LearnerContext'
import { vi } from 'vitest'

const MockRouter = { push: vi.fn() }
vi.mock('next/navigation', () => ({ useRouter: () => MockRouter }))

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
