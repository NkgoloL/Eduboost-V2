# 12. CI/CD, infrastructure, deployment, Docker, and environments

## 12.1 CI correctness

- [ ] `P0` Fix CI branch assumptions to support `master`.
- [ ] `P0` Ensure image scan runs on `master`.
- [ ] `P0` Ensure production gates run for release tags from `master`.
- [ ] `P0` Ensure CI uses same dependency files as local dev.
- [ ] `P0` Ensure backend lint runs.
- [ ] `P0` Ensure backend type check runs.
- [ ] `P0` Ensure backend unit tests run.
- [ ] `P0` Ensure backend integration tests run.
- [ ] `P0` Ensure Alembic migration check runs.
- [ ] `P0` Ensure POPIA tests run.
- [x] `P0` Ensure frontend tests run. Evidence: `docs/frontend/frontend_verification_evidence_2026-05-11.md`.
- [x] `P0` Ensure frontend type check runs. Evidence: `docs/frontend/frontend_verification_evidence_2026-05-11.md`.
- [x] `P0` Ensure frontend build runs. Evidence: `docs/frontend/frontend_verification_evidence_2026-05-11.md`.
- [x] `P0` Ensure Playwright E2E runs. Evidence: `docs/frontend/frontend_verification_evidence_2026-05-11.md`.
- [ ] `P0` Ensure Docker image scan runs.
- [ ] `P0` Ensure dependency audit runs.
- [ ] `P0` Ensure secret scan runs.
- [ ] `P0` Ensure staging smoke tests run before production promotion.
- [ ] `P1` Add workflow concurrency to cancel stale runs.
- [ ] `P1` Upload backend test reports.
- [ ] `P1` Upload frontend test reports.
- [ ] `P1` Upload coverage reports.
- [ ] `P1` Upload security scan reports.
- [ ] `P1` Upload OpenAPI diff artifact.
- [ ] `P1` Upload SBOM artifact.

## 12.2 Deployment target alignment

- [ ] `P0` Decide production deployment target.
- [ ] `P0` Reconcile Azure Container Apps docs with Kubernetes deployment commands.
- [ ] `P0` If ACA is target, remove or archive Kubernetes production deployment from CI.
- [ ] `P0` If AKS is target, update architecture docs to say AKS.
- [ ] `P0` Align Docker Compose with chosen target.
- [ ] `P0` Align Bicep with chosen target.
- [ ] `P0` Align Kubernetes manifests with chosen target or mark future-only.
- [ ] `P0` Align runbooks with chosen target.
- [ ] `P1` Add staging deployment workflow.
- [ ] `P1` Add production promotion workflow.
- [ ] `P1` Add deployment rollback workflow.
- [ ] `P2` Add blue-green deployment.
- [ ] `P2` Add canary deployment.
- [ ] `P2` Add automated rollback on failed health checks.

## 12.3 Docker and images

- [ ] `P0` Verify API Dockerfile builds from clean checkout.
- [ ] `P0` Verify frontend Dockerfile builds from clean checkout.
- [ ] `P0` Verify docs Dockerfile target builds from clean checkout.
- [ ] `P0` Align CI build paths with Dockerfile names.
- [ ] `P0` Run images as non-root.
- [ ] `P0` Pin base images.
- [ ] `P0` Minimize runtime layers.
- [ ] `P0` Add healthcheck to API image.
- [ ] `P0` Add healthcheck to frontend image if applicable.
- [ ] `P1` Remove build tools from runtime image.
- [ ] `P1` Add OCI image label for commit SHA.
- [ ] `P1` Add OCI image label for version.
- [ ] `P1` Add OCI image label for build time.
- [ ] `P1` Add OCI image label for source repo.
- [ ] `P1` Add OCI image label for license.
- [ ] `P1` Generate SBOM.
- [ ] `P1` Scan SBOM.
- [ ] `P2` Add image signing.

## 12.4 Environment management

- [ ] `P0` Define local environment.
- [ ] `P0` Define test environment.
- [ ] `P0` Define staging environment.
- [ ] `P0` Define production environment.
- [ ] `P0` Add `docs/environment_variables.md`.
- [ ] `P0` Document every env var name.
- [ ] `P0` Document whether each env var is required.
- [ ] `P0` Document default value if any.
- [ ] `P0` Document environment scope.
- [ ] `P0` Document sensitivity.
- [ ] `P0` Document example value.
- [ ] `P0` Validate required env vars at startup.
- [ ] `P0` Fail fast on missing production secrets.
- [ ] `P0` Store production secrets in Azure Key Vault or equivalent.
- [ ] `P1` Add secret rotation procedure.
- [ ] `P1` Add environment drift detection.
- [ ] `P1` Add staging env validation.
- [ ] `P1` Add production env validation.

## 12.5 Staging

- [ ] `P0` Provision staging environment.
- [ ] `P0` Configure staging database.
- [ ] `P0` Configure staging Redis.
- [ ] `P0` Configure staging secrets.
- [ ] `P0` Configure staging frontend.
- [ ] `P0` Configure staging API.
- [ ] `P0` Use synthetic data only in staging.
- [ ] `P0` Run smoke tests against staging.
- [ ] `P0` Run Playwright against staging.
- [ ] `P0` Run POPIA tests against staging-safe data.
- [ ] `P0` Run backup/restore drill against staging.
- [ ] `P0` Run security scan against staging.
- [ ] `P1` Run load smoke test against staging.
- [ ] `P0` Produce staging acceptance report.

---

