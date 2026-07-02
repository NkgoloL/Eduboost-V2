---
title: "RR-005 Technical Debt Burn-Down Policy"
status: active
owner: engineering
audience: developer
source_of_truth: true
evidence_command: "PYTHONPATH=. python3 scripts/technical_debt/audit_rr005_technical_debt.py --json"
---

# RR-005 Technical Debt Burn-Down Policy

This policy binds RR-005 to the reconciled outstanding-work register. It does not create a new roadmap phase.

## Required evidence areas

1. Ruff debt inventory is captured with `ruff check app tests scripts --statistics` and JSON output when the tool is available.
2. Import-linter `ignore_imports` exceptions are registered for follow-up.
3. Stale route comments are audited across active router files.
4. Alembic migration history is audited and a squash decision is recorded.
5. Dormant routers are reviewed before any retirement/archive work.

## Residual caveats carried forward

- RR-003 is recorded as valid, but the fallback coverage baseline recorded `0.0` because full test collection still had pre-existing blockers.
- RR-006 is recorded as valid, but its evidence PR merged with only the required branch-protection check blocking; other non-required checks were red.

## Boundaries

- Production release is not authorised.
- Deployment is not authorised.
- Release tagging is not authorised.
- Public beta is not authorised.
- Runtime KG implementation is not authorised and remains a future architectural north-star only.
