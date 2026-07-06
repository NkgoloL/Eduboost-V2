---
title: Next Execution Queue After JWT-001 / code_1071_1110
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

# Next Execution Queue After JWT-001 / code_1071_1110

## Next batch

`ARQ-001 / code_1111_1150` — ARQ dependency pin and worker import proof.

## Scope candidates

1. Detect dependency file convention.
2. Pin `arq`.
3. Regenerate requirements output if possible.
4. Add `import app.modules.jobs` clean-install smoke.
5. Validate `WorkerSettings.functions`.
6. Repair stale jobs checks to inspect `job_dependency_factory`.
