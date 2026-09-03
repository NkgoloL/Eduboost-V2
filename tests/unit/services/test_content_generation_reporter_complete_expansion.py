import csv
import json
from pathlib import Path
import pytest

from app.services.content_generation_reporter import (
    ContentGenerationReporter,
    GenerationReportData,
)


def test_content_generation_reporter_write_report(tmp_path: Path):
    reporter = ContentGenerationReporter(base_dir=str(tmp_path))

    data = GenerationReportData(
        run_id="test_run_123",
        scope_id="scope_math_g4",
        status="succeeded",
        planned_tasks=10,
        executed_tasks=10,
        generated_artifacts=20,
        pending_review=2,
        validation_failed=1,
        source_blockers=0,
        staging_seed_results=5,
        staging_verification_passed=True,
        errors=["Minor warning"],
        scope_readiness_before={"score": 0.8},
        scope_readiness_after={"score": 1.0},
        planned_tasks_list=[{"task_id": "t1", "layer": "lessons"}],
        executed_tasks_list=[{"task_id": "t1", "status": "succeeded"}],
        generated_artifacts_list=[{"art_id": "a1"}],
        pending_review_list=[{"art_id": "a1"}],
        validation_failed_list=[{"art_id": "a2", "reason": "format"}],
        source_blockers_list=[],  # empty rows check
        staging_seed_results_list=[{}],  # empty row dict check
    )

    report_dir = reporter.write_report(data)
    assert report_dir.exists()
    assert (report_dir / "summary.md").exists()
    assert (report_dir / "summary.json").exists()
    assert (report_dir / "scope_readiness_before.json").exists()
    assert (report_dir / "scope_readiness_after.json").exists()
    assert (report_dir / "planned_tasks.csv").exists()
    assert (report_dir / "executed_tasks.csv").exists()
    assert (report_dir / "generated_artifacts.csv").exists()
    assert (report_dir / "pending_review.csv").exists()
    assert (report_dir / "validation_failed.csv").exists()
    assert (report_dir / "staging_verification.json").exists()
    assert (report_dir / "errors.log").exists()

    # Verify content in summary.json
    with open(report_dir / "summary.json") as f:
        summary = json.load(f)
        assert summary["run_id"] == "test_run_123"
        assert summary["staging_verification_passed"] is True

    # Verify summary markdown
    with open(report_dir / "summary.md") as f:
        content = f.read()
        assert "**Run ID:** test_run_123" in content
        assert "Minor warning" in content


    # Test without errors and staging_verification_passed is False
    reporter_2 = ContentGenerationReporter(base_dir=str(tmp_path / "run_2"))
    data_no_errors = GenerationReportData(
        run_id="test_run_456",
        scope_id="scope_math_g4",
        status="failed",
        planned_tasks=1,
        executed_tasks=1,
        generated_artifacts=0,
        pending_review=0,
        validation_failed=1,
        source_blockers=1,
        staging_seed_results=0,
        staging_verification_passed=False,
        errors=[],
    )
    report_dir_2 = reporter_2.write_report(data_no_errors)
    assert not (report_dir_2 / "errors.log").exists()

    with open(report_dir_2 / "summary.md") as f:
        content_2 = f.read()
        assert "Staging Verification:** Failed" in content_2
