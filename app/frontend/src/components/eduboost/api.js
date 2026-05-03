export async function getLearnerMasteryAPI(learnerId) {
  const res = await fetch(`/api/v2/learners/${learnerId}/mastery`)
  return res.json()
}

export async function runDiagnosticAPI(learnerId, opts) {
  const res = await fetch(`/api/v2/diagnostics/${learnerId}`, { method: 'POST' })
  return res.json()
}

export async function awardXPAPI(learnerId, xp) {
  const res = await fetch(`/api/v2/gamification/award-xp`, { method: 'POST' })
  return res.json()
}

export async function getLearnerProfileAPI(learnerId) {
  const res = await fetch(`/api/v2/learners/${learnerId}`)
  return res.json()
}
