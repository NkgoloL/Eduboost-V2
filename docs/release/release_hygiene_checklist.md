---
title: Release Hygiene Checklist
status: release-record
owner: release-management
reviewers: [release-management, evidence-custodian, documentation-governance]
audience: release-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 180
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/release, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Release Hygiene Checklist

Status: pending release-owner review

Before tagging a release candidate, confirm:

- [ ] `git status` has only intended release changes.
- [ ] No secrets or local-only credentials are staged.
- [ ] Generated docs are current or explicitly deferred.
- [ ] `TODO.md` statuses match readable evidence files.
- [ ] CI evidence links point to the current commit.
- [ ] Migration evidence includes upgrade output and rollback policy.
- [ ] Staging smoke evidence uses a real non-placeholder HTTPS URL.
- [ ] Known issues and beta limitations are non-empty.
- [ ] POPIA/legal/security approvals are linked or marked pending.
- [ ] Release bundle links resolve.

## Completion Rule

Every checked box needs a command, reviewer, or artifact reference.