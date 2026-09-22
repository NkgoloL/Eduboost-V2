# LEV-02.15 — Implementation Task Card

**Workstream:** LEV-WS02 — Independently review CAPS concepts and assessment items  
**Phase:** LEV-2  
**Priority:** P1  
**Status:** `not_started`  
**Implementation type:** `human_governance_or_research`  
**Estimated effort:** L/XL; elapsed time may be term- or cohort-bound  
**Human dependency:** Yes  
**Cannot be completed by code alone:** Yes

## Required outcome

Obtain independent sign-off that the validation bank adequately represents the intended claims.

## Definition-of-done link

CAPS concepts and items are independently reviewed.

## Dependencies

- `LEV-02.14`

## Existing repository files to inspect or modify

- `app/modules/diagnostics/item_bank_pipeline.py`
- `app/modules/diagnostics/item_bank_service.py`
- `app/repositories/item_bank_repository.py`
- `app/services/curriculum/claim_validation.py`
- `docs/architecture/diagnostic_item_bank_canonicality.yml`
- `docs/diagnostics/assessment_quality_fairness_contract.md`
- `scripts/curriculum/build_launch_item_bank.py`
- `scripts/validate_item_bank.py`

## Planned or new files

- `docs/research/longitudinal_validation/caps_validation_blueprint.csv`
- `docs/research/longitudinal_validation/validation_item_bank_manifest.json`
- `docs/research/longitudinal_validation/evidence/02.15_signed_curriculum_and_psychometric_approval.md`

## Implementation procedure

1. Read the LEV-WS02 workstream specification and confirm prerequisites for task 02.15.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Obtain independent sign-off that the validation bank adequately represents the intended claims.
4. Confirm lawful authority, consent/assent, independence and conflict-of-interest controls before participant or reviewer activity.
5. Record attendance, decisions, dissent, requested corrections and signed approval or rejection.
6. Attach or link the required evidence: Signed curriculum and psychometric approval.
7. Mark complete only after the acceptance criterion is independently verifiable.

## Verification commands

```bash
python scripts/educational_validation/verify_lev_task_register.py --repo-root . --json
```
```bash
python scripts/educational_validation/lev_task_cli.py show <TASK_ID>
```
```bash
pytest -q tests/unit/modules/diagnostics tests/unit/test_diagnostic_item_bank_canonicality.py
```
```bash
python scripts/validate_item_bank.py
```

## Acceptance criteria

- [ ] Signed curriculum and psychometric approval.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Signed curriculum and psychometric approval.

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
