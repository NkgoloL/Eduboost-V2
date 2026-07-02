---
title: "JWT Rotation Introspection"
status: current-evidence
owner: security
reviewers: [security, engineering, privacy]
audience: security-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-02
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/security/README.md, app/security]
---

# JWT Rotation Introspection

Generated at: `2026-06-27T02:19:45Z`

| Check | Value |
|---|---|
| security.py exists | True |
| auth.py exists | True |
| jwt.encode count in security.py | 2 |
| jwt.decode count in security.py | 0 |
| jwt keyring imported in security.py | True |
| kid header references | 3 |
| decode keyring references | 2 |
