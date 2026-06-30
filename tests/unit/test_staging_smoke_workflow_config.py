from __future__ import annotations

from scripts.check_staging_smoke_workflow_config import build_status, write_status
from scripts.staging_smoke_probe import build_url, has_placeholder, normalize_path, valid_https_url


def test_staging_url_validation_rejects_placeholders():
    assert valid_https_url("https://staging.eduboost.internal")
    assert not valid_https_url("http://staging.eduboost.internal")
    assert not valid_https_url("https://example.com")
    assert not valid_https_url("http://localhost:8000")
    assert not valid_https_url("<staging-url>")


def test_staging_probe_path_normalization():
    assert normalize_path("health") == "/health"
    assert normalize_path("/health") == "/health"
    assert normalize_path("") == ""


def test_staging_probe_url_builder():
    assert build_url("https://staging.example.org", "/health") == "https://staging.example.org/health"


def test_placeholder_detection():
    assert has_placeholder("https://example.com")
    assert has_placeholder("REAL_STAGING_URL")
    assert not has_placeholder("https://staging.eduboost.internal")


def test_workflow_config_status_writes_reports():
    status = write_status()
    assert status.status in {
        "staging-smoke-workflow-configured",
        "staging-smoke-workflow-not-configured",
    }


def test_workflow_config_is_configured_after_batch_files_exist():
    status = build_status()
    assert status.workflow_exists
    assert status.probe_exists
    assert status.has_workflow_dispatch
    assert status.has_staging_base_url_secret
    assert status.has_probe_step
    assert status.has_artifact_upload
