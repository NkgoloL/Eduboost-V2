# LEV-01.03 — Implementation Task Card

**Workstream:** LEV-WS01 — Define mastery claims precisely  
**Phase:** LEV-0  
**Priority:** P0  
**Status:** `not_started`  
**Implementation type:** `human_governance_or_research`  
**Estimated effort:** L/XL; elapsed time may be term- or cohort-bound  
**Human dependency:** Yes  
**Cannot be completed by code alone:** Yes

## Required outcome

Separate the constructs of next-response probability, current independent proficiency, provisional mastery, durable mastery, retention and transfer.

## Definition-of-done link

Mastery claims are precisely defined.

## Dependencies

- `LEV-01.02`

## Existing repository files to inspect or modify

- `app/modules/progress/mastery_model.py`
- `app/services/runtime_kg/schemas.py`
- `app/services/runtime_kg/feature_flags.py`
- `app/services/runtime_kg/acceptance.py`
- `app/repositories/mastery_repository.py`
- `docs/learning_science/mastery_model.md`
- `docs/diagnostics/mastery_model_assessment_contract.md`
- `docs/research/mastery_model/rr013_mastery_model_research_policy.md`

## Planned or new files

- `docs/research/longitudinal_validation/mastery_interpretation_and_use_specification.md`
- `app/domain/educational_validation_schemas.py`
- `docs/research/longitudinal_validation/evidence/01.03_construct_taxonomy_approved_by_the_educational_measurement_lead.md`

## Implementation procedure

1. Read the LEV-WS01 workstream specification and confirm prerequisites for task 01.03.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Separate the constructs of next-response probability, current independent proficiency, provisional mastery, durable mastery, retention and transfer.
4. Confirm lawful authority, consent/assent, independence and conflict-of-interest controls before participant or reviewer activity.
5. Record attendance, decisions, dissent, requested corrections and signed approval or rejection.
6. Attach or link the required evidence: Construct taxonomy approved by the educational measurement lead.
7. Mark complete only after the acceptance criterion is independently verifiable.

## Verification commands

```bash
python scripts/educational_validation/verify_lev_task_register.py --repo-root . --json
```
```bash
python scripts/educational_validation/lev_task_cli.py show <TASK_ID>
```
```bash
pytest -q tests/unit/modules/progress/test_mastery_model.py tests/unit/runtime_kg
```

## Acceptance criteria

- [ ] Construct taxonomy approved by the educational measurement lead.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Construct taxonomy approved by the educational measurement lead.

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
