---
title: "Release — Next Execution Queue After JWT-001 / code_1071_1110"
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
