---
title: "Legal — Policy versioning and notification workflow"
status: "active"
owner: "compliance"
reviewers: ['compliance', 'legal', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Policy versioning and notification workflow

Policies use semantic versions: `major.minor.patch`.

- Major: material user-rights or processing change; requires explicit notification and possibly renewed acceptance.
- Minor: clarifies behavior without changing rights; requires publication and notification.
- Patch: typo or formatting correction; publication is sufficient.

## Workflow

1. Draft policy update with changelog.
2. Legal/compliance review.
3. Product verifies policy text matches actual behavior.
4. Publish version and effective date.
5. Notify affected guardians/users.
6. Capture renewed acceptance when required.
7. Preserve historical versions for audit and dispute handling.
