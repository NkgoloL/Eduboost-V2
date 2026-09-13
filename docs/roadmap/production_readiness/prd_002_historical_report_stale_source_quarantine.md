---
title: "PRD-0.2 — Historical Report and Stale-Source Quarantine"
status: "active"
owner: "product"
reviewers: ['product', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# PRD-0.2 — Historical Report and Stale-Source Quarantine

**Status:** Authority recorded; evidence pending capture  
**Stream:** PRD-PRODUCTION-READINESS  
**Depends on:** PRD-0.1 Canonical current-state documentation refresh

## Purpose

PRD-0.2 prevents historical reports from being mistaken for live roadmap authority after RR closure, KG closure, KG-ACT-001, KG-8, the KG closure report, PRD-0.0, and PRD-0.1.

## Scope

- Create a reports-directory authority note.
- Create a stale-source quarantine register.
- Mark the July 2026 true-status report as historical and superseded.
- Remove the Windows `Zone.Identifier` metadata sidecar from the reports directory.
- Preserve current authority boundaries.

## Not in scope

- No production release.
- No deployment.
- No public beta or live learner traffic.
- No billing launch or live payments.
- No new KG slice.
- No PRD-1 implementation.

## Next item after evidence

After PRD-0.2 evidence is captured and valid, the next authorised cleanup item is:

`PRD-0.3 — Documentation housekeeping ratchet refresh`
