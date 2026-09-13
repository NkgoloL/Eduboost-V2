---
title: "Release — Runtime Integration Rollback Checklist"
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
# Runtime Integration Rollback Checklist

**Status:** required for runtime PRs

## Checklist

- [ ] Revert commit identified
- [ ] No data migration reversal required
- [ ] Feature/helper can be disabled by revert
- [ ] Tests confirm legacy path remains available
- [ ] Incident owner identified
