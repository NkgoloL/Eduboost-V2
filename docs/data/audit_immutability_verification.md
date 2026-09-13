---
title: "Data — Audit Immutability Verification (TSR-7.10)"
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
# Audit Immutability Verification (TSR-7.10)

## Immutability Safeguards
PostgreSQL audit logs in table `audit_events` are protected by multiple redundant database-level controls:

1. **PostgreSQL Rules (`audit_events_no_update`, `audit_events_no_delete`):**
   - Direct DML `UPDATE` and `DELETE` queries are converted to `DO INSTEAD NOTHING`.
2. **PostgreSQL Row-Level Triggers (`trg_audit_events_immutable`):**
   - Fails closed with exception `'audit_events is append-only – modifications are forbidden'`.
3. **Role Permission Constraints:**
   - App roles have `REVOKE UPDATE, DELETE ON audit_events`.

## Automated Proof
Verified by `tests/integration/test_audit_immutability.py`, asserting that `INSERT` succeeds while `UPDATE` and `DELETE` queries fail to modify or delete historical records.
