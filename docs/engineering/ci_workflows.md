# CI/CD Workflows

**Owner:** Platform / Engineering
**Last updated:** 2026-05-27 (Phase 1 T140)
**Status:** Active

This document inventories all GitHub Actions workflows in `.github/workflows/`.
It is the authoritative reference for what runs, when, and why.

---

## Workflow index

| Workflow | File | Trigger | Purpose |
|---|---|---|---|
| **Main CI/CD** | `ci-cd.yml` | push (master/main/develop), PR (master/main), release | Lint, test, build, scan, deploy |
| **Release** | `release.yml` | workflow_dispatch | Version bump, tag, GitHub Release |
| **Migration check** | `migration_check.yml` | push, PR | Alembic integrity, model drift, seed schema |
| **Observability check** | `observability_check.yml` | push, PR | Promtool + amtool validation |
| **Staging smoke** | `staging-smoke.yml` | schedule (cron), workflow_dispatch | Staging health checks |
| **Auth refresh DB proof** | `auth-refresh-db-proof.yml` | push, PR | Auth token lifecycle DB integration |
| **Auth boundary** | `auth-boundary.yml` | push, PR | Auth module import boundary enforcement |
| **Privacy boundary** | `privacy-boundary.yml` | push, PR | POPIA-related import boundary checks |
| **POPIA consent audit** | `popia-consent-audit.yml` | push, PR | Consent record integrity checks |
| **Learner authz coverage** | `learner-authz-coverage.yml` | push, PR | Learner authorization coverage gate |
| **API envelope contract** | `api-envelope-error-contract.yml` | push, PR | API response envelope validation |
| **OpenAPI contract** | `openapi-contract.yml` | push, PR | OpenAPI spec contract validation |
| **OpenAPI drift** | `openapi-drift.yml` | push, PR | OpenAPI spec drift detection |
| **Legacy route guard** | `legacy-route-guard.yml` | push, PR | Legacy V1 route deprecation checks |
| **Runtime contract** | `runtime-contract.yml` | push, PR | Runtime behaviour contract checks |
| **Architecture gates** | `architecture-gates.yml` | push, PR | Architecture decision enforcement |
| **Backend consolidation** | `backend-consolidation.yml` | push, PR | Backend module consolidation checks |
| **Item bank CI** | `item_bank_ci.yml` | push, PR | Item bank coverage and quality gates |
| **CI diagnostics** | `ci_diagnostics_assessment.yml` | push, PR | CI pipeline diagnostic assessment |
| **Lesson quality** | `ci_lesson_quality.yml` | push, PR | Lesson content quality gates |
| **Cluster D CI** | `cluster-d-ci.yml` | push, PR | Cluster D (data) CI checks |
| **Cluster E data resilience** | `cluster-e-data-resilience.yml` | push, PR | Data resilience validation |
| **Cluster F AI safety** | `cluster-f-ai-safety.yml` | push, PR | AI safety release evidence checks |
| **Cluster G frontend** | `cluster-g-frontend.yml` | push, PR | Frontend build and test gates |
| **Cluster H release readiness** | `cluster-h-release-readiness.yml` | push, PR | Release readiness checklist |
| **DB backup dry-run** | `db-backup-dryrun.yml` | schedule (cron) | DB backup dry-run validation |
| **DB backup matrix** | `db-backup-matrix.yml` | schedule (cron) | Multi-environment backup matrix test |
| **DB backup restore rollback** | `db-backup-restore-rollback-evidence.yml` | schedule (cron) | Backup restore and rollback evidence |
| **Diag score live audit** | `diag-score-live-audit.yml` | schedule (cron) | Diagnostic score live audit |
| **Frontend E2E** | `frontend-e2e.yml` | push, PR | Frontend end-to-end tests |
| **Learning evidence** | `learning-evidence.yml` | push, PR | Learning outcome evidence collection |
| **Persistence resilience** | `persistence-resilience.yml` | push, PR | Persistence layer resilience checks |
| **Audit write runtime** | `audit-write-runtime-evidence.yml` | push, PR | Audit write runtime evidence |
| **Beta release approval** | `beta-release-approval.yml` | workflow_dispatch | Beta release approval gate |
| **Repo state** | `repo-state.yml` | push, PR | Repository state validation |

**Total:** 36 workflow files.

---

## Main CI/CD pipeline (`ci-cd.yml`)

This is the primary pipeline. All other workflows are specialised gates.

### Jobs (in dependency order)

| Job | Needs | Trigger | Duration (typical) | Fail strategy |
|---|---|---|---|---|
| `lint` | — | push, PR | ~3 min | Fail fast |
| `docs-quality` | — | push, PR | ~2 min | `continue-on-error: true` |
| `unit-tests` | — | push, PR | ~5 min | Fail fast |
| `integration-tests` | — | push, PR | ~8 min | Fail fast |
| `v2-smoke` | — | push, PR | ~3 min | Fail fast |
| `frontend` | — | push, PR | ~6 min | Fail fast |
| `e2e` | `integration-tests` | push, PR | ~10 min | Fail fast |
| `schema-drift` | — | push, PR | ~4 min | Fail fast |
| `content-factory-migrations` | — | push, PR | ~5 min | Fail fast |
| `content-factory-unit-tests` | — | push, PR | ~2 min | Fail fast |
| `popia-tests` | — | push, PR | ~3 min | Fail fast |
| `image-scan` | — | push to main, release | ~8 min | Fail fast |
| `secrets-scan` | — | push, PR | ~2 min | Fail fast |
| `production-promote` | all above | release published | ~5 min | Fail fast |

### Lint job details

```
ruff check app/ tests/ --output-format=github --select E9,F63,F7,F82
mypy app/ --ignore-missing-imports --strict-optional          (continue-on-error)
pip-audit -r requirements/base.txt -r requirements/ml.txt
bandit -r app/ -ll -ii --exclude app/tests -f json -o bandit-report.json
lint-imports
pymarkdown scan docs/ audits/ README.md SECURITY.md CONTRIBUTING.md  (continue-on-error)
```

### Production promotion gate

The `production-promote` job only runs on `release: published` events. It
requires ALL other jobs to pass:

```yaml
needs:
  - lint
  - unit-tests
  - integration-tests
  - frontend
  - schema-drift
  - content-factory-migrations
  - content-factory-unit-tests
  - popia-tests
  - image-scan
  - secrets-scan
  - e2e
```

Steps:
1. Run smoke tests against staging.
2. Deploy to Kubernetes (`kubectl set image`).
3. Verify production health (`/health`, `/judiciary/health`).

---

## Workflow maintenance

### Adding a new workflow

1. Create `.github/workflows/<name>.yml`.
2. Add it to this document.
3. If it is a required gate, add it to the `production-promote.needs` list in
   `ci-cd.yml`.
4. Open a PR and verify it passes on the PR branch.

### Removing a workflow

1. Delete the workflow file.
2. Remove it from this document.
3. Remove it from `production-promote.needs` if referenced.
4. Update the workflow index table.

### Python version policy

All workflows use `PYTHON_VERSION: "3.12.3"` (ADR-001). Do not change this
without updating ADR-001 and all workflow files.

---

## Validation

```bash
# List all workflow files
ls -1 .github/workflows/*.yml | wc -l

# Validate YAML syntax
python3 -c "
from pathlib import Path
import yaml
for p in Path('.github/workflows').glob('*.yml'):
    yaml.safe_load(p.read_text())
    print('OK:', p.name)
"
```
