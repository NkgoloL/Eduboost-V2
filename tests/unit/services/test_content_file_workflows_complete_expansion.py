import json
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from app.domain.content_scope import ContentScope, ContentScopeStatus
from app.services.content_file_lesson_quality import (
    ContentFileLessonQualityService,
    LessonFileQualityResult,
    _now_utc as lesson_now_utc,
    _write_json as lesson_write_json,
)
from app.services.content_file_promotion_readiness import (
    ContentFilePromotionReadinessService,
    PromotionReadinessResult,
    _counts_for_layer,
    _now_utc as promo_now_utc,
    _write_json as promo_write_json,
)
from app.services.content_file_review_workflow import (
    ContentFileReviewWorkflowService,
    _valid_evidence_url,
    _now_utc as review_now_utc,
    _write_json as review_write_json,
)
from app.services.content_generation.generated_lesson_contract import GeneratedLessonQualityResult


def test_content_file_lesson_quality_complete(tmp_path):
    registry = MagicMock()
    validator = MagicMock()
    service = ContentFileLessonQualityService(
        project_root=tmp_path,
        registry=registry,
        validator=validator,
    )

    # 1. Scope without lessons configured (line 49)
    scope_no_path = MagicMock(spec=ContentScope, scope_id="s_no_path", artifact_paths={})
    registry.get_scope.return_value = scope_no_path
    res1 = service.audit_scope("s_no_path")
    assert res1.exists is False
    assert res1.quarantined is True
    assert "Lessons artifact path is not configured" in res1.blockers[0]

    # 2. Scope with missing lessons file (line 64)
    scope_missing_file = MagicMock(
        spec=ContentScope,
        scope_id="s_missing",
        artifact_paths={"lessons": "data/missing.json"},
    )
    registry.get_scope.return_value = scope_missing_file
    res2 = service.audit_scope("s_missing")
    assert res2.exists is False
    assert res2.quarantined is True
    assert "Lessons artifact file is missing" in res2.blockers[0]

    # 3. Scope with lessons file that fails quality audit (line 87)
    lessons_file = tmp_path / "lessons.json"
    lessons_file.write_text(json.dumps({"lessons": [{"id": 1}]}), encoding="utf-8")
    scope_failed = MagicMock(
        spec=ContentScope,
        scope_id="s_fail",
        subject_code="MATH",
        subject="Mathematics",
        source_documents=["doc1"],
        artifact_paths={"lessons": "lessons.json"},
    )
    registry.get_scope.return_value = scope_failed

    mock_issue = MagicMock(lesson_id="L1", caps_ref="4.M.1", field="title", reason="too short")
    validator.validate_file_payload.return_value = GeneratedLessonQualityResult(
        passed=False,
        lesson_count=5,
        failed_lesson_count=2,
        aggregate={"title": 2},
        issues=[mock_issue],
    )
    res3 = service.audit_scope("s_fail")
    assert res3.passed is False
    assert res3.quarantined is True
    assert len(res3.blockers) == 1
    assert "Lesson layer failed quality audit" in res3.blockers[0]
    assert len(res3.issues) == 1
    assert res3.issues[0]["lesson_id"] == "L1"

    # 4. build_all and write_manifests (lines 112-137)
    registry.list_scopes.return_value = [scope_failed]
    out_dir = tmp_path / "quality_manifests"
    summary = service.write_manifests(output_dir=out_dir)
    assert summary["summary"]["scope_count"] == 1
    assert (out_dir / "s_fail_lesson_quality.json").exists()
    assert (out_dir / "all_scopes_lesson_quality_summary.json").exists()

    # 5. Helpers
    assert lesson_now_utc().endswith("Z")
    test_json_file = tmp_path / "test.json"
    lesson_write_json(test_json_file, {"a": 1})
    assert test_json_file.exists()


def test_content_file_promotion_readiness_complete(tmp_path):
    registry = MagicMock()
    review_svc = MagicMock()
    quality_svc = MagicMock()
    service = ContentFilePromotionReadinessService(
        project_root=tmp_path,
        registry=registry,
        review_service=review_svc,
        lesson_quality_service=quality_svc,
    )

    # 1. source_ready is False (line 76) & missing layer files (line 83)
    scope = MagicMock(
        spec=ContentScope,
        scope_id="math_g4",
        grade=4,
        phase="intermediate",
        subject_code="MATH",
        subject="Mathematics",
        language="en",
        caps_refs=["4.M.1"],
        status=ContentScopeStatus.DRAFT,
        topic_map_path=None,
        artifact_paths={},
    )
    registry.get_scope.return_value = scope

    quality_svc.audit_scope.return_value = LessonFileQualityResult(
        scope_id="math_g4",
        relative_path="lessons.json",
        exists=True,
        passed=False,
        lesson_count=10,
        failed_lesson_count=3,
        quarantined=True,
        blockers=["Lesson quality quarantined."],
        aggregate={},
        issues=[],
    )

    mock_rev_evidence = MagicMock(
        status="pending",
        approved=False,
        stage_unlocked=False,
        production_unlocked=False,
        manifest_path=None,
        stage_blockers=["Need review"],
        production_blockers=["Need review"],
        blockers=["Need review"],
    )
    review_svc.review_status.return_value = mock_rev_evidence

    with patch("app.services.content_file_promotion_readiness.generation_ready", return_value=False):
        res = service.evaluate_scope("math_g4")
        assert res.source_ready is False
        assert res.staging_eligible is False
        assert res.production_eligible is False
        assert any("Scope source material is not generation-ready" in b for b in res.blockers)
        assert any("Lesson quality quarantined" in b for b in res.blockers)
        assert any("Scope status draft is not production-promotable" in b for b in res.blockers)



    # 2. _layer_manifest with None, non-existent, and empty record count (lines 206, 218, 85)
    man_none = service._layer_manifest("math_g4", "topic_map", None)
    assert man_none["exists"] is False
    assert man_none["relative_path"] is None

    man_missing = service._layer_manifest("math_g4", "lessons", "nonexistent.json")
    assert man_missing["exists"] is False

    empty_json = tmp_path / "empty_lessons.json"
    empty_json.write_text(json.dumps({"lessons": []}), encoding="utf-8")
    man_empty = service._layer_manifest("math_g4", "lessons", "empty_lessons.json")
    assert man_empty["exists"] is True
    assert man_empty["record_count"] == 0

    # Scope with empty layer record count (hits line 85)
    scope_empty = MagicMock(
        spec=ContentScope,
        scope_id="math_empty",
        grade=4,
        phase="intermediate",
        subject_code="MATH",
        subject="Mathematics",
        language="en",
        caps_refs=["4.M.1"],
        status=ContentScopeStatus.ACTIVE,
        topic_map_path=None,
        artifact_paths={"lessons": "empty_lessons.json"},
    )
    registry.get_scope.return_value = scope_empty
    res_empty = service.evaluate_scope("math_empty")
    assert any("lessons artifact file contains no records" in b for b in res_empty.blockers)

    # 3. _counts_for_layer branches (topic without caps_ref, and unknown layer)
    payload_topic = {
        "terms": [
            {
                "topics": [
                    {"subtopics": [{"caps_ref": "4.M.1"}]},
                    {"caps_ref": "4.M.2", "subtopics": []},
                ]
            }
        ]
    }
    cnt, apprv, rev = _counts_for_layer("topic_map", payload_topic)
    assert cnt == 2

    cnt_unknown, apprv_unknown, _ = _counts_for_layer("unknown_layer_name", {"other": [1, 2]})
    assert cnt_unknown == 0

    # 4. Helpers
    assert promo_now_utc().endswith("Z")
    pj = tmp_path / "promo.json"
    promo_write_json(pj, {"hello": "world"})
    assert pj.exists()


def test_content_file_review_workflow_evidence_url_and_helpers(tmp_path):
    # Test _valid_evidence_url branches (lines 204, 209)
    assert _valid_evidence_url(None) is False
    assert _valid_evidence_url("") is False
    assert _valid_evidence_url("pending") is False
    assert _valid_evidence_url("http://insecure.example.com") is False
    assert _valid_evidence_url("https://") is False
    assert _valid_evidence_url("https://example.com/evidence") is False
    assert _valid_evidence_url("https://localhost:8000/report") is False
    assert _valid_evidence_url("https://valid-domain.co.za/reports/123") is True

    # Helpers
    assert review_now_utc().endswith("Z")
    rj = tmp_path / "rev.json"
    review_write_json(rj, {"a": "b"})
    assert rj.exists()
