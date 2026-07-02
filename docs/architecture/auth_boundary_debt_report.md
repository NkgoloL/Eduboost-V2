---
title: "Auth Boundary Debt Report"
status: current-evidence
owner: architecture
reviewers: [architecture, engineering]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-02
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/architecture/README.md]
---

# Auth Boundary Debt Report

Generated at: `2026-06-27T02:18:40Z`

| Item | Value |
|---|---|
| Repository imports | - |
| LearnerRepository symbol present | False |
| Direct get_by_guardian present | False |

## Remaining debt

- Extract remaining auth repository interactions into canonical AuthService
- Remove auth router repository imports after AuthService extraction
- Remove auth transition ignore_imports from .importlinter
