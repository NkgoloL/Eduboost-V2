---
title: "Data — Transaction Ownership and Isolation Policy (TSR-7.8)"
status: "active"
owner: "data"
reviewers: ['data', 'engineering']
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Transaction Ownership and Isolation Policy (TSR-7.8)

## Principles
1. **Explicit Transaction Boundaries:**
   - Read queries must never issue implicit `COMMIT` statements.
   - Command and mutating workflows must explicitly control transaction scopes using async context managers (`async with session.begin():`).
2. **Audit Event Atomicity:**
   - Security audit logs emitted during domain operations must be guaranteed persistence within the same or immediate secondary fail-closed transaction.
3. **Tenant & Learner Isolation:**
   - All learner queries must enforce `WHERE learner_id = :learner_id` scoped to the authenticated caller's identity context.
