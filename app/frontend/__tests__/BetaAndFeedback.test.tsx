import React from 'react'
import { render, screen } from '@testing-library/react'
import { BetaLabel, FeedbackButton } from '../src/components/eduboost/BetaAndFeedback'

test('renders BetaLabel text', () => {
  render(<BetaLabel />)
  expect(screen.getByLabelText(/Private beta/)).toBeInTheDocument()
  expect(screen.getByText(/Private beta · limited CAPS scope/)).toBeInTheDocument()
})

test('FeedbackButton constructs mailto link with context', () => {
  render(<FeedbackButton context="testing" />)
  const link = screen.getByRole('link', { name: /Report feedback/ }) as HTMLAnchorElement
  expect(link).toHaveAttribute('href')
  expect(link.href).toContain('mailto:')
  expect(link.href).toContain('feedback')
})
