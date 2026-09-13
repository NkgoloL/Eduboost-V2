---
title: "Branch/release naming reconciliation schema"
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
# Branch/release naming reconciliation schema

The generated inventory file is:

```text
docs/roadmap/production_readiness/branch_release_naming_reconciliation.json
```

Required top-level fields:

| Field | Description |
|---|---|
| `schema_version` | Must be `prd-branch-release-naming-reconciliation/v1`. |
| `prd_id` | Must be `PRD-0.8`. |
| `canonical_trunk_branch` | Must be `master`. |
| `legacy_main_alias_policy` | Explains how remaining `main` references are interpreted. |
| `release_branch_pattern` | Reserved release branch pattern, currently `release/**`. |
| `workflow_count` | Number of workflow YAML files inspected. |
| `workflow_branch_reference_summary` | Counts of workflow files referencing `master`, `main`, and `release/**`. |
| `release_event_workflows` | Workflow files that contain a release event trigger or release-specific commands. |
| `deployment_reference_workflows` | Workflow files containing deployment/promotion references. |
| `authority_boundaries` | Explicit production/beta/billing/deployment boundary flags. |
```
