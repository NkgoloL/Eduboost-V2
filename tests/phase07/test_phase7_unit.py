from __future__ import annotations

import uuid
from types import SimpleNamespace

import pytest

from app.domain.curriculum_expansion_schemas import ExpansionPlanRequest, TrainingManifestCreateRequest
from app.services.curriculum_expansion import (
    artifact_eligibility_reasons,
    build_training_record,
    dataset_sha256,
    forbidden_training_paths,
    record_sha256,
    validate_language_content,
)


def _artifact(**overrides):
    values = {
        "artifact_id": uuid.uuid4(),
        "artifact_hash": "a" * 64,
        "version_number": 1,
        "scope_id": "grade4_mathematics_en",
        "caps_ref": "4.M.1.1",
        "grade": 4,
        "subject_code": "M",
        "language": "en",
        "content_layer": SimpleNamespace(value="lessons"),
        "status": SimpleNamespace(value="published"),
        "source_snapshot_hash": "s" * 64,
        "quality_score": 0.95,
        "caps_alignment_score": 0.96,
        "safety_status": "approved",
        "answer_key_verified": False,
        "artifact_json": {"title": "Whole numbers", "summary": "A CAPS-aligned lesson."},
        "sources": [
            SimpleNamespace(
                license_status="government_open",
                source_hash="h" * 64,
                chunk_hash=None,
            )
        ],
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_published_grounded_safe_artifact_is_eligible():
    reasons = artifact_eligibility_reasons(
        _artifact(),
        require_published=True,
        min_quality_score=0.8,
        min_caps_alignment_score=0.8,
    )
    assert reasons == []


@pytest.mark.parametrize(
    ("change", "expected"),
    [
        ({"status": SimpleNamespace(value="pending_review")}, "ineligible_lifecycle_state"),
        ({"source_snapshot_hash": None}, "missing_source_snapshot_hash"),
        ({"quality_score": 0.2}, "quality_below_threshold"),
        ({"caps_alignment_score": 0.2}, "caps_alignment_below_threshold"),
        ({"safety_status": "unsafe"}, "safety_not_approved"),
        ({"sources": []}, "missing_sources"),
        (
            {"sources": [SimpleNamespace(license_status="unknown", source_hash="h", chunk_hash=None)]},
            "disallowed_source_license",
        ),
        ({"artifact_json": {"learner_id": "abc", "title": "Unsafe"}}, "forbidden_operational_fields"),
        ({"artifact_json": {"title": "Contact a@b.co.za"}}, "obvious_pii"),
    ],
)
def test_ineligible_artifacts_are_rejected(change, expected):
    reasons = artifact_eligibility_reasons(
        _artifact(**change),
        require_published=True,
        min_quality_score=0.8,
        min_caps_alignment_score=0.8,
    )
    assert expected in reasons


def test_diagnostic_requires_independent_answer_key():
    artifact = _artifact(
        content_layer=SimpleNamespace(value="diagnostic_items"),
        answer_key_verified=False,
    )
    reasons = artifact_eligibility_reasons(
        artifact,
        require_published=True,
        min_quality_score=0.8,
        min_caps_alignment_score=0.8,
    )
    assert "answer_key_not_verified" in reasons


def test_record_and_dataset_hashes_are_deterministic():
    record = build_training_record(_artifact())
    first = record_sha256(record)
    second = record_sha256(dict(reversed(list(record.items()))))
    assert first == second
    assert dataset_sha256([first, "b" * 64]) == dataset_sha256(["b" * 64, first])


def test_forbidden_paths_are_recursive():
    assert forbidden_training_paths({"content": [{"guardian_id": "x"}]}) == ["$.content[0].guardian_id"]


def test_language_validation_rejects_placeholders_and_unknown_language():
    assert "placeholder_text" in validate_language_content({"text": "TODO"}, "en")
    assert "unsupported_language" in validate_language_content({"text": "Valid content"}, "xx")


def test_strict_schemas_reject_duplicate_values_and_unknown_fields():
    with pytest.raises(ValueError):
        ExpansionPlanRequest(scope_ids=["same", "same"], unexpected=True)
    with pytest.raises(ValueError):
        TrainingManifestCreateRequest(
            dataset_version="../escape",
            scope_ids=["grade4_mathematics_en"],
            languages=["en"],
        )
