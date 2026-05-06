# EduBoost V2 — Completion Roadmap

This roadmap now serves as a completion ledger for the TODO execution run.

## Status

- Tasks complete: `59 / 60`
- Active runtime: `app.api_v2:app`
- Default local stack: `docker compose up --build`
- Archived compatibility layer: [`app/legacy/DEPRECATED.md`](/app/legacy/DEPRECATED.md)

## Completion Matrix

| Group | Scope | Status | Notes |
|---|---|---|---|
| A | CI/CD and repo hygiene | Complete | gitleaks, pip-audit, npm audit, Playwright gate, Dependabot, coverage enforcement |
| B | Security hardening | Complete | refresh rotation, RBAC, denylist, headers, Key Vault, broker credential cleanup |
| C | POPIA completion | Complete | erasure verification, consent audit trail, append-only audit table, renewal reminders, RLHF PII gate |
| D | V2 migration completion | Complete | Redis healthcheck, import-linter, core consolidation, job polling, dependency split, legacy decommission |
| E | Pedagogical validity | Complete | 500+ item seed, Ether onboarding, gap-probe cascade, CAPS alignment |
| F | AI layer and cost control | Complete | async LLM clients, schema enforcement, semantic cache, quotas, token telemetry |
| G | Observability | Complete | alerts, PostHog telemetry, deep health |
| H | Frontend and UX | Complete | strict TypeScript, 80% coverage gate, parent portal, offline sync |
| I | Dependency and infra | Complete | split lockfiles, Stripe, Docker layer caching, secret rotation, pip-compile |
| J | Docs and GA release | In progress | docs are complete; GA release publish remains blocked by final release verification |

## Verification Snapshot

Green in this execution batch:

- `PYTHONPATH=. .venv/bin/pytest tests/smoke -q -o addopts=""`
- `PYTHONPATH=. .venv/bin/python scripts/popia_sweep.py --fail-on-issues`
- `PYTHONPATH=. .venv/bin/mkdocs build --strict`
- `cd app/frontend && npm test`
- `cd app/frontend && npm run test:coverage`
- `cd app/frontend && npm run type-check`

## Release Blocker

Task 60 is the only remaining open item.

Current blockers:

1. The broader supported V2 pytest suite still reports active regressions.
2. GitHub release publication is not covered by the available local tooling in
   this run.
3. Production-promotion / Kubernetes rollout cannot be validated from the local
   WSL workspace alone.

## Next Action

Close the remaining V2 regression suite, then perform the GitHub release and
production-promotion verification in a connected release session.
