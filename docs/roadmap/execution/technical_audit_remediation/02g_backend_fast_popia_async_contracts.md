---
title: Technical Audit Remediation Phase 02G — Backend Fast POPIA Async Route Contracts
status: active-control
owner: roadmap-governance
reviewers: [roadmap-governance, release-management, documentation-governance]
audience: roadmap-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 30
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/roadmap, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
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
