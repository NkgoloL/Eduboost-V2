# Branch Protection Evidence

**Status:** verified

| Field | Value |
|---|---|
| Protected branch | codex/production_readiness |
| Required checks | ci-core, backend-runtime-enablement-full-check |
| Pull request required | True |
| Admin enforced | False |
| Bypass disabled | True |
| Evidence URL/path | https://github.com/NkgoloL/Eduboost-V2/settings/branches |
| Captured at | 2026-05-17T10:06:09Z |

## Usage

```bash
PROTECTED_BRANCH=codex/production_readiness \
BRANCH_REQUIRED_CHECKS='ci-core,backend-runtime-enablement-full-check' \
BRANCH_PR_REQUIRED=true \
BRANCH_BYPASS_DISABLED=true \
make branch-protection-evidence-capture
```
