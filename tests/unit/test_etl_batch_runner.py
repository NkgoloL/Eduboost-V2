"""Unit tests for tools.etl.batch_runner."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.etl.batch_runner import ETLBatchRunner, run_batch_ingestion


def _create_sample_topic_map(grade: int, subject: str) -> dict:
    return {
        "grade": grade,
        "subject": subject,
        "terms": [
            {
                "term": t,
                "topics": [
                    {
                        "topic": f"Topic {t}.{i}",
                        "caps_ref": f"{grade}.{subject[:3].upper()}.{t}.{i}",
                        "subtopics": [
                            {
                                "subtopic": f"Subtopic {t}.{i}",
                                "caps_ref": f"{grade}.{subject[:3].upper()}.{t}.{i}.1",
                                "assessment_standards": [
                                    f"Assessment standard text describing learning objectives for term {t} topic {i} in South African curriculum.",
                                    "Second assessment standard text with thorough descriptions of learner competencies.",
                                ],
                                "common_misconceptions": [f"misconception_{t}_{i}"],
                                "prerequisites": [],
                            }
                        ],
                    }
                    for i in range(1, 3)
                ],
            }
            for t in range(1, 5)
        ],
    }


def test_infer_metadata_grade_and_subject():
    runner = ETLBatchRunner(db_url="sqlite:///:memory:", storage_root="/tmp", auto_approve=True)

    meta1 = runner._infer_metadata(Path("grader_mathematics_en.json"))
    assert meta1["grade"] == 0
    assert meta1["subject"] == "mathematics"

    meta2 = runner._infer_metadata(Path("caps_topic_map_grade4_maths.json"))
    assert meta2["grade"] == 4
    assert meta2["subject"] == "mathematics"

    meta3 = runner._infer_metadata(Path("grade7_coding_and_robotics_en.json"))
    assert meta3["grade"] == 7
    assert meta3["subject"] == "coding_and_robotics"


def test_process_file_end_to_end(tmp_path: Path):
    db_file = tmp_path / "test_etl.db"
    storage = tmp_path / "storage"
    runner = ETLBatchRunner(
        db_url=f"sqlite:///{db_file}",
        storage_root=str(storage),
        auto_approve=True,
    )

    sample_doc = _create_sample_topic_map(4, "Mathematics")
    src_file = tmp_path / "grade4_mathematics_en.json"
    src_file.write_text(json.dumps(sample_doc), encoding="utf-8")

    res = runner.process_file(src_file)
    assert res.status == "approved"
    assert res.approved is True
    assert res.quality_score >= 0.70
    assert res.chunks_count >= 1
    assert res.document_id is not None

    # Idempotent re-run on existing file
    res2 = runner.process_file(src_file)
    assert res2.document_id == res.document_id
    assert res2.status == "approved"
    assert res2.error is None


def test_run_batch_ingestion_directory(tmp_path: Path):
    db_file = tmp_path / "test_etl.db"
    storage = tmp_path / "storage"
    in_dir = tmp_path / "input"
    in_dir.mkdir(parents=True)
    report_file = tmp_path / "report.json"

    for i in range(1, 4):
        file_path = in_dir / f"grade{i}_mathematics_en.json"
        doc = _create_sample_topic_map(i, "Mathematics")
        file_path.write_text(json.dumps(doc), encoding="utf-8")

    summary = run_batch_ingestion(
        input_dir=str(in_dir),
        db_url=f"sqlite:///{db_file}",
        storage_root=str(storage),
        output_report=str(report_file),
        auto_approve=True,
    )

    assert summary["total_files"] == 3
    assert summary["successful_ingestions"] == 3
    assert summary["approved_count"] == 3
    assert summary["failed_count"] == 0
    assert summary["total_chunks"] >= 3
    assert summary["average_quality_score"] >= 0.70
    assert report_file.exists()


def test_batch_runner_scopes_filter(tmp_path: Path):
    db_file = tmp_path / "test_etl.db"
    storage = tmp_path / "storage"
    in_dir = tmp_path / "input"
    in_dir.mkdir(parents=True)

    for i in range(1, 4):
        file_path = in_dir / f"grade{i}_mathematics_en.json"
        doc = _create_sample_topic_map(i, "Mathematics")
        file_path.write_text(json.dumps(doc), encoding="utf-8")

    # Ingest only grade2
    report_file = tmp_path / "filter_report.json"
    summary = run_batch_ingestion(
        input_dir=str(in_dir),
        db_url=f"sqlite:///{db_file}",
        storage_root=str(storage),
        output_report=str(report_file),
        auto_approve=True,
        scopes=["grade2_mathematics_en"],
    )

    assert summary["total_files"] == 1
    assert summary["successful_ingestions"] == 1
    assert summary["results"][0]["filename"] == "grade2_mathematics_en.json"
    assert report_file.exists()


def test_batch_runner_resumability_and_idempotency(tmp_path: Path):
    db_file = tmp_path / "test_etl.db"
    storage = tmp_path / "storage"
    in_dir = tmp_path / "input"
    in_dir.mkdir(parents=True)

    for i in range(1, 4):
        file_path = in_dir / f"grade{i}_mathematics_en.json"
        doc = _create_sample_topic_map(i, "Mathematics")
        file_path.write_text(json.dumps(doc), encoding="utf-8")

    # First pass: processes all 3
    report_file = tmp_path / "resumable_report.json"
    summary1 = run_batch_ingestion(
        input_dir=str(in_dir),
        db_url=f"sqlite:///{db_file}",
        storage_root=str(storage),
        output_report=str(report_file),
        auto_approve=True,
    )
    assert summary1["total_files"] == 3
    assert summary1["already_existing"] == 0
    assert report_file.exists()

    # Second pass: resumable skip
    summary2 = run_batch_ingestion(
        input_dir=str(in_dir),
        db_url=f"sqlite:///{db_file}",
        storage_root=str(storage),
        output_report=str(report_file),
        auto_approve=True,
    )
    assert summary2["total_files"] == 3
    assert summary2["already_existing"] == 3
    assert summary2["successful_ingestions"] == 3
    assert summary2["failed_count"] == 0
