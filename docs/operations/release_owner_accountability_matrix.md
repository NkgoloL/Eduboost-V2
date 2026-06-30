# Release Owner Accountability Matrix

## Purpose

This matrix records the accountable owners for the remaining manual actions in
the staging/beta release path.

## Accountability Matrix

| Area | Accountable Owner | Evidence |
| --- | --- | --- |
| Release operation | release operator | beta release execution plan |
| Technical approval | technical approver | beta sign-off manifest |
| Privacy/POPIA approval | privacy/POPIA approver | POPIA consent closure evidence |
| Rollback readiness | rollback owner | beta rollback runbook |
| Post-deploy verification | post-deploy verification owner | post-deploy staging smoke checklist |
| Incident response | incident contact | rollback runbook and release decision log |
| Release candidate tagging | release operator | release candidate tag manifest |
| PR evidence closeout | PR owner | PR closeout evidence checklist |

## Required Owner Assertions

- every manual release action has an accountable owner
- privacy/POPIA approval remains separate from technical approval
- rollback owner is assigned before release candidate tag creation
- post-deploy verification owner is assigned before deployment
- incident contact is known before beta release execution
- owner assignments must be recorded before manual approval

## Boundary

The accountability matrix records responsibility. It does not grant approval, execute deployment, or create release tags.

## Command

```bash
make release-owner-accountability-check
```
