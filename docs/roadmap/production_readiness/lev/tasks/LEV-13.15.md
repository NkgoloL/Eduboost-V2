# LEV-13.15 — Implementation Task Card

**Workstream:** LEV-WS13 — Operate drift detection and revalidation controls  
**Phase:** LEV-6  
**Priority:** P2  
**Status:** `not_started`  
**Implementation type:** `analysis_and_validation`  
**Estimated effort:** M/L after data readiness  
**Human dependency:** No  
**Cannot be completed by code alone:** Yes

## Required outcome

Maintain disaster-recovery procedures for telemetry loss, registry corruption and invalid model deployment.

## Definition-of-done link

Drift and revalidation controls operate in production.

## Dependencies

- `LEV-13.14`

## Existing repository files to inspect or modify

- `app/services/runtime_kg/feature_flags.py`
- `app/services/runtime_kg/acceptance.py`
- `prometheus`
- `grafana`
- `alertmanager`
- `docs/observability`
- `docs/operations`
- `scripts/roadmap_reconciliation`

## Planned or new files

- `app/services/educational_validation/drift.py`
- `scripts/educational_validation/check_educational_model_drift.py`
- `prometheus/rules/educational_validation.yml`
- `docs/research/longitudinal_validation/evidence/13.15_recovery_runbook_and_rehearsal.md`

## Implementation procedure

1. Read the LEV-WS13 workstream specification and confirm prerequisites for task 13.15.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Maintain disaster-recovery procedures for telemetry loss, registry corruption and invalid model deployment.
4. Freeze the analysis input manifest before examining outcome results.
5. Execute the pre-specified analysis with reproducible code and retain diagnostics, uncertainty and sensitivity outputs.
6. Attach or link the required evidence: Recovery runbook and rehearsal.
7. Mark complete only after the acceptance criterion is independently verifiable.

## Verification commands

```bash
python scripts/educational_validation/verify_lev_task_register.py --repo-root . --json
```
```bash
python scripts/educational_validation/lev_task_cli.py show <TASK_ID>
```
```bash
pytest -q tests/unit/runtime_kg tests/unit/test_health_readiness_schema_drift_guards.py
```

## Acceptance criteria

- [ ] Recovery runbook and rehearsal.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Recovery runbook and rehearsal.

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
