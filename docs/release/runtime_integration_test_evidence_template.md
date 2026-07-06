---
title: Runtime Integration Test Evidence Template
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
