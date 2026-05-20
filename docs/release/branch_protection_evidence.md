# Branch Protection Evidence

**Status:** pending_branch_protection_evidence

| Field | Value |
|---|---|
| Protected branch | codex/production_readiness |
| Required checks | PENDING |
| Pull request required | False |
| Admin enforced | False |
| Bypass disabled | False |
| Evidence URL/path | PENDING |
| Captured at | 2026-05-19T23:01:46Z |

## Usage

```bash
PROTECTED_BRANCH=codex/production_readiness \
BRANCH_REQUIRED_CHECKS='ci-core,backend-runtime-enablement-full-check' \
BRANCH_PR_REQUIRED=true \
BRANCH_BYPASS_DISABLED=true \
make branch-protection-evidence-capture
```
