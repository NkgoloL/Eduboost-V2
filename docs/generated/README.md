---
title: Generated Documentation Inventory and Findings
status: active
owner: documentation-governance
reviewers: [engineering, documentation-governance]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-08-26
review_interval_days: 30
evidence_command: make docs-housekeeping-check
code_anchors: [docs/generated/documentation_inventory.json, docs/generated/documentation_inventory.csv]
---

# Generated Documentation Inventory and Findings

This directory contains deterministic, machine-generated documentation audit manifests, inventories, and findings.

## Artifacts

- `documentation_inventory.json`: Full machine-readable inventory of repository markdown documents.
- `documentation_inventory.csv`: CSV export of documentation inventory.
- `documentation_findings.csv`: CSV export of documentation findings (broken links, metadata discrepancies).

To regenerate these files deterministically, run:
```bash
make docs-housekeeping-refresh
```
