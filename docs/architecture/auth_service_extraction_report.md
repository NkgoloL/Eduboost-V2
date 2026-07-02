---
title: "Auth Service Extraction Report"
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

# Auth Service Extraction Report

Generated at: `2026-06-27T02:18:40Z`

Repository imports remaining in auth router: `0`

## Repository imports


## Remaining business-logic extraction debt

- Move register orchestration into AuthApplicationService.register
- Move login orchestration into AuthApplicationService.login
- Move refresh orchestration into AuthApplicationService.refresh
- Move dev-session bootstrap into AuthApplicationService.create_dev_session
- Add HTTP dependency-override integration tests for each auth lifecycle path
