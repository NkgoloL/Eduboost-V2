---
title: "Technical Audit Remediation Phase 02G — Backend Fast POPIA Async Route Contracts"
status: "active"
owner: "compliance"
reviewers: ['compliance', 'legal', 'engineering']
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Technical Audit Remediation Phase 02G — Backend Fast POPIA Async Route Contracts

## Purpose

Reduce the remaining backend-fast failure cluster reported after Phase 02F by hardening POPIA service writes and route/auth contract behaviour under async test doubles.

## Scope

- POPIA data-subject-rights service DB mutation helper.
- LearnerRepository soft-delete DB-add handling under AsyncMock-backed sessions.
- Focused verifier and evidence collector for Phase 02G.
- Backend-fast retry remains the authority gate.

## Non-scope

- No Phase 02R governance changes.
- No passing backend-fast candidate evidence unless `make test-fast` exits 0.
- No live database migration.
- No runtime knowledge-graph implementation; KG remains a future architectural north star.

## Evidence policy

Phase 02G evidence may be recorded separately once the focused verifier passes. It does not replace backend-fast candidate evidence. The next controlled step after Phase 02G evidence is to rerun `bash scripts/audit_remediation/collect_backend_fast_evidence.sh`.
