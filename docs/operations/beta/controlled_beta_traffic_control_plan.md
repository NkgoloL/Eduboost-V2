---
title: Controlled Beta Traffic Control Plan
status: active-control
owner: operations
reviewers: [operations, security, release-management]
audience: operator
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 90
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/operations, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Controlled Beta Traffic Control Plan

This plan does not authorise controlled beta launch, deployment, or live learner
traffic.

- Controlled beta launch authorised: false
- Live learner traffic authorised: false

## Traffic Controls

- Controlled beta traffic must be explicitly enabled by a later activation gate.
- Access must be limited to the approved cohort.
- Public signup must remain disabled unless separately authorised.
- Any feature flag or allow-list must be reviewed before activation.
- Support and incident channels must be active before cohort access.

## Stop Conditions

Immediately pause controlled beta access if:

- learner data is exposed to the wrong guardian;
- consent enforcement fails;
- diagnostic or lesson generation returns unsafe content;
- availability or error rate breaches the beta threshold;
- data export or erasure flows fail for beta participants.
