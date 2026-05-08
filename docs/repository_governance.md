# Repository Governance

This document defines the repository operating model for EduBoost V2. It is intentionally conservative because the product handles learner data, AI-generated educational content, curriculum alignment, and production infrastructure.

## 1. Canonical repository

The documented canonical upstream for this snapshot is:

```text
NkgoloL/Eduboost-V2
```

Any other public or private clone is treated as a mirror or working fork unless this document is updated by the repository owner.

### Canonical upstream rules

- The canonical upstream is the only source from which production releases may be tagged.
- Release notes, security advisories, deployment manifests, and provenance evidence must point back to the canonical upstream.
- Mirrors may exist for disaster recovery, vendor review, or experimentation, but they must not publish production tags independently.
- If the canonical upstream changes, update this document, `README.md`, `SECURITY.md`, deployment docs, and CI environment references in the same PR.

## 2. Mirror and fork policy

| Repository type | Allowed use | Restrictions |
|---|---|---|
| Personal fork | Feature development and review | Must merge back by PR; no production tags |
| Disaster-recovery mirror | Backup of source and release evidence | Read-only unless formally promoted |
| Vendor/private mirror | External review, legal/compliance audit, isolated testing | Must not contain secrets or learner data |
| Experimental clone | Spikes and prototypes | Must not be treated as deployment authority |

Promotion of a mirror to canonical upstream requires explicit owner approval, updated governance docs, and a signed release handover note.

## 3. Branch policy

| Branch | Purpose | Rules |
|---|---|---|
| `master` / `main` | Production-ready branch | PR-only, required checks, no force-push, no direct commits |
| `develop` | Integration branch when used | PR-only, required checks for merge readiness |
| `feature/*` | Feature development | Short-lived, issue-linked, deleted after merge |
| `hotfix/*` | Urgent production fixes | Must include incident link and rollback note |
| `spike/*` | Experiments | Not production eligible; must not introduce release artifacts |

The repository currently uses `master` in the uploaded snapshot. `main` remains supported for future rename compatibility.

## 4. Required branch protections

Configure these in GitHub repository settings for `master` and `main`:

- Require pull request before merge.
- Require at least one approval from a code owner.
- Dismiss stale approvals when new commits are pushed.
- Require required status checks to pass.
- Require branches to be up to date before merge where practical.
- Block force pushes.
- Block branch deletion.
- Require conversation resolution before merge.
- Require signed commits if feasible for all maintainers.
- Restrict who can push directly to protected branches.

Minimum required checks before production release:

- Lint and type check.
- Unit tests.
- Integration tests.
- V2 smoke tests.
- Frontend tests/build where frontend files changed.
- Schema drift check where backend/database files changed.
- POPIA/security checks where learner-data or auth flows changed.
- Secrets scan.
- Documentation build or docs link check where docs changed.

## 5. Pull request requirements

Every PR must include:

- Problem statement and scope.
- Linked issue, TODO item, ADR, incident, or release gate.
- Validation evidence: commands, logs, screenshots, or artifacts.
- POPIA/security/accessibility/deployment impact assessment.
- Migration and rollback notes where applicable.
- Reviewer focus areas.

High-risk PRs require additional review:

| Change class | Required review emphasis |
|---|---|
| Auth/session/RBAC | Security and object-level access control |
| Learner data/consent/erasure | POPIA and auditability |
| AI lesson generation/content safety | Curriculum, safety, and output validation |
| Database migrations | Rollback, integrity, and migration ordering |
| Infrastructure/secrets/deployment | Operational and rollback plan |
| Billing/payments | Security, reconciliation, and compliance |

## 6. Release authority

Only the repository owner or delegated release manager may tag releases from the canonical production branch.

Release tag format:

```text
vMAJOR.MINOR.PATCH[-beta.N]
```

Release prerequisites:

- All required CI jobs pass on the release commit.
- `docs/release_checklist.md` is satisfied or explicitly waived.
- Migration/rollback notes exist for schema changes.
- Smoke-test target environment is documented.
- Security/privacy impact has been reviewed for learner-data changes.
- Release notes describe user-visible, operational, and migration changes.

## 7. Secret rotation authority

Secrets are managed outside Git. The repository may contain examples and names only.

| Secret class | Rotation authority | Required evidence |
|---|---|---|
| JWT/signing material | Technical lead / security owner | Rotation window, affected services, verification logs |
| Database credentials | Infrastructure owner | Migration/connection verification |
| Redis/session credentials | Infrastructure owner | Session invalidation plan where needed |
| LLM/API provider keys | AI platform owner | Provider dashboard rotation evidence |
| Email/billing provider keys | Operations owner | Webhook and callback validation |
| CI/CD deployment credentials | Release manager / infrastructure owner | Failed-old-token check and successful deployment check |

Rotation events must be tracked as an issue or incident when they affect production.

## 8. Security patch process

Security patches follow a compressed review path but still require evidence.

1. Triage severity and blast radius.
2. Create a private branch or security advisory workflow if details are sensitive.
3. Patch with the smallest safe change.
4. Add regression tests or a compensating verification script.
5. Rotate secrets if exposure is plausible.
6. Release from the canonical production branch.
7. Publish advisory/release notes after mitigation, excluding sensitive exploit details.
8. Complete post-incident review for SEV1/SEV2 issues.

## 9. Archive policy

- Delete merged feature branches after merge.
- Review stale branches older than 90 days.
- Archive abandoned experiments with a short note in the issue/PR that supersedes them.
- Keep release tags, release notes, migration history, ADRs, and audit evidence permanently unless legal/compliance review says otherwise.
- Do not archive or delete records needed for POPIA, incident response, financial reconciliation, or learner-data auditability without explicit approval.

## 10. Governance change control

Changes to this document require a PR. Material changes to canonical upstream, branch protections, release authority, security reporting, or secret rotation require owner approval.
