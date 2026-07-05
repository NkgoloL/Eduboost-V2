---
title: RR-004 Workspace Hygiene
status: active-control
owner: roadmap-reconciliation
reviewers: [roadmap-reconciliation, release-management, documentation-governance]
audience: roadmap-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-05
review_interval_days: 30
evidence_command: make roadmap-reconciliation-check
code_anchors: [docs/roadmap/reconciliation, scripts/roadmap_reconciliation]
---

# RR-004 Workspace Hygiene

**RR ID:** RR-004  
**Register item:** Workspace hygiene and auditability  
**Status:** authority installed; evidence pending until capture  

## Scope

This slice clears the RR-004 workspace-hygiene controls from the reconciled outstanding-work register:

- safe cleanup target for ignored build/cache artifacts;
- tracked-file-only audit inventory commands;
- reproducible scanner/audit counts;
- evidence capture for the above controls.

## Non-goals

This slice does not delete local artifacts by default, rewrite repository history, authorise production release, authorise deployment, authorise release tagging, authorise public beta, or claim runtime KG implementation.

## Commands

```bash
python3 scripts/workspace_hygiene/audit_workspace_hygiene.py --json
python3 scripts/workspace_hygiene/safe_cleanup_ignored_artifacts.py --dry-run --json
make rr004-workspace-hygiene-audit
make rr004-ignored-artifact-clean-dry-run
```

The cleanup command is dry-run by default. Actual deletion requires both `--execute` and `--confirm-delete-ignored-artifacts`.
