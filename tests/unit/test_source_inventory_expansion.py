from __future__ import annotations

import pytest

from app.domain.content_source import SourceDocumentStatus
from app.services.content_scope_registry import ContentScopeRegistry
from scripts.curriculum.source_inventory import build_inventory
from scripts.curriculum.validate_source_manifest import load_manifest, validate_source_manifest


pytestmark = pytest.mark.unit


def test_sepedi_fal_replaces_generic_first_additional_language_scopes() -> None:
    registry = ContentScopeRegistry()
    scope_ids = {scope.scope_id for scope in registry.list_scopes()}

    assert "grade4_sepedi_first_additional_language_en" in scope_ids
    assert "grade7_sepedi_first_additional_language_en" in scope_ids
    assert "grade4_first_additional_language_en" not in scope_ids
    scope = registry.get_scope("grade4_sepedi_first_additional_language_en")
    assert scope.subject == "Sepedi First Additional Language"
    assert scope.subject_code == "FAL"
    assert scope.source_documents == ["caps_intermediate_sepedi_first_additional_language_en"]


def test_coding_and_robotics_review_scopes_are_registered_for_grade_r_to_7() -> None:
    registry = ContentScopeRegistry()

    for scope_id in [
        "grader_coding_and_robotics_en",
        "grade1_coding_and_robotics_en",
        "grade4_coding_and_robotics_en",
        "grade7_coding_and_robotics_en",
    ]:
        scope = registry.get_scope(scope_id)
        assert scope.status.value == "review"
        assert scope.subject == "Coding and Robotics"
        assert scope.subject_code == "CR"
        assert scope.caps_refs
        assert scope.topic_map_path


def test_source_manifest_contains_sepedi_and_coding_documents() -> None:
    manifest = load_manifest()
    documents = {document.document_id: document for document in manifest.documents}

    sepedi = documents["caps_intermediate_sepedi_first_additional_language_en"]
    assert sepedi.subjects == ["Sepedi First Additional Language"]
    assert sepedi.language_role == "first_additional_language"
    assert sepedi.language_code == "nso"

    coding = documents["caps_senior_coding_and_robotics_en"]
    assert coding.status == SourceDocumentStatus.TOPIC_MAP_APPROVED
    assert coding.subjects == ["Coding and Robotics"]
    assert coding.language_role == "content_subject"
    assert coding.source_path == "data/caps/source_documents/raw/caps_senior_coding_and_robotics_en.pdf"
    assert coding.source_sha256


def test_source_manifest_validation_passes_after_scope_expansion() -> None:
    result = validate_source_manifest()

    assert result.passed is True
    assert len(result.generation_ready_scope_ids) == 51


def test_source_inventory_reports_generation_ready_and_missing_source_gaps() -> None:
    report = build_inventory()
    rows = {row["scope_id"]: row for row in report["rows"]}

    assert report["validation_passed"] is True
    assert rows["grade4_mathematics_en"]["has_object_uri"] is True
    assert rows["grade4_mathematics_en"]["gap_reason"] == "ok"
    assert rows["grade4_mathematics_en"]["is_generation_ready"] is True
    assert rows["grade4_natural_sciences_and_technology_en"]["gap_reason"] == "ok"
    assert rows["grade4_natural_sciences_and_technology_en"]["is_generation_ready"] is True
    assert rows["grade7_coding_and_robotics_en"]["has_url"] is True
    assert rows["grade7_coding_and_robotics_en"]["has_hash"] is True
    assert rows["grade7_coding_and_robotics_en"]["has_object_uri"] is True
    assert rows["grade7_coding_and_robotics_en"]["gap_reason"] == "ok"
    assert rows["grade7_coding_and_robotics_en"]["is_generation_ready"] is True
    assert report["summary"].get("missing_canonical_source_url", 0) == 0
    assert report["summary"].get("missing_sha256", 0) == 0
    assert report["summary"].get("missing_object_store_uri", 0) == 0
    assert report["summary"].get("not_generation_ready", 0) == 0
    assert report["summary"]["ok"] == 51
