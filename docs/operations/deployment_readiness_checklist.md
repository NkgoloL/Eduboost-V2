---
title: Deployment Readiness Checklist
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

# Deployment Readiness Checklist

## Runtime Contract

- `make runtime-check`
- `make openapi-check`
- `make route-inventory-check`

## Authorization Contract

- `make phase2-authz-check`
- `make learner-authz-check`
- `make phase2-authz-closure`

## POPIA Consent/Audit Contract

- `make popia-consent-closure-check`
- `make popia-consent-gate-check`
- `make popia-consent-boundary-check`
- `make popia-consent-order-check`
- `make popia-consent-source-check`
- `make popia-consent-rejection-audit-check`

## Environment Contract

- `make environment-security-check`
- `make dev-only-endpoint-check`
- `make production-secret-placeholder-check`

## Production Requirements

Production must use Azure Key Vault for required secrets and must fail closed
when `AZURE_KEY_VAULT_URL` is missing.

## Cluster D Closure

- `make cluster-d-closure-check`

## Release Gate Evidence

- `python3 scripts/generate_release_evidence_manifest.py`

## Release Gate Evidence

- `make staging-release-gate-check`

## Data Resilience Evidence

- `make cluster-e-closure-check`

## AI Safety Evidence

- `make cluster-f-closure-check`

## Frontend Journey Evidence

- `make cluster-g-closure-check`

## Release Evidence

Before staging or production release, attach command output for all checklist
items to the PR or release evidence record.
