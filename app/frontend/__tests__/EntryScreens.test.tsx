import React from 'react'
import { fireEvent, render, screen } from '@testing-library/react'
import { vi } from 'vitest'
import { Landing, Onboarding, ParentGateway } from '../src/components/eduboost/EntryScreens'

test('Landing buttons call handlers', () => {
  const onStart = vi.fn()
  const onParent = vi.fn()

  render(<Landing onStart={onStart} onParent={onParent} />)

  fireEvent.click(screen.getByRole('button', { name: /Start Learning/i }))
  expect(onStart).toHaveBeenCalled()

  fireEvent.click(screen.getByRole('button', { name: /Parent \/ Guardian Portal/i }))
  expect(onParent).toHaveBeenCalled()
})

test('Onboarding completes and calls onComplete', async () => {
  const onComplete = vi.fn()

  render(<Onboarding onComplete={onComplete} />)

  fireEvent.click(screen.getByText('Grade R'))
  fireEvent.click(screen.getByRole('button', { name: /Next/ }))
  await screen.findByText(/Pick your avatar/i)

  const avatarButtons = screen.getAllByRole('button').filter((button) => button.textContent?.trim().length === 2)
  fireEvent.click(avatarButtons[0])
  fireEvent.click(screen.getByRole('button', { name: /Next/ }))
  await screen.findByText(/What should we call you/i)

  fireEvent.change(screen.getByPlaceholderText(/e.g\. StarLearner, MathWiz/i), { target: { value: 'TestKid' } })
  fireEvent.click(screen.getByRole('button', { name: /Next/ }))
  await screen.findByText(/Safety First!/i)

  fireEvent.click(screen.getByRole('button', { name: /Let's Go!/i }))

  expect(onComplete).toHaveBeenCalledWith(expect.objectContaining({ nickname: 'TestKid' }))
})

test('ParentGateway back button calls onBack', () => {
  const onBack = vi.fn()
  render(<ParentGateway onBack={onBack} />)
  fireEvent.click(screen.getByRole('button', { name: /Back/i }))
  expect(onBack).toHaveBeenCalled()
})
