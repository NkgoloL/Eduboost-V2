# Phase 12 Execution Plan — Security Posture Deepening

**Date**: 2026-06-12
**Updated**: 2026-06-14
**Status**: Complete for static security-gate configuration; live CI proof pending
**Branch**: `phase-12/security-posture-deepening`
**Base**: `origin/master`
**Source**: `docs/roadmap/roadmap.md` § Phase 12
**Priority**: P1
**Scope**: Create a V2 threat model, refresh the pen-test checklist, and wire automated security scanning into pre-commit hooks and CI.

---

## 2026-06-14 Audit Note

Phase 12 originally overstated dependency-scan enforcement because audit
commands were warning-only and the workflow referenced a nonexistent publish
step. The workflow now fails on `pip-audit` findings and critical pnpm audit
findings, uploads audit JSON artifacts, and parses cleanly. `.gitleaks.toml` was
also added.

Live GitHub Actions execution remains the final external proof.

---

## Pre-Conditions

- [x] Phase 11 (Technical Debt Burn-Down) merged to `master`
- [x] Phases 0–11 complete and verified
- [x] Branch `phase-12/security-posture-deepening` created from `master`
- [x] Existing artifacts: `audits/security/pen_test_checklist.md` (47 lines, pre-V2), `.pre-commit-config.yaml` (34 lines, has detect-secrets hook), `.github/dependabot.yml`, `.secrets.baseline` (empty)

---

## Inventory of Gaps

| Area | Status | Action Needed |
|------|--------|---------------|
| Threat model for V2 | ❌ Missing | Create `docs/security/threat_model_v2.md` |
| Pen-test checklist | ⚠️ Stale (pre-V2) | Refresh for V2 routes and modules |
| Secrets scanning (CI) | ❌ Missing | Create `.github/workflows/secrets-scan.yml` |
| Secrets scanning (pre-commit) | ✅ Already wired (detect-secrets) | Verify it works with `.secrets.baseline` |
| Dependency scanning (CI) | ❌ Missing | Create `.github/workflows/dependency-scan.yml` with `pip-audit` |
| Dependabot | ✅ Exists | Verify it covers Python (pip) and Node (npm/pnpm), add CI gating |
| Gitleaks config | ❌ Missing | Create `.gitleaks.toml` |
| `.secrets.baseline` | ⚠️ Empty (7 lines) | Re-generate with actual scan baseline |

---

## Work Groups

### J.1 — V2 Threat Model [P1]

**Create** `docs/security/threat_model_v2.md` covering:

- [x] **Authentication surfaces**: JWT signing, refresh token rotation, cookie security, rate limiting
- [x] **Session surfaces**: Token revocation, Redis-backed session store, fail-closed behavior
- [x] **API surfaces**: All public routes, consent-gated routes, authorization policy helpers
- [x] **Data surfaces**: PII encryption-at-rest (pgcrypto), PII minimization (pseudonym_id for LLM), data export/erasure flows
- [x] **Infrastructure surfaces**: Azure Key Vault integration, Docker non-root, network isolation, WAF/CDN posture
- [x] **LLM surfaces**: Prompt injection risks, PII leakage prevention (popia_sweep), output validation
- [x] **Threat matrix**: STRIDE or equivalent categorization with mitigations

**Evidence:** `docs/security/threat_model_v2.md`  
**Risk:** Low — documentation effort, ~100–150 lines

### J.2 — Pen-Test Checklist Refresh [P1]

- [x] Review current `audits/security/pen_test_checklist.md` (47 lines, pre-V2)
- [x] Update to reference current V2 routes, modules, and infrastructure
- [x] Add test cases for:
  - V2 auth flows (register, login, refresh, logout, password reset)
  - Consent gate bypass attempts
  - Object-level authorization bypass attempts
  - Data export/erasure endpoint security
  - LLM prompt injection
- [x] Remove pre-V2 references (legacy routes, five-pillar terminology)

**Evidence:** Updated `audits/security/pen_test_checklist.md`  
**Risk:** Low — documentation refresh

### J.3 — Secrets Scanning CI [P1]

- [x] Create `.github/workflows/secrets-scan.yml`:
  - Runs `detect-secrets` scan on every push and PR
  - Uses `.secrets.baseline` for known false positives
  - Fails CI if new secrets detected without baseline update
- [x] Verify `.pre-commit-config.yaml` detect-secrets hook works correctly
- [x] Re-generate `.secrets.baseline`:
  - Run `detect-secrets scan > .secrets.baseline`
  - Audit results and add any false-positive exclusions
  - Commit the updated baseline

**Evidence:** `.github/workflows/secrets-scan.yml`, updated `.secrets.baseline`  
**Risk:** Low — CI workflow creation

### J.4 — Dependency Vulnerability Scanning CI [P1]

- [x] Create `.github/workflows/dependency-scan.yml`:
  - Installs `pip-audit` or uses `safety`
  - Runs against `requirements.txt`, `requirements-dev.txt`, `requirements-docs.txt`, `requirements-ml.txt`
  - Fails on critical-severity CVEs (configurable threshold)
  - Runs on push and PR
- [x] Add `pip-audit` to `requirements-dev.txt` for local availability
- [x] Optionally add npm audit step for frontend deps

**Evidence:** `.github/workflows/dependency-scan.yml`  
**Risk:** Low — CI workflow creation

### J.5 — Dependabot Gating Enhancement [P1]

- [x] Verify `.github/dependabot.yml` covers:
  - Python pip (`requirements/` directory)
  - Node npm/pnpm (`app/frontend/` directory)
  - GitHub Actions
- [x] Enable `open-pull-requests-limit` for manageable volume
- [x] Document in `docs/operations/dependency_management.md` the Dependabot workflow:
  - How to review and merge dependency PRs
  - Critical CVE response SLA
  - Automated merge strategy for patch versions (if any)

**Evidence:** Updated `.github/dependabot.yml`, updated `docs/operations/dependency_management.md`  
**Risk:** Low — configuration and documentation

---

## Execution Order

```
Week 1:  J.1 (threat model) — writing, most substantive deliverable
         J.2 (pen-test checklist) — quick refresh, can parallelize
Week 2:  J.3 (secrets scanning CI) — workflow + baseline generation
         J.4 (dependency scanning CI) — workflow creation
         J.5 (Dependabot gating) — config + docs
```

---

## Definition of Done

- [x] `docs/security/threat_model_v2.md` created covering auth, session, API, data, infra, and LLM surfaces
- [x] `audits/security/pen_test_checklist.md` refreshed for V2 routes and surfaces
- [x] `.github/workflows/secrets-scan.yml` created and functional
- [x] `.secrets.baseline` re-generated with real scan results
- [x] `.github/workflows/dependency-scan.yml` created with critical-CVE gate
- [x] `.github/dependabot.yml` verified to cover all ecosystems
- [x] `docs/operations/dependency_management.md` updated with Dependabot workflow
- [x] Implementation report written
- [x] PR merged to `master`
