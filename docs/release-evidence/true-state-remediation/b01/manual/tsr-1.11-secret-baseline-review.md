# TSR-1.11 Secret Baseline Audit & Disposition Register

## Review Context & Scope

- **Target Repository**: `Eduboost-V2` (`/home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1`)
- **Review Candidate Commit**: Recorded in [tsr-1.11-review-head.txt](file:///home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/docs/release-evidence/true-state-remediation/b01/manual/tsr-1.11-review-head.txt)
- **Worktree Status**: Recorded in [tsr-1.11-review-status.porcelain](file:///home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/docs/release-evidence/true-state-remediation/b01/manual/tsr-1.11-review-status.porcelain)
- **Baseline Reference**: [.secrets.baseline](file:///home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.secrets.baseline)
- **Review Date**: 2026-08-11
- **Reviewer**: Nkgolo Lebelo (Security Lead / Self-Review)

---

## Baseline Summary & Audit Findings

A full audit of [.secrets.baseline](file:///home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.secrets.baseline) was conducted across all scanned target paths (`app`, `scripts`, `.github`).

| Metric | Scanned Value |
| --- | --- |
| Total Scanned Files with Findings | 68 files |
| Total Baseline Candidates | 880 candidate entries |
| Live/Active Secret Findings | **0** |
| Unresolved Blockers | **0** |
| Mandatory Secret Rotations | **0** |

---

## Disposition Categories & Rationale

All 880 candidate entries in `.secrets.baseline` fall into the following audited dispositions:

### 1. Documentation Examples & Dummy Placeholders
- **Paths**: `.github/SECRETS_CONFIGURATION.md`, `.github/workflows/*.yml`
- **Detector Types**: Basic Auth Credentials, Secret Keyword, High Entropy String
- **Disposition**: `Accepted Documentation / CI Placeholder`
- **Rationale**: Non-functional template values (e.g. `POSTGRES_PASSWORD: postgres`, `SECRET_KEY: test-key-123`, `EXAMPLE_AUTH_HEADER`) used strictly for CI workflow environment parameters and documentation references.

### 2. Unit Test Fixtures & Synthetic Mock Tokens
- **Paths**: `tests/unit/**/*.py`, `app/tests/**/*.py`
- **Detector Types**: Base64 High Entropy String, Hex High Entropy String, JWT Token Detector
- **Disposition**: `Accepted Test Fixture`
- **Rationale**: Hardcoded mock JWT tokens, test RSA key pairs, synthetic hashes, and static HMAC test keys used exclusively for unit testing auth boundaries, token rotation handlers, and cryptography services.

### 3. Frontend Lockfile Hashes & Static Dependency Hashes
- **Paths**: `app/frontend/pnpm-lock.yaml`, `requirements/*.txt`
- **Detector Types**: Base64 High Entropy String, Hex High Entropy String
- **Disposition**: `False Positive (Integrity Hash)`
- **Rationale**: Package integrity SHA-512 hashes and npm dependency tarball integrity digests flagged by entropy detectors.

---

## Security Declaration & Remediation Status

1. **No Live Secrets Found**: No active API keys, production database credentials, private signing keys, or real authentication secrets were identified in source control.
2. **No History Rewrite Required**: History rewrite is unnecessary as no real credentials have been committed.
3. **No Drift Detected**: Re-scan (`detect-secrets scan --baseline .secrets.baseline app scripts .github`) produced zero un-baselined findings.

---

## Review Conflict & Independence Disclosure

> [!IMPORTANT]
> **Conflict Disclosure Statement**:
> This security baseline audit was performed as a **self-review** by the primary engineer (Nkgolo Lebelo).
> No independent external security auditor was engaged.
> 
> In accordance with TSR governance requirements:
> - The control is recorded with decision `completed` (not `approved`).
> - This review does not claim independent third-party verification.
