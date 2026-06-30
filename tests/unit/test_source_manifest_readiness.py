from __future__ import annotations

from pathlib import Path

import pytest

from app.services.content_scope_registry import ContentScopeRegistry
from scripts.curriculum.report_content_coverage import build_report
from scripts.curriculum.validate_scope_content import validate_scope
from scripts.curriculum.validate_source_manifest import generation_ready, validate_source_manifest


pytestmark = pytest.mark.unit


def test_source_manifest_validates_hashes_and_scope_links() -> None:
    result = validate_source_manifest()

    assert result.passed is True
    assert len(result.generation_ready_scope_ids) == 51
    assert result.generation_ready_scope_ids[0] == "grade1_coding_and_robotics_en"
    assert result.generation_ready_scope_ids[-1] == "grader_sepedi_first_additional_language_en"
    assert result.errors == []


def test_every_registered_scope_references_known_source_documents() -> None:
    registry = ContentScopeRegistry()
    result = validate_source_manifest(registry=registry)

    assert result.passed is True
    for scope in registry.list_scopes():
        assert scope.source_documents, scope.scope_id


def test_generation_ready_can_precede_learner_visibility() -> None:
    registry = ContentScopeRegistry()

    assert generation_ready("grade4_mathematics_en", registry=registry) is True
    assert generation_ready("grade4_natural_sciences_and_technology_en", registry=registry) is True
    assert registry.get_scope("grade4_natural_sciences_and_technology_en").status.value == "review"
    assert "grade4_natural_sciences_and_technology_en" not in {
        scope.scope_id for scope in registry.list_active_scopes()
    }
    assert generation_ready("grade5_mathematics_en", registry=registry) is True
    assert generation_ready("grade1_home_language_en", registry=registry) is True


def test_scope_validator_requires_source_readiness_for_active_scope() -> None:
    result = validate_scope("grade4_mathematics_en", strict=True)

    assert result.passed is True
    assert result.skipped is False


def test_coverage_report_exposes_generation_readiness_separately_from_visibility() -> None:
    report = build_report(strict_counts=True)

    assert report["summary"]["scopes.generation_ready"] == 51
    grade4 = next(row for row in report["scopes"] if row["scope_id"] == "grade4_mathematics_en")
    nst = next(row for row in report["scopes"] if row["scope_id"] == "grade4_natural_sciences_and_technology_en")
    grade5 = next(row for row in report["scopes"] if row["scope_id"] == "grade5_mathematics_en")
    assert grade4["learner_visible"] is True
    assert grade4["generation_ready"] is True
    assert nst["learner_visible"] is False
    assert nst["generation_ready"] is True
    assert nst["status"] == "review"
    assert grade5["learner_visible"] is False
    assert grade5["generation_ready"] is True
    assert grade5["status"] == "review"

def test_source_manifest_can_validate_clean_checkout_without_local_raw_files() -> None:
    result = validate_source_manifest(verify_local_files=False)

    assert result.passed is True


def test_source_manifest_local_file_verification_passes_on_vm_sources() -> None:
    if not Path("data/caps/source_documents/raw").exists():
        pytest.skip("ignored local CAPS PDF cache is not present in clean checkout")

    result = validate_source_manifest(verify_local_files=True)

    assert result.passed is True
