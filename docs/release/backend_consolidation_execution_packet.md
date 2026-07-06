---
title: Backend Consolidation Execution Packet
status: release-record
owner: release-management
reviewers: [release-management, evidence-custodian, documentation-governance]
audience: release-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 180
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/release, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Backend Consolidation Execution Packet

**Status:** implementation sequencing only

This packet defines the safe execution path for the backend consolidation dragons after the diagnostic/readiness batches.

## Execution sequence

| Sequence | Workstream | Scope | Destructive? | Required previous evidence |
|---:|---|---|---|---|
| 1 | Audit canonicalization | migrate call sites to canonical audit shape or adapter | no | audit inventory |
| 2 | Consent runtime repair | fix constructor/signature compatibility only | no | consent inventory |
| 3 | Schema drift DB proof | compare ORM tables to disposable DB tables | no | migration evidence |
| 4 | Deep-readiness design | document/guard deep health checks | no | health readiness contract |
| 5 | ADR decisions | decide audit/consent table semantics | no | inventories + DB proof |
| 6 | Runtime rewiring | only after contracts/tests prove compatibility | no/low | full suite green |
| 7 | Legacy deletion | delete only approved legacy paths | yes | release-owner approval |

## Explicitly forbidden in early execution

- deleting audit repositories before call-site migration
- merging `consent_records` and `parental_consents` without ADR and migration evidence
- discarding audit/consent history
- using `alembic stamp head` as a blind repair
- adding public health checks that write to the database
