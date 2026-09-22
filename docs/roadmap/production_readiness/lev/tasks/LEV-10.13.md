# LEV-10.13 — Implementation Task Card

**Workstream:** LEV-WS10 — Demonstrate that mastery-informed recommendations improve learning  
**Phase:** LEV-4  
**Priority:** P2  
**Status:** `not_started`  
**Implementation type:** `analysis_and_validation`  
**Estimated effort:** M/L after data readiness  
**Human dependency:** No  
**Cannot be completed by code alone:** Yes

## Required outcome

Conduct pre-specified per-protocol, exposure, mediation, sensitivity and subgroup analyses without replacing the primary result.

## Definition-of-done link

Recommendations improve independent learning outcomes.

## Dependencies

- `LEV-10.12`

## Existing repository files to inspect or modify

- `app/modules/study_plans/runtime_kg_planner.py`
- `app/modules/lessons/adaptive_remediation.py`
- `app/services/study_plan_service_v2.py`
- `app/services/lesson_service_v2.py`
- `tests/e2e/study_plan_and_lesson.spec.ts`

## Planned or new files

- `docs/research/longitudinal_validation/impact_study_protocol.md`
- `scripts/educational_validation/run_impact_analysis.py`
- `docs/research/longitudinal_validation/evidence/10.13_secondary_analysis_report.md`

## Implementation procedure

1. Read the LEV-WS10 workstream specification and confirm prerequisites for task 10.13.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Conduct pre-specified per-protocol, exposure, mediation, sensitivity and subgroup analyses without replacing the primary result.
4. Freeze the analysis input manifest before examining outcome results.
5. Execute the pre-specified analysis with reproducible code and retain diagnostics, uncertainty and sensitivity outputs.
6. Attach or link the required evidence: Secondary analysis report.
7. Mark complete only after the acceptance criterion is independently verifiable.

## Verification commands

```bash
python scripts/educational_validation/verify_lev_task_register.py --repo-root . --json
```
```bash
python scripts/educational_validation/lev_task_cli.py show <TASK_ID>
```
```bash
pytest -q tests/e2e/test_diagnostic_flow.spec.ts 2>/dev/null || true
```
```bash
pnpm --dir app/frontend test -- --runInBand
```

## Acceptance criteria

- [ ] Secondary analysis report.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Secondary analysis report.

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
