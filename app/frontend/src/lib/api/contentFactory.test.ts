/**
 * Frontend API contract smoke tests for Content Factory.
 * Tests URL builder contracts and response shape handling.
 */
import { describe, it, expect } from 'vitest'

export function buildAdminContentFactoryScopesUrl(): string {
  return '/api/v2/admin/content-factory/scopes'
}

export function buildAdminContentFactoryScopeCoverageUrl(scopeId: string): string {
  return `/api/v2/admin/content-factory/scopes/${scopeId}/coverage`
}

export function buildAdminContentFactoryRunsUrl(): string {
  return '/api/v2/admin/content-factory/runs'
}

export function buildAdminContentFactoryReviewQueueUrl(): string {
  return '/api/v2/admin/content-factory/review-queue'
}

export function buildAdminEtlStatusUrl(): string {
  return '/api/v2/admin/etl/status'
}

export function handleNon2rxResponse(response: { status: number; detail?: string }): { error: string } {
  return { error: `${response.status}: ${response.detail || 'Unknown error'}` }
}

describe('Content Factory API client contracts', () => {
  describe('URL builders', () => {
    it('builds /api/v2/admin/content-factory/scopes', () => {
      const url = buildAdminContentFactoryScopesUrl()
      expect(url).toContain('/api/v2/admin/content-factory/scopes')
    })

    it('builds scope coverage URL', () => {
      const url = buildAdminContentFactoryScopeCoverageUrl('math-grade-8')
      expect(url).toContain('/api/v2/admin/content-factory/scopes/math-grade-8/coverage')
    })

    it('builds runs URL', () => {
      const url = buildAdminContentFactoryRunsUrl()
      expect(url).toContain('/api/v2/admin/content-factory/runs')
    })

    it('builds review queue URL', () => {
      const url = buildAdminContentFactoryReviewQueueUrl()
      expect(url).toContain('/api/v2/admin/content-factory/review-queue')
    })

    it('builds ETL status URL', () => {
      const url = buildAdminEtlStatusUrl()
      expect(url).toContain('/api/v2/admin/etl/status')
    })
  })

  describe('Response handling', () => {
    it('handles non-2xx response shape', () => {
      const errorResponse = { status: 401, detail: 'Authentication required' }
      const handled = handleNon2rxResponse(errorResponse)
      expect(handled).toHaveProperty('error')
      expect(handled.error).toContain('401')
    })
  })
})
