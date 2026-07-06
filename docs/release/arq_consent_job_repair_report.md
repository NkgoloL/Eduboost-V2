---
title: ARQ Consent Job Repair Report
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

# ARQ Consent Job Repair Report

Generated at: `2026-05-17T22:05:40Z`

**Status:** implemented

- Consent reminder job uses `AsyncSessionLocal`.
- Consent reminder job constructs `ConsentRepository(session)`.
- Consent reminder job constructs `ConsentService` with explicit dependencies.
- FastAPI BackgroundTasks policy docstring updated.
