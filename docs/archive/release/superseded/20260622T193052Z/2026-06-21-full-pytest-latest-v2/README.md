---
title: Superseded Full Pytest Artifact
status: archived-record
owner: documentation-governance
reviewers: [documentation-governance, evidence-custodian, release-management]
audience: evidence-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 180
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/archive, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Superseded Full Pytest Artifact

`full_pytest_latest_v2.txt` is a stale failed-suite artifact retained for
history only. It records an old run with `19 failed, 1728 passed, 29 skipped`
and must not be used as current release evidence, Gate 2R.1 closure evidence,
or production-readiness proof.

Current Gate 2R.1 status remains:

- Gate 2R.1 is in progress.
- Gate 2R.1 closure is not established.
- Gate 2R.2 is blocked.

Any future full-suite evidence must be regenerated from a clean committed
worktree and stored with its source commit, evidence commit, command, runtime
environment, and checksum index.
