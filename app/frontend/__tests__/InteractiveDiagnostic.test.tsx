import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import { InteractiveDiagnostic } from '../src/components/eduboost/InteractiveDiagnostic'
import { DiagnosticService } from '../src/lib/api/services'
import { vi } from 'vitest'

const learner = { id: 'L1', learner_id: 'L1', nickname: 'Kid', grade: 4 }

test('handles start with no items', async () => {
  vi.spyOn(DiagnosticService, 'getItems').mockResolvedValue([])
  render(<InteractiveDiagnostic learner={learner as any} onComplete={() => {}} onBack={() => {}} />)
  const btn = screen.getByRole('button', { name: /Mathematics/i })
  btn.click()
  await waitFor(() => expect(screen.getByText(/No diagnostic items are available/)).toBeInTheDocument())
})

test('full flow submits and completes', async () => {
  vi.spyOn(DiagnosticService, 'getItems').mockResolvedValue([{ item_id: 'I1', question_text: 'q', options: ['a','b'], subject: 'MATH' }])
  vi.spyOn(DiagnosticService, 'submit').mockResolvedValue({ theta_after: 0, ranked_gaps: [] })
  const onComplete = vi.fn()
  render(<InteractiveDiagnostic learner={learner as any} onComplete={onComplete} onBack={() => {}} />)
  const btn = screen.getByRole('button', { name: /Mathematics/i })
  btn.click()
  await waitFor(() => expect(screen.getByText(/Question 1/)).toBeInTheDocument())
  const options = screen.getAllByRole('radio')
  options[0].click()
  await waitFor(() => expect(screen.getByText(/Assessment Complete/)).toBeInTheDocument())
  const updateBtn = screen.getByRole('button', { name: /Update My Study Plan/i })
  updateBtn.click()
  expect(onComplete).toHaveBeenCalled()
})
