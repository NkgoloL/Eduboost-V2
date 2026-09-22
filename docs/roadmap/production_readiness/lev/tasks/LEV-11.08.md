# LEV-11.08 — Implementation Task Card

**Workstream:** LEV-WS11 — Measure and control adverse educational effects  
**Phase:** LEV-3  
**Priority:** P1  
**Status:** `not_started`  
**Implementation type:** `human_governance_or_research`  
**Estimated effort:** L/XL; elapsed time may be term- or cohort-bound  
**Human dependency:** Yes  
**Cannot be completed by code alone:** Yes

## Required outcome

Analyse adverse indicators by learner context and model error type.

## Definition-of-done link

Adverse effects are measured and acceptably controlled.

## Dependencies

- `LEV-11.07`

## Existing repository files to inspect or modify

- `app/services/runtime_kg/feature_flags.py`
- `app/services/consent_service.py`
- `app/services/audit_service.py`
- `app/api_v2_routers/audit.py`
- `docs/operations`
- `docs/compliance`

## Planned or new files

- `app/services/educational_validation/safety.py`
- `docs/research/longitudinal_validation/adverse_consequence_monitoring_plan.md`
- `docs/research/longitudinal_validation/evidence/11.08_differential_consequence_report.md`

## Implementation procedure

1. Read the LEV-WS11 workstream specification and confirm prerequisites for task 11.08.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Analyse adverse indicators by learner context and model error type.
4. Confirm lawful authority, consent/assent, independence and conflict-of-interest controls before participant or reviewer activity.
5. Record attendance, decisions, dissent, requested corrections and signed approval or rejection.
6. Attach or link the required evidence: Differential consequence report.
7. Mark complete only after the acceptance criterion is independently verifiable.

## Verification commands

```bash
python scripts/educational_validation/verify_lev_task_register.py --repo-root . --json
```
```bash
python scripts/educational_validation/lev_task_cli.py show <TASK_ID>
```
```bash
pytest -q tests/popia tests/unit/runtime_kg
```

## Acceptance criteria

- [ ] Differential consequence report.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Differential consequence report.

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
