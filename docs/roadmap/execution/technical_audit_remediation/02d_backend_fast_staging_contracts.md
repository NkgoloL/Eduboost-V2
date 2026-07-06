---
title: Technical Audit Remediation Phase 02D — Backend Fast Staging and Contract Remediation
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

# Technical Audit Remediation Phase 02D — Backend Fast Staging and Contract Remediation

**Status:** Implementation ready  
**Authority gate:** `make test-fast`  
**Evidence boundary:** This slice may record targeted remediation evidence only. It does not create passing backend-fast evidence unless `make test-fast` exits `0`.

## Scope

This slice targets the highest-yield clusters remaining after the Phase 02C scope-registry expansion:

1. Staging readiness and seed defaults must remain active-scope bounded after the generated registry expanded to 51 scopes.
2. The ETL FastMCP server dependency must be declared in the backend-fast authority dependency set.
3. The auth-refresh DB proof workflow must use the proven `actions/upload-artifact@v4` action.
4. The Content Factory schema contract must declare the ORM tables and enum values that already exist in `app.models.content_factory`.

## Non-scope

- No passing backend-fast gate evidence is created by this implementation.
- No Phase 02R governance is changed.
- No product release-readiness claim is made.
- No live database migration is executed.
- No runtime knowledge-graph implementation is introduced. KG remains a future architectural north star.

## Verification

Run:

```bash
python3 scripts/audit_remediation/verify_backend_fast_phase02d.py --json
python3 -m compileall -q app/services/content_staging_readiness.py scripts/curriculum/seed_staging_review_scopes.py scripts/audit_remediation scripts/ci/content_factory_schema_contract.py
python3 -m pytest -q tests/unit/audit_remediation/test_backend_fast_phase02d.py --no-cov
```

Then run the targeted backend tests in the project `.venv` before retrying the full authority gate.

## Retry policy

After targeted evidence is recorded, rerun:

```bash
bash scripts/audit_remediation/collect_backend_fast_evidence.sh
```

If it fails, preserve diagnostics and continue with the next largest failure cluster.
