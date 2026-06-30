import type { RetentionPolicy } from './types'

export const DEFAULT_RETENTION_DAYS = 90

export const ParentReviewRetentionPolicy: RetentionPolicy = {
  retentionDays: DEFAULT_RETENTION_DAYS,
}

export function isExpired(timestamp: string, policy: RetentionPolicy = ParentReviewRetentionPolicy, now = Date.now()): boolean {
  const ts = Date.parse(timestamp)
  if (Number.isNaN(ts)) return false
  const cutoff = now - policy.retentionDays * 24 * 60 * 60 * 1000
  return ts < cutoff
}
