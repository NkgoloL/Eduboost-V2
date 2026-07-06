---
title: Technical Audit Remediation Phase 02F — Backend Fast Item/Seed/Router Contracts
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

# Technical Audit Remediation Phase 02F — Backend Fast Item/Seed/Router Contracts

**Status:** implementation package ready  
**Authority gate:** `make test-fast`  
**Purpose:** clear the next backend-fast failure clusters after Phase 02E without weakening the backend-fast evidence standard.

## Targeted clusters

1. **Staging seed executor/session doubles** — support real `AsyncSession` objects and lightweight unit-test session doubles by no-oping commit/rollback when not provided, while still committing in real sessions.
2. **Diagnostic item bank selection** — treat missing DB-default IRT quality state as `uncalibrated` for fresh ORM objects and MagicMock-backed unit tests.
3. **V2 router contract** — declare the existing `tutor` router fragment in the V2 router contract.
4. **Study-plan consent DB wiring** — preserve the audited DB import contract while continuing to use `get_db` for route dependencies.

## Non-scope

- No passing backend-fast evidence is created by this slice.
- No product release-readiness claim is made.
- No Phase 02R governance is changed.
- No live database migration is executed.
- No runtime knowledge-graph implementation is added. The KG pivot remains a future architectural north star only.

## Evidence policy

Phase 02F evidence may be recorded separately. The backend-fast authority gate remains blocked until:

```bash
bash scripts/audit_remediation/collect_backend_fast_evidence.sh
```

runs `make test-fast` and exits successfully.
