---
title: Combined Runtime Wiring PR Checklist
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

# Combined Runtime Wiring PR Checklist

## Scope

- [ ] Exactly one consent runtime candidate
- [ ] Read-only deep-readiness plan only
- [ ] No consent table merge
- [ ] No route registration change unless separately approved
- [ ] No DB write from public health/readiness
- [ ] No Alembic stamp/baseline
- [ ] Full tests pass

## Verification

```bash
make backend-implementation-431-450-full-check
pytest -c pytest.ini -q --no-cov
```
