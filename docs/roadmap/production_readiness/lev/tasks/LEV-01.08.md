# LEV-01.08 — Implementation Task Card

**Workstream:** LEV-WS01 — Define mastery claims precisely  
**Phase:** LEV-0  
**Priority:** P0  
**Status:** `not_started`  
**Implementation type:** `governance_and_documentation`  
**Estimated effort:** S/M  
**Human dependency:** No  
**Cannot be completed by code alone:** No

## Required outcome

Define prohibited uses, including high-stakes progression, formal marks, permanent labels and unsupported population extrapolation.

## Definition-of-done link

Mastery claims are precisely defined.

## Dependencies

- `LEV-01.07`

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
- `docs/research/longitudinal_validation/evidence/01.08_prohibited_use_register_approved_and_enforced_in_product_requirements.md`

## Implementation procedure

1. Read the LEV-WS01 workstream specification and confirm prerequisites for task 01.08.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Define prohibited uses, including high-stakes progression, formal marks, permanent labels and unsupported population extrapolation.
4. Circulate the draft to accountable and consulted roles.
5. Resolve comments and obtain the required versioned approval.
6. Attach or link the required evidence: Prohibited-use register approved and enforced in product requirements.
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

- [ ] Prohibited-use register approved and enforced in product requirements.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Prohibited-use register approved and enforced in product requirements.

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
