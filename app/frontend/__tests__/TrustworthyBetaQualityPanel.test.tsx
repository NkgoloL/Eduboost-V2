import React from 'react'
import { render, screen } from '@testing-library/react'
import { TrustworthyBetaQualityPanel } from '../src/components/eduboost/TrustworthyBetaQualityPanel'

test('renders RR-018 trustworthy beta quality surface', () => {
  render(<TrustworthyBetaQualityPanel context="diagnostic" />)

  expect(screen.getByTestId('trustworthy-beta-quality-panel')).toBeInTheDocument()
  expect(screen.getByRole('link', { name: /Report issue for diagnostic/i })).toHaveAttribute('href', expect.stringContaining('mailto:'))
  expect(screen.getByTestId('rr018-content-correction-workflow')).toHaveTextContent(/Content correction workflow/)
  expect(screen.getByTestId('rr018-human-review-queue')).toHaveTextContent(/Human review queue/)
  expect(screen.getByTestId('rr018-educator-caps-priority-review')).toHaveTextContent(/Educator CAPS priority review/)
  expect(screen.getByTestId('rr018-feedback-privacy-boundary')).toHaveTextContent(/Privacy boundary/)
})
