---
title: "Auth Boundary Debt Report"
status: "active"
owner: "engineering"
reviewers: ["engineering"]
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-08-26"
review_interval_days: 60
evidence_command: "make docs-housekeeping-check"
code_anchors: ["docs/architecture/auth_boundary_debt_report.md"]
---

# Auth Boundary Debt Report

Generated at: `2026-08-03T14:03:20Z`

| Item | Value |
|---|---|
| Repository imports | - |
| LearnerRepository symbol present | False |
| Direct get_by_guardian present | False |

## Remaining debt

- Extract remaining auth repository interactions into canonical AuthService
- Remove auth router repository imports after AuthService extraction
- Remove auth transition ignore_imports from .importlinter
