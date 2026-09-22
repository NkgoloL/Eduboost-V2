# PRD-4A Longitudinal Educational Validation Execution Package

This directory provides the executable task-control layer for EduBoost's 222 longitudinal educational-validation sub-tasks.

## Authoritative files

- `../../prd_4a_longitudinal_educational_validation_register.json` — machine-readable task register.
- `../../prd_4a_longitudinal_educational_validation_todo.md` — complete human-readable TODO.
- `tasks/` — 222 implementation task cards.
- `evidence/` — 222 evidence records, initially `not_started`.
- `workstreams/` — 15 workstream execution guides.
- `templates/` — required research, governance and evidence templates.
- `schemas/` — task, evidence and proposed runtime validation schemas.

## Non-negotiable limitation

The package implements planning, traceability and verification infrastructure. It does not fabricate longitudinal evidence, independent review, learner consent, school participation, calibrated item data or educational-effectiveness results. Tasks requiring those inputs remain open until real evidence exists.

## Commands

```bash
python scripts/educational_validation/lev_repository_preflight.py --repo-root . --json
python scripts/educational_validation/verify_lev_task_register.py --repo-root . --json
python scripts/educational_validation/lev_task_cli.py status
python scripts/educational_validation/lev_task_cli.py show 01.01
python scripts/educational_validation/generate_lev_status_report.py --repo-root .
```
