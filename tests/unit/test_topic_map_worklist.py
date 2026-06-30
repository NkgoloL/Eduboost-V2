from __future__ import annotations

from pathlib import Path

import pytest

from scripts.curriculum.build_topic_map_worklist import build_worklist
from scripts.curriculum.scaffold_topic_map_drafts import build_draft, draft_path


pytestmark = pytest.mark.unit


def test_topic_map_worklist_covers_all_registered_scopes_and_current_gaps() -> None:
    worklist = build_worklist()

    assert worklist["validation_passed"] is True
    assert worklist["summary"]["scopes_total"] == 51
    assert worklist["summary"]["scopes_generation_ready"] == 51
    assert worklist["summary"]["scopes_needing_topic_map"] == 0
    assert worklist["summary"]["source_documents_distinct"] == 23
    assert worklist["summary"].get("tasks.upload_source_pdf_to_object_store", 0) == 0
    assert worklist["summary"].get("tasks.extract_topic_map", 0) == 0


def test_topic_map_worklist_preserves_source_hashes_for_scope() -> None:
    worklist = build_worklist()
    grade7_math = next(item for item in worklist["items"] if item["scope_id"] == "grade7_mathematics_en")

    assert grade7_math["source_document_ids"] == ["caps_senior_mathematics_en"]
    assert grade7_math["source_sha256"] == ["64dcd19ee1d67109ff4172d9b098259954a2e77a55aeae0d11ee7ec033b0d8f8"]
    assert grade7_math["text_sha256"] == ["881f88f60186856703767333a0c3f2331b8aeebb52dd11fcf46c2f25c90d3c33"]
    assert grade7_math["text_extract_paths"] == ["data/caps/source_documents/text/caps_senior_mathematics_en.txt"]
    assert grade7_math["object_store_uris"] == [
        "https://eduboostcaps06022047.blob.core.windows.net/caps-sources/senior/mathematics/en/caps_senior_mathematics_en-64dcd19ee1d67109.pdf"
    ]
    assert "upload_source_pdf_to_object_store" not in grade7_math["outstanding_tasks"]
    assert grade7_math["generation_ready"] is True
    assert grade7_math["outstanding_tasks"] == []


def test_draft_path_stays_outside_runtime_topic_map_discovery_dir(tmp_path: Path) -> None:
    path = draft_path("grade7_mathematics_en", draft_dir=tmp_path / "drafts")

    assert path.name == "grade7_mathematics_en.json"
    assert "data/caps/topic_maps" not in str(path)


def test_build_draft_marks_envelope_unreviewed() -> None:
    draft = build_draft(
        {
            "scope_id": "grade7_mathematics_en",
            "grade": 7,
            "subject": "Mathematics",
            "subject_code": "M",
            "suggested_topic_map_path": "data/caps/topic_maps/grade7_mathematics_en.json",
            "source_document_ids": ["caps_senior_mathematics_en"],
            "source_paths": ["data/caps/source_documents/raw/caps_senior_mathematics_en.pdf"],
            "source_sha256": ["abc123"],
            "canonical_source_urls": ["https://example.test/source.pdf"],
            "object_store_uris": [],
            "text_extract_paths": ["data/caps/source_documents/text/caps_senior_mathematics_en.txt"],
            "text_sha256": ["abc123-text"],
            "outstanding_tasks": ["extract_topic_map", "approve_topic_map"],
        }
    )

    assert draft["_meta"]["status"] == "draft_unreviewed"
    assert draft["_meta"]["review_required"] is True
    assert draft["_meta"]["text_sha256"] == ["abc123-text"]
    assert draft["terms"] == []
