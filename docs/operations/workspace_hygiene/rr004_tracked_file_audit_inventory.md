---
title: "Workspace Hygiene — RR-004 Tracked-File Audit Inventory"
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
# RR-004 Tracked-File Audit Inventory

## Purpose

This document records the tracked-file-only inventory approach required by RR-004.

## Canonical command

```bash
git ls-files
```

The command is tracked-file-only and excludes untracked local scratch files. It provides a stable baseline for audit counts and repository hygiene reviews.

## Scanner command

```bash
python3 scripts/workspace_hygiene/audit_workspace_hygiene.py --json
```

The scanner records:

- `tracked_file_count`
- `tracked_docs_count`
- `tracked_scripts_count`
- `tracked_tests_count`
- `tracked_generated_or_evidence_count`
- `extension_counts`
- `top_level_counts`
- ignored artifact candidate count from `git status --ignored --short`

## Evidence

Captured evidence is written under:

```text
docs/release-evidence/roadmap-reconciliation/rr-004-workspace-hygiene/
```
