---
title: Backend Runtime Wiring PR Template
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

# Backend Runtime Wiring PR Template

## Scope

- [ ] Exactly one low-risk audit/consent call path wired
- [ ] Adapter-backed canonical payload used
- [ ] No repository deletion
- [ ] No consent table merge
- [ ] No Alembic stamp/baseline
- [ ] No public health write probe

## Evidence

```bash
make backend-runtime-enablement-full-check
pytest -c pytest.ini -q --no-cov
```

## Decision

- [ ] Approved for merge
- [ ] Blocked
