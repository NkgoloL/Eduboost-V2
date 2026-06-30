from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.services.content_file_promotion_readiness import ContentFilePromotionReadinessService
from scripts.curriculum.report_content_coverage import build_report

pytestmark = pytest.mark.unit
REPO_ROOT = Path(__file__).resolve().parents[2]


def test_file_promotion_readiness_marks_review_scopes_staging_ready_not_production_ready() -> None:
    service = ContentFilePromotionReadinessService(project_root=REPO_ROOT)

    result = service.evaluate_scope("grade5_mathematics_en")

    assert result.source_ready is True
    assert result.staging_eligible is True
    assert result.production_eligible is False
    assert result.manifest["layers"]["diagnostic_items"]["record_count"] >= 40
    joined = " ".join(result.blockers)
    assert "quality audit" not in joined


def test_file_promotion_readiness_writes_summary_and_per_scope_manifests(tmp_path: Path) -> None:
    service = ContentFilePromotionReadinessService(project_root=REPO_ROOT)

    summary = service.write_manifests(output_dir=tmp_path)

    assert summary["summary"]["scope_count"] == 51
    assert summary["summary"]["staging_eligible"] == 51
    assert summary["summary"]["production_eligible"] == 1
    assert summary["summary"]["review_blocked"] == 50
    assert summary["summary"]["lesson_quarantined"] == 0
    assert (tmp_path / "grade5_mathematics_en_promotion_readiness.json").exists()
    written = json.loads((tmp_path / "all_scopes_promotion_readiness_summary.json").read_text())
    assert written["summary"] == summary["summary"]


def test_registry_coverage_report_includes_layer_files_and_promotion_readiness() -> None:
    report = build_report(strict_counts=False)
    grade5 = next(row for row in report["scopes"] if row["scope_id"] == "grade5_mathematics_en")

    assert grade5["staging_eligible"] is True
    assert grade5["production_eligible"] is False
    assert grade5["artifact_layers"]["lessons"]["exists"] is True
    assert grade5["artifact_layers"]["study_plan_templates"]["record_count"] > 0
    assert report["summary"].get("scopes.staging_eligible", 0) == 51
