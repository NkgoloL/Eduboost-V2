---
title: "Release — Audit Canonicalization Slice 001"
status: "active"
owner: "release"
reviewers: ['release', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Audit Canonicalization Slice 001

**Status:** implementation scaffold active, runtime call-site migration pending

This slice introduces a learner-scoped canonical audit seam:

- `app/services/audit_canonicalization_slice.py`
- `build_learner_audit_command(...)`
- `record_learner_audit_event(...)`

## Boundary

This slice does not delete any legacy audit repository and does not migrate audit tables.

## Next migration target

Future implementation batches should migrate selected learner/POPIA-sensitive call sites to `record_learner_audit_event(...)`, one small group at a time, with tests proving the canonical payload shape.
