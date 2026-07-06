---
title: Phase 2R Gate 2R.2 Implementation Note — Secure Acquisition
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

# Phase 2R Gate 2R.2 Implementation Note — Secure Acquisition

**Status:** Implementation package applies Gate 2R.2 secure acquisition primitives only.

This note is intentionally not a closure report. Gate 2R.2 closure still requires
clean candidate evidence, approval, and a separate transition commit before Gate
2R.3 can be authorised.

## Implemented by package

- Immutable local object-store adapter for development and CI verification.
- Controlled acquisition service with fail-closed rights checks.
- Checksum verification before and after storage.
- Path-containment validation for local source acquisition.
- Optional manifest-based CLI for dry-run, real acquisition, or explicitly gated
  missing-source download.
- Focused Gate 2R.2 verifier and unit tests.

## Explicitly not implemented

- Gate 2R.3 extraction and chunking.
- Gate 2R.4 curriculum mapping.
- Gate 2R.5 active corpus activation/retrieval wiring.
- Gate 2R.6 generation grounding.
- Gate 2R.7 tutor/study-plan delivery.
- Gate 2R.8 final evaluation/release closure.
