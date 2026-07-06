---
title: Post-Deploy Staging Smoke Checklist
status: active
owner: operations
reviewers: [operations, security, release-management]
audience: operator
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 90
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/operations, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Post-Deploy Staging Smoke Checklist

## Purpose

This checklist defines the required post-deploy smoke checks after a staging or
beta release candidate is deployed.

## Backend Smoke Checks

- runtime `/health` or equivalent health endpoint responds
- canonical `app.api_v2:app` import remains valid
- OpenAPI schema matches committed contract
- V2 API prefix responds
- legacy hidden route remains excluded or returns expected shutdown response
- global error envelope remains canonical

## Security and Compliance Smoke Checks

- authorization denial returns safe response
- consent-required denial returns safe response
- POPIA audit event path remains available
- no production secret placeholder is accepted
- dev-only endpoints remain unavailable in production mode

## Data Resilience Smoke Checks

- backup manifest exists
- restore evidence exists
- backup integrity check passes
- restore integrity check passes
- production restore approval remains enforced

## AI Safety Smoke Checks

- AI fixture validation passes
- refusal fixture validation passes
- prompt secret leakage guard passes
- CAPS alignment contract passes
- output schema contract passes

## Frontend Smoke Checks

- learner journey entrypoint loads
- parent journey entrypoint loads
- mocked learner journey spec is available
- mocked parent journey spec is available
- accessibility static check passes
- auth/consent denial UX contract passes

## Command

```bash
make post-deploy-staging-smoke-checklist-check
```
