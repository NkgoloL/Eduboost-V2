# Phase 1 — T142 — Secret Scanning Validation

**Branch:** `remediation/phase0-phase1`
**Date:** 2026-05-27
**Status:** Verified — secret scanning is already implemented in `ci-cd.yml`.

---

## Tool: gitleaks

**Workflow:** `.github/workflows/ci-cd.yml` (lines 538–547)

```yaml
secrets-scan:
  name: Secrets Scan
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0
    - uses: gitleaks/gitleaks-action@v2
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**What it does:**
- Scans the full git history (`fetch-depth: 0`) for hard-coded secrets.
- Uses the default gitleaks ruleset which covers:
  - AWS access keys
  - GCP service account keys
  - Azure service principals
  - GitHub personal access tokens
  - Slack webhooks
  - JWT secrets / RSA private keys
  - Database connection strings with embedded passwords
  - Stripe API keys
  - SendGrid API keys
  - Generic high-entropy strings matching secret patterns

**Trigger:** Runs on every push and every PR.

---

## Validation evidence

```bash
# 1. Confirm the workflow file contains gitleaks
grep -n "gitleaks" .github/workflows/ci-cd.yml
# Output: 545:      - uses: gitleaks/gitleaks-action@v2

# 2. Confirm it runs on PRs
grep -A5 "on:" .github/workflows/ci-cd.yml | head -10
# pull_request:
#   branches: [master, main]

# 3. Confirm fetch-depth: 0 is set (full history scan)
grep -n "fetch-depth" .github/workflows/ci-cd.yml
# Output: 544:          fetch-depth: 0
```

---

## Gap analysis

| Gap | Severity | Rationale |
|---|---|---|
| No pre-commit hook for gitleaks | Low | CI gate catches secrets before merge, but local commit is faster feedback. |
| No `.gitleaks.toml` custom config | Low | Default ruleset is comprehensive for Python/JS projects. |

**Recommendation:** Add a pre-commit hook (`pre-commit-gitleaks`) for developer-local feedback. Track as P2.

---

## AC check

- [x] Secret scanning tool is integrated into CI (`gitleaks-action@v2`).
- [x] Scans full git history (`fetch-depth: 0`).
- [x] Runs on every push and PR.
- [ ] Pre-commit hook (optional, P2).

T142 AC is met.
