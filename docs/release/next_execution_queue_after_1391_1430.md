---
title: Next Execution Queue After TX-001 / code_1391_1430
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

# Next Execution Queue After TX-001 / code_1391_1430

## Recommended next batch

`TX-001B / code_1431_1470` — targeted rollback proof for one high-risk multi-write flow.

## Preferred scope

Start with POPIA lifecycle transition + audit write because it is both compliance-critical and transaction-sensitive.

Candidate acceptance:

1. Use a transactional test DB fixture.
2. Force audit write failure after consent transition attempt.
3. Assert consent transition is rolled back.
4. Force consent write failure before audit attempt.
5. Assert no audit orphan is written.
6. Record evidence without claiming all domains are atomic.
