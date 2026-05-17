# CI Evidence

**Status:** pending_remote_ci_evidence

| Field | Value |
|---|---|
| GitHub Actions run URL | PENDING |
| Commit SHA | PENDING |
| Branch | PENDING |
| Result | PENDING |
| Test summary | PENDING |
| Captured at | 2026-05-17T12:12:51Z |

## Usage

```bash
GITHUB_ACTIONS_RUN_URL=https://github.com/<owner>/<repo>/actions/runs/<id> \
CI_RESULT=success \
CI_COMMIT_SHA=<sha> \
CI_BRANCH=codex/production_readiness \
make remote-ci-evidence-capture
```
