"""Documentation contract tests for PR-002R evidence artifacts."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.integration

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


@pytest.mark.unit
def test_pr002r_evidence_doc_records_runtime_and_scope() -> None:
    content = _read("docs/pr/PR-002R_BACKEND_RUNTIME_API_CONTRACT.md")

    assert "app.api_v2:app" in content
    assert "master" in content
    assert "Merge pull request #52" in content
    assert "Explicit Non-Scope" in content


@pytest.mark.unit
def test_error_contract_documents_canonical_envelope() -> None:
    content = _read("docs/error_contract.md")

    assert '"data": null' in content
    assert '"error"' in content
    assert '"meta"' in content
    assert "validation_error" in content
    assert "internal_error" in content


@pytest.mark.unit
def test_api_versioning_policy_rejects_v1_growth() -> None:
    content = _read("docs/api_versioning_policy.md")

    assert "v2" in content
    assert "New V1 routes are forbidden" in content
    assert "make openapi-check" in content


@pytest.mark.unit
def test_route_inventory_records_legacy_exclusion() -> None:
    content = _read("docs/route_inventory.md")

    assert "/api/v2" in content
    assert "/v2" in content
    assert "/system" in content
    assert "/api/v1/lessons/generate" in content
    assert "must not be part of the canonical" in content


@pytest.mark.unit
def test_project_status_does_not_claim_production_ready() -> None:
    content = _read("docs/project_status.md")

    assert "production-readiness implementation phase" in content
    assert "Do not describe the repository as production-ready" in content
    assert "Remaining Release Blockers" in content


@pytest.mark.unit
def test_pr_integration_summary_links_pr002r_evidence() -> None:
    content = _read("audits/reports/PR_INTEGRATION_SUMMARY.md")

    assert "PR-002R" in content
    assert "docs/pr/PR-002R_BACKEND_RUNTIME_API_CONTRACT.md" in content
    assert "tests/unit/test_pr002r_docs_contract.py" in content
