---
title: "Release — Backend Runtime Probe Contract"
status: "active"
owner: "release"
reviewers: ['release', 'engineering']
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Backend Runtime Probe Contract

**Status:** diagnostic fixtures only

This contract defines non-destructive runtime probe fixtures for backend consolidation.

## Scope

The probes validate compatibility helpers and expected readiness semantics using local fixtures. They do not touch the live database, do not call external services, and do not alter runtime routes.

## Fixture catalog

| Fixture | Purpose |
|---|---|
| `tests/fixtures/backend_consolidation/audit_canonical_events.json` | canonical audit event normalization expectations |
| `tests/fixtures/backend_consolidation/consent_runtime_events.json` | consent event classification and audit mapping expectations |
| `tests/fixtures/backend_consolidation/deep_readiness_expected_checks.json` | expected deep-readiness check catalog |

## Safety rules

- Audit fixtures must preserve learner/resource identifiers in payload or resource fields.
- Consent fixtures must classify read/write boundaries explicitly.
- Deep-readiness fixtures must mark write probes as internal-only and disabled by default.
- No fixture may approve deletion, table consolidation, or Alembic stamping.
