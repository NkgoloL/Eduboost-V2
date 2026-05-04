# Security Policy

EduBoost SA handles children’s learning and consent data. Security work here is
product work, not housekeeping.

## Supported Versions

| Version | Supported |
|---|---|
| `master` | Yes |
| Current tagged release | Yes |
| Archived branches | No |

## Reporting a Vulnerability

Please do not open a public issue for security problems.

Report privately with:

- affected component
- reproduction steps
- impact
- any evidence of learner-data exposure

Use the maintainer contact listed on the GitHub profile:
[NkgoloL](https://github.com/NkgoloL)

## Security Controls in the V2 Runtime

- 15-minute access tokens and rotating refresh cookies
- Redis-backed JWT denylist and forced session invalidation
- RBAC across student, parent, teacher, and admin roles
- Azure Key Vault production secret loading plus hot rotation
- POPIA consent gating before learner-data access
- Append-only PostgreSQL audit events for sensitive workflows
- Security headers middleware and production TLS termination
- pip-audit, npm audit, Bandit, gitleaks, and Dependabot in the delivery path

## POPIA-Sensitive Areas

We treat the following as highest risk:

- consent bypass
- learner PII leakage
- export or erasure workflow failures
- audit tampering
- direct LLM exposure of real identifiers
- auth/session escalation across roles

## Known Gaps

All previously self-disclosed gaps are now closed:

| Gap | Status | Closing Commit |
|---|---|---|
| Right-to-erasure end-to-end verification | Complete | [`1160234`](https://github.com/NkgoloL/Eduboost-V2/commit/1160234) |
| Consent audit trail across workflows | Complete | [`1160234`](https://github.com/NkgoloL/Eduboost-V2/commit/1160234) |
| Automated dependency vulnerability scanning | Complete | [`b715422`](https://github.com/NkgoloL/Eduboost-V2/commit/b715422), [`b1bfa3e`](https://github.com/NkgoloL/Eduboost-V2/commit/b1bfa3e), [`25488dc`](https://github.com/NkgoloL/Eduboost-V2/commit/25488dc) |
| Production HTTPS enforcement and secure headers | Complete | [`f035974`](https://github.com/NkgoloL/Eduboost-V2/commit/f035974), [`b9f4f06`](https://github.com/NkgoloL/Eduboost-V2/commit/b9f4f06) |
| Refresh token rotation | Complete | [`4ef62f7`](https://github.com/NkgoloL/Eduboost-V2/commit/4ef62f7) |
| CI/CD secrets scanning and push protection | Complete | [`7407889`](https://github.com/NkgoloL/Eduboost-V2/commit/7407889), [`d8a6b54`](https://github.com/NkgoloL/Eduboost-V2/commit/d8a6b54) |

## Additional Controls Added

| Control | Status | Commit |
|---|---|---|
| Azure Key Vault production secret sourcing | Active | [`d2a7950`](https://github.com/NkgoloL/Eduboost-V2/commit/d2a7950) |
| Azure Key Vault hot secret rotation | Active | [`89c6c77`](https://github.com/NkgoloL/Eduboost-V2/commit/89c6c77) |
| Four-role RBAC | Active | [`91a2c41`](https://github.com/NkgoloL/Eduboost-V2/commit/91a2c41) |
| Redis JWT denylist | Active | [`d2a7950`](https://github.com/NkgoloL/Eduboost-V2/commit/d2a7950) |
| HTTP security headers | Active | [`b9f4f06`](https://github.com/NkgoloL/Eduboost-V2/commit/b9f4f06) |
| Append-only V2 audit table | Active | [`1160234`](https://github.com/NkgoloL/Eduboost-V2/commit/1160234) |

## Verification Expectations

Before security-sensitive merges:

```bash
pytest tests/popia -v
python scripts/popia_sweep.py --fail-on-issues
alembic check
```

For broader release confidence:

```bash
pytest tests/ -v --tb=short
cd app/frontend && npm run test:coverage
mkdocs build --strict
```
