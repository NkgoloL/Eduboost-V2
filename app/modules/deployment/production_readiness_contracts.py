"""Repository-verifiable CI/CD, infrastructure, deployment, Docker, and environment contracts.

These contracts are deterministic and do not call cloud providers, registries, or
deployment targets. They model release pipeline requirements, container hardening,
environment separation, deployment strategy, rollback controls, secret handling,
artifact provenance, and production-launch gates.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import re
from typing import Mapping


class EnvironmentName(str, Enum):
    LOCAL = "local"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class PipelineStage(str, Enum):
    LINT = "lint"
    TYPECHECK = "typecheck"
    UNIT_TEST = "unit_test"
    INTEGRATION_TEST = "integration_test"
    SECURITY_SCAN = "security_scan"
    BUILD = "build"
    MIGRATION_CHECK = "migration_check"
    SMOKE_TEST = "smoke_test"
    DEPLOY = "deploy"
    ROLLBACK = "rollback"


class DeploymentStrategy(str, Enum):
    MANUAL_APPROVAL = "manual_approval"
    BLUE_GREEN = "blue_green"
    ROLLING = "rolling"
    CANARY = "canary"
    FEATURE_FLAG = "feature_flag"


class RuntimeRole(str, Enum):
    API = "api"
    WORKER = "worker"
    FRONTEND = "frontend"
    MIGRATION = "migration"
    SCHEDULER = "scheduler"


REQUIRED_ENV_VARS = {
    EnvironmentName.STAGING: (
        "DATABASE_URL",
        "REDIS_URL",
        "APP_SECRET_KEY",
        "CORS_ORIGINS",
        "ENVIRONMENT",
        "LOG_LEVEL",
    ),
    EnvironmentName.PRODUCTION: (
        "DATABASE_URL",
        "REDIS_URL",
        "APP_SECRET_KEY",
        "CORS_ORIGINS",
        "ENVIRONMENT",
        "LOG_LEVEL",
        "SENTRY_DSN",
        "OTEL_EXPORTER_OTLP_ENDPOINT",
    ),
}

SECRET_NAME_PATTERNS = (
    re.compile(r".*SECRET.*", re.IGNORECASE),
    re.compile(r".*TOKEN.*", re.IGNORECASE),
    re.compile(r".*PASSWORD.*", re.IGNORECASE),
    re.compile(r".*PRIVATE_KEY.*", re.IGNORECASE),
    re.compile(r".*DATABASE_URL.*", re.IGNORECASE),
    re.compile(r".*REDIS_URL.*", re.IGNORECASE),
    re.compile(r".*DSN.*", re.IGNORECASE),
    re.compile(r".*OTEL_EXPORTER_OTLP_ENDPOINT.*", re.IGNORECASE),
)


@dataclass(frozen=True)
class InfrastructureProviderDecision:
    provider: str
    container_registry: str
    deployment_platform: str
    adr_path: str
    architecture_doc_path: str
    infrastructure_as_code_required: bool
    manual_production_approval_required: bool
    environment_separation_required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.provider:
            issues.append("infrastructure provider is required")
        if not self.container_registry:
            issues.append("container registry is required")
        if not self.deployment_platform:
            issues.append("deployment platform is required")
        if not self.adr_path.startswith("docs/adr/"):
            issues.append("infrastructure decision must be documented in docs/adr/")
        if not self.architecture_doc_path.startswith("docs/deployment/"):
            issues.append("deployment architecture must be documented in docs/deployment/")
        if not self.infrastructure_as_code_required:
            issues.append("infrastructure-as-code is required")
        if not self.manual_production_approval_required:
            issues.append("manual production approval is required")
        if not self.environment_separation_required:
            issues.append("environment separation is required")
        return issues


@dataclass(frozen=True)
class PipelineCheck:
    stage: PipelineStage
    command: str
    required_for_pr: bool
    required_for_staging: bool
    required_for_production: bool
    produces_artifact: bool
    blocks_deploy: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.command:
            issues.append(f"{self.stage.value} command is required")
        if self.required_for_production and not self.blocks_deploy:
            issues.append(f"{self.stage.value} production check must block deploy")
        if self.stage == PipelineStage.SECURITY_SCAN and not self.required_for_pr:
            issues.append("security scan must run for PRs")
        if self.stage == PipelineStage.MIGRATION_CHECK and not self.required_for_staging:
            issues.append("migration check must run before staging")
        return issues


@dataclass(frozen=True)
class DockerImageContract:
    runtime_role: RuntimeRole
    dockerfile_path: str
    non_root_user_required: bool
    pinned_base_image_required: bool
    healthcheck_required: bool
    multi_stage_build_required: bool
    dependency_lockfile_required: bool
    vulnerability_scan_required: bool
    sbom_required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.dockerfile_path:
            issues.append("dockerfile path is required")
        if not self.non_root_user_required:
            issues.append("container must run as non-root user")
        if not self.pinned_base_image_required:
            issues.append("base image pinning is required")
        if not self.healthcheck_required:
            issues.append("container healthcheck is required")
        if not self.multi_stage_build_required:
            issues.append("multi-stage build is required")
        if not self.dependency_lockfile_required:
            issues.append("dependency lockfile is required")
        if not self.vulnerability_scan_required:
            issues.append("container vulnerability scan is required")
        if not self.sbom_required:
            issues.append("SBOM generation is required")
        return issues


@dataclass(frozen=True)
class EnvironmentContract:
    environment: EnvironmentName
    required_variables: tuple[str, ...]
    forbidden_variables: tuple[str, ...]
    secrets_externalized: bool
    debug_disabled: bool
    uses_tls: bool
    database_migrations_controlled: bool
    observability_enabled: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        expected = REQUIRED_ENV_VARS.get(self.environment, ())
        for variable in expected:
            if variable not in self.required_variables:
                issues.append(f"{self.environment.value} missing required variable {variable}")
        if not self.secrets_externalized:
            issues.append(f"{self.environment.value} secrets must be externalized")
        if self.environment == EnvironmentName.PRODUCTION and not self.debug_disabled:
            issues.append("production debug must be disabled")
        if self.environment == EnvironmentName.PRODUCTION and not self.uses_tls:
            issues.append("production TLS is required")
        if not self.database_migrations_controlled:
            issues.append("database migrations must be controlled")
        if self.environment in {EnvironmentName.STAGING, EnvironmentName.PRODUCTION} and not self.observability_enabled:
            issues.append(f"{self.environment.value} observability is required")
        for variable in self.forbidden_variables:
            if variable in self.required_variables:
                issues.append(f"forbidden variable {variable} cannot be required")
        return issues


@dataclass(frozen=True)
class DeploymentGate:
    name: str
    environment: EnvironmentName
    strategy: DeploymentStrategy
    required_checks: tuple[PipelineStage, ...]
    manual_approval_required: bool
    rollback_plan_required: bool
    smoke_test_required: bool
    release_notes_required: bool
    owner: str

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.name:
            issues.append("deployment gate name is required")
        if not self.required_checks:
            issues.append("deployment gate requires checks")
        if self.environment == EnvironmentName.PRODUCTION and not self.manual_approval_required:
            issues.append("production deployment gate requires manual approval")
        if self.environment == EnvironmentName.PRODUCTION and self.strategy != DeploymentStrategy.MANUAL_APPROVAL:
            issues.append("production strategy must preserve manual approval")
        if not self.rollback_plan_required:
            issues.append("rollback plan is required")
        if not self.smoke_test_required:
            issues.append("smoke test is required")
        if not self.release_notes_required:
            issues.append("release notes are required")
        if not self.owner:
            issues.append("deployment gate owner is required")
        return issues


@dataclass(frozen=True)
class RollbackContract:
    environment: EnvironmentName
    rollback_command_documented: bool
    database_rollback_policy_documented: bool
    feature_flag_rollback_supported: bool
    previous_image_retained: bool
    smoke_test_after_rollback_required: bool
    incident_record_required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.rollback_command_documented:
            issues.append("rollback command must be documented")
        if not self.database_rollback_policy_documented:
            issues.append("database rollback policy must be documented")
        if not self.feature_flag_rollback_supported:
            issues.append("feature flag rollback support is required")
        if not self.previous_image_retained:
            issues.append("previous image must be retained")
        if not self.smoke_test_after_rollback_required:
            issues.append("post-rollback smoke test is required")
        if not self.incident_record_required:
            issues.append("rollback incident record is required")
        return issues


@dataclass(frozen=True)
class ArtifactProvenance:
    git_sha: str
    image_digest: str
    sbom_path: str
    build_log_path: str
    vulnerability_scan_path: str
    openapi_artifact_path: str
    generated_at_utc: str

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not re.fullmatch(r"[a-f0-9]{7,40}", self.git_sha):
            issues.append("git_sha must be lowercase hex")
        if not self.image_digest.startswith("sha256:"):
            issues.append("image_digest must be sha256")
        for name, value in {
            "sbom_path": self.sbom_path,
            "build_log_path": self.build_log_path,
            "vulnerability_scan_path": self.vulnerability_scan_path,
            "openapi_artifact_path": self.openapi_artifact_path,
        }.items():
            if not value:
                issues.append(f"{name} is required")
        if not self.generated_at_utc:
            issues.append("generated_at_utc is required")
        return issues


def looks_like_secret_name(name: str) -> bool:
    """Return whether an environment variable name should be treated as secret-bearing."""

    return any(pattern.fullmatch(name or "") for pattern in SECRET_NAME_PATTERNS)


def validate_env_manifest(environment: EnvironmentName, manifest: Mapping[str, str]) -> list[str]:
    """Validate required env-var presence without inspecting secret values."""

    issues: list[str] = []
    for variable in REQUIRED_ENV_VARS.get(environment, ()):
        if variable not in manifest:
            issues.append(f"missing required environment variable {variable}")
    for key, value in manifest.items():
        if looks_like_secret_name(key) and value in {"", "changeme", "placeholder", "secret", "password"}:
            issues.append(f"secret-like variable {key} has placeholder value")
    if environment == EnvironmentName.PRODUCTION and manifest.get("ENVIRONMENT") != "production":
        issues.append("production manifest must set ENVIRONMENT=production")
    return issues


def build_artifact_digest(parts: tuple[str, ...]) -> str:
    """Build deterministic artifact digest for provenance records."""

    return "sha256:" + hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


DEFAULT_PROVIDER_DECISION = InfrastructureProviderDecision(
    provider="containerized_cloud_runtime",
    container_registry="github_container_registry_or_managed_registry",
    deployment_platform="managed_container_platform",
    adr_path="docs/adr/ADR-012-ci-cd-infrastructure-deployment.md",
    architecture_doc_path="docs/deployment/production_deployment_architecture_contract.md",
    infrastructure_as_code_required=True,
    manual_production_approval_required=True,
    environment_separation_required=True,
)

DEFAULT_PIPELINE_CHECKS = (
    PipelineCheck(PipelineStage.LINT, "make lint", True, True, True, False, True),
    PipelineCheck(PipelineStage.TYPECHECK, "make typecheck", True, True, True, False, True),
    PipelineCheck(PipelineStage.UNIT_TEST, "pytest -c pytest.ini -q", True, True, True, False, True),
    PipelineCheck(PipelineStage.INTEGRATION_TEST, "make integration-test", True, True, True, False, True),
    PipelineCheck(PipelineStage.SECURITY_SCAN, "make security-scan", True, True, True, True, True),
    PipelineCheck(PipelineStage.BUILD, "make docker-build", True, True, True, True, True),
    PipelineCheck(PipelineStage.MIGRATION_CHECK, "make migration-check", True, True, True, False, True),
    PipelineCheck(PipelineStage.SMOKE_TEST, "make staging-smoke", False, True, True, True, True),
)

DEFAULT_DOCKER_IMAGES = (
    DockerImageContract(RuntimeRole.API, "Dockerfile", True, True, True, True, True, True, True),
    DockerImageContract(RuntimeRole.WORKER, "Dockerfile.worker", True, True, True, True, True, True, True),
    DockerImageContract(RuntimeRole.FRONTEND, "app/frontend/Dockerfile", True, True, True, True, True, True, True),
)

DEFAULT_ENVIRONMENTS = (
    EnvironmentContract(
        EnvironmentName.STAGING,
        REQUIRED_ENV_VARS[EnvironmentName.STAGING],
        ("DEBUG", "LOCAL_ONLY"),
        True,
        True,
        True,
        True,
        True,
    ),
    EnvironmentContract(
        EnvironmentName.PRODUCTION,
        REQUIRED_ENV_VARS[EnvironmentName.PRODUCTION],
        ("DEBUG", "LOCAL_ONLY", "TESTING"),
        True,
        True,
        True,
        True,
        True,
    ),
)

DEFAULT_DEPLOYMENT_GATES = (
    DeploymentGate(
        "staging-deploy",
        EnvironmentName.STAGING,
        DeploymentStrategy.ROLLING,
        (
            PipelineStage.LINT,
            PipelineStage.UNIT_TEST,
            PipelineStage.SECURITY_SCAN,
            PipelineStage.BUILD,
            PipelineStage.MIGRATION_CHECK,
            PipelineStage.SMOKE_TEST,
        ),
        manual_approval_required=False,
        rollback_plan_required=True,
        smoke_test_required=True,
        release_notes_required=True,
        owner="release-owner",
    ),
    DeploymentGate(
        "production-deploy",
        EnvironmentName.PRODUCTION,
        DeploymentStrategy.MANUAL_APPROVAL,
        (
            PipelineStage.LINT,
            PipelineStage.TYPECHECK,
            PipelineStage.UNIT_TEST,
            PipelineStage.INTEGRATION_TEST,
            PipelineStage.SECURITY_SCAN,
            PipelineStage.BUILD,
            PipelineStage.MIGRATION_CHECK,
            PipelineStage.SMOKE_TEST,
        ),
        manual_approval_required=True,
        rollback_plan_required=True,
        smoke_test_required=True,
        release_notes_required=True,
        owner="release-owner",
    ),
)

DEFAULT_ROLLBACKS = (
    RollbackContract(EnvironmentName.STAGING, True, True, True, True, True, True),
    RollbackContract(EnvironmentName.PRODUCTION, True, True, True, True, True, True),
)

DEFAULT_PROVENANCE = ArtifactProvenance(
    git_sha="abcdef1234567890",
    image_digest=build_artifact_digest(("abcdef1234567890", "api", "production")),
    sbom_path="artifacts/sbom/api.spdx.json",
    build_log_path="artifacts/build/api.log",
    vulnerability_scan_path="artifacts/security/api-vulnerability-scan.json",
    openapi_artifact_path="docs/openapi.json",
    generated_at_utc="2026-01-01T00:00:00Z",
)


def default_deployment_readiness_report() -> dict[str, object]:
    """Return deterministic deployment readiness evidence."""

    staging_manifest = {
        "DATABASE_URL": "external-secret-ref",
        "REDIS_URL": "external-secret-ref",
        "APP_SECRET_KEY": "external-secret-ref",
        "CORS_ORIGINS": "https://staging.example.test",
        "ENVIRONMENT": "staging",
        "LOG_LEVEL": "INFO",
    }
    production_manifest = {
        "DATABASE_URL": "external-secret-ref",
        "REDIS_URL": "external-secret-ref",
        "APP_SECRET_KEY": "external-secret-ref",
        "CORS_ORIGINS": "https://app.example.test",
        "ENVIRONMENT": "production",
        "LOG_LEVEL": "INFO",
        "SENTRY_DSN": "external-secret-ref",
        "OTEL_EXPORTER_OTLP_ENDPOINT": "external-secret-ref",
    }

    return {
        "provider_decision_issues": DEFAULT_PROVIDER_DECISION.validate(),
        "pipeline_check_issues": [issue for check in DEFAULT_PIPELINE_CHECKS for issue in check.validate()],
        "docker_image_issues": [issue for image in DEFAULT_DOCKER_IMAGES for issue in image.validate()],
        "environment_issues": [issue for environment in DEFAULT_ENVIRONMENTS for issue in environment.validate()],
        "deployment_gate_issues": [issue for gate in DEFAULT_DEPLOYMENT_GATES for issue in gate.validate()],
        "rollback_issues": [issue for rollback in DEFAULT_ROLLBACKS for issue in rollback.validate()],
        "provenance_issues": DEFAULT_PROVENANCE.validate(),
        "staging_manifest_issues": validate_env_manifest(EnvironmentName.STAGING, staging_manifest),
        "production_manifest_issues": validate_env_manifest(EnvironmentName.PRODUCTION, production_manifest),
        "artifact_digest_sample": build_artifact_digest(("abcdef1234567890", "api", "production")),
    }
