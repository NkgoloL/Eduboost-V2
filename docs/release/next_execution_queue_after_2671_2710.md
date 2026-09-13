---
title: "Release — Next Execution Queue After AUTH-REFRESH-DB-PROOF-001 / code_2671_2710"
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
# Next Execution Queue After AUTH-REFRESH-DB-PROOF-001 / code_2671_2710

## Recommended next action

Attach real auth refresh DB evidence by implementing and running `tests/integration/test_auth_refresh_db_proof.py` against a disposable DB.

## Required release command

```bash
AUTH_REFRESH_DB_PROOF_DSN="postgresql+asyncpg://..." make auth-refresh-db-proof-release-check
```

Do not classify skipped DB tests as proof.
