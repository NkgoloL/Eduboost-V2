# Branching and Protection Policy

**Owner:** Platform / Engineering
**Last updated:** 2026-05-27 (Phase 1 T141)
**Status:** Enforced via GitHub branch protection rules

---

## Branch model

EduBoost V2 uses a **trunk-based** branching model with short-lived feature
branches.

```
main  ──────────────────────────────────────────────►  production
  │                                                      deployment
  │    (tag → release.yml → production-promote)
  │
  ├─── remediation/phase0-phase1  ──► PR ──► squash merge
  ├─── feature/content-filter       ──► PR ──► squash merge
  └─── hotfix/jwt-key-rotation      ──► PR ──► squash merge
```

### Branch definitions

| Branch | Purpose | Lifetime |
|---|---|---|
| `main` | Production-ready trunk | Permanent |
| `remediation/*` | Hardening / security batches | Weeks |
| `feature/*` | New features | Days |
| `hotfix/*` | Urgent production fixes | Hours |

---

## Branch protection rules (`main`)

These rules are configured in the GitHub repository settings and must not be
relaxed without Security + Platform owner approval.

### Required status checks

The following CI jobs must pass before a PR can be merged into `main`:

| Check | Workflow | Rationale |
|---|---|---|
| `Lint & Type Check` | `ci-cd.yml` | Prevents syntax errors and type mismatches |
| `Unit Tests` | `ci-cd.yml` | Prevents regressions in unit-tested code |
| `Integration Tests` | `ci-cd.yml` | Prevents DB and service integration regressions |
| `V2 API Smoke Test` | `ci-cd.yml` | Prevents app startup / import failures |
| `Schema Drift Check` | `ci-cd.yml` | Prevents un-migrated model changes |
| `Secrets Scan` | `ci-cd.yml` | Prevents credential leakage |
| `Migration Check` | `migration_check.yml` | Prevents Alembic integrity issues |
| `Observability Check` | `observability_check.yml` | Prevents broken alerting configs |

### Merge requirements

- **Require pull request reviews before merging:** at least 1 approving review.
- **Require review from Code Owners:** for files matching `CODEOWNERS`.
- **Require status checks to pass:** all listed above.
- **Require branches to be up to date before merging:** yes (rebase or merge from `main`).
- **Require linear history:** yes (squash merge or rebase merge only).
- **Do not allow bypassing the above settings:** yes (even for admins).

### CODEOWNERS

```text
# Global fallback
* @nkgolol

# Security-sensitive files
app/core/security.py @nkgolol
app/core/token_config.py @nkgolol
app/core/config.py @nkgolol
app/services/jwt_keyring.py @nkgolol

# POPIA / privacy
app/api_v2_routers/popia.py @nkgolol
app/modules/consent/ @nkgolol

# CI/CD
.github/workflows/ @nkgolol
render.yaml @nkgolol

# Alerting / observability
alertmanager/ @nkgolol
prometheus/ @nkgolol

# Documentation
docs/adr/ @nkgolol
audits/ @nkgolol
```

*(Note: CODEOWNERS file should be created at repository root if not present.)*

---

## Commit conventions

All commits on `main` (via squash merge) must follow:

```text
<type>: <short description>

<body — optional but recommended for non-trivial changes>
```

Types:

| Type | Use for |
|---|---|
| `feat` | New features |
| `fix` | Bug fixes |
| `docs` | Documentation changes |
| `phase0` / `phase1` | Remediation batch work |
| `security` | Security fixes |
| `review` | Review corrections |
| `chore` | Maintenance, dependency updates |
| `ci` | CI/CD changes |
| `test` | Test-only changes |

---

## Release process

1. Create a release via GitHub UI → Actions → Release → Run workflow.
2. Select bump type (`patch`, `minor`, `major`).
3. The workflow:
   - Bumps `app/api/version.py`.
   - Updates `CHANGELOG.md`.
   - Commits, tags, pushes.
   - Creates a GitHub Release with notes.
4. The tag push triggers `production-promote` in `ci-cd.yml`.
5. `production-promote`:
   - Runs staging smoke tests.
   - Deploys to Kubernetes.
   - Verifies production health.

**No manual deploys to production.** All production deploys go through the
release workflow.

---

## Validation

```bash
# Confirm branch protection rules are visible (requires repo admin access)
gh api repos/nkgoloL/Eduboost-V2/branches/main/protection

# Confirm CODEOWNERS is present
test -f CODEOWNERS && echo "CODEOWNERS exists" || echo "CODEOWNERS missing"
```
