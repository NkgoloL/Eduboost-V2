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
def test_reporter_skips_empty_csv_files() -> None:
    """Reporter skips CSV files when data is empty."""
    import tempfile
    import shutil
    temp_dir = tempfile.mkdtemp()
    try:
        reporter = ContentGenerationReporter(base_dir=temp_dir)
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
            staging_verification_passed=True,
        )
        report_dir = reporter.write_report(data)
        assert not (report_dir / "planned_tasks.csv").exists()
        assert not (report_dir / "executed_tasks.csv").exists()
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
