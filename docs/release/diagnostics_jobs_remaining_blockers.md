---
title: Diagnostics and Jobs Remaining Blockers
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

# Diagnostics and Jobs Remaining Blockers

**Status:** queued after code_691_720

## Required follow-up

1. Add real DB integration tests proving diagnostic attempts cannot submit unserved item IDs.
2. Add regression tests proving historical theta updates use each historical item's parameters.
3. Run ARQ worker-context smoke for `send_consent_reminders`.
4. Confirm notification provider configuration for real consent reminder delivery.
5. Expand diagnostics integrity hooks into canonical diagnostics service methods, not just router entrypoints.

## Non-goals

This batch does not run a live ARQ worker and does not execute against production data.
