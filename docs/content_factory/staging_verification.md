# Content Factory Staging Verification

PR-CF-007 adds all-scope staging readiness verification for configured Content Factory scopes.

## Policy

Human review blocks production promotion and learner-visible release. It does not block coverage calculation, dry-run seed planning, staging verification reporting, or blocker inventory generation.

## Admin endpoints

- `POST /api/v2/admin/content-factory/staging-verification/all-scopes`
- `GET /api/v2/admin/content-factory/staging-verification/runs`
- `GET /api/v2/admin/content-factory/staging-verification/runs/{run_id}`
- `POST /api/v2/admin/content-factory/scopes/{scope_id}/staging-verification`
- `GET /api/v2/admin/content-factory/scopes/{scope_id}/staging-readiness`

## Readiness outputs

Each scope report distinguishes:

- `can_seed_staging`: true when approved/provenance-valid content can be staged, including partial staging.
- `can_promote_production`: true only when all configured targets are ready and no blockers remain.
- `blockers`: deterministic per-layer reasons such as pending review, missing coverage, invalid provenance, validation failure, license, or source quality.

## Persistence

Verification runs are stored in:

- `content_staging_verification_runs`
- `content_staging_verification_scope_results`

These tables preserve summary and blocker JSON for release evidence.

## Non-goals

This does not enable real provider generation, automatic approval, production promotion automation, learner-facing release, or reviewer workflow changes.
