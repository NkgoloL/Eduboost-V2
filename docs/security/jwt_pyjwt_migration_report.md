---
title: "JWT PyJWT Migration Report"
status: "active"
owner: "engineering"
reviewers: ["engineering"]
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-08-26"
review_interval_days: 60
evidence_command: "make docs-housekeeping-check"
code_anchors: ["docs/security/jwt_pyjwt_migration_report.md"]
---

# JWT PyJWT Migration Report

PRD-10.0-10.4 removes the runtime dependency on `python-jose` and places
JWT handling behind `app.core.jwt_compat`, backed by PyJWT.

Regression controls cover keyring round-trip behaviour, `kid` based previous
key decoding, tampered-token rejection, and requirements checks confirming
`python-jose` is no longer declared for runtime or dev installs.

This migration does not authorise live learner traffic.
