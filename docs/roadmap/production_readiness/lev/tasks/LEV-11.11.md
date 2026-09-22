# LEV-11.11 — Implementation Task Card

**Workstream:** LEV-WS11 — Measure and control adverse educational effects  
**Phase:** LEV-3  
**Priority:** P1  
**Status:** `not_started`  
**Implementation type:** `engineering`  
**Estimated effort:** M/L  
**Human dependency:** No  
**Cannot be completed by code alone:** Yes

## Required outcome

Implement automated freeze, rollback or authority-reduction behaviour for breached harm thresholds.

## Definition-of-done link

Adverse effects are measured and acceptably controlled.

## Dependencies

- `LEV-11.10`

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
- `docs/research/longitudinal_validation/evidence/11.11_safety_automation_rehearsal.md`

## Implementation procedure

1. Read the LEV-WS11 workstream specification and confirm prerequisites for task 11.11.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Implement automated freeze, rollback or authority-reduction behaviour for breached harm thresholds.
4. Add or update unit, integration and contract tests for the changed behaviour.
5. Run focused checks, then the LEV register verifier and applicable repository quality gates.
6. Attach or link the required evidence: Safety automation rehearsal.
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

- [ ] Safety automation rehearsal.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Safety automation rehearsal.

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
