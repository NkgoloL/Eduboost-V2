#!/usr/bin/env python3
"""Validate production-readiness item 12: CI/CD, infrastructure, deployment, Docker, and environments."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.modules.deployment.production_readiness_contracts import default_deployment_readiness_report


REQUIRED_FILES = (
    "app/modules/deployment/__init__.py",
    "app/modules/deployment/production_readiness_contracts.py",
    "docs/adr/ADR-012-ci-cd-infrastructure-deployment.md",
    "docs/deployment/production_deployment_architecture_contract.md",
    "docs/deployment/ci_pipeline_contract.md",
    "docs/deployment/docker_runtime_hardening_contract.md",
    "docs/deployment/environment_configuration_contract.md",
    "docs/deployment/deployment_gate_and_rollback_contract.md",
    "docs/deployment/artifact_provenance_and_release_contract.md",
    "docs/backlog/production_readiness/12_ci_cd_infrastructure_deployment_docker_and_environments.md",
    "tests/unit/test_ci_cd_deployment_production_readiness.py",
)

CONTENT_REQUIREMENTS = {
    "app/modules/deployment/production_readiness_contracts.py": (
        "class EnvironmentName",
        "class PipelineStage",
        "class DeploymentStrategy",
        "class RuntimeRole",
        "InfrastructureProviderDecision",
        "PipelineCheck",
        "DockerImageContract",
        "EnvironmentContract",
        "DeploymentGate",
        "RollbackContract",
        "ArtifactProvenance",
        "looks_like_secret_name",
        "validate_env_manifest",
        "build_artifact_digest",
        "default_deployment_readiness_report",
    ),
    "docs/adr/ADR-012-ci-cd-infrastructure-deployment.md": (
        "CI/CD, Infrastructure, Deployment, Docker, and Environment Decision",
        "containerized deployment model",
        "infrastructure-as-code is required",
        "manual production approval is required",
        "container images must be scanned",
        "SBOM generation is required",
        "production secrets must be externalized",
    ),
    "docs/deployment/production_deployment_architecture_contract.md": (
        "Production Deployment Architecture Contract",
        "containerized cloud runtime",
        "infrastructure-as-code boundary",
        "separate local, test, staging, and production environments",
        "externalized secret management",
        "manual production approval gate",
        "post-deploy smoke testing",
    ),
    "docs/deployment/ci_pipeline_contract.md": (
        "CI Pipeline Contract",
        "lint",
        "typecheck",
        "unit tests",
        "integration tests",
        "security scan",
        "Docker build",
        "migration check",
        "OpenAPI drift check",
        "failed smoke tests block deployment promotion",
    ),
    "docs/deployment/docker_runtime_hardening_contract.md": (
        "Docker Runtime Hardening Contract",
        "pinned base image",
        "multi-stage build",
        "non-root user",
        "container healthcheck",
        "vulnerability scan",
        "SBOM generation",
        "no development secrets in image",
    ),
    "docs/deployment/environment_configuration_contract.md": (
        "Environment Configuration Contract",
        "DATABASE_URL",
        "REDIS_URL",
        "APP_SECRET_KEY",
        "SENTRY_DSN",
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "production debug must be disabled",
        "placeholder secrets are prohibited",
    ),
    "docs/deployment/deployment_gate_and_rollback_contract.md": (
        "Deployment Gate and Rollback Contract",
        "Required Staging Gate",
        "Required Production Gate",
        "manual production approval",
        "rollback command is documented",
        "database rollback policy is documented",
        "previous image is retained",
        "post-rollback smoke test is required",
    ),
    "docs/deployment/artifact_provenance_and_release_contract.md": (
        "Artifact Provenance and Release Contract",
        "Git SHA",
        "image digest",
        "SBOM path",
        "vulnerability scan path",
        "OpenAPI artifact path",
        "manual production approval evidence is retained",
    ),
    "docs/backlog/production_readiness/12_ci_cd_infrastructure_deployment_docker_and_environments.md": (
        "12.6 Repository-side implementation evidence",
        "docs/deployment/production_deployment_architecture_contract.md",
        "scripts/check_ci_cd_deployment_production_readiness.py",
        "make ci-cd-deployment-production-readiness-check",
    ),
    "Makefile": (
        "ci-cd-deployment-production-readiness-check:",
        "scripts/check_ci_cd_deployment_production_readiness.py",
    ),
}


@dataclass(frozen=True)
class DeploymentReadinessResult:
    target: str
    ok: bool
    detail: str


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def run_checks() -> list[DeploymentReadinessResult]:
    results: list[DeploymentReadinessResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(
            DeploymentReadinessResult(
                rel_path,
                path.exists(),
                "file present" if path.exists() else "file missing",
            )
        )

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        text = _read(rel_path)
        for snippet in snippets:
            results.append(
                DeploymentReadinessResult(
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    try:
        report = default_deployment_readiness_report()
        results.extend(
            [
                DeploymentReadinessResult("deployment_contracts", report["provider_decision_issues"] == [], "provider decision validates"),
                DeploymentReadinessResult("deployment_contracts", report["pipeline_check_issues"] == [], "pipeline checks validate"),
                DeploymentReadinessResult("deployment_contracts", report["docker_image_issues"] == [], "Docker image contracts validate"),
                DeploymentReadinessResult("deployment_contracts", report["environment_issues"] == [], "environment contracts validate"),
                DeploymentReadinessResult("deployment_contracts", report["deployment_gate_issues"] == [], "deployment gates validate"),
                DeploymentReadinessResult("deployment_contracts", report["rollback_issues"] == [], "rollback contracts validate"),
                DeploymentReadinessResult("deployment_contracts", report["provenance_issues"] == [], "artifact provenance validates"),
                DeploymentReadinessResult("deployment_contracts", report["staging_manifest_issues"] == [], "staging env manifest sample validates"),
                DeploymentReadinessResult("deployment_contracts", report["production_manifest_issues"] == [], "production env manifest sample validates"),
                DeploymentReadinessResult("deployment_contracts", str(report["artifact_digest_sample"]).startswith("sha256:"), "artifact digest sample passes"),
            ]
        )
    except Exception as exc:  # pragma: no cover - defensive CLI output
        results.append(DeploymentReadinessResult("deployment_contracts", False, f"contract check failed: {exc}"))

    return results


def main() -> int:
    results = run_checks()
    print("CI/CD deployment production readiness check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
