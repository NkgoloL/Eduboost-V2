/// <reference types="vitest" />
import React from 'react'
import { test, expect } from 'vitest'
import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { PhonicsKaraokeText } from '../../../src/components/grade-r/PhonicsKaraokeText'

const segments = [
  { id: 's1', text: 'ba', startMs: 0, endMs: 200 },
  { id: 's2', text: 'be', startMs: 200, endMs: 400 },
  { id: 's3', text: 'bi', startMs: 400, endMs: 600 },
]

test('renders segments and highlights active index', () => {
  render(<PhonicsKaraokeText segments={segments} activeIndex={1} />)
  expect(screen.getByTestId('segment-0')).toBeInTheDocument()
  expect(screen.getByTestId('segment-1')).toHaveAttribute('aria-current', 'true')
})

test('respects reducedMotion by disabling transition', () => {
  render(<PhonicsKaraokeText segments={segments} activeIndex={0} reducedMotion={true} />)
  const el = screen.getByTestId('segment-0')
  expect(el).toHaveStyle({ transition: 'none' })
})
