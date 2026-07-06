---
title: Next Execution Queue After TX-001B / code_1431_1470
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

# Next Execution Queue After TX-001B / code_1431_1470

## Recommended next batch

`TX-002 / code_1471_1510` — wire POPIA lifecycle routes/dependencies through the transactional lifecycle boundary or add production-service rollback proof.

## Scope candidates

1. Find canonical POPIA lifecycle dependency construction.
2. Wrap lifecycle consent service + audit writer in `TransactionalPOPIAConsentLifecycleService`.
3. Add HTTP/runtime tests proving audit failure does not persist consent transition.
4. Keep external legal review and full consent-blocking sweep outside this narrow transaction proof.
