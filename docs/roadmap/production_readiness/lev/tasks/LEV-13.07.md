# LEV-13.07 — Implementation Task Card

**Workstream:** LEV-WS13 — Operate drift detection and revalidation controls  
**Phase:** LEV-3  
**Priority:** P1  
**Status:** `not_started`  
**Implementation type:** `engineering`  
**Estimated effort:** M/L  
**Human dependency:** No  
**Cannot be completed by code alone:** Yes

## Required outcome

Implement shadow evaluation for candidate models and policies before promotion.

## Definition-of-done link

Drift and revalidation controls operate in production.

## Dependencies

- `LEV-13.06`

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
- `docs/research/longitudinal_validation/evidence/13.07_shadow_deployment_evidence.md`

## Implementation procedure

1. Read the LEV-WS13 workstream specification and confirm prerequisites for task 13.07.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Implement shadow evaluation for candidate models and policies before promotion.
4. Add or update unit, integration and contract tests for the changed behaviour.
5. Run focused checks, then the LEV register verifier and applicable repository quality gates.
6. Attach or link the required evidence: Shadow-deployment evidence.
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

- [ ] Shadow-deployment evidence.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Shadow-deployment evidence.

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
