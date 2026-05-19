import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import { ParentDashboard } from '../src/components/eduboost/ParentDashboard'
import { ParentService, DataRightsService } from '../src/lib/api/services'
import { vi } from 'vitest'

vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
  BarChart: ({ children }: any) => <div>{children}</div>,
  Bar: (_: any) => <div />,
  XAxis: (_: any) => <div />,
  YAxis: (_: any) => <div />,
  Tooltip: (_: any) => <div />,
}))

beforeEach(() => {
  // @ts-ignore
  global.window = Object.create(window)
  const store: Record<string,string> = { guardian_id: 'G1' }
  // @ts-ignore
  global.window.localStorage = { getItem: (k:string)=>store[k]||null, setItem: (k:string,v:string)=>store[k]=v }
})

test('renders no learners when dashboard empty', async () => {
  vi.spyOn(ParentService, 'getTrustDashboard').mockResolvedValue({ learners: [] } as any)
  vi.spyOn(ParentService, 'getExportBundle').mockResolvedValue({ exports: [] } as any)
  render(<ParentDashboard onBack={() => {}} />)
  await waitFor(() => expect(screen.getByText(/No active learners were found/)).toBeInTheDocument())
})

test('data rights export updates status', async () => {
  const learner = { learner_id: 'L1', display_name: 'Kid', grade_level: 4, lesson_completion_rate_7d: 10, streak_days: 1, irt_theta: 0, top_knowledge_gaps: [], ai_progress_summary: '' }
  vi.spyOn(ParentService, 'getTrustDashboard').mockResolvedValue({ learners: [learner] } as any)
  vi.spyOn(ParentService, 'getExportBundle').mockResolvedValue({ exports: [{ learner_id: 'L1', display_name: 'Kid', export_url: 'http://x', filename: 'f' }] } as any)
  vi.spyOn(DataRightsService, 'exportLearner').mockResolvedValue({ filename: 'bundle.json' } as any)
  render(<ParentDashboard onBack={() => {}} />)
  await waitFor(() => expect(screen.getByText(/Request export/)).toBeInTheDocument())
  const btn = screen.getByRole('button', { name: /Request export/ })
  btn.click()
  await waitFor(() => expect(screen.getByRole('status')).toBeInTheDocument())
})

test('restrict processing updates privacy status', async () => {
  const learner = { learner_id: 'L1', display_name: 'Kid', grade_level: 4, lesson_completion_rate_7d: 10, streak_days: 1, irt_theta: 0, top_knowledge_gaps: [], ai_progress_summary: '' }
  vi.spyOn(ParentService, 'getTrustDashboard').mockResolvedValue({ learners: [learner] } as any)
  vi.spyOn(ParentService, 'getExportBundle').mockResolvedValue({ exports: [{ learner_id: 'L1', display_name: 'Kid', export_url: 'http://x', filename: 'f' }] } as any)
  vi.spyOn(DataRightsService, 'restrictProcessing').mockResolvedValue({ status: 'ok' } as any)
  render(<ParentDashboard onBack={() => {}} />)
  await waitFor(() => expect(screen.getByRole('button', { name: /Restrict processing/ })).toBeInTheDocument())
  const btn = screen.getByRole('button', { name: /Restrict processing/ })
  btn.click()
  await waitFor(() => expect(screen.getByText(/Processing restricted/)).toBeInTheDocument())
})

test('erasure request updates privacy status', async () => {
  const learner = { learner_id: 'L1', display_name: 'Kid', grade_level: 4, lesson_completion_rate_7d: 10, streak_days: 1, irt_theta: 0, top_knowledge_gaps: [], ai_progress_summary: '' }
  vi.spyOn(ParentService, 'getTrustDashboard').mockResolvedValue({ learners: [learner] } as any)
  vi.spyOn(ParentService, 'getExportBundle').mockResolvedValue({ exports: [{ learner_id: 'L1', display_name: 'Kid', export_url: 'http://x', filename: 'f' }] } as any)
  vi.spyOn(DataRightsService, 'requestErasure').mockResolvedValue({ status: 'queued' } as any)
  render(<ParentDashboard onBack={() => {}} />)
  await waitFor(() => expect(screen.getByRole('button', { name: /Request erasure/ })).toBeInTheDocument())
  const btn = screen.getByRole('button', { name: /Request erasure/ })
  btn.click()
  await waitFor(() => expect(screen.getByText(/Erasure request submitted/)).toBeInTheDocument())
})

test('privacy request failures show fallback message', async () => {
  const learner = { learner_id: 'L1', display_name: 'Kid', grade_level: 4, lesson_completion_rate_7d: 10, streak_days: 1, irt_theta: 0, top_knowledge_gaps: [], ai_progress_summary: '' }
  vi.spyOn(ParentService, 'getTrustDashboard').mockResolvedValue({ learners: [learner] } as any)
  vi.spyOn(ParentService, 'getExportBundle').mockResolvedValue({ exports: [{ learner_id: 'L1', display_name: 'Kid', export_url: 'http://x', filename: 'f' }] } as any)
  vi.spyOn(DataRightsService, 'restrictProcessing').mockRejectedValue(new Error('boom'))
  render(<ParentDashboard onBack={() => {}} />)
  await waitFor(() => expect(screen.getByRole('button', { name: /Restrict processing/ })).toBeInTheDocument())
  const btn = screen.getByRole('button', { name: /Restrict processing/ })
  btn.click()
  await waitFor(() => expect(screen.getByText(/boom/)).toBeInTheDocument())
})
