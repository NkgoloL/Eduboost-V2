# Release Checklist

Purpose: ensure every tagged release produces an evidence bundle and is safe for promotion.

Minimum required artifacts (produce and attach to the release):
- Backend image digest and tag
- Frontend build artifact or image digest
- Alembic migration revision(s) and migration plan
- Changelog entry summarizing user-facing changes
- SBOM for backend and frontend
- Test reports: unit, integration, and e2e (Playwright)
- Coverage reports
- Security scan reports (dependency scan, container image scan)
- Secret-scan report (no secrets in artifacts)
- Deployment manifest used for the release (K8s/Bicep/Docker Compose)

Pre-release checks (must pass before tagging):
- [ ] CI checks passed: lint, typecheck, unit tests, integration tests
- [ ] Alembic check passed (no drift)
- [ ] POPIA/privacy impact assessed for data-handling changes
- [ ] OpenAPI schema generated and reviewed for breaking changes
- [ ] Release notes drafted in `CHANGELOG.md`
- [ ] Rollback plan documented for any destructive migration
- [ ] Code owner(s) approved the PR

Post-release actions:
- Tag release in git with semantic version
- Publish image(s) to registry and record digest in evidence bundle
- Upload evidence bundle to release assets
- Notify stakeholders (ops, product, compliance)
- Monitor staging/production health and alerts for 30 minutes post-deploy

Use this checklist as the minimal baseline; add project-specific steps where required.
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
