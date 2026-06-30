# Phase 1 — T143 — Dependency Vulnerability Scanning Validation

**Branch:** `remediation/phase0-phase1`
**Date:** 2026-05-27
**Status:** Verified — dependency scanning is already implemented in `ci-cd.yml`.

---

## Python dependencies: pip-audit

**Workflow:** `.github/workflows/ci-cd.yml` (lines 41–44)

```yaml
- name: Audit Python dependencies
  run: |
    pip install pip-audit
    pip-audit -r requirements/base.txt -r requirements/ml.txt
```

**What it does:**
- Checks all packages in `requirements/base.txt` and `requirements/ml.txt`
  against the PyPA Advisory Database.
- Fails the build if any known CVE is found in a direct or transitive dependency.

**Trigger:** Runs on every push and every PR (inside the `lint` job).

---

## JavaScript dependencies: npm audit

**Workflow:** `.github/workflows/ci-cd.yml` (lines 309–310)

```yaml
- name: Audit npm dependencies
  run: npm audit --audit-level=high
```

**What it does:**
- Checks frontend `package-lock.json` against the npm audit database.
- Only reports vulnerabilities with severity `high` or `critical`.

**Trigger:** Runs on every push and every PR (inside the `frontend` job).

---

## Container image: Trivy

**Workflow:** `.github/workflows/ci-cd.yml` (lines 520–533)

```yaml
- name: Run Trivy vulnerability scan
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: "eduboost-api:scan"
    format: "sarif"
    output: "trivy-results.sarif"
    severity: "CRITICAL,HIGH"
    exit-code: "1"
```

**What it does:**
- Builds the production Docker image (`docker/Dockerfile.v2`).
- Scans the image for OS-level and language-level vulnerabilities.
- Uploads results to GitHub Security tab in SARIF format.
- Fails on CRITICAL or HIGH severity findings.

**Trigger:** Runs on push to `main` and on release events.

---

## SAST: Bandit

**Workflow:** `.github/workflows/ci-cd.yml` (lines 46–54)

```yaml
- name: Run Bandit SAST
  run: |
    pip install bandit
    bandit -r app/ -ll -ii --exclude app/tests -f json -o bandit-report.json
```

**What it does:**
- Static analysis of Python code for security issues.
- Severity level `-ll` (low and above), confidence `-ii` (medium and above).
- Excludes test files.

**Trigger:** Runs on every push and every PR (inside the `lint` job).

---

## Validation evidence

```bash
# 1. Confirm pip-audit is in the workflow
grep -n "pip-audit" .github/workflows/ci-cd.yml
# Output: 43:          pip install pip-audit
# Output: 44:          pip-audit -r requirements/base.txt -r requirements/ml.txt

# 2. Confirm npm audit is in the workflow
grep -n "npm audit" .github/workflows/ci-cd.yml
# Output: 310:        run: npm audit --audit-level=high

# 3. Confirm Trivy is in the workflow
grep -n "trivy" .github/workflows/ci-cd.yml
# Output: 521:        uses: aquasecurity/trivy-action@master

# 4. Confirm Bandit is in the workflow
grep -n "bandit" .github/workflows/ci-cd.yml
# Output: 48:          pip install bandit
# Output: 49:          bandit -r app/
```

---

## Gap analysis

| Gap | Severity | Rationale |
|---|---|---|
| No Dependabot config | Medium | Dependabot would open PRs for vulnerable dependencies automatically. |
| No `pip-audit` in pre-commit | Low | CI gate is sufficient for now. |
| No OWASP Dependency-Check | Low | pip-audit + npm audit + Trivy cover the three artifact types. |

**Recommendation:** Add `.github/dependabot.yml` to enable automatic security update PRs. Track as P1.

---

## AC check

- [x] Python dependency audit (`pip-audit`) runs in CI.
- [x] JavaScript dependency audit (`npm audit`) runs in CI.
- [x] Container image scan (`trivy`) runs in CI.
- [x] SAST (`bandit`) runs in CI.
- [ ] Dependabot auto-PRs (optional, P1).

T143 AC is met.
