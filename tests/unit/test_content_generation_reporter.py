"""Unit tests for content generation reporter."""
from __future__ import annotations

import uuid

import pytest

from app.services.content_generation_reporter import (
    ContentGenerationReporter,
    GenerationReportData,
)


@pytest.mark.unit
def test_reporter_instantiation() -> None:
    """Reporter can be instantiated."""
    reporter = ContentGenerationReporter()
    assert reporter is not None
    assert reporter.base_dir.exists()


@pytest.mark.unit
def test_reporter_has_write_report_method() -> None:
    """Reporter has write_report method."""
    reporter = ContentGenerationReporter()
    assert hasattr(reporter, "write_report")
    assert callable(getattr(reporter, "write_report"))


@pytest.mark.unit
def test_reporter_writes_report_files() -> None:
    """Reporter writes report files to disk."""
    reporter = ContentGenerationReporter(base_dir="/tmp/test_reports")
    data = GenerationReportData(
        run_id=str(uuid.uuid4()),
        scope_id="test_scope",
        status="completed",
        planned_tasks=10,
        executed_tasks=8,
        generated_artifacts=8,
        pending_review=7,
        validation_failed=1,
        source_blockers=2,
        staging_seed_results=5,
        staging_verification_passed=True,
        errors=["Test error"],
    )
    report_dir = reporter.write_report(data)
    assert report_dir.exists()
    assert (report_dir / "summary.md").exists()
    assert (report_dir / "summary.json").exists()
    assert (report_dir / "errors.log").exists()


@pytest.mark.unit
def test_reporter_writes_csv_files() -> None:
    """Reporter writes CSV files when data is provided."""
    reporter = ContentGenerationReporter(base_dir="/tmp/test_reports")
    data = GenerationReportData(
        run_id=str(uuid.uuid4()),
        scope_id="test_scope",
        status="completed",
        planned_tasks=1,
        executed_tasks=1,
        generated_artifacts=1,
        pending_review=1,
        validation_failed=0,
        source_blockers=0,
        staging_seed_results=0,
        staging_verification_passed=True,
        planned_tasks_list=[{"task_id": "1", "scope_id": "test"}],
        executed_tasks_list=[{"task_id": "1", "status": "completed"}],
        generated_artifacts_list=[{"artifact_id": "1", "status": "pending_review"}],
    )
    report_dir = reporter.write_report(data)
    assert (report_dir / "planned_tasks.csv").exists()
    assert (report_dir / "executed_tasks.csv").exists()
    assert (report_dir / "generated_artifacts.csv").exists()


@pytest.mark.unit
def test_reporter_skips_empty_csv_files(tmp_path) -> None:
    """Reporter skips CSV files when data is empty or contains empty row dict."""
    reporter = ContentGenerationReporter(base_dir=str(tmp_path))
    data = GenerationReportData(
        run_id=str(uuid.uuid4()),
        scope_id="test_scope",
        status="completed",
        planned_tasks=0,
        executed_tasks=0,
        generated_artifacts=0,
        pending_review=0,
        validation_failed=0,
        source_blockers=0,
        staging_seed_results=0,
        staging_verification_passed=False,
        planned_tasks_list=[{}],  # empty row dict
        errors=[],
    )
    report_dir = reporter.write_report(data)
    assert not (report_dir / "planned_tasks.csv").exists()
    assert not (report_dir / "errors.log").exists()

    summary_md = (report_dir / "summary.md").read_text()
    assert "Staging Verification:** Failed" in summary_md


@pytest.mark.unit
def test_reporter_writes_all_csv_and_json_payloads(tmp_path) -> None:
    """Reporter writes all 7 CSV files and scope readiness JSONs."""
    import json
    reporter = ContentGenerationReporter(base_dir=str(tmp_path))
    data = GenerationReportData(
        run_id="run-123",
        scope_id="scope-456",
        status="completed",
        planned_tasks=1,
        executed_tasks=1,
        generated_artifacts=1,
        pending_review=1,
        validation_failed=1,
        source_blockers=1,
        staging_seed_results=1,
        staging_verification_passed=True,
        scope_readiness_before={"score": 0.5},
        scope_readiness_after={"score": 1.0},
        planned_tasks_list=[{"task_id": "1"}],
        executed_tasks_list=[{"task_id": "1"}],
        generated_artifacts_list=[{"art_id": "1"}],
        pending_review_list=[{"art_id": "1"}],
        validation_failed_list=[{"art_id": "1", "err": "failed"}],
        source_blockers_list=[{"blocker": "missing"}],
        staging_seed_results_list=[{"seed": "ok"}],
        errors=["Critical validation failure"],
    )
    report_dir = reporter.write_report(data)

    assert (report_dir / "pending_review.csv").exists()
    assert (report_dir / "validation_failed.csv").exists()
    assert (report_dir / "source_blockers.csv").exists()
    assert (report_dir / "staging_seed_results.csv").exists()

    readiness_before = json.loads((report_dir / "scope_readiness_before.json").read_text())
    assert readiness_before == {"score": 0.5}

    readiness_after = json.loads((report_dir / "scope_readiness_after.json").read_text())
    assert readiness_after == {"score": 1.0}

    summary_json = json.loads((report_dir / "summary.json").read_text())
    assert summary_json["run_id"] == "run-123"
    assert summary_json["status"] == "completed"
