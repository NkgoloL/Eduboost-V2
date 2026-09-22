# LEV-11.14 — Implementation Task Card

**Workstream:** LEV-WS11 — Measure and control adverse educational effects  
**Phase:** LEV-6  
**Priority:** P2  
**Status:** `not_started`  
**Implementation type:** `operations`  
**Estimated effort:** M  
**Human dependency:** No  
**Cannot be completed by code alone:** No

## Required outcome

Operate a recurring educational-safety review board and publish internal trend reports.

## Definition-of-done link

Adverse effects are measured and acceptably controlled.

## Dependencies

- `LEV-11.13`

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
- `docs/research/longitudinal_validation/evidence/11.14_meeting_records_and_action_register.md`

## Implementation procedure

1. Read the LEV-WS11 workstream specification and confirm prerequisites for task 11.14.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Operate a recurring educational-safety review board and publish internal trend reports.
4. Define thresholds, escalation ownership, fallback behaviour and evidence retention.
5. Exercise the control in a rehearsal or controlled environment before production authority.
6. Attach or link the required evidence: Meeting records and action register.
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

- [ ] Meeting records and action register.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Meeting records and action register.

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
