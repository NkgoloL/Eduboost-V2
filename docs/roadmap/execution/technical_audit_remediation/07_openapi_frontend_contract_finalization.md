---
title: TA Phase 07 — OpenAPI / Frontend Contract Finalization
status: active-control
owner: roadmap-governance
reviewers: [roadmap-governance, release-management, documentation-governance]
audience: roadmap-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 30
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/roadmap, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# TA Phase 07 — OpenAPI / Frontend Contract Finalization

**Status:** implementation ready  
**Stream:** technical-audit-remediation  
**Authority scope:** regenerated backend OpenAPI contract plus frontend client route-contract verification.

## Purpose

Phase 07 closes the OpenAPI/frontend-contract blocker after the backend-fast, frontend-tooling, CI, dependency-scan, and Playwright authority gates have been stabilized.

The goal is to prove that:

1. `docs/openapi.json` is regenerated from the active FastAPI runtime.
2. the committed OpenAPI document is current according to `scripts/generate_openapi.py --check`.
3. canonical POPIA and parent data-rights routes remain present under both `/api/v2` and `/v2` prefixes.
4. frontend API service calls use canonical backend route fragments, not retired POPIA alias paths.
5. parent export links emitted by the backend use canonical POPIA export URLs.
6. evidence is recorded as a stable machine-readable bundle with SHA-256 integrity checks.

## Authority commands

```bash
PYTHON_BIN=.venv/bin/python bash scripts/audit_remediation/finalize_openapi_frontend_contract.sh --regenerate
python3 scripts/audit_remediation/verify_openapi_frontend_contract.py --json
bash scripts/audit_remediation/collect_openapi_frontend_contract_evidence.sh
python3 scripts/audit_remediation/verify_openapi_frontend_contract_evidence.py --evidence-dir docs/release-evidence/technical-audit/openapi-frontend-contract --json
```

## Boundary

This phase does **not** claim:

- product release readiness;
- remote GitHub Actions success;
- full backend-backed E2E readiness;
- dependency vulnerability absence;
- runtime knowledge-graph implementation.

The KG/knowledge-graph pivot remains a future architectural north star. This phase only preserves clean route-contract and provenance hooks for future work.

## Closure criteria

Phase 07 can be closed when:

- `docs/openapi.json` has been regenerated or confirmed current from the active runtime;
- the frontend contract verifier returns `valid: true`;
- evidence verifier returns `valid: true`;
- `TA-OPENAPI-001` is updated to `evidence_recorded` in the blocker register with the evidence commit recorded.
