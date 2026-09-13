---
title: "Operations — CI/CD And Staging Evidence"
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
# CI/CD And Staging Evidence

This index links workflow, Docker, environment, secret, deployment, and staging
smoke evidence.

Run:

```bash
make cicd-staging-check
```

Verification gaps: branch protection, actual staging deployment, image digest,
and live staging smoke output.
