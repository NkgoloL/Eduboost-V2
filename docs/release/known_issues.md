---
title: "Release — Known Issues And Beta Limitations"
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
# Known Issues And Beta Limitations

Status: active beta limitation register

## Current Limitations

- Public beta is blocked until CI, staging smoke, migration, backup, restore, rollback, legal/security/product approval, and go/no-go evidence exists.
- CAPS content is limited; current README context states Grade 4 Mathematics has 14 approved starter items against a 120-item production target.
- Staging smoke evidence is pending runtime execution.
- Migration, restore, and rollback evidence are pending runtime execution.
- Branch protection evidence requires repository administrator action.
- Legal, security, educator/content, product, and release-owner approvals remain external.
- Local unit evidence has one accepted non-failing AsyncMock warning tracked in `docs/release/unit_test_evidence.md`.

## User-Facing Beta Risk

Do not onboard real learner data or public beta users until this file is reviewed with the release decision log and beta acceptance criteria.