---
title: POPIA Consent Lifecycle Introspection
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

# POPIA Consent Lifecycle Introspection

Generated at: `2026-05-17T17:19:48Z`

| Check | Value |
|---|---|
| Router exists | True |
| Canonical service exists | True |
| Deprecated service exists | True |
| Generated UUID dependency count | 0 |
| Deprecated service imported by router | False |
| Canonical service imported by router | True |

## Router functions

- `_authenticated_actor_id`
- `_enforce_popia_learner_write`
- `cancel_erasure`
- `create_correction_request`
- `create_erasure_request`
- `create_export_request`
- `create_restriction_request`
- `deny_consent`
- `get_canonical_consent_service`
- `get_consent_service_for_router`
- `get_data_subject_rights_service_for_router`
- `grant_consent`
- `renew_consent`
- `withdraw_consent`

## Canonical service classes

- `ConsentService`
