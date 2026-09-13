---
title: "Engineering — PRD-6.0-6.4 Security Assurance Foundation"
status: "active"
owner: "engineering"
reviewers: ['engineering', 'architecture']
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# PRD-6.0-6.4 Security Assurance Foundation

PRD-6 starts the **Security Assurance and External Review** stream after PRD-5 POPIA privacy assurance closes.

This slice records application-visible readiness contracts for:

- DAST and API fuzzing readiness.
- Python/frontend dependency scanning readiness.
- Container/image scanning readiness.
- SBOM generation readiness.
- Secret-rotation drill readiness.
- Rate-limit and abuse-testing readiness.
- Critical endpoint authorization negative-test readiness.
- External review / penetration-test path readiness.

## Boundary

PRD-6.0-6.4 does **not** run a real external penetration test, alter branch protection, enable production release, enable deployment, enable release tags, enable public beta, enable live learner traffic, enable billing, or authorise PRD-7 implementation.

The next PRD-6 slice must turn this readiness contract into final security evidence, external/independent review evidence, reconciliation, and controlled handoff to PRD-7.
