---
title: Consent Service Compatibility Contract
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

# Consent Service Compatibility Contract

This contract records the safe path for resolving split consent runtime and persistence paths.

## Scope

This batch does not merge `consent_records` and `parental_consents`. It creates inventory and normalization helpers only.

## Required decisions before consolidation

| Question | Required answer before implementation |
|---|---|
| Is `consent_records` current state, event history, or both? | TODO |
| Is `parental_consents` current state, guardian/learner relationship consent, or legacy? | TODO |
| Which service owns `require_active_consent` at runtime? | TODO |
| Does consent grant/revoke emit canonical append-only audit events? | TODO |
| What data retention rule applies to historical consent records? | TODO |

## Release-safety invariants

- Active-consent checks must use a single canonical runtime path.
- POPIA/learner routes must preserve explicit read/write authorization.
- Consent event history must not be dropped without legal/security approval.
- Table consolidation requires ADR plus migration evidence.
- Constructor/signature compatibility may be repaired before schema consolidation.

## Migration sequence

1. Generate inventory.
2. Fix runtime constructor/signature errors without changing tables.
3. Add compatibility adapters/normalizers.
4. Write ADR for table semantics.
5. Migrate data only after approval.
6. Delete legacy paths last.
