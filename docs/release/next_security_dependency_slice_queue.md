---
title: Next Security and Dependency Slice Queue
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

# Next Security and Dependency Slice Queue

**Status:** queued after auth router boundary closure

## Candidate next batch

`code_751_780`: dependency pinning, JWT key rotation, and remaining auth service extraction.

## Scope candidates

1. Pin Python dependency lock files using the project virtual environment.
2. Add JWT `kid` support and current/previous key rotation contract.
3. Move remaining auth router repository usage into a canonical AuthService.
4. Remove auth router import-linter transition allowances.
5. Add regression tests for refresh-token authorization scope after key rotation.
