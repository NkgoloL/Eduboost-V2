---
title: "Release — Runtime Integration Test Evidence Template"
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
# Runtime Integration Test Evidence Template

**Status:** pending per runtime PR

## Required output

```bash
make backend-runtime-integration-readiness-full-check
pytest -c pytest.ini -q --no-cov
```

## Evidence fields

- Commit SHA: TODO
- Branch: TODO
- Test command: TODO
- Result: TODO
- Skips/warnings: TODO
