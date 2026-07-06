---
title: First Audit Runtime Wiring PR Checklist
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

# First Audit Runtime Wiring PR Checklist

## Scope

- [ ] Exactly one audit candidate wired
- [ ] Candidate uses `AuditRepositoryCompatAdapter`
- [ ] In-memory/non-DB tests pass
- [ ] No repository deletion
- [ ] No consent table merge
- [ ] No schema migration
- [ ] No route registration change
- [ ] No production database mutation

## Verification

```bash
make backend-implementation-421-430-full-check
pytest -c pytest.ini -q --no-cov
```

## Release owner decision

- [ ] Approved
- [ ] Blocked
- [ ] Requires changes
