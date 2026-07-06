---
title: Phase 2R Gate 2R.2 Control/Evidence Repair Note
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

# Phase 2R Gate 2R.2 Control/Evidence Repair Note

This repair hardens the gate-control and evidence-collection tooling after Gate 2R.2.

It makes `scripts/phase02r_gate_control.py` validate whichever gate is recorded as
approved, instead of hard-coding Gate 2R.1 approval/evidence paths. It also changes
Gate 2R.2 evidence collection to call the focused Gate 2R.2 verifier with real-source
acquisition instead of the static scaffold verifier.

This note does not close Gate 2R.2 and does not authorise Gate 2R.3. It only records
tooling repair needed to prevent a failed Gate 2R.2 evidence pack from being treated
as a valid transition basis.
