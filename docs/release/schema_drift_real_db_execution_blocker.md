---
title: "Release — Schema Drift Real DB Execution Blocker"
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
# Schema Drift Real DB Execution Blocker

**Status:** blocked until real disposable DB credentials are provided

Schema drift proof is not considered complete until the following passes against a real disposable database:

```bash
make schema-drift-disposable-proof
make schema-drift-disposable-proof-check
make schema-drift-check-db
```

Placeholder credentials and production databases are forbidden.
