---
title: "Operations — External Evidence Checklist"
status: "active"
owner: "operations"
reviewers: ['operations', 'sre', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
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
