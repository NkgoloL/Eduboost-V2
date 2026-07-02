---
title: "Auth Service Extraction Follow-up"
status: active
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

# Auth Service Extraction Follow-up

Generated at: `2026-05-22T14:25:43Z`

## Remaining repository imports


## Next steps

- Move remaining auth repository interactions into canonical AuthService
- Remove auth router repository imports
- Remove auth import-linter ignore_imports entries
- Add integration tests for register/login/refresh against canonical AuthService
