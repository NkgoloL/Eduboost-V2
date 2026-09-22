# LEV-05.06 — Implementation Task Card

**Workstream:** LEV-WS05 — Quantify false-mastery and false-non-mastery risk  
**Phase:** LEV-2  
**Priority:** P1  
**Status:** `not_started`  
**Implementation type:** `analysis_and_validation`  
**Estimated effort:** M/L after data readiness  
**Human dependency:** No  
**Cannot be completed by code alone:** Yes

## Required outcome

Estimate error by concept, difficulty, evidence count, hint use, response latency and time since learning.

## Definition-of-done link

False-mastery and false-non-mastery rates are understood.

## Dependencies

- `LEV-05.05`

## Existing repository files to inspect or modify

- `app/modules/progress/mastery_model.py`
- `app/modules/diagnostics/irt_engine.py`
- `app/services/runtime_kg/schemas.py`
- `docs/diagnostics/mastery_model_assessment_contract.md`

## Planned or new files

- `app/services/educational_validation/classification.py`
- `scripts/educational_validation/run_classification_analysis.py`
- `docs/research/longitudinal_validation/evidence/05.06_error_source_analysis.md`

## Implementation procedure

1. Read the LEV-WS05 workstream specification and confirm prerequisites for task 05.06.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Estimate error by concept, difficulty, evidence count, hint use, response latency and time since learning.
4. Freeze the analysis input manifest before examining outcome results.
5. Execute the pre-specified analysis with reproducible code and retain diagnostics, uncertainty and sensitivity outputs.
6. Attach or link the required evidence: Error-source analysis.
7. Mark complete only after the acceptance criterion is independently verifiable.

## Verification commands

```bash
python scripts/educational_validation/verify_lev_task_register.py --repo-root . --json
```
```bash
python scripts/educational_validation/lev_task_cli.py show <TASK_ID>
```
```bash
pytest -q tests/unit/modules/progress/test_mastery_model.py
```

## Acceptance criteria

- [ ] Error-source analysis.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Error-source analysis.

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
