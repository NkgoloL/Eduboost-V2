from __future__ import annotations

import textwrap

import pytest

from app.services.batch_generation import BatchGenerationEngine
from app.services.etl.etl_pipeline import (
    DocumentType,
    IngestRequest,
    LicenseStatus,
    SourceType,
)
from app.services.etl.etl_pipeline_v3_additions import EduboostETLv3
from app.services.llm_provider import GenerationResult, TokenUsage


def _sample_text() -> str:
    return textwrap.dedent(
        """
        # Grade 5 Mathematics Place Value

        **Place Value** helps learners understand thousands, hundreds, tens and
        ones. This CAPS-aligned lesson explains how each digit changes value
        depending on its position. Learners compare numbers, expand numbers and
        explain their reasoning using concrete examples.
        """
    )


@pytest.fixture
def etl(tmp_path):
    sample = tmp_path / "lesson.md"
    sample.write_text(_sample_text() * 30, encoding="utf-8")
    service = EduboostETLv3(
        db_url=f"sqlite:///{tmp_path / 'etl-v3.db'}",
        storage_root=str(tmp_path / "storage"),
    )
    service.init_db()
    try:
        request = IngestRequest(
            file_path=str(sample),
            source_type=SourceType.manual_upload,
            uploaded_by="teacher@example.com",
            document_type=DocumentType.lesson_plan,
            grade=5,
            subject="mathematics",
            license_status=LicenseStatus.government_open,
            title="Place Value Lesson",
        )
        document = service.ingest(request)
        service.run_full_pipeline(document.document_id)
        yield service, document.document_id
    finally:
        service.close()


def test_etl_v3_audit_metadata_deprecation_and_reviewer_workload(etl) -> None:
    service, document_id = etl

    unchanged = service.update_metadata_with_audit(
        document_id,
        updated_by="admin@example.com",
        fields={"title": "Place Value Lesson"},
    )
    changed = service.update_metadata_with_audit(
        document_id,
        updated_by="admin@example.com",
        fields={"title": "Expanded Place Value Lesson", "subject": "mathematics"},
    )
    assignment = service.assign_reviewer(
        task_id="review-task-1",
        document_id=document_id,
        assigned_to="reviewer@example.com",
        assigned_by="lead@example.com",
        priority="high",
        due_days=2,
    )
    workload = service.get_reviewer_workload()
    deprecated = service.deprecate_document(
        document_id,
        deprecated_by="admin@example.com",
        reason="superseded by curated source",
        replacement_id="replacement-doc",
    )
    trail = service.get_audit_trail(document_id)

    assert unchanged == {"success": True, "changed": 0, "message": "No fields changed."}
    assert changed["success"] is True
    assert "title" in changed["fields"]
    assert assignment["assigned_to"] == "reviewer@example.com"
    assert any(row["assigned_to"] == "reviewer@example.com" and row["urgent"] == 1 for row in workload)
    assert deprecated["success"] is True
    assert deprecated["replacement_id"] == "replacement-doc"
    assert {entry["action"] for entry in trail} >= {"metadata_update", "deprecate"}


def test_etl_v3_dataset_split_contamination_metrics_and_feedback(etl, tmp_path) -> None:
    service, document_id = etl
    service.mark_training_ready(document_id)
    dataset = service.generate_training_dataset(
        document_ids=[document_id],
        example_type="qa",
        dataset_name="Place Value QA",
        created_by="teacher@example.com",
    )

    split = service.split_dataset(dataset.dataset_id, train=0.5, val=0.25, test=0.25)
    train_stats = service.get_dataset_statistics(split.train_dataset_id)
    test_stats = service.get_dataset_statistics(split.test_dataset_id)
    contamination = service.check_contamination(
        split.train_dataset_id,
        split.test_dataset_id,
    )
    export_path = service.export_dataset(split.train_dataset_id, fmt="jsonl", out_dir=str(tmp_path / "exports"))
    csv_export_path = service.export_dataset(split.train_dataset_id, fmt="csv", out_dir=str(tmp_path / "exports"))

    service.record_metric("pipeline.documents_processed", 2.0, {"stage": "unit"})
    service.record_metric("pipeline.documents_processed", 3.0, {"stage": "unit"})
    metric_window = service.get_metric_window("pipeline.documents_processed", hours=24)
    trend = service.get_completeness_trend(days=30)

    feedback = service.submit_feedback(
        user_id="teacher@example.com",
        feedback_type="content_quality",
        details="Worked examples need clearer language.",
        document_id=document_id,
    )
    resolved = service.resolve_feedback(
        feedback.feedback_id,
        resolved_by="admin@example.com",
        resolution_type="fixed",
        notes="Updated source text.",
    )
    duplicate_resolution = service.resolve_feedback(
        feedback.feedback_id,
        resolved_by="admin@example.com",
        resolution_type="duplicate",
    )
    feedback_summary = service.get_feedback_summary(days=30)
    job_failure_rate = service.get_job_failure_rate(hours=24)
    monitoring_report = service.get_monitoring_report()
    completeness_report = service.get_completeness_report()

    assert split.train_count > 0
    assert split.test_count > 0
    assert train_stats["total"] == split.train_count
    assert test_stats["total"] == split.test_count
    assert contamination.passed is False
    assert contamination.overlap_count > 0
    assert contamination.overlap_example_ids
    assert export_path.endswith(".jsonl")
    assert csv_export_path.endswith(".csv")
    with pytest.raises(ValueError, match="Unsupported format"):
        service.export_dataset(split.train_dataset_id, fmt="yaml", out_dir=str(tmp_path / "exports"))
    assert metric_window and sum(bucket["value"] for bucket in metric_window) == 5.0
    assert isinstance(trend, list)
    assert resolved == {
        "success": True,
        "feedback_id": feedback.feedback_id,
        "resolution_type": "fixed",
    }
    assert duplicate_resolution == {"success": False, "error": "Feedback already resolved."}
    assert feedback_summary["content_quality"] == 1
    assert job_failure_rate["failure_rate"] == 0.0
    assert monitoring_report.total_documents >= 1
    assert monitoring_report.feedback_summary["content_quality"] == 1
    assert completeness_report["total_required"] > 0
    assert completeness_report["missing_count"] >= 0


def test_etl_v3_failure_paths_are_explicit(etl) -> None:
    service, _document_id = etl

    missing_deprecation = service.deprecate_document(
        "missing-doc",
        deprecated_by="admin@example.com",
    )
    missing_metadata = service.update_metadata_with_audit(
        "missing-doc",
        updated_by="admin@example.com",
        fields={"title": "Nope"},
    )
    bulk = service.bulk_review(
        ["missing-doc"],
        action="approve",
        reviewer="reviewer@example.com",
        reason="batch decision",
    )

    with pytest.raises(ValueError, match="Dataset missing-dataset not found"):
        service.split_dataset("missing-dataset")
    with pytest.raises(AssertionError, match="Split ratios"):
        service.split_dataset("missing-dataset", train=0.5, val=0.4, test=0.4)

    assert missing_deprecation["success"] is False
    assert missing_metadata["success"] is False
    assert bulk.total == 1
    assert bulk.failed == 1
    assert bulk.results[0]["success"] is False


def test_batch_generation_helpers_preserve_source_context_and_generation_audit() -> None:
    result = GenerationResult(
        text="Learner-safe lesson response",
        provider="deterministic",
        model="deterministic-v1",
        usage=TokenUsage(10, 20, 30, 0.0),
        latency_ms=12.5,
        request_id="request-123",
    )
    checks = BatchGenerationEngine._generation_checks(result, "prompt-v1")
    source_context = BatchGenerationEngine._build_source_context(
        [
            {
                "source_title": "CAPS mathematics",
                "text": "Place value source paragraph.",
            },
            {
                "title": "Fallback title",
                "citation_text": "Teacher guide citation.",
            },
            {
                "source_title": "Empty source",
                "text": "   ",
            },
        ]
    )

    assert checks == {
        "provider": "deterministic",
        "model": "deterministic-v1",
        "prompt_version": "prompt-v1",
        "latency_ms": 12.5,
        "request_id": "request-123",
    }
    assert "[Source 1: CAPS mathematics]" in source_context
    assert "[Source 2: Fallback title]" in source_context
    assert "Empty source" not in source_context
