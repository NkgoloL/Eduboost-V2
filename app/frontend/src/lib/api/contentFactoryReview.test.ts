import { describe, expect, it } from 'vitest'

function reviewQueueUrl() {
  return '/api/v2/admin/content-factory/review-queue'
}

function reviewBundleUrl(artifactId: string) {
  return `/api/v2/admin/content-factory/artifacts/${artifactId}/review-bundle`
}

function bulkApproveBody(artifactIds: string[], notes: string) {
  return { artifact_ids: artifactIds, notes }
}

function bulkRejectBody(artifactIds: string[], reason: string) {
  return { artifact_ids: artifactIds, reason }
}

function handleNon2xxResponse(response: { status: number; detail?: string }) {
  return { error: `${response.status}: ${response.detail || 'Unknown error'}` }
}

describe('Content Factory review API contracts', () => {
  it('fetchReviewQueue builds admin URL', () => {
    expect(reviewQueueUrl()).toContain('/api/v2/admin/content-factory/review-queue')
  })

  it('fetchReviewBundle builds admin URL', () => {
    expect(reviewBundleUrl('artifact-1')).toContain('/api/v2/admin/content-factory/artifacts/artifact-1/review-bundle')
  })

  it('bulkApproveReview builds admin body', () => {
    expect(bulkApproveBody(['a'], 'reviewed')).toEqual({ artifact_ids: ['a'], notes: 'reviewed' })
  })

  it('bulkRejectReview builds admin body', () => {
    expect(bulkRejectBody(['a'], 'bad source')).toEqual({ artifact_ids: ['a'], reason: 'bad source' })
  })

  it('non-2xx response handled', () => {
    expect(handleNon2xxResponse({ status: 409, detail: 'blocked' }).error).toContain('409')
  })
})
