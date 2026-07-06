---
title: Rollback Drill Evidence
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

# Rollback Drill Evidence

**Status:** pending runtime execution
<!-- Status: pending runtime execution -->

This file is the stable release gate for application rollback drill evidence. It must remain pending until a real rollback drill is accepted by the release owner.

Latest raw rollback output, when available:

- JSON: `docs/release/rollback_latest.json`
- Markdown: `docs/release/rollback_latest.md`

## Required environment

| Field | Value |
|---|---|
| Current version deployed | TODO |
| Rollback target version | TODO |
| Deployment mechanism | TODO |
| Commit SHA (target) | TODO |
| Operator | TODO |
| Timestamp UTC | TODO |

## Required checks

| Check | Expected result | Evidence |
|---|---|---|
| Application rollback command | succeeds without errors | TODO |
| Post-rollback health | all health endpoints respond correctly | TODO |
| Database state consistency | matches expected rollback target | TODO |
| Service connectivity restored | dependent services reachable | TODO |
| User traffic rerouted | requests succeed at previous version | TODO |

## Command log

```bash
# paste accepted rollback evidence commands and output here
```

## Decision

- [ ] Rollback drill passed and is accepted for release evidence.
- [ ] Rollback drill failed and release is blocked.
