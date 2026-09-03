from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from app.modules.deployment.production_readiness_contracts import (
    DEFAULT_DEPLOYMENT_GATES,
    DEFAULT_DOCKER_IMAGES,
    DEFAULT_ENVIRONMENTS,
    DEFAULT_PIPELINE_CHECKS,
    DEFAULT_PROVIDER_DECISION,
    DEFAULT_PROVENANCE,
    DEFAULT_ROLLBACKS,
    EnvironmentName,
    build_artifact_digest,
    looks_like_secret_name,
    validate_env_manifest,
)
from scripts.check_ci_cd_deployment_production_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_ci_cd_deployment_production_readiness_passes() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_ci_cd_deployment_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_ci_cd_deployment_production_readiness.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "CI/CD deployment production readiness check" in result.stdout


@pytest.mark.unit
def test_deployment_contracts_validate() -> None:
    assert DEFAULT_PROVIDER_DECISION.validate() == []
    assert [issue for check in DEFAULT_PIPELINE_CHECKS for issue in check.validate()] == []
    assert [issue for image in DEFAULT_DOCKER_IMAGES for issue in image.validate()] == []
    assert [issue for environment in DEFAULT_ENVIRONMENTS for issue in environment.validate()] == []
    assert [issue for gate in DEFAULT_DEPLOYMENT_GATES for issue in gate.validate()] == []
    assert [issue for rollback in DEFAULT_ROLLBACKS for issue in rollback.validate()] == []
    assert DEFAULT_PROVENANCE.validate() == []


@pytest.mark.unit
def test_secret_name_and_env_manifest_validation() -> None:
    assert looks_like_secret_name("APP_SECRET_KEY")
    assert looks_like_secret_name("DATABASE_PASSWORD")
    assert looks_like_secret_name("API_TOKEN")
    assert not looks_like_secret_name("LOG_LEVEL")

    issues = validate_env_manifest(
        EnvironmentName.PRODUCTION,
        {
            "DATABASE_URL": "external-secret-ref",
            "REDIS_URL": "external-secret-ref",
            "APP_SECRET_KEY": "external-secret-ref",
            "CORS_ORIGINS": "https://app.example.test",
            "ENVIRONMENT": "production",
            "LOG_LEVEL": "INFO",
            "SENTRY_DSN": "external-secret-ref",
            "OTEL_EXPORTER_OTLP_ENDPOINT": "external-secret-ref",
        },
    )
    assert issues == []

    bad_issues = validate_env_manifest(
        EnvironmentName.PRODUCTION,
        {
            "DATABASE_URL": "placeholder",
            "ENVIRONMENT": "staging",
        },
    )
    assert "missing required environment variable REDIS_URL" in bad_issues
    assert "secret-like variable DATABASE_URL has placeholder value" in bad_issues
    assert "production manifest must set ENVIRONMENT=production" in bad_issues


@pytest.mark.unit
def test_artifact_digest_is_sha256() -> None:
    digest = build_artifact_digest(("abcdef", "api", "production"))
    assert digest.startswith("sha256:")
    assert len(digest) == len("sha256:") + 64


@pytest.mark.unit
def test_makefile_exposes_ci_cd_deployment_target() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "ci-cd-deployment-production-readiness-check:" in text
    assert "scripts/check_ci_cd_deployment_production_readiness.py" in text


@pytest.mark.unit
def test_deployment_contracts_validation_error_branches() -> None:
    from app.modules.deployment.production_readiness_contracts import (
        ArtifactProvenance,
        DeploymentGate,
        DeploymentStrategy,
        DockerImageContract,
        EnvironmentContract,
        InfrastructureProviderDecision,
        PipelineCheck,
        PipelineStage,
        RollbackContract,
        RuntimeRole,
        default_deployment_readiness_report,
    )

    # 1. InfrastructureProviderDecision invalid branches
    bad_infra = InfrastructureProviderDecision(
        provider="",
        container_registry="",
        deployment_platform="",
        adr_path="invalid/path.md",
        architecture_doc_path="invalid/doc.md",
        infrastructure_as_code_required=False,
        manual_production_approval_required=False,
        environment_separation_required=False,
    )
    infra_issues = bad_infra.validate()
    assert "infrastructure provider is required" in infra_issues
    assert "container registry is required" in infra_issues
    assert "deployment platform is required" in infra_issues
    assert "infrastructure decision must be documented in docs/adr/" in infra_issues
    assert "deployment architecture must be documented in docs/deployment/" in infra_issues
    assert "infrastructure-as-code is required" in infra_issues
    assert "manual production approval is required" in infra_issues
    assert "environment separation is required" in infra_issues

    # 2. PipelineCheck invalid branches
    bad_check = PipelineCheck(
        stage=PipelineStage.SECURITY_SCAN,
        command="",
        required_for_pr=False,
        required_for_staging=False,
        required_for_production=True,
        produces_artifact=False,
        blocks_deploy=False,
    )
    check_issues = bad_check.validate()
    assert "security_scan command is required" in check_issues
    assert "security_scan production check must block deploy" in check_issues
    assert "security scan must run for PRs" in check_issues

    bad_migration = PipelineCheck(
        stage=PipelineStage.MIGRATION_CHECK,
        command="make check",
        required_for_pr=True,
        required_for_staging=False,
        required_for_production=False,
        produces_artifact=False,
        blocks_deploy=False,
    )
    assert "migration check must run before staging" in bad_migration.validate()

    # 3. DockerImageContract invalid branches
    bad_docker = DockerImageContract(
        runtime_role=RuntimeRole.API,
        dockerfile_path="",
        non_root_user_required=False,
        pinned_base_image_required=False,
        healthcheck_required=False,
        multi_stage_build_required=False,
        dependency_lockfile_required=False,
        vulnerability_scan_required=False,
        sbom_required=False,
    )
    docker_issues = bad_docker.validate()
    assert len(docker_issues) == 8

    # 4. EnvironmentContract invalid branches
    bad_env = EnvironmentContract(
        environment=EnvironmentName.PRODUCTION,
        required_variables=(),
        forbidden_variables=("DEBUG",),
        secrets_externalized=False,
        debug_disabled=False,
        uses_tls=False,
        database_migrations_controlled=False,
        observability_enabled=False,
    )
    env_issues = bad_env.validate()
    assert "production missing required variable DATABASE_URL" in env_issues
    assert "production secrets must be externalized" in env_issues
    assert "production debug must be disabled" in env_issues
    assert "production TLS is required" in env_issues
    assert "database migrations must be controlled" in env_issues
    assert "production observability is required" in env_issues

    # Forbidden var present in required
    forbidden_env = EnvironmentContract(
        environment=EnvironmentName.STAGING,
        required_variables=("DEBUG",),
        forbidden_variables=("DEBUG",),
        secrets_externalized=True,
        debug_disabled=True,
        uses_tls=True,
        database_migrations_controlled=True,
        observability_enabled=True,
    )
    assert "forbidden variable DEBUG cannot be required" in forbidden_env.validate()

    # 5. DeploymentGate invalid branches
    bad_gate = DeploymentGate(
        name="",
        environment=EnvironmentName.PRODUCTION,
        strategy=DeploymentStrategy.ROLLING,
        required_checks=(),
        manual_approval_required=False,
        rollback_plan_required=False,
        smoke_test_required=False,
        release_notes_required=False,
        owner="",
    )
    gate_issues = bad_gate.validate()
    assert "deployment gate name is required" in gate_issues
    assert "deployment gate requires checks" in gate_issues
    assert "production deployment gate requires manual approval" in gate_issues
    assert "production strategy must preserve manual approval" in gate_issues
    assert "rollback plan is required" in gate_issues
    assert "smoke test is required" in gate_issues
    assert "release notes are required" in gate_issues
    assert "deployment gate owner is required" in gate_issues

    # 6. RollbackContract invalid branches
    bad_rollback = RollbackContract(
        environment=EnvironmentName.PRODUCTION,
        rollback_command_documented=False,
        database_rollback_policy_documented=False,
        feature_flag_rollback_supported=False,
        previous_image_retained=False,
        smoke_test_after_rollback_required=False,
        incident_record_required=False,
    )
    assert len(bad_rollback.validate()) == 6

    # 7. ArtifactProvenance invalid branches
    bad_prov = ArtifactProvenance(
        git_sha="INVALID_SHA!",
        image_digest="invalid:digest",
        sbom_path="",
        build_log_path="",
        vulnerability_scan_path="",
        openapi_artifact_path="",
        generated_at_utc="",
    )
    prov_issues = bad_prov.validate()
    assert "git_sha must be lowercase hex" in prov_issues
    assert "image_digest must be sha256" in prov_issues
    assert "sbom_path is required" in prov_issues
    assert "generated_at_utc is required" in prov_issues

    # 8. default_deployment_readiness_report
    report = default_deployment_readiness_report()
    assert report["provider_decision_issues"] == []
    assert report["pipeline_check_issues"] == []
    assert "sha256:" in str(report["artifact_digest_sample"])
