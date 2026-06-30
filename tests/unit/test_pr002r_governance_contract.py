"""Governance contract tests for PR-002R evidence and PR template."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.integration

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


@pytest.mark.unit
def test_pull_request_template_requires_api_contract_checks() -> None:
    content = _read(".github/pull_request_template.md")

    assert "Runtime/API Contract Checklist" in content
    assert "app.api_v2:app" in content
    assert "make runtime-check" in content
    assert "make openapi-check" in content
    assert "make route-inventory-check" in content
    assert "legacy routes are not exposed" in content


@pytest.mark.unit
def test_pull_request_template_requires_security_and_popia_review() -> None:
    content = _read(".github/pull_request_template.md")

    assert "Security and POPIA Checklist" in content
    assert "Object-level authorization" in content
    assert "Consent gates" in content
    assert "learner/guardian PII" in content
    assert "Audit events" in content


@pytest.mark.unit
def test_pr002r_release_evidence_index_links_required_artifacts() -> None:
    content = _read("docs/release/PR-002R_EVIDENCE.md")

    assert "app.api_v2:app" in content
    assert "docs/pr/PR-002R_BACKEND_RUNTIME_API_CONTRACT.md" in content
    assert "docs/openapi.json" in content
    assert "scripts/check_runtime_entrypoints.py" in content
    assert "scripts/generate_route_inventory.py" in content
    assert ".github/workflows/openapi-drift.yml" in content
    assert ".github/workflows/runtime-contract.yml" in content


@pytest.mark.unit
def test_pr002r_release_evidence_index_records_non_scope() -> None:
    content = _read("docs/release/PR-002R_EVIDENCE.md")

    assert "does not approve production or public beta use" in content
    assert "POPIA consent enforcement" in content
    assert "backup/restore proof" in content
    assert "final go/no-go review" in content
