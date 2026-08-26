---
title: "Auth Service Extraction Report"
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
code_anchors: ["docs/architecture/auth_service_extraction_report.md"]
---

# Auth Service Extraction Report

Generated at: `2026-08-03T14:03:20Z`

Repository imports remaining in auth router: `0`

## Repository imports


## Remaining business-logic extraction debt

- Move register orchestration into AuthApplicationService.register
- Move login orchestration into AuthApplicationService.login
- Move refresh orchestration into AuthApplicationService.refresh
- Move dev-session bootstrap into AuthApplicationService.create_dev_session
- Add HTTP dependency-override integration tests for each auth lifecycle path
