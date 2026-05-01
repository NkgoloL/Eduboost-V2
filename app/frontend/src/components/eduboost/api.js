export async function getLearnerMasteryAPI(learnerId) {
  const res = await fetch(`/api/v1/learners/${learnerId}/mastery`)
  return res.json()
}

export async function runDiagnosticAPI(learnerId, opts) {
  const res = await fetch(`/api/v1/diagnostic/start`, { method: 'POST' })
  return res.json()
}

export async function awardXPAPI(learnerId, xp) {
  const res = await fetch(`/api/v1/learners/${learnerId}/xp`, { method: 'POST' })
  return res.json()
}

export async function getLearnerProfileAPI(learnerId) {
  const res = await fetch(`/api/v1/learners/${learnerId}/profile`)
  return res.json()
}
