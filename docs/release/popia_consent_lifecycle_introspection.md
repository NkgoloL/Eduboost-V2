---
title: "Release — POPIA Consent Lifecycle Introspection"
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
