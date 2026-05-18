# CI Evidence

**Status:** pending remote CI verification
<!-- Status: pending remote CI verification -->

This file is the stable release gate for remote CI/CD evidence. It must remain pending until a full CI pipeline run is accepted by the release owner.

Latest CI run evidence, when available:

- Full log: `docs/release/ci_latest.log`
- Summary: `docs/release/ci_latest_summary.md`

## Required CI checks

| Check | Expected result | Evidence |
|---|---|---|
| GitHub Actions run URL | workflow URL with all checks passing | TODO |
| Branch build passing | `codex/production_readiness` branch CI green | TODO |
| Route alias policy | all route alias security checks pass | TODO |
| All security scans | dependency audit, secrets scan, SAST passed | TODO |
| Test coverage threshold | meets minimum coverage requirement | TODO |
| Lint/format checks | no violations in code quality gates | TODO |

## Build environment

| Field | Value |
|---|---|
| GitHub Actions run URL | TODO |
| Commit SHA | TODO |
| Branch | TODO |
| Result | TODO |
| Test summary | TODO |
| Captured at | TODO |

## Usage

```bash
GITHUB_ACTIONS_RUN_URL=https://github.com/<owner>/<repo>/actions/runs/<id> \
CI_RESULT=success \
CI_COMMIT_SHA=<sha> \
CI_BRANCH=codex/production_readiness \
make remote-ci-evidence-capture
```

## Decision

- [ ] CI evidence passed and is accepted for release evidence.
- [ ] CI evidence failed and release is blocked.
