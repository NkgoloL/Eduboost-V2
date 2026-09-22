# LEV-15.04 — Implementation Task Card

**Workstream:** LEV-WS15 — Document unsupported uses and residual limitations  
**Phase:** LEV-0  
**Priority:** P0  
**Status:** `not_started`  
**Implementation type:** `human_governance_or_research`  
**Estimated effort:** L/XL; elapsed time may be term- or cohort-bound  
**Human dependency:** Yes  
**Cannot be completed by code alone:** Yes

## Required outcome

Define mandatory wording for internal documents, API descriptions, dashboards, reports, marketing and school agreements.

## Definition-of-done link

EduBoost clearly documents which uses remain unsupported.

## Dependencies

- `LEV-15.03`

## Existing repository files to inspect or modify

- `app/services/runtime_kg/feature_flags.py`
- `app/services/runtime_kg/schemas.py`
- `docs/learning_science/mastery_model.md`
- `docs/diagnostics/mastery_model_assessment_contract.md`
- `docs/roadmap/production_readiness/production_readiness_register.json`

## Planned or new files

- `docs/research/longitudinal_validation/unsupported_use_register.json`
- `app/services/educational_validation/use_authorization.py`
- `docs/research/longitudinal_validation/evidence/15.04_claims_and_wording_standard.md`

## Implementation procedure

1. Read the LEV-WS15 workstream specification and confirm prerequisites for task 15.04.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Define mandatory wording for internal documents, API descriptions, dashboards, reports, marketing and school agreements.
4. Confirm lawful authority, consent/assent, independence and conflict-of-interest controls before participant or reviewer activity.
5. Record attendance, decisions, dissent, requested corrections and signed approval or rejection.
6. Attach or link the required evidence: Claims and wording standard.
7. Mark complete only after the acceptance criterion is independently verifiable.

## Verification commands

```bash
python scripts/educational_validation/verify_lev_task_register.py --repo-root . --json
```
```bash
python scripts/educational_validation/lev_task_cli.py show <TASK_ID>
```
```bash
pytest -q tests/unit/runtime_kg tests/unit/modules/progress/test_mastery_model.py
```

## Acceptance criteria

- [ ] Claims and wording standard.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Claims and wording standard.

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
