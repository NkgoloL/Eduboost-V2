# LEV-07.07 — Implementation Task Card

**Workstream:** LEV-WS07 — Demonstrate transfer validity  
**Phase:** LEV-3  
**Priority:** P1  
**Status:** `not_started`  
**Implementation type:** `analysis_and_validation`  
**Estimated effort:** M/L after data readiness  
**Human dependency:** No  
**Cannot be completed by code alone:** Yes

## Required outcome

Estimate the relationship between concept mastery and near-transfer performance.

## Definition-of-done link

Estimates predict transfer to unfamiliar tasks.

## Dependencies

- `LEV-07.06`

## Existing repository files to inspect or modify

- `app/services/runtime_kg/service.py`
- `app/services/runtime_kg/schemas.py`
- `app/modules/lessons/adaptive_remediation.py`
- `app/modules/study_plans/runtime_kg_planner.py`
- `app/services/content_blueprint_validation.py`

## Planned or new files

- `app/services/educational_validation/transfer.py`
- `scripts/educational_validation/run_transfer_analysis.py`
- `docs/research/longitudinal_validation/evidence/07.07_near_transfer_validity_report.md`

## Implementation procedure

1. Read the LEV-WS07 workstream specification and confirm prerequisites for task 07.07.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Estimate the relationship between concept mastery and near-transfer performance.
4. Freeze the analysis input manifest before examining outcome results.
5. Execute the pre-specified analysis with reproducible code and retain diagnostics, uncertainty and sensitivity outputs.
6. Attach or link the required evidence: Near-transfer validity report.
7. Mark complete only after the acceptance criterion is independently verifiable.

## Verification commands

```bash
python scripts/educational_validation/verify_lev_task_register.py --repo-root . --json
```
```bash
python scripts/educational_validation/lev_task_cli.py show <TASK_ID>
```
```bash
pytest -q tests/unit/runtime_kg tests/unit/test_lesson_service_v2.py
```

## Acceptance criteria

- [ ] Near-transfer validity report.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Near-transfer validity report.

## Execution record

- **Owner:** Unassigned
- **Reviewer:** Unassigned
- **Started:** —
- **Candidate complete:** —
- **Closed:** —
- **Commit(s):** —
- **PR(s):** —
- **Study/data manifest:** —
- **Decision:** —
- **Blockers:** —
- **Notes:** —
