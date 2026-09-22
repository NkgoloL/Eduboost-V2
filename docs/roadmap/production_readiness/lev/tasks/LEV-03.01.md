# LEV-03.01 — Implementation Task Card

**Workstream:** LEV-WS03 — Make learner evidence and state changes fully traceable  
**Phase:** LEV-1  
**Priority:** P0  
**Status:** `not_started`  
**Implementation type:** `human_governance_or_research`  
**Estimated effort:** L/XL; elapsed time may be term- or cohort-bound  
**Human dependency:** Yes  
**Cannot be completed by code alone:** Yes

## Required outcome

Specify the canonical learner-interaction event schema, including item, concept, content, assistance, timing, language, device and consent context.

## Definition-of-done link

Learner evidence and state changes are fully traceable.

## Dependencies

- `LEV-01.10`
- `LEV-01.14`

## Existing repository files to inspect or modify

- `app/models/runtime_kg.py`
- `app/services/runtime_kg/repository.py`
- `app/services/runtime_kg/service.py`
- `app/services/runtime_kg/integration.py`
- `app/repositories/audit_repository.py`
- `app/services/audit_service.py`
- `app/core/audit.py`
- `alembic/versions`

## Planned or new files

- `app/models/educational_validation.py`
- `app/repositories/educational_validation_repository.py`
- `app/services/educational_validation/traceability.py`
- `alembic/versions/<new>_educational_validation_traceability.py`
- `docs/research/longitudinal_validation/evidence/03.01_versioned_schema_and_data_dictionary.md`

## Implementation procedure

1. Read the LEV-WS03 workstream specification and confirm prerequisites for task 03.01.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Specify the canonical learner-interaction event schema, including item, concept, content, assistance, timing, language, device and consent context.
4. Confirm lawful authority, consent/assent, independence and conflict-of-interest controls before participant or reviewer activity.
5. Record attendance, decisions, dissent, requested corrections and signed approval or rejection.
6. Attach or link the required evidence: Versioned schema and data dictionary.
7. Mark complete only after the acceptance criterion is independently verifiable.

## Verification commands

```bash
python scripts/educational_validation/verify_lev_task_register.py --repo-root . --json
```
```bash
python scripts/educational_validation/lev_task_cli.py show <TASK_ID>
```
```bash
pytest -q tests/unit/runtime_kg tests/integration/test_audit_immutability.py
```

## Acceptance criteria

- [ ] Versioned schema and data dictionary.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Versioned schema and data dictionary.

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
