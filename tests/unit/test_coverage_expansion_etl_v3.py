"""
Unit tests for app.services.etl.etl_pipeline_v3_additions (EduboostETLv3).
Covers init_db, audit trails, document deprecation, bulk review operations,
dataset splitting, contamination checks, and feedback resolutions.
"""
from __future__ import annotations

import os
import tempfile
import pytest

from app.services.etl.etl_pipeline_v3_additions import (
    EduboostETLv3,
    AuditEntry,
    BulkReviewResult,
    ContaminationReport,
    DatasetSplitResult,
)


@pytest.fixture
def etl_v3(tmp_path):
    storage_root = tmp_path / "data"
    storage_root.mkdir()
    db_file = tmp_path / "etl_v3_test.db"
    db_url = f"sqlite:///{db_file}"
    etl = EduboostETLv3(db_url=db_url, storage_root=str(storage_root))
    etl.init_db()
    return etl


def test_init_db(etl_v3):
    # Verify tables created
    tables = etl_v3._db().execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    table_names = [t[0] for t in tables]
    assert "document_audit_trail" in table_names
    assert "reviewer_assignments" in table_names
    assert "dataset_splits" in table_names
    assert "contamination_checks" in table_names


def test_audit_trail_and_deprecate(etl_v3):
    db = etl_v3._db()
    db.execute(
        "INSERT INTO documents (document_id, source_id, document_type, title, checksum, file_path_raw, processing_status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("doc-1", "src-1", "pdf", "Test Doc", "abc123hash", "/path/raw", "approved", "2026-08-01T00:00:00Z", "2026-08-01T00:00:00Z"),
    )
    db.commit()

    # Audit logging
    etl_v3._record_audit("doc-1", "test_action", "tester", notes="Testing")
    trail = etl_v3.get_audit_trail("doc-1")
    assert len(trail) >= 1
    assert trail[0]["action"] == "test_action"

    # Deprecate document
    dep_res = etl_v3.deprecate_document(
        document_id="doc-1",
        deprecated_by="admin@eduboost.co.za",
        reason="Superseded",
        replacement_id="doc-2",
    )
    assert dep_res["success"] is True
    assert str(dep_res["new_status"]).endswith("archived")


def test_bulk_review_and_reviewer_assignment(etl_v3):
    db = etl_v3._db()
    db.execute("INSERT INTO documents (document_id, source_id, document_type, title, checksum, file_path_raw, processing_status, created_at, updated_at) VALUES ('d1', 's1', 'pdf', 'D1', 'hash1', '/raw1', 'pending', '2026-08-01T00:00:00Z', '2026-08-01T00:00:00Z')")
    db.execute("INSERT INTO documents (document_id, source_id, document_type, title, checksum, file_path_raw, processing_status, created_at, updated_at) VALUES ('d2', 's2', 'pdf', 'D2', 'hash2', '/raw2', 'pending', '2026-08-01T00:00:00Z', '2026-08-01T00:00:00Z')")
    db.commit()

    res = etl_v3.bulk_review(
        document_ids=["d1", "d2"],
        action="approve",
        reviewer="reviewer@eduboost.co.za",
    )
    assert res.succeeded == 2

    # Assign reviewer
    assign_id = etl_v3.assign_reviewer(task_id="t1", document_id="d1", assigned_to="reviewer@eduboost.co.za")
    assert assign_id is not None

    workload = etl_v3.get_reviewer_workload()
    assert isinstance(workload, list)


def test_dataset_splits_and_contamination(etl_v3):
    db = etl_v3._db()
    db.execute(
        "INSERT INTO training_datasets (dataset_id, name, dataset_type, created_at) VALUES (?, ?, ?, ?)",
        ("ds-parent", "Parent DS", "rlhf", "2026-08-01T00:00:00Z"),
    )
    db.execute(
        "INSERT INTO training_datasets (dataset_id, name, dataset_type, created_at) VALUES (?, ?, ?, ?)",
        ("ds-train", "Train DS", "rlhf", "2026-08-01T00:00:00Z"),
    )
    db.execute(
        "INSERT INTO training_datasets (dataset_id, name, dataset_type, created_at) VALUES (?, ?, ?, ?)",
        ("ds-test", "Test DS", "rlhf", "2026-08-01T00:00:00Z"),
    )
    db.execute(
        "INSERT INTO training_examples (example_id, dataset_id, document_id, example_type, input_text, output_text, created_at) VALUES ('ex1', 'ds-train', 'd1', 'qa', 'c1', 'a1', '2026-08-01T00:00:00Z')"
    )
    db.execute(
        "INSERT INTO training_examples (example_id, dataset_id, document_id, example_type, input_text, output_text, created_at) VALUES ('ex2', 'ds-test', 'd1', 'qa', 'c1', 'a1', '2026-08-01T00:00:00Z')"
    )
    db.commit()

    split_res = etl_v3.split_dataset("ds-parent", train=0.6, val=0.2, test=0.2)
    assert split_res.parent_dataset_id == "ds-parent"

    contam = etl_v3.check_contamination("ds-train", "ds-test")
    assert contam.overlap_count == 1
    assert contam.passed is False  # 1 overlap found


def test_feedback_resolution_and_completeness(etl_v3):
    db = etl_v3._db()
    db.execute("INSERT INTO user_feedback (feedback_id, document_id, user_id, feedback_type, details, created_at) VALUES ('fb1', 'doc1', 'u1', 'formatting', 'Bad formatting', '2026-08-01T00:00:00Z')")
    db.commit()

    res = etl_v3.resolve_feedback("fb1", resolved_by="admin", resolution_type="fixed", notes="Fixed formatting")
    assert res["feedback_id"] == "fb1"

    trend = etl_v3.get_completeness_trend(days=7)
    assert isinstance(trend, list)
