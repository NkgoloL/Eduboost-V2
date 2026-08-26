---
title: "JWT Rotation Introspection"
status: "active"
owner: "engineering"
reviewers: ["engineering"]
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-08-26"
review_interval_days: 60
evidence_command: "make docs-housekeeping-check"
code_anchors: ["docs/security/jwt_rotation_introspection.md"]
---

# JWT Rotation Introspection

Generated at: `2026-08-03T14:19:38Z`

| Check | Value |
|---|---|
| security.py exists | True |
| auth.py exists | True |
| jwt.encode count in security.py | 2 |
| jwt.decode count in security.py | 0 |
| jwt keyring imported in security.py | True |
| kid header references | 3 |
| decode keyring references | 2 |
