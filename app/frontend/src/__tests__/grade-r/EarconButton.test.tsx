/// <reference types="vitest" />
import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { vi, test, expect } from 'vitest'
import { EarconProvider } from '../../../src/components/grade-r/EarconProvider'
import { EarconButton } from '../../../src/components/grade-r/EarconButton'
import * as earcons from '../../../src/lib/grade-r/earcons'

test('EarconButton enables and plays earcon on click', () => {
  const spy = vi.spyOn(earcons, 'playEarcon').mockImplementation(() => {})
  render(
    <EarconProvider>
      <EarconButton name="success" label="Play success" />
    </EarconProvider>
  )

  const btn = screen.getByRole('button', { name: /Play success/i })
  fireEvent.click(btn)
  expect(spy).toHaveBeenCalledWith('success')
  spy.mockRestore()
})
