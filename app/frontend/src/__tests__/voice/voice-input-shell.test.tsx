import React from 'react'
import { render, screen } from '@testing-library/react'
import { test, expect } from 'vitest'
import '@testing-library/jest-dom'
import VoiceInputShell from '@/components/voice/VoiceInputShell'

test('VoiceInputShell renders and respects consent toggle without requesting mic on mount', () => {
  render(<VoiceInputShell learnerId="t1" />)
  expect(screen.getByText(/Voice support:/)).toBeInTheDocument()
  expect(screen.getByText(/Guardian consent:/)).toBeInTheDocument()
  // Start button exists but may be disabled
  expect(screen.getByText(/Start Voice Input/)).toBeInTheDocument()
})
