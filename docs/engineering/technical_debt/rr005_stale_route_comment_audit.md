---
title: "RR-005 Stale Route Comment Audit"
status: active
owner: engineering
audience: developer
source_of_truth: true
evidence_command: "PYTHONPATH=. python3 scripts/technical_debt/audit_rr005_technical_debt.py --json"
---

# RR-005 Stale Route Comment Audit

This audit records stale route comments across active router files.

## Patterns

The audit checks router comments for:

- TODO
- FIXME
- HACK
- temporary
- legacy
- deprecated
- shim
- remove after

## Scope boundary

RR-005 records the route-comment debt and creates a follow-up basis. It does not delete routes or rewrite router behaviour without call-site proof.
