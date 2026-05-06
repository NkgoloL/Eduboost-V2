# Security Policy

EduBoost SA handles learner and guardian data. This document is meant to track
the verifiable security posture of the current `master` branch, not an
aspirational future state.

## Supported Versions

| Version | Supported |
|---|---|
| `master` | Yes |
| Current tagged release | Yes |
| Archived branches | No |

## Reporting a Vulnerability

Please do not open public issues for security problems.

Report privately with:

- affected component
- reproduction steps
- impact
- any evidence of learner-data exposure

Use the maintainer contact listed on the GitHub profile:
[NkgoloL](https://github.com/NkgoloL)

## Verified Controls on Current Master

- Access tokens default to **15 minutes**.
- Refresh tokens default to **7 days**.
- JWT revocation uses Redis-backed token and user invalidation checks.
- RBAC exists across student, parent, teacher, and admin roles.
- Production settings can source secrets from Azure Key Vault.
- Sensitive workflow auditing is routed through the V2 append-only PostgreSQL
  audit repository.
- Security-header middleware is present in the active runtime.
- CI workflow definitions include `pip-audit`, `Bandit`, `npm audit`, image
  scanning, and `gitleaks`.

These items reflect repository code and workflow configuration that is present
today. They do not, by themselves, guarantee that every deployment target or
release tag has already been operationally verified.

## POPIA-Sensitive Areas

We treat the following as highest risk:

- consent bypass
- learner PII leakage
- export or erasure workflow failures
- audit tampering
- direct LLM exposure of real identifiers
- auth or session escalation across roles

## Current Security Notes

- Redis is part of the active security/runtime story, but not as the primary
  audit ledger. It is used for token revocation, cache, and background job
  status.
- The V2 audit path is PostgreSQL-backed and append-only at the repository
  layer.
- Legacy compatibility shims still exist in the repository. They should be
  treated as migration support, not as the preferred implementation surface.

## Operational Checks We Still Expect

Before merging security-sensitive work:

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

## Known Follow-Up Work

The following areas should continue to be tracked explicitly rather than
assumed complete forever:

- confirm production environment values match the documented JWT and cookie
  policy
- keep CI security scans green as dependencies and workflows change
- continue retiring the remaining legacy compatibility surface
- validate release and production-promotion steps against the current Docker and
  Kubernetes assets

See the root [`TODO.md`](/TODO.md) for the audit-driven tracker that captures
those follow-ups.
