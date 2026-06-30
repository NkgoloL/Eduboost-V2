---
title: "ADR 0007: PostgreSQL Audit Ledger"
status: active
owner: architecture
reviewers: [engineering, architecture]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 180
evidence_command: make docs-housekeeping-stage3-check
code_anchors: []
---
# ADR 0007: PostgreSQL Audit Ledger

## Status
Proposed

## Context
EduBoost needs durable audit trails for learner-data access, consent changes, administrative actions, security-sensitive operations, and production incidents. Audit evidence must be queryable for compliance and operational review.

## Decision
Use PostgreSQL as the canonical audit ledger store, with append-oriented records and integrity controls appropriate to the sensitivity of each event class.

Expected properties:

- Structured event schema with actor, action, resource, purpose, timestamp, correlation/request ID, and outcome.
- No unnecessary learner PII in audit payloads.
- Tamper-evidence where high-risk events require it.
- Retention rules aligned with legal/compliance requirements.

## Consequences

- **Pros**: Transactional consistency, queryability, simpler backup/restore alignment with application data.
- **Cons**: Requires schema discipline, access restrictions, retention policy, and migration care.
