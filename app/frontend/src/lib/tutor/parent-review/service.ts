import { InMemoryParentReviewRepository } from './repository'
import { redactObjectForStorage } from './redaction'
import { toGuardianDTO } from './dto'
import { ParentReviewRetentionPolicy, isExpired } from './retention'

const repo = new InMemoryParentReviewRepository()

export async function saveSanitizedReview(payload: Record<string, unknown>) {
  const record = redactObjectForStorage(payload)
  if (!record) throw new Error('invalid_record')
  const saved = await repo.save(record)
  return toGuardianDTO(saved)
}

export async function listReviewsForLearner(learnerId: string) {
  const all = await repo.listByLearner(learnerId)
  // apply retention filter
  const now = Date.now()
  const filtered = all.filter((r) => !isExpired(r.timestamp, ParentReviewRetentionPolicy, now))
  return filtered.map(toGuardianDTO)
}

export const parentReviewService = { saveSanitizedReview, listReviewsForLearner }
