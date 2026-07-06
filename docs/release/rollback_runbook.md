---
title: Release Rollback Runbook
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

# Release Rollback Runbook

Status: pending staging drill
Scope: API, frontend, database, configuration, and feature flags for controlled beta.

## Preconditions

- Identify the release commit and the last known good commit.
- Confirm backup availability and checksum before database rollback.
- Confirm the release owner has approved rollback unless this is an emergency incident.

## API Rollback

1. Redeploy the last known good API image or commit.
2. Confirm `GET /api/v2/health/deep` returns healthy.
3. Check API logs for startup, migration, auth, and POPIA errors.

## Frontend Rollback

1. Redeploy the last known good frontend artifact.
2. Confirm login, dashboard load, lesson generation entry point, and consent screens render.
3. Verify CORS and security headers from the deployed frontend origin.

## Database Rollback

Default policy: prefer backup/restore over Alembic downgrade unless the migration explicitly declares a tested downgrade target.

- Upgrade proof command: `alembic upgrade head`
- Downgrade target: pending per migration evidence
- Restore fallback: use `docs/release/restore_drill_evidence.md` once proven

## Post-Rollback Checks

- `GET /api/v2/health/deep`
- Auth register/login/refresh/logout
- Lesson generation smoke
- Consent grant and POPIA export smoke
- Error logs and alert channel review