from __future__ import annotations

from scripts.staging_smoke_evidence_acceptance import _has_placeholder, _valid_staging_url, write_status


def test_placeholder_detection_rejects_unsafe_values():
    assert _has_placeholder("https://example.com")
    assert _has_placeholder("http://localhost:8000")
    assert _has_placeholder("<staging-url>")
    assert _has_placeholder("REAL_RUN_ID")


def test_valid_staging_url_requires_real_https_url():
    assert _valid_staging_url("https://staging.eduboost.example.org")
    assert not _valid_staging_url("http://staging.eduboost.example.org")
    assert not _valid_staging_url("https://example.com")
    assert not _valid_staging_url("http://localhost:8000")
    assert not _valid_staging_url("<url>")


def test_staging_smoke_status_writes_files_when_evidence_present_or_reports_blockers():
    status = write_status()
    assert status.status in {
        "staging-smoke-evidence-accepted",
        "staging-smoke-evidence-not-accepted",
    }


def test_makefile_contains_staging_smoke_targets():
    source = open("Makefile", encoding="utf-8").read()
    assert "staging-smoke-evidence-status:" in source
    assert "staging-smoke-evidence-check:" in source
    assert "backend-implementation-2911-2950-full-check:" in source
