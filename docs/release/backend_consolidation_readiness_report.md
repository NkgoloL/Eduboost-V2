# Backend Consolidation Readiness Report

Generated at: `2026-05-19T23:00:08Z`

| Check | Return code | Command |
|---|---:|---|
| backend consolidation report | 0 | `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/generate_backend_consolidation_report.py` |
| runtime compatibility report | 0 | `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/generate_backend_runtime_compatibility_report.py` |
| deletion candidate inventory | 0 | `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/generate_backend_deletion_candidate_inventory.py --fail-empty` |
| no-op guard | 0 | `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/check_backend_consolidation_noop_guard.py` |

## Boundary

This report does not approve deletion, table merging, Alembic stamping, or runtime rewiring.

## backend consolidation report

Command: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/generate_backend_consolidation_report.py`

Return code: `0`

```text
Wrote /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/docs/release/backend_consolidation_diagnostic_report.md
```

## runtime compatibility report

Command: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/generate_backend_runtime_compatibility_report.py`

Return code: `0`

```text
Wrote /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/docs/release/backend_runtime_compatibility_report.md
```

## deletion candidate inventory

Command: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/generate_backend_deletion_candidate_inventory.py --fail-empty`

Return code: `0`

```text
Wrote /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/docs/release/backend_deletion_candidate_inventory.md (248610 candidate row(s))
```

## no-op guard

Command: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/check_backend_consolidation_noop_guard.py`

Return code: `0`

```text
Backend consolidation no-op/deletion guard
- PASS [file] docs/release/backend_consolidation_readiness_matrix.md: present
- PASS [file] docs/release/backend_data_retention_decision_checklist.md: present
- PASS [file] docs/release/backend_consolidation_decision_record.md: present
- PASS [file] docs/release/backend_deletion_candidate_inventory.md: present
- PASS [decision] implementation decisions remain pending
- PASS [retention] default retention/destructive-decision safeguards present
- PASS [phrase] docs/release/backend_consolidation_decision_record.md: no forbidden approval phrase detected
- PASS [phrase] docs/release/backend_data_retention_decision_checklist.md: no forbidden approval phrase detected
- PASS [phrase] docs/release/backend_deletion_candidate_inventory.md: no forbidden approval phrase detected
- PASS [inventory] candidates default to not approved
- PASS backend consolidation no-op/deletion guard
```
