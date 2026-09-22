# LEV-06.09 — Implementation Task Card

**Workstream:** LEV-WS06 — Demonstrate delayed-retention validity  
**Phase:** LEV-3  
**Priority:** P1  
**Status:** `not_started`  
**Implementation type:** `human_governance_or_research`  
**Estimated effort:** L/XL; elapsed time may be term- or cohort-bound  
**Human dependency:** Yes  
**Cannot be completed by code alone:** Yes

## Required outcome

Test whether assisted success and repeated exposure produce weaker retention than independent success.

## Definition-of-done link

Estimates predict delayed retention.

## Dependencies

- `LEV-06.08`

## Existing repository files to inspect or modify

- `app/modules/progress/mastery_model.py`
- `app/services/runtime_kg/service.py`
- `app/modules/study_plans/runtime_kg_planner.py`
- `app/services/study_plan_service_v2.py`
- `docs/learning_science/mastery_model.md`

## Planned or new files

- `app/services/educational_validation/retention.py`
- `scripts/educational_validation/run_retention_analysis.py`
- `docs/research/longitudinal_validation/evidence/06.09_assistance_and_exposure_analysis.md`

## Implementation procedure

1. Read the LEV-WS06 workstream specification and confirm prerequisites for task 06.09.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Test whether assisted success and repeated exposure produce weaker retention than independent success.
4. Confirm lawful authority, consent/assent, independence and conflict-of-interest controls before participant or reviewer activity.
5. Record attendance, decisions, dissent, requested corrections and signed approval or rejection.
6. Attach or link the required evidence: Assistance and exposure analysis.
7. Mark complete only after the acceptance criterion is independently verifiable.

## Verification commands

```bash
python scripts/educational_validation/verify_lev_task_register.py --repo-root . --json
```
```bash
python scripts/educational_validation/lev_task_cli.py show <TASK_ID>
```
```bash
pytest -q tests/unit/test_study_plan_service_v2.py tests/unit/runtime_kg
```

## Acceptance criteria

- [ ] Assistance and exposure analysis.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Assistance and exposure analysis.

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
