import type { ParentReviewRecord } from './types'

// Simple server-side persistence abstraction. In FE-PR-013-B we provide an
// in-memory implementation suitable for tests and later wiring to durable
// storage in FE-PR-013-C. The abstraction prevents exposing raw transcripts.

export interface ParentReviewRepository {
  save(record: ParentReviewRecord): Promise<ParentReviewRecord>
  listByLearner(learnerId: string): Promise<ParentReviewRecord[]>
  deleteOlderThan(cutoffIso: string): Promise<number>
}

export class InMemoryParentReviewRepository implements ParentReviewRepository {
  private store: ParentReviewRecord[] = []

  async save(record: ParentReviewRecord): Promise<ParentReviewRecord> {
    // assign an id and store only the redacted record
    const id = `pr-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
    const toStore = { ...record, id }
    this.store.push(toStore)
    return toStore
  }

  async listByLearner(learnerId: string): Promise<ParentReviewRecord[]> {
    return this.store.filter((r) => r.learnerId === learnerId)
  }

  async deleteOlderThan(cutoffIso: string): Promise<number> {
    const before = this.store.length
    const cutoff = Date.parse(cutoffIso)
    this.store = this.store.filter((r) => Date.parse(r.timestamp) >= cutoff)
    return before - this.store.length
  }
}
