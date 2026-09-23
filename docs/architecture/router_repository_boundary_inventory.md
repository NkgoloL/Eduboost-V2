---
title: "Router Repository Boundary Inventory"
status: current-evidence
owner: architecture
reviewers: [architecture, engineering]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-09-23
review_interval_days: 60
evidence_command: "PYTHONPATH=. python3 scripts/run_import_linter_contracts.py"
code_anchors: [".importlinter", "app/api_v2_routers/", "scripts/run_import_linter_contracts.py"]
---

# Router Repository Boundary Inventory

This document tracks the repository boundaries accessed by application routers, ensuring that dependency injection is used correctly and that routers do not bypass service layer validation.

## Status
- Initial inventory created for documentation intelligence check.
- Further details will be populated in upcoming execution batches.
