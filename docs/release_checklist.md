# Release Checklist

This checklist must be completed and verified before every tagged release (e.g., `v0.1.0-beta`).

## 1. Quality Assurance
- [ ] All unit tests pass (`pytest tests/`).
- [ ] Backend coverage is ≥ 80%.
- [ ] All integration tests pass.
- [ ] Manual smoke test of core flows (Signup, Lesson Generation, Diagnostics) performed in Staging.
- [ ] No critical linting errors.

## 2. Security & Compliance
- [ ] Security scan performed (e.g., Bandit, Safety).
- [ ] POPIA audit logs verified for sensitive operations.
- [ ] No secrets or PII leaked in logs.
- [ ] Dependencies audited for known vulnerabilities.

## 3. Database & Migrations
- [ ] All migrations verified on a staging database.
- [ ] Rollback plan documented for every destructive migration.
- [ ] DB performance check (slow queries) performed.

## 4. Evidence Bundle
- [ ] Image digests captured for all production containers.
- [ ] Migration revision (Alembic) recorded.
- [ ] Changelog updated.
- [ ] SBOM (Software Bill of Materials) generated.
- [ ] Test reports attached to the release tag.
- [ ] Deployment manifests (K8s/Docker) verified.

## 5. Stakeholder Approval
- [ ] Curriculum team approved lesson content quality.
- [ ] Legal/Compliance team approved privacy notice changes.
- [ ] Product owner signed off on launch scope.
