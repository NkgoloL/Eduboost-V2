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
