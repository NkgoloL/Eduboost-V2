---
title: "Content Factory Promotion Gates"
status: active
owner: "content-factory"
reviewers: ["content-factory", "curriculum", "engineering"]
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: '2026-09-23'
review_interval_days: 90
evidence_command: make docs-housekeeping-check
code_anchors: "[app/services/content_factory, data/content_factory, docs/content_factory/control_plane.md]"
---
# Content Factory Promotion Gates

Production promotion must fail closed unless all required checks pass:

- diagnostic item and lesson coverage are green for configured targets
- production-bound artifacts are approved
- rejected, quarantined, and validation-failed artifacts are blocked
- source citations exist and pass provenance validation
- staging seed verification passes
- an admin actor initiates the action

Future configured layers must not silently pass when targets exist and coverage is unmet.
