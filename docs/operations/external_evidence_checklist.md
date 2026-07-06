---
title: External Evidence Checklist
status: active
owner: operations
reviewers: [operations, security, release-management]
audience: operator
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 90
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/operations, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# External Evidence Checklist

- [ ] Remote CI green on current fork.
- [ ] Branch protection enabled.
- [ ] POPIA sweep evidence committed.
- [ ] Disposable DB schema proof executed.
- [ ] Staging smoke executed.
- [ ] Backup/restore drill executed.
- [ ] Rollback drill executed.
- [ ] Alertmanager notification test fired.
- [ ] Educator item review threshold satisfied.
- [ ] Release owner go/no-go signed.
