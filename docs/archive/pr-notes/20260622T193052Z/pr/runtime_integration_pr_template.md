---
title: Runtime Integration PR Template
status: archived-record
owner: documentation-governance
reviewers: [documentation-governance, evidence-custodian, release-management]
audience: evidence-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 180
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/archive, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Runtime Integration PR Template

## Scope

- [ ] One scoped runtime integration target
- [ ] No route registration unless explicitly approved
- [ ] No schema migration
- [ ] No destructive data operation
- [ ] Tests added or updated
- [ ] Rollback path documented

## Evidence

```bash
make backend-runtime-integration-readiness-full-check
pytest -c pytest.ini -q --no-cov
```

## Decision

- [ ] Approved
- [ ] Blocked
- [ ] Requires changes
