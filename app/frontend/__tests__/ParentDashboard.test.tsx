import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import { ParentDashboard } from '../src/components/eduboost/ParentDashboard'
import { ConsentService, DataRightsService, ParentService } from '../src/lib/api/services'
import { beforeEach, expect, test, vi } from 'vitest'

vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
  BarChart: ({ children }: any) => <div>{children}</div>,
  Bar: (_: any) => <div />,
  XAxis: (_: any) => <div />,
  YAxis: (_: any) => <div />,
  Tooltip: (_: any) => <div />,
}))

beforeEach(() => {
  window.localStorage.clear()
  window.localStorage.setItem('guardian_id', 'G1')
})

test('renders no learners when dashboard empty', async () => {
  vi.spyOn(ParentService, 'getTrustDashboard').mockResolvedValue({ learners: [] } as any)
  vi.spyOn(ParentService, 'getExportBundle').mockResolvedValue({ exports: [] } as any)
  render(<ParentDashboard onBack={() => {}} />)
  await waitFor(() => expect(screen.getByText(/No active learners were found/)).toBeInTheDocument())
})

test('renders Info Officer notice', async () => {
  vi.spyOn(ParentService, 'getTrustDashboard').mockResolvedValue({ learners: [] } as any)
  vi.spyOn(ParentService, 'getExportBundle').mockResolvedValue({ exports: [] } as any)
  render(<ParentDashboard onBack={() => {}} />)
  await waitFor(() => expect(screen.getByText(/POPIA Information Officer/)).toBeInTheDocument())
  await waitFor(() => expect(screen.getByText(/info.officer@eduboost.sa/)).toBeInTheDocument())
})

test('data rights export updates status with audit evidence', async () => {
  const learner = { learner_id: 'L1', display_name: 'Kid', grade_level: 4, lesson_completion_rate_7d: 10, streak_days: 1, irt_theta: 0, top_knowledge_gaps: [], ai_progress_summary: '' }
  vi.spyOn(ParentService, 'getTrustDashboard').mockResolvedValue({ learners: [learner] } as any)
  vi.spyOn(ParentService, 'getExportBundle').mockResolvedValue({ exports: [{ learner_id: 'L1', display_name: 'Kid', export_url: 'http://x', filename: 'f' }] } as any)
  vi.spyOn(DataRightsService, 'exportLearner').mockResolvedValue({ filename: 'bundle.json', status: { audit_event: 'audit-12345678' } } as any)
  render(<ParentDashboard onBack={() => {}} />)
  await waitFor(() => expect(screen.getByText(/Request export/)).toBeInTheDocument())
  const btn = screen.getByRole('button', { name: /Request export/ })
  btn.click()
  await waitFor(() => expect(screen.getByText(/Audit:/)).toBeInTheDocument())
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

test('consent grant updates status', async () => {
  const learner = { learner_id: 'L1', display_name: 'Kid', grade_level: 4, lesson_completion_rate_7d: 10, streak_days: 1, irt_theta: 0, top_knowledge_gaps: [], ai_progress_summary: '' }
  vi.spyOn(ParentService, 'getTrustDashboard').mockResolvedValue({ learners: [learner] } as any)
  vi.spyOn(ParentService, 'getExportBundle').mockResolvedValue({ exports: [] } as any)
  vi.spyOn(ConsentService, 'status').mockResolvedValue({ active: false, learner_id: 'L1' } as any)
  vi.spyOn(ConsentService, 'grant').mockResolvedValue({ id: 'C1', learner_id: 'L1', granted_at: new Date().toISOString(), expires_at: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(), message: 'Consent granted' } as any)
  render(<ParentDashboard onBack={() => {}} />)
  await waitFor(() => expect(screen.getByText(/No consent/)).toBeInTheDocument())
  const btn = screen.getByRole('button', { name: /Grant consent/ })
  btn.click()
  await waitFor(() => expect(screen.getByText(/Consent granted successfully/)).toBeInTheDocument())
})

test('consent revoke updates status', async () => {
  const learner = { learner_id: 'L1', display_name: 'Kid', grade_level: 4, lesson_completion_rate_7d: 10, streak_days: 1, irt_theta: 0, top_knowledge_gaps: [], ai_progress_summary: '' }
  vi.spyOn(ParentService, 'getTrustDashboard').mockResolvedValue({ learners: [learner] } as any)
  vi.spyOn(ParentService, 'getExportBundle').mockResolvedValue({ exports: [] } as any)
  vi.spyOn(ConsentService, 'status').mockResolvedValue({ active: true, learner_id: 'L1', days_remaining: 30 } as any)
  vi.spyOn(ConsentService, 'revoke').mockResolvedValue({ revoked: 1, message: 'Consent revoked' } as any)
  render(<ParentDashboard onBack={() => {}} />)
  await waitFor(() => expect(screen.getByText(/Consent active/)).toBeInTheDocument())
  const btn = screen.getByRole('button', { name: /Revoke consent/ })
  btn.click()
  await waitFor(() => expect(screen.getByText(/Consent revoked successfully/)).toBeInTheDocument())
})
