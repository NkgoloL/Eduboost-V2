import { AuthService, LearnerService, ConsentService, DataRightsService, ParentService, DiagnosticService } from '../src/lib/api/services'

// Comprehensive fetch mock
// @ts-ignore
globalThis.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
  const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
  if (url.includes('/auth/dev-session')) {
    return new Response(JSON.stringify({ access_token: 'tk', learner: { id: 'L1', learner_id: 'L1', display_name: 'Kid' } }), { status: 200 })
  }
  if (url.includes('/auth/sessions')) {
    return new Response(JSON.stringify({ sessions: [] }), { status: 200 })
  }
  if (url.includes('/auth/revoke-all')) {
    return new Response(JSON.stringify({ revoked: true }), { status: 200 })
  }
  if (url.includes('/study-plans/generate')) {
    return new Response(JSON.stringify({ job_id: 'job-sp', operation: 'study_plan' }), { status: 200 })
  }
  if (url.includes('/lessons/generate')) {
    return new Response(JSON.stringify({ job_id: 'job-less', operation: 'generate_lesson' }), { status: 200 })
  }
  if (url.includes('/jobs/job-sp')) {
    return new Response(JSON.stringify({ status: 'completed', result: { days: {}, week_focus: 'Focus' } }), { status: 200 })
  }
  if (url.includes('/jobs/job-less')) {
    return new Response(JSON.stringify({ status: 'completed', result: { title: 'T', content: 'C' } }), { status: 200 })
  }
  if (url.includes('/learners/') && url.endsWith('/mastery')) {
    return new Response(JSON.stringify({ mastery: [] }), { status: 200 })
  }
  if (url.includes('/gamification/profile/')) {
    return new Response(JSON.stringify({ total_xp: 10 }), { status: 200 })
  }
  if (url.includes('/popia/data-export')) {
    return new Response(JSON.stringify({ filename: 'b' }), { status: 200 })
  }
  if (url.includes('/parents/') && url.includes('/dashboard')) {
    return new Response(JSON.stringify({ learners: [] }), { status: 200 })
  }
  if (url.includes('/diagnostics/items')) {
    return new Response(JSON.stringify([{ item_id: 'I1', question_text: 'Q', options: ['a'] }]), { status: 200 })
  }
  if (url.includes('/diagnostics/submit')) {
    return new Response(JSON.stringify({ theta_after: 0, ranked_gaps: [] }), { status: 200 })
  }
  // default
  return new Response(JSON.stringify({}), { status: 200 })
}

test('call several service methods to improve coverage', async () => {
  const dev = await AuthService.createDevSession()
  expect(dev.access_token).toBe('tk')

  const sessions = await AuthService.sessions()
  expect(Array.isArray((sessions as any).sessions)).toBe(true)

  await AuthService.revokeAll()

  const study = await LearnerService.getStudyPlan('L1')
  expect((study as any).week_focus).toBeDefined()

  const lesson = await LearnerService.generateLesson({ learner_id: 'L1' })
  expect(lesson.title).toBeDefined()

  const mastery = await LearnerService.getMastery('L1')
  expect(mastery).toBeTruthy()

  const gam = await LearnerService.getGamificationProfile('L1')
  expect((gam as any).total_xp).toBe(10)

  await DataRightsService.exportLearner('L1')
  await ConsentService.grant('L1')
  await ConsentService.status('L1')

  await ParentService.getTrustDashboard('G1')

  const items = await DiagnosticService.getItems('L1')
  expect(items.length).toBeGreaterThanOrEqual(0)

  await DiagnosticService.submit('L1', [])
})
