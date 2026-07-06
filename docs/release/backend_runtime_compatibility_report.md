---
title: Backend Runtime Compatibility Report
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

# Backend Runtime Compatibility Report

Generated at: `2026-06-27T02:21:34Z`

| Check | Return code | Command |
|---|---:|---|
| runtime compatibility | 0 | `/home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python scripts/check_backend_runtime_compatibility.py` |
| audit compatibility | 0 | `/home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python scripts/generate_audit_callsite_inventory.py --fail-empty` |
| consent compatibility | 0 | `/home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python scripts/generate_consent_callsite_inventory.py --fail-empty` |
| health readiness | 0 | `/home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python scripts/check_health_readiness_contract.py` |

## Boundary

This report proves compatibility surfaces exist. It does not approve deletion, table merging, or runtime rewiring.

## runtime compatibility

Command: `/home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python scripts/check_backend_runtime_compatibility.py`

Return code: `0`

```text
Audit runtime compatibility surface
- PASS [audit compat] AuditRepositoryCompatAdapter: present
- PASS [audit compat] AuditEventInput: present
- PASS [audit compat] normalize_audit_kwargs: present
- PASS [audit repository] exposes record/append/create-compatible method
Consent runtime compatibility surface
- PASS [consent compat] ConsentAuditEvent: present
- PASS [consent compat] normalize_consent_audit_event: present
- PASS [consent compat] classify_consent_action: present
- PASS [consent import] app.services.consent_service: importable
- PASS [consent import] app.modules.consent.service: importable
- PASS [consent import] app.services.popia_service: importable
Deep-health compatibility surface
- PASS [health contract] contains 'database connectivity'
- PASS [health contract] contains 'Alembic current revision'
- PASS [health contract] contains 'required core table presence'
- PASS backend runtime compatibility surface
```

## audit compatibility

Command: `/home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python scripts/generate_audit_callsite_inventory.py --fail-empty`

Return code: `0`

```text
Wrote /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/docs/release/audit_callsite_inventory.md (3966 row(s))
```

## consent compatibility

Command: `/home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python scripts/generate_consent_callsite_inventory.py --fail-empty`

Return code: `0`

```text
Wrote /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/docs/release/consent_callsite_inventory.md (600 row(s))
```

## health readiness

Command: `/home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python scripts/check_health_readiness_contract.py`

Return code: `0`

```text
Health/readiness diagnostic contract check
- PASS [file] docs/release/health_readiness_diagnostic_contract.md: present
- PASS [content] docs/release/health_readiness_diagnostic_contract.md: contains 'Lightweight health'
- PASS [content] docs/release/health_readiness_diagnostic_contract.md: contains 'Deep health'
- PASS [content] docs/release/health_readiness_diagnostic_contract.md: contains 'database connectivity'
- PASS [content] docs/release/health_readiness_diagnostic_contract.md: contains 'Alembic current revision'
- PASS [content] docs/release/health_readiness_diagnostic_contract.md: contains 'required core table presence'
- PASS [content] docs/release/health_readiness_diagnostic_contract.md: contains 'no unsafe public write operations'
- PASS [file] docs/release/schema_drift_evidence_contract.md: present
- PASS [content] docs/release/schema_drift_evidence_contract.md: contains 'make schema-drift-check'
- PASS [content] docs/release/schema_drift_evidence_contract.md: contains 'make schema-drift-check-db'
- PASS [content] docs/release/schema_drift_evidence_contract.md: contains 'alembic upgrade head'
- PASS [content] docs/release/schema_drift_evidence_contract.md: contains 'alembic stamp head'
- WARN [source] no known health router source found
- PASS health/readiness diagnostics documented
```
