# 12. CI/CD, infrastructure, deployment, Docker, and environments

## 12.1 CI correctness

- [verify] `P0` Fix CI branch assumptions to support `master`.
- [verify] `P0` Ensure image scan runs on `master`.
- [verify] `P0` Ensure production gates run for release tags from `master`.
- [verify] `P0` Ensure CI uses same dependency files as local dev.
- [verify] `P0` Ensure backend lint runs.
- [verify] `P0` Ensure backend type check runs.
- [verify] `P0` Ensure backend unit tests run.
- [verify] `P0` Ensure backend integration tests run.
- [verify] `P0` Ensure Alembic migration check runs.
- [verify] `P0` Ensure POPIA tests run.
- [x] `P0` Ensure frontend tests run. Evidence: `docs/frontend/frontend_verification_evidence_2026-05-11.md`.
- [x] `P0` Ensure frontend type check runs. Evidence: `docs/frontend/frontend_verification_evidence_2026-05-11.md`.
- [x] `P0` Ensure frontend build runs. Evidence: `docs/frontend/frontend_verification_evidence_2026-05-11.md`.
- [x] `P0` Ensure Playwright E2E runs. Evidence: `docs/frontend/frontend_verification_evidence_2026-05-11.md`.
- [verify] `P0` Ensure Docker image scan runs.
- [verify] `P0` Ensure dependency audit runs.
- [verify] `P0` Ensure secret scan runs.
- [verify] `P0` Ensure staging smoke tests run before production promotion.
- [verify] `P1` Add workflow concurrency to cancel stale runs.
- [verify] `P1` Upload backend test reports.
- [verify] `P1` Upload frontend test reports.
- [verify] `P1` Upload coverage reports.
- [verify] `P1` Upload security scan reports.
- [verify] `P1` Upload OpenAPI diff artifact.
- [verify] `P1` Upload SBOM artifact.

## 12.2 Deployment target alignment

- [verify] `P0` Decide production deployment target.
- [verify] `P0` Reconcile Azure Container Apps docs with Kubernetes deployment commands.
- [verify] `P0` If ACA is target, remove or archive Kubernetes production deployment from CI.
- [verify] `P0` If AKS is target, update architecture docs to say AKS.
- [verify] `P0` Align Docker Compose with chosen target.
- [verify] `P0` Align Bicep with chosen target.
- [verify] `P0` Align Kubernetes manifests with chosen target or mark future-only.
- [verify] `P0` Align runbooks with chosen target.
- [verify] `P1` Add staging deployment workflow.
- [verify] `P1` Add production promotion workflow.
- [verify] `P1` Add deployment rollback workflow.
- [verify] `P2` Add blue-green deployment.
- [verify] `P2` Add canary deployment.
- [verify] `P2` Add automated rollback on failed health checks.

## 12.3 Docker and images

- [verify] `P0` Verify API Dockerfile builds from clean checkout.
- [verify] `P0` Verify frontend Dockerfile builds from clean checkout.
- [verify] `P0` Verify docs Dockerfile target builds from clean checkout.
- [verify] `P0` Align CI build paths with Dockerfile names.
- [verify] `P0` Run images as non-root.
- [verify] `P0` Pin base images.
- [verify] `P0` Minimize runtime layers.
- [verify] `P0` Add healthcheck to API image.
- [verify] `P0` Add healthcheck to frontend image if applicable.
- [verify] `P1` Remove build tools from runtime image.
- [verify] `P1` Add OCI image label for commit SHA.
- [verify] `P1` Add OCI image label for version.
- [verify] `P1` Add OCI image label for build time.
- [verify] `P1` Add OCI image label for source repo.
- [verify] `P1` Add OCI image label for license.
- [verify] `P1` Generate SBOM.
- [verify] `P1` Scan SBOM.
- [verify] `P2` Add image signing.

## 12.4 Environment management

- [verify] `P0` Define local environment.
- [verify] `P0` Define test environment.
- [verify] `P0` Define staging environment.
- [verify] `P0` Define production environment.
- [verify] `P0` Add `docs/environment_variables.md`.
- [verify] `P0` Document every env var name.
- [verify] `P0` Document whether each env var is required.
- [verify] `P0` Document default value if any.
- [verify] `P0` Document environment scope.
- [verify] `P0` Document sensitivity.
- [verify] `P0` Document example value.
- [verify] `P0` Validate required env vars at startup.
- [verify] `P0` Fail fast on missing production secrets.
- [verify] `P0` Store production secrets in Azure Key Vault or equivalent.
- [verify] `P1` Add secret rotation procedure.
- [verify] `P1` Add environment drift detection.
- [verify] `P1` Add staging env validation.
- [verify] `P1` Add production env validation.

## 12.5 Staging

- [verify] `P0` Provision staging environment.
- [verify] `P0` Configure staging database.
- [verify] `P0` Configure staging Redis.
- [verify] `P0` Configure staging secrets.
- [verify] `P0` Configure staging frontend.
- [verify] `P0` Configure staging API.
- [verify] `P0` Use synthetic data only in staging.
- [verify] `P0` Run smoke tests against staging.
- [verify] `P0` Run Playwright against staging.
- [verify] `P0` Run POPIA tests against staging-safe data.
- [verify] `P0` Run backup/restore drill against staging.
- [verify] `P0` Run security scan against staging.
- [verify] `P1` Run load smoke test against staging.
- [verify] `P0` Produce staging acceptance report.

---



## 12.6 Repository-side implementation evidence

- [verify] CI/CD and deployment decision is documented in `docs/adr/ADR-012-ci-cd-infrastructure-deployment.md`.
- [verify] Deployment architecture is documented in `docs/deployment/production_deployment_architecture_contract.md`.
- [verify] CI pipeline requirements are documented in `docs/deployment/ci_pipeline_contract.md`.
- [verify] Docker runtime hardening is documented in `docs/deployment/docker_runtime_hardening_contract.md`.
- [verify] Environment configuration and secret handling are documented in `docs/deployment/environment_configuration_contract.md`.
- [verify] Deployment gates and rollback controls are documented in `docs/deployment/deployment_gate_and_rollback_contract.md`.
- [verify] Artifact provenance and release evidence are documented in `docs/deployment/artifact_provenance_and_release_contract.md`.
- [verify] Deterministic repository contracts live in `app/modules/deployment/production_readiness_contracts.py`.
- [verify] Repository validation is provided by `scripts/check_ci_cd_deployment_production_readiness.py`.
- [verify] Domain validation wrapper is provided by `scripts/check_domain_12_ci_cd_deployment_evidence.py`.
- [verify] Unit coverage is provided by `tests/unit/test_ci_cd_deployment_production_readiness.py`.
- [verify] Make target is `make ci-cd-deployment-production-readiness-check`.

### Verification boundary

This implementation provides repository-side CI/CD, infrastructure, Docker, deployment, environment, rollback, and artifact-provenance readiness evidence. It does not provision infrastructure, configure live secrets, build container images, push artifacts, deploy workloads, or authorize production launch.
