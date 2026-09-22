# LEV-13.01 — Implementation Task Card

**Workstream:** LEV-WS13 — Operate drift detection and revalidation controls  
**Phase:** LEV-3  
**Priority:** P1  
**Status:** `not_started`  
**Implementation type:** `governance_and_documentation`  
**Estimated effort:** S/M  
**Human dependency:** No  
**Cannot be completed by code alone:** Yes

## Required outcome

Define drift types: population, concept prevalence, item parameter, calibration, performance, feature, label, graph, content and policy drift.

## Definition-of-done link

Drift and revalidation controls operate in production.

## Dependencies

- `LEV-03.14`
- `LEV-04.14`
- `LEV-05.14`
- `LEV-08.14`
- `LEV-09.15`
- `LEV-11.14`
- `LEV-12.13`

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
- `docs/research/longitudinal_validation/evidence/13.01_drift_taxonomy.md`

## Implementation procedure

1. Read the LEV-WS13 workstream specification and confirm prerequisites for task 13.01.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Define drift types: population, concept prevalence, item parameter, calibration, performance, feature, label, graph, content and policy drift.
4. Circulate the draft to accountable and consulted roles.
5. Resolve comments and obtain the required versioned approval.
6. Attach or link the required evidence: Drift taxonomy.
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

- [ ] Drift taxonomy.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Drift taxonomy.

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
