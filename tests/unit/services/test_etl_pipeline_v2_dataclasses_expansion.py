import pytest

from app.services.etl.etl_pipeline_v2 import (
    DocumentVersion,
    TrainingDataset,
    TrainingExample,
    FeedbackRecord,
    MonitoringReport,
)


def test_etl_v2_dataclasses_and_defaults():
    ver = DocumentVersion(
        version_id="ver-1",
        document_id="doc-1",
        version_number="1.0",
        change_summary="Initial release",
        created_by="admin",
        created_at="2026-08-29T10:00:00Z",
    )
    assert ver.version_id == "ver-1"
    assert ver.version_number == "1.0"

    ds = TrainingDataset(
        dataset_id="ds-1",
        name="CAPS G4 Maths",
        description="Grounded QA dataset",
        dataset_type="qa_pairs",
        version="1.0",
        split="train",
        document_ids=["doc-1"],
    )
    assert ds.dataset_id == "ds-1"
    assert len(ds.created_at) > 0

    ex = TrainingExample(
        example_id="ex-1",
        dataset_id="ds-1",
        document_id="doc-1",
        chunk_id="chk-1",
        example_type="qa",
        input_text="What is 2 + 2?",
        output_text="4",
    )
    assert ex.example_id == "ex-1"
    assert ex.quality_score == 0.0

    fb = FeedbackRecord(
        feedback_id="fb-1",
        document_id="doc-1",
        chunk_id=None,
        user_id="usr-1",
        feedback_type="incorrect_answer",
        details="Typo in answer",
    )
    assert fb.resolved is False
    assert len(fb.created_at) > 0
