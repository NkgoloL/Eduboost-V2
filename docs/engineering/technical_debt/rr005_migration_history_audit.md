---
title: "RR-005 Migration History Audit"
status: active
owner: engineering
audience: developer
source_of_truth: true
evidence_command: "PYTHONPATH=. python3 scripts/technical_debt/audit_rr005_technical_debt.py --json"
---

# RR-005 Migration History Audit

RR-005 audits Alembic migration history and records a squash decision.

## Squash decision

Current decision: **defer migration squash**.

Reason:

- migration history is already part of audit evidence;
- destructive production database changes remain blocked;
- a squash requires a dedicated migration window, restore proof, and rollback proof.

## Evidence

The RR-005 audit records migration file count, deprecated migration count, merge migration count, and revision/down-revision metadata where it can be parsed safely.
