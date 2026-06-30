# JWT Secret Rotation Evidence Status

Generated at: `2026-05-24T00:12:54Z`
Commit: `f9e64c13994a7d5e025bedba6e05eb1f41ffe60a`

**Status:** `jwt-secret-rotation-not-accepted`
**Environment:** ``
**Algorithm:** `HS256`
**Secret store:** ``
**Rotation reference:** ``
**Rotation date:** ``
**Rotation result:** ``
**Run ID:** ``
**Run URL:** ``
**Workflow:** ``

## Redacted secret evidence

| Secret | Present | Length | Fingerprint prefix | Placeholder-like |
|---|---:|---:|---|---:|
| access current | False | 0 | `` | False |
| refresh current | False | 0 | `` | False |
| access previous | False | n/a | `` | n/a |
| refresh previous | False | n/a | `` | n/a |

## Rotation proof

- Access secret rotated: `False`
- Refresh secret rotated: `False`

## JWT self-test

- Access issue/verify: `False`
- Refresh issue/verify: `False`
- Access tamper rejected: `False`
- Refresh tamper rejected: `False`
- Access/refresh separated: `False`

## Blockers

- current access JWT secret is missing
- current refresh JWT secret is missing
- JWT token self-test skipped because current secrets are missing

## No false-closure rules

- This proof closes JWT-001 only in JWT_EVIDENCE_ACCEPT=1 mode.
- Raw JWT secrets are never written to release evidence.
- Access and refresh secrets must be present, non-placeholder, at least 32 characters, and different.
- Previous fingerprints or previous secret values are required to prove rotation.
- Current fingerprints must differ from previous fingerprints.
- JWT issue/verify/tamper-reject self-tests must pass.
- A successful GitHub Actions run matching current commit is required.
- This proof does not close ARQ, DIAG-SCORE, AUDIT-WRITE, DB-ROLLBACK, approvals, frontend runtime, image/SBOM, security scans, or beta release.
