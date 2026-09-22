# LEV-02.13 — Implementation Task Card

**Workstream:** LEV-WS02 — Independently review CAPS concepts and assessment items  
**Phase:** LEV-2  
**Priority:** P1  
**Status:** `not_started`  
**Implementation type:** `engineering`  
**Estimated effort:** M/L  
**Human dependency:** No  
**Cannot be completed by code alone:** No

## Required outcome

Build parallel forms, common anchor sets and controlled exposure schedules for baseline, term, retention and transfer assessments.

## Definition-of-done link

CAPS concepts and items are independently reviewed.

## Dependencies

- `LEV-02.12`

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
- `docs/research/longitudinal_validation/evidence/02.13_form_equating_plan_and_secure_form_manifests.md`

## Implementation procedure

1. Read the LEV-WS02 workstream specification and confirm prerequisites for task 02.13.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Build parallel forms, common anchor sets and controlled exposure schedules for baseline, term, retention and transfer assessments.
4. Add or update unit, integration and contract tests for the changed behaviour.
5. Run focused checks, then the LEV register verifier and applicable repository quality gates.
6. Attach or link the required evidence: Form-equating plan and secure form manifests.
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

- [ ] Form-equating plan and secure form manifests.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Form-equating plan and secure form manifests.

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
