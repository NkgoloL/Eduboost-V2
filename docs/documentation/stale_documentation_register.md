---
title: Stale Documentation Register
status: active
owner: documentation-governance
reviewers: [engineering, release-management]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-22
review_interval_days: 30
evidence_command: python3 scripts/maintenance/audit_documentation_inventory.py --root . --out-json docs/generated/documentation_inventory.json --out-csv docs/generated/documentation_inventory.csv --out-findings docs/generated/documentation_findings.csv
code_anchors: [docs/generated/documentation_findings.csv]
---

# Stale Documentation Register

This register is the human triage companion to the generated documentation inventory.

The housekeeping script writes migration manifests under `docs/documentation/migration_manifests/`. The documentation inventory writes findings under `docs/generated/documentation_findings.csv`.

## Triage statuses

| Status | Meaning |
|---|---|
| keep_current | Document is current and should receive metadata if missing. |
| rewrite | Document should remain active but needs truth alignment. |
| merge | Document duplicates a canonical document and should be merged. |
| archive | Document is historical/superseded and should move to archive. |
| generated | Document should be regenerated, not hand-edited. |
| evidence | Document is evidence and should be linked from a summary. |

## Initial known areas

| Area | Initial action |
|---|---|
| `docs/DOC/` | Archive as legacy formal pack unless regenerated from canonical docs. |
| `docs/release/superseded/` | Archive under release history. |
| `docs/api/build/`, `docs/api/_build/` | Move generated HTML under generated output. |
| `docs/todos/` | Archive or merge into active roadmap/backlog. |
| `docs/patches/` | Archive patch notes after applied. |
| `docs/generated/` | Keep, but treat as generated and reproducible. |
| `docs/release-evidence/` | Keep stable while Phase 02R gate automation expects this path. |
