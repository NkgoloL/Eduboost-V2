/// <reference types="vitest" />
import React from 'react'
import { test, expect } from 'vitest'
import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { GradeRShell } from '../../../src/components/grade-r/GradeRShell'

test('GradeRShell renders large touch targets and accessible labels', () => {
  render(<GradeRShell text="ba be bi" />)
  const prev = screen.getByRole('button', { name: /Previous/i })
  const next = screen.getByRole('button', { name: /Next/i })
  expect(prev).toHaveStyle({ minWidth: '64px', minHeight: '64px' })
  expect(next).toHaveStyle({ minWidth: '64px', minHeight: '64px' })
})
