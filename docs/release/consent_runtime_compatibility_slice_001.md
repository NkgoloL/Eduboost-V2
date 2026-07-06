---
title: Consent Runtime Compatibility Slice 001
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

# Consent Runtime Compatibility Slice 001

**Status:** non-destructive implementation scaffold

## Scope

This slice introduces a consent runtime compatibility seam without merging consent tables or changing existing consent route behavior.

## Invariants

- `ConsentService` and `POPIADataRightsService` constructor surfaces are probed, not rewritten.
- Consent runtime operations normalize into audit-compatible event payloads.
- Read/write operation classification remains explicit in metadata.
- No `consent_records` / `parental_consents` merge is performed.

## Verification

```bash
make consent-runtime-compatibility-slice-check
```
