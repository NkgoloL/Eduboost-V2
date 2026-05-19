import React from 'react'
import { fireEvent, render, screen } from '@testing-library/react'
import { vi } from 'vitest'
import { ErrorBoundary } from '../src/components/eduboost/ErrorBoundary'

function Bomb() {
  throw new Error('boom')
}

test('ErrorBoundary catches error and shows message and retry', async () => {
  const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

  render(
    <ErrorBoundary title="Oops">
      <Bomb />
    </ErrorBoundary>
  )

  expect(await screen.findByText('Oops')).toBeInTheDocument()
  expect(screen.getByRole('button', { name: /Try Again/i })).toBeInTheDocument()
  expect(consoleSpy).toHaveBeenCalled()

  consoleSpy.mockRestore()
})

test('ErrorBoundary onRetry invokes reset state callback', async () => {
  const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
  const setStateSpy = vi.spyOn(ErrorBoundary.prototype, 'setState')

  render(
    <ErrorBoundary title="Oops">
      <Bomb />
    </ErrorBoundary>
  )

  expect(await screen.findByText('Oops')).toBeInTheDocument()
  fireEvent.click(screen.getByRole('button', { name: /Try Again/i }))

  expect(setStateSpy).toHaveBeenCalledWith({ hasError: false, message: '' })
  setStateSpy.mockRestore()
  consoleSpy.mockRestore()
})

test('ErrorBoundary uses default title when title prop is omitted', async () => {
  const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

  render(
    <ErrorBoundary>
      <Bomb />
    </ErrorBoundary>
  )

  expect(await screen.findByText('This screen could not load.')).toBeInTheDocument()
  consoleSpy.mockRestore()
})
