---
title: "Backlog — Pr Chore Docs Governance Body"
status: "active"
owner: "product"
reviewers: ['product', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
Title: chore(docs): governance, retention, auth policy, backlog audit

Summary:
- Regenerates `docs/backlog` from TODO.md and integrates artifacts from `temp_1`.
- Adds governance, release checklist, secrets, data retention and subprocessor docs.
- Integrates PR-003 auth/session RBAC artifacts and adds `docs/security/auth_session_policy.md`.
- Adds CODEOWNERS, GitHub templates, Dependabot config, and Makefile targets.

Linked issues:
- Redmine issue: #16 (created by automation; internal tracker)

Changes:
- Files added/updated: docs/repository_governance.md, docs/release_checklist.md, docs/secrets.md, docs/data_retention_policy.md, docs/subprocessor_register.md, docs/security/auth_session_policy.md, docs/backlog/*, .github/*, Makefile, scripts/maintenance/audit_todo_backlog.py

Testing:
- Ran `python3 scripts/maintenance/audit_todo_backlog.py` to regenerate backlog files.
- Local unit tests not fully run in this environment; see CI for full test matrix.

Notes for reviewer:
- This is primarily documentation and governance changes; low risk.
- Please include reviewers from CODEOWNERS (NkgoloL) and verify CI passes before merge.
