---
title: "Engineering — PRD-2.7-2.9 Runtime KG Acceptance and Handoff"
status: "active"
owner: "engineering"
reviewers: ['engineering', 'architecture']
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# PRD-2.7-2.9 Runtime KG Acceptance and Handoff

Status: authority prepared  
Scope: final PRD-2 runtime acceptance, evidence capture, and controlled handoff to PRD-3

PRD-2 moved the knowledge graph from evidence artifacts into runtime application plumbing. This closure slice confirms that the runtime KG foundation, route projections, study-plan focus metadata, and rollback path exist behind the feature flag.

## Acceptance boundary

Runtime KG remains disabled by default. PRD-2.7-2.9 does not authorise production release, deployment, live learner traffic, public beta, billing, or PRD-3 implementation.

## Handoff

After evidence capture, the next authorised workstream is PRD-3 — Learner and Parent Vertical Journey Hardening. PRD-3 must decide how the learner/parent journey uses the runtime KG path in vertical flows.
