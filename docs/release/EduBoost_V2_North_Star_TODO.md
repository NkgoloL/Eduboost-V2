---
title: EduBoost V2 North-Star TODO
status: release-record
owner: release-management
reviewers: [release-management, evidence-custodian, documentation-governance]
audience: release-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 180
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/release, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# EduBoost V2 North-Star TODO

## North Star

Ship a production-capable EduBoost V2 backend by converting repository-level completion into external runtime evidence, release-owner approval, and controlled production deployment.

## Current state

- Backend consolidation slices: complete through 530/530.
- Repository implementation: green, per user-provided status.
- Runtime-facing helpers: implemented for audit, consent, and read-only deep readiness.
- Phase 1 corrective package: verified complete with disposable PostgreSQL evidence and corrective audit pass.
- Production launch: pending external evidence and human signoff.

## P0 — Freeze and evidence refresh

- [ ] Pull latest `codex/production_readiness`.
- [ ] Confirm clean working tree with `git status --short`.
- [ ] Run `pytest -c pytest.ini -q --no-cov`.
- [ ] Save output to `docs/release/full_pytest_latest_green.txt`.
- [ ] Run final runtime enablement/report targets.
- [ ] Commit and push refreshed evidence.

## P1 — Remote CI evidence

- [ ] Confirm final branch pushed.
- [ ] Run remote CI.
- [ ] Record GitHub Actions URL in `docs/release/ci_evidence.md`.
- [ ] Confirm CI green.
- [ ] Record warnings/skips.

## P2 — Disposable DB proof

- [ ] Provision disposable PostgreSQL DB.
- [ ] Set safe test-only `DATABASE_URL`.
- [ ] Run `make disposable-db-schema-proof-execute`.
- [ ] Run `make disposable-db-schema-proof-execution-check`.
- [ ] Run `make schema-drift-check-db`.
- [ ] Commit generated DB proof evidence.

## P3 — Staging smoke

- [ ] Deploy current branch to staging.
- [ ] Set `STAGING_BASE_URL`.
- [ ] Run `make staging-smoke`.
- [ ] Run `make staging-smoke-check`.
- [ ] Commit staging smoke evidence.

## P4 — Operational drills

- [ ] Backup drill.
- [ ] Restore drill.
- [ ] Rollback drill.
- [ ] Monitoring dashboard verification.
- [ ] Incident response handoff verification.

## P5 — Human approvals

- [ ] Security review.
- [ ] POPIA/privacy review.
- [ ] Legal review.
- [ ] CAPS/content review.
- [ ] Release-owner go/no-go signoff.

## P6 — Controlled production deployment

- [ ] Confirm production secrets configured.
- [ ] Confirm production deployment plan.
- [ ] Confirm rollback command and owner.
- [ ] Execute approved deployment window.
- [ ] Run post-deployment smoke.
- [ ] Archive final launch evidence.

## Explicitly blocked until approval

- [ ] Drop `audit_logs`.
- [ ] Merge `consent_records` and `parental_consents`.
- [ ] Delete audit or consent history.
- [ ] Use `alembic stamp head` as repair.
- [ ] Run production DB mutation outside approved migration window.
- [ ] Add public mutating health/write probes.
